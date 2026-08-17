"""D-05 full-run 독립 검증 (§7).

manifest가 스스로 통과했다고 말한 내용을 물리 parquet에서 다시 계산한다.
검증 로직 자체는 src/tokenization_premium/chunking.py의 validate_chunk_measurements를 재사용한다.
"""

from __future__ import annotations

import json

import duckdb

from tokenization_premium.chunking import (
    CHUNK_RELATIVE_PATH,
    CHUNK_SCHEMA_VERSION,
    CHUNKING_CONFIG_SHA256,
    chunk_schema,
    validate_chunk_measurements,
)
from tokenization_premium.hashing import sha256_file
from tokenization_premium.lineage import (
    CANONICAL_ARTIFACTS,
    CANONICAL_COHORT_N,
    CANONICAL_PAIR_SET_MD5,
    pair_set_md5,
)
from tokenization_premium.paths import PROJECT_ROOT
from tokenization_premium.tokenizer_measurement import PAT_STR_SHA256

MANIFEST = PROJECT_ROOT / "outputs/manifests/CHUNK_O200K_BASE_MANIFEST_v001.json"
REPORT = PROJECT_ROOT / "outputs/manifests/CHUNK_O200K_BASE_VALIDATION_v001.json"
SPILL = PROJECT_ROOT / ".runtime/nb06-validate/spill"


def main() -> None:
    chunk_path = PROJECT_ROOT / CHUNK_RELATIVE_PATH
    token_path = CANONICAL_ARTIFACTS["TOKEN_O200K_BASE_v001"].path
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    SPILL.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute("SET memory_limit='3GB'")
    con.execute("SET threads=8")
    con.execute(f"SET temp_directory='{SPILL.as_posix()}'")
    con.execute("SET preserve_insertion_order=false")

    chunk_rel = f"read_parquet('{chunk_path.as_posix()}')"
    token_rel = f"read_parquet('{token_path.as_posix()}')"

    validate_chunk_measurements(chunk_path, expected_rows=CANONICAL_COHORT_N)

    row = con.execute(f"""
        SELECT count(*), count(DISTINCT pair_id), count(DISTINCT chunk_measurement_id),
               count(DISTINCT tokenizer_measurement_id),
               count(DISTINCT chunking_config_sha256), count(DISTINCT pat_str_sha256),
               sum(CASE WHEN analysis_warning_flag THEN 1 ELSE 0 END),
               sum(CASE WHEN NOT token_equivalence_ok THEN 1 ELSE 0 END),
               sum(CASE WHEN NOT chunk_reconstruction_ok THEN 1 ELSE 0 END),
               min(chunking_config_sha256), min(pat_str_sha256)
        FROM {chunk_rel}
    """).fetchone()
    (rows, pairs, ids, fks, cfg_n, pat_n, warnings, token_bad, recon_bad,
     cfg_sha, pat_sha) = row
    # D-03/D-04와 동일한 규약: schema version은 행에 넣지 않고 manifest와 config hash로 고정한다.
    schema_v = manifest["output"]["schema_version"]

    missing = con.execute(
        f"SELECT count(*) FROM {token_rel} t ANTI JOIN {chunk_rel} c USING (pair_id)").fetchone()[0]
    extra = con.execute(
        f"SELECT count(*) FROM {chunk_rel} c ANTI JOIN {token_rel} t USING (pair_id)").fetchone()[0]
    fk_orphans = con.execute(f"""
        SELECT count(*) FROM {chunk_rel} c ANTI JOIN {token_rel} t
        ON c.tokenizer_measurement_id = t.measurement_id
    """).fetchone()[0]
    # 해시 정의를 다시 적지 않고 canonical helper를 쓴다 (구분자 하나만 달라도 값이 바뀐다).
    pair_md5 = pair_set_md5(chunk_path, con)
    columns = list(con.execute(f"SELECT * FROM {chunk_rel} LIMIT 0").df().columns)
    con.close()

    artifact_sha = sha256_file(chunk_path)
    declared = list(chunk_schema().names)

    checks = {
        "row_count_equals_canonical_cohort": int(rows) == CANONICAL_COHORT_N,
        "pair_id_unique": int(pairs) == int(rows),
        "chunk_measurement_id_unique": int(ids) == int(rows),
        "tokenizer_fk_unique": int(fks) == int(rows),
        "no_missing_vs_d04": int(missing) == 0,
        "no_extra_vs_d04": int(extra) == 0,
        "no_orphan_tokenizer_fk": int(fk_orphans) == 0,
        "pair_set_md5_matches_canonical": pair_md5 == CANONICAL_PAIR_SET_MD5,
        "single_chunking_config": int(cfg_n) == 1 and cfg_sha == CHUNKING_CONFIG_SHA256,
        "single_pat_str_in_artifact": int(pat_n) == 1 and pat_sha == PAT_STR_SHA256,
        "manifest_schema_version_matches": schema_v == CHUNK_SCHEMA_VERSION,
        "physical_columns_match_schema": set(columns) == set(declared),
        "zero_token_equivalence_failures": int(token_bad) == 0,
        "zero_reconstruction_failures": int(recon_bad) == 0,
        "manifest_sha256_matches_artifact": artifact_sha == manifest["output"]["sha256"],
        "manifest_row_count_matches": int(manifest["output"]["row_count"]) == int(rows),
        "r1_periodic_telemetry": bool(manifest["runtime_telemetry"]["r1_periodic_sampling"]),
    }
    status = "PASS" if all(checks.values()) else "FAIL"

    report = {
        "artifact_id": "CHUNK_O200K_BASE_VALIDATION_v001",
        "validated_artifact": str(CHUNK_RELATIVE_PATH),
        "artifact_sha256": artifact_sha,
        "row_count": int(rows),
        "column_count": len(columns),
        "schema_version": schema_v,
        "chunking_config_sha256": cfg_sha,
        "pat_str_sha256": pat_sha,
        "pair_set_md5": pair_md5,
        "canonical_pair_set_md5": CANONICAL_PAIR_SET_MD5,
        "analysis_warning_rows": int(warnings),
        "token_equivalence_failures": int(token_bad),
        "reconstruction_failures": int(recon_bad),
        "anti_join_missing_vs_d04": int(missing),
        "anti_join_extra_vs_d04": int(extra),
        "orphan_tokenizer_measurement_id": int(fk_orphans),
        "runtime_telemetry": {k: v for k, v in manifest["runtime_telemetry"].items()
                              if k != "samples"},
        "checks": checks,
        "validation_status": status,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")

    width = max(len(k) for k in checks)
    for key, ok in checks.items():
        print(f"  {key:<{width}}  {'PASS' if ok else 'FAIL'}")
    print(f"\n  rows={int(rows):,}  cols={len(columns)}  sha256={artifact_sha[:16]}…")
    print(f"  wrote {REPORT.relative_to(PROJECT_ROOT)}")
    print(f"  VALIDATION_STATUS = {status}")
    if status != "PASS":
        raise SystemExit("D-05 검증 실패")


if __name__ == "__main__":
    main()
