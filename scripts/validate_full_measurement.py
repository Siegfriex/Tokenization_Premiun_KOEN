"""전집단 D-03 / D-04 산출물 독립 검증 + exact decomposition (G2 evidence).

파이프라인 통계가 아니라 저장된 artifact를 직접 재질의한다.
"""

from __future__ import annotations

import datetime as dt
import json
from zoneinfo import ZoneInfo

import duckdb

from tokenization_premium.hashing import sha256_file
from tokenization_premium.paths import PROJECT_ROOT
from tokenization_premium.tokenizer_measurement import EXACT_DECOMPOSITION_EPSILON

KST = ZoneInfo("Asia/Seoul")
REP = PROJECT_ROOT / "data/registry/REP_FEATURES_v002.parquet"
MORPH = PROJECT_ROOT / "data/registry/MORPH_FEATURES_KIWI_v001.parquet"
TOK = PROJECT_ROOT / "data/registry/TOKEN_O200K_BASE_v001.parquet"
OUT = PROJECT_ROOT / "outputs/manifests/FULL_MEASUREMENT_VALIDATION_v001.json"

con = duckdb.connect()
con.execute("SET memory_limit='5GB'")
con.execute("SET threads=8")
con.execute(f"SET temp_directory='{(PROJECT_ROOT / '.runtime/validate-spill').as_posix()}'")
con.execute("SET preserve_insertion_order=false")
(PROJECT_ROOT / ".runtime/validate-spill").mkdir(parents=True, exist_ok=True)

R, M, T = (f"read_parquet('{p.as_posix()}')" for p in (REP, MORPH, TOK))
N = con.execute(f"SELECT count(*) FROM {R}").fetchone()[0]
print(f"reference cohort N = {N:,}\n")

report: dict = {"artifact_id": "FULL_MEASUREMENT_VALIDATION_v001",
                "generated_kst": dt.datetime.now(tz=KST).isoformat(timespec="seconds"),
                "reference_cohort_n": N}

# ---------- D-03 morphology --------------------------------------------------
m = con.execute(f"""
SELECT count(*), count(DISTINCT pair_id), count(DISTINCT morph_measurement_id),
  sum(analysis_warning_flag::INT), sum((morpheme_count = 0)::INT),
  sum((length(morpheme_sequence) <> morpheme_count)::INT),
  sum((particle_count + ending_count + deriv_affix_count > morpheme_count)::INT),
  sum((eojeol_count <= 0)::INT),
  sum((NOT isfinite(morpheme_density))::INT),
  sum((abs(morpheme_density - morpheme_count::DOUBLE / eojeol_count) > 1e-12)::INT),
  sum((morpheme_count > 0 AND (particle_ratio IS NULL OR ending_ratio IS NULL
       OR deriv_affix_ratio IS NULL OR function_morpheme_ratio IS NULL))::INT),
  sum((morpheme_count = 0 AND (particle_ratio IS NOT NULL))::INT),
  sum(morpheme_count), sum(particle_count), sum(ending_count), sum(deriv_affix_count),
  min(morpheme_density), median(morpheme_density), max(morpheme_density)
FROM {M}""").fetchone()
morph_missing, morph_extra = con.execute(
    f"SELECT (SELECT count(*) FROM (SELECT pair_id FROM {R} EXCEPT SELECT pair_id FROM {M})),"
    f"       (SELECT count(*) FROM (SELECT pair_id FROM {M} EXCEPT SELECT pair_id FROM {R}))").fetchone()
report["d03_morphology"] = {
    "row_count": m[0], "distinct_pair_id": m[1], "distinct_measurement_id": m[2],
    "pairs_missing_vs_rep_v002": morph_missing, "pairs_extra_vs_rep_v002": morph_extra,
    "analysis_warning_rows": m[3], "analysis_warning_rate": m[3] / m[0],
    "zero_morpheme_rows": m[4], "zero_morpheme_rate": m[4] / m[0],
    "sequence_count_mismatch": m[5], "bucket_sum_exceeds_morpheme_count": m[6],
    "eojeol_nonpositive": m[7], "nonfinite_density": m[8], "density_definition_violation": m[9],
    "null_ratio_where_defined": m[10], "nonnull_ratio_where_undefined": m[11],
    "total_morphemes": m[12], "total_particles": m[13], "total_endings": m[14],
    "total_deriv_affixes": m[15],
    "density_min": m[16], "density_median": m[17], "density_max": m[18],
    "artifact_sha256": sha256_file(MORPH),
}
print("D-03 MORPHOLOGY")
print(f"  rows / distinct pair_id / distinct measurement_id : {m[0]:,} / {m[1]:,} / {m[2]:,}")
print(f"  missing vs REP v002 / extra                        : {morph_missing} / {morph_extra}")
print(f"  warning rows / zero-morpheme rows                  : {m[3]:,} / {m[4]:,}")
print(f"  sequence-count mismatch / bucket overflow          : {m[5]} / {m[6]}")
print(f"  density definition violation / nonfinite           : {m[9]} / {m[8]}")
print(f"  ratio-null contract violations                     : {m[10]} / {m[11]}")
print(f"  morphemes {m[12]:,}  particles {m[13]:,}  endings {m[14]:,}  deriv {m[15]:,}")
print(f"  density  min {m[16]:.4f}  median {m[17]:.4f}  max {m[18]:.4f}")

# POS family aggregate (base tag)
pos = con.execute(f"""
SELECT split_part(x.pos, '-', 1) AS base, count(*) AS n
FROM {M}, unnest(morpheme_sequence) AS t(x)
GROUP BY base ORDER BY n DESC LIMIT 25""").fetchall()
irr = con.execute(f"""
SELECT x.pos AS tag, count(*) AS n
FROM {M}, unnest(morpheme_sequence) AS t(x)
WHERE x.pos LIKE '%-%' GROUP BY tag ORDER BY n DESC""").fetchall()
report["d03_morphology"]["base_tag_top25"] = {k: int(v) for k, v in pos}
report["d03_morphology"]["irregular_tag_counts"] = {k: int(v) for k, v in irr}
print(f"  distinct irregular tags: {len(irr)} -> {dict(irr)}")

# ---------- D-04 tokenizer ---------------------------------------------------
t = con.execute(f"""
SELECT count(*), count(DISTINCT pair_id), count(DISTINCT measurement_id),
  sum((NOT roundtrip_ok)::INT),
  sum((identity_abs_error >= {EXACT_DECOMPOSITION_EPSILON})::INT),
  max(identity_abs_error),
  quantile_cont(identity_abs_error, [0.99, 0.999]),
  sum((length(ko_token_ids) <> ko_token_count)::INT),
  sum((length(en_token_ids) <> en_token_count)::INT),
  sum((token_difference <> ko_token_count - en_token_count)::INT),
  sum((abs(token_premium - ko_token_count::DOUBLE / en_token_count) > 1e-12)::INT),
  sum((NOT isfinite(log_token_premium))::INT),
  sum(ko_token_count), sum(en_token_count),
  min(token_premium), median(token_premium), max(token_premium),
  min(log_token_premium), median(log_token_premium), max(log_token_premium),
  median(code_point_ratio), median(byte_density_ratio), median(compression_penalty),
  count(DISTINCT tokenizer_config_sha256), count(DISTINCT encoding_file_sha256)
FROM {T}""").fetchone()
tok_missing, tok_extra = con.execute(
    f"SELECT (SELECT count(*) FROM (SELECT pair_id FROM {R} EXCEPT SELECT pair_id FROM {T})),"
    f"       (SELECT count(*) FROM (SELECT pair_id FROM {T} EXCEPT SELECT pair_id FROM {R}))").fetchone()
q99, q999 = list(t[6])
report["d04_tokenizer"] = {
    "row_count": t[0], "distinct_pair_id": t[1], "distinct_measurement_id": t[2],
    "pairs_missing_vs_rep_v002": tok_missing, "pairs_extra_vs_rep_v002": tok_extra,
    "roundtrip_failures": t[3], "roundtrip_pass_rate": 1 - t[3] / t[0],
    "token_id_length_mismatch_ko": t[7], "token_id_length_mismatch_en": t[8],
    "token_difference_violation": t[9], "token_premium_definition_violation": t[10],
    "nonfinite_log_tp": t[11],
    "total_ko_tokens": t[12], "total_en_tokens": t[13],
    "tp_min": t[14], "tp_median": t[15], "tp_max": t[16],
    "logtp_min": t[17], "logtp_median": t[18], "logtp_max": t[19],
    "median_code_point_ratio": t[20], "median_byte_density_ratio": t[21],
    "median_compression_penalty": t[22],
    "distinct_config_sha": t[23], "distinct_encoding_sha": t[24],
    "artifact_sha256": sha256_file(TOK),
}
report["exact_decomposition"] = {
    "epsilon": EXACT_DECOMPOSITION_EPSILON,
    "checked_pairs": t[0],
    "violations": t[4],
    "max_abs_error": t[5], "p99_abs_error": q99, "p999_abs_error": q999,
    "identity": "logTP = logCodePointRatio + logByteDensityRatio + logCompressionPenalty",
    "spec_ref": "SSOT §8; G2 Representation Integrity",
}
print("\nD-04 TOKENIZER")
print(f"  rows / distinct pair_id / distinct measurement_id : {t[0]:,} / {t[1]:,} / {t[2]:,}")
print(f"  missing vs REP v002 / extra                        : {tok_missing} / {tok_extra}")
print(f"  roundtrip failures                                 : {t[3]}  (pass rate {1 - t[3]/t[0]:.6f})")
print(f"  token id length mismatch ko/en                     : {t[7]} / {t[8]}")
print(f"  TP definition / token_difference violations        : {t[10]} / {t[9]}")
print(f"  total tokens KO {t[12]:,}  EN {t[13]:,}")
print(f"  TP     min {t[14]:.4f}  median {t[15]:.4f}  max {t[16]:.4f}")
print(f"  logTP  min {t[17]:.4f}  median {t[18]:.4f}  max {t[19]:.4f}")
print(f"  median CR {t[20]:.4f} | BDR {t[21]:.4f} | CP {t[22]:.4f}")

print("\nEXACT DECOMPOSITION (SSOT §8, all final pairs)")
print(f"  epsilon        {EXACT_DECOMPOSITION_EPSILON}")
print(f"  checked pairs  {t[0]:,}")
print(f"  violations     {t[4]}")
print(f"  max abs error  {t[5]:.6e}")
print(f"  p99 / p99.9    {q99:.6e} / {q999:.6e}")

# ---------- cross-artifact ---------------------------------------------------
cross = con.execute(
    f"SELECT (SELECT count(*) FROM (SELECT pair_id FROM {M} EXCEPT SELECT pair_id FROM {T})),"
    f"       (SELECT count(*) FROM (SELECT pair_id FROM {T} EXCEPT SELECT pair_id FROM {M}))").fetchone()
report["cross_artifact"] = {"morph_minus_tok": cross[0], "tok_minus_morph": cross[1]}
print(f"\nCROSS-ARTIFACT pair-set  morph−tok {cross[0]}  tok−morph {cross[1]}")

failures = []
d3, d4 = report["d03_morphology"], report["d04_tokenizer"]
if not (d3["row_count"] == d3["distinct_pair_id"] == d3["distinct_measurement_id"] == N):
    failures.append("D-03 row/pair_id/measurement_id count")
if d3["pairs_missing_vs_rep_v002"] or d3["pairs_extra_vs_rep_v002"]:
    failures.append("D-03 pair-set equality")
for k in ("sequence_count_mismatch", "bucket_sum_exceeds_morpheme_count", "eojeol_nonpositive",
          "nonfinite_density", "density_definition_violation", "null_ratio_where_defined",
          "nonnull_ratio_where_undefined"):
    if d3[k]:
        failures.append(f"D-03 {k}")
if not (d4["row_count"] == d4["distinct_pair_id"] == d4["distinct_measurement_id"] == N):
    failures.append("D-04 row/pair_id/measurement_id count")
if d4["pairs_missing_vs_rep_v002"] or d4["pairs_extra_vs_rep_v002"]:
    failures.append("D-04 pair-set equality")
if d4["roundtrip_failures"]:
    failures.append("D-04 roundtrip (G3 blocker)")
for k in ("token_id_length_mismatch_ko", "token_id_length_mismatch_en",
          "token_difference_violation", "token_premium_definition_violation", "nonfinite_log_tp"):
    if d4[k]:
        failures.append(f"D-04 {k}")
if report["exact_decomposition"]["violations"]:
    failures.append("exact decomposition (G2 blocker)")
if cross[0] or cross[1]:
    failures.append("cross-artifact pair-set equality")

report["failures"] = failures
report["validation_status"] = "PASS" if not failures else "FAIL"
report["gate_evidence"] = {
    "G2_exact_decomposition": "PASS" if not report["exact_decomposition"]["violations"] else "BLOCKED",
    "G3_roundtrip": "PASS" if not d4["roundtrip_failures"] else "BLOCKED",
    "G4_morphology_artifact": "EVIDENCE_COMPLETE_AWAITING_ADJUDICATION",
    "note": "Gate 판정은 Claude-B의 몫이며 여기서는 증거만 제시한다",
}
OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
con.close()
print(f"\nFAILURES: {failures or 'NONE'}")
print(f"VALIDATION_STATUS = {report['validation_status']}")
print(f"wrote {OUT.relative_to(PROJECT_ROOT)}")
