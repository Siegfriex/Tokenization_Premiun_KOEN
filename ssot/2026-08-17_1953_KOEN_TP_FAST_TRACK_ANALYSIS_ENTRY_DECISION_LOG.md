# KOEN — Fast-Track Analysis Entry Decision Log

> Decision ID: RD-FAST-G5-01
> Authority: Research Director
> Parent Authority: KOEN-TP-RS-001
> Effective date: 2026-08-17 KST
>
> Status:
> APPROVED
>
> Classification:
> POST-FREEZE DIRECTOR DECISION
> REALIZED-MODEL CONTRACT
> ANALYSIS FAST-TRACK
>
> Associated approved Change Requests:
> CR-FAST-G5-REALIZED-MODEL-01
> CR-FAST-G5-SPLIT-RELOCATION-01
>
> This decision does NOT alter:
> - primary research question
> - primary outcome
> - o200k_base tokenizer
> - exact decomposition
> - morphology measurement
> - D-02/D-03/D-04 bytes
> - paired observational / non-causal claim boundary

---

## 1. Integration evidence entering this decision

Canonical main before integration:

28d88ad40d85fa6067c6388fb8fbf8b2b6c5e329

Claude-A checkpoint:

branch:
impl/pre-g5-checkpoint-a-20260817

SHA:
a127551ec346762ac1c79aa4007e957911d54ac5

Claude-B checkpoint:

branch:
research/pre-g5-checkpoint-b-20260817

SHA:
b2d6447da11c127be8d4e34549b770db3f35a6dd

EDA V2 checkpoint:

branch:
results/pre-g5-eda-v2-20260817

SHA:
a4b9ca1a0a767b53c29ba0c104810b82c15b65bb

EDA V1 frozen historical snapshot:

aabd068a4eef1245420ba4cc0a510ca4e27deae2

V1 remains unmerged and immutable.

---

## 2. Current measurement state

G0 PASS / CLOSED
G1 PASS / CLOSED
G2 PASS / CLOSED
G3 PASS / CLOSED
G4 PASS / CLOSED

MEASUREMENT_FOUNDATION_CLOSED_THROUGH_G4

Canonical final pair universe:

N = 3,835,988

D-02:
REP_FEATURES_v002.parquet
SHA256 =
dfae8e01cd3fe2ca949d8754678e508203ad1a7aa6abea418008a33ac650d309

D-03:
MORPH_FEATURES_KIWI_v001.parquet
SHA256 =
0fe5bd74e3993a7141c5c33ea78e71b2c66e3ecd296544bde2615acb43e50f7d

D-04:
TOKEN_O200K_BASE_v001.parquet
SHA256 =
1c30e3276222dd94885ae4f79fc6ab5c45e4e26226de0afd91fc6b1f7d2c16e7

Pair-set hash:

d9660d654ee449e4d0c23a0070225274

No D-02/D-03/D-04 regeneration is authorized by this decision.

---

## 3. Research operating decision

The project now moves from measurement validation to substantive analysis.

The new operating priority is:

1. freeze the realized analysis contract;
2. remove only mathematically non-estimable or deterministically redundant terms;
3. run the minimum required G-ID diagnostics on the actual planned model matrix;
4. produce RQ1 inference and canonical descriptive results without waiting on predictive-only infrastructure;
5. complete D-05 in parallel;
6. defer predictive leakage grouping to the stage where it is actually required.

Broad re-auditing or feature-by-feature gate bureaucracy is not authorized without a material threat to the estimand.

---

## 4. CR-FAST-G5-REALIZED-MODEL-01 — APPROVED

### 4.1 sentence_type

Observed realized state:

sentence_type has one level over the final cohort.

Therefore:

sentence_type is excluded from all realized primary model matrices.

Classification:

REALIZED_ZERO_VARIANCE_COVARIATE
NON_ESTIMABLE

This exclusion is not outcome-driven feature selection.

The conceptual SSOT variable remains historically documented.

---

### 4.2 logical_corpus

source_id and logical_corpus are bijective over the realized cohort.

Therefore:

logical_corpus is retained for provenance and descriptive reporting only.

It is excluded from model matrices when source_id or its approved replacement control is present.

Forbidden:

source_id + logical_corpus

or any model claiming independent coefficients for both.

Classification:

DETERMINISTIC_CATEGORICAL_REDUNDANCY

---

### 4.3 Primary source/domain control

The primary metadata control becomes the observed-cell factor:

source_domain_cell
=
interaction(source_id, domain)

The realized cells are approximately:

025 × dialogue
025 × general
025 × other
026 × other
026 × technology

This parameterization is used to avoid unsupported decomposition of source and domain variation.

Interpretation:

coefficients describe conditional contrasts between observed source-domain strata.

Forbidden interpretation:

- independent domain causal effect
- independent source causal effect
- pure technology effect

Sensitivity specification:

domain + source_id

may be fitted only if the realized additive design matrix is full-rank and numerically acceptable.

---

### 4.4 Pair-size control

The primary absolute pair-size covariate is:

pair_log_size_i
=
0.5 ×
(
log(C_KO,i)
+
log(C_EN,i)
)

equivalently:

pair_log_size_i
=
log sqrt(C_KO,i × C_EN,i)

where both codepoint counts are strictly positive.

No +1 smoothing is used.

This separates overall pair scale from:

logCodePointRatio
=
log(C_KO/C_EN)

because:

log C_KO
=
pair_log_size + 0.5 logCodePointRatio

log C_EN
=
pair_log_size - 0.5 logCodePointRatio

---

## 5. Realized explanatory model ladder

Primary outcome A:

Y_A = log_token_premium

Secondary outcome B:

Y_B = log_compression_penalty

### M0

Y
~
pair_log_size
+
source_domain_cell
+
translation_direction

UNKNOWN translation direction remains an explicit level in the primary cohort.

Known-direction-only is a sensitivity analysis.

### M1

M0
+
logCodePointRatio
+
logByteDensityRatio
+
nonredundant whitespace / surface features
+
reference-coded script composition

M1 is an accounting / representation-associated model.

It is not a causal model.

For Y_A = logTP:

logCompressionPenalty,
TP,
logTP,
token counts,

must not be inserted as RHS predictors in a way that mechanically leaks the outcome.

### M2

M1
+
morpheme_density
+
particle_ratio
+
ending_ratio
+
deriv_affix_ratio

Primary morphology question:

M2 − M1 incremental explanatory value.

### M2A sensitivity

M1
+
morpheme_density
+
function_morpheme_ratio
+
deriv_affix_ratio

function_morpheme_ratio must not coexist with particle_ratio + ending_ratio
in the same primary specification.

### M3

M2
+
D-05 regex-chunk/tokenizer mechanism block

M3 remains a mechanism audit.

It is not a stricter causal-adjustment model.

---

## 6. Fast collinearity policy

The following order is frozen.

### Step 1 — structural removal

Remove before empirical diagnostics:

- exact identities
- deterministic derived duplicates
- zero-variance features
- categorical bijections
- compositional overparameterization

### Step 2 — inspect only the actual planned reduced matrix

Do not perform open-ended feature fishing.

### Step 3 — diagnostics

Hard stop:

design matrix rank deficient

Reparameterization trigger:

condition number >= 100

Strong review trigger:

VIF/GVIF >= 20

Same-construct redundancy review:

|Spearman rho| >= 0.95

Values below these review triggers do not automatically imply absence of multicollinearity,
but they do not independently stop the research.

VIF alone never determines scientific feature meaning.

---

## 7. Primary analysis cohort — Director authorization

The primary analysis cohort is authorized as the complete validated final pair universe:

N = 3,835,988

No primary exclusion is introduced for:

- eojeol_count = 1
- short text
- TP extremes
- morphology extremes
- translation_direction = UNKNOWN

These conditions are handled by stratification and/or robustness analysis.

Primary sensitivity candidates include:

- known translation direction only
- eojeol_count > 1
- short-text removed
- domain = other
- central length strata

The cohort reaches formal frozen artifact status when an
ANALYSIS_COHORT_v001 manifest containing N, pair-set hash,
input artifact hashes, field-completeness checks and decision ID is persisted.

---

## 8. CR-FAST-G5-SPLIT-RELOCATION-01 — APPROVED

The split-manifest and LR-01 near-duplicate grouping requirement is removed
from the universal G5 Analysis Readiness prerequisite.

It is relocated to:

PRE-NB10 PREDICTIVE READINESS — HARD PREREQUISITE

Reason:

NB07 descriptive analysis,
NB08 paired primary inference,
and NB09 full-cohort explanatory inference

do not use a train/validation/test split.

Near-duplicate leakage grouping is directly required for predictive generalization,
not for those analyses.

This decision does not weaken LR-01.

Before NB10 begins, the following remain mandatory:

- leakage-group policy
- near-duplicate/paraphrase grouping as required
- final holdout assignment
- tuning/CV split assignment
- split manifest freeze
- train/test leakage audit

No NB10 predictive result may be produced before that prerequisite passes.

---

## 9. Revised G5 scope

No new Gate name is created.

G5 remains:

Analysis Readiness.

Following the approved split-relocation CR,
G5 requires:

1. realized-model identifiability check;
2. collinearity/composition report;
3. analysis cohort freeze.

The check is performed on the actual reduced model matrix defined in this decision.

The predictive split requirement is no longer a G5 universal blocker.

---

## 10. NB08 fast-path

RQ1 is analytically independent of:

- D-05
- morphology explanatory model
- source-domain coefficient identifiability
- VIF of explanatory predictors
- predictive split

Therefore NB08 implementation may proceed in parallel.

Formal NB08 numerical execution requires only:

1. ANALYSIS_COHORT_v001 freeze;
2. D-04 canonical identity validation;
3. primary inference protocol freeze.

The inference protocol must be fixed before inspecting the resulting test output,
including:

- one-sided signed-rank specification;
- zero/tie handling;
- sign-test robustness;
- bootstrap statistic definitions;
- B = 5000 unless an approved SSOT change says otherwise;
- bootstrap seed;
- source-stratified resampling policy where applicable;
- CI construction;
- nonfinite policy.

NB08 may execute before explanatory-model G-ID is complete.

However its release/promotion must preserve all SSOT RQ1 claim boundaries.

---

## 11. NB06 fast-path

NB06 remains required for:

- D-05
- RQ5
- M3
- regex-chunk mechanism reporting

NB06 does not block NB08.

Current status:

NB06 = NOT_STARTED

R1 periodic-memory/heartbeat defect = NOT_FIXED

Therefore:

NB06 design/code/pilot may start immediately.

NB06 full-population D-05 execution is prohibited until R1 is fixed and tested.

New canonical chunking logic must live under:

src/tokenization_premium/

and be surfaced through:

notebooks/06_regex_chunk_audit.ipynb

No new canonical research logic may be placed exclusively in scripts/.

---

## 12. R1 execution-observability condition

Before the next heavy population run:

periodic heartbeat / memory telemetry must be implemented.

Required minimum:

- repeated sampling throughout the run
- RSS
- MemAvailable
- swap state
- vmstat si/so
- elapsed
- progress
- timestamp
- final status

A two-sample start/end monitor is insufficient.

This is an engineering execution prerequisite,
not a blocker for NB07 drafting, NB08 inference, or G-ID.

---

## 13. EDA V1 / V2 status

EDA V1:

branch:
results/preliminary-eda-v1-20260817

SHA:
aabd068a4eef1245420ba4cc0a510ca4e27deae2

Status:

HISTORICAL SNAPSHOT
IMMUTABLE
NOT MERGED

EDA V2:

branch:
results/pre-g5-eda-v2-20260817

checkpoint SHA:
a4b9ca1a0a767b53c29ba0c104810b82c15b65bb

Status remains:

NON_CANONICAL
PRE-G5 EXPLORATORY
NOT GATE EVIDENCE

Its incorporation into main under this integration is archival/reproducibility integration only.

MERGE INTO MAIN
!=
PROMOTION TO CANONICAL EVIDENCE

Its method caveats at a4b9ca1 remain controlling.

---

## 14. Concurrency incident record

During checkpointing, A and B briefly operated against the same shared working tree,
and a branch checkout caused B's staged handoff file to disappear from that tree.

The file was recovered byte-identically from the Git object database.

B then recreated its checkpoint from the correct 28d88ad base in a separate worktree,
and A's branch was restored to its remote state.

Current remote refs are independent and valid.

Classification:

RECOVERED_CONCURRENCY_INCIDENT
NO_PERSISTED_RESEARCH_DATA_LOSS
NO_GATE_IMPACT

Operational consequence:

all future multi-lane work must use separate worktrees.

The integration itself must occur in a new isolated clean worktree.

No shared main working tree is to be used for branch switching.

---

## 15. Integration authorization

The following checkpoints are authorized for serial integration:

B:
b2d6447da11c127be8d4e34549b770db3f35a6dd

A:
a127551ec346762ac1c79aa4007e957911d54ac5

EDA V2:
a4b9ca1a0a767b53c29ba0c104810b82c15b65bb

V1 is not merged.

The exact remote SHA of every branch must be revalidated immediately before merge.

Any SHA mismatch aborts integration.

---

## 16. Post-integration execution lanes

After a single FINAL_MAIN_SHA is established,
new work branches only from that SHA.

Parallel lanes:

ENGINEERING:
R1 fix
→ NB06 pilot
→ NB06 D-05 full run

STATISTICS / G5:
analysis cohort manifest
→ reduced model-matrix contract
→ fast rank / VIF / condition diagnostics
→ G5 adjudication

RQ1:
NB08 inference protocol freeze
→ NB08 execution

DESCRIPTIVE:
NB07 core D-02/D-03/D-04 drafting
→ append D-05 section after NB06
→ canonical finalization

PRE-NB10:
near-duplicate grouping
→ LR-01 validation
→ split manifest
→ predictive modeling

---

## 17. Gate board after this decision

G0 PASS / CLOSED
G1 PASS / CLOSED
G2 PASS / CLOSED
G3 PASS / CLOSED
G4 PASS / CLOSED

G5:
OPEN / FAST-CLOSE PATH AUTHORIZED

NB06:
NOT STARTED

NB07:
DRAFTING AUTHORIZED

NB08:
PROTOCOL + EXECUTION AUTHORIZED AFTER COHORT FREEZE

NB09:
M0–M2 EXECUTION AFTER G5 PASS

NB10:
BLOCKED UNTIL PRE-NB10 PREDICTIVE READINESS

G6:
NOT OPEN

---

## 18. Claim boundary

Nothing in this decision establishes:

- causal domain effects
- causal morphology effects
- generalization beyond o200k_base
- NB08 inferential results before execution
- RQ5 before D-05
- predictive generalization before PRE-NB10 leakage control

The purpose of this decision is to remove non-scientific serial bottlenecks
while preserving the already frozen estimand and claim boundaries.

---

## 19. Director verdict

APPROVED.

FAST-TRACK ANALYSIS ENTRY is authorized.

The project must now prioritize result production over additional open-ended preprocessing
or generalized audit work.

Any new blocker must identify a concrete threat to:

estimand
→ artifact identity
→ model estimability
→ inference validity
→ leakage control at the stage where leakage control is actually required.

---

---

# Transcription notes — Claude-A, not part of the Director decision

The decision text above is persisted verbatim as received. Two notes are appended below the rule so
they cannot be mistaken for Director text.

## T1. Corrupted token in §14 — RESOLVED

The classification block in §14 was originally persisted as:

```
RECOVERED_CONCURRENCY_INCIDENT
NO_PERSISTED_RESEARCH_DATA_LOSS
NO_Gonsequence:
```

The third line was a transcription artifact concatenating a classification token with the following
heading. Claude-A did not repair it at the time, because inventing a classification token in an
SSOT-class decision log is not this agent's call.

**The Research Director / Main Vice Director has since confirmed the intended original.** The
approved classification is:

```
RECOVERED_CONCURRENCY_INCIDENT
NO_PERSISTED_RESEARCH_DATA_LOSS
NO_GATE_IMPACT
```

with `Operational consequence:` restored as the separate heading it was concatenated into. §14 above
now reads as approved.

Classification of this edit: `TRANSCRIPTION_RESTORATION`. It is explicitly
`NO_SSOT_SEMANTIC_CHANGE` and `NO_NEW_CHANGE_REQUEST`; no wording beyond the confirmed original was
introduced.

## T2. Verification performed before persisting

Every SHA and artifact identity asserted in §1 and §2 was re-checked against the actual repository
and the physical Parquet files at 2026-08-17 19:53 KST, rather than accepted as written.

| assertion | source | result |
|---|---|---|
| main before integration `28d88ad…` | `origin/main` | MATCH |
| A checkpoint `a127551…` | `origin/impl/pre-g5-checkpoint-a-20260817` | MATCH |
| B checkpoint `b2d6447…` | `origin/research/pre-g5-checkpoint-b-20260817` | MATCH |
| EDA V2 `a4b9ca1…` | `origin/results/pre-g5-eda-v2-20260817` | MATCH |
| EDA V1 `aabd068…` | `origin/results/preliminary-eda-v1-20260817` | MATCH |
| D-02 `dfae8e01…`, N = 3,835,988 | `REP_FEATURES_v002.parquet` | MATCH |
| D-03 `0fe5bd74…`, N = 3,835,988 | `MORPH_FEATURES_KIWI_v001.parquet` | MATCH |
| D-04 `1c30e327…`, N = 3,835,988 | `TOKEN_O200K_BASE_v001.parquet` | MATCH |
| pair-set hash `d9660d65…` | recomputed on all three cohort artifacts | MATCH, identical across all three |

The two engineering status claims in §11 were also confirmed rather than assumed:
`NB06 = NOT_STARTED` (no notebook, no `chunking.py`, no `CHUNK_O200K_BASE` artifact/manifest/config/
test; every `D-05` string in the repository is either the unrelated decision id `D-RD-05` or prose
marking the mechanism out of scope) and `R1 = NOT_FIXED` (`execute_morphology_run` and
`execute_token_measurement_run` contain no `MemoryGuard` call; both full-run manifests record
`sample_count = 2`).

## T3. How this document was persisted

Written and committed in a dedicated isolated worktree branched from `28d88ad`, per §14's
consequence that no shared main working tree is to be used for branch switching. The shared working
tree was not switched, and no other lane's files were staged, moved or modified.

Claude-A does not merge this to `main`; serial integration remains the Integration Steward's call
under §15.
