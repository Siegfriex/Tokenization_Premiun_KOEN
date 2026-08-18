# PRE-NB09 Explanatory-Model Protocol v001

> Protocol ID: `PRE_NB09_PROTOCOL_v001`
>
> Frozen: 2026-08-18 14:46 KST — **before any model was fitted and before any coefficient,
> standard error, R² or model-comparison statistic existed in this working line.**
>
> Branch: `research/pre-nb09-protocol-20260818`
> Base: `9d99e13026b89dcf7d8846d0c105a811f64274bc` (`audit(g5): independently verify analysis readiness`)
>
> Authority: `KOEN-TP-RS-001` §17.3 · §18 · §19 · §20 · §21 · §22 · §23.1 · §24 · §29 · §32 →
> `RD-FAST-G5-01` / `CR-FAST-G5-REALIZED-MODEL-01` / `CR-FAST-G5-SPLIT-RELOCATION-01` ·
> `RD-SSOT-CANONICAL-RETURN-01` §14–§16 · `RD-G5-ENTRY-GOVERNANCE-CLOSEOUT-01`
>
> Operational authority of record: **`VD-NB09-OPERATIONALIZATION-01`** — R0
> `APPROVE_BLOCK_LEVEL_PRIMARY_INTERPRETATION` with the `SM-01`, `M3-01`, `ID-03`, `ID-04`,
> `SPEC-01`/`SPEC-02` dispositions transcribed in §8.
> `SSOT_CONFORMANT_OPERATIONALIZATION` · `NOT_A_DIRECTOR_DECISION`.

```
NB09_FITTED                 = NO
COEFFICIENT_PRODUCED        = NO
MODEL_COMPARISON_PRODUCED   = NO
PRIMARY_COLUMN_SET_CHANGED  = NO      (mechanically verified, §2.5)
EDA_USED_FOR_SELECTION      = NO
```

Planning reference, **not authority and not a decision**:
`dd525ef019c9dfe019db667799ce726f4943ce0f` (`docs(g5): prepare PRE-NB09 review decisions`) on
`research/g5-analysis-readiness-20260818`. It is referenced by SHA rather than cherry-picked,
because its option tables were superseded by the operational dispositions transcribed in §8 and merging a
stale alternatives list into the protocol lane would invite it being read as live. That branch is
now closed and does not move again.

---

## 0. Authority labels

`VD-BASELINE-20260818-1520` §6 forbids promoting an agent recommendation or a Vice-Director
operationalization into a Research Director decision. Every load-bearing statement in this protocol
is therefore labelled by its actual source.

| class | content in this document | may be relabelled `RD-*`? |
|---|---|---|
| **Research Director decision** `RD-*` | *none is claimed by this protocol.* No `RD-*` record was separately issued for the NB09 interpretation contract. | — |
| **Vice-Director operationalization** `VD-NB09-OPERATIONALIZATION-01` | R0 block-level primary interpretation; the `SM-01`, `M3-01`, `ID-03`, `ID-04`, `SPEC-01`/`SPEC-02` dispositions transcribed in §8; the instruction that the primary column set is not changed; the instruction that NB09 does not wait for EDA | **NO** — `SSOT_CONFORMANT_OPERATIONALIZATION`, `NOT_A_DIRECTOR_DECISION` |
| **SSOT** `KOEN-TP-RS-001` | outcomes §18; ladder §19; identifiability §20; collinearity §21; estimator family §22; full-cohort inference + bootstrap §23.1; robustness list §24; reporting and multiplicity §29; seed policy §30.3 | n/a — supreme authority |
| **Prior approved decisions** | `RD-FAST-G5-01`, `CR-FAST-G5-REALIZED-MODEL-01`, `CR-FAST-G5-SPLIT-RELOCATION-01`, `RD-SSOT-CANONICAL-RETURN-01`, `RD-G5-ENTRY-GOVERNANCE-CLOSEOUT-01` | n/a — already Director-approved |
| **Vice-Director operational baseline** `VD-BASELINE-20260818-1520` | gate/phase board §1; audit policy; branch immutability §11.1; observability §11.5; the globally forbidden claims restated in §7.5 | **NO** |
| **Agent-level derivation, Claude-B** | the HC1 primary SE choice; the multiplier-bootstrap companion; the refusal of cluster-robust SE; the seed-derivation rule and the three frozen seeds; the metric table in §5; the mandatory caveat in §5.1; the table-level limitation and instability sentences in §6.4 and §6.5 | **NO** — these are `B-*` findings offered for audit, not decisions |

Nothing in the agent-level row has been approved by the Director. If the protocol audit or the
Director rejects any of it, the item changes without touching the operational dispositions in §8.

### 0.1 Baseline verification at freeze

```
CANONICAL_MAIN_SHA     9fbcf0c127c804e8682edf1a1f14c3eea0e423a0   confirmed
CANONICAL_TREE_SHA     c80269a5113a69c403abd62b2afb1b38d09b2041   confirmed
BASE (this branch)     9d99e13026b89dcf7d8846d0c105a811f64274bc   tree == CANONICAL_TREE_SHA
```

Basing this lane on the audit-PASS commit rather than on the merge commit is the
`VD-BASELINE-20260818-1520` §9 critical-path rule, not drift: the two resolve to the same tree.

### 0.2 Corrections applied before audit handoff

`83a686c7b5064d8cd77f0e329e651eb235f2703b` was the first freeze of this protocol. Three defects
were found on re-checking it against `VD-BASELINE-20260818-1520` and are corrected here, **before**
any audit began and **before** any result exists — the only window in which correcting a frozen
protocol is legitimate. The superseded SHA is named so the change is visible rather than silent.

| # | defect in `83a686c` | correction |
|---|---|---|
| 1 | the bootstrap seed was deferred to run time ("derived from the protocol identifier, recorded before execution"), which is the reproducibility gap `VD-BASELINE-20260818-1520` §7 lists as a HARD FAIL class | seeds frozen in §3.3 and `03_NB09_SEED_REGISTRY_v001.json`, with the derivation rule verified against the RQ1 precedent and `determinism_status` recorded per SSOT §30.3 |
| 2 | the claim boundary omitted three globally forbidden claims — inherent Korean AI inefficiency, "UTF-8 3 bytes ⇒ 3× tokens", and token premium ⇒ reasoning degradation | §7.5 added |
| 3 | authority labels were not separated, so agent-level derivations such as the HC1 choice sat alongside Director dispositions without distinction | §0 added |

Also added: audit-subject immutability (§11.1) and the single-heavy-job constraint (§11.5).

---

## 1. Gate state entering NB09

```
G0 · G1 · G2 · G3 · G4        PASS / CLOSED
RQ1 / NB08                    PASS / CLOSED       RQ1_PRIMARY_INFERENCE_PASS
NB06 / D-05                   PASS / CLOSED
G5                            PASS_WITH_NOTES     independently audited, merged at 9fbcf0c
NB07                          canonical descriptive stage, runs in parallel — NOT a gate on this protocol
NB09                          protocol frozen here; execution not started
G6                            NOT OPEN
```

`CR-FAST-G5-SPLIT-RELOCATION-01` remains in force: split manifest and `LR-01` near-duplicate
grouping are **PRE-NB10** prerequisites, not NB09 prerequisites, and `LR-01` is not weakened.

---

## 2. Frozen model specification

### 2.1 Outcomes — both frozen

```
OUTCOME A   Y_A = log_token_premium          D-04   PRIMARY               SSOT §18.1
OUTCOME B   Y_B = log_compression_penalty    D-04   SECONDARY_MECHANISM   SSOT §18.2 · IR-02
```

Exact decomposition (G2-verified, re-verified at G5 to 8.9e-16):
`logTP = logCR + logBDR + logCP`, therefore `Y_B = Y_A − logCR − logBDR`.

`IR-02`: the A model explains the total premium; the B model explains tokenizer compression
asymmetry once byte representation volume is separated. The two are reported separately and their
narratives are **never merged**.

Binding on every NB09 output:

```
OUTCOME A   total tokenization premium association
OUTCOME B   compression asymmetry after representation accounting

OUTCOME B IS NOT "the cause of" OUTCOME A
```

The exact decomposition is an **accounting identity**, not causal mediation. `logCP` is defined as
the residual of `logTP` after `logCR` and `logBDR` are removed; writing that relationship as one
component "causing" another mistakes arithmetic for mechanism.

### 2.2 Right-hand side — identical for A and B

Both outcomes are fitted on the **same** design. G5 verified that neither outcome is reconstructible
from its own right-hand side. The exclusions that make this true are structural and were measured,
not assumed:

| excluded from both matrices | measured basis |
|---|---|
| `token_premium`, `log_token_premium` | `Y_A`; with `logCR`+`logBDR` reconstructs `Y_B` |
| `compression_penalty`, `log_compression_penalty` | `Y_B`; with `logCR`+`logBDR` reconstructs `Y_A` |
| `ko/en_tokens_per_byte` | `ln(ko) − ln(en) = logCP = Y_B` exactly (4.4e-16) |
| `ko/en_tokens_per_codepoint` | `ln(ko) − ln(en) = logTP − logCR` (6.7e-16) |
| `ko/en_token_count`, `token_difference` | reconstruct `logTP` |
| `ko/en_chunk_token_total` | equal the D-04 token counts (**0.0**) |
| `ko/en_tokens_per_chunk` | `× chunk_count = chunk_token_total` (5.7e-14) |
| `ko/en_chunk_byte_total` | equal D-02 `utf8_bytes` (**0.0**) |
| `pair_byte_ratio`, `pair_codepoint_ratio`, `pair_codepoint_diff`, `pair_chunk_ratio` | exact identities / deterministic duplicates |
| `code_point_ratio`, `byte_density_ratio` | non-log duplicates of the log terms |

### 2.3 Ladder — exact physical columns, carried over unchanged

The machine-readable contract is `ssot_nb09/02_NB09_MODEL_MATRIX_CONTRACT_v001.json`, generated
from the audited G5 contract artifact rather than retyped.

**M0** — `pair_log_size` (derived, `0.5·(ln C_KO + ln C_EN)`) + `source_domain_cell` (categorical)
+ `translation_direction` (categorical). `p = 8`.

**M1 = M0 +** `log_code_point_ratio`, `log_byte_density_ratio`, `delta_whitespace_density`
(derived, KO−EN), `ko_latin_share`, `ko_digit_share`, `ko_punctuation_share`,
`ko_symbol_other_share`, `en_hangul_share`, `en_digit_share`, `en_punctuation_share`,
`en_symbol_other_share`, `ko_script_type_count`, `ko_script_switch_count`,
`en_script_type_count`, `en_script_switch_count`. `p = 23`.

**M2 = M1 +** `morpheme_density`, `particle_ratio`, `ending_ratio`, `deriv_affix_ratio`. `p = 27`.

**M2A = M1 +** `morpheme_density`, `function_morpheme_ratio`, `deriv_affix_ratio`. `p = 26`.
M2 and M2A are **alternatives, never combined** — `function_morpheme_ratio` never coexists with
`particle_ratio` + `ending_ratio` (SSOT §12.3).

**M3 = M2 +** `ko_chunk_count_log`, `en_chunk_count_log` (derived, `ln k`),
`ko/en_mean_chunk_bytes`, `ko/en_p50_chunk_bytes`, `ko/en_p90_chunk_bytes`,
`ko/en_max_chunk_bytes`, `ko/en_max_tokens_per_chunk`, `ko/en_chunk_type_share_number`,
`ko/en_chunk_type_share_punctuation`, `ko/en_chunk_type_share_whitespace`. `p = 45`.

### 2.4 Reference coding — frozen, unchanged from G5

```
intercept                 included; reference level dropped for each categorical
source_domain_cell        reference = 025-…-other        (largest realized cell, 1,165,510)
translation_direction     reference = KO_TO_EN           (largest realized level, 2,512,152)
KO script composition     reference = ko_hangul_share    (definitional, native script)
EN script composition     reference = en_latin_share     (definitional, native script)
KO D-05 chunk type        reference = ko_chunk_type_share_letter   (definitional, base class)
EN D-05 chunk type        reference = en_chunk_type_share_letter   (definitional, base class)
```

No reference is re-selected in response to any diagnostic or any fit. `translation_direction =
UNKNOWN` is an explicit level, never a missing value; dropping or collapsing it is forbidden
(`RD-FAST-G5-01` §7).

### 2.5 `PRIMARY_COLUMN_SET_CHANGED = NO`

Verified mechanically, not asserted: every model's `continuous` list and `p_with_intercept` in
`02_NB09_MODEL_MATRIX_CONTRACT_v001.json` compares equal to the corresponding entry of the audited
`G5_REALIZED_MODEL_CONTRACT_v001.json` on `main`. `VD-NB09-OPERATIONALIZATION-01` forbids any post-hoc change to
the primary M1 or M3 span, and none was made.

Carried forward from G5, unchanged:

| model | p | rank | cond (std) | max VIF |
|---|---:|---:|---:|---:|
| M0 | 8 | 8 | 10.24 | 3.25 |
| M1 | 23 | 23 | 20.10 | 12.95 |
| M2 | 27 | 27 | 20.98 | 17.47 |
| M2A | 26 | 26 | 20.97 | 16.69 |
| M3 | 45 | 45 | 134.57 | 1,252.61 |

---

## 3. Estimator and standard errors

### 3.1 Estimator

Fixed-effects OLS on the full analysis cohort (`N = 3,835,988`), per SSOT §22 (explanatory /
hypothesis testing → mixed-effects or fixed-effects regression, role = coefficient + CI) and §23.1
(explanatory coefficient inference is performed on the **entire** analysis cohort).

**No random intercept on `source` is fitted as the primary specification.** SSOT §18.1/§18.2 write
`u_source[i]`; SSOT §20.1 directs a source fixed effect or a source-domain composite whenever source
levels are few or a source is nearly fully coupled with a domain. The realized cohort has **two**
sources, `other` is the only domain occurring under both, and G5 recorded
`SOURCE_DOMAIN_IDENTIFIABILITY = COMPOSITE_CELL_CONTROL_ONLY`.

The statement of record is:

> With only two realized source levels and strong source-domain coupling, a source random-intercept
> specification is insufficiently supported as the primary inferential specification; the approved
> realized model uses `source_domain_cell` fixed control under SSOT §20.1.

This is a support and identifiability judgement, **not** a claim that a two-level variance component
is mathematically impossible — no such proof is offered and none is relied on. SSOT §24 item 9
("source fixed vs random specification, *within the feasible range*") is answered by that judgement;
if the Director or an auditor wants the random specification demonstrated rather than judged, it
belongs in NB11 as candidate #9.

### 3.2 Standard errors — frozen

```
PRIMARY SE      HC1 heteroskedasticity-consistent  (White / Huber–Eicker, small-sample corrected)
COMPANION       pair-level multiplier (wild) bootstrap, Rademacher weights, B = 2000
                seeds FROZEN in ssot_nb09/03_NB09_SEED_REGISTRY_v001.json, not chosen at run time
                  NB09_GLOBAL            2703484264
                  NB09_COEF_BOOTSTRAP_A  1222524615
                  NB09_COEF_BOOTSTRAP_B  1018984010
REPORTED AS     SE type "HC1" in every regression table (SSOT §29 mandatory field)
```

Rationale, stated so it can be audited rather than trusted:

- Heteroskedasticity is expected on this outcome — the dispersion of `logTP` varies systematically
  with pair length, since the outcome is a ratio of integer token counts and short pairs sit on a
  coarser lattice. Classical OLS SEs are therefore not defensible as primary.
- HC1 is computable **exactly** at `N = 3.8M` from the Gram matrix plus one streaming accumulation
  of `Xᵀ diag(e²) X`; no subsampling and no approximation is involved.
- SSOT §23.1 requires bootstrap alongside model diagnostics for explanatory inference. The
  multiplier bootstrap is used rather than a row-resampling bootstrap because it streams: each row
  receives an independent weight, so no resampling index over 3.8M rows is materialized, and the
  same single pass yields the bootstrap distribution of both the coefficient vector and the
  block-comparison metrics of §5.

**The multiplier bootstrap does not correct duplicate-cluster dependence.** It resamples weights at
the pair level, so it addresses estimator variability under heteroskedasticity — not dependence
between paraphrase or near-duplicate pairs. Recorded explicitly so the companion procedure is not
over-read:

```
PAIR_LEVEL_MULTIPLIER_BOOTSTRAP  !=  DUPLICATE_CLUSTER_DEPENDENCE_CORRECTION
```

Duplicate / paraphrase dependence remains simultaneously a stated NB09 **limitation**, an **NB11
sensitivity candidate** (#12), and a **PRE-NB10 grouping prerequisite** for prediction.

`B = 2000` and the seeds in §3.3 are frozen here and are **not** altered after seeing any result.

**Cluster-robust SE is NOT used as primary, and the reason is recorded rather than glossed.**
Clustering on `source_id` gives 2 clusters and on `source_domain_cell` gives 5. Cluster-robust
asymptotics require many clusters; at 2 and 5 the resulting intervals are badly biased and would be
falsely reassuring. This is the same condition SSOT §17.2 already invoked when it made source
cluster bootstrap conditional on "source level 수가 충분할 때", and which the RQ1 closeout applied
when it recorded `cluster_bootstrap: NOT_PERFORMED`.

**Residual dependence is a declared limitation of NB09, not a solved problem.** Paraphrase and
near-duplicate clusters induce dependence between pairs; `LR-01` observed 25,247 upstream
`TRAIN↔VALID` exact shared pairs, and D-01 carries `duplicate_group_id` /
`analysis_representative_pair_id`. Whether those fields define the right dependence unit, and
whether they yield enough clusters, is a **PRE-NB10** question under
`CR-FAST-G5-SPLIT-RELOCATION-01`. NB09 must **not** invent a leakage grouping to manufacture a
cluster-robust SE. Duplicate-cluster-robust SE is listed as an NB11 sensitivity candidate (§9) and
every NB09 table carries the limitation sentence in §6.4.

### 3.3 Seeds and determinism (SSOT §30.3)

Seeds are frozen here, before execution, rather than "derived at run time". The derivation rule is
`seed = uint32 big-endian of the first 4 bytes of sha256(seed_source_string)`, and it is not
asserted — it is verified by reproducing the RQ1 precedent exactly:
`sha256("NB08_RQ1_SSOT_CLOSEOUT_v001|SOURCE_STRATIFIED")` → `aa49bab8…` → `2856958648`, the value
frozen in `ssot_nb01/06_NB08_RQ1_SSOT_CLOSEOUT_v001.json`.

```
determinism_status
  estimation            DETERMINISTIC     closed-form OLS from an exact Gram; no RNG in any estimate
  HC1 standard errors   DETERMINISTIC     closed form, no RNG
  multiplier bootstrap  SEEDED_DETERMINISTIC   numpy PCG64, seeds above

split seed              N/A — relocated to PRE-NB10 (CR-FAST-G5-SPLIT-RELOCATION-01)
model tuning seed       N/A — fixed-effects OLS has no tuning
serving generation seed N/A — Track B / NB12 on HOLD
```

**Row-order dependency, stated rather than assumed.** The multiplier bootstrap consumes weights in
physical row order, so reproduction requires the same `ORDER BY pair_id` ordering used at G5. The
run must **assert** that ordering, not assume it; a mismatch makes the bootstrap non-reproducible
and is a `HARD STOP`.

### 3.4 Precision at this sample size

At `N ≈ 3.8M`, interval width is small for every specification and the choice among HC variants
changes little. SSOT §17.3 and §29 therefore govern reporting: **effect size and CI first,
p-values never reported alone, and never used to rank features.** A narrow interval is a statement
about sampling precision on this cohort under this design — not about generalization to other
tokenizers, other corpora or other languages.

---

## 4. Missingness, weighting, and cohort handling

```
missingness        NONE — G5 measured 0 nulls, 0 non-finite, 0 non-positive log arguments
                   across all 39 predictors, both outcomes and all categorical fields
imputation         FORBIDDEN — a null appearing at NB09 is a HARD STOP, not an imputation trigger
weights            NONE — unweighted; the cohort is the population of accepted pairs
row deletion       FORBIDDEN — no post-hoc, result-dependent exclusion
cohort             ANALYSIS_COHORT_v001 · N = 3,835,988 · pair-set d9660d654ee449e4d0c23a0070225274
```

Artifact identity (D-01 `95f523d1…`, D-02 `dfae8e01…`, D-03 `0fe5bd74…`, D-04 `1c30e327…`,
D-05 `bfa98bd6…`) must be re-verified fail-closed at the head of the NB09 run. A mismatch is a
`HARD STOP`; no analysis proceeds on an unrecognized artifact.

---

## 5. Model comparison metrics — frozen

Director R0: primary evidence is **incremental / partial R², model-level improvement, and model
stability** — not a ranking of individual coefficient p-values.

| metric | definition | role |
|---|---|---|
| `ΔR²` | `R²_full − R²_reduced` | **primary** for every block comparison |
| partial `R²` | `(R²_full − R²_reduced) / (1 − R²_reduced)` | **primary** — the share of otherwise-unexplained variance the block accounts for |
| adjusted `R²` | per model | reported for every model (SSOT §19.2, fixed OLS variants) |
| AIC · BIC | per model | reported (SSOT §19.2) |
| likelihood-ratio test | nested pairs **only** | reported **with** the caveat in §5.1 |
| `ΔR²` bootstrap interval | from the §3.2 multiplier bootstrap | **model stability** evidence |
| coefficient-vector stability | bootstrap dispersion of the block's coefficients | **model stability** evidence |

Not computed at NB09:

```
out-of-sample MAE / RMSE / R²      → NB10, after PRE-NB10 (split relocated by CR-FAST-G5-SPLIT-RELOCATION-01)
marginal / conditional R²          → not applicable: no random-effects model is fitted (§3.1)
SHAP · permutation importance      → predictive attribution only (SSOT §22); not an explanatory result
```

### 5.1 Mandatory caveat on nested tests

At `N ≈ 3.8M` nested tests may have very high power and can reject practically negligible
increments. Statistical significance therefore **never overrides `ΔR²` / partial `R²` effect
magnitude**. A nested test statistic is reported beside the effect magnitudes, never as the finding,
and a block whose partial `R²` is negligible is described as negligible whatever its test statistic
says (SSOT §17.3, §29).

Individual coefficient p-values are **secondary inferential detail**. They may be reported alongside
the coefficient and its 95% CI, and they may **never** be used to rank predictors or to decide what
enters, stays in or leaves a model.

### 5.2 The three comparisons

```
RQ3   M1 − M0     representation / surface block
RQ4   M2 − M1     morphology block          ← primary morphology question (SSOT §19.2)
RQ5   M3 − M2     regex-chunk mechanism block
```

Each is computed for **both** Outcome A and Outcome B and reported separately per `IR-02`.

`M2A − M1` is reported as the pre-specified morphology **specification sensitivity** (SSOT §24
item 7), never as a competing primary answer to RQ4.

---

## 6. Coefficient reporting restrictions

### 6.1 Mandatory table fields (SSOT §29)

Every regression table records, without exception:

```
N pairs · source count · domain count · estimator · SE type ·
random/fixed effects specification · reference levels · missingness handling ·
R² or likelihood metric · preprocessing/version ID ·
execution_code_commit and artifact_record_commit (§30.2, C012)
```

### 6.2 Multiplicity (SSOT §29, §24)

```
primary RQ1                     one primary test + CI · NO FDR (already closed at NB08)
morphology block                block-level test FIRST
individual morphology coefficients   95% CI + Benjamini-Hochberg FDR q-value
                                     family = the morphology block's coefficients
domain interaction family       separate FDR family — none is fitted at NB09 (§7.4)
post-hoc extreme-case exploration    reported separately from confirmatory results
```

### 6.3 Terms whose individual coefficients may not carry a substantive claim

| terms | restriction | basis |
|---|---|---|
| `ko/en_script_type_count`, `ko/en_script_switch_count` | **no `INDEPENDENT_SUBSTANTIVE_EFFECT`.** Neither coefficient may be promoted to an independent substantive linguistic effect. Only the block-level contribution of the script-mixing construct is interpreted, and every table reporting these terms carries the flag `SCRIPT_MIXING_BLOCK_INTERNAL_REDUNDANCY = YES`. | `SM-01`; `VD-NB09-OPERATIONALIZATION-01` §8 |
| `ko_chunk_count_log`, `en_chunk_count_log` and the D-05 chunk-scale terms | **no substantive interpretation of raw chunk-count coefficients.** Every M3 table carries the coefficient-level instability warning of §6.5. | `M3-01`; `VD-NB09-OPERATIONALIZATION-01` §8 |
| `source_domain_cell` dummies | conditional contrasts between observed strata only; **no pure source effect, no pure domain effect** | `ID-03`; SSOT §20.1 final clause, §32 T-04 |
| `translation_direction` dummies | identified primarily from within-025 support; must be stated wherever a direction coefficient appears | `ID-04`; SSOT §32 T-03 |

### 6.4 Limitation sentence required on every NB09 table

> Standard errors are HC1 heteroskedasticity-consistent and do not account for dependence between
> paraphrase or near-duplicate pairs. Near-duplicate grouping is a PRE-NB10 prerequisite under
> `CR-FAST-G5-SPLIT-RELOCATION-01` and has not been applied here. Cluster-robust standard errors on
> `source_id` (2 levels) or `source_domain_cell` (5 levels) are not reported because the cluster
> count is far below what cluster-robust asymptotics require.

### 6.5 Coefficient-level instability warning required on every M3 table

> The M3 design is full rank (45/45) but carries a standardized condition number of 134.57 and a
> maximum VIF of 1,252.61, concentrated on `pair_log_size` and the chunk-scale terms. Individual
> coefficients within the D-05 block are correspondingly unstable and are not interpreted. RQ5 is
> reported as the `M3 − M2` block comparison.

Every M3 result table, report and manifest additionally carries these three fields verbatim:

```
M3_INTERNAL_COLLINEARITY_REVIEW                          = YES
RAW_CHUNK_COUNT_COEFFICIENT_SUBSTANTIVE_INTERPRETATION   = PROHIBITED
RQ5_PRIMARY                                              = BLOCK_LEVEL_M3_MINUS_M2
```

---

## 7. Claim boundaries

### 7.1 RQ3 — `M1 − M0`

**Permitted**: that the approved representation / surface block accounts for a stated share of
variance in `Y_A` (and separately in `Y_B`) beyond `M0`, on this cohort, under the frozen
`o200k_base` Track A configuration.

**Forbidden**: that any individual surface feature has an independent effect; that script mixing
"causes" premium; any causal language; generalization to other tokenizers, corpora or languages.

### 7.2 RQ4 — `M2 − M1`

**Permitted**: that the morphology block provides a stated incremental explanatory contribution
**after** surface, stratum and direction are controlled — a **conditional association**, per
`RD-SSOT-CANONICAL-RETURN-01` §15.

**Forbidden**: that morphology **causes** the token premium; that raw morphology correlation equals
conditional incremental value; that predictive importance equals causal effect; that a negligible
`ΔR²` is meaningful because an LR test rejected.

Note that `SM-01` sits entirely inside M1 and therefore appears on **both** sides of `M2 − M1`. It
does not affect the RQ4 comparison.

### 7.3 RQ5 — `M3 − M2`

**Permitted**: that the D-05 regex-chunk mechanism block accounts for a stated additional share, as
a **mechanism audit** (SSOT §19.3).

**Forbidden**: reading M3 as a stricter causal adjustment, as a morphology-effect purifier, or as a
predictive win. SSOT §19.3 states a high R² for M3 is *expected* because chunk features sit close to
the outcome's generative process, and it therefore earns no scientific credit. Individual chunk
coefficients carry no claim (§6.3).

### 7.4 Not fitted at NB09

```
cell × direction interaction        NOT ESTIMABLE (3 of 15 combinations empty) — not introduced
any domain interaction family       not fitted; if ever fitted it is a separate FDR family (§6.2)
domain + source_id additive         requires its own identifiability check; NOT run, NOT proposed
random intercept on source          not the primary specification; insufficiently supported
                                    at 2 source levels (§3.1) — NB11 candidate #9
```

### 7.5 Globally forbidden claims (VD-BASELINE-20260818-1520 §11)

Binding on every NB09 output regardless of what any comparison shows:

```
FORBIDDEN
  causal morphology effect
  inherent Korean AI inefficiency
  "UTF-8 is 3 bytes therefore 3x tokens"
  token premium implies reasoning degradation
  pure source effect · pure domain effect
  predictive importance treated as causal effect
  generalization beyond o200k_base, this cohort, Track A raw text

ALLOWED
  the observed tokenization premium under o200k_base
  its decomposition into representation and compression components
  conditional associations
  block-level explanatory value
  descriptive heterogeneity
```

The byte-count claim deserves its own line because the exact decomposition already refutes it:
`logTP = logCR + logBDR + logCP`, so byte density is **one** of three multiplicative components and
never the whole premium. Any sentence that maps a byte ratio directly onto a token ratio contradicts
an identity this project has verified to 8.9e-16.

### 7.6 The three boundaries

`RD-SSOT-CANONICAL-RETURN-01` §9 and SSOT §5.1 remain binding throughout:

```
linguistic morphology  ≠  o200k_base regex chunking  ≠  final subword tokenization
```

D-04 remains the sole authority for token counts and TP. M3 is not a second tokenizer outcome
factory.

---

## 8. `VD-NB09-OPERATIONALIZATION-01` — operational dispositions of record

```
Decision ID     VD-NB09-OPERATIONALIZATION-01
Classification  SSOT_CONFORMANT_OPERATIONALIZATION
                NO_SSOT_CHANGE · NO_ESTIMAND_CHANGE · NO_PRIMARY_COLUMN_CHANGE · NO_DATA_CHANGE
                NOT_A_DIRECTOR_DECISION
```

These are Vice-Director operational interpretations that conform to the SSOT and to the already
approved `RD-FAST-G5-01` / `CR-FAST-G5-*` / `RD-SSOT-CANONICAL-RETURN-01` records. **They are not a
Research Director decision and must never be relabelled `RD-*` without explicit user approval**
(`VD-BASELINE-20260818-1520` §6). They are binding on this protocol as operational instructions.

```
R0     APPROVE_BLOCK_LEVEL_PRIMARY_INTERPRETATION
       RQ3 = M1 − M0 · RQ4 = M2 − M1 · RQ5 = M3 − M2
       primary evidence = incremental/partial R², model-level improvement, model stability
       NOT a ranking of individual coefficient p-values

SM-01  PRIMARY MODEL: current frozen M1 block retained.
       script_type_count and script_switch_count are NOT deleted from the primary model on the
       basis of a post-G5 observation.
       Individual coefficients: INDEPENDENT_SUBSTANTIVE_EFFECT interpretation FORBIDDEN.
       Block-level contribution of the construct only.
       Alternative parameterization → NB11 robustness candidate.

M3-01  PRIMARY MODEL: current frozen M3 block retained.
       High VIF / condition number stated explicitly as a coefficient-level instability warning.
       RQ5 primary = M3 − M2 nested block comparison.
       Raw chunk-count individual coefficients: substantive interpretation FORBIDDEN.
       Chunk-density reparameterization → NB11 robustness / sensitivity candidate.
       The primary M3 span is NOT changed post hoc.

ID-03  source_domain_cell = OBSERVED_STRATUM CONTROL.
       Pure source effect FORBIDDEN. Pure domain effect FORBIDDEN.
       025-other vs 026-other is named ONLY as a same-domain source-stratum contrast.

ID-04  translation_direction identified primarily from within-025 support.
       026 contains no EN_TO_KO. UNKNOWN retained.
       Creation of unsupported interactions FORBIDDEN.

SPEC-01 / SPEC-02   carried forward as NB09 interpretation limitations.

EDA    NB07 results are descriptive corroboration and explanation ONLY.
       Using an EDA result as a predictor-selection criterion is FORBIDDEN.
```

### 8.1 Consequence for sequencing

Because the primary column set is fixed and EDA may not inform selection, **NB09 does not wait for
NB07 to complete.** NB07 supplies descriptive corroboration for the interpretation sections; it
supplies no input to the design matrix.

### 8.2 Carried finding from the G5 independent audit

The independent audit (`9d99e13`) established, beyond its brief, that
`chunk_count × mean_chunk_bytes = utf8_bytes` to 1.14e-13. On the log scale
`ln k + ln(mean_chunk_bytes) = ln B`, and `ln B` is already spanned by M1's
`pair_log_size` + `log_code_point_ratio` + `log_byte_density_ratio`. M3 remains full rank only
because `mean_chunk_bytes` enters on its native scale — near-exact, but not linear.

Binding consequence for §9: any NB11 chunk reparameterization that moves `mean_chunk_bytes` to the
log scale **while retaining `ko/en_chunk_count_log`** would create an exact identity and a rank
deficiency. Such a candidate must be rank-checked before it is fitted, exactly as G5 checked the
primary ladder. This is recorded now so it is not discovered during NB11 execution.

---

## 9. NB11 sensitivity candidates — registered, not scheduled here

Mapped to SSOT §24's required list plus the two reparameterizations deferred by the Director.

| # | candidate | source |
|---|---|---|
| 1 | raw text vs analysis-normalized text | SSOT §24.1 |
| 2 | NFC-only vs primary analysis text | SSOT §24.2 |
| 3 | full accepted cohort vs curated-source-only cohort | SSOT §24.3 |
| 4 | anomaly flag included vs excluded | SSOT §24.4 |
| 5 | extreme length strata excluded | SSOT §24.5 |
| 6 | known-direction-only subset (`N = 3,785,441`) | SSOT §24.6; RQ1 precedent |
| 7 | morphology primary block vs alternative function-morpheme block (`M2` vs `M2A`) | SSOT §24.7 — already in the ladder |
| 8 | OLS vs Huber vs quantile regression | SSOT §24.8; SSOT §22 |
| 9 | source fixed vs random — **feasible range is fixed only** (2 levels) | SSOT §24.9; §20.1 |
| 10 | `SM-01` alternative parameterization: `1{script_type_count ≥ 2}` + `script_switch_count`, or a single representative | `VD-NB09-OPERATIONALIZATION-01` §8 |
| 11 | `M3-01` chunk-density reparameterization — **rank-check first per §8.2** | `VD-NB09-OPERATIONALIZATION-01` §8 |
| 12 | duplicate-cluster-robust SE, once PRE-NB10 fixes the grouping | §3.2 declared limitation |
| 13 | `SPEC-01` held-out D-02 variables as a sensitivity block | `SPEC-01` |

Multiple-comparison handling for NB11: Benjamini–Hochberg FDR on secondary feature-level and
interaction-level hypothesis families; no FDR on the single primary RQ1 (SSOT §24, §29).

---

## 10. Prohibitions binding on NB09 execution

```
no outcome-driven feature selection — no predictor is added, dropped, kept or reparameterized
  on the basis of any relationship to Y_A or Y_B
no EDA-driven feature selection — NB07 output is corroboration, never a criterion
no reference level re-selected in response to a fit
no post-hoc row deletion, no imputation, no weighting
no D-02/D-03/D-04/D-05 regeneration
no causal language
no p-value-only reporting; no feature ranked by p-value
no individual coefficient claim for the terms listed in §6.3
no interaction that G5 found unsupported
the primary column set is not changed — any change is a protocol amendment with its own
  pre-result commit, re-measured rank/condition/VIF, and a fresh independent audit
```

An amendment cannot be adopted and fitted in one step.

---

## 11. Execution preconditions for NB09

Before the first fit:

1. artifact identity re-verified fail-closed, 5/5;
2. cohort re-verified: `N`, distinct `pair_id`, pair-set hash, zero missingness;
3. rank re-confirmed for each model actually fitted;
4. this protocol committed and pushed **before** any coefficient exists;
5. `ENG-OBS-001` telemetry on any stage exceeding 30 seconds — 10-second periodic samples carrying
   timestamp, stage, elapsed, rows processed when known, rate, RSS, `MemAvailable`, swap state and
   status, with no fabricated percentage or ETA. Percentage is emitted only when the denominator is
   genuinely known, and **one heavy WSL population job runs at a time**
   (`VD-BASELINE-20260818-1520` §10).

### 11.1 Audit-subject immutability

At handoff the protocol SHA becomes the immutable `AUDIT_SUBJECT_SHA`. The auditor audits that SHA,
not the moving branch name. Once the audit has started, this executor appends no further work to
this branch; any new task opens a new branch (`VD-BASELINE-20260818-1520` §8). The corrections
recorded in §0.2 were made **before** handoff, which is the only window in which they were
permitted.

**Engineering debt carried in, addressed to Claude-A** — `A-02` from the G5 audit:
`scripts/g5_diagnostics_v001.py` advances the Spearman-stage telemetry counter by
`n_rows // len(FAMILIES)` per family, so `3,835,988 // 11 × 11 = 3,835,986` and the manifest records
a two-row shortfall. The defect is in the counter arithmetic only — no correlation and no cohort
figure is affected, and the independent audit reproduced every correlation over the full
3,835,988-row join. It must be corrected before the next heavy run so the counter is not mistaken
for cohort loss. `A-01` (the raw-coding condition number is computed without the intercept column,
a non-trigger quantity) requires only that the convention be stated wherever that figure is quoted.

---

**Frozen**: 2026-08-18 14:46 KST, Claude-B. No model fitted. Not merged to `main`.
**Next**: Claude-A independent protocol audit, then Director authorization to execute NB09.
