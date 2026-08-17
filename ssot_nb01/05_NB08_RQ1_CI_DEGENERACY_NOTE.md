# NB08 RQ1 — Degenerate Bootstrap CI: Post-hoc Diagnostic Note

> **Status**: `POST-HOC DIAGNOSTIC` — **not** part of the frozen protocol `NB08_RQ1_PROTOCOL_v001`.
> **Changes nothing**: no estimand, test, CI method, seed, replicate count, cohort or reported value
> is altered by this note. It exists because the primary CI would be misleading if reported without
> the explanation below.

---

## 1. What was observed

```
median(logTP)          0.2876820725
95% percentile CI      [0.2876820725, 0.2876820725]
bootstrap replicate sd  5.553e-17
```

Both CI endpoints equal the point estimate to full double precision. Read naively this looks like
either a bug or an implausible claim of infinite precision. It is neither.

## 2. Why it happens

The outcome is `logTP = log(T_KO / T_EN)`, where `T_KO` and `T_EN` are **integer token counts**. A
ratio of small integers is heavily concentrated on a small set of exact values.

Measured over the full cohort:

```
distinct logTP values                3,725      over N = 3,835,988
median value                         0.28768207245178085  ==  ln(4/3)   (exact equality)
rows exactly at the median           123,040    (3.2075%)
rows strictly below the median       1,841,884  (48.0159%)
rows strictly above the median       1,871,064  (48.7766%)
```

`N` is even, so the sample median averages order statistics 1,917,994 and 1,917,995. Both fall
**inside** the 123,040-row point mass at `ln(4/3)`:

```
1,841,884  <  1,917,994  and  1,917,995  <=  1,841,884 + 123,040 = 1,964,924
```

The margin on either side is roughly 76,000 observations. A bootstrap resample would have to shift
the middle order statistic out of a point mass that is ~3.2 % of the sample — a deviation of about
`76,000 / sqrt(3,835,988) ≈ 39` standard errors of the relevant count. Across 2,000 replicates this
never occurred, so every replicate median is exactly `ln(4/3)` and the percentile interval collapses
to a point.

The most frequent outcome values confirm the discreteness:

| `logTP` | `TP` | rows | share |
|---:|---:|---:|---:|
| 0.0000000000 | 1.000000 | 196,718 | 5.128 % |
| 0.4054651081 | 1.500000 | 147,699 | 3.850 % |
| **0.2876820725** | **1.333333** | **123,040** | **3.208 %** |
| 0.2231435513 | 1.250000 | 91,499 | 2.385 % |
| 0.3364722366 | 1.400000 | 68,013 | 1.773 % |
| 0.1823215568 | 1.200000 | 67,478 | 1.759 % |
| 0.5108256238 | 1.666667 | 63,954 | 1.667 % |
| 0.6931471806 | 2.000000 | 55,306 | 1.442 % |

## 3. What this does and does not mean

**Does mean.** At this sample size the *sampling* uncertainty of the median, as captured by a
pair-level iid percentile bootstrap, is smaller than the spacing between adjacent attainable values
of the outcome. The interval is degenerate because the estimator is pinned to a lattice point, not
because the estimate is infinitely precise.

**Does not mean.**

- It does **not** mean the median is known to ~1e-16. The *resolution* of the estimator is the gap
  between neighbouring attainable values, which is far coarser than the reported digits.
- It does **not** license reporting `95% CI = [0.2877, 0.2877]` without this caveat. Doing so would
  imply a precision the design does not support.
- It does **not** validate the row-level iid resampling assumption. Source dependence and source
  imbalance remain unaddressed (`RD-RQ1-FIRST-RESULT-01` §4.9); a dependence-aware bootstrap could
  widen the interval and is deferred to an NB08 appendix or NB11.
- It is **not** evidence about `H1`. The directional evidence comes from the Wilcoxon signed-rank
  and sign tests, both of which are reported separately and neither of which depends on the CI.

## 4. Recommended reporting form

Report the CI **with** the degeneracy stated, for example:

> median log token premium 0.2877 (= ln 4/3); 95 % percentile bootstrap CI degenerate at the same
> value (B = 2,000, pair-level iid), because the median lies on a 123,040-row point mass in a
> discrete outcome taking only 3,725 distinct values.

Do **not** report a bare `[0.2877, 0.2877]`.

## 5. Recommended follow-up (not required for this release)

For a non-degenerate interval, later work may use a method that respects the lattice, for example an
exact order-statistic (Clopper–Pearson style) interval for the population median, or a
dependence-aware / source-stratified bootstrap. Both are out of scope for this first-result lane and
neither changes anything reported here.

---

**Recorded**: 2026-08-17 KST, Claude-B (RQ1 Primary Inference Steward).
**Frozen protocol unaffected**: `NB08_RQ1_PROTOCOL_v001` §1–§8 unchanged.
