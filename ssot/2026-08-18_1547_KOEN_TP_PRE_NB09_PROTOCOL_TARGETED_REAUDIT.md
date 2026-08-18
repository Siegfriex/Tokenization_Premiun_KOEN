# KOEN — PRE-NB09 Protocol · Targeted Re-Audit (`N-01` closure)

> Re-audit ID: `PRE_NB09_PROTOCOL_TARGETED_REAUDIT_20260818`
> Class: **TARGETED RE-AUDIT** — scope limited to one finding. Not a second protocol audit.
>
> Auditor: Claude-A
>
> ```
> RE_AUDIT_SUBJECT_SHA = 1dd6f753bf74dfa704c59a4b61373ec047c6ef2a
>                        fix(nb09-protocol): remove residual false Director label
> parent               = 81b682527c587f64c817b7dab74f538f16bf9152   ← the pinned audited subject
> prior audit          = 33c59d58a00202e961aa68a2f9e23fcf27033004   PRE_NB09_PROTOCOL_AUDIT_PASS
> canonical main       = 17e5a472854fee4bc7e281eece25913e197f5cbd
> executed             = 2026-08-18 15:47 KST
> ```
>
> This is an `A-*` agent finding, not an `RD-*` decision.

---

## 1. Scope

The full protocol audit at `33c59d5` returned `PRE_NB09_PROTOCOL_AUDIT_PASS` with
`HARD_FAIL_COUNT = 0`, and recorded as `N-01` that §5 still opened `Director R0:` although §0 and §8
both label R0 as `VD-NB09-OPERATIONALIZATION-01` and §0 states that no `RD-*` is claimed. It was
filed as a NOTE, not a blocker, precisely because the document's own governing section already
denied the attribution — stale prose cannot confer authority the same document explicitly disclaims.

The same residual was raised externally. B has pushed a targeted remediation. This re-audit checks
**only** whether that patch does what it says and nothing else.

```
NOT RE-RUN, CARRIED FORWARD FROM 33c59d5:
  C0 artifact / cohort / join / non-finite        PASS
  C1 predictor inventory                          PASS
  C2 outcome-leakage identities                   PASS
  C3 matrix rank                                  PASS
  C4 standardized condition number                PASS
  C5 VIF / GVIF                                   PASS
  C6 same-construct redundancy                    PASS
  C7 nested block consistency                     PASS
  A-M01 estimator · A-M02 HC1 · A-M03 bootstrap · A-M04 model comparison
  A-M05 reporting · A-M06 SM-01 · A-M07 M3-01 · A-M08 chronology     PASS
```

Re-running these would be waste, and the justification is mechanical rather than a judgement call:
§3 below shows the design-matrix contract and the seed registry are byte-identical across the patch,
so every quantity those classes measured is unchanged by construction.

---

## 2. The diff, in full

Parent is exactly the pinned subject `81b6825`. Two files, four hunks, seven changed lines — six of
which carry an authority token, and the seventh is the line-wrap continuation of one of them.

| # | location | before | after |
|---|---|---|---|
| 1 | `01` §0.2 defect table, row 3 | "sat alongside **Director dispositions** without distinction" | "sat alongside **the operational dispositions** without distinction" |
| 2 | `01` §5 lead sentence | "**Director R0:** primary evidence is …" | "**`VD-NB09-OPERATIONALIZATION-01` R0:** primary evidence is …" |
| 3 | `01` §9 lead sentence | "the two reparameterizations deferred **by the Director**" | "the two reparameterizations deferred by **`VD-NB09-OPERATIONALIZATION-01`**" |
| 4 | `02` `change_note` | "**Director ruling:** no post-hoc change to the primary M1 or M3 span" | "**`VD-NB09-OPERATIONALIZATION-01`:** no post-hoc change to the primary M1 or M3 span" |

Hunk 2 is the `N-01` site. Hunks 1, 3 and 4 are three further instances of the same class that B
found by sweeping rather than patching only the one that was reported — the right response to a
label defect, since fixing the reported instance alone would have left the same misattribution
standing in two other sections and in the machine-readable contract.

```
ONLY_AUTHORITY_WORDING_CHANGED = YES
```

---

## 3. Model and inference contract — unchanged, verified mechanically

`ssot_nb09/02_NB09_MODEL_MATRIX_CONTRACT_v001.json` was parsed at both SHAs and compared key by key.

```
differing top-level keys        ['change_note']       ← a prose field only

models                          identical
outcomes                        identical
reference_levels                identical
cohort                          identical
rank_at_g5 · condition_number_standardized_at_g5 · max_vif_at_g5    identical
identifiability                 identical
interpretation_restrictions     identical
primary_column_set_changed      False -> False
nb09_fitted                     False -> False
```

`ssot_nb09/03_NB09_SEED_REGISTRY_v001.json` is **byte-identical** — untouched by the patch. The
three frozen seeds, `B = 2000`, the derivation rule and `determinism_status` all stand exactly as
independently rederived at `33c59d5`.

`ssot_nb09/01` carries no change outside the three authority sentences: no estimator, standard-error,
bootstrap, model-comparison, claim-boundary, prohibition or precondition text moved.

```
MODEL_CONTRACT_UNCHANGED     = YES  (byte-identical apart from one prose field)
INFERENCE_CONTRACT_UNCHANGED = YES
```

---

## 4. `FALSE_DIRECTOR_ATTRIBUTION_COUNT`

Every occurrence of "Director" in all three patched files was enumerated and classified. Twelve
remain in `01`; the contract and the seed registry contain none.

| line | text | class |
|---|---|---|
| 39–40 | "…forbids promoting an agent recommendation or a Vice-Director operationalization into a Research Director decision" | states the rule |
| 45 | "**Research Director decision** `RD-*` \| *none is claimed by this protocol*" | explicit denial |
| 46 | "**Vice-Director operationalization** `VD-NB09-OPERATIONALIZATION-01`" | correct class label |
| 48 | `RD-FAST-G5-01`, `CR-FAST-G5-*`, `RD-SSOT-CANONICAL-RETURN-01`, `RD-G5-ENTRY-GOVERNANCE-CLOSEOUT-01` — "already Director-approved" | **true** — those decisions genuinely are Director-approved |
| 52–53 | "Nothing in the agent-level row has been approved by the Director. If the protocol audit or the Director rejects any of it…" | denial + hypothetical |
| 231 | "if the Director or an auditor wants the random specification demonstrated rather than judged…" | hypothetical future request |
| 541–543 | "These are Vice-Director operational interpretations … must never be relabelled `RD-*` without explicit user approval" | explicit denial |
| 682 | "then Director authorization to execute NB09" | **requests** authorization; does not claim it |

Not one occurrence attributes a disposition **in this protocol** to the Research Director.

```
FALSE_DIRECTOR_ATTRIBUTION_COUNT = 0
```

---

## 5. Verdict

The patch changes authority wording and nothing else. The design matrix, the reference levels, the
carried G5 diagnostics, the outcomes, the seed registry and every inference-method clause are
unchanged, so the sixteen audit classes that passed at `33c59d5` carry forward without re-execution.

```
PRE_NB09_TARGETED_REAUDIT_PASS

N-01                              CLOSED
ONLY_AUTHORITY_WORDING_CHANGED    YES
FALSE_DIRECTOR_ATTRIBUTION_COUNT  0
MODEL_CONTRACT_UNCHANGED          YES
INFERENCE_CONTRACT_UNCHANGED      YES
NEW_HARD_FAIL                     0

PRE_NB09_PROTOCOL_AUDIT_PASS      UPHELD at 1dd6f753bf74dfa704c59a4b61373ec047c6ef2a
NB09_EXECUTION_AUTHORIZED         YES  (unchanged; was never withdrawn)
```

`N-02` (the literal token `AUTHORITY_LABEL_FIXED = YES` is absent while §0 supplies the substance)
stands as recorded. `R-01` through `R-04` and `N-03`, `N-04` are unaffected by this patch and stand
as recorded at `33c59d5`; in particular `R-04` — the HC1 finite-sample scale is named but never
written literally — remains for verification at the NB09 result audit.

NB09 may execute from `1dd6f75` or from the prior audit commit; the science contract is identical
across both. Authorization was never withdrawn, so nothing was blocked while this re-audit ran.
