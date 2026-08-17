# Claude-A — PRE-ANALYSIS Integration Checkpoint

> **Role**: Engineering / Canonical Notebook / Runtime / NB06 preparation
> **Purpose**: freeze A's engineering state as a Git reference point for NB06 / G5 / NB07 / NB08.
> **This is a checkpoint and handoff only.** No new analysis and no new feature was started.

---

## A. Timestamp

```
2026-08-17 19:28 KST
```

## B. Branch and worktree

```
worktree      /home/sieg/projects-wsl/Tokenization_KOEN        (main)
checkpoint    impl/pre-g5-checkpoint-a-20260817                 (created from 28d88ad)
```

Other worktrees observed and **not touched**:

```
/home/sieg/projects-wsl/Tokenization_KOEN_pre_g5_eda_v2   adf1eaf  [results/pre-g5-eda-v2-20260817]
/home/sieg/projects-wsl/Tokenization_KOEN_prelim_eda_v1   aabd068  [results/preliminary-eda-v1-20260817]
```

No branch checked out in another worktree was switched, reset or modified. No `reset --hard`,
`clean`, or `restore .` was run at any point in this checkpoint.

## C. Base `origin/main` SHA

```
28d88ad40d85fa6067c6388fb8fbf8b2b6c5e329
```

Matches the expected baseline.

## D. HEAD before checkpoint

```
28d88ad40d85fa6067c6388fb8fbf8b2b6c5e329   (HEAD == origin/main, ahead 0 / behind 0)
```

## E. Owned changed files

**A-owned uncommitted changes: none.**

```
git diff --name-only          (empty)
git diff --cached --name-only (empty)
```

Every piece of A's engineering work was already committed and pushed at or before `28d88ad`. The
only file this checkpoint adds is this handoff document.

Ownership classification of the working tree at checkpoint time:

| path | classification | note |
|---|---|---|
| `docs/results/pre_g5_v2/**` (4 files) | `OTHER_AGENT_OWNED` | EDA V2 lane, `run_id EDA_V2_PRE_G5_20260817T181311`, self-declared `NON_CANONICAL` |
| `notebooks/exploratory/EDA_preG5_fullstack_v2.ipynb` | `OTHER_AGENT_OWNED` | EDA V2 notebook (1.4 MB) |
| `notebooks/exploratory/EDA_representation_kiwi_o200k_casebook.ipynb` | `OTHER_AGENT_OWNED` | EDA lane casebook (1.8 MB) |
| `outputs/manifests/QC_MANIFEST_v001.json` | `UNKNOWN` | predates this session's reboot (mtime 10:22), P2 canonical run record |
| `ssot/HumanLebeled/KOEN_AUDIT_500_REJUDICATION_SUMMARY.md` | `UNKNOWN` | predates this session's reboot (mtime 11:26) |

## F. Completed engineering work

All of the following are committed on `main` at or before `28d88ad`.

| item | state | commit |
|---|---|---|
| D-02 SSOT §12.2 lexical-length conformance, `REP_FEATURES_v002` | COMPLETE | `287781a` |
| D-03 conformance restoration M1–M5 + bounded max-throughput Kiwi engine | COMPLETE | `9860d74` |
| Corrected morphology pilot v002 + Director N=100 audit pack | COMPLETE | `2d99c90` |
| Full-cohort Kiwi measurement, `MORPH_FEATURES_KIWI_v001` | COMPLETE | `6739658` |
| Full-cohort o200k measurement, `TOKEN_O200K_BASE_v001` | COMPLETE | `92dc07a` |
| Legacy reference census (`LEGACY_REFERENCE_AUDIT_PRE_G5_v001`) | COMPLETE | `40f015d`, closed at `111579f` |
| `src/tokenization_premium/lineage.py` fail-closed canonical registry | COMPLETE | `838a3ab` |
| Canonical NB03 reconciliation | COMPLETE | `838a3ab` |
| Canonical NB04 reconciliation | COMPLETE | `9d59a35` |
| Canonical NB05 reconciliation | COMPLETE | `8091b80` |
| Notebook regression tests (37) | COMPLETE | `8352b64` |
| TOKEN manifest lineage-note correction | COMPLETE | `1f2e323` |
| Director PRE-G5 closeout decision log `RD-20260817-G2G4-CLOSEOUT-01` | COMPLETE | `28d88ad` |

Verified outcomes carried forward:

- canonical notebook legacy **P0 = 0** (census re-run after reconciliation)
- NB03/NB04/NB05 execute headless with 0 errors and leave every canonical artifact byte-identical
- fail-closed lineage: no `exists()` guard, no pilot/synthetic/older-version fallback in any
  canonical notebook; `REBUILD_CANONICAL_ARTIFACT` defaults to `False`

## G. Incomplete engineering work

| item | status | note |
|---|---|---|
| **R1 — periodic memory/heartbeat sampling** | **NOT FIXED** | see §J |
| **NB06 regex chunk audit** | **NOT_STARTED** | see §J |
| `scripts/` versus SSOT §36 IA migration (R2) | DEFERRED by decision | `RD-20260817-G2G4-CLOSEOUT-01` §5; standing constraint: no new canonical logic in `scripts/` |
| mypy hygiene (R5) | OPEN | 75 errors across 8 files, concentrated in `scripts/`; non-blocking |
| NB07–NB13 | NOT_STARTED | none of these notebooks exist |

**Work in progress at pause time: none.** No implementation was mid-flight when this checkpoint was
taken; the previous task (micro-closeout) had completed and pushed.

## H. Canonical artifact SHAs

Re-verified from disk at checkpoint time, all four `CANONICAL_ARTIFACT_IDENTITY_VERIFIED`:

| artifact | SHA-256 | rows | cols |
|---|---|---:|---:|
| `data/registry/PAIR_REGISTRY_v002.parquet` | `95f523d11b0e8fcfd761dee949f082e9b4590b919801441fbcfa3426010bec52` | 5,652,925 | 69 |
| `data/registry/REP_FEATURES_v002.parquet` | `dfae8e01cd3fe2ca949d8754678e508203ad1a7aa6abea418008a33ac650d309` | 3,835,988 | 49 |
| `data/registry/MORPH_FEATURES_KIWI_v001.parquet` | `0fe5bd74e3993a7141c5c33ea78e71b2c66e3ecd296544bde2615acb43e50f7d` | 3,835,988 | 19 |
| `data/registry/TOKEN_O200K_BASE_v001.parquet` | `1c30e3276222dd94885ae4f79fc6ab5c45e4e26226de0afd91fc6b1f7d2c16e7` | 3,835,988 | 28 |

Sorted pair-set hash `d9660d654ee449e4d0c23a0070225274`, identical across D-02, D-03 and D-04.

## I. Tests actually run

```
pytest -q                                     171 passed, 0 failed   (4.21 s)
ruff check src/tokenization_premium tests scripts   All checks passed
```

No heavy population recompute was performed for this checkpoint.

## J. Remaining engineering risks

### NEXT HEAVY RUN BLOCKER — R1 periodic memory/heartbeat

```
R1_STATUS = NOT_FIXED
```

Evidence, not recollection:

- `grep` confirms `execute_morphology_run` and `execute_token_measurement_run` contain **no**
  `MemoryGuard` call at all; the guard is used only by `scripts/run_full_measurement.py`, twice per
  workload (before and after).
- The stored manifests record `memory_guard.sample_count = 2` for both full runs, with
  `min_mem_available_gib` 7.499 (morph) and 6.063 (tok).
- External 20-second monitoring during the concurrent run observed `MemAvailable` reaching
  **4.75 GiB**, below the RED threshold. The recorded minima are therefore not true minima, and the
  guard could not have aborted even if it had needed to.
- The substantive failure signal stayed clean: swap delta 0.25 MiB, 64 pages out, 0 pages in, no
  OOM, no writer error — which is why the artifacts are trustworthy despite the instrumentation gap.

Required before the next heavy population run: periodic sampling inside the execution loop, not just
at entry and exit.

### NB06

```
NB06_STATUS = NOT_STARTED
```

Evidence:

- `notebooks/06_regex_chunk_audit.ipynb` — absent
- `src/tokenization_premium/chunking.py` — absent
- no `CHUNK_O200K_BASE` artifact, manifest, config block or test anywhere
- every `D-05` string in the repository is either the unrelated Director decision id `D-RD-05` or
  prose stating that the regex chunk mechanism is out of the current module's scope

No design document, contract or pilot exists for NB06.

### Other

- **R2** `scripts/` IA debt — deferred by decision; four files carrying canonical research execution
  logic sit outside SSOT §36's information architecture, including the exact lineage that produced
  the adjudicated artifacts.
- **R3** 42,096 rows (1.0974%) with `eojeol_count = 1` carry the maximum `morpheme_density` and
  `particle_ratio`; `PLAUSIBLE_EXTREME`, a reporting caveat for NB07/NB08, not a defect.
- **R4** the `92dc07a` commit body says "29 columns"; the artifact, manifest and schema all carry 28.
  `REPORT_TYPO_ONLY` — do not propagate.

## K. Files explicitly NOT staged

```
docs/results/pre_g5_v2/**                                     OTHER_AGENT_OWNED (EDA V2)
notebooks/exploratory/EDA_preG5_fullstack_v2.ipynb            OTHER_AGENT_OWNED (EDA V2)
notebooks/exploratory/EDA_representation_kiwi_o200k_casebook.ipynb  OTHER_AGENT_OWNED (EDA)
outputs/manifests/QC_MANIFEST_v001.json                       UNKNOWN, predates reboot
ssot/HumanLebeled/KOEN_AUDIT_500_REJUDICATION_SUMMARY.md      UNKNOWN, predates reboot
```

Also excluded by `.gitignore` and never staged: `data/registry/*.parquet` (≈5.3 GB), `.runtime/**`,
all `*.xlsx` human workbooks, `*:Zone.Identifier` streams.

Staging was done with explicit paths only. No `git add .` and no `git add -A` was used.

## L. Common state at this checkpoint

```
G0  PASS / CLOSED
G1  PASS / CLOSED
G2  PASS / CLOSED
G3  PASS / CLOSED
G4  PASS / CLOSED

MEASUREMENT_FOUNDATION_CLOSED_THROUGH_G4
D-02 / D-03 / D-04  FROZEN
NB03 / NB04 / NB05  CURRENT
canonical legacy P0 = 0

B adjudication            441d5802bfebe178fd220d08b653c60dfad17faf
Director PRE-G5 closeout  28d88ad40d85fa6067c6388fb8fbf8b2b6c5e329
EDA V2                    NON-CANONICAL, separate branch/worktree
```

### Fast-track decision direction — recorded, not approved

The following are noted as the current direction of travel. **This checkpoint does not approve any
SSOT semantic change**, and none of these has been implemented:

- `sentence_type` has zero variance in the final cohort (single level `other`, N = 3,835,988) →
  realized-model exclusion **candidate**
- `logical_corpus` duplicates `source_id` → model exclusion **candidate**
- near-duplicate split work → deferred, pre-NB10 **candidate**
- NB06 / NB07 / NB08 parallel entry structure → **under review**

Each remains a candidate requiring a separate Director decision.

## M. Next recommended task

1. **Close R1** — periodic memory/heartbeat sampling inside the execution loop. This is the gating
   item for any further heavy population run.
2. **NB06 design and contract**, then a bounded pilot, following the same pattern used for D-03:
   contract → pilot → audit → authorized full run.
3. **G5 prerequisites** — identifiability (including the known 026 `특허정보원 ↔ 기술과학`
   biconditional), collinearity report, analysis cohort freeze, LR-01 split manifest freeze.

## N. No-new-work declaration

No new analysis, feature, notebook, artifact or population run was started for this checkpoint. The
only change is this document. No canonical artifact was read for measurement, regenerated or
modified; the four artifact SHAs in §H are unchanged from `28d88ad`.

**Claude-A does not merge to `main`.** Serial integration order is controlled by the Integration
Steward.

```
A_CHECKPOINT_PERSISTED
WAITING_FOR_SERIAL_INTEGRATION
```
