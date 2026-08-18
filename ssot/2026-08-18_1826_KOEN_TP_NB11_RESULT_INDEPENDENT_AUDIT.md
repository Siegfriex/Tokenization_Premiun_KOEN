# KOEN — NB11 Robustness · Independent Result Audit

> Audit ID: `NB11_RESULT_INDEPENDENT_AUDIT_20260818`
> Class: **RESULT AUDIT** — eight declared targets, NB09 not re-audited.
>
> Auditor: Claude-A
>
> ```
> AUDIT_SUBJECT_SHA = fe5446d5806b7a8986baccb3a8c91025dbd1cc87
>                     research(nb11): execute pre-registered robustness matrix
> branch            = research/nb11-robustness-20260818
> parent            = 925697ccc06514f86ae48952ab42f18bae3fd70f  (canonical main)
> executed          = 2026-08-18 18:22–18:26 KST
> ```
>
> This is an `A-*` agent finding, not an `RD-*` decision.

The NB09 result audit (`27814139`), its supplement (`c12ca80`) and the block-CI correction
(`7bbe11a`) are all ancestors of this subject and are **not** revisited.

---

## 1. Subject and scope

One commit on canonical main: README, notebook, run manifest, robustness summary, sensitivity
matrix CSV, and a `.gitignore` allowlist line. Six subsets × seven variants × five models = 210
designs, 312 sensitivity rows.

```
subsets   FULL 3,835,988 · KNOWN_DIR 3,785,441 · NO_ANOMALY 3,728,608
          CENTRAL_LENGTH 2,387,120 · SOURCE_025 2,485,963 · SOURCE_026 1,350,025
variants  V0 · V1_SM01 · V2_M3DENS · V3_M3DENS_LOGMCB · V4_B_SSOT182 · V5_SRC_DOM · V6_SPEC01
```

---

## 2. Target 2–3 — the subset pruning rule is structural only — `PASS`

The rule, read verbatim from the notebook rather than from its description:

```python
def prune(sub, cols):
    G = ST[sub]["G"]; n_ = max(ST[sub]["n"], 1)
    for j in cols:
        if j == IDX["__intercept__"]: keep; continue
        gjj = G[j, j]; mean = G[IDX["__intercept__"], j] / n_
        ss = gjj - n_ * mean * mean                 # centred sum of squares
        if ss / max(gjj, 1.0) <= ZV_TOL: drop
        else: keep
```

It touches `ST[sub]["G"]` and nothing else. The Gram is accumulated as `ST[s]["G"] += Xs.T @ Xs` —
**design only**. The outcome lives in three separate keys, `Xty`, `yty` and `ysum`, and none of them
appears anywhere in `prune` or in `rank_of`. `fit_sub` calls `prune` **before** it first touches
`Xty`.

So the decision to drop a column is a function of that column's within-subset variance and of
nothing else. No coefficient, no p-value, no `R²`, no performance figure participates.

```
PRUNING_RULE = STRUCTURAL_SUPPORT_ONLY
OUTCOME_DRIVEN_PRUNING = NONE
zero-variance / unsupported columns removed across all 210 designs = 215
tolerance = 1e-12 on the ratio of centred to raw sum of squares
```

The same deterministic rule is applied to every subset, and every drop is logged per design in
`structural_pruning.per_design`.

---

## 3. Target 4 — identifiability of every effective design — `PASS`

```
designs                          210
full rank after pruning          175
not identifiable after pruning    35
records with inconsistent full_rank / deficiency fields   0
non-identifiability causes left UNCLASSIFIED               0
```

Cause breakdown, all pre-classified by the executor:

| cause | designs |
|---|---:|
| `REFERENCE_CELL_ABSENT_IN_SUBSET_DUMMIES_SATURATE_INTERCEPT` | 29 |
| `EXACT_IDENTITY_ln_k_PLUS_ln_mean_chunk_bytes_EQUALS_ln_bytes` | 5 |
| both causes together | 1 |

**No rank-deficient design was fitted.** `fit_sub` returns `None` whenever `rank != p`, and the
comparison loop emits a `NOT_IDENTIFIABLE_EXACT_IDENTITY` row instead of an estimate. All 54 blocked
CSV rows carry `rank_full < effective_p_full`, verified row by row.

The primary specification `V0` fails on exactly one subset, `SOURCE_026`, and the cause is
structural rather than empirical: the frozen reference cell is a **025** cell, so it is absent from a
source-026-only subset by construction, and the surviving cell dummies sum to one and saturate the
intercept. The executor did **not** repair this by re-referencing, which would have changed the
frozen coding rule mid-robustness-analysis. Stopping is the correct response and it is disclosed in
the README.

---

## 4. Target 5 — `V2_M3DENS` same-span claim — `PASS`, verified two ways

The claim is that replacing `ko/en_chunk_count_log` with `ko/en_chunk_density_log` is a change of
basis inside the same column space.

**Algebraically**, `chunk_density_log = ln k − ln C`, so `ln k = density + ln C`; and
`ln C_KO = pair_log_size + ½·logCR`, `ln C_EN = pair_log_size − ½·logCR`, both already in M1.

**Measured by this auditor over the full cohort**, not asserted:

```
ln C_KO − (pair_log_size + ½·logCR)                          max|err| 8.882e-16   EXACT
ln C_EN − (pair_log_size − ½·logCR)                          max|err| 8.882e-16   EXACT
ln k_KO − density_KO − pair_log_size − ½·logCR               max|err| 8.882e-16   EXACT
ln k_EN − density_EN − pair_log_size + ½·logCR               max|err| 8.951e-16   EXACT
```

**And by independent Gram recomputation of both M3 designs:**

| design | p | rank | condition (RMS, uncentred) | `R²` (Outcome A) |
|---|---:|---:|---:|---|
| V0 `chunk_count_log` | 45 | **45** | 1172.8096 | 0.806938598911 |
| V2 `chunk_density_log` | 45 | **45** | 653.3555 | 0.806938598911 |

```
|R²(V0) − R²(V2)| = 5.8e-14 … 2.3e-13 across repeated runs   (executor reported 1.19e-13)
condition numbers reproduce the executor's 1172.8096 and 653.3555 exactly
```

Same span, identical fit, better conditioning. `SAME_SPAN_REPARAMETERIZATION` is the right label and
`block_conclusion_changed: false` is correct.

---

## 5. Target 6 — `V3_M3DENS_LOGMCB` exact rank deficiency — `PASS`

This is the failure mode the G5 independent audit flagged in advance, in §8.2 of the PRE-NB09
protocol: moving `mean_chunk_bytes` to the log scale **while retaining** the chunk-count term creates
an exact identity. It materialised exactly as forecast.

Derivation, then measurement. Since `ln k + ln(mcb) = ln B` per side and
`density = ln k − ln C`:

```
(density_KO + ln mcb_KO) − (density_EN + ln mcb_EN)
   = (ln B_KO − ln C_KO) − (ln B_EN − ln C_EN)
   = ln(B_KO/B_EN) − logCR
   = logBDR
```

Measured over the full cohort by this auditor:

```
(density_KO + ln mcb_KO) − (density_EN + ln mcb_EN) − logBDR      max|err| 1.665e-15
ln k_KO + ln mcb_KO − ln B_KO                                      max|err| 8.882e-16
ln k_EN + ln mcb_EN − ln B_EN                                      max|err| 8.882e-16
```

**One** exact linear dependency, therefore a rank deficiency of **exactly one**. Independent Gram
recomputation:

```
V3 / M3 / FULL   p = 45   rank = 44   deficiency = 1      (executor reported 45 -> 44)
```

The executor stopped the sensitivity rather than repairing it by deleting a substantive variable
(`repaired_by_deletion: false`). That is the correct call: deleting a term to restore rank would have
turned a diagnostic into a different model chosen after seeing that it failed.

---

## 6. Target 7 — `V4_B_SSOT182` Outcome-B effect sizes — `PASS`

Recomputed independently **without a second data pass**, by exploiting `y_B = y_A − logCR − logBDR`:
both ratios are columns of the audit's own Gram, so `X'y_B`, `y_B'y_B` and `Σy_B` follow
algebraically from quantities already accumulated for Outcome A.

| comparison | executor | this audit | difference |
|---|---|---|---:|
| RQ4 `ΔR²` | 0.053425545893626 | 0.053425545893620 | 6e-15 |
| RQ4 partial `R²` | 0.083067388126373 | 0.083067388126364 | 9e-15 |
| RQ5 `ΔR²` | 0.298368125558966 | 0.298368125558981 | 1.5e-14 |
| RQ5 partial `R²` | 0.505937177396042 | 0.505937177396066 | 2.4e-14 |

Supporting fits: M1 `p=21 R²=0.356841`, M2 `p=25 R²=0.410266`, M3 `p=43 R²=0.708635`.

**Substantively this is the most consequential number in NB11.** Under the approved common ladder
Outcome B's morphology block carries partial `R²` 0.0188 — a figure that `B-N01` showed is
algebraically identical to Outcome A's. Removing the two representation ratios, as SSOT §18.2's own
illustrative form does, breaks that tie and the morphology block's incremental value for compression
asymmetry rises to **0.0831, roughly 4.4×**. The executor classified this
`OUTCOME_B_MORPHOLOGY = SPECIFICATION_SENSITIVE`, kept `promoted_to_primary: false`, and left
Outcome A untouched.

That handling is correct and the classification is not softened. It is a sensitivity that says the
common-ladder Outcome-B result understates morphology's role for compression asymmetry — a finding
about the specification, not a corrected primary model, and one that belongs in front of the
Director alongside `B-N01`.

---

## 7. Target 8 — RQ3 / RQ4 / RQ5 robustness ranges — `PASS`

All six ranges recomputed from the sensitivity CSV and compared to the claim register. Every one
matches, including the specification counts and the `all_positive` flags.

| claim | outcome | specs | `ΔR²` range | partial `R²` range | all positive |
|---|---|---:|---|---|---|
| RQ3 | A | 31 | 0.604706 – 0.711574 | 0.621022 – 0.733965 | yes |
| RQ3 | B | 31 | 0.326351 – 0.472463 | 0.399022 – 0.481725 | yes |
| RQ4 | A | 31 | 0.004990 – 0.007767 | 0.015893 – 0.023507 | yes |
| RQ4 | B | 31 | 0.006985 – 0.012285 | 0.015893 – 0.023507 | yes |
| RQ5 | A | 26 | 0.077425 – 0.179427 | 0.307417 – 0.496678 | yes |
| RQ5 | B | 26 | 0.152590 – 0.283776 | 0.307417 – 0.496678 | yes |

Ratios against the NB09 primary (Outcome A) and the resulting labels:

```
RQ3   [0.9738, 1.1459]   DIRECTION_STABLE  MAGNITUDE_STABLE
RQ4   [0.7572, 1.1786]   DIRECTION_STABLE  MAGNITUDE_STABLE
RQ5   [0.5135, 1.1901]   DIRECTION_STABLE  MAGNITUDE_ATTENUATED
```

The magnitude rule is `MAGNITUDE_STABLE iff 0.75 ≤ min and max ≤ 1.35`, applied uniformly. RQ4 at
0.7572 sits just inside the lower bound and RQ5 at 0.5135 falls outside — and RQ5 is labelled
`MAGNITUDE_ATTENUATED` accordingly rather than being described as stable. The threshold was
pre-registered in the notebook before fitting and is applied without exception, which is what makes
the label meaningful.

Every `ΔR²` in all 258 fitted rows is positive: no specification reverses the direction of any block
comparison.

---

## 8. Additional checks

**The A6 binding consequence was honoured.** The supplemental NB09 audit required that NB11 not
inherit the defective block-ΔR² bootstrap construction. NB11 records
`NB11_BOOTSTRAP_CI = NOT_USED — pending Claude-A review A6` and judges stability from point-estimate
ranges, rank, conditioning and estimator-family comparison instead. No NB11 conclusion depends on the
held construction.

**`A-R01` reporting debt partially discharged.** NB11 carries an `ssot_29_reporting_fields` block
with source count, domain count, all eight reference levels, missingness handling and a
preprocessing/version id. The FDR q-values and the p-value underflow metadata remain open in the
debt bundle.

**Not-testable items are bounded rather than skipped.** `SSOT_24_1` and `SSOT_24_2` are declared
`NOT_TESTABLE_AT_NB11` because they would require regenerating D-02 and D-04, which no decision
authorises, and each carries a measured bound on how many rows differ from the analysis text.
`SSOT_24_3` is `REALIZED_SUPPORT_ABSENT` — `source_tier` has one realised level — with the per-source
subsets run as the labelled closest analogue rather than passed off as a curated-tier contrast.
`SSOT_24_9` is `FEASIBLE_SUPPORT_IS_FIXED_ONLY` with `V5_SRC_DOM` as the feasible fixed alternative.

**Dependence remains correctly open.** NB11 records
`DEPENDENCY_PENDING_PRE_NB10_GROUPING` and states that `duplicate_group_id` is all-singleton and does
not implement `LR-01` — independently confirmed by this auditor's PRE-NB10 inventory, which measured
3,835,988 distinct values over 3,835,988 rows. **No grouping key was invented at NB11**, which is
the correct boundary.

Repository hygiene: 276 tests pass, ruff clean, worktree clean, no raw text persisted.

---

## 9. Findings

### HARD FAIL — none

```
NEW_HARD_FAIL_COUNT = 0
```

No outcome-driven pruning, no rank-deficient design fitted, no unpre-declared non-identifiability, no
primary result redefined, no causal language, no bootstrap interval claimed from the held
construction.

### NOTE

| id | note |
|---|---|
| `A-N11-01` | The field `condition_number_standardized` in NB11 is **not** the quantity of the same name in NB09/G5. NB11's `rank_of` scales by `sqrt(diag(G)/n)` — root-mean-square, **uncentred**; NB09 protocol §8 specifies centring plus unit SD. For the identical M3/FULL design the two conventions give **1172.81** and **134.57**. Both are internally consistent and this audit reproduced NB11's 1172.8096 exactly, so nothing is wrong — but the shared field name invites a false cross-stage comparison. Recommend renaming to `condition_number_rms_uncentred` in a later artifact, or stating the convention beside the number. This is the `A-01` class of ambiguity recurring in a new place. |
| `A-N11-02` | `V4_B_SSOT182` raises Outcome-B morphology partial `R²` by ~4.4×. It is correctly filed as a sensitivity, but together with `B-N01` it means the Outcome-B result under the approved common ladder carries very little independent information about morphology. Worth the Director's attention as a pair, not as two separate notes. |

### Auditor self-correction

This audit's first probe of the target-5 span identity carried a sign error on the `logCR` term and
printed a conclusion line that was not conditioned on the measured value — it reported `4.094e+00`,
which is simply `max|logCR|`, under a heading claiming confirmation. Corrected in the same session
and re-measured at `8.882e-16`. Recorded because an audit that hides its own slips is not an audit.

---

## 10. Verdict

Every one of the eight declared targets was checked against the canonical artifacts rather than
against the executor's report. The pruning rule is design-only by code inspection and by Gram
construction. Rank, both condition-number conventions, the V2 same-span `R²` equality, the V3
deficiency of exactly one, and the V4 Outcome-B effect sizes were all recomputed independently and
agree to between `1e-13` and `1e-15`. The two structural identities behind V2 and V3 were measured
over the full cohort at `8.9e-16` and `1.7e-15`.

```
NB11_RESULT_AUDIT_PASS
NB11_STATUS = CLOSED

NEW_HARD_FAIL_COUNT = 0
NOTE_COUNT          = 2
NB09_RE_AUDITED     = NO
```

The heavy slot is released to the PRE-NB10 lane, which proceeds on the already-approved Tier-1 +
Tier-2 grouping at a 19% group-aware holdout. No new method decision is opened, no MinHash and no
embedding tier is added.

This audit certifies that NB11's reported stability figures are what its pre-registered
specifications produce on the canonical artifacts. It endorses no interpretation beyond the
conditional, block-level boundary NB09 fixed, and it treats `V4_B_SSOT182` as a sensitivity exactly
as the executor filed it.
