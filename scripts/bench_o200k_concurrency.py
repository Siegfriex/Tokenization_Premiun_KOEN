"""o200k standalone benchmark + Kiwi/o200k concurrency interference test.

Addendum §5: o200k는 Kiwi만큼의 full-population 동시성 증거가 없다. full launch 전에
bounded benchmark로 standalone 성능을 재고, 그 뒤 두 workload를 동시에 돌려 간섭을
측정해 PARALLEL_FULL_EXECUTION_AUTHORIZED / SEQUENTIAL_FALLBACK 을 자동 판정한다.

usage:
  python scripts/bench_o200k_concurrency.py standalone
  python scripts/bench_o200k_concurrency.py interference
"""

from __future__ import annotations

import datetime as dt
import json
import subprocess
import sys
import time
from pathlib import Path
from zoneinfo import ZoneInfo

import psutil

from tokenization_premium.memory_guard import MemoryGuard
from tokenization_premium.paths import PROJECT_ROOT

KST = ZoneInfo("Asia/Seoul")
REP_V2 = PROJECT_ROOT / "data/registry/REP_FEATURES_v002.parquet"
PAIR = PROJECT_ROOT / "data/registry/PAIR_REGISTRY_v002.parquet"
CACHE = PROJECT_ROOT / ".runtime/tiktoken-cache"
RUNTIME = PROJECT_ROOT / ".runtime/o200k-bench"
REPORT = PROJECT_ROOT / "outputs/reports/runtime"
FINAL_N = 3_835_988

BENCH_N = 100_000          # standalone bounded benchmark
INTERFERENCE_N = 50_000    # 각 workload 동시 실행 규모

# Addendum §5 판정 임계값
PRE_MIN_AVAIL_GIB = 8.0
DURING_MIN_AVAIL_GIB = 6.0
MAX_SWAP_DELTA_MIB = 128.0
MAX_SLOWDOWN = 0.30


def worker_script(kind: str, n: int, out_dir: Path, tag: str) -> str:
    """별도 process로 실행할 workload 스크립트를 만든다 (독립 runtime/tmp)."""
    if kind == "tok":
        body = f"""
from pathlib import Path
from tokenization_premium.tokenizer_measurement import execute_token_measurement_run
m = execute_token_measurement_run(
    project_root=Path({str(PROJECT_ROOT)!r}),
    rep_features_path=Path({str(REP_V2)!r}),
    pair_registry_path=Path({str(PAIR)!r}),
    output_path=Path({str(out_dir)!r}) / "tok_{tag}.parquet",
    runtime_dir=Path({str(out_dir)!r}),
    run_id="BENCH_TOK_{tag}",
    run_mode="BENCHMARK",
    limit={n},
    batch_rows=2500,
    cache_dir=Path({str(CACHE)!r}),
)
print("RESULT", m["output"]["row_count"], m["stage_duration_sec"], m["rows_per_sec"])
"""
    else:
        body = f"""
from pathlib import Path
from tokenization_premium.morphology import execute_morphology_run
m = execute_morphology_run(
    project_root=Path({str(PROJECT_ROOT)!r}),
    rep_features_v002_path=Path({str(REP_V2)!r}),
    pair_registry_path=Path({str(PAIR)!r}),
    output_path=Path({str(out_dir)!r}) / "morph_{tag}.parquet",
    runtime_dir=Path({str(out_dir)!r}),
    run_id="BENCH_MORPH_{tag}",
    run_mode="BENCHMARK",
    limit={n},
    num_workers=24,
    batch_rows=2500,
)
print("RESULT", m["output"]["row_count"], m["stage_duration_sec"], m["rows_per_sec"])
"""
    return body


def run_workload(kind: str, n: int, tag: str, *, wait: bool = True):
    """workload를 별도 process로 띄운다."""
    out_dir = RUNTIME / tag
    out_dir.mkdir(parents=True, exist_ok=True)
    for stale in out_dir.glob("*.parquet*"):
        stale.unlink()
    script = out_dir / f"{kind}_worker.py"
    script.write_text(worker_script(kind, n, out_dir, tag), encoding="utf-8")
    proc = subprocess.Popen(
        [str(PROJECT_ROOT / ".venv/bin/python"), str(script)],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        env={"PATH": "/usr/bin:/bin", "HOME": str(Path.home()),
             "PYTHONUNBUFFERED": "1",
             "TOKENIZATION_PREMIUM_PROGRESS_INTERVAL_SEC": "10",
             "TIKTOKEN_CACHE_DIR": str(CACHE),
             "TMPDIR": str(out_dir)},
    )
    if not wait:
        return proc
    out, _ = proc.communicate()
    return parse_result(out, proc.returncode)


def parse_result(out: str, code: int) -> dict:
    for line in (out or "").splitlines():
        if line.startswith("RESULT"):
            _, rows, secs, rps = line.split()
            return {"ok": code == 0, "rows": int(rows), "elapsed_sec": float(secs),
                    "rows_per_sec": float(rps)}
    return {"ok": False, "rows": 0, "elapsed_sec": None, "rows_per_sec": None,
            "tail": (out or "")[-600:]}


def monitor(procs: list, guard: MemoryGuard, interval: float = 2.0) -> dict:
    """실행 중 memory/swap을 표본화하고 각 process RSS를 추적한다."""
    peak_rss = {}
    while any(p.poll() is None for p in procs):
        guard.sample()
        for p in procs:
            try:
                rss = psutil.Process(p.pid).memory_info().rss / 2**30
                for child in psutil.Process(p.pid).children(recursive=True):
                    rss += child.memory_info().rss / 2**30
                peak_rss[p.pid] = max(peak_rss.get(p.pid, 0.0), rss)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        time.sleep(interval)
    guard.sample()
    return {"peak_rss_gib_by_pid": {str(k): round(v, 3) for k, v in peak_rss.items()},
            "combined_peak_rss_gib": round(sum(peak_rss.values()), 3)}


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "standalone"
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.mkdir(parents=True, exist_ok=True)
    started = dt.datetime.now(tz=KST)
    boot = MemoryGuard("boot")
    b = boot.sample()
    print(f"[{started.isoformat(timespec='seconds')}] mode={mode}  "
          f"MemAvailable={b.mem_available_gib} GiB  swappiness={boot.swappiness}  status={b.status}")

    if mode == "standalone":
        guard = MemoryGuard("o200k_standalone")
        guard.sample()
        proc = run_workload("tok", BENCH_N, "standalone_tok", wait=False)
        mon = monitor([proc], guard)
        out, _ = proc.communicate()
        res = parse_result(out, proc.returncode)
        art = RUNTIME / "standalone_tok" / "tok_standalone_tok.parquet"
        size = art.stat().st_size if art.exists() else 0
        summary = guard.summary()
        payload = {
            "generated_kst": started.isoformat(timespec="seconds"),
            "standalone_o200k": {
                "n": BENCH_N, **res,
                "artifact_bytes": size,
                "bytes_per_row": round(size / res["rows"], 1) if res.get("rows") else None,
                "projected_full_min": round(FINAL_N / res["rows_per_sec"] / 60, 2)
                if res.get("rows_per_sec") else None,
                "projected_full_artifact_gib": round(size / res["rows"] * FINAL_N / 2**30, 2)
                if res.get("rows") else None,
                "memory_guard": summary, **mon,
            },
        }
        print(f"\no200k standalone: {res.get('rows',0):,} rows  "
              f"{res.get('rows_per_sec') or 0:,.1f} rows/s  "
              f"peak RSS {mon['combined_peak_rss_gib']} GiB  "
              f"swapΔ {summary['peak_swap_delta_mib']} MiB  status {summary['worst_status']}")
        print(f"  bytes/row {payload['standalone_o200k']['bytes_per_row']}  "
              f"-> full artifact ≈ {payload['standalone_o200k']['projected_full_artifact_gib']} GiB")
        print(f"  projected full ETA {payload['standalone_o200k']['projected_full_min']} min")
        if art.exists():
            art.unlink()
        (REPORT / "O200K_STANDALONE_BENCHMARK.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"\nwrote {(REPORT / 'O200K_STANDALONE_BENCHMARK.json').relative_to(PROJECT_ROOT)}")

    else:
        prior = json.loads((REPORT / "O200K_STANDALONE_BENCHMARK.json").read_text(encoding="utf-8"))
        tok_solo_rps = prior["standalone_o200k"]["rows_per_sec"]

        print(f"\n[1/3] morphology solo baseline (N={INTERFERENCE_N:,})")
        g1 = MemoryGuard("morph_solo")
        p1 = run_workload("morph", INTERFERENCE_N, "solo_morph", wait=False)
        m1 = monitor([p1], g1)
        morph_solo = parse_result(*[p1.communicate()[0], p1.returncode])
        print(f"      {morph_solo.get('rows_per_sec') or 0:,.1f} rows/s  RSS {m1['combined_peak_rss_gib']} GiB")

        print(f"\n[2/3] tokenizer solo baseline (N={INTERFERENCE_N:,})")
        g2 = MemoryGuard("tok_solo")
        p2 = run_workload("tok", INTERFERENCE_N, "solo_tok", wait=False)
        m2 = monitor([p2], g2)
        tok_solo = parse_result(*[p2.communicate()[0], p2.returncode])
        print(f"      {tok_solo.get('rows_per_sec') or 0:,.1f} rows/s  RSS {m2['combined_peak_rss_gib']} GiB")

        print(f"\n[3/3] concurrent (both N={INTERFERENCE_N:,}, separate processes/tmp)")
        gc_ = MemoryGuard("concurrent")
        pre = gc_.sample()
        pa_ = run_workload("morph", INTERFERENCE_N, "conc_morph", wait=False)
        pb_ = run_workload("tok", INTERFERENCE_N, "conc_tok", wait=False)
        mc = monitor([pa_, pb_], gc_)
        morph_conc = parse_result(*[pa_.communicate()[0], pa_.returncode])
        tok_conc = parse_result(*[pb_.communicate()[0], pb_.returncode])
        summary = gc_.summary()

        def slowdown(solo, conc):
            if not (solo.get("rows_per_sec") and conc.get("rows_per_sec")):
                return None
            return round(1 - conc["rows_per_sec"] / solo["rows_per_sec"], 4)

        s_morph, s_tok = slowdown(morph_solo, morph_conc), slowdown(tok_solo, tok_conc)
        print(f"      morph {morph_conc.get('rows_per_sec') or 0:,.1f} rows/s (slowdown {s_morph})")
        print(f"      tok   {tok_conc.get('rows_per_sec') or 0:,.1f} rows/s (slowdown {s_tok})")
        print(f"      combined peak RSS {mc['combined_peak_rss_gib']} GiB  "
              f"min avail {summary['min_mem_available_gib']} GiB  "
              f"swapΔ {summary['peak_swap_delta_mib']} MiB")

        checks = {
            "pre_mem_available_ok": pre.mem_available_gib >= PRE_MIN_AVAIL_GIB,
            "during_mem_available_ok": (summary["min_mem_available_gib"] or 0) >= DURING_MIN_AVAIL_GIB,
            "swap_delta_ok": summary["peak_swap_delta_mib"] <= MAX_SWAP_DELTA_MIB,
            "persistent_swap_io_zero": summary["total_swap_in_pages"] == 0
            and summary["total_swap_out_pages"] == 0,
            "no_writer_error": bool(morph_conc.get("ok") and tok_conc.get("ok")),
            "morph_slowdown_ok": s_morph is not None and s_morph <= MAX_SLOWDOWN,
            "tok_slowdown_ok": s_tok is not None and s_tok <= MAX_SLOWDOWN,
        }
        verdict = "PARALLEL_FULL_EXECUTION_AUTHORIZED" if all(checks.values()) else "SEQUENTIAL_FALLBACK"
        print("\n  gate:")
        for k, v in checks.items():
            print(f"    {'PASS' if v else 'FAIL'}  {k}")
        print(f"\n  VERDICT = {verdict}")

        for tag in ("solo_morph", "solo_tok", "conc_morph", "conc_tok"):
            for f in (RUNTIME / tag).glob("*.parquet"):
                f.unlink()

        payload = {
            "generated_kst": started.isoformat(timespec="seconds"),
            "interference_n": INTERFERENCE_N,
            "standalone_o200k_rows_per_sec": tok_solo_rps,
            "morph_solo": morph_solo, "tok_solo": tok_solo,
            "morph_concurrent": morph_conc, "tok_concurrent": tok_conc,
            "morph_slowdown": s_morph, "tok_slowdown": s_tok,
            "concurrent_memory": {**mc, "memory_guard": summary,
                                  "pre_mem_available_gib": pre.mem_available_gib},
            "thresholds": {"pre_min_avail_gib": PRE_MIN_AVAIL_GIB,
                           "during_min_avail_gib": DURING_MIN_AVAIL_GIB,
                           "max_swap_delta_mib": MAX_SWAP_DELTA_MIB,
                           "max_slowdown": MAX_SLOWDOWN},
            "checks": checks, "verdict": verdict,
        }
        (REPORT / "O200K_CONCURRENCY_BENCHMARK.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"\nwrote {(REPORT / 'O200K_CONCURRENCY_BENCHMARK.json').relative_to(PROJECT_ROOT)}")
