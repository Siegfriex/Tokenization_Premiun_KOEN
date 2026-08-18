"""
/**
 * @purpose G5 analysis cohort을 동결 protocol대로 조립하고 fail-closed 완전성/구조 identity를
 *          검증한 뒤, 진단용 수치 행렬을 .runtime에 물질화한다.
 * @spec_ref ssot_g5/02_G5_DIAGNOSTIC_PROTOCOL_v001.md §1 §3 §5 §6 §7
 * @param 없음 (경로는 이 worktree 고정)
 * @return outputs/manifests/ANALYSIS_COHORT_v001.json,
 *         outputs/reports/G5_REALIZED_MODEL_CONTRACT_v001.json,
 *         .runtime/g5/analysis_matrix.parquet
 * @raises SystemExit(1) HARD FAIL 조건 (행수/해시/null/비유한/비양수/join 손실)
 * @validation 어떤 행도 삭제하지 않는다. 결측은 보간하지 않고 즉시 실패한다.
 */
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import duckdb

from tokenization_premium.telemetry import RuntimeTelemetry

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "data" / "registry"
RUNTIME = ROOT / ".runtime" / "g5"
PROTOCOL_ID = "G5_DIAGNOSTIC_PROTOCOL_v001"
BASE_MAIN = "4eaa35e8437fc9013305c2b3fcf53133f2a0bddf"
EXPECTED_N = 3_835_988
EXPECTED_PAIR_SET = "d9660d654ee449e4d0c23a0070225274"

P = f"read_parquet('{(REG / 'PAIR_REGISTRY_v002.parquet').as_posix()}')"
R = f"read_parquet('{(REG / 'REP_FEATURES_v002.parquet').as_posix()}')"
M = f"read_parquet('{(REG / 'MORPH_FEATURES_KIWI_v001.parquet').as_posix()}')"
T = f"read_parquet('{(REG / 'TOKEN_O200K_BASE_v001.parquet').as_posix()}')"
K = f"read_parquet('{(REG / 'CHUNK_O200K_BASE_v001.parquet').as_posix()}')"

# protocol §4 — 물리 예측변수. 이 목록은 동결분이며 결과를 보고 바꾸지 않는다.
CONTINUOUS = [
    "pair_log_size",
    "log_code_point_ratio", "log_byte_density_ratio", "delta_whitespace_density",
    "ko_latin_share", "ko_digit_share", "ko_punctuation_share", "ko_symbol_other_share",
    "en_hangul_share", "en_digit_share", "en_punctuation_share", "en_symbol_other_share",
    "ko_script_type_count", "ko_script_switch_count",
    "en_script_type_count", "en_script_switch_count",
    "morpheme_density", "particle_ratio", "ending_ratio", "deriv_affix_ratio",
    "function_morpheme_ratio",
    "ko_chunk_count_log", "en_chunk_count_log",
    "ko_mean_chunk_bytes", "ko_p50_chunk_bytes", "ko_p90_chunk_bytes", "ko_max_chunk_bytes",
    "en_mean_chunk_bytes", "en_p50_chunk_bytes", "en_p90_chunk_bytes", "en_max_chunk_bytes",
    "ko_max_tokens_per_chunk", "en_max_tokens_per_chunk",
    "ko_chunk_type_share_number", "ko_chunk_type_share_punctuation",
    "ko_chunk_type_share_whitespace",
    "en_chunk_type_share_number", "en_chunk_type_share_punctuation",
    "en_chunk_type_share_whitespace",
]
OUTCOMES = ["log_token_premium", "log_compression_penalty"]
CATEGORICAL = ["source_domain_cell", "translation_direction"]

SELECT_SQL = f"""
SELECT
  t.pair_id,
  t.log_token_premium,
  t.log_compression_penalty,
  t.log_code_point_ratio,
  t.log_byte_density_ratio,
  0.5 * (ln(r.ko_codepoint_count) + ln(r.en_codepoint_count))       AS pair_log_size,
  r.ko_whitespace_density - r.en_whitespace_density                  AS delta_whitespace_density,
  r.ko_latin_share, r.ko_digit_share, r.ko_punctuation_share, r.ko_symbol_other_share,
  r.en_hangul_share, r.en_digit_share, r.en_punctuation_share, r.en_symbol_other_share,
  CAST(r.ko_script_type_count AS DOUBLE)   AS ko_script_type_count,
  CAST(r.ko_script_switch_count AS DOUBLE) AS ko_script_switch_count,
  CAST(r.en_script_type_count AS DOUBLE)   AS en_script_type_count,
  CAST(r.en_script_switch_count AS DOUBLE) AS en_script_switch_count,
  m.morpheme_density, m.particle_ratio, m.ending_ratio, m.deriv_affix_ratio,
  m.function_morpheme_ratio,
  ln(k.ko_chunk_count) AS ko_chunk_count_log,
  ln(k.en_chunk_count) AS en_chunk_count_log,
  k.ko_mean_chunk_bytes, k.ko_p50_chunk_bytes, k.ko_p90_chunk_bytes,
  CAST(k.ko_max_chunk_bytes AS DOUBLE) AS ko_max_chunk_bytes,
  k.en_mean_chunk_bytes, k.en_p50_chunk_bytes, k.en_p90_chunk_bytes,
  CAST(k.en_max_chunk_bytes AS DOUBLE) AS en_max_chunk_bytes,
  CAST(k.ko_max_tokens_per_chunk AS DOUBLE) AS ko_max_tokens_per_chunk,
  CAST(k.en_max_tokens_per_chunk AS DOUBLE) AS en_max_tokens_per_chunk,
  k.ko_chunk_type_share_number, k.ko_chunk_type_share_punctuation,
  k.ko_chunk_type_share_whitespace,
  k.en_chunk_type_share_number, k.en_chunk_type_share_punctuation,
  k.en_chunk_type_share_whitespace,
  p.source_id || '-' || p.domain AS source_domain_cell,
  p.translation_direction,
  p.source_id, p.domain, p.logical_corpus, p.sentence_type
FROM {T} t
JOIN {P} p ON p.pair_id = t.pair_id
JOIN {R} r ON r.pair_id = t.pair_id
JOIN {M} m ON m.pair_id = t.pair_id
JOIN {K} k ON k.pair_id = t.pair_id
"""


def _one(con: duckdb.DuckDBPyConnection, sql: str):
    return con.execute(sql).fetchone()


def main() -> int:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    (ROOT / "outputs" / "manifests").mkdir(parents=True, exist_ok=True)
    (ROOT / "outputs" / "reports").mkdir(parents=True, exist_ok=True)

    con = duckdb.connect()
    con.execute("PRAGMA memory_limit='3GB'")
    con.execute(f"PRAGMA temp_directory='{(RUNTIME / 'spill').as_posix()}'")
    con.execute("PRAGMA threads=4")

    hard_fail: list[str] = []
    out: dict = {
        "artifact_id": "ANALYSIS_COHORT_v001",
        "cohort_id": "ANALYSIS_COHORT_v001",
        "protocol_id": PROTOCOL_ID,
        "base_main_sha": BASE_MAIN,
        "prior_g5_scratch_observed": True,
        "prior_g5_scratch_evidence": False,
    }

    with RuntimeTelemetry(run_id="G5_COHORT_v001", stage="SOURCE_COUNTS",
                          total=EXPECTED_N, abort_on_red=True) as tel:
        # ---- per-artifact row counts, before any join -----------------------
        counts = {}
        for name, rel in (("D-01", P), ("D-02", R), ("D-03", M), ("D-04", T), ("D-05", K)):
            counts[name] = _one(con, f"SELECT count(*), count(DISTINCT pair_id) FROM {rel}")
        out["source_row_counts"] = {k: {"rows": v[0], "distinct_pair_id": v[1]}
                                    for k, v in counts.items()}

        tel.set_stage("MATERIALIZE")
        mat = (RUNTIME / "analysis_matrix.parquet").as_posix()
        con.execute(f"COPY ({SELECT_SQL}) TO '{mat}' (FORMAT PARQUET, COMPRESSION ZSTD)")
        A = f"read_parquet('{mat}')"

        tel.set_stage("COHORT_IDENTITY")
        n, ndist = _one(con, f"SELECT count(*), count(DISTINCT pair_id) FROM {A}")
        pair_set = _one(con, f"SELECT md5(string_agg(pair_id, '' ORDER BY pair_id)) FROM {A}")[0]
        tel.update(n)
        out.update({"N": n, "distinct_pair_id": ndist, "pair_set_hash": pair_set,
                    "expected_N": EXPECTED_N, "expected_pair_set_hash": EXPECTED_PAIR_SET,
                    "N_matches_expected": n == EXPECTED_N,
                    "distinct_pair_id_equals_N": ndist == n,
                    "pair_set_hash_matches_expected": pair_set == EXPECTED_PAIR_SET})
        if n != EXPECTED_N:
            hard_fail.append(f"COHORT_N_MISMATCH: {n} != {EXPECTED_N}")
        if ndist != n:
            hard_fail.append(f"PAIR_ID_NOT_UNIQUE: distinct {ndist} != rows {n}")
        if pair_set != EXPECTED_PAIR_SET:
            hard_fail.append("PAIR_SET_HASH_MISMATCH")
        d04_rows = counts["D-04"][0]
        out["join_preserves_d04_spine"] = n == d04_rows
        if n != d04_rows:
            hard_fail.append(f"JOIN_LOSS: cohort {n} != D-04 {d04_rows}")

        # ---- completeness, fail-closed --------------------------------------
        tel.set_stage("COMPLETENESS")
        cols = CONTINUOUS + OUTCOMES
        null_expr = ", ".join(f"sum(CASE WHEN {c} IS NULL THEN 1 ELSE 0 END) AS n_{c}"
                              for c in cols)
        nonfin_expr = ", ".join(
            f"sum(CASE WHEN {c} IS NOT NULL AND NOT isfinite({c}) THEN 1 ELSE 0 END) AS f_{c}"
            for c in cols)
        cat_expr = ", ".join(f"sum(CASE WHEN {c} IS NULL THEN 1 ELSE 0 END) AS c_{c}"
                             for c in ["source_id", "domain", "translation_direction",
                                       "logical_corpus", "source_domain_cell"])
        nulls = dict(zip(cols, _one(con, f"SELECT {null_expr} FROM {A}"), strict=True))
        nonfin = dict(zip(cols, _one(con, f"SELECT {nonfin_expr} FROM {A}"), strict=True))
        catnulls = dict(zip(["source_id", "domain", "translation_direction", "logical_corpus",
                             "source_domain_cell"],
                            _one(con, f"SELECT {cat_expr} FROM {A}"), strict=True))
        out["null_counts"] = {k: int(v) for k, v in nulls.items()}
        out["nonfinite_counts"] = {k: int(v) for k, v in nonfin.items()}
        out["categorical_null_counts"] = {k: int(v) for k, v in catnulls.items()}
        out["total_null_or_nonfinite"] = int(sum(nulls.values()) + sum(nonfin.values())
                                             + sum(catnulls.values()))
        if out["total_null_or_nonfinite"] != 0:
            hard_fail.append("REQUIRED_FIELD_INCOMPLETE")

        # ---- strict positivity of log arguments -----------------------------
        pos = _one(con, f"""
          SELECT sum(CASE WHEN r.ko_codepoint_count <= 0 THEN 1 ELSE 0 END),
                 sum(CASE WHEN r.en_codepoint_count <= 0 THEN 1 ELSE 0 END),
                 sum(CASE WHEN k.ko_chunk_count <= 0 THEN 1 ELSE 0 END),
                 sum(CASE WHEN k.en_chunk_count <= 0 THEN 1 ELSE 0 END)
          FROM {T} t JOIN {R} r ON r.pair_id=t.pair_id JOIN {K} k ON k.pair_id=t.pair_id
        """)
        out["nonpositive_log_arguments"] = {
            "ko_codepoint_count": int(pos[0]), "en_codepoint_count": int(pos[1]),
            "ko_chunk_count": int(pos[2]), "en_chunk_count": int(pos[3])}
        if any(pos):
            hard_fail.append("NONPOSITIVE_LOG_ARGUMENT")

        # ---- structural identities (protocol §5, §6.2) ----------------------
        tel.set_stage("STRUCTURAL_IDENTITIES")
        ident_sql = f"""
        SELECT
          max(abs(ln(r.pair_byte_ratio) - (t.log_code_point_ratio + t.log_byte_density_ratio))),
          max(abs(r.pair_codepoint_ratio - exp(t.log_code_point_ratio))),
          max(abs(ln(k.pair_chunk_ratio) - (ln(k.ko_chunk_count) - ln(k.en_chunk_count)))),
          max(abs(CAST(k.ko_chunk_byte_total AS DOUBLE) - CAST(r.ko_utf8_bytes AS DOUBLE))),
          max(abs(CAST(k.en_chunk_byte_total AS DOUBLE) - CAST(r.en_utf8_bytes AS DOUBLE))),
          max(abs(CAST(k.ko_chunk_token_total AS DOUBLE) - CAST(t.ko_token_count AS DOUBLE))),
          max(abs(CAST(k.en_chunk_token_total AS DOUBLE) - CAST(t.en_token_count AS DOUBLE))),
          max(abs(k.ko_tokens_per_chunk * k.ko_chunk_count
                  - CAST(k.ko_chunk_token_total AS DOUBLE))),
          max(abs(k.en_tokens_per_chunk * k.en_chunk_count
                  - CAST(k.en_chunk_token_total AS DOUBLE))),
          max(abs((ln(t.ko_tokens_per_byte) - ln(t.en_tokens_per_byte))
                  - t.log_compression_penalty)),
          max(abs((ln(t.ko_tokens_per_codepoint) - ln(t.en_tokens_per_codepoint))
                  - (t.log_token_premium - t.log_code_point_ratio))),
          max(abs(CAST(r.ko_whitespace_count AS DOUBLE)
                  - r.ko_whitespace_density * r.ko_codepoint_count)),
          max(abs(t.log_token_premium - (t.log_code_point_ratio + t.log_byte_density_ratio
                                         + t.log_compression_penalty))),
          max(abs((r.ko_hangul_share + r.ko_latin_share + r.ko_digit_share
                   + r.ko_punctuation_share + r.ko_symbol_other_share
                   + r.ko_whitespace_density) - 1.0)),
          max(abs((r.en_hangul_share + r.en_latin_share + r.en_digit_share
                   + r.en_punctuation_share + r.en_symbol_other_share
                   + r.en_whitespace_density) - 1.0)),
          max(abs((k.ko_chunk_type_share_letter + k.ko_chunk_type_share_number
                   + k.ko_chunk_type_share_punctuation
                   + k.ko_chunk_type_share_whitespace) - 1.0)),
          max(abs((k.en_chunk_type_share_letter + k.en_chunk_type_share_number
                   + k.en_chunk_type_share_punctuation
                   + k.en_chunk_type_share_whitespace) - 1.0))
        FROM {T} t
        JOIN {R} r ON r.pair_id=t.pair_id
        JOIN {K} k ON k.pair_id=t.pair_id
        """
        keys = [
            "ln(pair_byte_ratio) == logCR + logBDR",
            "pair_codepoint_ratio == exp(logCR)",
            "ln(pair_chunk_ratio) == ko_chunk_count_log - en_chunk_count_log",
            "ko_chunk_byte_total == ko_utf8_bytes",
            "en_chunk_byte_total == en_utf8_bytes",
            "ko_chunk_token_total == ko_token_count",
            "en_chunk_token_total == en_token_count",
            "ko_tokens_per_chunk * ko_chunk_count == ko_chunk_token_total",
            "en_tokens_per_chunk * en_chunk_count == en_chunk_token_total",
            "ln(ko_tokens_per_byte) - ln(en_tokens_per_byte) == log_compression_penalty",
            "ln(ko_tpc) - ln(en_tpc) == log_token_premium - logCR",
            "ko_whitespace_count == ko_whitespace_density * ko_codepoint_count",
            "log_token_premium == logCR + logBDR + logCP",
            "KO script shares + whitespace_density == 1",
            "EN script shares + whitespace_density == 1",
            "KO chunk type shares == 1",
            "EN chunk type shares == 1",
        ]
        vals = _one(con, ident_sql)
        out["structural_identity_max_abs_error"] = {
            k: (None if v is None else float(v)) for k, v in zip(keys, vals, strict=True)}

        # ---- approved covariate decisions, re-measured ----------------------
        tel.set_stage("COVARIATE_DECISIONS")
        st = con.execute(
            f"SELECT sentence_type, count(*) FROM {A} GROUP BY 1 ORDER BY 2 DESC").fetchall()
        lc = _one(con, f"""SELECT count(DISTINCT source_id), count(DISTINCT logical_corpus),
                                  count(DISTINCT (source_id || '||' || logical_corpus))
                           FROM {A}""")
        out["sentence_type_levels"] = {str(k): int(v) for k, v in st}
        out["sentence_type_zero_variance"] = len(st) == 1
        out["logical_corpus_bijection"] = {
            "distinct_source_id": int(lc[0]), "distinct_logical_corpus": int(lc[1]),
            "distinct_pairs": int(lc[2]),
            "is_bijective": lc[0] == lc[1] == lc[2]}

        # ---- categorical support --------------------------------------------
        tel.set_stage("CATEGORICAL_SUPPORT")
        out["source_domain_cell_counts"] = {
            str(k): int(v) for k, v in con.execute(
                f"SELECT source_domain_cell, count(*) FROM {A} GROUP BY 1 ORDER BY 2 DESC"
            ).fetchall()}
        out["translation_direction_counts"] = {
            str(k): int(v) for k, v in con.execute(
                f"SELECT translation_direction, count(*) FROM {A} GROUP BY 1 ORDER BY 2 DESC"
            ).fetchall()}
        out["source_by_domain"] = [
            {"source_id": a, "domain": b, "n": int(c)} for a, b, c in con.execute(
                f"SELECT source_id, domain, count(*) FROM {A} GROUP BY 1,2 ORDER BY 1,2"
            ).fetchall()]
        out["cell_by_direction"] = [
            {"source_domain_cell": a, "translation_direction": b, "n": int(c)}
            for a, b, c in con.execute(
                f"SELECT source_domain_cell, translation_direction, count(*) FROM {A} "
                "GROUP BY 1,2 ORDER BY 1,2").fetchall()]

        # ---- frozen references, instantiated by the frozen rule -------------
        out["reference_levels"] = {
            "source_domain_cell": max(out["source_domain_cell_counts"],
                                      key=out["source_domain_cell_counts"].get),
            "translation_direction": max(out["translation_direction_counts"],
                                         key=out["translation_direction_counts"].get),
            "ko_script_composition": "ko_hangul_share",
            "en_script_composition": "en_latin_share",
            "ko_chunk_type": "ko_chunk_type_share_letter",
            "en_chunk_type": "en_chunk_type_share_letter",
            "rule": "categorical = largest realized level by N (frozen in protocol §8); "
                    "composition = definitional native script / base chunk class (§6.3)",
        }
        tel.set_stage("DONE")
        telemetry = tel

    summary = telemetry.summary()
    summary.pop("samples", None)          # manifest에는 요약만; 표본 전문은 .runtime에 남긴다
    telemetry.write(RUNTIME / "G5_COHORT_v001_telemetry.json")
    out["runtime_telemetry"] = summary

    out["primary_exclusion_policy"] = (
        "NONE beyond the frozen G1 final cohort (RD-FAST-G5-01 §7). UNKNOWN direction, "
        "eojeol_count=1, short texts, TP extremes and morphology extremes are all retained.")
    out["retained_by_policy"] = ["translation_direction=UNKNOWN", "eojeol_count=1",
                                 "short texts", "TP extremes", "morphology extremes"]
    out["post_hoc_row_deletion"] = "FORBIDDEN"
    out["hard_fail"] = hard_fail
    out["status"] = "ANALYSIS_COHORT_FROZEN" if not hard_fail else "G5_COHORT_HARD_FAIL"

    path = ROOT / "outputs" / "manifests" / "ANALYSIS_COHORT_v001.json"
    path.write_text(json.dumps(out, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    print(json.dumps({k: out[k] for k in
                      ("N", "distinct_pair_id", "pair_set_hash", "total_null_or_nonfinite",
                       "status", "hard_fail")}, indent=2))
    print("\nstructural identity max |error|:")
    for k, v in out["structural_identity_max_abs_error"].items():
        print(f"  {v!r:<24} {k}")
    print("\nreference levels:", json.dumps(out["reference_levels"], ensure_ascii=False))
    return 1 if hard_fail else 0


if __name__ == "__main__":
    sys.exit(main())
