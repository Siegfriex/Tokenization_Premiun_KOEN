# KOEN — G5 Analysis Readiness Adjudication

> **Adjudicator**: Claude-B (Research / Statistics / Identifiability)
> **Snapshot**: 2026-08-18 13:25 KST
> **Base main**: `4eaa35e8437fc9013305c2b3fcf53133f2a0bddf`
> **Branch**: `research/g5-analysis-readiness-20260818`
> **Protocol**: `G5_DIAGNOSTIC_PROTOCOL_v001` frozen at `4e9bab8b0f2e71ee3b5f8f5fb0ea6ca2480b48fc`,
> pushed **before** any rank, condition-number, VIF or correlation value was computed.
>
> **Authority**: `KOEN-TP-RS-001` §12 · §13 · §18 · §19 · §20.2 · §21 · §31 · §32 →
> `RD-FAST-G5-01` · `CR-FAST-G5-REALIZED-MODEL-01` · `CR-FAST-G5-SPLIT-RELOCATION-01` ·
> `RD-SSOT-CANONICAL-RETURN-01` · `RD-G5-ENTRY-GOVERNANCE-CLOSEOUT-01`

No model was fitted. No coefficient was produced. This gate measures whether the approved design is
estimable and numerically acceptable — nothing about what it would estimate.

```
PRIOR_G5_SCRATCH_OBSERVED = YES
PRIOR_G5_SCRATCH_EVIDENCE = NO
```

Every number below comes from this working line's own execution against the canonical artifacts.

---

## 1. Split-manifest override — applied

`KOEN-TP-RS-001` §31 lists **split manifest freeze** among G5's four PASS conditions.
`CR-FAST-G5-SPLIT-RELOCATION-01` (`RD-FAST-G5-01` §8, APPROVED) relocates it, together with `LR-01`
near-duplicate grouping, to **PRE-NB10 PREDICTIVE READINESS**, because NB07, NB08 and NB09 use no
train/validation/test split.

```
SPLIT_MANIFEST_SCORED_AS_G5_CONDITION = NO   (override applied, not an omission)
SPLIT_MANIFEST_RELOCATED_TO           = PRE-NB10
LR-01_WEAKENED                        = NO
```

G5 is therefore adjudicated on three conditions: cohort freeze, identifiability, collinearity /
composition.

---

## 2. Artifact identity

| dataset | expected SHA-256 | result | placement |
|---|---|---|---|
| D-01 `PAIR_REGISTRY_v002` | `95f523d1…10bec52` | **MATCH** | symlink → canonical store |
| D-02 `REP_FEATURES_v002` | `dfae8e01…50d309` | **MATCH** | symlink → canonical store |
| D-03 `MORPH_FEATURES_KIWI_v001` | `0fe5bd74…3e50f7d` | **MATCH** | symlink → canonical store |
| D-04 `TOKEN_O200K_BASE_v001` | `1c30e327…2c16e7` | **MATCH** | symlink → canonical store |
| D-05 `CHUNK_O200K_BASE_v001` | `bfa98bd6…1944ab` | **MATCH** | independent copy in this tree |

```
ARTIFACT_IDENTITY = 5 / 5
```

D-05 was copied (`cp --reflink=auto`; ext4 has no reflink support, so an ordinary copy), **not**
hardlinked: link count 1, inode 1702251, distinct from the NB06 worktree's inode 1699463.

---

## 3. Analysis cohort freeze

```
cohort_id            ANALYSIS_COHORT_v001
N                    3,835,988          matches expected
distinct pair_id     3,835,988
pair-set hash        d9660d654ee449e4d0c23a0070225274   matches expected
```

The cohort is the D-04 pair-id spine. D-01 carries 5,652,925 rows; every join to the D-04 spine
preserved N exactly, so no row was silently gained or lost.

Completeness across all 39 model-required continuous columns plus both outcomes and all five
categorical fields:

```
null values                    0
non-finite values              0
categorical nulls              0
non-positive log arguments     0   (ko/en codepoint counts and chunk counts all > 0)
total_null_or_nonfinite        0
```

Primary exclusions: **NONE** beyond the frozen G1 cohort. Retained by policy:
`translation_direction = UNKNOWN` (50,547), `eojeol_count = 1`, short texts, TP extremes, morphology
extremes. Post-hoc, result-dependent row deletion is **forbidden** and none occurred.

```
ANALYSIS_COHORT_FROZEN
```

---

## 4. Structural pruning — measured, not assumed

Every removal is justified by an identity, a degenerate level or a composition. None is justified by
an association with either outcome. Each identity was verified numerically over all 3,835,988 rows.

### 4.1 Approved covariate decisions, re-measured

| variable | claim | measured | classification |
|---|---|---|---|
| `sentence_type` | one realized level | `other` = 3,835,988 / 3,835,988 | `REALIZED_ZERO_VARIANCE_COVARIATE` · `NON_ESTIMABLE` |
| `logical_corpus` | bijective with `source_id` | 2 distinct / 2 distinct / 2 joint | `DETERMINISTIC_CATEGORICAL_REDUNDANCY` — provenance only |

Both `CR-FAST-G5-REALIZED-MODEL-01` §4.1 and §4.2 hold on the realized data.

### 4.2 Exact identities and deterministic duplicates

| relation | max abs error over N | classification |
|---|---:|---|
| `ko_chunk_token_total == ko_token_count` | **0.0** | `OUTCOME_LEAKAGE_EXCLUSION` |
| `en_chunk_token_total == en_token_count` | **0.0** | `OUTCOME_LEAKAGE_EXCLUSION` |
| `ko_chunk_byte_total == ko_utf8_bytes` | **0.0** | `DETERMINISTIC_DERIVED_DUPLICATE` |
| `en_chunk_byte_total == en_utf8_bytes` | **0.0** | `DETERMINISTIC_DERIVED_DUPLICATE` |
| `ln(ko_tokens_per_byte) − ln(en_tokens_per_byte) == log_compression_penalty` | 4.44e-16 | `EXACT_ALGEBRAIC_IDENTITY` |
| `ln(ko_tpc) − ln(en_tpc) == log_token_premium − logCR` | 6.66e-16 | `OUTCOME_LEAKAGE_EXCLUSION` |
| `ln(pair_byte_ratio) == logCR + logBDR` | 8.88e-16 | `EXACT_ALGEBRAIC_IDENTITY` |
| `ln(pair_chunk_ratio) == ko_chunk_count_log − en_chunk_count_log` | 8.88e-16 | `EXACT_ALGEBRAIC_IDENTITY` |
| `tokens_per_chunk × chunk_count == chunk_token_total` (both sides) | 5.68e-14 | `OUTCOME_LEAKAGE_EXCLUSION` |
| `pair_codepoint_ratio == exp(logCR)` | 1.42e-14 | `DETERMINISTIC_DERIVED_DUPLICATE` |
| `ko_whitespace_count == ko_whitespace_density × ko_codepoint_count` | 1.42e-14 | `DETERMINISTIC_DERIVED_DUPLICATE` |

The first four rows are the substantive findings of this gate. `chunk_token_total` **is** the token
count, to the bit. Since `logTP = ln(T_KO/T_EN)`, admitting it — or admitting `tokens_per_chunk`
alongside `chunk_count` — would place the outcome on the right-hand side of the M3 model.
`chunk_byte_total` is likewise the exact UTF-8 byte count already carried by `logBDR`.

Control identity, unchanged from G2: `log_token_premium == logCR + logBDR + logCP` holds to
8.88e-16 over the full cohort.

### 4.3 Compositional reference exclusions

| family | closure | max abs deviation | reference excluded |
|---|---|---:|---|
| KO script shares + whitespace density | `= 1` | 2.22e-16 | `ko_hangul_share` |
| EN script shares + whitespace density | `= 1` | 2.22e-16 | `en_latin_share` |
| KO D-05 chunk type shares | `= 1` | 2.22e-16 | `ko_chunk_type_share_letter` |
| EN D-05 chunk type shares | `= 1` | 2.22e-16 | `en_chunk_type_share_letter` |

References were fixed **definitionally** in the frozen protocol (§6.3) — the side's own native script
and the D-05 base chunk class — before any diagnostic ran. No reference was re-selected in response
to a VIF.

Note that the composition closes only when `whitespace_density` is included with the five script
shares. `delta_whitespace_density` therefore enters the model as the KO−EN difference and the raw
per-side densities stay out, which keeps the composition from being saturated.

```
COMPOSITION_STATUS = VALID
```

### 4.4 Zero and near-zero variance

```
zero-variance design columns        NONE
near-zero-variance review (binary)  NONE   (smallest dummy share far above 0.001·N)
```

---

## 5. Identifiability

### 5.1 `source × domain` (SSOT §20.2, §32 T-04)

Two sources, four domains, five realized cells:

```
025 × dialogue      516,162        026 × other         990,120
025 × general       804,291        026 × technology    359,905
025 × other       1,165,510
```

Only `other` occurs under both sources. `dialogue` and `general` are exclusive to 025;
`technology` is exclusive to 026. **Independent main effects of source and domain are therefore not
separately identifiable.**

The approved design already anticipates this: it uses `source_domain_cell`, an observed-stratum
conditional control, whose coefficients may **not** be read as a pure source effect or a pure domain
effect. This is SSOT §20.1's final clause applied to the realized data.

```
SOURCE_DOMAIN_IDENTIFIABILITY = COMPOSITE_CELL_CONTROL_ONLY      → NOTE ID-03
```

### 5.2 `source_domain_cell × translation_direction` (SSOT §32 T-03)

| cell | KO_TO_EN | EN_TO_KO | UNKNOWN |
|---|---:|---:|---:|
| 025-dialogue | 247,947 | 254,955 | 13,260 |
| 025-general | 354,654 | 449,606 | **31** |
| 025-other | 559,527 | 568,728 | 37,255 |
| 026-other | 990,119 | **0** | **1** |
| 026-technology | 359,905 | **0** | **0** |

Three of fifteen combinations are empty and two more are near-singletons (31 and 1). The 026 family
contains **no** `EN_TO_KO` observation at all.

Under the contracted main-effects-only coding this does not break estimability — M0 is full rank and
the direction contrast is identified from within-025 variation. But the identification source is
narrow and must be stated whenever a direction coefficient is interpreted. A `cell × direction`
interaction is **not estimable** in this realized design and is not introduced.

```
DIRECTION_IDENTIFIABILITY = MAIN_EFFECT_ESTIMABLE_FROM_025_WITHIN_VARIATION   → NOTE ID-04
CELL_x_DIRECTION_INTERACTION = NOT_ESTIMABLE_NOT_INTRODUCED
```

### 5.3 Reference levels — instantiated from the frozen rule

```
source_domain_cell     025-…-other        (largest realized cell, 1,165,510)
translation_direction  KO_TO_EN           (largest realized level, 2,512,152)
```

---

## 6. Rank

Streaming Householder QR on the standardized design, singular values from the resulting R factor;
rank counted at `max(N, p) · eps · σ_max`.

| model | p (incl. intercept) | rank | deficiency |
|---|---:|---:|---:|
| M0 | 8 | 8 | **0** |
| M1 | 23 | 23 | **0** |
| M2 | 27 | 27 | **0** |
| M2A | 26 | 26 | **0** |
| M3 | 45 | 45 | **0** |

```
RANK_STATUS = FULL_RANK_ALL_MODELS
NO_HARD_STOP
```

Outcome A and Outcome B share an identical right-hand side, so these ranks apply to both. Neither
outcome is reconstructible from its own design: `log_compression_penalty` and the
`tokens_per_byte` pair are excluded from the A matrix, `log_token_premium` and the
`tokens_per_codepoint` pair from the B matrix, and the token counts and D-05 token totals from both.

```
OUTCOME_A_MATRIX_STATUS = ESTIMABLE · NO_SELF_RECONSTRUCTION
OUTCOME_B_MATRIX_STATUS = ESTIMABLE · NO_SELF_RECONSTRUCTION · IDENTICAL_RHS_TO_A
```

---

## 7. Collinearity

Triggers: condition number ≥ 100 → `REPARAMETERIZATION_REVIEW`; VIF/GVIF ≥ 20 →
`STRONG_REDUNDANCY_REVIEW`; `|Spearman ρ| ≥ 0.95` within a construct family →
`REPRESENTATIVE_FEATURE_REVIEW`. **None of these is an automatic drop.**

| model | cond. (standardized) | cond. (raw coding) | max VIF | trigger |
|---|---:|---:|---:|---|
| M0 | 10.24 | 36.58 | 3.25 | — |
| M1 | 20.10 | 5,110.55 | 12.95 | — |
| M2 | 20.98 | 5,712.99 | 17.47 | — |
| M2A | 20.97 | 5,719.03 | 16.69 | — |
| M3 | **134.57** | 33,381.31 | **1,252.61** | both fired |

The standardized figure is the trigger quantity. The raw-coding figure is large for every model
simply because the columns sit on wildly different natural scales (log ratios near 0, shares in
[0,1], switch counts in the tens); it is reported for completeness and is explicitly not a trigger.

GVIF for the categorical blocks is mild throughout — `source_domain_cell` `GVIF^(1/2df)` ranges
1.19–1.34 and `translation_direction` 1.10–1.16 across M0–M3. **The categorical coding is not the
source of any collinearity pressure.**

### 7.1 M3 — both triggers fire

Top VIFs: `pair_log_size` 1,252.61 · `en_chunk_count_log` 854.04 · `ko_chunk_count_log` 791.04 ·
`log_code_point_ratio` 60.41 · `en_mean_chunk_bytes` 51.53 · `ko_mean_chunk_bytes` 47.99.

The cause is interpretable rather than pathological: the number of regex chunks is close to
proportional to text length, so the chunk-scale terms nearly reproduce the M0 length term and the M1
length ratio. Rank is full, so this is a **reparameterization question, not a structural defect** —
resolve it before M3 is fitted, not by deleting a variable here.

```
M3_STRUCTURAL_READINESS = REVIEW                                  → REVIEW M3-01
```

### 7.2 Same-construct Spearman screening

Computed on the full cohort — no sampling, therefore no seed — and within the frozen families only.
No all-pairs fishing was performed.

| family | max abs ρ | pair | trigger |
|---|---:|---|---|
| `script_mixing` | **0.9994** | `en_script_type_count ~ en_script_switch_count` | **fired** |
| `script_mixing` | **0.9910** | `ko_script_type_count ~ ko_script_switch_count` | **fired** |
| `d05_chunk_type_en` | 0.9053 | `en_chunk_type_share_number ~ …_whitespace` | — |
| `d05_chunk_scale` | 0.9368 | `ko_chunk_count_log ~ en_chunk_count_log` | — |
| `d05_chunk_bytes_ko` | 0.8307 | `ko_mean_chunk_bytes ~ ko_p50_chunk_bytes` | — |
| `d05_chunk_bytes_en` | 0.7861 | `en_mean_chunk_bytes ~ en_p90_chunk_bytes` | — |
| `d05_chunk_type_ko` | 0.7516 | `ko_chunk_type_share_number ~ …_whitespace` | — |
| `morphology` | 0.6014 | `ending_ratio ~ function_morpheme_ratio` | — |
| `en_script_comp` | 0.2830 | `en_punctuation_share ~ en_symbol_other_share` | — |
| `d05_max_tokens` | 0.2729 | `ko_max_tokens_per_chunk ~ en_max_tokens_per_chunk` | — |
| `ko_script_comp` | 0.2626 | `ko_punctuation_share ~ ko_symbol_other_share` | — |
| `pair_scale` | 0.2157 | `pair_log_size ~ log_code_point_ratio` | — |

**Two same-side pairs fire, both inside the M1 script-mixing block.** `script_type_count` and
`script_switch_count` are very nearly rank-equivalent within each language side — 0.9994 on the EN
side and 0.9910 on the KO side. This is not an M3-only issue: it is carried by M1, M2, M2A and M3
alike. Their VIFs stay moderate (`en_script_type_count` 9.11–9.16), so linear redundancy is not
extreme, but the monotone relationship is near-perfect and a representative feature must be chosen
on construct grounds — not on a coefficient — before the script-mixing block is interpreted.

```
SCRIPT_MIXING_REDUNDANCY = REPRESENTATIVE_FEATURE_REVIEW          → REVIEW SM-01
```

The `morphology` family is deliberately screened across the M2 and M2A blocks so that the
`function_morpheme_ratio` versus `particle_ratio + ending_ratio` relationship is measured even
though the two never enter one model. Its maximum is 0.6014 — well below the trigger — which is
consistent with M2 and M2A being genuine alternatives rather than restatements.

A low `|ρ|` does not establish the absence of collinearity and is not reported as if it did.

### 7.3 Disagreement with the quarantined scratch — disclosed

`ssot_g5/01_G5_ENTRY_DECISION.md` §3 requires that any disagreement with the previously observed
2026-08-17 scratch be reported rather than reconciled. The scratch reported a single pooled
`script_switching` family figure of roughly 0.52 and did **not** raise a representative-feature
review for it. This execution, screening the same construct with both same-side pairs present, finds
0.9994 and 0.9910. **The fresh result governs.** The practical consequence is that `SM-01` is a new
review item that the earlier working line did not carry.

---

## 8. Verdict

| G5 condition | result |
|---|---|
| artifact identities exact | **PASS** (5/5) |
| analysis cohort frozen | **PASS** (N, pair-set, zero incompleteness) |
| structural removals justified without outcome reference | **PASS** (all identities measured) |
| M0 full rank | **PASS** (8/8) |
| M1 full rank | **PASS** (23/23) |
| M2 full rank | **PASS** (27/27) |
| M2A full rank | **PASS** (26/26) |
| M3 full rank after structural pruning | **PASS** (45/45) |
| intended categorical contrasts estimable | **PASS** with `ID-03`, `ID-04` |
| composition coding valid | **PASS** (closure 2.22e-16, reference-coded) |
| no unresolved deterministic redundancy | **PASS** (all resolved structurally) |
| Outcome A / Outcome B both estimable, neither self-reconstructing | **PASS** |
| split manifest | **NOT A G5 CONDITION** — relocated to PRE-NB10 |

No `HARD FAIL` condition is present: no unresolved rank deficiency, no structurally non-estimable
required variable, no artifact identity mismatch, no cohort ambiguity, no missingness.

```
G5_ANALYSIS_READINESS_PASS_WITH_NOTES

ANALYSIS_COHORT_FROZEN
REALIZED_MODEL_CONTRACT_FROZEN
OUTCOME_A_CONTRACT = FROZEN
OUTCOME_B_CONTRACT = FROZEN (SPEC-02 recorded)
```

### 8.1 Registers, kept separate

**HARD FAIL** — none.

**REVIEW TRIGGER** — resolution required before the affected model is fitted, not a failure:

| id | item | owner |
|---|---|---|
| `M3-01` | M3 fires both collinearity triggers through chunk-scale ↔ length (cond 134.57, VIF 1,252.61). Fix a reparameterization or a representative rule **in advance** of fitting M3. | pre-M3 |
| `SM-01` | `script_type_count ~ script_switch_count` is near rank-equivalent on both sides (0.9994 EN, 0.9910 KO). Choose a representative on construct grounds before the M1 script-mixing block is interpreted. Affects M1, M2, M2A, M3. | pre-M1 interpretation |

**NOTE** — interpretation constraints carried to NB09:

| id | item |
|---|---|
| `ID-03` | source and domain are not separately identifiable; `source_domain_cell` is an observed-stratum control only, never a pure source or pure domain effect |
| `ID-04` | the direction contrast is identified from within-025 variation only; 026 contains no `EN_TO_KO`; `cell × direction` interaction is not estimable |
| `SPEC-01` | D-02 special-expression flags, space-run counts and grapheme-scale parallels are held for NB11 sensitivity, not entered in any primary matrix |
| `SPEC-02` | SSOT §18.2's illustrative Outcome-B form omits `logCR`/`logBDR`; the approved common ladder includes them, so Outcome B's M1 conditions on both representation ratios |

**OPERATIONAL DEBT** — no bearing on estimability:

| id | item | owner |
|---|---|---|
| `OPS-G5-01` | D-05 exists in `KOEN_nb06_d05` and in this G5 tree, but not in the canonical working tree; place it there before NB09 executes from that tree | Claude-A |
| `OPS-G5-02` | the canonical working tree is still at `07d132e` with three preserved untracked recovery files; fast-forward it when convenient — it is not a G5 prerequisite | Claude-A |

---

## 9. Claim boundary at this snapshot

**Permitted.** The realized M0, M1, M2, M2A and M3 design matrices are full rank on the frozen
cohort of 3,835,988 pairs; the identifiability, rank, condition-number, VIF/GVIF and same-construct
correlation figures above were measured on those actual matrices, for both Outcome A and Outcome B.

**Not permitted** — none of the following is established by anything in this document:

```
that any explanatory result exists
that the morphology block has, or lacks, incremental value
that any coefficient has been estimated
that source or domain effects have been separated
that M3 is ready to fit
that regex chunking explains fragmentation
any causal statement whatsoever
```

---

## 10. Execution record

```
protocol frozen     4e9bab8b0f2e71ee3b5f8f5fb0ea6ca2480b48fc   (pushed before execution)
cohort build        G5_COHORT_v001      24.6 s · 4 samples @10 s · peak RSS 3.25 GiB
                                        min MemAvailable 7.35 GiB · worst status YELLOW
                                        RED-or-worse samples 0 · guard abort none
diagnostics         G5_DIAG_PASS1 / G5_DIAG_PASS2 / G5_DIAG_SPEARMAN, all under the same
                    10-second periodic telemetry contract (ENG-OBS-001 · R1)
no fabricated percentage or ETA was emitted; rows_per_second is null where the denominator
was not known
```

Outputs:

```
outputs/manifests/ANALYSIS_COHORT_v001.json
outputs/reports/G5_REALIZED_MODEL_CONTRACT_v001.json
outputs/reports/G5_IDENTIFIABILITY_v001.json
outputs/reports/G5_COLLINEARITY_v001.json
```

No parquet, no raw KO/EN text, no `pair_id` list and no token or chunk string is written to any of
them.

---

**Adjudication closed**: 2026-08-18 13:25 KST, Claude-B.
**Next canonical stage**: NB07 — after Director confirmation and Claude-A's independent G5 audit.
**This branch is not merged to `main`.**
