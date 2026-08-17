"""REP_FEATURES_v002 빌드 — SSOT §12.2 lexical length 보강 (47 feature 재계산 없음).

Decision: RD-20260817-D02D03-CONFORMANCE-01

v001의 47개 열은 exact value equality로 보존하고, PAIR_REGISTRY_v002의 원문에서
ko_eojeol_count / en_word_count 만 새로 계산해 pair_id exact join으로 결합한다.
메모리는 batch 단위로 bounded 상태를 유지한다.
"""

from __future__ import annotations

import datetime as dt
import json
import time
from zoneinfo import ZoneInfo

import duckdb
import pyarrow as pa
import pyarrow.parquet as pq

from tokenization_premium.hashing import canonical_json_bytes, sha256_bytes, sha256_file
from tokenization_premium.paths import PROJECT_ROOT
from tokenization_premium.progress import ProgressHeartbeat
from tokenization_premium.representation import (
    REP_FEATURES_V2_SCHEMA_VERSION,
    REPRESENTATION_V2_LEXICAL_CONFIG,
    REPRESENTATION_V2_LEXICAL_CONFIG_SHA256,
    lexical_segment_count,
    rep_features_schema,
    rep_features_v002_schema,
)

KST = ZoneInfo("Asia/Seoul")

V1_PATH = PROJECT_ROOT / "data/registry/REP_FEATURES_v001.parquet"
V2_PATH = PROJECT_ROOT / "data/registry/REP_FEATURES_v002.parquet"
PAIR_PATH = PROJECT_ROOT / "data/registry/PAIR_REGISTRY_v002.parquet"
SIDECAR = PROJECT_ROOT / ".runtime/rep-v002/LEXICAL_LENGTH_SIDECAR.parquet"
SPILL = PROJECT_ROOT / ".runtime/rep-v002/duckdb-spill"
MANIFEST = PROJECT_ROOT / "outputs/manifests/REP_FEATURES_MANIFEST_v002.json"
ADJUDICATION = PROJECT_ROOT / "ssot/HumanLebeled/KOEN_G1_HUMAN_AUDIT_FINAL_ADJUDICATION.md"

V1_SHA = "335c20deacb355dc1ca147547ae18e1a5ab1508fe5272508b62ee04ddf819e45"
PAIR_SHA = "95f523d11b0e8fcfd761dee949f082e9b4590b919801441fbcfa3426010bec52"
BATCH_ROWS = 100_000

LEXICAL_SCHEMA = pa.schema([
    pa.field("pair_id", pa.string(), nullable=False),
    pa.field("ko_eojeol_count", pa.int64(), nullable=False),
    pa.field("en_word_count", pa.int64(), nullable=False),
])


def connect() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    con.execute("SET memory_limit='6GB'")
    con.execute("SET threads=8")
    con.execute(f"SET temp_directory='{SPILL.as_posix()}'")
    con.execute("SET preserve_insertion_order=false")
    return con


def build_sidecar(con: duckdb.DuckDBPyConnection, expected_rows: int, run_id: str) -> dict:
    """cohort 원문에서 lexical length만 streaming 계산해 sidecar parquet으로 쓴다."""
    SIDECAR.parent.mkdir(parents=True, exist_ok=True)
    partial = SIDECAR.with_suffix(SIDECAR.suffix + ".partial")
    if partial.exists():
        partial.unlink()

    reader = con.execute(
        "SELECT r.pair_id, p.ko_text_analysis AS ko, p.en_text_analysis AS en "
        f"FROM read_parquet('{V1_PATH.as_posix()}') r "
        f"JOIN read_parquet('{PAIR_PATH.as_posix()}') p USING (pair_id)"
    ).fetch_record_batch(BATCH_ROWS)

    zero_ko = zero_en = 0
    written = 0
    writer = pq.ParquetWriter(partial, schema=LEXICAL_SCHEMA, compression="zstd")
    try:
        with ProgressHeartbeat(
            run_id=run_id, phase="REP_V002", stage="LEXICAL_LENGTH",
            total=expected_rows, progress_dir=PROJECT_ROOT / ".runtime/progress",
        ) as heartbeat:
            for batch in reader:
                pair_ids = batch.column("pair_id").to_pylist()
                ko_counts = [lexical_segment_count(t) for t in batch.column("ko").to_pylist()]
                en_counts = [lexical_segment_count(t) for t in batch.column("en").to_pylist()]
                zero_ko += sum(1 for c in ko_counts if c == 0)
                zero_en += sum(1 for c in en_counts if c == 0)
                writer.write_batch(pa.RecordBatch.from_pydict(
                    {"pair_id": pair_ids, "ko_eojeol_count": ko_counts, "en_word_count": en_counts},
                    schema=LEXICAL_SCHEMA))
                written += len(pair_ids)
                heartbeat.update(len(pair_ids))
                del pair_ids, ko_counts, en_counts, batch   # bounded memory
    finally:
        writer.close()

    if written != expected_rows:
        partial.unlink(missing_ok=True)
        raise ValueError(f"lexical sidecar row count {written} != expected {expected_rows}")
    if zero_ko or zero_en:
        partial.unlink(missing_ok=True)
        raise ValueError(f"HARD_INVALID: zero lexical count (ko={zero_ko}, en={zero_en})")
    partial.replace(SIDECAR)
    return {"rows": written, "zero_ko": zero_ko, "zero_en": zero_en}


def build_v002(con: duckdb.DuckDBPyConnection) -> None:
    """v001 열을 그대로 투영하고 lexical length를 exact pair_id join으로 결합한다."""
    if V2_PATH.exists():
        raise FileExistsError("REP_FEATURES_v002.parquet이 이미 존재한다; 자동 덮어쓰기는 금지된다")
    select = ", ".join(
        f"s.{f.name}" if f.name in ("ko_eojeol_count", "en_word_count") else f"v1.{f.name}"
        for f in rep_features_v002_schema()
    )
    partial = V2_PATH.with_suffix(V2_PATH.suffix + ".partial")
    con.execute(
        f"COPY (SELECT {select} "
        f"FROM read_parquet('{V1_PATH.as_posix()}') v1 "
        f"JOIN read_parquet('{SIDECAR.as_posix()}') s USING (pair_id)) "
        f"TO '{partial.as_posix()}' (FORMAT PARQUET, COMPRESSION ZSTD)")
    partial.replace(V2_PATH)


def validate(con: duckdb.DuckDBPyConnection, expected_rows: int, excluded: list[str]) -> dict:
    """acceptance criteria 1-6을 v002 산출물에 대해 직접 검증한다."""
    v2 = f"read_parquet('{V2_PATH.as_posix()}')"
    v1 = f"read_parquet('{V1_PATH.as_posix()}')"
    checks: dict[str, object] = {}

    rows, distinct = con.execute(f"SELECT COUNT(*), COUNT(DISTINCT pair_id) FROM {v2}").fetchone()
    checks["row_count"] = rows
    checks["distinct_pair_id"] = distinct

    # pair-id set exact equality against v001 (both directions)
    only_v2, only_v1 = con.execute(
        f"SELECT (SELECT COUNT(*) FROM (SELECT pair_id FROM {v2} EXCEPT SELECT pair_id FROM {v1})), "
        f"       (SELECT COUNT(*) FROM (SELECT pair_id FROM {v1} EXCEPT SELECT pair_id FROM {v2}))"
    ).fetchone()
    checks["pair_ids_only_in_v002"] = only_v2
    checks["pair_ids_only_in_v001"] = only_v1

    con.execute("CREATE OR REPLACE TEMP TABLE excluded(pair_id VARCHAR)")
    con.executemany("INSERT INTO excluded VALUES (?)", [(i,) for i in excluded])
    checks["g1_excluded_present"] = con.execute(
        f"SELECT COUNT(*) FROM {v2} JOIN excluded USING (pair_id)").fetchone()[0]

    # exact value equality of every v001 column
    v1_cols = [f.name for f in rep_features_schema() if f.name != "pair_id"]
    diff_expr = " OR ".join(f"a.{c} IS DISTINCT FROM b.{c}" for c in v1_cols)
    checks["v001_columns_compared"] = len(v1_cols)
    checks["v001_value_mismatch_rows"] = con.execute(
        f"SELECT COUNT(*) FROM {v2} a JOIN {v1} b USING (pair_id) WHERE {diff_expr}").fetchone()[0]

    new_stats = con.execute(
        "SELECT SUM((ko_eojeol_count IS NULL)::INT), SUM((en_word_count IS NULL)::INT), "
        "MIN(ko_eojeol_count), MAX(ko_eojeol_count), MIN(en_word_count), MAX(en_word_count), "
        "AVG(ko_eojeol_count), AVG(en_word_count), "
        "SUM((ko_eojeol_count <= 0)::INT), SUM((en_word_count <= 0)::INT), "
        "SUM((ko_eojeol_count > ko_codepoint_count)::INT), "
        "SUM((en_word_count > en_codepoint_count)::INT), "
        "SUM((ko_eojeol_count <> ko_space_run_count + 1)::INT), "
        "SUM((en_word_count <> en_space_run_count + 1)::INT) "
        f"FROM {v2}").fetchone()
    (checks["ko_eojeol_null"], checks["en_word_null"], checks["ko_eojeol_min"],
     checks["ko_eojeol_max"], checks["en_word_min"], checks["en_word_max"],
     checks["ko_eojeol_mean"], checks["en_word_mean"], checks["ko_eojeol_nonpositive"],
     checks["en_word_nonpositive"], checks["ko_eojeol_gt_codepoints"],
     checks["en_word_gt_codepoints"], checks["ko_eojeol_ne_spacerun_plus1"],
     checks["en_word_ne_spacerun_plus1"]) = new_stats

    failures = []
    if rows != expected_rows or distinct != expected_rows:
        failures.append("row_count / distinct pair_id != expected")
    if only_v2 or only_v1:
        failures.append("pair-id set differs from v001")
    if checks["g1_excluded_present"]:
        failures.append("G1-excluded pair_id present")
    if checks["v001_value_mismatch_rows"]:
        failures.append("v001 column value equality broken")
    if checks["ko_eojeol_null"] or checks["en_word_null"]:
        failures.append("new lexical field has NULL")
    if checks["ko_eojeol_nonpositive"] or checks["en_word_nonpositive"]:
        failures.append("HARD_INVALID: lexical count <= 0")
    if checks["ko_eojeol_gt_codepoints"] or checks["en_word_gt_codepoints"]:
        failures.append("lexical count exceeds codepoint count")
    checks["failures"] = failures
    return checks


if __name__ == "__main__":
    import re

    RUN_ID = "REP_V002_" + dt.datetime.now(tz=KST).strftime("%Y%m%dT%H%M%S")
    SPILL.mkdir(parents=True, exist_ok=True)
    start = dt.datetime.now(tz=KST)
    t0 = time.monotonic()

    print(f"[{start.isoformat(timespec='seconds')}] run_id={RUN_ID}")
    for path, expected in ((V1_PATH, V1_SHA), (PAIR_PATH, PAIR_SHA)):
        actual = sha256_file(path)
        print(f"  input {path.name:32s} {'PASS' if actual == expected else 'FAIL'} {actual}")
        if actual != expected:
            raise SystemExit("input artifact hash mismatch — halt")

    excluded_ids = sorted(set(re.findall(r"pair_[0-9a-f]{64}", ADJUDICATION.read_text(encoding="utf-8"))))
    connection = connect()
    try:
        expected_rows = connection.execute(f"SELECT COUNT(*) FROM read_parquet('{V1_PATH.as_posix()}')").fetchone()[0]
        print(f"  expected rows (derived from v001, no hardcoded constant): {expected_rows:,}")

        t = time.monotonic()
        side = build_sidecar(connection, expected_rows, RUN_ID)
        print(f"  lexical sidecar: {side['rows']:,} rows in {time.monotonic()-t:.1f}s")

        t = time.monotonic()
        build_v002(connection)
        print(f"  v002 written in {time.monotonic()-t:.1f}s")

        result = validate(connection, expected_rows, excluded_ids)
    finally:
        connection.close()

    v2_sha = sha256_file(V2_PATH)
    schema_hash = sha256_bytes(canonical_json_bytes(
        [{"name": f.name, "type": str(f.type), "nullable": f.nullable} for f in rep_features_v002_schema()]))
    end = dt.datetime.now(tz=KST)

    print("\n  validation:")
    for k, v in result.items():
        if k != "failures":
            print(f"    {k:34s} {v}")
    print(f"    {'FAILURES':34s} {result['failures'] or 'NONE'}")

    manifest = {
        "artifact_id": "REP_FEATURES_MANIFEST_v002",
        "run_id": RUN_ID,
        "run_mode": "CONFORMANCE_RESTORATION",
        "decision_id": "RD-20260817-D02D03-CONFORMANCE-01",
        "classification": "SSOT_CONFORMANCE_RESTORATION",
        "spec_ref": "SSOT §12.2 lexical length (ko_eojeol_count, en_word_count)",
        "input": {
            "rep_features_v001": {"path": "data/registry/REP_FEATURES_v001.parquet", "sha256": V1_SHA},
            "pair_registry_v002": {"path": "data/registry/PAIR_REGISTRY_v002.parquet", "sha256": PAIR_SHA},
        },
        "output": {
            "path": "data/registry/REP_FEATURES_v002.parquet",
            "sha256": v2_sha,
            "row_count": result["row_count"],
            "column_count": len(rep_features_v002_schema()),
            "schema_version": REP_FEATURES_V2_SCHEMA_VERSION,
            "schema_sha256": schema_hash,
        },
        "method": (
            "v001의 47개 feature는 재계산하지 않고 pair_id exact join으로 그대로 투영했다. "
            "PAIR_REGISTRY_v002 원문에서 lexical length 2개 열만 새로 계산했다."
        ),
        "lexical_rule": REPRESENTATION_V2_LEXICAL_CONFIG,
        "lexical_rule_sha256": REPRESENTATION_V2_LEXICAL_CONFIG_SHA256,
        "validation": {k: v for k, v in result.items()},
        "validation_status": "PASS" if not result["failures"] else "FAIL",
        "recomputed_v001_features": False,
        "start_kst": start.isoformat(timespec="seconds"),
        "end_kst": end.isoformat(timespec="seconds"),
        "stage_duration_sec": round(time.monotonic() - t0, 3),
        "gate_claims": {
            "G2_representation_integrity": "NOT_CLAIMED — research adjudication (Claude-B)",
        },
        "status": "CONFORMANCE_RESTORED",
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    print(f"\n  v002 sha256   {v2_sha}")
    print(f"  schema sha256 {schema_hash}")
    print(f"  manifest      {MANIFEST.relative_to(PROJECT_ROOT)} ({sha256_file(MANIFEST)})")
    if result["failures"]:
        raise SystemExit(f"VALIDATION FAILED: {result['failures']}")
    print("\nREP_FEATURES_v002 = PASS")
