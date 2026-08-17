# Claude-B — PRE-G5 Research Checkpoint

> **Snapshot**: 2026-08-17 19:29 KST
> **Role**: Research / Statistics / Gate Steward (Claude-B)
> **Purpose**: freeze the current forensic Gate state and the PRE-G5 realized-design findings as Git
> evidence, before any G5 statistics, model fit, NB07 or NB08 work begins.
> **Status**: no new analysis was started. This document records judgment only.

This checkpoint records **recommendations**, not approvals. Nothing in §F is an approved decision.
The Research Director and the formal G5 adjudication are the only authorities that can promote any
item here into a design decision.

---

## A. Git reality

```
base main (fetched)      28d88ad40d85fa6067c6388fb8fbf8b2b6c5e329   ← matches expected
origin/main              28d88ad40d85fa6067c6388fb8fbf8b2b6c5e329
checkpoint branch        research/pre-g5-checkpoint-b-20260817
```

`main` at the moment of this checkpoint:

```
28d88ad  docs(ssot): close G2-G4 and enter PRE-G5
1f2e323  fix(lineage): correct tokenizer artifact lineage note
111579f  audit(repo): close legacy census after notebook reconciliation
8352b64  test(notebooks): enforce canonical artifact fail-closed lineage
8091b80  fix(nb05): align canonical tokenizer notebook with full D04 evidence
9d59a35  fix(nb04): align canonical morphology notebook with full D03 evidence
838a3ab  fix(nb03): align canonical representation notebook with D02 v002
```

Working tree at branch creation carried only untracked files, all owned by other lanes
(`docs/results/`, `notebooks/exploratory/EDA_preG5_fullstack_v2.ipynb`,
`notebooks/exploratory/EDA_representation_kiwi_o200k_casebook.ipynb`,
`outputs/manifests/QC_MANIFEST_v001.json`,
`ssot/HumanLebeled/KOEN_AUDIT_500_REJUDICATION_SUMMARY.md`). None was staged.

Other branches observed and deliberately not touched: `impl/g2-g4-notebook-reconciliation-20260817`,
`results/pre-g5-eda-v2-20260817` (`adf1eaf`), `results/preliminary-eda-v1-20260817` (`aabd068`).

## B. Formal Gate state

```
G0 — Design Freeze              PASS / CLOSED
G1 — Data Integrity             PASS / CLOSED
G2 — Representation Integrity   PASS / CLOSED
G3 — Tokenizer Integrity        PASS / CLOSED
G4 — Morphology Integrity       PASS / CLOSED

MEASUREMENT_FOUNDATION_CLOSED_THROUGH_G4
Current formal phase: PRE-G5
```

| record | commit | document |
|---|---|---|
| B independent forensic adjudication | `441d5802bfebe178fd220d08b653c60dfad17faf` | `ssot/2026-08-17_1730_KOEN_TP_G2_G3_G4_FINAL_ADJUDICATION.md` |
| Director closeout / PRE-G5 entry | `28d88ad40d85fa6067c6388fb8fbf8b2b6c5e329` | `ssot/2026-08-17_1740_KOEN_TP_G2_G4_CLOSEOUT_AND_PRE_G5_ENTRY_DECISION_LOG.md` (`RD-20260817-G2G4-CLOSEOUT-01`) |

`441d580` is an ancestor of `origin/main` (verified), so the adjudication is on the canonical line.

## C. Evidence accepted

Frozen measurement layer, `N = 3,835,988`, sorted pair-set hash `d9660d654ee449e4d0c23a0070225274`
identical across D-02/D-03/D-04:

| dataset | artifact | SHA-256 | cols |
|---|---|---|---:|
| D-02 | `REP_FEATURES_v002.parquet` | `dfae8e01…c650d309` | 49 |
| D-03 | `MORPH_FEATURES_KIWI_v001.parquet` | `0fe5bd74…43e50f7d` | 19 |
| D-04 | `TOKEN_O200K_BASE_v001.parquet` | `1c30e327…7d2c16e7` | 28 |

Accepted as Gate evidence because it was independently recomputed by Claude-B from the physical
artifacts, not from any pipeline report: representation fields over 102,278 pairs (0 mismatch),
exact decomposition over all 3,835,988 pairs (max identity error 8.88e-16, 0 violations, stored
derived fields reproducing bit-identically), tokenizer identity against a live-rebuilt encoder
(7 single-valued hashes), decode **and** encode round-trip over 20,524 pairs (0 mismatch), token-byte
reconstruction (5,951 tokens, 0 mismatch, 173 genuine multi-byte splits), and every morphology count
and ratio re-derived from the stored `morpheme_sequence` over the full population (0 mismatch).

### C.1 Self-correction carried forward

Claude-B's §22 lineage fix at `441d580` added a correct `artifact_record_commit` to both full-run
manifests, but copied the **morphology-specific** `lineage_note` verbatim into the TOKEN manifest,
citing `MORPHOLOGY_CONFIG_SHA256` and `base_tag` / `classify_tag` / `features_from_morphs` /
`morph_features_schema` — none of which govern D-04. Commit `1f2e323` replaced it with
tokenizer-identity lineage. That correction is accurate and is accepted. The `artifact_record_commit`
values themselves were correct, and no artifact byte was affected in either edit.

## D. EDA V2 candidate evidence — NOT promoted

`results/pre-g5-eda-v2-20260817` (`adf1eaf`) holds full-population PRE-G5 diagnostics.
Per `RD-20260817-G2G4-CLOSEOUT-01` §3, **V2 is exploratory and non-canonical**: it may not be cited
as Gate evidence, may not replace a canonical notebook, may not write to `data/registry/`, and may
not be promoted into V1 without a separate Director decision.

The findings below are therefore recorded as **G5 formal-review candidates**, not as established
results. Claude-B has **not** independently revalidated them at this checkpoint; they carry V2's
non-canonical status until the formal G5 review inspects them against V1 artifacts.

| id | candidate finding | status |
|---|---|---|
| C-01 | `sentence_type` has one realized level — zero variance in the final cohort | candidate |
| C-02 | `source_id ↔ logical_corpus` bijective / structurally redundant | candidate |
| C-03 | `domain` / `source` / `direction` have uneven support; formal additive-model rank not yet determined | candidate, **unresolved** |
| C-04 | measurement cohort `N = 3,835,988` | **accepted** (this one is Gate evidence, §C) |
| C-05 | near-duplicate grouping is a predictive-leakage issue | candidate |
| C-06 | NB06 / D-05 has no formal completion | **accepted** (absence of an artifact is directly verifiable) |

C-04 and C-06 are marked accepted because each is verifiable against V1 or against the file system
without relying on V2 analysis. C-01, C-02, C-03 and C-05 are V2-sourced and remain candidates.

## E. Realized-design blockers

| id | blocker | nature | resolves at |
|---|---|---|---|
| E-01 | `sentence_type` is non-estimable in the realized cohort (single level) | design-matrix rank | G5 identifiability |
| E-02 | `source_id` and `logical_corpus` cannot both enter one design matrix | deterministic redundancy | G5 identifiability |
| E-03 | The 026 `특허정보원 ↔ 기술과학` biconditional (N = 359,910, exception 0) makes domain and source non-separable within 026 | SSOT §20.2 identifiability, already known | G5 identifiability (§20.2) |
| E-04 | Additive `source` + `domain` parameterization may be rank-deficient on the realized cells; not yet determined | **open question** | G5 identifiability |
| E-05 | No analysis cohort freeze exists | G5 prerequisite | G5 |
| E-06 | No train/hold-out split manifest under LR-01 | G5 prerequisite | G5 |
| E-07 | NB06 / D-05 regex chunk audit does not exist | SSOT §12.5, RQ5 mechanism line | before the tokenizer-mechanism line closes |

E-04 is stated as an open question, not a conclusion. Claude-B has not inspected the realized cell
composition at this checkpoint and does not assert rank deficiency.

## F. Recommended fast-track model decisions — **B RECOMMENDATIONS, NOT APPROVALS**

Each item below is a Claude-B recommendation for the formal G5 review to adjudicate. None is
approved, and none may be cited as a design decision until the Director or the G5 adjudication
promotes it.

| id | recommendation | rationale | status |
|---|---|---|---|
| **B-REC-01** | Remove `sentence_type` from the realized model | It is **non-estimable** — one realized level, zero variance. The reason is structural, **not** an observed outcome; no outcome was inspected to reach it. | RECOMMENDED |
| **B-REC-02** | `logical_corpus` and `source_id` must not coexist in one design matrix | They are bijective; including both makes the matrix rank-deficient by construction. Which one survives is a separate choice this recommendation does not make. | RECOMMENDED |
| **B-REC-03** | If additive `source` + `domain` parameterization proves unstable, treat the observed `source_domain` cell composite as the candidate primary descriptive/explanatory control | Conditional recommendation. It is contingent on E-04, which is unresolved. It is **not** a claim that the additive form is unstable. | RECOMMENDED — CONDITIONAL |
| **B-REC-04** | Near-duplicate split grouping is **not** required for NB07 descriptive, NB08 primary inference, or full-cohort NB09 explanatory inference; it **is** required before NB10 predictive evaluation | LR-01 leakage is an out-of-sample generalization concern. It does not affect descriptive summaries or full-cohort inference where no held-out prediction is claimed. | RECOMMENDED |
| **B-REC-05** | Formal G-ID should inspect the **actual reduced model matrix**, not every conceivable feature combination | Identifiability is a property of the matrix that will be fitted. Auditing hypothetical combinations inflates scope without improving the guarantee. | RECOMMENDED |
| **B-REC-06** | Remove deterministic redundancy and zero-variance features **before** running empirical VIF diagnostics | VIF on a rank-deficient matrix is undefined or misleading. Structural elimination must precede empirical diagnosis. Per D-RD-01 this remains "no automatic deletion" — removal here means structural non-estimability, not a threshold-triggered drop. | RECOMMENDED |

Cross-cutting caution attached to B-REC-01, B-REC-02 and B-REC-06: every removal proposed here is
justified by **non-estimability or deterministic redundancy**, never by an observed effect,
p-value, or outcome distribution. No outcome-dependent feature selection is proposed or implied.

## G. What may proceed immediately

- NB06 / D-05 regex chunk audit (E-07) — it is a measurement task on frozen D-04 inputs and does not
  depend on any G5 decision.
- Closing carried debt R1 (memory-guard periodic sampling), required before the next heavy run.
- Formal G5 preparatory work: identifiability inspection of the realized design matrix, collinearity
  report construction, analysis cohort freeze, split manifest freeze.
- V2 exploratory work in its own non-canonical lane.

## H. What still blocks G5

Per SSOT §31, all four remain open:

```
1. identifiability check (§20.2)      — E-01, E-02, E-03, E-04
2. collinearity report                 — VIF warning ≥ 5, severe ≥ 10, no automatic deletion (D-RD-01)
3. analysis cohort freeze              — E-05
4. train/hold-out split manifest freeze under LR-01  — E-06
```

The redundancy findings in the exploratory representation diagnostics are **not** a collinearity
gate result and must not be cited as one.

## I. What no longer needs to block NB07 / NB08

- **Measurement integrity.** G2/G3/G4 are closed; D-02/D-03/D-04 are frozen and independently
  verified. No further measurement validation is a precondition for descriptive or inferential work.
- **Near-duplicate split grouping.** Per B-REC-04 (recommendation, pending adjudication) this is an
  NB10 predictive-evaluation prerequisite, not an NB07/NB08 one.
- **The 28-vs-29 column question.** Resolved as `REPORT_TYPO_ONLY`; 28 is authoritative.
- **The morphology conformance defects M1–M6.** Closed and verified at full population.

These are unblocked **on measurement grounds only**. NB07 and NB08 remain blocked by the G5
prerequisites in §H, which this checkpoint does not relax.

## J. Exact claim boundaries

Permitted at this snapshot:

- G0–G4 are closed and the three measurement artifacts are frozen at the hashes in §C
- `TP` and its exact decomposition are measured over all 3,835,988 pairs with 0 identity violations
  and 100 % round-trip
- the corrected morphology mapping counts 28,492 irregular derivational affixes the previous mapping
  dropped
- `sentence_type` has one realized level in the final cohort, and `source_id ↔ logical_corpus` is
  bijective — **as V2 candidate findings awaiting formal G5 confirmation**, not as established design
  facts

Not permitted:

- that G5 has been entered, or that analysis readiness is established
- that any item in §F has been approved, decided, or adopted
- that any RQ has been answered — no test, interval, or effect estimate exists
- that the exploratory redundancy findings constitute a collinearity gate result
- that the additive source/domain model is rank-deficient (E-04 is unresolved)
- that the regex chunk mechanism has been examined — NB06 does not exist
- any causal language
- that V2 EDA output is Gate evidence

---

**Checkpoint closed**: 2026-08-17 19:29 KST, Claude-B (Research / Statistics / Gate Steward)
**Base main**: `28d88ad40d85fa6067c6388fb8fbf8b2b6c5e329`
**Merge authority**: Integration Steward only. Claude-B does not merge to `main`.

```
B_CHECKPOINT_PERSISTED
WAITING_FOR_SERIAL_INTEGRATION
```
