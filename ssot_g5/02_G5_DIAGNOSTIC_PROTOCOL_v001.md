# G5 Diagnostic Protocol v001

> Protocol ID: `G5_DIAGNOSTIC_PROTOCOL_v001`
> Frozen: 2026-08-18 13:12 KST — **before any rank, condition-number, VIF/GVIF or correlation
> value was computed in this working line.**
>
> Base: `4eaa35e8437fc9013305c2b3fcf53133f2a0bddf`

Every predictor, removal, reference level, transform and threshold below is fixed here and is not
revised in response to any result. Nothing in this document is derived from the quarantined
2026-08-17 scratch (`01_G5_ENTRY_DECISION.md` §3).

---

## 1. Cohort

```
cohort_id            ANALYSIS_COHORT_v001
definition           the pair_id set of D-04 TOKEN_O200K_BASE_v001, which is the frozen final
                     validated pair universe (RD-FAST-G5-01 §7; ssot_nb01/02 primary_cohort_n)
expected N           3,835,988
expected pair-set    d9660d654ee449e4d0c23a0070225274
pair-set definition  md5(string_agg(pair_id, '' ORDER BY pair_id))   — lineage.pair_set_md5
join                 inner join D-01/D-02/D-03/D-05 on pair_id
join requirement     each join must preserve N exactly; any loss is a HARD FAIL
```

Primary exclusions: **NONE** beyond the frozen G1 final cohort (`RD-FAST-G5-01` §7). Retained by
policy: `translation_direction = UNKNOWN`, `eojeol_count = 1`, short texts, TP extremes, morphology
extremes. Post-hoc, result-dependent row deletion is **forbidden**.

Sensitivity cohorts named but **not** executed at this gate: known-direction only,
`eojeol_count > 1`, short-text removed, `domain = other`, central length strata.

---

## 2. Outcomes — both frozen

```
OUTCOME A   Y_A = log_token_premium            D-04   (KOEN-TP-RS-001 §18.1; primary)
OUTCOME B   Y_B = log_compression_penalty      D-04   (KOEN-TP-RS-001 §18.2; secondary mechanism)
```

Exact decomposition (SSOT §8, G2-verified): `logTP = logCR + logBDR + logCP`, therefore
`Y_B = Y_A − logCR − logBDR`. This identity drives the leakage rules in §5.

`IR-02`: the A model explains the total premium; the B model explains tokenizer compression
asymmetry once byte representation volume is separated. The two are reported separately.

**`SPEC-02` — recorded divergence, not a defect.** SSOT §18.2's *illustrative* form for Outcome B
(`예시:`) omits `logCodePointRatio` and `logByteDensityRatio`. The Director's approved common ladder
runs the identical M0–M3 ladder for both outcomes, with only the self-reconstruction prohibition
differing. This protocol follows the approved common ladder and records the divergence here so the
NB09 interpretation of Outcome B states that its M1 conditions on both representation ratios.

---

## 3. Frozen derived transforms

Only these four derived columns are constructed. Each is specified by authority; none is invented.

| name | definition | authority |
|---|---|---|
| `pair_log_size` | `0.5 * (ln(ko_codepoint_count) + ln(en_codepoint_count))` | `CR-FAST-G5-REALIZED-MODEL-01` §4.4 |
| `delta_whitespace_density` | `ko_whitespace_density − en_whitespace_density` | SSOT §13.4 + §18.1 `ΔWhitespaceDensity` |
| `ko_chunk_count_log` / `en_chunk_count_log` | `ln(ko_chunk_count)` / `ln(en_chunk_count)` | count-scale rule, §3.1 |
| `source_domain_cell` | `source_id ‖ '-' ‖ domain` | `CR-FAST-G5-REALIZED-MODEL-01` §4.3 |

No `+1` smoothing anywhere (SSOT §13.5; `CR` §4.4). `ko_codepoint_count`, `en_codepoint_count`,
`ko_chunk_count`, `en_chunk_count` are asserted strictly positive in §7; a non-positive value is a
HARD FAIL, never a smoothing trigger.

### 3.1 Count-scale rule

Count-valued predictors enter on the natural-log scale, consistent with the specification's own
treatment of size (`§13.5 LengthRatio = log(C_KO/C_EN)`; `CR §4.4 pair_log_size`). This applies to
`ko_chunk_count` / `en_chunk_count`. Share, ratio, density and byte-length columns enter on their
native scale.

---

## 4. Realized model ladder — exact physical columns

Categorical terms are treatment (dummy) coded with an intercept; the reference level is dropped.
Column names are the physical artifact columns unless marked *derived* (§3).

### M0 — both outcomes

| # | term | type | artifact |
|---|---|---|---|
| 1 | `pair_log_size` | continuous | *derived* from D-02 |
| 2 | `source_domain_cell` | categorical | *derived* from D-01 `source_id`, `domain` |
| 3 | `translation_direction` | categorical | D-01 |

`UNKNOWN` remains an explicit level of `translation_direction` in the primary cohort
(`CR` §5, M0).

### M1 = M0 + representation / surface block

Mapped from SSOT §18.1's explicit form
`β1 logCodePointRatio + β2 logByteDensityRatio + β3 ΔWhitespaceDensity + β4ᵀ ScriptFeatures`,
with `ScriptFeatures` resolved against the SSOT §12.2 D-02 variable groups *script* and *mixing*.

| # | term | type | artifact | §12.2 group |
|---|---|---|---|---|
| 4 | `log_code_point_ratio` | continuous | D-04 | — (§18.1 β1) |
| 5 | `log_byte_density_ratio` | continuous | D-04 | — (§18.1 β2) |
| 6 | `delta_whitespace_density` | continuous | *derived* from D-02 | whitespace (§18.1 β3) |
| 7 | `ko_latin_share` | continuous | D-02 | script |
| 8 | `ko_digit_share` | continuous | D-02 | script |
| 9 | `ko_punctuation_share` | continuous | D-02 | script |
| 10 | `ko_symbol_other_share` | continuous | D-02 | script |
| 11 | `en_hangul_share` | continuous | D-02 | script |
| 12 | `en_digit_share` | continuous | D-02 | script |
| 13 | `en_punctuation_share` | continuous | D-02 | script |
| 14 | `en_symbol_other_share` | continuous | D-02 | script |
| 15 | `ko_script_type_count` | continuous | D-02 | mixing |
| 16 | `ko_script_switch_count` | continuous | D-02 | mixing |
| 17 | `en_script_type_count` | continuous | D-02 | mixing |
| 18 | `en_script_switch_count` | continuous | D-02 | mixing |

`ko_hangul_share` and `en_latin_share` are the composition reference categories (§6.3).

### M2 = M1 + morphology block

| # | term | artifact |
|---|---|---|
| 19 | `morpheme_density` | D-03 |
| 20 | `particle_ratio` | D-03 |
| 21 | `ending_ratio` | D-03 |
| 22 | `deriv_affix_ratio` | D-03 |

### M2A = M1 + morphology sensitivity block

| # | term | artifact |
|---|---|---|
| 19a | `morpheme_density` | D-03 |
| 20a | `function_morpheme_ratio` | D-03 |
| 21a | `deriv_affix_ratio` | D-03 |

**Hard rule** (SSOT §12.3; `CR` §5): `function_morpheme_ratio` never coexists with
`particle_ratio` + `ending_ratio` in the same specification. M2 and M2A are alternatives, never
combined.

### M3 = M2 + D-05 regex-chunk mechanism block

Assembled from existing physical D-05 fields only. No new mechanism feature is created; no PCA or
other transform is introduced.

| # | term | artifact | §12.5 group |
|---|---|---|---|
| 23 | `ko_chunk_count_log` | *derived* from D-05 | chunk count |
| 24 | `en_chunk_count_log` | *derived* from D-05 | chunk count |
| 25 | `ko_mean_chunk_bytes` | D-05 | chunk byte length |
| 26 | `ko_p50_chunk_bytes` | D-05 | chunk length distribution |
| 27 | `ko_p90_chunk_bytes` | D-05 | chunk length distribution |
| 28 | `ko_max_chunk_bytes` | D-05 | chunk length distribution |
| 29 | `en_mean_chunk_bytes` | D-05 | chunk byte length |
| 30 | `en_p50_chunk_bytes` | D-05 | chunk length distribution |
| 31 | `en_p90_chunk_bytes` | D-05 | chunk length distribution |
| 32 | `en_max_chunk_bytes` | D-05 | chunk length distribution |
| 33 | `ko_max_tokens_per_chunk` | D-05 | chunk token load |
| 34 | `en_max_tokens_per_chunk` | D-05 | chunk token load |
| 35 | `ko_chunk_type_share_number` | D-05 | chunk type composition |
| 36 | `ko_chunk_type_share_punctuation` | D-05 | chunk type composition |
| 37 | `ko_chunk_type_share_whitespace` | D-05 | chunk type composition |
| 38 | `en_chunk_type_share_number` | D-05 | chunk type composition |
| 39 | `en_chunk_type_share_punctuation` | D-05 | chunk type composition |
| 40 | `en_chunk_type_share_whitespace` | D-05 | chunk type composition |

`ko_chunk_type_share_letter` / `en_chunk_type_share_letter` are the composition reference
categories (§6.3).

M3 is a **mechanism audit** (SSOT §19.3), not a stricter causal-adjustment model and not a
predictive-win claim. A high R² for M3 is expected and carries no scientific credit.

---

## 5. Outcome-leakage exclusions — structural, applied to both outcomes

Every exclusion below rests on an identity, not on an observed association. Each identity is
verified numerically at execution and the measured maximum absolute error is reported.

| excluded | identity | class |
|---|---|---|
| `log_token_premium`, `token_premium` | `Y_A` itself; with `logCR`+`logBDR` in M1 it reconstructs `Y_B = Y_A − logCR − logBDR` | `OUTCOME_LEAKAGE_EXCLUSION` |
| `log_compression_penalty`, `compression_penalty` | `Y_B` itself; with `logCR`+`logBDR` it reconstructs `Y_A` | `OUTCOME_LEAKAGE_EXCLUSION` |
| `ko_token_count`, `en_token_count`, `token_difference` | reconstruct `logTP = ln(T_KO/T_EN)` | `OUTCOME_LEAKAGE_EXCLUSION` |
| `ko_tokens_per_byte`, `en_tokens_per_byte` | `ln(ko_tpb) − ln(en_tpb) = logCP = Y_B` **exactly** | `EXACT_ALGEBRAIC_IDENTITY` |
| `ko_tokens_per_codepoint`, `en_tokens_per_codepoint` | `ln(ko_tpc) − ln(en_tpc) = logTP − logCR` | `OUTCOME_LEAKAGE_EXCLUSION` |
| `ko_chunk_token_total`, `en_chunk_token_total` | equal the D-04 token counts (D-05 token-equivalence contract) | `OUTCOME_LEAKAGE_EXCLUSION` |
| `ko_tokens_per_chunk`, `en_tokens_per_chunk` | `tokens_per_chunk × chunk_count = chunk_token_total = token count`; `chunk_count` is in M3 | `OUTCOME_LEAKAGE_EXCLUSION` |
| `code_point_ratio`, `byte_density_ratio` | non-log duplicates of terms 4 and 5 | `DETERMINISTIC_DERIVED_DUPLICATE` |

`log_code_point_ratio` and `log_byte_density_ratio` **remain admissible**: they are two of the three
exact-decomposition components, so the model residual for `Y_A` is the third
(`log_compression_penalty`), which is precisely the accounting intent of SSOT §18.1.

---

## 6. Structural removals — before any empirical diagnostic

`CR-FAST-G5-REALIZED-MODEL-01` §6 Step 1. Nothing here is removed for a p-value, a VIF or a
correlation.

### 6.1 Approved covariate decisions

| variable | basis | class |
|---|---|---|
| `sentence_type` | one realized level over the final cohort | `REALIZED_ZERO_VARIANCE_COVARIATE` · `NON_ESTIMABLE` (`CR` §4.1) |
| `logical_corpus` | bijective with `source_id` over the realized cohort | `DETERMINISTIC_CATEGORICAL_REDUNDANCY` — provenance only (`CR` §4.2) |
| `source_id` + `domain` as independent main effects | replaced by `source_domain_cell` | `OBSERVED_STRATUM_CONTROL` (`CR` §4.3) |

Both the zero-variance claim for `sentence_type` and the bijection claim for `logical_corpus` are
re-measured at execution and reported; they are not assumed.

### 6.2 Exact identities and deterministic duplicates

| excluded | basis | class |
|---|---|---|
| `pair_byte_ratio` | `ln(pair_byte_ratio) = log_code_point_ratio + log_byte_density_ratio` | `EXACT_ALGEBRAIC_IDENTITY` |
| `pair_codepoint_ratio` | `= exp(log_code_point_ratio)` | `DETERMINISTIC_DERIVED_DUPLICATE` |
| `pair_codepoint_diff` | deterministic in `ko/en_codepoint_count` | `DETERMINISTIC_DERIVED_DUPLICATE` |
| `pair_chunk_ratio` | `ln(pair_chunk_ratio) = ko_chunk_count_log − en_chunk_count_log` | `EXACT_ALGEBRAIC_IDENTITY` |
| `ko/en_chunk_byte_total` | regex chunks partition the analysis text, so this equals D-02 `utf8_bytes` | `DETERMINISTIC_DERIVED_DUPLICATE` |
| `ko/en_whitespace_count` | `= whitespace_density × codepoint_count` | `DETERMINISTIC_DERIVED_DUPLICATE` |
| `ko/en_codepoint_count`, `ko/en_utf8_bytes`, `ko/en_bytes_per_codepoint` | jointly absorbed by `pair_log_size` + `log_code_point_ratio` + `log_byte_density_ratio` | `SPECIFICATION_PARAMETERIZATION` |

### 6.3 Compositional reference exclusions

SSOT §21: script shares form a composition; exclude one reference category. References are fixed
**definitionally** — the side's own native script, and the D-05 base chunk class — so that no
reference is selected in response to a diagnostic.

| family | reference excluded | rule |
|---|---|---|
| KO script composition | `ko_hangul_share` | native script of the KO side |
| EN script composition | `en_latin_share` | native script of the EN side |
| KO D-05 chunk type | `ko_chunk_type_share_letter` | base chunk class |
| EN D-05 chunk type | `en_chunk_type_share_letter` | base chunk class |

Closure (`Σ shares ≈ 1`) is measured at execution and reported with its maximum absolute deviation.

### 6.4 Not in the primary specification

Present in the artifacts, deliberately **not** entered in any primary matrix at this gate, because
SSOT §18.1's explicit form does not carry them and `RD-SSOT-CANONICAL-RETURN-01` §11 forbids
expanding G5 into an open-ended feature audit.

| variable | disposition |
|---|---|
| `ko/en_url_flag`, `ko/en_email_flag`, `ko/en_emoji_flag`, `ko/en_code_like_flag` | D-02 *special expression*; `NB11_SENSITIVITY_AVAILABLE` |
| `ko/en_space_run_count` | count-scale surface variable outside §18.1's form; `NB11_SENSITIVITY_AVAILABLE` |
| `ko/en_whitespace_density` as separate levels | §18.1 specifies the difference; `SPECIFICATION_PARAMETERIZATION` |
| `ko/en_grapheme_count`, `pair_grapheme_ratio`, `ko/en_bytes_per_grapheme` | grapheme-scale parallels of the codepoint terms; `NB11_SENSITIVITY_AVAILABLE` |
| `ko_eojeol_count`, `en_word_count` | lexical length; enters M2 only through `morpheme_density`'s denominator |
| D-01 QC flags, provenance, raw text, `duplicate_group_id`, `length_stratum` | not covariates in any approved model |

Recorded as `SPEC-01`. These are scope decisions of this protocol, disclosed for Director
visibility, not structural impossibilities.

---

## 7. Cohort completeness checks — fail-closed

| check | requirement |
|---|---|
| row count | `= 3,835,988` |
| `pair_id` uniqueness | `distinct = N` |
| pair-set hash | `= d9660d654ee449e4d0c23a0070225274` |
| join preservation | every artifact join preserves N exactly |
| nulls in required columns | `0` |
| non-finite in required continuous columns | `0` |
| `ko_codepoint_count`, `en_codepoint_count` | strictly `> 0` |
| `ko_chunk_count`, `en_chunk_count` | strictly `> 0` |
| categorical nulls (`source_id`, `domain`, `translation_direction`, `logical_corpus`) | `0` |

Any violation is a **HARD FAIL**. Imputation, row deletion and smoothing are all forbidden
responses.

---

## 8. Diagnostic definitions — frozen before results

| item | definition |
|---|---|
| coding | treatment (dummy) coding, intercept included, reference level dropped |
| `source_domain_cell` reference | the **largest realized cell by N** (rule frozen here; the realized level is reported at execution) |
| `translation_direction` reference | the **largest realized level by N** (same rule) |
| composition references | §6.3, definitional |
| scaling for condition number | each continuous column centred and scaled to unit standard deviation; dummy columns left as 0/1; intercept a constant column. **The standardized figure is the trigger quantity.** |
| raw-coding condition number | also reported, explicitly **not** a trigger — natural scales differ by orders of magnitude |
| rank | `numpy.linalg.matrix_rank` on the standardized design, default tolerance `max(M,N) · eps · σ_max`; also reported as the count of singular values above that tolerance |
| VIF | `VIF_j = [R⁻¹]_jj` where `R` is the correlation matrix of the non-intercept design columns |
| GVIF | Fox–Monette for each categorical block: `GVIF = det(R_xx)·det(R_zz)/det(R_full)`, reported as `GVIF^(1/(2·df))` |
| zero variance | `sd = 0` → structural removal, `REALIZED_ZERO_VARIANCE_COVARIATE` |
| near-zero variance | a 0/1 column whose minority count `< 0.001·N` → `NEAR_ZERO_VARIANCE_REVIEW`, **not** an automatic removal |
| same-construct correlation | Spearman `ρ`, computed **within the families of §9 only**, on the full cohort — no sampling, therefore no seed |
| missing / non-finite | fail-closed per §7; never imputed |

Computation route: a single streaming pass accumulates the Gram matrix `XᵀX` (with intercept) for
each design; rank, condition number, VIF and GVIF are all derived from that exact Gram matrix. No
model is fitted and no coefficient is produced.

---

## 9. Same-construct correlation families

Screened within family only. No all-pairs fishing.

```
pair_scale          pair_log_size · log_code_point_ratio
ko_script_comp      ko_latin_share · ko_digit_share · ko_punctuation_share · ko_symbol_other_share
en_script_comp      en_hangul_share · en_digit_share · en_punctuation_share · en_symbol_other_share
script_mixing       ko_script_type_count · ko_script_switch_count
                    en_script_type_count · en_script_switch_count
morphology          morpheme_density · particle_ratio · ending_ratio · deriv_affix_ratio
                    · function_morpheme_ratio
d05_chunk_scale     ko_chunk_count_log · en_chunk_count_log
d05_chunk_bytes_ko  ko_mean_chunk_bytes · ko_p50_chunk_bytes · ko_p90_chunk_bytes · ko_max_chunk_bytes
d05_chunk_bytes_en  en_mean_chunk_bytes · en_p50_chunk_bytes · en_p90_chunk_bytes · en_max_chunk_bytes
d05_chunk_type_ko   ko_chunk_type_share_number · ko_chunk_type_share_punctuation
                    · ko_chunk_type_share_whitespace
d05_chunk_type_en   en_chunk_type_share_number · en_chunk_type_share_punctuation
                    · en_chunk_type_share_whitespace
d05_max_tokens      ko_max_tokens_per_chunk · en_max_tokens_per_chunk
```

`morphology` deliberately spans the M2 and M2A blocks so the `function_morpheme_ratio` versus
`particle_ratio + ending_ratio` relationship is measured, even though the two never enter one model.

A low `|ρ|` does not establish the absence of collinearity and will not be reported as if it did.

---

## 10. Thresholds and verdict semantics

```
design matrix rank deficient          → HARD FAIL / HARD STOP
condition number (standardized) ≥ 100 → REPARAMETERIZATION_REVIEW
VIF or GVIF ≥ 20                      → STRONG_REDUNDANCY_REVIEW
|Spearman ρ| ≥ 0.95 within family     → REPRESENTATIVE_FEATURE_REVIEW
zero variance                         → structural removal
near-zero variance (binary)           → NEAR_ZERO_VARIANCE_REVIEW
```

**A review trigger is not a failure.** `CR-FAST-G5-REALIZED-MODEL-01` §6 Step 3 and SSOT §21: values
below the triggers do not independently prove absence of multicollinearity, and values above them do
not independently stop the research. **VIF alone never deletes a variable and never determines
scientific meaning.**

The adjudication separates four registers and does not promote between them automatically:

```
HARD FAIL          rank deficiency · artifact identity mismatch · cohort ambiguity
                   · structurally non-estimable required variable
REVIEW TRIGGER     a threshold above fired; resolution required before the affected model is fitted
NOTE               interpretation constraint carried forward to NB09
OPERATIONAL DEBT   engineering or placement item, no bearing on estimability
```

---

## 11. Identifiability measurements

| measurement | purpose | authority |
|---|---|---|
| `source_id × domain` contingency | whether independent source and domain main effects are separable | SSOT §20.2, §32 T-04 |
| `source_domain_cell × translation_direction` contingency | whether the direction contrast is supported within cells | SSOT §20.2, §32 T-03 |
| level support for every categorical | zero and near-singleton cells | SSOT §20.2 |
| rank of each design | estimability | SSOT §31 |

If source and domain are structurally inseparable, `source_domain_cell` is used and its coefficients
may **not** be read as a pure source effect or a pure domain effect (SSOT §20.1 final clause). That
is a `NOTE`, not a `HARD FAIL`, because the approved design already uses the composite cell.

No `cell × direction` interaction is introduced at this gate.

---

## 12. Execution outputs

```
outputs/manifests/ANALYSIS_COHORT_v001.json
outputs/reports/G5_REALIZED_MODEL_CONTRACT_v001.json
outputs/reports/G5_IDENTIFIABILITY_v001.json
outputs/reports/G5_COLLINEARITY_v001.json
ssot/2026-08-18_<HHMM>_KOEN_TP_G5_ANALYSIS_READINESS_ADJUDICATION.md
```

No parquet, no raw KO/EN text, no `pair_id` list and no token/chunk string is written to any of
them.

## 13. Observability

Any stage expected to exceed 30 seconds runs under `tokenization_premium.telemetry.RuntimeTelemetry`
with a 10-second periodic sample carrying timestamp, stage, elapsed, rows processed when known,
rate, RSS, `MemAvailable`, swap state and status (`ENG-OBS-001`; `RD-FAST-G5-01` §12 R1;
`RD-SSOT-CANONICAL-RETURN-01` §10). Percentage and ETA are emitted only when the denominator is
actually known, and are never fabricated.
