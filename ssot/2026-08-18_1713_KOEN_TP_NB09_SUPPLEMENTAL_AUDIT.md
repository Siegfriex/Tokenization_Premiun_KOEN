# KOEN — NB09 Supplemental Audit · Bootstrap Construction, Code Provenance, Reporting Debt

> Audit ID: `NB09_SUPPLEMENTAL_AUDIT_20260818`
> Class: **SUPPLEMENTAL RESULT AUDIT** — narrow scope, three targets. Not a re-audit.
>
> Auditor: Claude-A
>
> ```
> AUDIT_SUBJECT_SHA = 820943391fb8601f64e79d9ae1b13fc60eeaa694
> PRIOR_RESULT_AUDIT = 27814139a43bfbe3d4eb2e646e97c0107acfa582   NB09_RESULT_AUDIT_PASS
> CANONICAL_MAIN     = bc8187cceae67ac87c9df1c4a08b54ca753ae035
> executed           = 2026-08-18 16:50–17:13 KST
> ```
>
> This is an `A-*` agent finding, not an `RD-*` decision.

## 0. Scope and honesty about the prior pass

The prior result audit at `27814139` returned `NB09_RESULT_AUDIT_PASS` and is canonical. It
reproduced all 258 coefficients, all 258 HC1 standard errors, every fit statistic, every block
metric and the `B-N01` algebra. **Those classes are closed and are not recomputed here.**

Two things that pass did **not** do, and this one does:

- it accepted the bootstrap on the strength of frozen seeds, matching `B`, and the point estimate
  lying inside its own interval. It did **not** inspect the algorithm or reproduce an interval.
- it did not check whether `code_sha` names a commit that actually contains the executed code.

Both gaps were raised externally. Both turned out to contain a real finding. Recorded plainly
rather than folded into the earlier PASS.

---

## 1. `T1` / `A6` — block-comparison bootstrap

### 1.1 What the executor's algorithm actually does

Read from `notebooks/09_explanatory_models.ipynb`, cells 11, 12 and 14 — not inferred from the
manifest.

Per batch, one Rademacher matrix `W` is drawn **per outcome** and reused across all five models:

```python
W = {o: rng[o].integers(0, 2, size=(m, B)).astype(float) * 2.0 - 1.0 for o in OUTCOMES}
for (mod, o), f in FITS.items():
    Xc = X[:, f["cols"]]; yhat = Xc @ f["beta"]; e = Y[o] - yhat
    sb[(mod, o)] += (Xc * e[:, None]).T @ W[o]
    ub[(mod, o)] += (yhat * e) @ W[o]
```

So the **weight vector is shared** across models — the pairing requirement is met at that level.
Then each model's replicate `R²` is built from **its own** pseudo-outcome:

```
y*_m = ŷ_m + e_m ∘ w          (cell 12: yy_star = yhat_sq + 2·ub + ssr, Xty_star = Gβ + sb)
ΔR²*  = R²*_full − R²*_reduced (cell 14)
```

The algebra inside cell 12 is correct for what it computes. `w² = 1` for Rademacher, so
`y*'y* = Σŷ² + 2Σŷeʷ + Σe²` is exact; `X'y* = Gβ + X'(e∘w)` is exact; `Σy* = Σy + Σeʷ` uses
`Σe = 0`, which holds because every design carries an intercept. Nothing here is a coding error.

**The issue is the construction, not the arithmetic.** The full and reduced models are evaluated on
**two different pseudo-outcomes**: `y*_full = ŷ_full + e_full∘w` and `y*_red = ŷ_red + e_red∘w`.
Writing `d = ŷ_full − ŷ_red = e_red − e_full`, these differ by `d ∘ (1 − w)`, which is `0` on rows
with `w = +1` and `2d` on rows with `w = −1`. A paired bootstrap of a comparison should evaluate
both models on **one** pseudo-outcome.

### 1.2 The reference construction, and why the DGP is the full model

```
CONSTRUCTION-P     y* = ŷ_full + e_full ∘ w        ONE pseudo-outcome
                   R²*_full and R²*_reduced BOTH computed on that same y*
```

The DGP is defined by the **full** fitted model, i.e. alternative-imposed. The quantity being
bounded is a confidence interval for the observed `ΔR²`, not a null-hypothesis test. Resampling
around the full fit centres the replicate distribution on the estimate, which is what a percentile
CI requires. The null-imposed alternative (`ŷ_red + e_red∘w`) answers "is `ΔR²` larger than under
the null" — a test, not an interval — and is not what the protocol asks for. Stated here so the
choice is auditable rather than assumed.

Both constructions were computed from **one shared weight stream** under this auditor's own seed
`20260818`, deliberately **not** B's seeds, so the comparison is an independent implementation and
the only difference between the two columns is the construction itself. All quantities come from
streaming accumulations; no model is refitted per replicate.

### 1.3 Step 1 — the reimplementation reproduces the executor's published intervals

Before comparing constructions, `CONSTRUCTION-B` was reimplemented here and checked against what
the executor published. A different seed means agreement is expected only to Monte-Carlo error.

| RQ | published CI | independent repro of the same construction | half-width ratio |
|---|---|---|---:|
| RQ3 | `[0.620245, 0.621652]` | `[0.620283, 0.621633]` | 0.960 |
| RQ4 | `[0.006476, 0.006701]` | `[0.006484, 0.006700]` | 0.963 |
| RQ5 | `[0.150248, 0.151317]` | `[0.150255, 0.151307]` | 0.984 |

The algorithm was therefore read correctly, and what follows is a comparison of constructions rather
than a disagreement about what the executor did.

### 1.4 Step 2 — the measurement (Outcome A, `B = 2000`, shared weight stream)

| RQ | point ΔR² | B mean | P mean | B sd | P sd | sd ratio P/B | half-width ratio P/B |
|---|---:|---:|---:|---:|---:|---:|---:|
| RQ3 `M0→M1` | 0.620954 | 0.620947 | 0.620950 | 3.509e-04 | 3.352e-04 | 0.955 | **0.990** |
| RQ4 `M1→M2` | 0.006590 | 0.006592 | 0.006590 | 5.471e-05 | 8.737e-05 | **1.597** | **1.580** |
| RQ5 `M2→M3` | 0.150770 | 0.150780 | 0.150784 | 2.682e-04 | 2.197e-04 | 0.819 | **0.798** |

```
current_B_CI            RQ3 [0.620283, 0.621633]   RQ4 [0.006484, 0.006700]   RQ5 [0.150255, 0.151307]
paired_reference_CI     RQ3 [0.620275, 0.621612]   RQ4 [0.006414, 0.006756]   RQ5 [0.150362, 0.151201]
abs endpoint difference RQ3 ≤2.1e-05               RQ4 ≤7.0e-05               RQ5 ≤1.1e-04
relative width diff     RQ3 −1.0%                  RQ4 **+58.0%**             RQ5 −20.2%
point estimate          UNCHANGED in every case — both constructions centre on it to ~1e-5
```

### 1.5 Step 3 — is this Monte-Carlo noise?

The relative Monte-Carlo standard error of a bootstrap sd at `B = 2000` is `1/√(2B) = 1.58%`.

```
RQ3   sd ratio 0.955   ->   2.0 sigma from equivalence
RQ4   sd ratio 1.597   ->  26.7 sigma from equivalence
RQ5   sd ratio 0.819   ->   8.1 sigma from equivalence
```

RQ3 is practically equivalent. RQ4 and RQ5 are not, and RQ4 is decisively not — the executor's
interval is roughly **37% too narrow** relative to the paired reference (`1/1.597`). The direction
is not uniform: RQ5 goes the other way, so this is a construction-dependent distortion rather than a
constant bias that could be argued away.

**RQ4 is the primary morphology question** (SSOT §19.2), where the increment is small
(`ΔR² = 0.0066`) and the whole interpretive weight sits on whether that increment is bounded away
from negligible. That is precisely the comparison where an understated stability interval matters.

### 1.6 Classification and scope

```
BOOTSTRAP_BLOCK_CI = NARROW_METHOD_DEFECT_REQUIRING_CI_CORRECTION
```

The correction scope is **the block ΔR² bootstrap interval and its `delta_r2_bootstrap_sd`
companion, and nothing else.** Explicitly unaffected, because none of them consumes the bootstrap:

```
beta                    UNAFFECTED   closed-form OLS from the Gram
HC1 standard errors     UNAFFECTED   closed-form sandwich, no RNG
R2 / adjusted R2        UNAFFECTED
ΔR² point estimate      UNAFFECTED   both constructions centre on it
partial R² point est.   UNAFFECTED
AIC / BIC               UNAFFECTED
LR chi-square           UNAFFECTED
B-N01                   UNAFFECTED   algebraic, verified independently at 27814139
artifact / cohort       UNAFFECTED
```

The **coefficient** bootstrap (`boot_coef_sd`, from `δβ* = G⁻¹X'(e∘w)`) is a textbook multiplier
bootstrap of a single estimator and is **valid as it stands** — perturbing each model around its own
fit is correct when only that model's own dispersion is wanted. The defect appears only when
differencing across two models, which is the one thing the block comparison does.

### 1.7 Binding consequence for NB11

```
NB11 MUST NOT reuse the block-ΔR² bootstrap implementation until it is corrected.
NB11 MAY reuse the coefficient multiplier bootstrap unchanged.
```

NB11 is a robustness stage whose whole purpose is comparing specifications, so it would inherit this
construction at exactly the wrong place. The correction is small — accumulate `X_reduced'(e_full∘w)`
alongside the existing terms and evaluate both models on the full model's pseudo-outcome — and needs
no re-fit and no new pass over the data beyond the one already performed.

The intervals in §1.4 are from this auditor's seed and are **evidence of the size of the effect, not
a replacement result**. A corrected artifact must be recomputed under the frozen seeds in
`03_NB09_SEED_REGISTRY_v001.json`.

---

## 2. `T2` — code provenance

### 2.1 The finding

`code_sha` in both `NB09_RUN_MANIFEST_v001.json` and `NB09_EXPLANATORY_RESULTS_v001.json` is
`6368687c3def…`. `notebooks/09_explanatory_models.ipynb` **does not exist at that commit**, and no
NB09 script exists there either. The notebook is first introduced by the result commit itself.

Mechanism, from cell 18 of the notebook:

```python
CODE_SHA = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], ...).stdout.strip()
```

`git rev-parse HEAD` is evaluated **at run time**, when the notebook was still uncommitted in the
worktree `/home/sieg/projects-wsl/KOEN_nb09_20260818`. It therefore captured the base commit the
working tree stood on, not the commit that would later contain the executed code. That worktree now
sits at `8209433`, consistent with the notebook having been committed after the run.

This is precisely the situation SSOT §30.2 `[C012]` created the two-field record for
(`execution_code_commit` + `artifact_record_commit` "when artifact persistence occurs in a later
commit"), and the project already uses that convention in `TOKEN_O200K_BASE_MANIFEST_v001.json` and
`MORPH_FEATURES_KIWI_MANIFEST_v001.json`, each with a `lineage_note`.

### 2.2 Evidence that the committed code is the executed code

This is the question that decides whether the finding is metadata or science. It is answered
positively, and by artifact rather than by argument.

The committed notebook carries stored output on **all 11 code cells** with `execution_count` set,
and those stored outputs match the persisted artifacts exactly:

```
model-fit lines matching persisted R2 / p / rank            10 / 10
block-comparison lines matching persisted ΔR² / partial R² / bootstrap CI    8 / 8
HC1_SCALE printed line matches persisted hc1_scale          yes

notebook code-cell source sha256  e44b4d00ca0e63ee8688134ded064032cbf5efd3f9ecd5d20b87460d4cec4e44
notebook file sha256              eb242c0eddfbd8c5d25c9d220879024fe90f1fcfcda70cf796f5cb22f3fa1906
```

A notebook whose stored outputs reproduce the published numbers line for line is the notebook that
produced them. No evidence of divergence between executed and committed source exists.

### 2.3 Record of factual classification

```
EXECUTION_PARENT_SHA        6368687c3def9786ad886d3c4886862403e22dd1
EXECUTION_CODE_COMMIT       UNCOMMITTED_WORKTREE_AT_RUN_START  (working tree based on 6368687)
RESULT_ARTIFACT_COMMIT      820943391fb8601f64e79d9ae1b13fc60eeaa694
RESULT_CODE_OF_RECORD_SHA   820943391fb8601f64e79d9ae1b13fc60eeaa694
MANIFEST_CODE_SHA_ORIGINAL  6368687c3def9786ad886d3c4886862403e22dd1

CODE_PROVENANCE_CLASSIFICATION = CODE_PROVENANCE_METADATA_DEFECT
```

`8209433` is **not** relabelled as a historical execution commit. It is the commit in which the
executed source and its artifacts were persisted — the `artifact_record_commit` of the C012 pair —
and the run's own parent is recorded separately. Reproduction is performed from `8209433`.

Does not block NB11.

---

## 3. `T3` — `NB09_RELEASE_REPORTING_DEBT`

Bundled, per instruction, without further compute.

| item | state | evidence |
|---|---|---|
| p-value underflow metadata | 167 of 258 coefficient rows and all 8 block rows store `p = 0.0` with no underflow flag and no `log10(p)` companion | the project's own RQ1 precedent on `main` records `pvalue_raw: 0.0` **plus** `pvalue_underflowed: true`, `pvalue_reported: "p < 1e-300 (underflow; log10(p) = −517715.4)"` and `log10_pvalue`. NB09 stores only the raw zero. |
| BH-FDR q-values, morphology family | absent from every artifact | computed by this auditor at `27814139`: three at `0.0`, `particle_ratio` at `8.791e-11`. No conclusion changes. |
| source count | not restated | derivable from the cell dummies |
| domain count | not restated | derivable from the cell dummies |
| reference levels | not restated in the result artifacts | present in the contract on `main`; also recoverable as the omitted level |
| missingness handling statement | not restated | fixed by the protocol; G5 measured zero |

```
NB09_RELEASE_REPORTING_DEBT   OPEN — must close before NB13
P_VALUE_UNDERFLOW_STATUS      NOTE, folded into the debt bundle
```

No scientific claim rests on `p = 0`: the README carries no p-value column at all, and every block
row records `primary_evidence = delta_r2 / partial_r2 / stability`. Does not block NB11.

---

## 4. Verdict

```
NEW_HARD_FAIL_COUNT = 0

BOOTSTRAP_BLOCK_CI_STATUS     NARROW_METHOD_DEFECT_REQUIRING_CI_CORRECTION
BOOTSTRAP_CORRECTION_REQUIRED YES — block ΔR² interval + delta_r2_bootstrap_sd only
                              coefficient multiplier bootstrap remains valid
CODE_PROVENANCE_STATUS        CODE_PROVENANCE_METADATA_DEFECT
                              committed code proven to be the executed source
P_VALUE_UNDERFLOW_STATUS      NOTE — bundled into NB09_RELEASE_REPORTING_DEBT
A_R01_STATUS                  OPEN — bundled into NB09_RELEASE_REPORTING_DEBT, close before NB13

NB09_POINT_RESULTS_STATUS     VALID — unchanged, independently reproduced at 27814139
NB09_HC1_STATUS               VALID — unchanged, independently reproduced at 27814139

NB11_ENTRY_AUTHORIZED = YES
```

No wider scientific dependency was found. The bootstrap defect does not reach any point estimate,
any standard error, any information criterion, any nested statistic, or `B-N01`; it reaches one
interval artifact and its companion sd, on a stage whose primary evidence the protocol already
defines as `ΔR²` and partial `R²` magnitude with the interval as **stability** evidence beside them.

The one thing that must not happen is NB11 inheriting the construction. That is recorded in §1.7 as
binding.

`NB09_RESULT_AUDIT_PASS` at `27814139` stands. This supplement adds two findings it did not cover
and narrows the correction scope so no science is re-opened.
