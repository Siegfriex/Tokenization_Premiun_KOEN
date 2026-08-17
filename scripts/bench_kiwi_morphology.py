"""Kiwi morphology 실행 엔진 adaptive benchmark.

Decision: RD-20260817-D02D03-CONFORMANCE-01 (RD-D) + EXECUTION SAFETY ADDENDUM

절대 gate: optimized path는 scalar reference와 exact output equality를 가져야 한다.
mismatch가 1건이라도 있으면 throughput과 무관하게 해당 candidate를 거부한다.

Addendum 준수:
  §5  ANALYSIS_BATCH / ARROW_WRITE_BATCH / CHECKPOINT_PART 를 서로 독립적으로 다룬다
  §6  전체 corpus를 하나의 iterable로 Kiwi에 넘기지 않는다 (항상 bounded chunk)
  §7  analyze -> consume -> write -> release 순으로만 진행 (unbounded queue 없음)
  §8  Kiwi Token 참조는 chunk 경계에서 즉시 해제한다
  §12 Stage A coarse (N=5,000) -> Stage B finalists (N=20,000) -> §13 final (N=100,000)
  §14 throughput decay 기반 thermal/power throttle 탐지
  §15 peak가 아니라 sustained throughput으로 선택

usage:
  python scripts/bench_kiwi_morphology.py stage_a
  python scripts/bench_kiwi_morphology.py stage_b
  python scripts/bench_kiwi_morphology.py final
"""

from __future__ import annotations

import datetime as dt
import gc
import json
import statistics
import sys
import time
from pathlib import Path
from zoneinfo import ZoneInfo

import duckdb
import psutil
import pyarrow as pa
import pyarrow.parquet as pq
from kiwipiepy import Kiwi

from tokenization_premium.memory_guard import (
    STATUS_GREEN,
    MemoryGuard,
    MemoryGuardAbort,
)
from tokenization_premium.morphology import (
    analyze_batch,
    build_record,
    compare_feature_dicts,
    features_from_morphs,
    morph_features_schema,
)
from tokenization_premium.paths import PROJECT_ROOT

KST = ZoneInfo("Asia/Seoul")
REP_V2 = PROJECT_ROOT / "data/registry/REP_FEATURES_v002.parquet"
PAIR = PROJECT_ROOT / "data/registry/PAIR_REGISTRY_v002.parquet"
RUNTIME = PROJECT_ROOT / ".runtime/morph-bench"
REPORT = PROJECT_ROOT / "outputs/reports/runtime"

SAMPLE_SALT = "MORPH_BENCH_v002"
STAGE_A_N = 5_000
STAGE_B_N = 20_000
FINAL_N = 100_000

STAGE_A_WORKERS = [1, 4, 8, 12, 16, 20, 24]
STAGE_A_ANALYSIS_BATCH = 5_000
STAGE_B_ANALYSIS_BATCHES = [1_000, 2_500, 5_000, 10_000]   # §5: 10,000 초과 금지
CHECKPOINT_PART_ROWS = 50_000                              # §5 기본 후보
WARMUP_TEXT = "형태소 분석기 워밍업 문장입니다"
THROTTLE_DECAY_RATIO = 0.75                                 # §14: 25% 이상 감소
THROTTLE_CONSECUTIVE = 5


def load_sample(n: int) -> tuple[list[str], list[str], list[int]]:
    """final cohort에서 결정적 고정 표본을 읽는다 (재실행해도 동일한 행 집합)."""
    con = duckdb.connect()
    con.execute("SET memory_limit='4GB'")
    con.execute("SET threads=4")
    (RUNTIME / "duckdb-spill").mkdir(parents=True, exist_ok=True)
    con.execute(f"SET temp_directory='{(RUNTIME / 'duckdb-spill').as_posix()}'")
    try:
        df = con.execute(
            "SELECT r.pair_id, p.ko_text_analysis AS ko_text, r.ko_eojeol_count AS eojeol_count "
            f"FROM read_parquet('{REP_V2.as_posix()}') r "
            f"JOIN read_parquet('{PAIR.as_posix()}') p USING (pair_id) "
            f"ORDER BY md5(r.pair_id || '{SAMPLE_SALT}') LIMIT {n}"
        ).fetchdf()
    finally:
        con.close()
    return df["pair_id"].tolist(), df["ko_text"].tolist(), [int(v) for v in df["eojeol_count"]]


def make_kiwi(num_workers: int | None) -> tuple[Kiwi, float]:
    """새 Kiwi 인스턴스를 만들고 warm-up까지 마친 뒤 startup 시간을 함께 돌려준다."""
    t0 = time.monotonic()
    kiwi = Kiwi() if num_workers is None else Kiwi(num_workers=num_workers)
    kiwi.analyze(WARMUP_TEXT, top_n=1)        # lazy initialization을 여기서 끝낸다
    analyze_batch([WARMUP_TEXT], kiwi=kiwi)    # iterable 경로도 별도로 예열한다
    return kiwi, round(time.monotonic() - t0, 3)


def scalar_reference(texts: list[str], eojeols: list[int]) -> tuple[list[dict], dict]:
    """scalar path 기준 결과와 성능을 만든다 (exactness 비교의 기준선)."""
    kiwi, startup = make_kiwi(None)
    guard = MemoryGuard("scalar_reference")
    guard.sample()
    t0 = time.monotonic()
    reference = [
        features_from_morphs(kiwi.analyze(t, top_n=1)[0][0], eojeol_count=e)
        for t, e in zip(texts, eojeols, strict=True)
    ]
    elapsed = time.monotonic() - t0
    guard.sample()
    del kiwi
    gc.collect()
    return reference, {
        "label": "scalar_reference", "num_workers": None, "startup_sec": startup,
        "elapsed_sec": round(elapsed, 3),
        "rows_per_sec": round(len(texts) / elapsed, 1),
        "ms_per_pair": round(1000 * elapsed / len(texts), 4),
        "memory_guard": guard.summary(),
    }


def chunk_bounds(total: int, size: int):
    """§6: 전체를 한 번에 넘기지 않도록 bounded chunk 경계를 만든다."""
    for start in range(0, total, size):
        yield start, min(start + size, total)


def run_analysis_only(
    texts: list[str], eojeols: list[int], *, workers: int, analysis_batch: int, guard: MemoryGuard
) -> tuple[list[dict], dict]:
    """§7 backpressure: chunk 하나를 분석 -> 즉시 feature로 소비 -> 참조 해제."""
    kiwi, startup = make_kiwi(workers)
    proc = psutil.Process()
    cpu_before = proc.cpu_times()
    chunk_throughput: list[float] = []
    features: list[dict] = []
    t0 = time.monotonic()
    try:
        for start, stop in chunk_bounds(len(texts), analysis_batch):
            c0 = time.monotonic()
            analyses = analyze_batch(texts[start:stop], kiwi=kiwi)
            for morphs, eojeol in zip(analyses, eojeols[start:stop], strict=True):
                features.append(features_from_morphs(morphs, eojeol_count=eojeol))
            del analyses                       # §8: Kiwi Token 참조를 즉시 해제한다
            chunk_throughput.append((stop - start) / max(time.monotonic() - c0, 1e-9))
            guard.check()                      # RED/EMERGENCY면 MemoryGuardAbort
    finally:
        elapsed = time.monotonic() - t0
        del kiwi
        gc.collect()
    cpu_after = proc.cpu_times()
    cpu_sec = (cpu_after.user - cpu_before.user) + (cpu_after.system - cpu_before.system)
    return features, {
        "startup_sec": startup,
        "elapsed_sec": round(elapsed, 3),
        "cpu_sec": round(cpu_sec, 3),
        "cpu_utilization_x": round(cpu_sec / elapsed, 2) if elapsed else None,
        "rows_per_sec": round(len(texts) / elapsed, 1),
        "ms_per_pair": round(1000 * elapsed / len(texts), 4),
        "chunk_throughput": [round(v, 1) for v in chunk_throughput],
    }


def detect_throttle(chunk_throughput: list[float]) -> dict:
    """§14: memory 문제가 없는데 throughput이 지속적으로 떨어지면 throttle을 의심한다."""
    if len(chunk_throughput) < 3 + THROTTLE_CONSECUTIVE:
        return {"verdict": "INSUFFICIENT_CHUNKS", "baseline_rows_per_sec": None}
    baseline = statistics.median(chunk_throughput[:3])
    run = 0
    for value in chunk_throughput[3:]:
        run = run + 1 if value < baseline * THROTTLE_DECAY_RATIO else 0
        if run >= THROTTLE_CONSECUTIVE:
            return {"verdict": "THERMAL_OR_POWER_THROTTLE_SUSPECTED",
                    "baseline_rows_per_sec": round(baseline, 1)}
    return {"verdict": "NO_THROTTLE_DETECTED", "baseline_rows_per_sec": round(baseline, 1)}


def equality_gate(reference: list[dict], candidate: list[dict]) -> dict:
    """§14 absolute gate: 전건 field 단위 exact 비교."""
    mismatch_rows = 0
    mismatch_fields: dict[str, int] = {}
    for ref, cand in zip(reference, candidate, strict=True):
        diff = compare_feature_dicts(ref, cand)
        if diff:
            mismatch_rows += 1
            for field_name in diff:
                mismatch_fields[field_name] = mismatch_fields.get(field_name, 0) + 1
    sequence_mismatch = sum(
        1 for r, c in zip(reference, candidate, strict=True)
        if r["morpheme_sequence"] != c["morpheme_sequence"])
    pos_mismatch = sum(
        1 for r, c in zip(reference, candidate, strict=True)
        if [m["pos"] for m in r["morpheme_sequence"]] != [m["pos"] for m in c["morpheme_sequence"]])
    return {
        "compared_rows": len(reference),
        "mismatch_rows": mismatch_rows,
        "mismatch_fields": mismatch_fields,
        "sequence_mismatch_rows": sequence_mismatch,
        "pos_mismatch_rows": pos_mismatch,
        "status": "ACCEPTED" if mismatch_rows == 0 else "REJECTED_OUTPUT_MISMATCH",
    }


def stage_a() -> dict:
    """Stage A — coarse worker sweep, analyzer 중심, 메모리 등급으로 조기 탈락."""
    _, texts, eojeols = load_sample(STAGE_A_N)
    print(f"Stage A: N={len(texts):,}  analysis_batch={STAGE_A_ANALYSIS_BATCH:,}  workers={STAGE_A_WORKERS}")
    reference, scalar = scalar_reference(texts, eojeols)
    print(f"  scalar_reference  {scalar['rows_per_sec']:>9,.1f} rows/s  "
          f"{scalar['ms_per_pair']:.4f} ms/pair  startup={scalar['startup_sec']}s")

    rows = [scalar]
    for workers in STAGE_A_WORKERS:
        guard = MemoryGuard(f"stage_a_w{workers}")
        try:
            candidate, perf = run_analysis_only(
                texts, eojeols, workers=workers,
                analysis_batch=STAGE_A_ANALYSIS_BATCH, guard=guard)
        except MemoryGuardAbort as exc:
            print(f"  w={workers:<3} ABORTED by memory guard: {exc}")
            rows.append({"label": f"w{workers}", "num_workers": workers,
                         "status": "REJECTED_MEMORY_GUARD", "error": str(exc),
                         "memory_guard": guard.summary()})
            gc.collect()
            continue

        gate = equality_gate(reference, candidate)
        summary = guard.summary()
        row = {
            "label": f"w{workers}", "num_workers": workers,
            "analysis_batch": STAGE_A_ANALYSIS_BATCH, **perf,
            "equality": gate, "memory_guard": summary,
            "speedup_vs_scalar": round(scalar["elapsed_sec"] / perf["elapsed_sec"], 2),
            "status": gate["status"] if summary["worst_status"] == STATUS_GREEN
            else f"{gate['status']}_MEMORY_{summary['worst_status']}",
        }
        rows.append(row)
        print(f"  w={workers:<3} {row['rows_per_sec']:>9,.1f} rows/s  cpu={row['cpu_utilization_x']}x  "
              f"rss={summary['peak_rss_gib']}GiB  swapΔ={summary['peak_swap_delta_mib']}MiB  "
              f"memAvail_min={summary['min_mem_available_gib']}GiB  x{row['speedup_vs_scalar']}  "
              f"mismatch={gate['mismatch_rows']}  {row['status']}")
        del candidate
        gc.collect()

    eligible = [r for r in rows if r.get("status") == "ACCEPTED"]
    eligible.sort(key=lambda r: -r["rows_per_sec"])
    top = [r["num_workers"] for r in eligible[:3]]
    print(f"\n  Stage A finalists (accepted, top throughput): {top}")
    return {"stage": "A", "sample_n": len(texts), "sample_salt": SAMPLE_SALT,
            "analysis_batch": STAGE_A_ANALYSIS_BATCH, "workers_swept": STAGE_A_WORKERS,
            "rows": rows, "finalists": top}


def run_end_to_end(
    pair_ids: list[str], texts: list[str], eojeols: list[int], *,
    workers: int, analysis_batch: int, arrow_batch: int, part_rows: int,
    out_dir: Path, guard: MemoryGuard,
) -> dict:
    """analysis -> feature -> Arrow -> checkpoint part parquet 까지 포함한 실제 저장 경로."""
    schema = morph_features_schema()
    out_dir.mkdir(parents=True, exist_ok=True)
    for stale in out_dir.glob("part-*.parquet*"):
        stale.unlink()

    proc = psutil.Process()
    cpu_before = proc.cpu_times()
    chunk_throughput: list[float] = []
    part_index, part_rows_written, written = 0, 0, 0
    writer: pq.ParquetWriter | None = None
    part_path = out_dir / f"part-{part_index:06d}.parquet"
    parts: list[dict] = []
    t0 = time.monotonic()
    try:
        for start, stop in chunk_bounds(len(texts), analysis_batch):
            c0 = time.monotonic()
            analyses = analyze_batch(texts[start:stop], kiwi=KIWI)
            records = [
                build_record(pid, morphs, eojeol_count=e)
                for pid, morphs, e in zip(pair_ids[start:stop], analyses, eojeols[start:stop], strict=True)
            ]
            del analyses                                 # §8 즉시 해제
            for a_start, a_stop in chunk_bounds(len(records), arrow_batch):
                if writer is None:
                    part_path = out_dir / f"part-{part_index:06d}.parquet"
                    writer = pq.ParquetWriter(
                        part_path.with_suffix(".parquet.partial"), schema=schema, compression="zstd")
                writer.write_batch(pa.RecordBatch.from_pylist(records[a_start:a_stop], schema=schema))
                part_rows_written += a_stop - a_start
                if part_rows_written >= part_rows:            # §9 checkpoint part 완성
                    writer.close()
                    writer = None
                    partial = part_path.with_suffix(".parquet.partial")
                    partial.replace(part_path)
                    parts.append({"part": part_index, "rows": part_rows_written,
                                  "bytes": part_path.stat().st_size})
                    part_index += 1
                    part_rows_written = 0
            written += len(records)
            del records
            chunk_throughput.append((stop - start) / max(time.monotonic() - c0, 1e-9))
            guard.check()
    finally:
        if writer is not None:
            writer.close()
            partial = part_path.with_suffix(".parquet.partial")
            if partial.exists():
                partial.replace(part_path)
                parts.append({"part": part_index, "rows": part_rows_written,
                              "bytes": part_path.stat().st_size})
        elapsed = time.monotonic() - t0
    cpu_after = proc.cpu_times()
    cpu_sec = (cpu_after.user - cpu_before.user) + (cpu_after.system - cpu_before.system)
    total_bytes = sum(p["bytes"] for p in parts)
    for stale in out_dir.glob("part-*.parquet"):
        stale.unlink()
    return {
        "rows_written": written,
        "elapsed_sec": round(elapsed, 3),
        "cpu_sec": round(cpu_sec, 3),
        "cpu_utilization_x": round(cpu_sec / elapsed, 2) if elapsed else None,
        "rows_per_sec": round(written / elapsed, 1),
        "ms_per_pair": round(1000 * elapsed / written, 4),
        "parts_written": len(parts),
        "parquet_mib": round(total_bytes / 2**20, 2),
        "bytes_per_row": round(total_bytes / written, 1) if written else None,
        "chunk_throughput": [round(v, 1) for v in chunk_throughput],
        "throttle": detect_throttle(chunk_throughput),
    }


def stage_b(finalists: list[int]) -> dict:
    """Stage B — finalist worker × analysis batch 격자를 end-to-end로 재검증."""
    global KIWI
    pair_ids, texts, eojeols = load_sample(STAGE_B_N)
    print(f"\nStage B: N={len(texts):,}  finalists={finalists}  batches={STAGE_B_ANALYSIS_BATCHES}")
    reference, scalar = scalar_reference(texts, eojeols)
    print(f"  scalar_reference  {scalar['rows_per_sec']:>9,.1f} rows/s")

    rows = []
    for workers in finalists:
        for analysis_batch in STAGE_B_ANALYSIS_BATCHES:
            guard = MemoryGuard(f"stage_b_w{workers}_b{analysis_batch}")
            KIWI, startup = make_kiwi(workers)
            try:
                perf = run_end_to_end(
                    pair_ids, texts, eojeols, workers=workers,
                    analysis_batch=analysis_batch, arrow_batch=analysis_batch,
                    part_rows=CHECKPOINT_PART_ROWS,
                    out_dir=RUNTIME / f"b_w{workers}_b{analysis_batch}", guard=guard)
            except MemoryGuardAbort as exc:
                print(f"  w={workers:<3} batch={analysis_batch:<6} ABORTED: {exc}")
                rows.append({"num_workers": workers, "analysis_batch": analysis_batch,
                             "status": "REJECTED_MEMORY_GUARD", "error": str(exc),
                             "memory_guard": guard.summary()})
                del KIWI
                gc.collect()
                continue

            # exactness는 동일 config의 analysis-only 재현으로 확인한다.
            candidate = [
                features_from_morphs(m, eojeol_count=e)
                for start, stop in chunk_bounds(len(texts), analysis_batch)
                for m, e in zip(analyze_batch(texts[start:stop], kiwi=KIWI),
                                eojeols[start:stop], strict=True)
            ]
            gate = equality_gate(reference, candidate)
            del candidate, KIWI
            gc.collect()

            summary = guard.summary()
            row = {"num_workers": workers, "analysis_batch": analysis_batch,
                   "arrow_write_batch": analysis_batch, "checkpoint_part_rows": CHECKPOINT_PART_ROWS,
                   "startup_sec": startup, **perf, "equality": gate, "memory_guard": summary,
                   "speedup_vs_scalar": round(scalar["elapsed_sec"] / perf["elapsed_sec"], 2),
                   "status": gate["status"] if summary["worst_status"] == STATUS_GREEN
                   else f"{gate['status']}_MEMORY_{summary['worst_status']}"}
            rows.append(row)
            print(f"  w={workers:<3} batch={analysis_batch:<6} {row['rows_per_sec']:>9,.1f} rows/s  "
                  f"cpu={row['cpu_utilization_x']}x  rss={summary['peak_rss_gib']}GiB  "
                  f"swapΔ={summary['peak_swap_delta_mib']}MiB  parts={row['parts_written']}  "
                  f"mismatch={gate['mismatch_rows']}  {row['throttle']['verdict']}  {row['status']}")

    accepted = [r for r in rows if r.get("status") == "ACCEPTED"]
    accepted.sort(key=lambda r: -r["rows_per_sec"])
    top2 = [{"num_workers": r["num_workers"], "analysis_batch": r["analysis_batch"]} for r in accepted[:2]]
    print(f"\n  Stage B top-2 for final confirmation: {top2}")
    return {"stage": "B", "sample_n": len(texts), "scalar": scalar, "rows": rows, "top2": top2}


def final_confirmation(top2: list[dict]) -> dict:
    """§13 — 상위 2 config만 N=100,000 end-to-end + checkpoint part로 안정성 확인."""
    global KIWI
    pair_ids, texts, eojeols = load_sample(FINAL_N)
    print(f"\nFinal confirmation: N={len(texts):,}  candidates={top2}")
    rows = []
    for cfg in top2:
        workers, analysis_batch = cfg["num_workers"], cfg["analysis_batch"]
        guard = MemoryGuard(f"final_w{workers}_b{analysis_batch}")
        KIWI, startup = make_kiwi(workers)
        try:
            perf = run_end_to_end(
                pair_ids, texts, eojeols, workers=workers,
                analysis_batch=analysis_batch, arrow_batch=analysis_batch,
                part_rows=CHECKPOINT_PART_ROWS,
                out_dir=RUNTIME / f"final_w{workers}_b{analysis_batch}", guard=guard)
        except MemoryGuardAbort as exc:
            print(f"  w={workers} batch={analysis_batch} ABORTED: {exc}")
            rows.append({"num_workers": workers, "analysis_batch": analysis_batch,
                         "status": "REJECTED_MEMORY_GUARD", "error": str(exc),
                         "memory_guard": guard.summary()})
            del KIWI
            gc.collect()
            continue
        del KIWI
        gc.collect()

        chunks = perf["chunk_throughput"]
        head = statistics.median(chunks[: max(1, len(chunks) // 10)])
        tail = statistics.median(chunks[-max(1, len(chunks) // 10):])
        summary = guard.summary()
        row = {**cfg, "startup_sec": startup, **perf, "memory_guard": summary,
               "first_decile_rows_per_sec": round(head, 1),
               "last_decile_rows_per_sec": round(tail, 1),
               "sustained_ratio_last_over_first": round(tail / head, 3) if head else None,
               "status": "ACCEPTED" if summary["worst_status"] == STATUS_GREEN
               else f"MEMORY_{summary['worst_status']}"}
        rows.append(row)
        print(f"  w={workers:<3} batch={analysis_batch:<6} sustained {row['rows_per_sec']:>9,.1f} rows/s  "
              f"first10%={row['first_decile_rows_per_sec']:,.1f} last10%={row['last_decile_rows_per_sec']:,.1f} "
              f"(ratio {row['sustained_ratio_last_over_first']})  rss={summary['peak_rss_gib']}GiB  "
              f"swapΔ={summary['peak_swap_delta_mib']}MiB  {row['throttle']['verdict']}  {row['status']}")

    ok = [r for r in rows if r.get("status") == "ACCEPTED"]
    ok.sort(key=lambda r: -r["rows_per_sec"])          # §15 sustained 기준
    selected = ok[0] if ok else None
    if selected:
        eta_sec = 3_835_988 / selected["rows_per_sec"]
        print(f"\n  SELECTED: num_workers={selected['num_workers']} "
              f"analysis_batch={selected['analysis_batch']}  "
              f"sustained {selected['rows_per_sec']:,.1f} rows/s  "
              f"-> full-cohort ETA {eta_sec / 60:.1f} min")
    return {"stage": "FINAL", "sample_n": len(texts), "rows": rows, "selected": selected}


KIWI: Kiwi | None = None

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "stage_a"
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.mkdir(parents=True, exist_ok=True)
    started = dt.datetime.now(tz=KST)
    boot_guard = MemoryGuard("boot")
    boot = boot_guard.sample()

    print(f"[{started.isoformat(timespec='seconds')}] mode={mode}")
    print(f"  cpu logical={psutil.cpu_count(logical=True)} physical={psutil.cpu_count(logical=False)}")
    print(f"  vm.swappiness={boot_guard.swappiness} (read-only; host policy is never modified)")
    print(f"  MemAvailable={boot.mem_available_gib} GiB  SwapUsed baseline="
          f"{boot_guard.baseline_swap_used / 2**20:.1f} MiB  status={boot.status}")

    payload: dict = {
        "generated_kst": started.isoformat(timespec="seconds"),
        "cpu_logical": psutil.cpu_count(logical=True),
        "cpu_physical": psutil.cpu_count(logical=False),
        "boot_memory": boot.to_dict(),
        "vm_swappiness": boot_guard.swappiness,
        "sample_salt": SAMPLE_SALT,
        "size_contract": {
            "analysis_batch_size": "Kiwi iterable 한 번에 넘기는 text 수",
            "arrow_write_batch_size": "한 번에 RecordBatch로 materialize하는 row 수",
            "checkpoint_part_rows": CHECKPOINT_PART_ROWS,
        },
    }

    if mode == "stage_a":
        payload["stage_a"] = stage_a()
        out_path = REPORT / "MORPH_KIWI_BENCHMARK_STAGE_A.json"
    elif mode == "stage_b":
        prior = json.loads((REPORT / "MORPH_KIWI_BENCHMARK_STAGE_A.json").read_text(encoding="utf-8"))
        payload["stage_b"] = stage_b(prior["stage_a"]["finalists"])
        out_path = REPORT / "MORPH_KIWI_BENCHMARK_STAGE_B.json"
    else:
        prior = json.loads((REPORT / "MORPH_KIWI_BENCHMARK_STAGE_B.json").read_text(encoding="utf-8"))
        payload["final"] = final_confirmation(prior["stage_b"]["top2"])
        out_path = REPORT / "MORPH_KIWI_BENCHMARK_FINAL.json"

    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nwrote {out_path.relative_to(PROJECT_ROOT)}")
