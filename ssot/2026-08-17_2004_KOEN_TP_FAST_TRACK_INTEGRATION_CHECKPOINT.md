# KOEN — Fast-Track Analysis Baseline: Integration Checkpoint

> **Decision**: `RD-FAST-G5-01`
> **Snapshot**: 2026-08-17 20:04 KST
> **Role**: Integration Steward (Claude-A)
> **Classification**: `SERIAL_INTEGRATION` / `BASELINE_PUBLICATION`
> **Scope**: integration only. No new science, no NB06, no NB07, no NB08.

---

## 1. Integrated SHAs

```
BASE_MAIN_SHA                     = 28d88ad40d85fa6067c6388fb8fbf8b2b6c5e329

B_CHECKPOINT_SHA                  = b2d6447da11c127be8d4e34549b770db3f35a6dd
A_CHECKPOINT_SHA                  = a127551ec346762ac1c79aa4007e957911d54ac5
EDA_V2_CHECKPOINT_SHA             = a4b9ca1a0a767b53c29ba0c104810b82c15b65bb

FAST_TRACK_DECISION_ORIGINAL_SHA  = 7400cd7e076cdea9bc95279fef8e20404eecd770
FAST_TRACK_DECISION_PATCH_SHA     = b98168f7554eb9931d0655385cb4a7024b2fff7c

V1_FROZEN_SHA                     = aabd068a4eef1245420ba4cc0a510ca4e27deae2
V1_MERGED                         = NO
```

Every remote ref was re-resolved immediately before merge and matched its expected value; no drift
was observed. Ancestry was verified rather than assumed: A and B are direct children of
`28d88ad`, EDA V2 is `28d88ad → adf1eaf → a4b9ca1`, and the decision branch is
`28d88ad → 7400cd7 → b98168f`.

### Merge order and results

Serial, `--no-ff`, in the order fixed by the directive. No conflict occurred at any step.

| step | input | merge commit |
|---|---|---|
| 5.1 | B checkpoint | `d63690d7c954d3d341c9200b53ab5774309a6782` |
| 5.2 | A checkpoint | `e999de54687611a631c5b98e23677a97ce4e0f4b` |
| 5.3 | EDA V2 | `12ad7db5c1e9a9cea0ed7923168f511262c66dd5` |
| 5.4 | Director fast-track decision | `efda80bf7ada07646e96bf7256d6a2e48cab9d46` |

### Transcription restoration applied before integration

`RD-FAST-G5-01` §14 had been persisted with a transcription defect, `NO_Gonsequence:`, produced by a
classification token being concatenated with the heading that followed it. The Research Director /
Main Vice Director confirmed the intended original, and it was restored on the decision branch at
`b98168f` as:

```
RECOVERED_CONCURRENCY_INCIDENT
NO_PERSISTED_RESEARCH_DATA_LOSS
NO_GATE_IMPACT

Operational consequence:
```

Classification `TRANSCRIPTION_RESTORATION` — `NO_SSOT_SEMANTIC_CHANGE`, `NO_NEW_CHANGE_REQUEST`. No
wording beyond the confirmed original was introduced and no other Director text was altered.

---

## 2. Gate board

```
G0  PASS / CLOSED
G1  PASS / CLOSED
G2  PASS / CLOSED
G3  PASS / CLOSED
G4  PASS / CLOSED

G5  OPEN / FAST-CLOSE AUTHORIZED
```

`MEASUREMENT_FOUNDATION_CLOSED_THROUGH_G4`. The frozen measurement layer is unchanged by this
integration: D-02 `dfae8e01…`, D-03 `0fe5bd74…`, D-04 `1c30e327…`, all at N = 3,835,988 with
pair-set hash `d9660d654ee449e4d0c23a0070225274`.

---

## 3. Current execution authorization

```
RQ1 / NB08 fast-path     AUTHORIZED
NB06 parallel path       AUTHORIZED  (design/code/pilot only)
NB07 drafting            AUTHORIZED
```

### Explicit non-blockers for RQ1

Per `RD-FAST-G5-01` §10, none of the following gates RQ1:

```
D-05
R1
G-ID
VIF / GVIF
source-domain modeling
near-duplicate clustering
predictive split
```

### RQ1 prerequisites

```
1. RQ1 cohort freeze
2. outcome freeze
3. inference protocol freeze
```

The inference protocol must be fixed before the resulting test output is inspected.

---

## 4. Engineering status carried into the baseline

```
R1_STATUS   = NOT_FIXED
NB06_STATUS = NOT_STARTED
```

`R1` — the memory guard samples only at entry and exit, so its recorded minima are not true minima.
Periodic in-loop telemetry is required before the next heavy population run. This blocks NB06's
full-population D-05 execution; it does not block NB07 drafting, NB08 inference, or G-ID.

`NB06` — no notebook, no `chunking.py`, no `CHUNK_O200K_BASE` artifact, manifest, config or test
exists. Design, code and pilot may begin immediately; the full D-05 run may not.

---

## 5. Non-canonical and frozen material

```
EDA V2   NON_CANONICAL / PRE-G5 EXPLORATORY / NOT GATE EVIDENCE
V1       HISTORICAL / IMMUTABLE / UNMERGED
```

EDA V2 is now present in `main` for archival and reproducibility only.
**Merge into main is not promotion to canonical evidence.** Its method caveats at `a4b9ca1` remain
controlling, and it may not be cited as Gate evidence.

V1 (`aabd068`) is not an ancestor of this integration; verified explicitly.

---

## 6. Concurrency policy

```
ONE AGENT PER WORKING TREE
NO SHARED-TREE BRANCH SWITCHING
```

This integration was performed in a dedicated isolated worktree created from `28d88ad`. The shared
project working tree was not switched, and no other lane's files were staged, moved or modified.

---

## 7. Hygiene

Files newly introduced into `main` by this integration:

```
docs/handoff/2026-08-17_1928_CLAUDE_A_PRE_ANALYSIS_CHECKPOINT.md
docs/handoff/2026-08-17_1929_CLAUDE_B_PRE_G5_RESEARCH_CHECKPOINT.md
docs/results/pre_g5_v2/KOEN_EDA_V2_CHECKPOINT.md
docs/results/pre_g5_v2/KOEN_EDA_V2_PRE_G5_DIAGNOSTICS.md
docs/results/pre_g5_v2/KOEN_EDA_V2_TRACEABILITY.md
docs/results/pre_g5_v2/KOEN_EDA_V2_V1_COMPARISON_MATRIX.md
docs/results/pre_g5_v2/README.md
notebooks/exploratory/EDA_preG5_fullstack_v2.ipynb
ssot/2026-08-17_1953_KOEN_TP_FAST_TRACK_ANALYSIS_ENTRY_DECISION_LOG.md
```

Checked against the base tree: `0` parquet, `0` xlsx, `0` `.runtime/`, `0` `Zone.Identifier`, and no
raw KO/EN sentence text newly committed.

---

## 8. Claim boundary

This integration establishes a Git baseline. It establishes no scientific result. Nothing here
asserts an RQ1 outcome, a causal domain or morphology effect, an RQ5 finding before D-05, or
predictive generalization before PRE-NB10 leakage control.
