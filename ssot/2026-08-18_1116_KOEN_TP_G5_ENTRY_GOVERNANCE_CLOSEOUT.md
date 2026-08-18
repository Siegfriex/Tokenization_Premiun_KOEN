# KOEN — G5 Entry Governance Closeout

> Decision ID: RD-G5-ENTRY-GOVERNANCE-CLOSEOUT-01
>
> Authority: Research Director
>
> Parent Authority:
> KOEN-TP-RS-001
> RD-FAST-G5-01
> RD-SSOT-CANONICAL-RETURN-01
>
> Effective: 2026-08-18 11:16 KST
>
> Status: APPROVED
>
> Classification:
> GOVERNANCE_CLOSEOUT
> LINEAGE_INTEGRITY
> NO_NEW_RQ
> NO_NEW_PRIMARY_ESTIMAND
> NO_MEASUREMENT_REOPEN
> NO_DATA_REGENERATION
>
> Executor: Claude-A (Engineering / Reproducibility Executor)
>
> Base: `origin/main` @ `a31a4c27417b93567bb6e261b6225813aaa5f66e`
> (`merge: close Phase-4 regex chunk measurement`)

---

## 0. Why this document exists

Three governance items were left open when the previous engineering session froze.
None of them is a scientific question. All three are questions about whether the
canonical history states the truth about itself.

| # | open item | raised by |
|---|---|---|
| 1 | `RD-SSOT-CANONICAL-RETURN-01` was never merged into canonical `main`, so the decision that *requires* R1 periodic telemetry lived on a branch while the implementation that *satisfies* it lived on `main`. | `2026-08-17_2233_CLAUDE_A_NB06_D05_SESSION_FREEZE.md` §9.1 |
| 2 | Two memory-guard corrections in `0ae4c214…` changed how a run is graded, and were merged before an explicit Director classification existed. | same, §9.2 / §6.3 / §6.4 |
| 3 | The frozen NB08 RQ1 closeout records a SHA-256 for the primary result JSON that does not match the file it names. | this run |

This closeout resolves all three. It changes no measurement, no estimand and no result.

---

## 1. Canonical-return decision integration

### 1.1 What was wrong

```
decision   RD-SSOT-CANONICAL-RETURN-01
branch     docs/ssot-canonical-return-20260817
commit     e92701289edec339fc2f6eb7b7a8c1292190815e
file       ssot/2026-08-17_2042_KOEN_TP_SSOT_CANONICAL_RETURN_DECISION_LOG.md

git merge-base --is-ancestor e927012 origin/main  ->  exit 1   (NOT ANCESTOR)
```

The decision is the stated authority for, among others:

- §10 — the R1 execution-observability prerequisite that gated the D-05 full-population run;
- §11 / §12 — the G5 role and the realized-model contract that G5 entry is measured against;
- §21 — the Director verdict that closed the orchestration-heavy fast track.

Two later artifacts cite it as parent authority: `ssot_nb01/07_NB08_RQ1_CANONICAL_CLOSEOUT.md`
and the NB06/D-05 session freeze. Neither citation resolved inside canonical history.

### 1.2 What was done

The decision file was materialized onto this branch **from the original blob**, not retyped:

```
git checkout e92701289edec339fc2f6eb7b7a8c1292190815e -- \
  ssot/2026-08-17_2042_KOEN_TP_SSOT_CANONICAL_RETURN_DECISION_LOG.md
```

Verified identity:

```
source blob object id     c7fdc7bf10b7f4c0b4d5d5a65da87f0192519232
materialized blob id      c7fdc7bf10b7f4c0b4d5d5a65da87f0192519232
diff vs source            EMPTY
lines                     613
file sha256               7c5a4949c421bb718f9d2a4f413d9d20d3564cf98daa098e5bb2473c00ee2bdd

CONTENT_IDENTICAL = YES
```

All 21 Director sections, and the appended `Verification notes — Claude-A` block that the
original document already carried below the rule, are byte-for-byte unchanged. Nothing was
rewritten, reordered, summarized or re-dated.

### 1.3 Classification

```
DOCUMENT_MATERIALIZATION_ONLY
NO_SEMANTIC_CHANGE
NO_RENUMBERING
NO_REDATING
```

The decision's effective date remains **2026-08-17 20:42 KST**. Materializing it on
2026-08-18 does not change when it took effect; it changes only where it can be read from.

---

## 2. Memory-guard corrections — approval of record

### 2.1 Subject

```
commit  0ae4c214155c50860ac2a6f7390b08d1f398ee61
title   fix(runtime): keep the memory guard from misreporting healthy runs
status  already an ancestor of origin/main (a31a4c2)
```

**No code is modified by this closeout.** The code is already canonical. What was missing
was the Director classification of what that code change means.

### 2.2 Correction A — closing telemetry sample must observe, not abort

Previous behaviour: `RuntimeTelemetry.__exit__` took a final sample and could raise
`MemoryGuardAbort` from it.

Observed consequence: the first D-05 full-population run wrote, validated and promoted all
3,835,988 rows, and *then* aborted on the closing sample — destroying only the manifest.
The abort saved nothing and deleted evidence of a completed, correct run.

Corrected behaviour: the closing sample observes. The verdict is preserved in
`guard_abort_reason` and `worst_memory_status` rather than thrown away as an exception.

Rationale of record: the guard's contract is to protect execution **before and during** a
run. A run that has already finished cannot be protected by failing it.

### 2.3 Correction B — system-wide paging alone must not raise RED

Previous behaviour: the consecutive-swap-io rule escalated to RED whenever the
`pswpin` / `pswpout` deltas were greater than zero.

Observed consequence: those are **system-wide** counters in `/proc/vmstat` and therefore
count background paging by unrelated processes. 30 of 36 samples in a healthy run were
graded RED while every other RED rule stayed silent — minimum `MemAvailable` 6.33 GiB,
peak RSS 3.28 GiB, peak swap delta 19 MiB, 45.2 MiB of paging across 340 seconds.

Corrected behaviour: consecutive swap io escalates to RED only when the run's **own**
footprint has crossed the YELLOW threshold and is actually accumulating. This restores the
module's documented contract of judging against baseline rather than against ambient
system noise.

### 2.4 Director classification

```
APPROVED_ENGINEERING_GUARD_CORRECTION
NO_MEASUREMENT_SEMANTIC_CHANGE
NO_PRIOR_D05_RESULT_CHANGE
```

Explicitly recorded, and binding on later heavy runs:

- **Memory-exhaustion thresholds remain binding.** Neither correction relaxes the
  `MemAvailable` floor, the RSS ceiling, or the run-own swap accumulation rule. The
  pre-flight and in-flight abort paths are unchanged.
- **D-05 measurement values are unaffected.** The guard observes the run; it does not
  participate in chunking, encoding, reconstruction or any written column.
- **D-05 17/17 validation is unaffected.** `outputs/manifests/CHUNK_O200K_BASE_VALIDATION_v001.json`
  remains `validation_status: PASS`, artifact sha256
  `bfa98bd6cf7ee8b7254c469aed3e259ce43cc8f0529153347ca4c2c3fc1944ab`, N = 3,835,988,
  39 columns, pair-set `d9660d654ee449e4d0c23a0070225274`. This closeout does not touch
  that manifest.
- **Future heavy runs use the corrected semantics.** Telemetry grades emitted from this
  point forward are produced under corrections A and B. Historical grades recorded before
  `0ae4c214…` are not retroactively restated.

Reversal, if the Director later wants it, is confined to one conditional in
`src/tokenization_premium/memory_guard.py` and the `__exit__` try/except in
`src/tokenization_premium/telemetry.py`.

---

## 3. RQ1 lineage SHA — factual correction

### 3.1 The discrepancy

The frozen NB08 closeout records, as evidence of record, a SHA-256 for the primary result
JSON. That value does not match the file.

```
file                 ssot_nb01/04_NB08_RQ1_RESULTS_v001.json
recorded sha256      5daaa164061a0bbeda39ae823ce000a9e986c26baf9cc27c2f2c9479f0993562
actual sha256        768a3bccc7d5d081e90e6b2e1bf0dbc7230f416fce824698aa6d97f718cfbb59
```

### 3.2 The file did not change — the record was wrong

Established from history, not from assertion:

```
git log --follow -- ssot_nb01/04_NB08_RQ1_RESULTS_v001.json
  502bc128f6b5855f1648802cc990b715808f26f3   research(nb08): execute RQ1 primary token-premium inference
  (single commit; no later modification)

sha256 at 502bc12   768a3bccc7d5d081e90e6b2e1bf0dbc7230f416fce824698aa6d97f718cfbb59
sha256 at HEAD      768a3bccc7d5d081e90e6b2e1bf0dbc7230f416fce824698aa6d97f718cfbb59
sha256 on disk      768a3bccc7d5d081e90e6b2e1bf0dbc7230f416fce824698aa6d97f718cfbb59
```

The recorded value `5daaa164…` corresponds to **no committed version of the file, ever**.
It is a transcription error in the closeout metadata, not evidence of a mutated result.

```
RQ1_RESULT_BYTES_UNCHANGED = YES
```

### 3.3 What was corrected

Two reference sites, both metadata about the result rather than the result:

| file | site |
|---|---|
| `ssot_nb01/06_NB08_RQ1_SSOT_CLOSEOUT_v001.json` | `evidence_of_record.primary_result_json_sha256` |
| `ssot_nb01/07_NB08_RQ1_CANONICAL_CLOSEOUT.md` | §1 evidence-of-record block, `primary result JSON … sha256` line |

**`ssot_nb01/04_NB08_RQ1_RESULTS_v001.json` was not modified.** Correcting the pointer by
editing the thing it points at would have destroyed the very lineage this section repairs.

### 3.4 Classification

```
FACTUAL_LINEAGE_CORRECTION
NO_NEW_PRIMARY_ESTIMAND
NO_RQ1_REOPEN
RQ1_RESULT_BYTES_UNCHANGED = YES
```

Unchanged by this correction. RQ1 reports one primary estimand and, beside it,
sensitivity and robustness quantities computed on different denominators. They are
stated separately here so that no sensitivity figure can be read as the primary
result. Values below are read from `ssot_nb01/04_NB08_RQ1_RESULTS_v001.json`
(`primary`, `sensitivity_known_direction`) and `ssot_nb01/03_NB08_RQ1_PROTOCOL_v001.md` §1.

**PRIMARY — the RQ1 result of record**

```
RQ1 result          unchanged
RQ1 primary estimand
                    theta = Median(log_token_premium)
                    H0: theta = 0      H1: theta > 0   (one-sided, greater)
RQ1 primary cohort  PRIMARY_FINAL_COHORT
                    N = 3,835,988
                    pair-set hash d9660d654ee449e4d0c23a0070225274
RQ1 protocol        NB08_RQ1_PROTOCOL_v001, protocol cells modified = 0
RQ1 primary statistics
                    median log TP      0.28768207245178085
                    Wilcoxon W         6405551963244.0
                    sign  positive     3,375,095
                          negative       264,175
                          ties           196,718
                    bootstrap B        2000
                    bootstrap seed     969634713
RQ1 verdict         RQ1_PRIMARY_INFERENCE_PASS / NB08_RQ1_CLOSED
```

The pair-set hash above belongs to the primary cohort of N = 3,835,988. It is not
the identity of any sensitivity subset.

**KNOWN_DIRECTION_ONLY — sensitivity, not primary**

```
label               KNOWN_DIRECTION_ONLY
role                sensitivity cohort reported beside the primary result
N                   3,785,441
Wilcoxon W          6237534311943.0
sign positive       3,330,539
```

These figures are computed on a smaller cohort than the primary one and do not
replace any primary value.

**CONDITIONAL_NONZERO_SIGN_TEST — robustness, not primary**

```
label               CONDITIONAL_NONZERO_SIGN_TEST
estimand            P(Y > 0 | Y != 0)
null                P(Y > 0 | Y != 0) = 0.5
role                polarity robustness among non-zero observations only
```

Because zero-valued pairs are excluded from the denominator, this test infers a
conditional probability, not a marginal one. It is a robustness check on the sign of
the outcome. **It does not replace, restate or stand in for the primary estimand
`Median(log_token_premium)`.**

### 3.5 Fail-closed enforcement

A regression check was added inside the existing test architecture
(`tests/test_lineage.py`) so this class of error fails at CI rather than surviving into a
frozen record:

- the recomputed SHA-256 of `04_NB08_RQ1_RESULTS_v001.json` must equal the
  `evidence_of_record.primary_result_json_sha256` recorded in the `06` closeout JSON;
- the `07` canonical closeout prose must quote that same hash;
- the superseded value `5daaa164…` must not reappear anywhere under `ssot_nb01/`.

This is a lineage consistency check. It introduces no research logic, no new estimand and
no new artifact.

---

## 4. Science unchanged

This closeout is governance and lineage only. Explicitly:

```
NO NEW RQ
NO NEW PRIMARY ESTIMAND
NO DATA REGENERATION
NO D02/D03/D04/D05 REOPEN
NO RQ1 REOPEN
```

Also unchanged:

- primary unit — the KO/EN semantic-correspondence sentence pair `(x_i,KO, x_i,EN)`;
- primary tokenizer — `o200k_base`, Track A, raw text, no chat template, no special-token
  injection;
- primary outcome — `Y_i = log(TP_i)`, `TP_i = T_KO,i / T_EN,i`;
- the exact decomposition `logTP = logCR + logBDR + logCP`;
- the three-way distinction between linguistic morphology, tokenizer regex chunking and
  final subword tokenization;
- the paired observational — **not causal** — status of the analysis.

No parquet, no raw KO/EN text, no chunk string, no token-id array and no human audit
workbook is introduced by this commit.

### 4.1 Gate board after this closeout

| gate | status |
|---|---|
| G0 · G1 · G2 · G3 · G4 | CLOSED |
| RQ1 / NB08 | PASS / CLOSED — lineage reference corrected, result untouched |
| NB06 / D-05 | PASS / CLOSED |
| G5 | OPEN — analysis readiness; governance prerequisites now closed |
| NB07 · NB09 · NB10 · NB11 | NOT STARTED |

Per `RD-FAST-G5-01` §8 (`CR-FAST-G5-SPLIT-RELOCATION-01`), split-manifest and
near-duplicate leakage grouping remain relocated to **PRE-NB10** and are not a G5 blocker.
Per `RD-SSOT-CANONICAL-RETURN-01` §11, G5 requires cohort freeze, realized-model
identifiability, and collinearity/composition diagnostics on the actually planned model
matrices — and must not expand into an open-ended feature audit.

### 4.2 Executor boundary

Claude-A executed document materialization, lineage correction and test hardening only.
Claude-A did not fit a model, did not produce a coefficient, did not open G5, and did not
merge anything into `main`.

```
G5_ENTRY_GOVERNANCE_CLOSEOUT = EXECUTED
DO_NOT_MERGE_MAIN            = pending Claude-B audit and Director instruction
```
