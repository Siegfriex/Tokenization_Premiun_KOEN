# KOEN — PRE-NB09 Explanatory-Model Protocol · Independent Audit

> Audit ID: `PRE_NB09_PROTOCOL_INDEPENDENT_AUDIT_20260818`
> Class: **PROTOCOL AUDIT** (`VD-BASELINE-20260818-1520` §7 B — performed before results)
>
> Auditor: Claude-A (Engineering / Reproducibility Auditor · Integration Steward)
>
> ```
> AUDIT_SUBJECT_SHA = 81b682527c587f64c817b7dab74f538f16bf9152
>                     research(nb09) fix: finalize authority and inference contract
> subject branch    = research/pre-nb09-protocol-20260818
> superseded        = 83a686c7b5064d8cd77f0e329e651eb235f2703b  (first freeze — NOT audited as final)
> baseline main     = 9fbcf0c127c804e8682edf1a1f14c3eea0e423a0
> harness           = 966e1e6194ecaca81bbadaff379f3ec4f45863a5
> audit worktree    = /home/sieg/projects-wsl/KOEN_audit_prenb09_protocol
> executed          = 2026-08-18 15:00–15:35 KST
> ```
>
> Authority for this audit: `VD-BASELINE-20260818-1520` §7 · §8 · §9.
> This audit is an `A-*` agent finding. It is not an `RD-*` decision and does not become one.

Every structural number below was recomputed from the canonical D-01…D-05 parquet artifacts. B's
reported figures were used only as a comparison target, never as an input. Every SSOT clause the
protocol cites was read out of `KOEN-TP-RS-001` itself rather than accepted from the protocol's
paraphrase.

---

## 0. Subject resolution — the first freeze is not the subject

`83a686c` was the candidate named at handoff. On fetch it proved to be an **ancestor** of the branch
tip, superseded by `81b6825` at 15:31 KST. The audit was re-pinned before any finding was recorded;
nothing from the `83a686c` pass is carried into this verdict.

`81b6825` corrects three defects B found in its own first freeze, all **before** handoff and before
any result existed — the only window in which correcting a frozen protocol is legitimate:

| # | defect in `83a686c` | correction in `81b6825` | audited |
|---|---|---|---|
| 1 | bootstrap seed deferred to run time | seeds frozen in §3.3 + `03_NB09_SEED_REGISTRY_v001.json` | §5 `A-M03` — **verified by independent rederivation** |
| 2 | three globally forbidden claims missing from the claim boundary | §7.5 added | §6 — present and correct |
| 3 | authority labels not separated | §0 added | §1 — correct |

Item 1 mattered: a run-time-derived seed is the reproducibility gap `VD-BASELINE-20260818-1520` §7
lists as a HARD FAIL class. Had `83a686c` been audited as final it would have failed on that point.
Auditing the tip rather than the named candidate is what caught it.

```
AUDIT_SUBJECT_SHA is now immutable. Later commits on
research/pre-nb09-protocol-20260818 are a different subject and do not reopen this audit.
```

---

## 1. Authority labelling

`VD-BASELINE-20260818-1520` §6 forbids promoting an agent recommendation or a Vice-Director
operationalization into a Research Director decision. HARD FAIL if false Director authority remains.

The subject's §0 carries a per-class table and states plainly that **no `RD-*` is claimed** for the
NB09 interpretation contract. R0 and the `SM-01` / `M3-01` / `ID-03` / `ID-04` / `SPEC-01` /
`SPEC-02` dispositions are labelled `VD-NB09-OPERATIONALIZATION-01` ·
`SSOT_CONFORMANT_OPERATIONALIZATION` · `NOT_A_DIRECTOR_DECISION`. §8's heading carries the same
label. The HC1 choice, the multiplier bootstrap, the refusal of cluster-robust SE, the seed rule and
the §5 metric table are labelled **agent-level `B-*` findings offered for audit**.

Independent check of that last claim: `KOEN-TP-RS-001` prescribes only that **SE type be reported**
(§29 mandatory field list). It nowhere prescribes which SE. HC1 is therefore genuinely B's own
derivation and is labelled correctly rather than dressed as a specification requirement.

Required tokens:

| required | present |
|---|---|
| `VD-NB09-OPERATIONALIZATION-01` | YES — header, §0 table, §8 heading |
| `NOT_A_DIRECTOR_DECISION` | YES — header, §0, §8 |
| `PRIMARY_COLUMN_SET_CHANGED = NO` | YES — header block, mechanically verified in §2 below |
| `NB09_FITTED = NO` | YES — header block; corroborated by the tree contents in §7 |
| `AUTHORITY_LABEL_FIXED = YES` | **substance yes, literal token no** → `N-02` |

```
FALSE_DIRECTOR_AUTHORITY_REMAINS = NO
```

---

## 2. `PRIMARY_COLUMN_SET_CHANGED = NO` — mechanically verified

The subject asserts this in §2.5. It was not accepted. Every model's column list and
`p_with_intercept` in `ssot_nb09/02_NB09_MODEL_MATRIX_CONTRACT_v001.json` was compared element by
element against `outputs/reports/G5_REALIZED_MODEL_CONTRACT_v001.json` **on canonical `main`** —
the artifact this auditor independently verified at `9d99e13`.

| model | continuous cols | list identical | `p` | reference levels identical |
|---|---|---|---|---|
| M0 | 1 vs 1 | **YES** | 8 vs 8 | YES (both categoricals) |
| M1 | 16 vs 16 | **YES** | 23 vs 23 | YES |
| M2 | 20 vs 20 | **YES** | 27 vs 27 | YES |
| M2A | 19 vs 19 | **YES** | 26 vs 26 | YES |
| M3 | 38 vs 38 | **YES** | 45 vs 45 | YES |

Identical as ordered lists, not merely as sets. The carried G5 diagnostics in the contract
(`rank_at_g5`, `condition_number_standardized_at_g5`, `max_vif_at_g5`) reproduce the audited values
to full stored precision — e.g. M3 `134.5679824256145` and `1252.608683352504`, byte-identical to
the merged report.

The matrix contract is also **unchanged between `83a686c` and `81b6825`**, so the correction round
touched prose and seeds only, never the science contract.

```
UNAPPROVED_PRIMARY_MATRIX_CHANGE = NONE
```

---

## 3. Structural audit — layer A (`C0`–`C7`)

Run with `scripts/audit_pre_nb09.py` from the prepared harness (`966e1e6`), driven by a spec
transcribed from the **subject's own** `02_NB09_MODEL_MATRIX_CONTRACT_v001.json`. The transcription
was checked both ways: no column the subject names is missing from the transform layer, and no
transform-layer column goes unused. Isolated worktree, `PYTHONPATH` forced to it, artifacts
symlinked to the canonical store, offline tokenizer cache provisioned.

Method note on independence: rank, condition number, VIF and GVIF are derived here from an exact
Gram matrix accumulated in two streaming passes. B's G5 figures came from a streaming Householder
QR. Two different numerical routes over the same artifacts.

### C0 — prerequisites

```
artifact identity   5/5 rehashed from the physical files
  D-01 95f523d1…0bec52   D-02 dfae8e01…50d309   D-03 0fe5bd74…3e50f7d
  D-04 1c30e327…2c16e7   D-05 bfa98bd6…1944ab
cohort              N = 3,835,988 · distinct pair_id = 3,835,988
pair-set md5        d9660d654ee449e4d0c23a0070225274
join preservation   D-04 × D-01 / D-02 / D-03 / D-05 = 3,835,988 each
non-finite          0 across all 41 design terms
```

### C1–C7 — results

| model | p | rank | deficiency | cond (standardized) | max VIF |
|---|---:|---:|---:|---:|---:|
| M0 | 8 | **8** | 0 | 10.2375 | 3.2465 |
| M1 | 23 | **23** | 0 | 20.1005 | 12.9512 |
| M2 | 27 | **27** | 0 | 20.9757 | 17.4665 |
| M2A | 26 | **26** | 0 | 20.9719 | 16.6896 |
| M3 | 45 | **45** | 0 | 134.5680 | 1252.6087 |

Matches the G5 baseline reference exactly, which is the expected outcome given §2 — but it was
measured, not assumed. Had it deviated it would have been investigated, not forced.

174 findings, all `PASS` except three `REVIEW_TRIGGER`:

```
C0_artifact_identity        5 PASS     C2_excluded_stays_out    23 PASS
C0_cohort_n                 1 PASS     C2_identity_holds        11 PASS
C0_join_preserves_n         4 PASS     C2_outcome_not_on_rhs    10 PASS
C0_pair_set_md5             1 PASS     C3_rank                   5 PASS
C0_nonfinite                1 PASS     C4_condition_number       4 PASS · 1 REVIEW
C1_column_evaluable        41 PASS     C5_vif_gvif               4 PASS · 1 REVIEW
C1_physical_column_exists  36 PASS     C6_same_construct        10 PASS · 1 REVIEW
C1_reference_level          2 PASS     C7_nesting                5 PASS
C1_zero_variance            1 PASS     C7_mutual_exclusion      10 PASS

HARD_FAIL = []
```

`C2` deserves naming. Eleven identities were re-measured over the full cohort, including the two
that would silently put the outcome on the right-hand side: `ko/en_chunk_token_total` equal the D-04
token counts to **0.0**, and `ln(ko_tokens_per_byte) − ln(en_tokens_per_byte)` reproduces
`log_compression_penalty` — Outcome B itself — to 4.4e-16. Both column families are excluded from
both matrices. Neither outcome reconstructs from its own design.

`C7` confirms `M0 ⊂ M1 ⊂ M2 ⊂ M3` and `M0 ⊂ M1 ⊂ M2A` as strict subset ladders, and confirms
`function_morpheme_ratio` never co-occurs with `particle_ratio` or `ending_ratio` in any model —
`KOEN-TP-RS-001` §21's rule against entering a function ratio alongside its own components.

```
STRUCTURAL_AUDIT = PASS
```

---

## 4. SSOT conformance — read from the specification, not from the protocol

Each cited clause was extracted from `KOEN-TP-RS-001` (REDLINE) and compared to what the protocol
does with it.

| SSOT clause | what it says | protocol | verdict |
|---|---|---|---|
| §22 | 설명·가설검정 → *mixed-effects / fixed-effects regression*, role = coefficient + CI | fixed-effects OLS | **conformant** — fixed effects is an explicitly permitted member |
| §23.1 | "설명모형의 계수 추론은 전체 analysis cohort에서 수행하되 bootstrap 및 model diagnostics를 적용한다" | full cohort `N = 3,835,988`; HC1 + multiplier bootstrap companion; G5 diagnostics carried | **conformant** |
| §20.1 | "source 수가 적거나 특정 source가 특정 domain과 거의 완전히 결합되어 있으면 source fixed effect 또는 source-domain composite 사용" | 2 sources, one shared domain, `source_domain_cell` fixed | **conformant** — this is the clause's second branch, not a deviation |
| §20.1 final | "domain과 source가 완전 공선이면 둘의 독립계수를 동시에 해석하지 않는다" | `ID-03`: no pure source effect, no pure domain effect | **conformant** |
| §17.2 | "source cluster bootstrap은 source level 수가 충분할 때 보조로 수행한다" | cluster-robust refused at 2 / 5 clusters, reason recorded | **conformant** — the conditional is not met |
| §17.3 | p-value 단독 보고 금지 · effect size + CI 우선 · 큰 표본에서 significance보다 크기 | §3.4, §5.1, §6 | **conformant** |
| §19.2 | LR test on nested only · AIC/BIC · adjusted R² for fixed OLS · marginal/conditional R² for mixed · partial R² for the morphology block | all present; marginal/conditional R² correctly marked N/A (no random effect fitted) | **conformant** |
| §19.3 | M3 is a mechanism audit; a high R² is expected and is not a predictive win | §7.3 states exactly this | **conformant** |
| §21 | function ratio not with its components · script share reference category · **VIF만으로 feature를 자동 삭제하지 않는다** | M2/M2A alternatives; definitional references; §10 forbids VIF-only deletion | **conformant** |
| §29 | multiplicity list + mandatory regression-table fields incl. `[C012]` lineage commits | §6.1 and §6.2 reproduce both lists item for item | **conformant** |
| §30.3 | seeds: global · split · bootstrap · tuning · serving + `determinism_status` where determinism is not guaranteed | 3 frozen, 3 marked N/A with reasons, `determinism_status` per component | **conformant** |
| §24 | robustness list | §9 maps all nine SSOT items plus four registered candidates | **conformant** |

`SSOT_CONTRADICTION = NONE`

Two SSOT items are deferred rather than dropped, both under approved decisions: out-of-sample
metrics (§19.2) move to NB10 under `CR-FAST-G5-SPLIT-RELOCATION-01`, and the random-intercept
demonstration (§24 item 9) is registered as NB11 candidate #9. Neither is silently omitted.

---

## 5. Inference-method audit — layer B

### `A-M01` Estimator — **PASS**

Fixed-effects OLS on the full cohort is SSOT-permitted (§22, §23.1, verified above).
`source_domain_cell` is used as an observed-stratum fixed control under §20.1's second branch, and
§6.3 forbids reading its dummies as a pure source or pure domain effect. The `025-other` vs
`026-other` contrast is named only as a same-domain source-stratum contrast.

One point of craft worth recording. `83a686c` argued that "a two-level random intercept has no
estimable variance component" — an overclaim, since a two-level variance component is estimable in
principle even if badly determined. `81b6825` replaces it with a support-and-identifiability
judgement and states explicitly that no impossibility proof is offered or relied on, routing the
demonstration to NB11 candidate #9. The corrected form is what an auditor can check; the original
was not.

### `A-M02` HC1 — **PASS with `R-04`**

The protocol names HC1 ("White / Huber–Eicker, small-sample corrected"), states it is computed
exactly from the Gram plus one streaming accumulation of `Xᵀ diag(e²) X`, requires the SE type be
recorded in every table per §29, and marks it `DETERMINISTIC`. The robust covariance is specified
against the final exact design matrix, and `N = 3.8M` with `p ≤ 45` makes the sandwich exactly
computable with no subsampling.

**What is not written anywhere in the subject is the finite-sample scale itself.** Grep across both
protocol files returns no `N/(N−p)`, no `n/(n−p)`, and no explicit sandwich formula. HC1 has a
single standard definition — `(XᵀX)⁻¹ · [n/(n−p)] · Xᵀdiag(e_i²)X · (XᵀX)⁻¹` — and "small-sample
corrected" uniquely selects it against HC0, so this is **not** an invalid formula and therefore not
a HARD FAIL. It is an unwritten constant in a document that writes down everything else, and it is
the one number that separates HC1 from HC0 in a produced standard error.

Resolution, non-blocking: the NB09 run must record the literal scale factor it applied alongside the
`SE type = HC1` field. This auditor will verify at the result audit that the implemented scale is
`n/(n−p)` with `p` counting the intercept, by recomputing a standard error independently. No
protocol amendment and no remediation loop is required.

### `A-M03` Bootstrap — **PASS**

```
method   pair-level multiplier (wild) bootstrap        as required
weights  Rademacher                                    as required
B        2000, frozen, RQ1 precedent cited             as required
seeds    frozen in 03_NB09_SEED_REGISTRY_v001.json     as required
```

The seeds were **not** accepted on assertion. The stated rule — `uint32` big-endian of the first
four bytes of `sha256(seed_source_string)` — was reimplemented here and all three seeds reproduce:

```
PRE_NB09_PROTOCOL_v001|GLOBAL                        -> 2703484264   matches
PRE_NB09_PROTOCOL_v001|MULTIPLIER_BOOTSTRAP|OUTCOME_A -> 1222524615   matches
PRE_NB09_PROTOCOL_v001|MULTIPLIER_BOOTSTRAP|OUTCOME_B -> 1018984010   matches
```

and the precedent the registry claims — `sha256("NB08_RQ1_SSOT_CLOSEOUT_v001|SOURCE_STRATIFIED")` →
`aa49bab8…` → `2856958648` — reproduces and equals the value frozen in
`ssot_nb01/06_NB08_RQ1_SSOT_CLOSEOUT_v001.json` on `main`. The rule is therefore verified against an
already-closed artifact, not merely self-consistent.

`frozen_before_execution = true`, and the subject tree contains no result (§7), so the freeze
precedes any result by construction.

The protocol states explicitly that the procedure does **not** correct near-duplicate dependence:

```
PAIR_LEVEL_MULTIPLIER_BOOTSTRAP  !=  DUPLICATE_CLUSTER_DEPENDENCE_CORRECTION
```

with the same limitation restated in the §6.4 sentence mandatory on every table. That is the
required disclaimer, present without prompting.

Reproducibility caveat the protocol raises itself and this auditor endorses: the multiplier
bootstrap consumes weights in physical row order, so reproduction requires the same
`ORDER BY pair_id` ordering used at G5, and the run must **assert** it rather than assume it. This
will be checked at the result audit.

### `A-M04` Model comparison — **PASS**

```
ΔR²         = R²_full − R²_reduced                        exact match to the required definition
partial R²  = (R²_full − R²_reduced) / (1 − R²_reduced)   exact match
```

Nested comparisons only, and the three declared pairs are genuinely nested — verified structurally
by `C7`, not by inspection: `M1 ⊃ M0`, `M2 ⊃ M1`, `M3 ⊃ M2` as strict ordered-subset ladders.
`M2A − M1` is declared a pre-specified specification sensitivity (SSOT §24 item 7), never a
competing primary answer to RQ4; `M2A` sits outside the `M0→M1→M2→M3` primary chain and is reachable
only through the second `M0 ⊂ M1 ⊂ M2A` ladder.

§5.1's caveat is correctly stated as a power argument rather than an anti-testing rule: at
`N ≈ 3.8M` a nested test may reject a practically negligible increment, so significance never
overrides `ΔR²` / partial `R²` magnitude, and a negligible block is described as negligible whatever
its statistic says.

### `A-M05` Reporting — **PASS**

Effect magnitude is primary; individual coefficient p-values are explicitly demoted to "secondary
inferential detail" that may never rank predictors or decide model membership; §10 forbids
p-value-only reporting and p-value-ranked features; §7.1–§7.3 forbid causal readings of every
comparison; §7.5 restates the six globally forbidden claims of `VD-BASELINE-20260818-1520` §11 and
adds the byte-count refutation from the exact decomposition. `§6.1` reproduces the SSOT §29
mandatory field list including the `[C012]` lineage commits.

### `A-M06` `SM-01` — **PASS**

Primary M1 span unchanged (verified mechanically in §2). Both `script_type_count` and
`script_switch_count` are retained — they are **not** deleted on the basis of a post-G5 observation,
which is what SSOT §21's "VIF만으로 feature를 자동 삭제하지 않는다" requires. Individual coefficients
carry `no INDEPENDENT_SUBSTANTIVE_EFFECT`, only the block-level contribution is interpreted, and
every table reporting these terms must carry `SCRIPT_MIXING_BLOCK_INTERNAL_REDUNDANCY = YES`.
Alternative parameterization is registered as NB11 candidate #10.

`SM-01` sits entirely inside M1 and therefore appears on both sides of `M2 − M1`; the protocol says
so and it is correct — RQ4 is unaffected.

### `A-M07` `M3-01` — **PASS**

Primary M3 span unchanged (§2). RQ5 remains the `M3 − M2` block comparison. Raw chunk-count
coefficients carry no substantive interpretation and every M3 table must carry the §6.5 instability
warning quoting the measured 134.57 and 1,252.61. Chunk-density reparameterization is NB11
candidate #11.

The protocol carries forward, correctly attributed, the mechanism this auditor established at G5:
`chunk_count × mean_chunk_bytes = utf8_bytes` to 1.14e-13, so on the log scale
`ln k + ln(mean_chunk_bytes) = ln B`, and `ln B` is already spanned by M1. M3 stays full rank only
because `mean_chunk_bytes` enters on its native scale. §8.2 draws the binding consequence — any NB11
reparameterization that moves `mean_chunk_bytes` to the log scale **while retaining**
`ko/en_chunk_count_log` creates an exact identity and a rank deficiency, and must be rank-checked
before it is fitted. Recording that before NB11 rather than discovering it during NB11 is the right
call.

### `A-M08` Chronology — **PASS**

```
tree diff  9fbcf0c → 81b6825   ssot_nb09/01_PRE_NB09_PROTOCOL_v001.md
                               ssot_nb09/02_NB09_MODEL_MATRIX_CONTRACT_v001.json
                               ssot_nb09/03_NB09_SEED_REGISTRY_v001.json
```

Three protocol files. **No coefficient, standard error, R², ΔR², partial R², AIC, BIC or bootstrap
output exists anywhere in the subject tree.** A scan for result-shaped paths returns nothing. The
branch is based on `9d99e13`, whose tree equals `CANONICAL_TREE_SHA c80269a5…` — the §9 critical-path
rule, not drift.

```
RESULT_EXISTED_BEFORE_PROTOCOL_FREEZE = NO
INFERENCE_METHOD_AUDIT = PASS
```

---

## 6. Findings

### HARD FAIL — none

Checked against the full `VD-BASELINE-20260818-1520` §6 list: artifact/cohort mismatch (no — 5/5 and
exact), outcome or estimand changed (no — `Y_A`/`Y_B` unchanged from SSOT §18), unapproved primary
matrix change (no — mechanically identical), outcome leakage (no — 11 identities measured, both
outcomes non-reconstructible), rank deficiency (no — 0 in all five models), invalid inferential
formula or implementation (no — see `R-04` for the one unwritten constant), bootstrap parameter not
frozen pre-result (no — three seeds frozen and independently rederived), result before protocol
freeze (no — tree contains none), SSOT contradiction (none found across twelve clauses read from the
specification), false Director authority remaining (no — §0 denies any `RD-*` claim).

```
HARD_FAIL_COUNT = 0
```

### REVIEW — 4, none blocking

| id | finding | disposition |
|---|---|---|
| `R-01` | M3 fires both collinearity triggers — standardized condition number 134.57, max VIF 1,252.61, concentrated on `pair_log_size` and the chunk-scale terms | already governed: primary span retained, §6.5 instability warning mandatory, RQ5 read as `M3 − M2`, reparameterization → NB11 #11 |
| `R-02` | `SM-01` — `script_type_count ~ script_switch_count` Spearman 0.99935 (EN) / 0.99101 (KO), recomputed here at full cohort | already governed: both retained, no independent substantive effect, `SCRIPT_MIXING_BLOCK_INTERNAL_REDUNDANCY = YES` flag, → NB11 #10 |
| `R-03` | duplicate / paraphrase dependence is not corrected by any NB09 procedure | declared by the protocol itself; §6.4 sentence mandatory on every table; → NB11 #12 and PRE-NB10 grouping |
| `R-04` | the HC1 finite-sample scale is never written literally | **new** — the run must record the applied scale; this auditor recomputes an SE independently at the result audit. No amendment required. |

`R-01`–`R-03` are the review classes `VD-BASELINE-20260818-1520` §6 already names. None blocks
progression and none triggers a remediation loop.

### NOTE — 4

| id | note |
|---|---|
| `N-01` | §5 still opens "Director R0:" although §0 and §8 both label R0 as `VD-NB09-OPERATIONALIZATION-01` and §0 states no `RD-*` is claimed. Stale prose contradicted by the document's own governing section; it confers no authority. Worth a one-word edit whenever §5 is next touched. |
| `N-02` | the literal token `AUTHORITY_LABEL_FIXED = YES` does not appear. §0's table does the work substantively — the required content is present, only the token string is not. |
| `N-03` | `A-02` engineering debt is correctly addressed to Claude-A and B's root-cause diagnosis is confirmed: `scripts/g5_diagnostics_v001.py:262` calls `tel.update(n_rows // len(FAMILIES))` per family, giving `3,835,988 // 11 × 11 = 3,835,986`. Counter arithmetic only; no correlation or cohort figure is affected. To be fixed before the next heavy run. |
| `N-04` | `A-01` is resolved for future audits: the harness spec now forces `condition_number_includes_intercept`, `spearman_tie_handling` and `standardize_dummies` to be declared, and echoes them into every audit output. |

```
REVIEW_COUNT = 4
NOTE_COUNT   = 4
```

---

## 7. Verdict

The protocol changes no outcome, no estimand and no primary column; its structural claims were
recomputed from the canonical artifacts by a different numerical route and agree exactly; its SSOT
citations verify against the specification text; its seeds are frozen and independently rederivable,
including against an already-closed RQ1 artifact; its authority labels no longer claim Director
authority for anything; and no result exists anywhere in its tree.

```
PRE_NB09_PROTOCOL_AUDIT_PASS

AUDIT_SUBJECT_SHA        = 81b682527c587f64c817b7dab74f538f16bf9152
STRUCTURAL_AUDIT         = PASS   (C0–C7, 174 findings, 0 hard fail)
INFERENCE_METHOD_AUDIT   = PASS   (A-M01 … A-M08)
HARD_FAIL_COUNT          = 0
REVIEW_COUNT             = 4
NOTE_COUNT               = 4

NB09_EXECUTION_AUTHORIZED = YES
```

Per `VD-BASELINE-20260818-1520` §9, NB09 execution may begin from this audit commit without waiting
for `main` integration. Canonical integration proceeds serially and separately; if default-branch
publication is blocked by harness policy the correct report is
`MAIN_CANONICALIZATION_PENDING_OPERATIONAL_ONLY`, and `NB09_EXECUTION_AUTHORIZED` stays `YES`.

This audit certifies that the protocol is sound to execute. It certifies nothing about what NB09
will find, and no coefficient, comparison or claim is anticipated by anything in this document. The
next audit of this lane is a **result audit** on a new branch cut from B's NB09 result SHA.
