"""Final-cohort D-03 (Kiwi) / D-04 (o200k) 전집단 실행 — 단일 workload runner.

Authorization: MORPHOLOGY_SANITY_REVIEW_PASS + MORPHOLOGY_FULL_RUN_AUTHORIZED
               (0a6457a research(g4): adjudicate corrected morphology manual audit)

usage:
  python scripts/run_full_measurement.py morph
  python scripts/run_full_measurement.py tok

각 workload는 별도 process/tmp에서 돌며, 상위 orchestrator가 동시에 띄운다.
"""

from __future__ import annotations

import datetime as dt
import json
import sys
from zoneinfo import ZoneInfo

from tokenization_premium.hashing import canonical_json_bytes, sha256_bytes
from tokenization_premium.memory_guard import MemoryGuard
from tokenization_premium.morphology import (
    MORPH_FEATURES_RELATIVE_PATH,
    MORPHOLOGY_CONFIG,
    MORPHOLOGY_CONFIG_SHA256,
    execute_morphology_run,
    morph_features_schema,
)
from tokenization_premium.paths import PROJECT_ROOT
from tokenization_premium.tokenizer_measurement import (
    TOKEN_MEASUREMENT_RELATIVE_PATH,
    execute_token_measurement_run,
    token_measurement_schema,
)

KST = ZoneInfo("Asia/Seoul")
REP_V2 = PROJECT_ROOT / "data/registry/REP_FEATURES_v002.parquet"
PAIR = PROJECT_ROOT / "data/registry/PAIR_REGISTRY_v002.parquet"
CACHE = PROJECT_ROOT / ".runtime/tiktoken-cache"

# benchmark 선정 config (Addendum §4, concurrency probe로 재확인).
KIWI_WORKERS = 24
ANALYSIS_BATCH = 2_500
TOK_BATCH = 2_500


def schema_hash(schema) -> str:
    return sha256_bytes(canonical_json_bytes(
        [{"name": f.name, "type": str(f.type), "nullable": f.nullable} for f in schema]))


def git_sha() -> str:
    import subprocess
    return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                          cwd=PROJECT_ROOT).stdout.strip()


if __name__ == "__main__":
    kind = sys.argv[1]
    stamp = dt.datetime.now(tz=KST).strftime("%Y%m%dT%H%M%S")

    if kind == "morph":
        run_id = f"MORPH_FULL_{stamp}"
        out = PROJECT_ROOT / MORPH_FEATURES_RELATIVE_PATH
        runtime = PROJECT_ROOT / ".runtime/morph-full" / run_id
        manifest_path = PROJECT_ROOT / "outputs/manifests/MORPH_FEATURES_KIWI_MANIFEST_v001.json"
        guard = MemoryGuard(run_id)
        guard.sample()
        manifest = execute_morphology_run(
            project_root=PROJECT_ROOT,
            rep_features_v002_path=REP_V2,
            pair_registry_path=PAIR,
            output_path=out,
            runtime_dir=runtime,
            run_id=run_id,
            run_mode="FULL_POPULATION",
            limit=None,
            num_workers=KIWI_WORKERS,
            batch_rows=ANALYSIS_BATCH,
        )
        guard.sample()
        manifest.update({
            "artifact_id": "MORPH_FEATURES_KIWI_MANIFEST_v001",
            "ssot_naming_ref": "SSOT §38 MORPH_FEATURES_KIWI_v001.parquet",
            "authorization": {
                "verdicts": ["MORPHOLOGY_SANITY_REVIEW_PASS", "MORPHOLOGY_FULL_RUN_AUTHORIZED"],
                "adjudication_commit": "0a6457a8c8a46b6d1502b18b9a1c7e51791caca5",
                "note": "MORPHOLOGY_FULL_RUN_AUTHORIZED != G4 PASS",
            },
            "morphology_config": MORPHOLOGY_CONFIG,
            "morphology_config_sha256": MORPHOLOGY_CONFIG_SHA256,
            "schema_sha256": schema_hash(morph_features_schema()),
            "execution_code_commit": git_sha(),
            "memory_guard": guard.summary(),
            "engine": {"num_workers": KIWI_WORKERS, "analysis_batch": ANALYSIS_BATCH,
                       "arrow_write_batch": ANALYSIS_BATCH},
        })
    else:
        run_id = f"TOK_FULL_{stamp}"
        out = PROJECT_ROOT / TOKEN_MEASUREMENT_RELATIVE_PATH
        runtime = PROJECT_ROOT / ".runtime/tok-full" / run_id
        manifest_path = PROJECT_ROOT / "outputs/manifests/TOKEN_O200K_BASE_MANIFEST_v001.json"
        guard = MemoryGuard(run_id)
        guard.sample()
        manifest = execute_token_measurement_run(
            project_root=PROJECT_ROOT,
            rep_features_path=REP_V2,
            pair_registry_path=PAIR,
            output_path=out,
            runtime_dir=runtime,
            run_id=run_id,
            run_mode="FULL_POPULATION",
            limit=None,
            batch_rows=TOK_BATCH,
            cache_dir=CACHE,
        )
        guard.sample()
        manifest.update({
            "artifact_id": "TOKEN_O200K_BASE_MANIFEST_v001",
            "ssot_naming_ref": "SSOT §38 TOKEN_O200K_BASE_v001.parquet",
            "schema_sha256": schema_hash(token_measurement_schema()),
            "execution_code_commit": git_sha(),
            "memory_guard": guard.summary(),
            "engine": {"batch_rows": TOK_BATCH},
        })

    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                             encoding="utf-8")
    print(f"RESULT {kind} rows={manifest['output']['row_count']} "
          f"sec={manifest['stage_duration_sec']} rps={manifest['rows_per_sec']} "
          f"sha={manifest['output']['sha256']}")
    print(f"manifest {manifest_path.relative_to(PROJECT_ROOT)}")
