"""D-05 full-population 실행 (N=3,835,988).

전제조건 (§7): R1_STATUS=PASS 이고 pilot invariant total_mismatch == 0 일 때만 실행한다.
연구 로직은 src/tokenization_premium/chunking.py에 있으며, 이 파일은 실행 wrapper다.
"""

from __future__ import annotations

import gc
import json

import duckdb

from tokenization_premium.chunking import CHUNK_RELATIVE_PATH, execute_chunk_run
from tokenization_premium.lineage import CANONICAL_ARTIFACTS, assert_canonical_artifact
from tokenization_premium.paths import PROJECT_ROOT

CACHE = PROJECT_ROOT / ".runtime/tiktoken-cache"
RUNTIME = PROJECT_ROOT / ".runtime/nb06-full"
PILOT = PROJECT_ROOT / "outputs/manifests/CHUNK_O200K_BASE_PILOT_MANIFEST_v001.json"
MANIFEST = PROJECT_ROOT / "outputs/manifests/CHUNK_O200K_BASE_MANIFEST_v001.json"


def main() -> None:
    # ---- §7 gate: pilot이 통과하지 않았으면 full run을 시작하지 않는다 ----------
    pilot = json.loads(PILOT.read_text(encoding="utf-8"))
    if not pilot["full_run_authorized"]:
        raise SystemExit("pilot이 full run을 인가하지 않았다 — 실행 중단")
    print(f"  pilot gate OK  mismatch={pilot['total_mismatch']}  "
          f"r1={pilot['runtime_telemetry']['r1_periodic_sampling']}")

    # ---- fail-closed lineage: 무거운 hash/pair-set 검증을 먼저 끝내고 메모리를 돌려준다 ----
    RUNTIME.mkdir(parents=True, exist_ok=True)
    spill = RUNTIME / "preflight-spill"
    spill.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute("SET memory_limit='2GB'")
    con.execute("SET threads=4")
    con.execute(f"SET temp_directory='{spill.as_posix()}'")
    tok = assert_canonical_artifact("TOKEN_O200K_BASE_v001", verify_pair_set=True, con=con)
    pair = assert_canonical_artifact("PAIR_REGISTRY_v002", con=con)
    print(f"  D-04 {tok['identity']} sha {tok['sha256'][:16]}… N={tok['row_count']:,}")
    print(f"  PAIR sha {pair['sha256'][:16]}… N={pair['row_count']:,}")
    con.close()                      # heavy run 이전에 pre-flight 메모리를 반환한다
    del con
    gc.collect()

    manifest = execute_chunk_run(
        project_root=PROJECT_ROOT,
        token_path=CANONICAL_ARTIFACTS["TOKEN_O200K_BASE_v001"].path,
        pair_registry_path=CANONICAL_ARTIFACTS["PAIR_REGISTRY_v002"].path,
        output_path=PROJECT_ROOT / CHUNK_RELATIVE_PATH,
        runtime_dir=RUNTIME,
        run_id="D05_FULL_v001",
        run_mode="FULL",
        limit=None,
        batch_rows=2_500,
        cache_dir=CACHE,
        telemetry_interval_sec=10.0,
        duckdb_memory_limit="3GB",
        duckdb_threads=8,
    )
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    print(f"\n  wrote {MANIFEST.relative_to(PROJECT_ROOT)}")
    print(f"  rows={manifest['output']['row_count']:,}  "
          f"sha256={manifest['output']['sha256'][:16]}…")


if __name__ == "__main__":
    main()
