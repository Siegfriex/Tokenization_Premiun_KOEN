# RQ1 — Manuscript-ready text

Drop-in English text for the paper. Every number is copied from
`ssot_nb01/04_NB08_RQ1_RESULTS_v001.json` and `ssot_nb01/06_NB08_RQ1_SSOT_CLOSEOUT_v001.json`.
Nothing here is re-estimated.

---

## Results paragraph

> Across 3,835,988 semantically matched Korean–English sentence pairs tokenized with a frozen
> `o200k_base` encoder (tiktoken 0.13.0, raw text, no chat template and no special tokens), the
> median pair-level tokenization premium was 4/3: the median of `log(T_KO/T_EN)` was 0.2877
> (= ln 4/3), corresponding to a median token-count ratio of 1.3333. The premium was not confined to
> the centre of the distribution — 87.99 % of pairs (3,375,095) required more Korean than English
> tokens, 5.13 % (196,718) required exactly the same number, and 6.89 % (264,175) required fewer. A
> one-sample Wilcoxon signed-rank test rejected the null of a zero median in the positive direction
> (p < 1e-300). The direction was unchanged under a conservative tie-aware sign test that retains all
> ties in the denominator (P(Y > 0) = 0.8799), under restriction to pairs with a known translation
> direction (N = 3,785,441; median unchanged to all reported digits), and under a source-stratified
> bootstrap that holds the source composition fixed. The 95 % percentile bootstrap interval for the
> median was degenerate at ln(4/3); this reflects the discreteness of a ratio of integer token counts
> — only 3,725 distinct values occur, and 123,040 pairs (3.21 %) sit exactly at the median — rather
> than infinite precision. An exact order-statistic interval for the median is degenerate at the same
> value.

## Methods summary

> The primary outcome was `Y_i = log(T_KO,i / T_EN,i)`, the pair-level log tokenization premium,
> measured on the analysis text of each pair with a frozen `o200k_base` encoder whose encoding file,
> mergeable-rank table, regex pattern and special-token map were hash-pinned. The estimand was
> `Median(Y)`, tested one-sided as `H0: Median(Y) = 0` against `H1: Median(Y) > 0` using a one-sample
> Wilcoxon signed-rank test (`zero_method = "wilcox"`). A one-sample sign test was reported alongside
> it as a robustness check, in a conditional form that excludes exact ties and in a conservative
> tie-aware form whose denominator retains them. Uncertainty for the median was quantified by a 95 %
> percentile bootstrap resampling pairs independently (B = 2,000; seed 969634713 derived
> deterministically from the analysis-plan identifier), with a source-stratified bootstrap
> (B = 2,000; seed 2856958648) as a sensitivity analysis. The analysis decision, the cohort
> definition and the inference protocol were each committed to version control before any outcome was
> computed, and the executed notebook re-derives the bootstrap seed from its source string at run time.

## Table-ready values

| Quantity | Primary final cohort | Known direction only |
|---|---:|---:|
| N | 3,835,988 | 3,785,441 |
| Median `logTP` | 0.28768207245178085 | 0.28768207245178085 |
| Median `TP` scale | 1.3333333333333333 | 1.3333333333333333 |
| 95 % bootstrap CI | degenerate at ln(4/3) | degenerate at ln(4/3) |
| Wilcoxon signed-rank | p < 1e-300 | p < 1e-300 |
| Tie-aware sign, P(Y > 0) | 0.879850 | 0.879829 |
| P(TP > 1) | 87.9850 % | 87.9829 % |
| P(TP = 1) | 5.1282 % | — |
| P(TP < 1) | 6.8868 % | — |

Source-stratified bootstrap (SSOT §17.2): 95 % CI degenerate at ln(4/3); conclusion not reversed.
Source cluster bootstrap was not performed — only two source levels, below the sufficiency condition.

## Figure captions

**Figure NB08-RQ1-V01.** Distribution of the pair-level log tokenization premium over the final
cohort (N = 3,835,988), binned at 0.05. The dashed line marks parity (`logTP = 0`); the solid line
marks the median at ln(4/3). The lower panel shows the cumulative distribution at nine quantiles. The
outcome is a ratio of integer token counts and therefore discrete; no kernel smoothing is applied.

**Figure NB08-RQ1-V02.** Composition of pair polarity: the share of pairs for which the Korean side
required more, the same, or fewer tokenizer tokens than the English side. Counts and percentages are
both shown. This is a descriptive composition and is not itself the sign-test statistic.

**Figure NB08-RQ1-V03.** The eight most frequent exact values of the outcome, drawn as a stem plot
(upper), and the rank position of the median relative to its point mass (lower). The median lattice
point TP = 4/3 carries 123,040 observations (3.21 %). The 95 % order-statistic interval spans ranks
1,916,074–1,919,915, both of which fall inside the point mass at ranks 1,841,885–1,964,924. The
degenerate bootstrap interval reflects this large discrete point mass at the median, not infinite
measurement precision.

**Figure NB08-RQ1-V04.** Robustness and sensitivity summary for the primary cohort and the
known-direction subset. Both medians coincide at ln(4/3); the pair-level and source-stratified
bootstrap intervals are degenerate at that value and are shown as such rather than as an artificial
interval width. p-value magnitude is not visualized.

**Figure NB08-RQ1-S01 (supplementary).** Descriptive statistics by source stratum. These are
descriptive strata, **not** a source effect estimate: source and domain are not separately
identifiable in this cohort, so the difference between strata cannot be attributed to either.

## Limitation sentence

> These results are specific to the `o200k_base` tokenizer under raw-text Track A measurement and to
> the corpus from which this paired cohort was constructed; they do not generalize to other
> tokenizers, other corpora, or serving-time token accounting. The design is paired and
> observational, so no causal mechanism — morphological, orthographic, or domain-related — is
> established, and the reported median is a pair-level quantity that is not equal to the aggregate
> corpus token ratio. Because the outcome is a ratio of integer counts, the bootstrap interval for
> the median is degenerate at a lattice point; this indicates discreteness, not precision, and
> interval estimates on such an outcome should be reported with that caveat.

## Reporting conventions used

- p-values are reported as `p < 1e-300` where the exact value underflows double precision. The
  normal-approximation `log10(p)` recorded in the artifacts is a distance-from-null diagnostic, not
  an exact log p-value, and is not used as a headline number.
- "33.3 % premium" is always qualified as a **median pair-level** premium and never presented as an
  aggregate corpus token ratio.
- A degenerate confidence interval is reported as degenerate, never widened for presentation.
