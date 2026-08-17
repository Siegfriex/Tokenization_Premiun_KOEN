"""D-05 물리 artifact와 manifest에서 시각화용 aggregate를 추출한다.

이 스크립트만 canonical parquet을 읽는다. 여기서 만든 JSON이 커밋되고,
build_nb06_figures.py는 그 JSON만 읽어 Git checkout만으로 figure를 재생성한다.

원문(raw KO/EN text), regex chunk 문자열, token ID 배열은 출력에 담지 않는다.
집계 수치만 담으며, 모든 값에 출처(provenance)를 병기한다.
"""

from __future__ import annotations

import json

import duckdb

from tokenization_premium.chunking import CHUNK_RELATIVE_PATH, CHUNK_SCHEMA_VERSION, CHUNK_TYPES
from tokenization_premium.hashing import sha256_file
from tokenization_premium.lineage import CANONICAL_ARTIFACTS
from tokenization_premium.paths import PROJECT_ROOT

PACKAGE = PROJECT_ROOT / "docs/results/nb06_d05"
OUT = PACKAGE / "data/NB06_D05_VISUAL_DATA_v001.json"
MANIFEST = PROJECT_ROOT / "outputs/manifests/CHUNK_O200K_BASE_MANIFEST_v001.json"
PILOT = PROJECT_ROOT / "outputs/manifests/CHUNK_O200K_BASE_PILOT_MANIFEST_v001.json"
VALIDATION = PROJECT_ROOT / "outputs/manifests/CHUNK_O200K_BASE_VALIDATION_v001.json"
SPILL = PROJECT_ROOT / ".runtime/nb06-visual/spill"


def connect() -> duckdb.DuckDBPyConnection:
    SPILL.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute("SET memory_limit='3GB'")
    con.execute("SET threads=8")
    con.execute("SET preserve_insertion_order=false")
    con.execute(f"SET temp_directory='{SPILL.as_posix()}'")
    return con


def side_profile(con: duckdb.DuckDBPyConnection, relation: str, side: str) -> dict[str, float]:
    shares = ", ".join(f"avg({side}_chunk_type_share_{t})" for t in CHUNK_TYPES)
    row = con.execute(f"""
        SELECT avg({side}_chunk_count), median({side}_chunk_count),
               avg({side}_tokens_per_chunk), median({side}_tokens_per_chunk),
               avg({side}_mean_chunk_bytes), avg({side}_p90_chunk_bytes),
               avg({side}_chunk_token_total), {shares}
        FROM {relation}
    """).fetchone()
    keys = ["mean_chunk_count", "median_chunk_count", "mean_tokens_per_chunk",
            "median_tokens_per_chunk", "mean_chunk_bytes", "mean_p90_chunk_bytes",
            "mean_token_total", *[f"chunk_type_share_{t}" for t in CHUNK_TYPES]]
    return {k: round(float(v), 6) for k, v in zip(keys, row, strict=True)}


def main() -> None:
    chunk_path = PROJECT_ROOT / CHUNK_RELATIVE_PATH
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    pilot = json.loads(PILOT.read_text(encoding="utf-8"))
    validation = json.loads(VALIDATION.read_text(encoding="utf-8"))

    con = connect()
    relation = f"read_parquet('{chunk_path.as_posix()}')"

    ko = side_profile(con, relation, "ko")
    en = side_profile(con, relation, "en")

    decomposition = con.execute(f"""
        SELECT avg(ln(ko_chunk_count::DOUBLE / en_chunk_count)),
               avg(ln(ko_tokens_per_chunk / en_tokens_per_chunk)),
               avg(ln(ko_chunk_token_total::DOUBLE / en_chunk_token_total)),
               max(abs(ln(ko_chunk_count::DOUBLE / en_chunk_count)
                       + ln(ko_tokens_per_chunk / en_tokens_per_chunk)
                       - ln(ko_chunk_token_total::DOUBLE / en_chunk_token_total))),
               avg(pair_chunk_ratio), median(pair_chunk_ratio)
        FROM {relation}
    """).fetchone()

    # figure의 분포 패널용 히스토그램. 개별 행이 아니라 bin 개수만 저장한다.
    def histogram(expression: str, lo: float, hi: float, bins: int) -> dict[str, list[float]]:
        rows = con.execute(f"""
            SELECT bucket, count(*) FROM (
                SELECT least({bins} - 1, greatest(0,
                    floor(({expression} - {lo}) / (({hi} - {lo}) / {bins}))))::INTEGER AS bucket
                FROM {relation})
            GROUP BY bucket ORDER BY bucket
        """).fetchall()
        counts = dict.fromkeys(range(bins), 0)
        counts.update({int(b): int(c) for b, c in rows})
        width = (hi - lo) / bins
        return {"bin_edges_lo": [round(lo + i * width, 6) for i in range(bins)],
                "bin_width": round(width, 6),
                "counts": [counts[i] for i in range(bins)]}

    histograms = {
        "ko_tokens_per_chunk": histogram("ko_tokens_per_chunk", 0.5, 4.5, 40),
        "en_tokens_per_chunk": histogram("en_tokens_per_chunk", 0.5, 4.5, 40),
        "ko_chunk_count": histogram("ko_chunk_count::DOUBLE", 0, 60, 40),
        "en_chunk_count": histogram("en_chunk_count::DOUBLE", 0, 60, 40),
        "pair_chunk_ratio": histogram("pair_chunk_ratio", 0, 2.0, 40),
    }
    con.close()

    telemetry = manifest["runtime_telemetry"]
    samples = [{k: s[k] for k in ("elapsed_sec", "rows_processed", "rows_per_second",
                                  "rss_gib", "mem_available_gib", "swap_used_mib",
                                  "memory_status")}
               for s in telemetry["samples"]]

    payload = {
        "artifact_id": "NB06_D05_VISUAL_DATA_v001",
        "content": "aggregate numerics only; no raw text, no chunk strings, no token id arrays",
        "provenance": {
            "d05_artifact": {
                "path": str(CHUNK_RELATIVE_PATH),
                "sha256": sha256_file(chunk_path),
                "row_count": manifest["output"]["row_count"],
                "column_count": manifest["output"]["column_count"],
                "schema_version": CHUNK_SCHEMA_VERSION,
                "pair_set_md5": validation["pair_set_md5"],
            },
            "d04_authority": {
                "name": "TOKEN_O200K_BASE_v001",
                "sha256": CANONICAL_ARTIFACTS["TOKEN_O200K_BASE_v001"].sha256,
                "role": "sole authority for token IDs, token counts and Tokenization Premium",
            },
            "manifests": {
                "full_run": {"path": str(MANIFEST.relative_to(PROJECT_ROOT)),
                             "sha256": sha256_file(MANIFEST)},
                "pilot": {"path": str(PILOT.relative_to(PROJECT_ROOT)),
                          "sha256": sha256_file(PILOT)},
                "validation": {"path": str(VALIDATION.relative_to(PROJECT_ROOT)),
                               "sha256": sha256_file(VALIDATION)},
            },
            "aggregates_recomputed_from": "physical parquet via extract_visual_data.py",
        },
        "tokenizer": {
            "tokenizer_id": manifest["tokenizer_identity"]["tokenizer_id"],
            "tiktoken_version": manifest["tokenizer_identity"]["tiktoken_version"],
            "pat_str_sha256": manifest["tokenizer_identity"]["pat_str_sha256"],
            "chunking_config_sha256": manifest["chunking_config_sha256"],
            "track": "Track A (raw text; no chat template; no special tokens)",
        },
        "population": {"n_pairs": manifest["output"]["row_count"]},
        "side_profile": {"ko": ko, "en": en},
        "decomposition": {
            "mean_log_chunk_count_term": round(float(decomposition[0]), 6),
            "mean_log_tokens_per_chunk_term": round(float(decomposition[1]), 6),
            "mean_log_token_ratio": round(float(decomposition[2]), 6),
            "max_identity_residual": float(decomposition[3]),
            "mean_pair_chunk_ratio": round(float(decomposition[4]), 6),
            "median_pair_chunk_ratio": round(float(decomposition[5]), 6),
            "identity": "ln(N_ko/N_en) = ln(C_ko/C_en) + ln((N_ko/C_ko)/(N_en/C_en))",
        },
        "histograms": histograms,
        "pilot": {
            "pilot_n": pilot["pilot_n"],
            "total_chunks_inspected": pilot["total_chunks_inspected"],
            "invariants": pilot["invariants"],
            "total_mismatch": pilot["total_mismatch"],
            "sampling_salt": pilot["sampling_salt"],
        },
        "validation": {
            "checks": validation["checks"],
            "validation_status": validation["validation_status"],
            "anti_join_missing_vs_d04": validation["anti_join_missing_vs_d04"],
            "anti_join_extra_vs_d04": validation["anti_join_extra_vs_d04"],
            "orphan_tokenizer_measurement_id": validation["orphan_tokenizer_measurement_id"],
            "token_equivalence_failures": validation["token_equivalence_failures"],
            "reconstruction_failures": validation["reconstruction_failures"],
            "analysis_warning_rows": validation["analysis_warning_rows"],
        },
        "runtime": {
            # 두 구간을 구분한다. stage는 reader 생성~write~promotion 전체,
            # telemetry는 RuntimeTelemetry context가 열려 있던 구간이다.
            "stage_duration_sec": manifest["stage_duration_sec"],
            "stage_rows_per_sec": manifest["rows_per_sec"],
            "telemetry_elapsed_sec": telemetry["elapsed_sec"],
            "telemetry_mean_rows_per_second": telemetry["mean_rows_per_second"],
            "sample_count": telemetry["sample_count"],
            "interval_sec": telemetry["interval_sec"],
            "min_mem_available_gib": telemetry["min_mem_available_gib"],
            "peak_rss_gib": telemetry["peak_rss_gib"],
            "peak_swap_delta_mib": telemetry["peak_swap_delta_mib"],
            "red_or_worse_sample_count": telemetry["red_or_worse_sample_count"],
            "worst_memory_status": telemetry["worst_memory_status"],
            "final_status": telemetry["final_status"],
            "r1_periodic_sampling": telemetry["r1_periodic_sampling"],
            "duckdb_memory_limit": manifest["duckdb_memory_limit"],
            "duckdb_threads": manifest["duckdb_threads"],
            "batch_rows": manifest["batch_rows"],
            "samples": samples,
        },
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8")
    print(f"wrote {OUT.relative_to(PROJECT_ROOT)}")
    print(f"  sha256 {sha256_file(OUT)}")
    print(f"  KO mean_chunk_count={ko['mean_chunk_count']}  "
          f"tokens_per_chunk={ko['mean_tokens_per_chunk']}")
    print(f"  EN mean_chunk_count={en['mean_chunk_count']}  "
          f"tokens_per_chunk={en['mean_tokens_per_chunk']}")


if __name__ == "__main__":
    main()
