# KO-EN Tokenization Premium — G1 Entry / Midpoint Decision, Branch Reconciliation & SSOT Alignment Log

> **Snapshot:** 2026-08-16 16:16 KST  
> **Project:** Korean–English Tokenization Premium  
> **Authority SSOT:** `KOEN-TP-RS-001` — `Korean_English_Tokenization_Premium_Research_Spec_v1.0`  
> **SSOT status:** `FINAL DESIGN / PRE-ANALYSIS`  
> **Canonical project root:** `/home/sieg/projects-wsl/Tokenization_Premium`  
> **Canonical package namespace:** `src/tokenization_premium/` (`CR-001`, Research Director approved)  
> **GitHub:** `Siegfriex/Tokenization_Premium`  
> **Current formal state:** `G0 CLOSED / PHASE 1 IMPLEMENTATION IN PROGRESS / G1 NOT PASSED`  
> **Prepared by:** Main Vice Director / Senior Research Architect  
> **Final authority:** Research Director  
> **Supersedes operational current-state sections of:** `2026-08-16_1522_KOEN_TP_G0_CLOSEOUT_AND_G1_ENTRY_DECISION_LOG.md`  
> Earlier logs remain immutable historical snapshots.

---

# 0. Executive Adjudication

## 0.1 G0 remains closed

No new evidence reopens G0.

Canonical G0 release remains:

```text
main
f1b2a901b3bc9a9d759af0698bd0c308ec6e468b
```

G0 status:

```text
G0 Design Freeze                  PASS / CLOSED
Phase-0 Environment/Repro         PASS / RELEASED
Track B                           DEFERRED_NOT_EXECUTED
```

## 0.2 Phase 1 has formally started

The project is now inside:

```text
SSOT §37
Phase 1 — Data Contract
01_build_pair_registry.ipynb
```

Canonical Phase-1 implementation exists on `impl/g1-codex` and is actively executing on the full local raw corpus.

Current remote Codex snapshot:

```text
impl/g1-codex
0b401d169b651a90efdab3fae8feef772982275f
```

Direct Git comparison to released main:

```text
status: ahead
ahead_by: 3
behind_by: 0
```

Current branch content includes:

- `notebooks/01_build_pair_registry.ipynb`
- `src/tokenization_premium/registry.py`
- `src/tokenization_premium/schemas.py`
- `tests/test_registry.py`
- `.gitignore`
- `data/registry/.gitkeep`
- `pyproject.toml`
- `uv.lock`

The ongoing full-population streaming staging run is **reported execution evidence**, not yet a persisted final Phase-1 artifact.

Therefore:

```text
Phase 1 implementation      IN PROGRESS
G1 Data Integrity           NOT PASSED
```

---

# 1. Current Remote Branch Truth

Directly reverified remote refs:

| Branch | Current HEAD | Role | Vice Director state |
|---|---|---|---|
| `main` | `f1b2a901b3bc9a9d759af0698bd0c308ec6e468b` | released G0 base | FROZEN RELEASE |
| `integration/g1` | `f1b2a901b3bc9a9d759af0698bd0c308ec6e468b` | G1 integration | EMPTY / BASE ONLY |
| `research/g1-claude` | `f7dd12d690b1b1ec6dbb757a3f654d949dd7d9d0` | canonical G1 research/data contract | READY TO INTEGRATE |
| `data/g1-recon` | `617f6fdaf994f9496d97e15621a6921d49451015` | independent ingest oracle | READY TO INTEGRATE |
| `evidence/g1-perplexity` | `cc535b3b8299a1119d96456bad784cbcb963c614` | official-source provenance evidence | READY TO INTEGRATE |
| `eda/g1-support` | `2e11112eb4b545d76c20f09d7071e7b477e09985` | sanitized auxiliary EDA/evidence | HOLD — PATH PORTABILITY FIX |
| `impl/g1-codex` | `0b401d169b651a90efdab3fae8feef772982275f` | D-01 implementation | RUNNING / DO NOT MERGE YET |

Historical branches that must not be merged wholesale into G1:

- `research/g1-prep-claude`
- `data/g0-aihub-recon`
- `eda/g0-raw-notebooks`
- `evidence/g0-perplexity`
- all G0 agent branches

---

# 2. Immediate Branch Traffic Decision

## 2.1 Merge now

The following three branches are canonicalized from the released G0 `main` and occupy non-overlapping ownership domains:

```text
research/g1-claude@f7dd12d...
data/g1-recon@617f6fd...
evidence/g1-perplexity@cc535b3...
```

Decision:

```text
MERGE INTO integration/g1 NOW
```

Recommended order:

1. research/g1-claude
2. data/g1-recon
3. evidence/g1-perplexity

Reason:

- research contract/config becomes the semantic base
- data-recon oracle becomes the independent ingest expectation
- external provenance evidence is additive and does not alter approved Director roles

No main merge.

## 2.2 Do not merge EDA support yet

`eda/g1-support@2e11112...` is privacy-sanitized and independently rebuilt from released main, but the four executable notebooks currently hard-code:

```text
/home/sieg/projects-wsl/Tokenization_Premium/.agent_worktrees/raw-eda-g1
```

as `WORKTREE_ROOT`.

This means a notebook merged into `integration/g1` may continue writing output into the old EDA worktree rather than the currently checked-out repository.

Decision:

```text
EDA privacy / content safety     PASS
EDA execution portability       FAIL / FIX REQUIRED
EDA integration                 HOLD
```

Required correction:

- resolve current repository root from `tokenization_premium.paths.PROJECT_ROOT` or equivalent package-root discovery
- make output paths relative to the current repository/worktree
- keep raw root separately configurable (`TOKENIZATION_PREMIUM_RAW_ROOT`)
- fresh-kernel rerun all four notebooks
- regenerate artifact hashes
- push one follow-up commit
- only then merge `eda/g1-support`

## 2.3 Do not merge Codex yet

Codex is actively running the full 5.65M-row ingest.

Current remote commit contains implementation code but no completed canonical Phase-1 result artifact.

Decision:

```text
impl/g1-codex merge = WAIT_FOR_FINAL_RUN_AND_COMMIT
```

Codex is merged last, after:

- full run completes
- final pair/source registry hashes exist
- full-table oracle passes
- notebook fresh-kernel execution is persisted
- branch is clean
- final commit/push is reported

---

# 3. Canonical G1 Research Contract State

`research/g1-claude@f7dd12d...` is accepted as the implementation-ready semantic contract.

## 3.1 D-RD-05 Source Portfolio

```text
025:
  candidate tier = A
  role = PRIMARY_BACKBONE
  primary eligible = true
  provenance closure = PENDING_OFFICIAL_SCHEMA_AND_RELEASE_LINK

026:
  candidate tier = A
  role = PRIMARY_DOMAIN_SUPPLEMENT
  primary eligible = true
  provenance closure = PENDING_OFFICIAL_SCHEMA_AND_RELEASE_LINK

Legacy:
  tier = null / UNASSIGNED
  role = SENSITIVITY_ONLY
  primary eligible = false
  provenance closure =
    PARTIAL_OFFICIAL_CONSTRUCTION_CONFIRMED_FIELD_AND_RELEASE_LINK_PENDING
```

D71693 remains outside current corpus.

## 3.2 D-RD-06 Translation Direction

```text
025    KO_TO_EN / EN_TO_KO
026    KO_TO_EN
Legacy UNKNOWN
```

## 3.3 D-RD-07 Domain Mapping

Approved top-level mapping remains frozen.

Raw domain/subdomain labels are never overwritten.

## 3.4 D-RD-08 Primary cohort policy

No convenience cap.

Final numeric N is realized after QC/dedup.

## 3.5 D-01 field contract extensions

Current G1 config freezes:

- `sentence_type`: source value if available, else `other` + provenance status
- `*_text_nfc`, `*_text_analysis`: nullable at Phase 1
- `normalization_status=NOT_GENERATED_PHASE1`
- Phase 2 writes a new registry version rather than silently mutating frozen Phase-1 registry
- `pair_quality_status=review` in Phase 1
- `qc_stage_status=PENDING_PHASE2`
- `pair_quality_score=null`
- `pair_version=v001`
- duplicate representative = lexicographic minimum `pair_id`
- representative is provenance pointer only
- semantic conflict flags are separate

This is a legitimate operational elaboration of SSOT D-01 and Phase 1/2 boundaries, not a new research estimand.

---

# 4. Independent G1 Ingest Oracle

`data/g1-recon@617f6fd...` is accepted as independent implementation oracle.

## 4.1 Exact expected logical population

```text
025      2,700,345
026      1,350,162
Legacy   1,602,418
Total    5,652,925
```

## 4.2 Physical ingest contract

Physical files observed:

```text
23
```

Canonical ingest allowlist:

```text
16
```

Aliases / containers excluded from canonical ingest:

```text
7
```

The contract explicitly prevents recursive double ingest.

Naive recursive read would inflate:

```text
025 → 5,400,690
026 → 2,700,324
```

before additional archive duplication.

## 4.3 Duplicate / identity oracle

Expected raw exact-pair values:

```text
025 duplicate-after-first            214,252
025 duplicate groups                  93,823

026 duplicate-after-first                 44
026 duplicate groups                      44

025 cross-direction shared groups     50,511
TRAIN↔VALID shared distinct pairs      25,247

025↔026                                    0
025↔Legacy                                35
026↔Legacy                                 1

Legacy News(2)↔Culture                 2,469

025 sn dataset-wide collision              0
026 sn dataset-wide collision              0
```

These are independent expectations, not values Codex may redefine to make its own implementation pass.

---

# 5. Official Provenance Evidence

`evidence/g1-perplexity@cc535b3...` is accepted as current official-source evidence.

Evidence layers remain separated:

```text
WEB/OFFICIAL
LOCAL_REPORTED_GIT_EVIDENCE
UNVERIFIED_LINK
```

Current closure:

```text
D71265  OPEN
D71266  OPEN
D87     OPEN
```

This does not automatically overwrite Director-approved source roles.

Forbidden inference remains:

- `mt` = confirmed MT draft
- `ko/en` = confirmed human-final translation
- `ko_original/en_original` semantics inferred from names
- `source_language/target_language` officially proven direction fields
- `license="open"` = redistribution permission
- Legacy local 1,602,418 = proven exact D87 release

D87 official 2019 construction/QA evidence is stronger than before, but release-link and local-field semantics remain open.

---

# 6. Deep Audit — Four Sanitized Notebooks

Uploaded notebooks were inspected structurally and byte-matched to `eda/g1-support`.

## 6.1 Byte identity

Current remote hash manifest and uploaded files agree exactly:

```text
AIHUB_LOCAL_RECON_EVIDENCE_EXPORT_20260816.ipynb
SHA-256:
2b55f2d007fb8f6e1ea518b0ec3d026cd4d993c982d90c756dcb0a32d33dc6c7

EDA_RAW_AIHUB_025_G1_SANITIZED.ipynb
SHA-256:
217335e297ee08b27295115824b1b1ef2d474492bfeca68691862fc24c9a7de1

EDA_RAW_AIHUB_026_G1_SANITIZED.ipynb
SHA-256:
d2ead7c01f3b4e955f536378124e3634aaa6223f014ac1d3cfbce71eb3f963aa

EDA_RAW_LEGACY_KO_EN_XLSX_G1_SANITIZED.ipynb
SHA-256:
bbd702bc3bed78ad77625a0ef1d22ec6888a7cf68e5f6a9dd564ab260b5a5b21
```

The earlier reported evidence-notebook SHA `d3e2df...` is therefore a stale/intermediate snapshot, not the current remote artifact identity.

## 6.2 Execution state

Evidence notebook:

```text
cells           36
code cells      17
execution       1..17
errors          0
```

Each sanitized raw EDA notebook:

```text
code cells      5
execution       1..5
errors          0
```

## 6.3 Privacy / raw-text findings

The current notebooks do not render raw KO/EN sentence examples.

The raw EDA support module explicitly:

- uses KO/EN text transiently for aggregate counters
- uses a random-salted in-memory BLAKE2b-128 key only for equality grouping
- does not persist duplicate hashes
- does not persist raw previews
- rejects raw columns in exported aggregate frames
- keeps URLs/email/phone-like category values out of safe category exports

Result:

```text
raw-text output exposure in current sanitized notebooks:
NOT OBSERVED

raw sentence/sample CSV export:
NOT OBSERVED

persistent pair/text hashes in sanitized EDA:
NOT OBSERVED
```

## 6.4 Scope integrity

No actual tokenization, morphology inference, or statistical inference is performed by the four notebooks.

String matches such as "tokenization" arise from project/path/narrative labels.

## 6.5 Portability defect

All four notebooks are bound to an absolute EDA-agent worktree path.

This is the sole integration-blocking defect currently found in the sanitized notebook set.

---

# 7. Public Old-EDA Branch Remediation

Historical branch:

```text
eda/g0-raw-notebooks@4e56fdbc...
```

still contains raw KO/EN preview artifacts in public Git history.

Sanitized G1 work does not depend on those blobs and does not port them.

Status:

```text
OPS-DR-01
AWAITING RESEARCH DIRECTOR APPROVAL
```

Recommended action:

```text
APPROVE sanitation/removal of old EDA remote branch reference,
with main/integration/G0/G1 canonical branches explicitly protected.
```

This is repository hygiene and distribution-risk management, not a research-design change.

---

# 8. SSOT Page-by-Page Alignment

Physical PDF page numbers below are 1-based PDF pages.
The document footer is one page lower on the main body because of front matter.

## 8.1 PDF p.9 (footer 8) — §6 Research Questions

SSOT fixes:

- §6.1 RQ1: `Median(log TP)`
- §6.2 RQ2: exact structural decomposition
- D-01: use log(TP), not absolute token difference, for primary test

Current state:

```text
FROZEN in G0
UNCHANGED
```

No Phase-1 decision modifies estimand or RQ.

## 8.2 PDF p.10 (footer 9) — §6.3–6.7 and §7

SSOT fixes:

- surface features
- morphology incremental value
- tokenizer mechanism audit
- heterogeneity
- serving track
- paired analysis unit

Current state:

- RQ1–RQ6 intact
- RQ7 retained but `DEFERRED_NOT_EXECUTED`
- pair registry is being constructed to instantiate §7.1 analysis-unit lineage

## 8.3 PDF p.12 (footer 11) — §9 Data Design

SSOT defines:

- §9.1 sample-scale guidance
- §9.2 domain/sentence type/direction/source/length strata
- §9.3 source Tier A/B/C hierarchy

Added operational decisions:

- D-RD-05 maps current corpora to source roles
- D-RD-07 maps actual raw domains to canonical taxonomy
- D-RD-08 resolves N as QC-realized rather than pre-capped
- `provenance_closure_status` is added as an orthogonal operational field

Important:
`provenance_closure_status` does not redefine Tier A/B/C.

## 8.4 PDF p.13 (footer 12) — §10 Pair Quality Control

SSOT defines:

### §10.1 hard exclusion
- null/empty
- exact duplicate
- clear language-ID failure
- markup-dominant
- control/zero-width anomalies
- decoder/tokenizer round-trip failure
- clear semantic mismatch

### §10.2 soft flags

### §10.3 semantic QC
- source metadata
- multilingual similarity/alignment
- 300–500 manual audit
- 2/1/0 rubric

Current Phase-1 rule:

- raw registry does not silently exclude parseable duplicates
- duplicate group membership is recorded
- `pair_quality_status=review` until Phase 2

This preserves 01/02 lineage.

## 8.5 PDF p.14 (footer 13) — §11 and §12.1 D-01

SSOT D-01 fields are the canonical pair registry contract.

Current G1 additions are auxiliary/operational:

- `source_record_id`
- `raw_locator`
- `duplicate_group_id`
- `domain_raw`
- `subdomain_raw`
- `source_provenance_raw`
- upstream split provenance
- normalization status
- QC-stage status
- conflict flags
- representative pointer

These fields do not replace SSOT D-01 fields.

## 8.6 PDF p.22 (footer 21) — §20.2 Identifiability Gate

SSOT requires:

- source×domain
- source×direction
- condition number
- VIF
- low-variance checks
- pairwise correlations

Current local evidence adds a concrete known case:

```text
026:
source_provenance_raw=특허정보원
iff
domain_raw=기술과학
N=359,910
```

This is not yet a model redesign.
It is a future G-ID hard warning.

## 8.7 PDF p.23 (footer 22) — §23 Leakage Rule LR-01

SSOT says duplicate/paraphrase clusters cannot cross train/test.

Current G1 contract therefore preserves upstream AIHub train/validation only as provenance.

Future predictive split will be project-defined and duplicate-cluster-safe.

## 8.8 PDF p.27–28 (footer 26–27) — §30 Reproducibility and §31 Gates

§30.2 requires release lineage:

- raw file hash
- source registry
- transformation manifest
- rejected pair list
- accepted pair hash
- feature/token/morphology hashes
- config
- Git SHA

Current Phase-1 implementation directly implements the first lineage layer.

§31 G1 requires:

- pair IDs unique
- null/duplicate checks
- LID/QC pass rate
- source/license metadata complete

Current status:

```text
pair ID implementation        RUNNING
null/duplicate oracle         READY
source/license contract       READY
LID/QC pass-rate closure      NOT YET SATISFIED
```

Therefore `01_build_pair_registry` engineering PASS will not by itself authorize a Vice Director G1 PASS unless the LID/QC condition is explicitly satisfied.

## 8.9 PDF p.31–32 (footer 30–31) — §36 IA and §37 Notebook Order

SSOT fixes:

```text
Phase 1:
01_build_pair_registry.ipynb
- source ingest
- stable pair ID
- metadata schema
- raw hash

Phase 2:
02_normalize_and_qc.ipynb
- NFC/analysis text
- anomaly flags
- duplicate/LID/parallel quality
- QC flow table
```

Current implementation matches Phase-1 duties.

However §31 G1's requirement for `LID/QC pass rate` overlaps with §37 Phase-2 duties.

This is an SSOT sequencing ambiguity and must not be silently papered over.

See `CR-003 candidate` below.

## 8.10 PDF p.34 (footer 33) — §39 Pre-analysis Checklist

Already materially satisfied:

- RQ / estimand freeze
- tokenizer implementation freeze
- morphology analyzer/POS freeze
- pair QC rubric freeze
- tokenizer environment roundtrip

Not yet satisfied:

- completed source registry/license note in canonical G1 artifact
- Unicode normalization tests on accepted corpus
- exact decomposition on accepted corpus
- morphology sample audit on corpus
- identifiability audit PASS
- analysis cohort hash
- holdout manifest
- figure/table IDs

Therefore the project is still well before formal analysis readiness.

---

# 9. SSOT Sequencing Ambiguity — CR-003 Candidate

## Problem

SSOT §31 G1 (`PDF p.28`) requires:

```text
LID/QC pass rate 보고
```

but SSOT §37 (`PDF p.32`) assigns:

```text
duplicate/LID/parallel quality
```

to Phase 2 `02_normalize_and_qc.ipynb`.

The project operating rule also expects notebook/Phase/Gate traceability.

If ignored, two invalid outcomes are possible:

1. declare G1 PASS after notebook 01 without LID/QC pass rate; or
2. run Phase 2 formally while G1 is still failed/unclosed.

Neither should happen silently.

## Recommended resolution

Do not alter Phase-1 registry semantics or execute Phase-2 exclusion inside notebook 01.

Recommended clarification:

```text
D-RD-09 / CR-003 candidate:

01_build_pair_registry completes D-01 and a non-mutating
G1 data-integrity diagnostic report.

02_normalize_and_qc remains authoritative for normalization and
actual accepted/review/rejected QC disposition.

Formal G1 PASS is adjudicated only when the required LID/QC pass-rate
artifact exists; until then Phase 1 may be ENGINEERING COMPLETE but
G1 remains OPEN.
```

A precise implementation choice for LID/QC diagnostic must be frozen before G1 is declared PASS.

No SSOT text has yet been amended.

---

# 10. Current Codex Implementation Assessment

Current `01_build_pair_registry.ipynb` remote snapshot is structurally strong.

Observed design:

- exact 16-file allowlist
- raw SHA audit
- streaming ingest
- explicit Arrow schemas
- provenance-based `pair_id`
- raw SHA-256 `duplicate_group_id`
- ignored >GB staging path
- DuckDB out-of-core group resolution
- deterministic final ordering
- representative `min(pair_id)`
- full-table independent oracle checks
- source registry
- artifact manifest
- Vice Director-owned final G1 adjudication

Data-heavy registry artifacts are protected by `.gitignore`:

```text
data/interim/**
data/registry/**
```

so the >1GB raw-containing registry is not intended for public Git commit.

Current implementation gap for formal G1:

```text
no explicit LID/QC pass-rate gate artifact is present in the
current 01 notebook snapshot.
```

This is not a reason to abort the active full ingest.
It is a Gate-closeout issue to resolve immediately after D-01 engineering completion.

---

# 11. Immediate Execution Plan

## Wave 1 — now

1. Merge research/g1-claude into integration/g1.
2. Merge data/g1-recon.
3. Merge evidence/g1-perplexity.
4. Do not merge EDA.
5. Do not merge Codex.

## Wave 2 — parallel

EDA:
- fix path portability
- rerun 4 notebooks
- update hash manifest
- push

Claude:
- read-only inspect current Codex D-01 implementation vs frozen contract
- draft CR-003 / D-RD-09 gate-sequencing resolution
- do not modify SSOT without Director approval

Data Recon:
- prepare independent registry audit runner that consumes final Codex pair/source registry without changing implementation or expected values

Perplexity:
- freeze unless new official schema/license evidence is found
- no further source-role revisions

Codex:
- continue current bounded full ingest
- do not restart solely for branch integration
- finish artifact / oracle / fresh-kernel evidence
- do not self-merge

## Wave 3 — after Codex final report

1. merge portability-fixed EDA support
2. merge final `impl/g1-codex`
3. run strict cross-agent integration tests
4. canonical-root fresh-kernel `01_build_pair_registry.ipynb`
5. generate canonical registry manifest/hash
6. independently audit with Data Recon
7. Claude semantic contract audit
8. Vice Director adjudication:
   - Phase 1 engineering complete?
   - G1 conditions all satisfied?
9. if LID/QC rate unresolved:
   - G1 remains OPEN
   - execute approved CR-003 sequencing plan
10. only after G1 PASS may later-phase evidence be promoted

---

# 12. Current Decisions Required from Research Director

## OPS-DR-01 — Old EDA public-history sanitation

Recommendation:

```text
APPROVE
```

Scope only:

```text
eda/g0-raw-notebooks
```

Protected from rewrite:

```text
main
integration/g0
integration/g1
research/*
data/g1-recon
eda/g1-support
evidence/g1-perplexity
impl/g1-codex
```

## CR-003 / D-RD-09 — G1 Gate sequencing clarification

Recommendation:

```text
APPROVE drafting/freeze of the clarification:

D-01/01 remains ingest-only with non-mutating integrity diagnostics.
02 remains authoritative QC/exclusion.
G1 cannot PASS until its LID/QC pass-rate requirement is actually evidenced.
```

The exact LID diagnostic method must be proposed by Claude and validated by Codex before final freeze.

---

# 13. Progress Evaluation

## Research architecture

```text
VERY STRONG
```

The research question → contract → raw inventory → exact ingest oracle → canonical D-01 implementation lineage is intact.

## Reproducibility engineering

```text
STRONG
```

The project already moved from proposal-level source assumptions to byte-hashed file allowlists, independent duplicate oracles, worktree separation, and streaming bounded ingest.

## Data integrity risk control

```text
STRONG BUT NOT CLOSED
```

Large duplicate structure, cross-direction reuse, split overlap, physical alias duplication, and source/domain confounding have been surfaced before modeling.

## Repository hygiene

```text
G1 sanitized lane = GOOD
historical EDA branch = UNRESOLVED RISK
```

## Statistical readiness

```text
NOT READY — appropriately so
```

No TP/inference result is yet official.

This is methodologically correct.

---

# 14. Next Vice Director Checkpoint

Checkpoint name:

```text
G1 INTEGRATION / D-01 CANONICAL EXECUTION AUDIT
```

Required inputs:

- integration/g1 merge SHA
- portability-fixed EDA SHA
- final Codex SHA
- fresh-kernel 01 execution evidence
- pair registry manifest SHA
- source registry manifest/hash
- reconciliation PASS table
- Data Recon independent audit
- Claude semantic audit
- CR-003 / D-RD-09 resolution status
- OPS-DR-01 status

Only then may the Vice Director issue:

```text
G1 PASS
or
G1 OPEN / BLOCKED
```

---

**Snapshot fixed:** 2026-08-16 16:16 KST  
**Current formal stage:** `Phase 1 — Data Contract / 01_build_pair_registry.ipynb`  
**Current Gate:** `G1 OPEN`  
**G0:** `CLOSED`  
**Next formal decision point:** `D-01 canonical integration + G1 pass-condition reconciliation`
