# RQ1 First Paper-Ready Result — Director Decision Log

> **Decision ID**: `RD-RQ1-FIRST-RESULT-01`
> **Status**: `APPROVED / EXECUTION AUTHORIZED`
> **Snapshot**: 2026-08-17 KST
> **Lane**: `research/nb08-rq1-primary-20260817` (Claude-B, RQ1 Primary Inference Steward)

**Parent authorities**

```
KOEN-TP-RS-001                    (SSOT)
RD-FAST-G5-01                     (Fast-Track Analysis Entry Decision)
FINAL_MAIN_SHA = 79490b723ff4413763a84d310e50fa2748ccca6c
```

**Scope note on `ssot_nb01/`.** This directory is **not** canonical notebook 01. It is the
branch-scoped `RQ1_FIRST_RESULT_EXECUTION_SSOT` for this lane only. Canonical notebook numbering is
unchanged; the inference notebook is `notebooks/08_primary_inference.ipynb`.

---

## 4.1 Purpose

The purpose of this lane is **not** to complete the research programme. It is to produce

> the first primary statistical result that can be cited directly in the paper.

Everything not required for that result is deliberately out of scope.

## 4.2 Primary cohort

The final validated pair universe is used as-is.

```
Expected N      = 3,835,988
pair-set hash   = d9660d654ee449e4d0c23a0070225274
```

**Primary exclusions: NONE beyond the already-frozen final cohort.**

Explicitly **not** excluded from the primary analysis:

- `translation_direction = "UNKNOWN"`
- `eojeol_count = 1`
- short text
- TP extremes
- morphology extremes

Excluding any of these from the primary would be an outcome-adjacent cohort choice. The primary
cohort is the frozen G1/G2/G3/G4 cohort and nothing else.

## 4.3 Outcome

```
Primary outcome      : log_token_premium               (D-04 column, Track A)
Secondary transform  : exp( Median(logTP) )
```

`exp(Median(logTP))` may be reported on a `Median(TP)` scale. It **must not** be conflated with the
aggregate total-token ratio `Σ T_KO / Σ T_EN`, which is a different quantity.

## 4.4 Hypothesis

```
Estimand   theta = Median(log_token_premium)

H0 : theta = 0
H1 : theta > 0
```

## 4.5 SSOT primary test

```
Primary test : one-sample Wilcoxon signed-rank
alternative  : greater
```

**Interpretation note (binding).** The Wilcoxon signed-rank test carries a distributional
symmetry / location-shift interpretation. Its rejection is therefore not, on its own, a statement
about the median under arbitrary asymmetry. For that reason a **one-sample sign test is reported
alongside it as a robustness check on the median estimand. The sign test is not optional.**

## 4.6 Zero / tie policy — frozen before execution

```
Wilcoxon   zero_method = "wilcox"
           exact zero differences are dropped from the signed-rank computation

Sign test  logTP > 0  -> positive
           logTP < 0  -> negative
           logTP = 0  -> tie
           ties are excluded from the effective binomial denominator
```

The total tie count and tie share **must** be reported separately in both cases.

**This policy may not be changed after execution.**

## 4.7 Bootstrap

```
Primary uncertainty : 95% percentile bootstrap CI for Median(logTP)
B (first release)   : 2,000
```

The broader plan specifies `B = 5,000`. The reduction is recorded as an explicit change request:

```
CR-RQ1-BOOTSTRAP-FAST-2000-01
APPROVED BY DIRECTOR FOR FIRST RQ1 RELEASE
```

This change:

- does **not** change the statistic
- does **not** change the confidence level
- does **not** change the resampling unit

It reduces the first-release replicate count from 5,000 to 2,000 only. `B ≥ 5,000` may be re-run in
NB11 robustness work.

## 4.8 Bootstrap seed — frozen before any outcome is observed

The seed is derived deterministically from the Decision ID and protocol ID; it was **not** chosen by
hand.

```
seed = uint32( first_8_hex( SHA256( "RD-RQ1-FIRST-RESULT-01|NB08_RQ1_PROTOCOL_v001" ) ) )

SHA256      = 39cb7399372c9ede5fbbb0a9199e1e16d0f5a33ed7a93443e7f1a5a34dc53802
first_8_hex = 39cb7399
seed        = 969634713
```

**This seed may not be changed after execution.**

## 4.9 Bootstrap resampling unit

```
Primary : pair_id row-level iid bootstrap
```

Source-stratified bootstrap is **not** a hard prerequisite for this first-result release.

**Caveat carried into the result document**: source dependence and source imbalance may exist in
this cohort, and the row-level iid bootstrap does not account for them. Source-stratified and
dependence-sensitive robustness may be performed in a later NB08 appendix or in NB11.

## 4.10 Sensitivity

```
First sensitivity : known-direction only, translation_direction != "UNKNOWN"
Expected N        ≈ 3,785,441
```

This sensitivity **does not replace** the primary cohort; it is reported beside it.

`eojeol_count > 1` and similar filters are **not** required for this first result.

## 4.11 Claim boundary

Permitted final claim (exact wording to be written against the observed CI and test results):

> Under the fixed `o200k_base` raw-text Track A measurement and the defined final paired KO–EN
> cohort, statistical evidence was observed that the pair-level median log token premium is greater
> than zero.

**Prohibited**, regardless of the result:

- that Korean is intrinsically inefficient for AI
- generalization to all tokenizers
- that morphology is the cause
- any domain effect claim
- reasoning degradation
- that API cost increases by 33 % (or any fixed figure) unconditionally
- any causal language

## Out of scope for this lane

```
NB06 · regex chunking · D-05 · morphology explanatory model · M0/M1/M2/M3
VIF/GVIF · condition number · source_domain_cell modeling
near-duplicate clustering · train/test split · NB10 · G-ID · NB09
```

---

**Decision recorded before any outcome test was executed.**
No signed-rank, sign test, or bootstrap computation had been run at the time of this commit.
