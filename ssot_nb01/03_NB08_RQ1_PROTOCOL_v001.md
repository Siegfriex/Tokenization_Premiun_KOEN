# NB08 — RQ1 Primary Inference Protocol v001

> **Protocol ID**: `NB08_RQ1_PROTOCOL_v001`
> **Decision ID**: `RD-RQ1-FIRST-RESULT-01`
> **Base main**: `79490b723ff4413763a84d310e50fa2748ccca6c`
> **Decision commit**: `e72274086a7e9c611c9014e6b5612df0e69dae30`
> **Cohort commit**: `9b695307c0551be84d4d6c374646bfe001b7b3a9`
> **Notebook**: `notebooks/08_primary_inference.ipynb`

**Frozen before any result was observed.** At the time of this commit no Wilcoxon statistic, no sign
test, no bootstrap replicate and no median of the outcome had been computed. The only outcome-column
quantities computed so far are the null and non-finite counts required by the cohort manifest.

---

## 1. Outcome and estimand

```
Y        = log_token_premium            (D-04, o200k_base raw-text Track A)
Estimand theta = Median(Y)
H0       theta = 0
H1       theta > 0            (one-sided, greater)
```

## 2. Primary test

```
one-sample Wilcoxon signed-rank
alternative = "greater"
zero_method = "wilcox"        exact zero differences dropped from the signed-rank computation
```

Reported: `W` statistic, one-sided p-value, number of zero differences dropped.

The signed-rank test carries a symmetry / location-shift interpretation and is therefore not, by
itself, a distribution-free statement about the median. §3 is mandatory for that reason.

## 3. Robustness test — mandatory

```
one-sample sign test (exact binomial, alternative = "greater")
positive : Y > 0
negative : Y < 0
tie      : Y = 0
ties are excluded from the effective binomial denominator
```

Reported: positive count, negative count, tie count, tie share, effective `n = pos + neg`,
one-sided p-value. The sign test is **not** optional and is **not** subordinate to §2.

## 4. Point estimate and transform

```
point estimate    median(Y)
transformed       exp( median(Y) )
```

`exp(median(Y))` is reported on a `Median(TP)` scale. It is **not** the aggregate token ratio
`Σ T_KO / Σ T_EN` and must not be presented as such.

## 5. Primary confidence interval

```
method          95% percentile bootstrap CI for Median(Y)
resampling unit pair_id row-level iid
B               2000                     (CR-RQ1-BOOTSTRAP-FAST-2000-01)
seed            969634713
quantiles       0.025, 0.975
```

Seed derivation, recorded for reproduction:

```
source string = "RD-RQ1-FIRST-RESULT-01|NB08_RQ1_PROTOCOL_v001"
SHA256        = 39cb7399372c9ede5fbbb0a9199e1e16d0f5a33ed7a93443e7f1a5a34dc53802
first_8_hex   = 39cb7399
uint32        = 969634713
```

A bootstrap **equivalence benchmark** is executed: the vectorised implementation used for the full
run is checked against a straightforward reference implementation on a reduced replicate count with
the same seed. Both must produce identical replicate medians. A non-zero mismatch invalidates the
CI regardless of runtime.

## 6. Sensitivity

```
KNOWN_DIRECTION_ONLY : translation_direction != "UNKNOWN"
```

Same estimand, same tests, same bootstrap settings and same seed. This is reported **beside** the
primary result and does not replace it.

## 7. Non-finite policy

```
HARD FAIL if any non-finite Y is observed at analysis time.
No post-hoc deletion is permitted.
```

## 8. p-value reporting policy

`p = 0` is **never** reported. On floating-point underflow the protocol reports either

- `p < <numerical reporting threshold>`, or
- a computable `log10(p)`

whichever is available, with the underflow stated explicitly.

## 9. Software identity

```
python   3.12.3
numpy    2.5.2
scipy    1.18.0
pyarrow  24.0.0
duckdb   1.5.5
tiktoken 0.13.0     (identity only; no re-tokenization is performed in NB08)
```

## 10. Notebook cell protocol

```
01  Canonical D-04 fail-closed validation      (SHA, schema, N, pair-set hash)
02  RQ1 cohort manifest validation             (re-assert 02_ANALYSIS_COHORT_RQ1_v001.json)
03  Descriptive outcome snapshot
04  Wilcoxon signed-rank
05  Sign test
06  Bootstrap equivalence benchmark
07  Full primary bootstrap CI
08  Known-direction sensitivity
09  Primary results table
10  Claim boundary / interpretation
```

## 11. Source discipline

Every number is computed independently from the **D-04 physical artifact**. No value is copied from
EDA V1 or EDA V2. **EDA V2 is not an inference source.**

## 12. Immutability

Sections 1–8 are frozen at this commit. No protocol element may be modified after any result is
observed. Any deviation discovered during execution must be reported as a protocol violation rather
than silently accommodated.
