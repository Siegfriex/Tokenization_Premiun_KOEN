"""D-05 bounded pilot — §5 불변식 전수 확인. full run의 게이트다.

V2의 NB06_TARGET_STRATA는 표본 선정 보조로만 참고 가능하며, V2 숫자는 evidence로 쓰지 않는다.
표본은 결정적 해시로 뽑고, 층위 커버리지는 canonical artifact에서 직접 읽는다.
"""

from __future__ import annotations

import datetime as dt
import json
import sys
from zoneinfo import ZoneInfo

import duckdb

from tokenization_premium.chunking import (
    CHUNKING_CONFIG_SHA256,
    ChunkInvariantViolation,
    assert_tokenizer_identity,
    build_chunk_record,
    classify_chunk,
    regex_chunks,
)
from tokenization_premium.lineage import CANONICAL_ARTIFACTS, assert_canonical_artifact
from tokenization_premium.paths import PROJECT_ROOT
from tokenization_premium.telemetry import RuntimeTelemetry
from tokenization_premium.tokenizer_measurement import load_o200k_base_offline

KST = ZoneInfo("Asia/Seoul")
CACHE = PROJECT_ROOT / ".runtime/tiktoken-cache"
RUNTIME = PROJECT_ROOT / ".runtime/nb06-pilot"
REPORT = PROJECT_ROOT / "outputs/manifests/CHUNK_O200K_BASE_PILOT_MANIFEST_v001.json"
SALT = "D05_PILOT_v001"
PILOT_N = int(sys.argv[1]) if len(sys.argv) > 1 else 20_000


def connect() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    con.execute("SET memory_limit='5GB'")
    con.execute("SET threads=8")
    con.execute("SET preserve_insertion_order=false")
    (RUNTIME / "spill").mkdir(parents=True, exist_ok=True)
    con.execute(f"SET temp_directory='{(RUNTIME / 'spill').as_posix()}'")
    return con


if __name__ == "__main__":
    started = dt.datetime.now(tz=KST)
    RUNTIME.mkdir(parents=True, exist_ok=True)
    con = connect()

    # ---- fail-closed canonical inputs -------------------------------------
    TOK = assert_canonical_artifact("TOKEN_O200K_BASE_v001", verify_pair_set=True, con=con)
    PAIR = assert_canonical_artifact("PAIR_REGISTRY_v002", con=con)
    print(f"[{started.isoformat(timespec='seconds')}] D-05 PILOT  N={PILOT_N:,}")
    print(f"  D-04 {TOK['identity']}  sha {TOK['sha256'][:16]}…  N={TOK['row_count']:,}")

    encoding = load_o200k_base_offline(CACHE)
    identity = assert_tokenizer_identity(encoding)
    print(f"  tokenizer identity MATCH  pat_str {identity['pat_str_sha256'][:16]}…")
    print(f"  chunking config    {CHUNKING_CONFIG_SHA256[:16]}…")

    T = f"read_parquet('{CANONICAL_ARTIFACTS['TOKEN_O200K_BASE_v001'].path.as_posix()}')"
    P = f"read_parquet('{CANONICAL_ARTIFACTS['PAIR_REGISTRY_v002'].path.as_posix()}')"

    # ---- deterministic stratified-ish sample -------------------------------
    rows = con.execute(f"""
        SELECT t.pair_id, t.measurement_id, p.ko_text_analysis AS ko, p.en_text_analysis AS en,
               t.ko_token_ids, t.en_token_ids, p.domain, p.length_stratum, p.translation_direction
        FROM {T} t JOIN {P} p USING (pair_id)
        ORDER BY md5(t.pair_id || '{SALT}') LIMIT {PILOT_N}
    """).fetchall()
    print(f"  deterministic sample n={len(rows):,} (salt='{SALT}')")

    # ---- invariants --------------------------------------------------------
    concat_failures, empty_chunks, order_failures = 0, 0, 0
    ko_id_mismatch, en_id_mismatch, count_mismatch = 0, 0, 0
    warn_rows, type_share_bad, unclassified = 0, 0, 0
    failure_examples: list[dict] = []
    total_chunks = 0

    with RuntimeTelemetry(run_id="D05_PILOT", stage="PILOT_INVARIANTS",
                          total=len(rows), interval_sec=2.0) as tel:
        for pid, mid, ko, en, ko_ids, en_ids, *_ in rows:
            try:
                ko_chunks = regex_chunks(ko, encoding=encoding)
                en_chunks = regex_chunks(en, encoding=encoding)
            except ChunkInvariantViolation as exc:
                concat_failures += 1
                if len(failure_examples) < 20:
                    failure_examples.append({"pair_id": pid, "kind": "RECONSTRUCTION",
                                             "detail": str(exc)[:200]})
                tel.update(1)
                continue

            if "".join(ko_chunks) != ko or "".join(en_chunks) != en:
                concat_failures += 1
            if any(not c for c in ko_chunks + en_chunks):
                empty_chunks += 1
            if ko_chunks != regex_chunks(ko, encoding=encoding):
                order_failures += 1
            total_chunks += len(ko_chunks) + len(en_chunks)
            if any(classify_chunk(c) not in
                   ("letter", "number", "punctuation", "whitespace") for c in ko_chunks + en_chunks):
                unclassified += 1

            record = build_chunk_record(pid, mid, ko, en, ko_ids, en_ids, encoding=encoding)
            if not record["token_equivalence_ok"]:
                if "KO_TOKEN_FLATTEN_MISMATCH" in record["analysis_warning_reason"]:
                    ko_id_mismatch += 1
                if "EN_TOKEN_FLATTEN_MISMATCH" in record["analysis_warning_reason"]:
                    en_id_mismatch += 1
                if len(failure_examples) < 20:
                    failure_examples.append({"pair_id": pid, "kind": "TOKEN_ID",
                                             "detail": record["analysis_warning_reason"]})
            if record["ko_chunk_token_total"] != len(ko_ids) or \
               record["en_chunk_token_total"] != len(en_ids):
                count_mismatch += 1
            if record["analysis_warning_flag"]:
                warn_rows += 1
            for side in ("ko", "en"):
                share = sum(record[f"{side}_chunk_type_share_{t}"]
                            for t in ("letter", "number", "punctuation", "whitespace"))
                if abs(share - 1.0) > 1e-9:
                    type_share_bad += 1
            tel.update(1)

    telemetry = tel.summary()
    invariants = {
        "1_concat_reconstruction_failures": concat_failures,
        "1b_empty_chunks": empty_chunks,
        "2_lost_or_duplicated_span": concat_failures,   # regex_chunks가 둘 다 fail-closed로 잡는다
        "3_chunk_order_nondeterministic": order_failures,
        "4_ko_token_id_mismatch": ko_id_mismatch,
        "4_en_token_id_mismatch": en_id_mismatch,
        "5_token_count_mismatch": count_mismatch,
        "6_unclassified_chunk_type": unclassified,
        "6b_type_share_not_one": type_share_bad,
        "warning_rows": warn_rows,
    }
    total_mismatch = sum(v for k, v in invariants.items() if k != "warning_rows")

    print("\n  §5 invariants:")
    for k, v in invariants.items():
        print(f"    {k:36s} {v}")
    print(f"\n  total chunks inspected : {total_chunks:,}")
    print(f"  TOTAL MISMATCH         : {total_mismatch}")
    print(f"  telemetry samples      : {telemetry['sample_count']}  "
          f"periodic={telemetry['r1_periodic_sampling']}  "
          f"min_mem={telemetry['min_mem_available_gib']} GiB  peak_rss={telemetry['peak_rss_gib']} GiB")

    coverage = {}
    for col in ("domain", "length_stratum", "translation_direction"):
        idx = {"domain": 6, "length_stratum": 7, "translation_direction": 8}[col]
        counts: dict[str, int] = {}
        for r in rows:
            counts[str(r[idx])] = counts.get(str(r[idx]), 0) + 1
        coverage[col] = dict(sorted(counts.items()))
    print(f"  coverage domain        : {coverage['domain']}")
    print(f"  coverage length        : {coverage['length_stratum']}")

    payload = {
        "artifact_id": "CHUNK_O200K_BASE_PILOT_MANIFEST_v001",
        "run_mode": "PILOT",
        "generated_kst": started.isoformat(timespec="seconds"),
        "pilot_n": len(rows),
        "sampling_salt": SALT,
        "sampling_note": "deterministic md5(pair_id||salt); V2 NB06_TARGET_STRATA는 evidence로 쓰지 않았다",
        "input": {"token_o200k_base": {"sha256": TOK["sha256"], "row_count": TOK["row_count"]},
                  "pair_registry_v002": {"sha256": PAIR["sha256"]}},
        "tokenizer_identity": identity,
        "chunking_config_sha256": CHUNKING_CONFIG_SHA256,
        "invariants": invariants,
        "total_mismatch": total_mismatch,
        "total_chunks_inspected": total_chunks,
        "failure_examples": failure_examples,
        "coverage": coverage,
        "runtime_telemetry": telemetry,
        "full_run_authorized": total_mismatch == 0 and telemetry["r1_periodic_sampling"],
    }
    REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")
    con.close()
    print(f"\n  wrote {REPORT.relative_to(PROJECT_ROOT)}")
    print(f"  FULL_RUN_AUTHORIZED = {payload['full_run_authorized']}")
    if total_mismatch:
        raise SystemExit("PILOT MISMATCH > 0 — full run 금지")
