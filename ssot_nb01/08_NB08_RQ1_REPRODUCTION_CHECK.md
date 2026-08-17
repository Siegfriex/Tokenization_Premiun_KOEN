# NB08 RQ1 — Independent Re-execution Check

> **Status**: verification record. Changes no protocol element, no cohort, and no reported value.
> **Protocol**: `NB08_RQ1_PROTOCOL_v001` · **Decision**: `RD-RQ1-FIRST-RESULT-01`

---

## 1. What was done

`notebooks/08_primary_inference.ipynb` was executed headless a second time, from the same committed
protocol, against the same D-04 artifact, with no edit of any kind between the two runs. Both runs
completed with exit code 0 and zero error outputs across all ten code cells.

```
run 1   2026-08-17 20:25:23 KST     (the committed evidence of record)
run 2   2026-08-17 20:39:48 KST     (this check)
```

## 2. Result

```
REPRODUCTION = EXACT
```

Every statistic, count, identifier and hash matched **bit-for-bit**. The comparison stripped only
wall-clock fields (`created_at_kst`, `runtime_sec*`), then compared the entire results object:

| quantity | run 1 | run 2 | identical |
|---|---|---|---|
| primary `median_logTP` | `0.28768207245178085` | same | ✔ |
| primary bootstrap CI | `[0.28768207245178085, 0.28768207245178085]` | same | ✔ |
| primary Wilcoxon `W` | `6405551963244.0` | same | ✔ |
| primary sign positive | `3,375,095` | same | ✔ |
| known-direction `median_logTP` | `0.28768207245178085` | same | ✔ |
| known-direction Wilcoxon `W` | `6237534311943.0` | same | ✔ |
| known-direction sign positive | `3,330,539` | same | ✔ |
| bootstrap seed | `969634713` | same | ✔ |
| bootstrap equivalence audit | `PASS` | `PASS` | ✔ |
| full results object (volatiles stripped) | — | — | **identical** |

Diff of the two notebook renderings: **zero** lines containing a statistic changed. The only
differences anywhere were execution counts, timestamps and runtimes:

```
runtime_sec.load            0.84  ->  0.77
runtime_sec.wilcoxon        0.64  ->  0.61
runtime_sec_primary        58.10  -> 59.34
runtime_sec_known_direction 57.88 -> 58.43
created_at_kst          20:25:23  -> 20:39:48
```

## 3. What this does and does not establish

**Establishes.** The pipeline is deterministic under the frozen seed: the bootstrap draws, the
signed-rank statistic and the sign counts are reproducible from the committed protocol without any
hidden state. The `969634713` seed derivation, which the notebook re-derives from its source string
at run time and asserts, held on both runs.

**Does not establish.** Determinism is not independent verification of correctness — both runs used
the same implementation. Correctness rests on the separate checks already recorded: the cohort
validation against the D-04 artifact, and the bootstrap equivalence benchmark against a direct
`np.median` reference on identical drawn indices (25 replicates, 0 mismatch).

## 4. Evidence of record

Run 1 remains the committed evidence. Run 2's outputs were discarded after comparison so the
recorded artifact keeps a single, stable provenance:

```
notebooks/08_primary_inference.ipynb        restored to the run-1 commit
ssot_nb01/04_NB08_RQ1_RESULTS_v001.json     restored to the run-1 commit
```

---

**Recorded**: 2026-08-17 KST, Claude-B (RQ1 Primary Inference Steward).
