# KOEN Preliminary Multilayer EDA V1

```
Status:      HISTORICAL_PRELIMINARY_RESULTS_SNAPSHOT
Authority:   NON_CANONICAL
             SUBORDINATE_TO KOEN-TP-RS-001
Class:       PRELIMINARY_RESULTS_DISCOVERY_V1
```

| Item | Value |
|---|---|
| Execution date | 2026-08-17 |
| Execution window (KST) | `15:13:17.266596+09:00` → `15:14:34.484709+09:00` |
| `run_id` | `VIZ_CASEBOOK_20260817T151317` |
| Notebook | `notebooks/exploratory/EDA_representation_kiwi_o200k_casebook_v1.ipynb` |
| Base Git SHA (V1 execution context) | `2d99c906c7c94a9ce2ee2e0ff9dc01cf61998c3a` |
| Base commit subject | `feat(morph): corrected pilot v002 and director manual audit pack` |
| Notebook SHA-256 | `3852df21c8b36e099040d568309f21cc970c02ce4d8a8b9943c0c4e53264f2dd` |
| Byte-identical to source | `TRUE` |
| Branch | `results/preliminary-eda-v1-20260817` |

The base SHA above is **the value recorded inside the notebook's own reproducibility
record** (`REPRO["git"]["head"]`), independently re-verified against `git log` in this
repository. It is not taken from memory or from an external report.

---

## 1. What this branch is

This branch preserves, unmodified, the **first-pass multilayer EDA** that was executed
at the moment described above — that is, at the point where:

- **Representation (D-02)** was available as a validated **full-population** artifact
  (`REP_FEATURES_v002.parquet`, N = 3,835,988, 49 columns), and
- **Morphology (D-03)** and **o200k tokenizer measurement (D-04)** had **no
  full-population artifact yet**, so both were measured on a bounded, deterministically
  frozen **40-pair sample** (10 per populated domain).

It answers exactly one historical question:

> *Immediately before full D-03 / D-04 existed, what result axes and hypotheses were
> visible from the full Representation artifact plus a bounded morphology/o200k probe?*

## 2. What this branch is **not**

This snapshot is **not**:

- canonical `NB07` (`07_eda_and_decomposition.ipynb`)
- G2 / G3 / G4 / G5 evidence
- a publication-ready result
- a full-population multilayer result
- a draft of V2

`V1 ≠ V2 draft`. `V1 = immutable historical snapshot`.

No Gate verdict is issued anywhere in this branch. Where the notebook reports
roundtrip counts or exact-decomposition identity error, those are recorded as
**evidence for** the corresponding Gate conditions, never as a **verdict on** them.

## 3. Deliberate non-rebase

**This branch is intentionally not rebased to the latest research state.**

V1 is preserved to enable a controlled **V1 → V2 comparison** after full-population
D-03 and D-04 measurements become available.

Rebasing, cherry-picking later fixes onto this branch, or re-running the notebook
would destroy the only property that makes V1 useful: that it demonstrably did **not**
know what was discovered afterwards. Commits created after the V1 base — including
later narrative corrections, repository-hygiene fixes, the morphology audit request and
its Director adjudication, and the subsequent full-population D-03 / D-04 executions —
are deliberately **absent** from this branch's history.

Consequently:

- Do **not** rerun the notebook.
- Do **not** update its numbers.
- Do **not** backport full Kiwi / full o200k results into it.
- Do **not** merge this branch into `main`, and do **not** open a PR from it.

Knowledge acquired after the V1 execution is recorded **outside** the notebook, in
[`KOEN_EDA_V1_RETROSPECTIVE_CAVEATS.md`](KOEN_EDA_V1_RETROSPECTIVE_CAVEATS.md).

## 4. Contents of this freeze

| File | Role |
|---|---|
| `notebooks/exploratory/EDA_representation_kiwi_o200k_casebook_v1.ipynb` | The frozen artifact itself (byte-identical copy) |
| `docs/results/preliminary_v1/README.md` | This file |
| `docs/results/preliminary_v1/KOEN_EDA_V1_TRACEABILITY.md` | RQ ↔ estimand ↔ data ↔ notebook ↔ validation ↔ claim matrix |
| `docs/results/preliminary_v1/KOEN_PRELIMINARY_RESULTS_AXIS_V1.md` | The five result axes V1 is allowed to assert |
| `docs/results/preliminary_v1/KOEN_EDA_V1_RETROSPECTIVE_CAVEATS.md` | How to read V1 from a later vantage point |
| `docs/results/preliminary_v1/EDA_V1_FREEZE_MANIFEST.json` | Machine-readable freeze record |

The manifest contains **no newly computed numbers**. Every value in it is transcribed
from the reproducibility record already embedded in the notebook.

## 5. Evidence basis at V1

| Layer | Basis | Status recorded in notebook |
|---|---|---|
| **R** Representation | `REP_FEATURES_v002.parquet`, N = 3,835,988 (post-exclusion final cohort) | `FROM_FULL_ARTIFACT` |
| **M** Morphology | 40-pair recompute via canonical `morphology_features()` (Kiwi 0.23.2 / model 0.23.0, no custom dictionary) | `SAMPLE_RECOMPUTED_FOR_VISUALIZATION` |
| **T** o200k | 40-pair recompute via canonical `pair_token_measurement()` (o200k_base, tiktoken 0.13.0, Track A: no chat template, no special tokens) | `SAMPLE_RECOMPUTED_FOR_VISUALIZATION` |

Sample: 40 pairs, 10 per populated domain (`dialogue`, `general`, `other`,
`technology`), drawn once and shared by all three layers.
Frozen seed `2995913794` (D-RD-01 `auxiliary_seed`; no new seed was created).
Selection rule: `partition by domain, order by md5(pair_id || seed) then pair_id, rank <= 10`.
Pair-set SHA-256: `5b4393fb541c3a6dc347fa2422ed25fbfb384eed45a4b98b652ed3f85c8e0ac1`.

Because the pair set is content-addressed, a future full-population D-03 / D-04 run can
join on these exact `pair_id`s and perform a direct **equality check** against V1's
40-pair values. That is the intended V1 → V2 bridge.

## 6. SSOT / redline relationship

Authority documents are referenced **by path only**; they are not duplicated into this
branch.

- `ssot/Korean_English_Tokenization_Premium_Research_Spec_v1.0-2.pdf` (`KOEN-TP-RS-001`)
- `ssot/KOEN-TP-RS-001_v1.0_REDLINE_2026-08-16_1711KST.pdf`

Principal SSOT sections this snapshot connects to:

| § | Subject |
|---|---|
| §8 | Exact decomposition — $TP = \text{CodePointRatio} \times \text{ByteDensityRatio} \times \text{CompressionPenalty}$ |
| §5 / §5.1 | morphology $\neq$ regex chunking $\neq$ subword tokenization |
| §12 | D-02 Representation / D-03 Morphology / D-04 Token Measurement schemas |
| §16 | Core distributions, required visualization, extreme-case audit |
| §19 | Stepwise model comparison — morphology's explanatory role (M2 vs M1) |
| §20 | Source effect and identifiability (Gate G-ID) |
| §31 | Research Gates G0–G6 |
| §33 | Result-interpretation frame, Case A–E |
| §34 | Traceability matrix |

V1 supplies **inputs to** these sections. It closes none of them.

---

**Freeze status**

```
EDA_V1_HISTORICAL_SNAPSHOT_FROZEN
```
