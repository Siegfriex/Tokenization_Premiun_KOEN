# KOEN — NB09 Explanatory Models · Independent Result Audit

> Audit ID: `NB09_RESULT_INDEPENDENT_AUDIT_20260818`
> Class: **RESULT AUDIT** (`VD-BASELINE-20260818-1520` §7 C — performed after execution)
>
> Auditor: Claude-A (Engineering / Reproducibility Auditor · Integration Steward)
>
> ```
> AUDIT_SUBJECT_SHA = 820943391fb8601f64e79d9ae1b13fc60eeaa694
>                     research(nb09): execute canonical explanatory models M0-M3
> subject branch    = research/nb09-explanatory-20260818
> protocol          = 81b682527c587f64c817b7dab74f538f16bf9152  (+ erratum 1dd6f75)
> protocol audit    = 33c59d58a00202e961aa68a2f9e23fcf27033004  PASS
> targeted re-audit = 85aa19ef1d92e636ff009794915e460a526d21bf  PASS
> canonical main    = 6368687c3def9786ad886d3c4886862403e22dd1
> audit worktree    = /home/sieg/projects-wsl/KOEN_audit_nb09   (new branch, not reused)
> executed          = 2026-08-18 16:41–16:47 KST
> ```
>
> This is an `A-*` agent finding. It is not an `RD-*` decision.

Every number below was recomputed from the canonical D-01…D-05 parquet artifacts. B's notebook was
neither imported nor executed. All 258 reported coefficients and all 258 HC1 standard errors were
independently reproduced.

---

## 1. Method — why this counts as independent

The executor solved each model from a streaming Gram. This audit accumulates the **augmented** Gram
`[1, X_universe, y_A, y_B]ᵀ[same]` **once**, then solves every one of the ten model × outcome
combinations from submatrices of that single object — so the ten fits share one pass rather than ten,
and the design is rebuilt from `ssot_nb09/02_NB09_MODEL_MATRIX_CONTRACT_v001.json` rather than from
B's code.

The solver is itself cross-checked: β is obtained by Cholesky on the normal equations **and**
independently by eigendecomposition of `XᵀX`. The two routes agree to `2.5e-09` at worst (M3), and
below `2e-10` for every other model, so the comparison against B is not resting on a single
factorization.

HC1 is recomputed, not accepted: a second pass accumulates `Σᵢ eᵢ² xᵢ xᵢᵀ` for all ten combinations
simultaneously, and `V = [N/(N−p)] (XᵀX)⁻¹ M (XᵀX)⁻¹` is formed from it.

---

## 2. Ancestry and chronology — `PASS`

```
protocol subject 81b6825   ANCESTOR of the result
authority erratum 1dd6f75  ANCESTOR
protocol audit 33c59d5     ANCESTOR
targeted re-audit 85aa19e  ANCESTOR
canonical main 6368687     ANCESTOR
```

The result is a single commit on top of canonical `main`, and `main` already contained the audited
protocol. The protocol therefore precedes every coefficient by Git ancestry, not by assertion.

The run manifest records the same four SHAs itself (`AUDITED_PROTOCOL_SHA`,
`AUTHORITY_ERRATUM_SHA`, `PROTOCOL_AUDIT_SHA`, `CANONICAL_BASE_SHA`), which is the SSOT §30.2 `C012`
lineage requirement satisfied in the artifact rather than only in the commit graph.

```
RESULT_GENERATED_BEFORE_PROTOCOL_FREEZE = NO
```

---

## 3. Artifacts, cohort, and the fitted design — `PASS`

```
artifact identity   5/5   D-01 95f523d1…  D-02 dfae8e01…  D-03 0fe5bd74…
                          D-04 1c30e327…  D-05 bfa98bd6…
N                   3,835,988
pair-set hash       d9660d654ee449e4d0c23a0070225274
row order           ORDER BY pair_id — asserted in the run, as the protocol §3.3 required
```

The fitted model set is exactly the contract's: `{M0, M1, M2, M2A, M3}`, no extras, none missing.
Column-by-column against the contract, taken from the coefficient table rather than from a summary
field:

| model | continuous used | expected | extras | missing | p | rank |
|---|---:|---:|---|---|---:|---:|
| M0 | 1 | 1 | — | — | 8 | **8** |
| M1 | 16 | 16 | — | — | 23 | **23** |
| M2 | 20 | 20 | — | — | 27 | **27** |
| M2A | 19 | 19 | — | — | 26 | **26** |
| M3 | 38 | 38 | — | — | 45 | **45** |

Full rank everywhere. No rank deficiency, no dropped term, no added term, no reference level moved.

```
UNAPPROVED_PRIMARY_MATRIX_CHANGE = NONE
RANK_DEFICIENCY = NONE
```

---

## 4. Independent recomputation — the numbers

### 4.1 Coefficients and HC1 standard errors

All 258 coefficient records were matched term by term. B labels categorical dummies `cell::…` and
`dir::…` where this audit labels them `source_domain_cell::…` and `translation_direction::…`; after
normalising that naming, **zero terms went unmatched**.

| model / outcome | terms | worst rel. Δβ | worst rel. ΔSE(HC1) | worst rel. Δz |
|---|---:|---:|---:|---:|
| M0/A | 8 | 6.1e-12 | 4.5e-14 | 6.1e-12 |
| M0/B | 8 | 5.8e-13 | 5.9e-14 | 6.4e-13 |
| M1/A | 23 | 7.4e-11 | 6.9e-12 | 7.3e-11 |
| M1/B | 23 | 5.5e-11 | 6.1e-12 | 5.4e-11 |
| M2/A | 27 | 1.0e-10 | 9.6e-12 | 1.0e-10 |
| M2/B | 27 | 6.0e-11 | 8.3e-12 | 6.0e-11 |
| M2A/A | 26 | 4.3e-11 | 9.2e-12 | 4.4e-11 |
| M2A/B | 26 | 2.5e-11 | 7.6e-12 | 2.6e-11 |
| M3/A | 45 | 1.3e-08 | 6.2e-11 | 1.3e-08 |
| M3/B | 45 | **1.5e-08** | 6.0e-11 | 1.5e-08 |

Worst relative disagreement anywhere: **β 1.5e-08, HC1 SE 6.2e-11, z 1.5e-08.** M3 is the loosest,
which is expected rather than alarming — its standardized condition number is 134.57, so roughly
eight digits of agreement is what two different factorizations should deliver.

Reported `ci95_lo`/`ci95_hi` equal `coef ± 1.959964 · HC1_SE` for **all 258 rows**.

### 4.2 `A-M02` / `R-04` — the HC1 scale, closed

The one review the protocol audit left open was that HC1's finite-sample scale was named but never
written literally. The run states it and applies it:

```
hc1_scale_formula = "N / (N - p)"
```

and the per-model constants match `N/(N−p)` exactly at machine precision for all ten:

```
p= 8  1.0000020855166085     p=23  1.0000059958836955     p=26  1.0000067779607826
p=27  1.000007038653417      p=45  1.000011731144076
```

That, plus the independently recomputed sandwich agreeing to 6.2e-11, closes `R-04`. The
implementation is HC1, not HC0, not HC2, not HC3.

```
R-04 = CLOSED
```

### 4.3 Fit statistics and comparison metrics

Recomputed from my own Gram; every relation holds exactly:

```
R²        = 1 − SSR/SST                         max diff 0.0  across all ten
adj R²    = 1 − (1−R²)(N−1)/(N−p)               max diff 0.0  across all ten
ΔR²       = R²_full − R²_reduced                max diff 0.0  across all eight comparisons
partial R²= (R²_full − R²_reduced)/(1 − R²_red) max diff 0.0  across all eight
AIC/BIC   = −2·llf + 2(p+1) / −2·llf + (p+1)ln N   agrees to ≤4.4e-06
LR χ²     = N · ln(SSR_reduced / SSR_full)      agrees to ≤2.3e-11 across all eight
```

The AIC/BIC convention is the standard one counting the variance parameter (`k = p+1`); the
alternative `k = p` convention is off by exactly 2.0 and is not what was used. Worth recording
because the constant is a convention, not a derivation.

Every reported ΔR² lies inside its own reported bootstrap 95% interval.

### 4.4 Bootstrap parameters

```
B         2000                       == frozen registry
seeds     NB09_GLOBAL 2703484264      == frozen registry
          NB09_COEF_BOOTSTRAP_A 1222524615   == frozen registry
          NB09_COEF_BOOTSTRAP_B 1018984010   == frozen registry
method    pair-level multiplier (wild), Rademacher     == protocol §3.2
row order ORDER BY pair_id (asserted)                  == protocol §3.3
```

All three seeds were independently rederived from the protocol's stated rule at the protocol audit
and are used unchanged here. Nothing was chosen after seeing a result.

```
BOOTSTRAP_PARAMETER_NOT_FROZEN_PRE_RESULT = NO
```

---

## 5. `B-N01` — verified, and it is not a defect

The executor discloses, unprompted, that above M0 the Outcome B fit **is** the Outcome A fit. This
audit confirms it algebraically and numerically.

`Y_B = Y_A − logCR − logBDR` by the exact decomposition, and both `logCR` and `logBDR` are columns of
M1. Their sum therefore lies in the column space of every model from M1 up, so the projection
residual of `Y_B` equals that of `Y_A` exactly, and β differs only by `−1` on those two coordinates.

Measured, by this auditor, on the recomputed coefficient vectors:

| model | max abs deviation of (β_B − β_A) from the predicted −1 shift | SSR_A − SSR_B |
|---|---:|---:|
| M1 | 5.2e-12 | 2.3e-08 |
| M2 | 6.4e-12 | 2.6e-08 |
| M2A | 5.8e-12 | 2.5e-08 |
| M3 | 1.2e-11 | −6.1e-09 |
| M0 | n/a — design omits both terms | **73,289.885** |

Exactly as predicted: identical above M0, materially different at M0.

Consequences the executor states and this audit endorses:

- RQ4 and RQ5 partial `R²` are **identical** across outcomes by construction — `0.018807` and
  `0.438500` respectively, in both columns. They are **not two independent confirmations**.
- ΔR² differs between outcomes only through the SST denominator.
- AIC and BIC coincide for M1, M2, M2A, M3; only M0 differs.
- Only RQ3 carries genuinely different information between the outcomes.

**This is not outcome leakage.** Leakage would mean an outcome reconstructible from its own
right-hand side; neither is, which G5 established structurally and full rank at every model
re-confirms. It is the measured consequence of `SPEC-02` — SSOT §18.2's illustrative Outcome-B form
omits the two representation ratios while the approved common ladder includes them — which the
protocol recorded before execution and my protocol audit carried forward as a NOTE.

The executor made no protocol change in response, routed the re-specification question to the
Director, and registered it as an NB11 candidate. That is the correct handling: the protocol was
audited and closed, and it was executed as frozen.

Recording it prominently rather than reporting "both outcomes confirm the morphology block" is the
single most consequential judgement in this result set, and it was made in the right direction.

---

## 6. Claim boundary — `PASS`

Scanned `README.md`, both result JSONs, the run manifest and both CSV tables for causal language,
Korean-inefficiency claims, the byte-count fallacy, reasoning-degradation claims, pure source or
domain effects, and predictive-importance-as-cause. Every hit is a prohibition or a denial. The two
"because" clauses in the B-N01 section explain an algebraic identity, not a mechanism in the world.

The ten binding restrictions are carried in the README **and** embedded in all three machine-readable
artifacts, so a downstream consumer reading only the JSON still receives them:

```
SCRIPT_MIXING_BLOCK_INTERNAL_REDUNDANCY = YES
M3_INTERNAL_COLLINEARITY_REVIEW         = YES
RAW_CHUNK_COUNT_COEFFICIENT_SUBSTANTIVE_INTERPRETATION = PROHIBITED
RQ5_PRIMARY = BLOCK_LEVEL_M3_MINUS_M2
source_domain_cell / translation_direction restrictions
PAIR_LEVEL_MULTIPLIER_BOOTSTRAP != DUPLICATE_CLUSTER_DEPENDENCE_CORRECTION
coefficient_p_values = secondary; never used to rank predictors
causal_language = PROHIBITED
outcome_A_and_B_narratives = never merged
```

p-values appear as `p_value_secondary`, `nested_p_value` and `hc1_robust_wald_p_value`; the block
comparison table's `primary_evidence` column reads `delta_r2 / partial_r2 / stability` on every row.
No feature is ranked by p-value anywhere.

---

## 7. Findings

### HARD FAIL — none

Checked against the full `VD-BASELINE-20260818-1520` §6 list: artifact or cohort mismatch (no — 5/5,
N and pair-set exact), outcome or estimand changed (no), unapproved primary matrix change (no —
column-exact), outcome leakage (no — §5), rank deficiency (no — full rank in all five), invalid or
non-reproducible inferential formula or implementation (no — 258 coefficients and 258 HC1 SEs
independently reproduced, HC1 scale verified), bootstrap parameter not frozen pre-result (no — seeds
and B match the frozen registry), result before protocol freeze (no — §2), SSOT contradiction (none
in the science; see `A-R01` for reporting completeness), false Director authority (none — the
artifacts cite `VD-NB09-OPERATIONALIZATION-01`).

```
HARD_FAIL_COUNT = 0
```

### REVIEW

| id | finding | required closure |
|---|---|---|
| `A-R01` | **SSOT §29 mandatory reporting fields are incomplete.** The BH-FDR q-value required for individual morphology coefficients is absent from every artifact — no `q_value`, `fdr` or `benjamini` field exists anywhere. Also absent as restated fields: source count, domain count, reference levels, and the missingness-handling statement. | add before NB09 is cited in any release. Nothing needs re-running: see below. |
| `R-01` | M3 collinearity (cond 134.57, max VIF 1,252.61) — carried from G5 | governed: instability warning, RQ5 read as block comparison, NB11 #11 |
| `R-02` | `SM-01` script-mixing redundancy — carried from G5 | governed: block-level only, NB11 #10 |
| `R-03` | duplicate / paraphrase dependence not corrected | declared; NB11 #12, PRE-NB10 grouping |
| `B-N01` | Outcome B is the same fit as Outcome A above M0 | Director decision on re-specification; NB11 candidate. Verified in §5; **not** a defect |

**On `A-R01`, and why it is a REVIEW rather than a HARD FAIL.** No computed quantity is wrong, no
estimand, cohort or matrix is affected, and the missing items are restatements of facts already
fixed and audited elsewhere in the lineage — reference levels are in the contract on `main` and are
recoverable from the omitted dummy level, and the protocol fixes the missingness rule. The FDR gap
touches only individual coefficient inference, which the protocol explicitly demotes to secondary
and forbids using to rank anything. But SSOT §29 states the list as mandatory for every regression
table, and this is a real omission against it.

To show the gap is closable without re-running and to quantify its materiality, this auditor computed
the Benjamini–Hochberg q-values over the morphology family (m = 4, M2, both outcomes) from the
reported p-values:

```
morpheme_density    coef +7.313080e-02   p 0.000e+00    BH q 0.000e+00
particle_ratio      coef +1.261123e-02   p 8.791e-11    BH q 8.791e-11
ending_ratio        coef −1.074457e-01   p 0.000e+00    BH q 0.000e+00
deriv_affix_ratio   coef −1.579680e-01   p 0.000e+00    BH q 0.000e+00
```

No conclusion changes. The correction is a reporting addition, not a re-analysis. Per
`VD-BASELINE-20260818-1520` §6 a REVIEW does not block progression and must not trigger a
remediation loop, so NB11 is not gated on it — but it must be closed before NB13.

### NOTE

| id | note |
|---|---|
| `A-N01` | `eng_obs_001_note` says the materialize stage "ran ~10 s" with "sample count 2"; the recorded telemetry shows 16.01 s and 3 samples. The point the note makes — that the stage is under the 30 s ENG-OBS-001 threshold and its sample count is by design — stands. Prose only. |
| `A-N02` | The `software` block (duckdb 1.5.5, numpy 2.5.2, pyarrow 24.0.0, python 3.12.3, scipy 1.18.0) plus `code_sha` satisfies SSOT §29's preprocessing/version ID; noted so `A-R01` is not read as including it. |

Telemetry itself is compliant: three stages, 10-second periodic sampling, all `COMPLETED`, zero
RED-or-worse samples, minimum `MemAvailable` 7.74 GiB, peak RSS 3.36 GiB, one heavy job at a time.
`pass2` ran 579.9 s under 59 samples.

Repository hygiene: 276 tests pass, ruff clean, worktree clean, no parquet or raw text staged, zero
Hangul characters and no `pair_id` list in any published artifact, longest embedded array 258 (the
coefficient table). The `.gitignore` allowlist additions (`!outputs/reports/NB09_*`,
`!outputs/tables/`, `!outputs/tables/NB09_*`) follow the established per-family pattern and admit
exactly the four evidence files.

---

## 8. Verdict

Two hundred fifty-eight coefficients and two hundred fifty-eight HC1 standard errors were
reproduced from the canonical artifacts by a different computational route, agreeing to 1.5e-08 and
6.2e-11 respectively. Every fit statistic, every block-comparison metric and every nested test
statistic reproduces from an independently accumulated Gram. The design matrices are column-exact
against the audited contract, full rank at every model. The bootstrap parameters are the ones frozen
before execution. The protocol precedes the result by ancestry. No causal or out-of-scope claim
appears anywhere, and the one structurally consequential finding in the result set — that Outcome B
is not an independent confirmation above M0 — was surfaced by the executor rather than left for the
auditor to catch.

```
NB09_RESULT_AUDIT_PASS

HARD_FAIL_COUNT = 0
REVIEW_COUNT    = 5   (A-R01 new · R-01 R-02 R-03 carried · B-N01 Director decision)
NOTE_COUNT      = 2
R-04            = CLOSED

NB11_ENTRY_AUTHORIZED = YES
```

Per `VD-BASELINE-20260818-1520` §9, NB11 may begin directly from this audit commit; canonical
integration proceeds serially and separately and is not a science blocker.

This audit certifies that the reported numbers are what the frozen protocol produces on the
canonical artifacts. It certifies nothing about what those numbers mean beyond the conditional,
block-level claim boundary the protocol fixed, and it endorses no interpretation of any individual
coefficient.
