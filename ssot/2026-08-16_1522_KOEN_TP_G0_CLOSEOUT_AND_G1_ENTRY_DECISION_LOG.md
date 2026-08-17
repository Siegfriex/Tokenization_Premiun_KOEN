# KO-EN Tokenization Premium — G0 Official Closeout & G1 Entry Decision / Execution Log

> **Snapshot:** 2026-08-16 15:22 KST  
> **Project:** Korean–English Tokenization Premium  
> **Authority SSOT:** `KOEN-TP-RS-001` — `Korean_English_Tokenization_Premium_Research_Spec_v1.0`  
> **SSOT status:** `FINAL DESIGN / PRE-ANALYSIS`  
> **Canonical project root:** `/home/sieg/projects-wsl/Tokenization_Premium`  
> **Canonical package namespace:** `src/tokenization_premium/`  
> **GitHub:** `Siegfriex/Tokenization_Premium`  
> **Repository visibility:** PUBLIC  
> **Operational status:** `G0 CLOSED / MAIN RELEASED`  
> **Next formal phase:** `Phase 1 — Data Contract / G1 Data Integrity`  
> **Prepared by:** Main Vice Director / Senior Research Architect  
> **Final authority:** Research Director  
> **Operational supersession:** supersedes the current-state portion of `2026-08-16_1356_KOEN_TP_VICE_DIRECTOR_DECISION_EXECUTION_LOG.md`; the earlier file remains an immutable historical snapshot.

---

# 0. Document Role / Authority Boundary

This document is a **point-in-time decision, execution, lineage, and Gate closeout log**.

It does **not** replace or amend `KOEN-TP-RS-001`.

Authority order remains:

```text
KOEN-TP-RS-001
    ↓
Research Director approved decisions / CHANGELOG
    ↓
Phase-specific research contracts
    ↓
implementation / notebooks / tests / artifacts
    ↓
agent reports
```

If an agent report, code artifact, or later convenience conflicts with the SSOT, the SSOT wins unless a formal approved change has been recorded.

No research claim is promoted solely because an agent reports completion.

Evidence hierarchy remains:

```text
LEVEL 0 — Proposal
LEVEL 1 — Code exists
LEVEL 2 — Code executed
LEVEL 3 — Validation passed
LEVEL 4 — Artifact persisted + hash
LEVEL 5 — Statistical / robustness evidence
LEVEL 6 — Release evidence
```

---

# 1. Executive Verdict

## 1.1 G0 is formally closed

**Vice Director final verdict: `G0 — PASS / CLOSED`.**

The Phase-0 canonical integration was validated in the canonical project root and promoted to `main` without content delta.

Current release anchor:

```text
main
f1b2a901b3bc9a9d759af0698bd0c308ec6e468b
```

G0 canonical integration anchor:

```text
integration/g0
3170fc8f83558fc3fc9c919b1e998dc6b1520311
```

Both commits carry the same Git tree:

```text
a41e832f16c048863a6f89480631e5e498a340bf
```

Therefore the `main` promotion changed ancestry, not project content.

## 1.2 G1 has not passed and has not yet produced D-01

Current formal state:

```text
G0 Design Freeze             PASS / CLOSED
Phase 0 Environment          PASS / RELEASED TO MAIN

Phase 1 Data Contract        READY TO ENTER
G1 Data Integrity            NOT PASSED
D-01 Pair Registry           NOT BUILT
02 Normalize & QC            NOT STARTED
G2+                          NOT ENTERED
```

The next canonical notebook remains:

```text
notebooks/01_build_pair_registry.ipynb
```

No exploratory or evidence notebook may replace that canonical role.

## 1.3 Track B

```text
RQ7 / Track B
= DEFERRED_NOT_EXECUTED
```

Track B remains in the SSOT but is not executed in the present research line.

If reactivated later, the approved baseline is Hugging Face hosted API, with endpoint/model/revision/provider/API semantics re-frozen at the time of activation.

Track A / RQ1–RQ6 are unaffected.

---

# 2. SSOT Re-read — Phase / Gate Realignment

The SSOT notebook order is binding:

```text
Phase 0 — Environment
00_environment_repro.ipynb

Phase 1 — Data Contract
01_build_pair_registry.ipynb

Phase 2 — Normalization & QC
02_normalize_and_qc.ipynb

Phase 3 — Feature Layer
03_representation_features.ipynb
04_morphology_features.ipynb

Phase 4 — Tokenizer Measurement
05_o200k_measurement.ipynb
06_regex_chunk_audit.ipynb

Phase 5 — Statistics
07_eda_and_decomposition.ipynb
08_primary_inference.ipynb
09_explanatory_models.ipynb
10_predictive_models.ipynb
11_robustness.ipynb

Phase 6 — Serving
12_gpt_oss_serving.ipynb

Phase 7 — Release
13_release_tables_figures.ipynb
```

## 2.1 G0 PASS conditions

SSOT G0 requires:

- RQ / estimand frozen
- primary outcome frozen
- tokenizer / analyzer frozen
- QC rubric frozen
- main / sensitivity boundary frozen

All are satisfied and persisted on the released `main` tree.

## 2.2 G1 PASS conditions

G1 is a different Gate.

SSOT G1 requires:

- pair IDs unique
- null / duplicate checks
- LID / QC pass rate reported
- source / license metadata complete

Therefore PRE-G1 reconnaissance, EDA, source documentation, or pairability evidence are **inputs to G1**, not G1 PASS itself.

## 2.3 01 / 02 boundary

Canonical interpretation:

```text
01_build_pair_registry
= deterministic ingest + identity + raw provenance + schema + lineage

02_normalize_and_qc
= normalization + hard exclusions + soft flags + semantic QC
```

Exact duplicates may be **identified/grouped** in D-01, but SSOT hard-exclusion is applied in the QC layer.

A successfully parsed duplicate is not silently removed during ingest.

---

# 3. Directly Verified Git State

## 3.1 Current branch heads

| Branch | Remote HEAD | Role | State |
|---|---|---|---|
| `main` | `f1b2a901b3bc9a9d759af0698bd0c308ec6e468b` | canonical release | **G0 RELEASE** |
| `integration/g0` | `3170fc8f83558fc3fc9c919b1e998dc6b1520311` | closed G0 integration | CLOSED |
| `impl/g0-codex` | `467b3608d702abdd4c19344c345c022dafc604ce` | G0 engineering source branch | FROZEN |
| `research/g0-claude` | `51147e31f42cdcd4748bcbb31609f46b27243cc6` | G0 research source branch | FROZEN |
| `research/g1-prep-claude` | `970a52effffb5b103a8a6bd798f5e588dfaf4217` | PRE-G1 research contract | EVIDENCE / NOT ON MAIN |
| `data/g0-aihub-recon` | `6e89b9ea774f61175875fead14c15eb5ef5035ff` | local raw / duplicate recon | EVIDENCE / NOT ON MAIN |
| `eda/g0-raw-notebooks` | `4e56fdbc70c0571e9eeb912c61816885ad5477a7` | exploratory raw EDA | **QUARANTINE BEFORE PORT** |
| `evidence/g0-perplexity` | `c5b704f4b534f4a5d4da5d3c3af78516f6814f6b` | official web source audit | EVIDENCE / NOT ON MAIN |

No PRE-G1 evidence branch is an ancestor of the G0 release commit.

## 3.2 Divergence from released main

Direct Git comparison:

```text
research/g1-prep-claude:
  ahead of main: 3
  behind main: 11
  merge-base: research/g0-claude@51147e3

data/g0-aihub-recon:
  ahead of main: 3
  behind main: 13
  merge-base: b37f733

eda/g0-raw-notebooks:
  ahead of main: 5
  behind main: 13
  merge-base: b37f733

evidence/g0-perplexity:
  ahead of main: 1
  behind main: 13
  merge-base: b37f733
```

Conclusion:

> PRE-G1 branches must **not** be merged wholesale into `main`.

G1 must be rebased structurally by creating a new integration line from the released `main`.

---

# 4. G0 Evidence Closure

## 4.1 Research contract

Released `main` contains the machine-readable research contract.

Frozen core:

- primary estimand: `Median(log_token_premium)`
- primary tokenizer: `o200k_base`
- tiktoken design freeze: `0.13.0`
- morphology analyzer: Kiwi / kiwipiepy `0.23.2`
- paired observational interpretation
- causal language forbidden
- QC rubric
- normalization contract
- model/sensitivity boundaries
- seed policy
- Track A/B separation
- Track B execution deferral

## 4.2 Phase-0 canonical validation

Canonical `ENVIRONMENT_REPRO_v001.json` records:

```text
cross_agent_contract = PASS
namespace = tokenization_premium
track_a_b_separation = PASS
Track B engineering state = deferred
Track B research state = DEFERRED_NOT_EXECUTED

research seed config = PASS
```

Frozen research seeds:

```text
master_seed = 20260816
split       = 1456095166
bootstrap   = 4263151703
model_tuning= 3618347261
serving     = 2218276919
auxiliary   = 2995913794
```

Tokenizer:

```text
tokenizer_id             = o200k_base
tiktoken_version         = 0.13.0
encoding_file_sha256     = 446a9538cb6c348e3516120d7c08b09f57c36495e2acfffe59a5bf8b0cfb1a2d
mergeable_ranks_count    = 199998
roundtrip_pass_rate      = 1.0
```

Kiwi:

```text
kiwipiepy          = 0.23.2
model version      = 0.23.0
model manifest SHA = 3baa52f40876b78dab7e9428f2e488ca2ae3ed6b3d813df17f72e15a61fc516a
```

## 4.3 Canonical execution reported and accepted

Codex canonical integration report:

- pytest: `12 passed`, `0 skipped`
- Ruff: PASS
- mypy: PASS
- `uv lock --check`: PASS
- `uv pip check`: PASS
- fresh-kernel `00_environment_repro.ipynb`: `12/12`, error 0
- canonical root execution
- `.agent_worktrees/codex` path absent from canonical final artifact
- canonical artifact/hash regeneration complete

This satisfies G0 engineering/reproducibility acceptance.

## 4.4 Main release

Main promotion:

```text
merge commit
f1b2a901b3bc9a9d759af0698bd0c308ec6e468b

parent 1
5bf770eacbdd341d9539bd392614657f6cf0777a

parent 2
3170fc8f83558fc3fc9c919b1e998dc6b1520311

tree
a41e832f16c048863a6f89480631e5e498a340bf
```

The integration commit has the same tree SHA.

Therefore:

```text
G0 MAIN PROMOTION = PASS
G0 OFFICIAL STATUS = CLOSED
```

This is a G0 milestone release and is not the same concept as the future research-wide SSOT Gate `G6 — Release`.

---

# 5. Frozen Decisions Through G0 / PRE-G1

## CR-001 — Python namespace

```text
canonical:
src/tokenization_premium/

do not:
rename to koen_tp
create dual package
create alias package
```

Status: APPROVED / ACTIVE.

## D-RD-01 — G0 parameter bundle

Approved and frozen:

- exact-decomposition epsilon `1e-10`
- bootstrap `B=5000`
- BH-FDR alpha `0.05`
- length strata = EN-codepoint quintiles
- semantic audit `N=500`
- holdout `20%`
- digit soft flag `>0.20`
- punctuation soft flag `>0.20`
- source fixed effects primary
- random intercept sensitivity only under preregistered conditions
- VIF warning 5 / severe 10, no auto-delete
- quantile `.50/.90/.95`
- approved seeds above

## D-RD-02 — Git integration policy

Completed for G0:

```text
agent branch
→ integration/g0
→ cross-agent validation
→ canonical Run All
→ main
```

## D-RD-03 / CR-002 — Track B

`DEFERRED_NOT_EXECUTED`.

## D-RD-04 — Raw EDA auxiliary track

Authorized as supporting / exploratory evidence only.

It never substitutes for canonical notebooks 00–13.

## D-RD-05 — Source portfolio

Approved PRE-G1 classification:

```text
025 / D71265
candidate tier = A
role = PRIMARY_BACKBONE
primary-analysis eligible = true

026 / D71266
candidate tier = A
role = PRIMARY_DOMAIN_SUPPLEMENT
primary-analysis eligible = true

Legacy / D87
tier = null / UNASSIGNED
role = SENSITIVITY_ONLY
primary-analysis eligible = false

D71693
NOT_ACQUIRED / OUTSIDE_CURRENT_CORPUS
```

`source_tier` and official-provenance closure are separate axes.

The following additional provenance status is required:

```text
025/026:
PENDING_OFFICIAL_SCHEMA_AND_RELEASE_LINK

Legacy:
PARTIAL_OFFICIAL_CONSTRUCTION_CONFIRMED_FIELD_AND_RELEASE_LINK_PENDING
```

## D-RD-06 — Translation direction

```text
025: KO_TO_EN / EN_TO_KO from local provenance
026: KO_TO_EN
Legacy: UNKNOWN
```

Never infer human-only translation or MT/post-edit workflow without official evidence.

## D-RD-07 — Canonical top-level domain mapping

```text
025
일상생활          → general
해외고객과의채팅 → dialogue
해외영업          → other

026
기술과학 → technology
세계     → other
경제     → other
정치     → other
기후     → other

Legacy
구어체         → general
대화체         → dialogue
뉴스           → news
한국문화       → other
조례           → legal
지자체웹사이트 → administration
```

Raw labels remain preserved separately.

## D-RD-08 — Primary cohort size policy

No arbitrary pre-analysis cap.

```text
final primary N
=
realized N after ingest validity
+ QC acceptance
+ exact duplicate policy
for eligible 025 + 026 pairs
```

`100,000+` in SSOT is a recommended analysis scale, not a maximum.

---

# 6. PRE-G1 Local Evidence State

## 6.1 Raw inventory

Canonical local raw reconnaissance established:

```text
025                 2,700,345
026                 1,350,162
Legacy              1,602,418
--------------------------------
Total unique-content records
                    5,652,925
```

This is not the final analysis N.

## 6.2 SHA-256 duplicate / identity recon — L4

Remote-persisted:

```text
data/g0-aihub-recon
6e89b9ea774f61175875fead14c15eb5ef5035ff
```

Exact raw pair digest:

```text
SHA256(
  u64be(len(ko_utf8)) || ko_utf8 ||
  u64be(len(en_utf8)) || en_utf8
)
```

No normalization is used for this raw identity audit.

Results:

```text
025 duplicate rows after first     214,252
025 duplicate groups                93,823
026 duplicate rows after first          44
026 duplicate groups                    44

025 shared distinct exact pairs
EN_TO_KO ↔ KO_TO_EN                 50,511

TRAIN ↔ VALIDATION shared
distinct exact pairs                25,247

025 sn dataset-wide collision            0
026 sn dataset-wide collision            0

cross-corpus exact overlap:
025 ↔ 026                                0
025 ↔ Legacy                            35
026 ↔ Legacy                             1

Legacy News(2) ↔ Culture             2,469
```

The News(2)↔Culture overlap remains:

`POTENTIAL_SOURCE_REUSE / COMPOSITION_OVERLAP`

—not an asserted error.

## 6.3 Targeted EDA — L4 supporting evidence

Remote-persisted:

```text
eda/g0-raw-notebooks
4e56fdbc70c0571e9eeb912c61816885ad5477a7
```

High-value observations:

### 025

- 2,700,345 full-population rows
- exact duplicate-after-first: 214,252
- cross-direction 1:1-matchable duplicate rows: 50,529
- within-direction duplicate-after-first:
  - EN_TO_KO: 26,525
  - KO_TO_EN: 137,216
- within-split:
  - TRAIN: 164,170
  - VALID: 24,844
- cross-split matchable rows: 36,089
- mechanisms overlap; counts are not mutually additive
- duplicate-group maximum multiplicity: 5,508
- SBS 449,805 rows are observed only in `KO_TO_EN × 일상생활`

Important denominator distinction:

```text
Recon 50,511 = shared distinct exact-pair digests
EDA   50,529 = 1:1-matchable rows
```

These are different statistics and must not be presented as a contradiction.

### 026

Row-level biconditional is locally observed:

```text
source_provenance_raw = 특허정보원
iff
domain_raw = 기술과학

count = 359,910
exceptions = 0
```

Therefore `source_provenance_raw` and `domain` are not independently estimable within 026.

This directly activates the SSOT identifiability warning.

### Legacy

News(2) ↔ Culture exact overlap:

```text
groups = 2,469
News(2) share = 1.2312%
Culture share = 2.4532%
combined multiplicity = 2 for every group
```

The overlap is highly concentrated in a specific metadata subset.

Root cause remains unadjudicated.

---

# 7. Pair Identity / Duplicate Semantics Fixed for G1

## 7.1 Identity layers

Approved:

```text
pair_id
= provenance-based raw record identity

duplicate_group_id
= content-based exact KO+EN identity
```

These answer different questions and must never be collapsed.

For 025/026, the current raw snapshot supports `sn` as a dataset-wide unique natural source-record candidate because cross-sub-file collision is zero.

`raw_locator` remains mandatory even when `sn` is unique.

## 7.2 Registry vs QC

D-01 keeps all structurally ingestible records.

At Phase 1:

- preserve pair identity
- preserve raw locator
- preserve upstream split
- compute/query duplicate group membership
- preserve all raw provenance fields

At Phase 2:

- decide exact duplicate hard-exclusion from the analysis cohort
- apply LID / anomaly / semantic QC
- produce accepted/review/rejected status

## 7.3 Analysis Representative

The representative record of a duplicate group is a **provenance pointer only**.

It must not arbitrarily supply group-level semantic covariates.

Translation-direction resolution:

```text
direction set = {KO_TO_EN}
→ KO_TO_EN

direction set = {EN_TO_KO}
→ EN_TO_KO

direction set = {KO_TO_EN, EN_TO_KO}
→ UNKNOWN
+ direction_conflict_flag = true
```

Domain/source group-conflict handling still requires a machine-readable diagnostic before final Phase-2 exclusion logic is frozen.

## 7.4 Upstream train/validation

AIHub train/validation is raw provenance only.

Project predictive split is constructed later under SSOT LR-01 and must not allow duplicate/near-duplicate clusters on both sides.

---

# 8. External Provenance Evidence State

Current persisted Perplexity branch remains:

```text
evidence/g0-perplexity
c5b704f4b534f4a5d4da5d3c3af78516f6814f6b
```

The later Perplexity report supplied to the Vice Director contains additional official-document findings, especially for D87, but that update is **not yet remote-persisted** and therefore is not Level 4 project evidence.

Operational rule:

```text
WEB / OFFICIAL evidence
≠
LOCAL OBSERVED evidence
```

Neither silently overwrites the other.

Current forbidden inferences:

- `mt` means confirmed MT draft
- `ko/en` means confirmed human-final translation
- `ko_original/en_original` semantics are known merely from their names
- `license="open"` means AI Hub redistribution permission
- local D87 1,602,418 rows are proven identical to a specific official release

---

# 9. Critical Repository Hygiene Finding

## 9.1 EDA branch raw-text exposure

The repository is public.

Direct inspection of:

```text
eda/g0-raw-notebooks:
outputs/eda_raw/aihub_025/aihub_025_samples.csv
```

confirmed that the committed file contains actual KO/EN sentence previews (`ko_preview`, `en_preview`), not aggregate-only statistics.

Therefore:

```text
eda/g0-raw-notebooks
= QUARANTINED FOR G1 PORT
```

The branch must **not** be merged or cherry-picked wholesale into `integration/g1`.

This does not contaminate G0 `main`; the EDA branch is not an ancestor of the released main.

Required next action:

1. build a new sanitized G1 EDA/evidence branch from released `main`
2. port aggregate-only artifacts and sanitized notebooks
3. audit every sample CSV / notebook output for raw licensed text
4. decide whether to rewrite/delete the historical EDA branch ref because raw text is already present in public Git history

A history rewrite / branch deletion is an exceptional destructive Git operation and requires explicit Research Director authorization.

## 9.2 Canonical notebook namespace collision

The untracked canonical-root file:

```text
notebooks/01_aihub_local_recon_evidence_export.ipynb
```

was independently inspected:

- SHA-256:
  `d3e2df39d1cd6fed21631be91e1cdb65377a1e0bda9a59f22eef0ea8dc740af5`
- code cells: 17
- execution counts: 1–17
- error outputs: 0
- raw files modified: 0
- reported raw text exported: 0

However the filename/location conflicts with the canonical SSOT Phase-1 namespace.

It must **not** remain as `notebooks/01_*`.

Recommended sanitized auxiliary path:

```text
notebooks/exploratory/evidence/
AIHUB_LOCAL_RECON_EVIDENCE_EXPORT_20260816.ipynb
```

The canonical root must reserve:

```text
notebooks/01_build_pair_registry.ipynb
```

for Phase 1.

---

# 10. Formal G0 Closeout Decision

## G0-CL-01

```text
Decision:
G0 Design Freeze and Phase-0 Environment/Reproducibility are closed.

Release anchor:
main@f1b2a901b3bc9a9d759af0698bd0c308ec6e468b

Canonical integration:
integration/g0@3170fc8f83558fc3fc9c919b1e998dc6b1520311

Tree:
a41e832f16c048863a6f89480631e5e498a340bf

Result:
PASS
```

No additional G0 work is permitted except factual correction to the closeout record.

Any new data/source/QC implementation belongs to G1 or later.

## G0-CL-02 — Branch Freeze

The following branches are historical/frozen inputs:

```text
research/g0-claude
impl/g0-codex
integration/g0
```

Do not continue Phase-1 development on them.

## G0-CL-03 — G1 base

All canonical Phase-1 development must descend from:

```text
main@f1b2a901b3bc9a9d759af0698bd0c308ec6e468b
```

—not from any PRE-G1 branch head.

---

# 11. G1 Repository Architecture

Create:

```text
main
f1b2a90...
    │
    └── integration/g1
          │
          ├── research/g1-claude
          ├── impl/g1-codex
          ├── data/g1-recon
          ├── eda/g1-support
          └── evidence/g1-perplexity
```

Recommended worktrees:

```text
.agent_worktrees/
├── integration-g1/
├── codex-g1/
├── claude-g1-canonical/
├── data-recon-g1/
├── raw-eda-g1/
└── perplexity-g1/
```

`main` remains release/integration only.

No agent directly implements on `main`.

---

# 12. G1 Evidence Port Policy

## 12.1 Claude PRE-G1

Current branch is 3 commits ahead of main and 11 behind.

Port the unique PRE-G1 research commits onto `research/g1-claude` based on the released main.

Expected unique sequence:

```text
a3d2c45...
1ba3baa...
970a52e...
```

Do not merge the divergent branch wholesale.

## 12.2 Data Recon

Current branch is 3 commits ahead of main and 13 behind.

Port the unique data-recon evidence onto `data/g1-recon`, preserving:

- raw inventory/hash evidence
- duplicate/overlap manifests
- SHA-256 collision-resistant duplicate audit
- non-claim boundaries

No raw data is committed.

## 12.3 EDA

Do **not** cherry-pick the five unique EDA commits wholesale.

Build a clean `eda/g1-support` from main and selectively recreate/port only:

- aggregate tables
- aggregate figures
- reports without raw text
- sanitized notebook versions with raw sample outputs removed
- targeted decision audit aggregates
- safe local-recon evidence notebook under auxiliary namespace

Do not port:

- sample CSV containing KO/EN text
- notebook output cells containing licensed raw sentence samples
- raw URLs / PII / source text
- any artifact whose redistribution status is unclear

## 12.4 Perplexity

Create fresh `evidence/g1-perplexity` from main.

Port the existing official source audit, then persist the new D87 construction/quality evidence as a G1 official-evidence update.

Perplexity is never treated as a local-filesystem observer.

---

# 13. G1 Implementation Roadmap

## Stage G1-A — Canonical G1 branch / contract port

Goal:

```text
main G0 release
→ integration/g1
→ canonical G1 research/data evidence branches
```

Outputs:

- G1 branch lineage
- G1 approved decisions carried onto canonical base
- `configs/research_v1.yaml` G1 delta applied on the G1 research branch
- evidence/provenance closure statuses
- sanitized EDA/evidence branch
- local ingest expectations manifest

No pair registry yet.

## Stage G1-B — Pair Registry implementation

Canonical notebook:

```text
01_build_pair_registry.ipynb
```

Responsibilities:

- deterministic source ingest
- stable `pair_id`
- `source_record_id`
- `raw_locator`
- `duplicate_group_id`
- source tier / role / provenance closure fields
- raw-domain and canonical-domain fields
- translation-direction record field
- upstream split provenance
- raw text fields
- exact physical source hash linkage
- schema validation
- row-count reconciliation
- byte-identical physical alias suppression

No SSOT hard QC exclusion at ingest except structural/parsing failure.

## Stage G1-C — Independent registry audit

Data Recon validates:

- expected input files
- expected unique-content counts
- pair-ID uniqueness
- 025/026 `sn` uniqueness
- no accidental source/label double ingest
- raw file hash match
- registry row reconciliation
- duplicate-group counts against independent recon

Claude validates research semantics.

Codex validates schema and deterministic reproduction.

## Stage G1-D — G1 Gate adjudication

G1 PASS requires:

```text
pair IDs unique
null / duplicate checks complete
LID / QC pass rate report available
source / license metadata complete
```

Important interpretation:

Some QC outcomes are generated in Phase 2.
Therefore the G1 closeout must clearly distinguish:

- D-01 registry integrity
- preliminary QC counters needed for G1
- full Phase-2 accepted/rejected cohort

If strict SSOT interpretation requires full LID/QC pass-rate from Phase 2 before declaring G1 PASS, G1 remains `CONDITIONALLY READY` until the minimum QC audit has run; do not fake a PASS.

## Stage G2 onward

Only after G1 is accepted:

```text
02_normalize_and_qc
→ G2 representation integrity work
→ 03 representation features
→ 04 morphology
→ 05 o200k measurement / exact decomposition
...
```

No Tokenization Premium result is official before the upstream Gates pass.

---

# 14. Immediate Acceptance Criteria for Starting Notebook 01

Before Codex writes the canonical notebook, all must be true:

- `integration/g1` exists from `main@f1b2a90...`
- `research/g1-claude` contains canonicalized G1 contract
- `configs/research_v1.yaml` includes the approved G1 delta
- `data/g1-recon` contains expected ingest manifests
- EDA raw-text leakage branch is not being used as a merge source
- the auxiliary local-recon notebook has a non-canonical filename/path
- raw roots remain read-only
- physical alias handling is specified
- D-01 schema + auxiliary fields are frozen
- exact duplicate identity implementation contract is frozen
- no Track B work is activated

---

# 15. Current Decision Required from Research Director

## OPS-DR-01 — EDA branch history sanitation

Direct evidence shows raw KO/EN sentence text is present in the **public** `eda/g0-raw-notebooks` Git history.

Recommended action:

```text
APPROVE
exceptional sanitation of the isolated EDA branch history
while keeping main / integration/g0 immutable.
```

Minimum safe policy:

1. create clean `eda/g1-support` from released main
2. port only aggregate/sanitized artifacts
3. remove the old public `eda/g0-raw-notebooks` branch ref
4. if complete public-history removal is required, use a narrowly scoped history rewrite / force update only for the contaminated EDA branch, never for main
5. document the exception in the operations log

This is an operational/repository-hygiene decision, not a research-design change.

---

# 16. Final Gate Matrix at Closeout

| Gate / Phase | Status | Evidence |
|---|---|---|
| G0 Design Freeze | **PASS / CLOSED** | research contract + approved decisions |
| Phase 0 Environment/Repro | **PASS / RELEASED** | canonical Run All, tests, artifacts, main release |
| G1 Data Integrity | **NOT PASSED** | D-01 not built |
| G2 Representation Integrity | NOT ENTERED | no canonical normalized/representation cohort |
| G3 Tokenizer Integrity | environment-level tokenizer audit exists; formal downstream Gate not yet adjudicated on research cohort | future |
| G4 Morphology Integrity | environment-level analyzer freeze exists; formal cohort audit not run | future |
| G5 Analysis Readiness | NOT ENTERED | cohort/split not frozen |
| G6 Research Release | NOT ENTERED | final analysis/release absent |
| Track B | `DEFERRED_NOT_EXECUTED` | CR-002 |

---

# 17. Research Claim Boundary at G0 Close

Allowed:

- G0 design/environment reproducibility is released.
- Local raw data contain deterministic KO/EN pair candidates.
- substantial exact duplication exists in 025.
- part of 025 duplication is cross-direction content reuse.
- 026 contains a structural raw-source/domain confound.
- Legacy News(2)/Culture content overlap exists and needs provenance interpretation.
- source-role/domain/direction decisions are frozen for G1 contract application.

Not allowed:

- the observed 5,652,925 raw records are the final cohort
- duplicate rows are all errors
- 025 cross-direction duplicates are all benign
- D87 local files are proven to be a particular official release
- `mt` is a confirmed MT draft
- `ko/en` are confirmed human-final fields
- `license=open` means public redistribution is permitted
- any TP/logTP/morphology mechanism result has been established
- any causal language claim

---

# 18. Next Vice Director Checkpoint

Next formal checkpoint:

```text
G1 ENTRY AUDIT
```

Required evidence bundle:

1. `integration/g1` and all agent branch SHAs
2. canonicalized G1 contract/config
3. sanitized EDA support branch
4. persisted official G1 evidence audit
5. D-01 implementation commit
6. fresh-kernel `01_build_pair_registry.ipynb`
7. registry artifact + SHA
8. schema tests
9. row reconciliation
10. source/license/provenance report
11. preliminary null/duplicate/LID/QC accounting
12. Gate recommendation

Only then will the Vice Director issue:

```text
G1 PASS
or
G1 FAIL / BLOCKED
```

---

**Snapshot closed:** `2026-08-16 15:22 KST`  
**G0 release anchor:** `main@f1b2a901b3bc9a9d759af0698bd0c308ec6e468b`  
**G0 status:** `OFFICIALLY CLOSED`  
**Next phase:** `Phase 1 — Data Contract / G1 Data Integrity`
