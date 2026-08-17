# KOEN — G2 / G3 / G4 Measurement Integrity Final Adjudication

> **Adjudicator**: Claude-B (Evidence Validator / Research Gate Steward)
> **Snapshot**: 2026-08-17 17:30 KST
> **Adjudicated main**: `92dc07a6f2c5af3c3161d7f7a615dc7211e27559`
> **Authority**: `KOEN-TP-RS-001` §8 · §12.2/12.3/12.4 · §13 · §14 · §15 · §30.2 · §31 · §37–39 → approved redline → `RD-20260817-D02D03-CONFORMANCE-01` → frozen configs → execution evidence

**Method statement.** No number in this document was taken from a commit message, an agent report,
or a manifest summary. Every gating quantity was recomputed by Claude-B directly from the physical
Parquet artifacts, from an independently reconstructed tokenizer, or from the raw analysis text.
Manifests were treated as claims to be tested, not as evidence.

No raw KO/EN sentence text is reproduced here (repository hygiene, OPS-DR-01).

---

## 1. Artifact identity — SHA-256 recomputed locally

| artifact | expected | recomputed | size | verdict |
|---|---|---|---|---|
| `data/registry/PAIR_REGISTRY_v002.parquet` | `95f523d1…0bec52` | identical | 2,954,269,647 B | **MATCH** |
| `data/registry/REP_FEATURES_v002.parquet` | `dfae8e01…50d309` | identical | 258,395,410 B | **MATCH** |
| `data/registry/MORPH_FEATURES_KIWI_v001.parquet` | `0fe5bd74…e50f7d` | identical | 568,758,730 B | **MATCH** |
| `data/registry/TOKEN_O200K_BASE_v001.parquet` | `1c30e327…2c16e7` | identical | 812,812,998 B | **MATCH** |

```
ARTIFACT_IDENTITY_VALIDATED   (4 / 4)
```

## 2. Physical schemas — dual-path (PyArrow + DuckDB)

| artifact | rows | cols (PyArrow) | cols (DuckDB) | names agree | row groups |
|---|---:|---:|---:|---|---:|
| REP_FEATURES_v002 | 3,835,988 | 49 | 49 | yes | 32 |
| MORPH_FEATURES_KIWI_v001 | 3,835,988 | 19 | 19 | yes | 1,535 |
| TOKEN_O200K_BASE_v001 | 3,835,988 | 28 | 28 | yes | 1,535 |

`morpheme_sequence` physical type: `list<struct<form: string not null, pos: string not null> not null>`
— ordered, lossless, non-nullable. `ko_token_ids` / `en_token_ids`: `list<int32 not null>`.

### 2.1 The 28-vs-29 column discrepancy — resolved

```
VERDICT: REPORT_TYPO_ONLY
```

Source located: the **commit message body of `92dc07a`** states `29 columns`. The physical artifact
carries **28** columns on both independent read paths, and
`TOKEN_O200K_BASE_MANIFEST_v001.output.column_count = 28`. All fifteen SSOT §12.4 D-04 required
fields are present:

`measurement_id · pair_id · tokenizer_id · tiktoken_version · encoding_file_sha256 ·
mergeable_ranks_hash · pat_str_sha256 · special_tokens_hash · ko_token_ids · en_token_ids ·
ko_token_count · en_token_count · token_premium · log_token_premium · token_difference ·
compression_penalty · roundtrip_ok`

The remaining columns (`tokenizer_config_sha256`, `code_point_ratio`, `byte_density_ratio`,
`log_*`, `identity_abs_error`, `*_tokens_per_byte`, `*_tokens_per_codepoint`) are §8 decomposition
support fields, not omissions. No D-04 field is missing, so this is **not** a manifest defect and
**not** a schema-contract defect. The erroneous figure lives only in immutable commit prose and is
recorded here rather than corrected.

## 3. Cohort and pair-set integrity

| artifact | rows | distinct pair_id | null | duplicate |
|---|---:|---:|---:|---:|
| REP | 3,835,988 | 3,835,988 | 0 | 0 |
| MORPH | 3,835,988 | 3,835,988 | 0 | 0 |
| TOKEN | 3,835,988 | 3,835,988 | 0 | 0 |

All six directed anti-joins (REP↔MORPH, REP↔TOKEN, MORPH↔TOKEN) return **0**.

Stable sorted pair-set hash — `md5(string_agg(pair_id ORDER BY pair_id))`:

```
REP    d9660d654ee449e4d0c23a0070225274
MORPH  d9660d654ee449e4d0c23a0070225274
TOKEN  d9660d654ee449e4d0c23a0070225274
ALL THREE IDENTICAL
```

The 25 G1-excluded `pair_id`s were re-parsed from
`KOEN_G1_HUMAN_AUDIT_FINAL_ADJUDICATION.md` (25 recovered) and joined against each artifact:
**0 present in REP, 0 in MORPH, 0 in TOKEN.**

## 4. Measurement-ID integrity

| artifact | id column | n | distinct | null | pair_id↔id 1:1 |
|---|---|---:|---:|---:|---|
| MORPH | `morph_measurement_id` | 3,835,988 | 3,835,988 | 0 | **yes** |
| TOKEN | `measurement_id` | 3,835,988 | 3,835,988 | 0 | **yes** |

Both directions tested (no `pair_id` with >1 id, no id with >1 `pair_id`). Construction rule
confirmed in source: `sha256(SCHEMA_VERSION | CONFIG_SHA256 | pair_id)` with a namespace prefix
(`morph_…` / `tok_…`).

## 5. Representation — independent recomputation (G2)

Deterministic sample, salt `B_REP_v001`: 2.4 % stable-hash base plus targeted oversampling of
shortest/longest KO and EN, grapheme≠codepoint disagreement rows, `script_type_count ≥ 3`,
byte-density extremes and `symbol_other_share > 0.05`.

```
sample N = 102,278  (primary pass)   /  96,787  (script-share corrected pass)
```

Every field was recomputed from `PAIR_REGISTRY_v002.ko_text_analysis` / `en_text_analysis` by
Claude-B's own code path — **not** by calling the production feature functions.

| field group | fields checked | mismatches |
|---|---|---:|
| length | `ko/en_codepoint_count`, `ko/en_grapheme_count` (UAX#29 `\X`), `ko/en_utf8_bytes` | **0** |
| lexical | `ko_eojeol_count`, `en_word_count` | **0** |
| whitespace | `ko_whitespace_count`, `ko_space_run_count`, `ko_whitespace_density` | **0** |
| derived density | `ko/en_bytes_per_codepoint`, `ko_bytes_per_grapheme` | **0** |
| script shares | `hangul`, `latin`, `digit`, `punctuation`, `symbol_other` | **0** |
| script structure | `ko_script_type_count`, `ko_script_switch_count` | **0** |
| closure identity | `Σ shares + whitespace_density = 1` | **0** |
| pair ratios | `pair_codepoint_ratio`, `pair_grapheme_ratio`, `pair_byte_ratio`, `pair_codepoint_diff` | **0** |

Unicode normalization audit: `NFC(analysis_text) ≠ analysis_text` in **0 / 102,278** rows on both
sides — the analysis text is NFC-stable, as §11 requires.

> **Auditor self-correction (recorded, per §22).** Claude-B's first pass reported 11,160
> `ko_punctuation_share` mismatches. Investigation of `representation.py:38–48` showed the frozen
> classifier assigns `punct = \p{P}` only, routing `\p{S}` to `symbol_other`; the auditor's first
> classifier had merged `\p{P}` and `\p{S}`. **The defect was in the audit code, not the artifact.**
> Re-run against the exact frozen definition: 0 mismatches. No artifact change was made or implied.

## 6. Exact decomposition — full population, independent (G2)

Recomputed for **all 3,835,988 pairs** from constituent fields only
(`T_KO`, `T_EN` from TOKEN; `C_KO`, `C_EN`, `B_KO`, `B_EN` from REP), ignoring every stored
derived column:

```
TP  = T_KO/T_EN     CPR = C_KO/C_EN
BDR = (B_KO/C_KO)/(B_EN/C_EN)      CP = (T_KO/B_KO)/(T_EN/B_EN)
identity tested:  | log TP − (log CPR + log BDR + log CP) |
```

| quantity | value |
|---|---|
| max identity error | `8.881784197001252e-16` |
| p99 | `3.330669e-16` |
| p99.9 | `3.885781e-16` |
| identity violations at ε = 1e-10 | **0** |
| `TP` non-finite / `logTP` non-finite | **0 / 0** |

Stored-vs-recomputed comparison, maximum absolute difference across the whole population:

```
token_premium            0.0        log_token_premium        0.0
code_point_ratio         0.0        log_code_point_ratio     0.0
byte_density_ratio       0.0        log_byte_density_ratio   0.0
compression_penalty      0.0        log_compression_penalty  0.0
token_difference mismatch rows       0
```

Every stored derived field reproduces **exactly** (bit-identical, not merely within tolerance).
The stored `identity_abs_error` maximum (`8.88e-16`) equals the independently computed maximum.

## 7. Tokenizer forensics (G3)

The encoder was rebuilt offline from the local cache and all hashes recomputed live, then compared
against **two** independent sources: the values embedded in every row of the artifact, and the
Phase-0 `TOKENIZER_O200K_BASE_ARTIFACT_v001.json` produced long before this run.

```
encoding name = o200k_base    n_vocab = 200,019
mergeable_ranks = 199,998     special_tokens = 2
```

| field | artifact-embedded | live recomputation | Phase-0 manifest | verdict |
|---|---|---|---|---|
| `tokenizer_id` | `o200k_base` | same | same | **MATCH** |
| `tiktoken_version` | `0.13.0` | same | same | **MATCH** |
| `encoding_file_sha256` | `446a9538…fb1a2d` | same | same | **MATCH** |
| `mergeable_ranks_hash` | `f2f61460…61e2d0` | same | same | **MATCH** |
| `pat_str_sha256` | `2d1b8dc1…857420` | same | same | **MATCH** |
| `special_tokens_hash` | `160541c3…afa14d` | same | same | **MATCH** |

Distinct-value counts over all 3,835,988 rows: `tokenizer_id` 1, `tiktoken_version` 1,
`encoding_file_sha256` 1, `mergeable_ranks_hash` 1, `pat_str_sha256` 1, `special_tokens_hash` 1,
`tokenizer_config_sha256` 1. No configuration contamination.

`tokenizer_config_sha256` (`c29ea389…`) differs from the Phase-0 `config_sha256` (`038bb343…`)
because they hash different objects — the measurement rule config versus the Phase-0 artifact
config. This is expected, not a mismatch.

## 8. Token-ID structural validation — full population (G3)

```
len(ko_token_ids) ≠ ko_token_count        0
len(en_token_ids) ≠ en_token_count        0
ko_token_count ≤ 0 / en_token_count ≤ 0   0 / 0
token_count range   KO [1, 401]   EN [1, 453]
roundtrip_ok = false                      0
token id range      [0, 199997]   negatives 0
```

`max token id = 199,997 < n_vocab = 200,019` and also `< 199,998` (the mergeable-rank count) —
therefore **no special-token ID appears anywhere in the corpus**, positively confirming
SSOT §14.2 Track A (`allowed_special = none`, no chat template).

## 9. Independent roundtrip decode audit (G3)

The stored `roundtrip_ok` flag was **not** relied upon. Deterministic samples (salts `B_RT_v001`,
`B_RT_v002`), oversampling TP extremes, token-count extremes, byte-density extremes,
`script_switch ≥ 6`, emoji flags, `symbol_other_share > 0.1`, and grapheme≠codepoint rows:

```
sample N = 20,524 pairs  (16,324 + 4,200 top-up)   = 41,048 decoded sides
coverage: 4 domains, strata Q1–Q5
rare Unicode actually exercised: combining marks 27, zero-width 75, astral (>U+FFFF) 6

enc.decode(stored_token_ids) ≠ analysis_text   :  0
enc.encode(analysis_text)    ≠ stored_token_ids:  0     (reverse direction also tested)
```

Both directions were verified, so the audit excludes an encode-side error that a decode-only check
would miss.

## 10. Token-byte audit (G3)

Independent deterministic 100-row sample (salt `B_TB_v001`), 200 sides, 5,951 tokens. For every
token: `decode_single_token_bytes` → concatenation → hex reconstruction, compared against the
UTF-8 source bytes.

```
Σ decode_single_token_bytes ≠ UTF-8 source bytes : 0
hex reconstruction mismatch                       : 0
multi-byte split tokens observed                  : 173
```

The 173 tokens that are individually invalid UTF-8 fragments confirm that Hangul multi-byte
sequences genuinely split across BPE token boundaries in this corpus — the audit exercises the
condition it is meant to test rather than passing vacuously.

## 11. Morphology physical schema and structural validation (G4)

All SSOT §12.3 D-03 fields present with correct physical types (19 columns, §2). Ratio columns are
nullable by design; `morpheme_density` and all counts are non-nullable.

Full-population re-derivation from the stored `morpheme_sequence` — Claude-B recomputed every
count and ratio from the nested POS list, independently of the pipeline:

| check | violations (of 3,835,988) |
|---|---:|
| `len(morpheme_sequence) ≠ morpheme_count` | **0** |
| `particle_count ≠ Σ base_tag startswith "J"` | **0** |
| `ending_count ≠ Σ base_tag startswith "E"` | **0** |
| `deriv_affix_count ≠ Σ base_tag ∈ {XSN,XSV,XSA}` | **0** |
| `morpheme_density ≠ morpheme_count / eojeol_count` (§13.6) | **0** |
| `particle_ratio ≠ particle_count / morpheme_count` (§13.7) | **0** |
| `ending_ratio` / `deriv_affix_ratio` / `function_morpheme_ratio` | **0 / 0 / 0** |
| `analysis_warning_flag ⇎ (morpheme_count = 0)` | **0** |
| `eojeol_count ≤ 0` | **0** |
| ratio outside [0,1] · non-finite density | **0 · 0** |
| `MORPH.eojeol_count ≠ REP_v002.ko_eojeol_count` | **0** |

`zero_morpheme_rows = 0`, `analysis_warning_rate = 0.0`.
Analyzer provenance distinct counts over the full population: name 1, package 1 (`0.23.2`),
model 1 (`0.23.0`), `analyzer_config_hash` 1 (`6f48802a…`).

## 12. XSA-I full-population effect (G4)

Recounted directly from the nested POS sequence and simulated against the superseded exact-match
mapping:

```
deriv total, base-tag mapping (current)  6,712,268
deriv total, exact-match mapping (old)   6,683,776
delta                                       28,492
XSA-I occurrences counted independently     28,492      →  delta == XSA-I count
rows changed by the M2 fix                  28,029
```

Cross-check: `XSA 824,147 + XSA-I 28,492 + XSN 1,743,941 + XSV 4,115,688 = 6,712,268`, matching the
independently recomputed base-mapping total exactly. The M2 correction is therefore **provably
applied across the full population**, with an effect that matches the expected mechanism precisely
and touches nothing else.

## 13. Morphology distribution sanity (G4)

Full population, exact quantiles:

| feature | min | p0.1 | p1 | p5 | median | p95 | p99 | p99.9 | max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `morpheme_count` | 1 | 2 | 4 | 7 | 19 | 53 | 63 | 74 | 291 |
| `eojeol_count` | 1 | 1 | 1 | 3 | 9 | 24 | 29 | 30 | 158 |
| `morpheme_density` | 0.500 | 1.375 | 1.600 | 1.773 | 2.214 | 3.000 | 4.000 | 6.000 | 30.000 |
| `particle_ratio` | 0 | 0 | 0 | 0 | 0.158 | 0.250 | 0.300 | 0.364 | 0.600 |
| `ending_ratio` | 0 | 0 | 0 | 0.077 | 0.175 | 0.318 | 0.400 | 0.500 | 0.667 |
| `deriv_affix_ratio` | 0 | 0 | 0 | 0 | 0.065 | 0.152 | 0.200 | 0.250 | 0.500 |
| `function_morpheme_ratio` | 0 | 0 | 0 | 0.200 | 0.342 | 0.450 | 0.500 | 0.545 | 0.667 |

**`density_max = 30.0` — bounded audit of the top-10 extremes.** Every one has `eojeol_count = 1`,
i.e. a genuinely unspaced string. Inspected POS signatures: a 26-morpheme run of `NR` (an unspaced
numeral string), a 17-morpheme `SL/SN/SW` alternation (an unspaced alphanumeric code), and several
1-eojeol clauses that are grammatically complete but written without spaces. In every case
`morpheme_count` reproduces from the sequence and `eojeol_count = 1` is arithmetically correct.

```
CLASSIFICATION: PLAUSIBLE_EXTREME  (definitionally correct, not an implementation defect)
```

`eojeol_count = 1` covers **42,096 rows (1.10 %)** with median density 4.0. Combined with the
Director-audit caveat, this is the region where analyzer limitations concentrate: the density and
particle-ratio maxima in this band can be analyzer artefacts on short interjections rather than
linguistic signal. This is a **reporting caveat carried into NB07/NB08**, not a gate blocker.

Observed but deliberately unmapped: `XSM` (adverb-deriving suffix, 624 occurrences). SSOT §12.3
fixes the derivational-affix set to `{XSN, XSV, XSA}`; excluding `XSM` is contract-conformant.

## 14. Human audit lineage (G4)

```
workbook : ssot/HumanLebeled/[HUMAN_confirmed1606]_MORPHOLOGY_AUDIT_100_v001.xlsx
SHA-256  : 5f6dd073554582227ab781a084fe6e1c144617c0a42ef1335a4c4491b023dca1   (re-verified)
sampling key set equality with the workbook: TRUE (100/100, both anti-joins 0)
first pass: O = 94, X = 6, blank 0, invalid 0
X mechanism: ANALYZER_LIMITATION 5, NATURAL_AMBIGUITY 1, IMPLEMENTATION_DEFECT 0
```

Adjudicated at commit `0a6457a` (`KOEN_G4_MORPHOLOGY_DIRECTOR_AUDIT_FINAL_ADJUDICATION.md`).
The 6 % X rate is an audit-sample rate on a deliberately extreme-weighted frame and is **not**
extrapolated to the population.

## 15. Manifest ↔ artifact bidirectional audit

Every manifest key was classified `ARTIFACT_DERIVABLE` (recomputed directly) or
`EXECUTION_METADATA` (verified against git/logs/config).

`FULL_MEASUREMENT_VALIDATION_v001` — A's self-validation — was compared field-by-field against
Claude-B's independent recomputation. Agreement on every gating quantity, including
`total_deriv_affixes 6,712,268`, `XSA-I 28,492`, `density_max 30.0`,
`density_median 2.2142857142857144`, `sequence_count_mismatch 0`, `total_morphemes 92,652,231`,
and all cross-artifact anti-joins.

### 15.1 Lineage metadata defect — corrected under §22

```
CLASSIFICATION: MANIFEST_INCONSISTENCY (lineage metadata)  — corrected, no artifact change
```

Both full-run manifests recorded `execution_code_commit = 0a6457a…` and carried **no**
`artifact_record_commit`, contrary to the SSOT §30.2 distinction. The recorded commit does not hold
the code that actually ran: `src/tokenization_premium/tokenizer_measurement.py` gained 454 lines
between `0a6457a` and `92dc07a`, and `morphology.py` changed between `0a6457a` and `6739658`.

Materiality assessment before correcting:

- morphology: the only delta is the output-path constant
  (`MORPH_FEATURES_v002.parquet` → `MORPH_FEATURES_KIWI_v001.parquet`, SSOT §38 naming).
  `base_tag`, `classify_tag`, `features_from_morphs` and `morph_features_schema` are
  **byte-identical**, and `MORPHOLOGY_CONFIG_SHA256` is identical at `0a6457a`, `6739658` and
  `92dc07a` — and equals the hash embedded in all 3,835,988 artifact rows. Measurement semantics
  are invariant.
- tokenizer: the full-run implementation was materialised at `92dc07a`; all configuration hashes
  embedded in the artifact reproduce from a live encoder rebuild (§7).

Correction applied (metadata only — no artifact byte, estimand, feature semantic, or algorithm was
touched):

| | BEFORE | AFTER |
|---|---|---|
| `MORPH_FEATURES_KIWI_MANIFEST_v001` | `artifact_record_commit` absent | `= 67396588aa5b03dc9f57a89a9a41365eb04f993c` |
| `TOKEN_O200K_BASE_MANIFEST_v001` | `artifact_record_commit` absent | `= 92dc07a6f2c5af3c3161d7f7a615dc7211e27559` |
| both | no lineage explanation | `lineage_note` recording the §30.2 split and the semantic-invariance evidence |

**IMPACT**: reproduction is now unambiguously anchored to the artifact-record commit. Artifact
SHA-256 values are unchanged (re-verified after the edit).

## 16. Memory-monitoring finding

```
CLASSIFICATION: EXECUTION_MONITORING_DEFECT  (execution instrumentation, not artifact integrity)
```

| run | samples | reported min MemAvailable | peak RSS | swap out | worst |
|---|---:|---:|---:|---:|---|
| MORPH full | **2** | 7.499 GiB | 0.822 GiB | 64 pages | YELLOW |
| TOKEN full | **2** | 6.063 GiB | 0.363 GiB | 64 pages | YELLOW |

Only **two** guard samples were taken across runs of 188 s and 133 s. External observation during
the run reported a MemAvailable minimum near 4.75 GiB, below both recorded minima. With a sample
count of 2 the guard **cannot** have captured the true minimum, so the recorded minima are not
trustworthy lower bounds.

No re-run is required. Memory pressure did not corrupt data, and this is not inferred from the
guard — it follows from the independent full-population validations above: 0 mismatches on every
field of every artifact, 0 identity violations, exact stored-vs-recomputed agreement, and identical
pair-set hashes across three artifacts. Swap activity was 64 pages out (≈256 KiB) with 0 pages in.

**Required before the next heavy run**: periodic sampling (fixed interval, not endpoint-only) so
that `min_mem_available_gib` is a genuine minimum rather than a sample of two.

## 17. Test suite

```
pytest : 125 passed, 1 failed
ruff   : All checks passed
mypy   : 75 errors in 8 files (pre-existing; scripts/ DuckDB fetchone() Optional handling)
```

The single failure is
`tests/test_phase2.py::test_canonical_notebook_consumes_v11_and_authorizes_only_population_qc`,
asserting that `notebooks/02_normalize_and_qc.ipynb` stores no execution counts.

```
HEAD committed  : 12 code cells, 0 with non-null execution_count   → test passes on a clean tree
working tree    : 12 code cells, 12 with non-null execution_count  → test fails locally
```

```
CLASSIFICATION: WORKING_TREE_HYGIENE  (uncommitted executed notebook state)
```

This is not a repository defect and not an artifact defect. The committed tree is clean. Claude-B
did not modify the file — it is A's uncommitted work. The mypy errors are pre-existing engineering
hygiene in `scripts/`, outside the measurement path, and are recorded rather than fixed.

## 18. Gate verdicts

### G2 — Representation Integrity

| criterion | evidence |
|---|---|
| Unicode normalization audit | NFC-stable, 0/102,278 deviations (§5) |
| codepoint / grapheme / byte unit correctness | independently recomputed, 0 mismatches on 21 field groups (§5) |
| exact decomposition, all pairs | full population, max identity error 8.88e-16, 0 violations, stored fields reproduce exactly (§6) |
| artifact identity, cohort, pair set | SHA match, N = 3,835,988, identical pair-set hash, 0 G1-excluded (§1, §3) |
| schema / lineage | 49 columns, §12.2 lexical group present; lineage metadata corrected (§15.1) |

```
G2_REPRESENTATION_INTEGRITY_PASS
```

### G3 — Tokenizer Integrity

| criterion | evidence |
|---|---|
| roundtrip 100 % | stored flag: 0 failures over 3,835,988; independent decode **and** encode audit over 20,524 pairs: 0 mismatches (§8, §9) |
| tiktoken version / hash | `0.13.0`, `encoding_file_sha256` matches live rebuild and Phase-0 (§7) |
| `pat_str` hash | `2d1b8dc1…` matches across three independent sources, 1 distinct value population-wide (§7) |
| token byte audit | 5,951 tokens, 0 reconstruction mismatches, 173 genuine multi-byte splits exercised (§10) |
| D-04 physical schema contract | all 15 §12.4 fields present; 28-vs-29 resolved as commit prose typo (§2.1) |
| structural invariants | list lengths, positivity, ID range `[0, 199997] < n_vocab`, no special tokens (§8) |

```
G3_TOKENIZER_INTEGRITY_PASS
```

### G4 — Morphology Integrity

| criterion | evidence |
|---|---|
| analyzer / version / hash | Kiwi `0.23.2` / model `0.23.0` / config `6f48802a…`, 1 distinct value each over the full population (§11) |
| failure rate | `zero_morpheme_rows = 0`, `analysis_warning_rate = 0.0`, `eojeol_count ≤ 0` = 0 (§11) |
| POS mapping freeze | every count re-derived from the stored sequence, 0 mismatches over 3,835,988 rows (§11) |
| XSA-I fix applied population-wide | delta 28,492 over 28,029 rows, exactly equal to the independently counted `XSA-I` occurrences (§12) |
| sample manual inspection | Director N = 100, workbook SHA re-verified, O 94 / X 6, 0 implementation defects (§14) |
| systematic implementation defect | **NO** |

```
G4_MORPHOLOGY_INTEGRITY_PASS
```

## 19. Remaining non-blocking risks

| # | item | class | owner |
|---|---|---|---|
| R1 | Memory guard sampled twice per run; recorded minima are not true minima | EXECUTION_MONITORING_DEFECT | A — periodic sampling before the next heavy run |
| R2 | `92dc07a` commit body states `29 columns`; artifact and manifest carry 28 | immutable prose error | recorded here; do not propagate the figure |
| R3 | `eojeol_count = 1` band (42,096 rows, 1.10 %) carries the density/particle-ratio maxima; analyzer artefacts concentrate here | reporting caveat | carry into NB07/NB08 distribution reporting and extreme-case panels |
| R4 | `notebooks/02_normalize_and_qc.ipynb` executed in the working tree, failing a hygiene test | WORKING_TREE_HYGIENE | A — strip outputs or commit intentionally |
| R5 | mypy: 75 errors in 8 files, concentrated in `scripts/` Optional handling | pre-existing engineering hygiene | A — outside the measurement path |
| R6 | Branch `results/preliminary-eda-v1-20260817` (`aabd068`) holds a preliminary multilayer results snapshot off `main` | scope | not gate evidence; V2 EDA remains **HOLD** |

None of R1–R6 affects artifact integrity, and none was allowed to influence the verdicts above.

## 20. Next-gate prerequisites

```
MEASUREMENT_FOUNDATION_CLOSED_THROUGH_G4
```

The measurement foundation — cohort → representation → morphology → tokenization → exact
decomposition — is closed and independently verified end to end.

Still **HOLD**, per directive: `NB06`, `NB07`, `NB08`, V2 EDA. G5 (collinearity / identifiability)
and G6 have not been entered. `REPRESENTATION_EDA_MANIFEST_v001` remains pinned to the historical
`REP_FEATURES_v001`; its 47 shared feature values are unchanged in v002 by the D2-3 exact-equality
result, so it requires an addendum for the two new lexical columns rather than a re-run.

---

**Adjudication closed**: 2026-08-17 17:30 KST, Claude-B (Evidence Validator / Research Gate Steward).
**Adjudicated main**: `92dc07a6f2c5af3c3161d7f7a615dc7211e27559`

```
G2_REPRESENTATION_INTEGRITY_PASS
G3_TOKENIZER_INTEGRITY_PASS
G4_MORPHOLOGY_INTEGRITY_PASS

MEASUREMENT_FOUNDATION_CLOSED_THROUGH_G4
```
