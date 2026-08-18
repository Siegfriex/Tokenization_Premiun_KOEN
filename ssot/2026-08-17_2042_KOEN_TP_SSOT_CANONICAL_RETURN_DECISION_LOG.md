# KOEN — Return to SSOT Canonical Research Path

> Decision ID: RD-SSOT-CANONICAL-RETURN-01
> Authority: Research Director
> Parent Authority: KOEN-TP-RS-001
> Effective: 2026-08-17 20:42 KST
>
> Status: APPROVED
>
> Classification:
> OPERATIONAL_REALIGNMENT
> RETURN_TO_CANONICAL_RESEARCH_SEQUENCE
> NO_NEW_RQ
> NO_NEW_PRIMARY_ESTIMAND
> NO_NEW_DATA_SOURCE
> NO_MEASUREMENT_REOPEN

---

## 1. Trigger

The measurement foundation has been closed through G4 and the first
formal RQ1 inference has been executed on a dedicated branch.

The preceding fast-track orchestration achieved its purpose:
it produced the first statistical result without reopening D-02/D-03/D-04.

Further orchestration-layer growth is now terminated.

The project returns to the canonical SSOT notebook / RQ sequence.

---

## 2. Git state at decision

Canonical main:

79490b723ff4413763a84d310e50fa2748ccca6c

RQ1 branch:

research/nb08-rq1-primary-20260817

Current RQ1 branch HEAD:

e893eef1a5c9b8120fecd0daf68fe71898ab1e13

Primary RQ1 result commit:

502bc128f6b5855f1648802cc990b715808f26f3

Pre-result commits:

Decision:
e72274086a7e9c611c9014e6b5612df0e69dae30

Cohort:
9b695307c0551be84d4d6c374646bfe001b7b3a9

Protocol:
86521fdf04839d2e3e8e5db8e15a08ea067871e3

---

## 3. Current Gate board

G0 PASS / CLOSED
G1 PASS / CLOSED
G2 PASS / CLOSED
G3 PASS / CLOSED
G4 PASS / CLOSED

G5 OPEN

G6 NOT OPEN

Measurement foundation:

D-02 FROZEN
D-03 FROZEN
D-04 FROZEN

No D-02/D-03/D-04 regeneration is authorized by this decision.

---

## 4. RQ1 current status

The first formal RQ1 execution exists.

Primary cohort:

N = 3,835,988

Primary estimand:

Median(log_token_premium)

Observed primary point estimate:

Median(logTP)
=
0.28768207245178085
=
ln(4/3)

TP-scale median quantity:

exp(Median(logTP))
=
1.3333333333333333

Descriptive polarity:

positive:
3,375,095

negative:
264,175

exact zero:
196,718

share(TP > 1):
0.8798502498

The result is based on the physical D-04 artifact, not EDA V2.

---

## 5. RQ1 evidence classification

Current status:

RQ1_FIRST_RESULT_EXECUTED

Evidence level:

LEVEL_5_CANDIDATE

The result is not yet declared canonical-close because a bounded
methodological closeout remains.

Required closeout:

1. preserve the existing frozen primary protocol and result;
2. retain the Wilcoxon signed-rank as the SSOT primary test;
3. distinguish the existing zero-excluded sign test from a direct
   median-with-ties robustness statement;
4. add a tie-aware conservative sign robustness check;
5. perform source-stratified bootstrap sensitivity consistent with
   SSOT §17.2;
6. clarify that underflow log10-p values are approximation diagnostics;
7. preserve the bootstrap-CI degeneracy explanation without claiming
   infinite precision;
8. merge the closed RQ1 evidence into main.

No new exploratory sensitivity family is authorized in this closeout.

---

## 6. NB08 CI interpretation

The primary pair-level percentile bootstrap produced:

[0.28768207245178085,
 0.28768207245178085]

This is not classified as an implementation failure.

The median is located on a large discrete point mass caused by integer
token-count ratios.

Therefore:

DEGENERATE_BOOTSTRAP_CI
=
VALID_OBSERVED_PROPERTY_OF_CURRENT_ESTIMATOR_AND_RESAMPLING_SCHEME

It must not be presented as infinite numerical precision.

A bare interval without the discreteness caveat is prohibited.

---

## 7. Canonical execution sequence from this decision

The active research sequence becomes:

1. NB08 RQ1 method closeout
2. NB06 regex chunk audit / D-05
3. G5 Analysis Readiness
4. NB07 canonical EDA and decomposition
5. NB09 explanatory models
6. NB11 robustness / sensitivity
7. NB10 predictive analysis
8. NB13 release
9. Track B / NB12 only after Track A core results are stable, unless
   separately reauthorized earlier

NB08 has already executed out of order under the prior approved fast-track.
After its closeout, the project resumes at the earliest unfinished canonical
measurement notebook: NB06.

---

## 8. Prior Director decisions retained

RD-FAST-G5-01 is not revoked in substance.

The following approved realized-data decisions remain active:

- sentence_type is excluded from realized model matrices because it is
  zero-variance and non-estimable;
- logical_corpus is provenance/descriptive only when source_id is used,
  because the two are bijective in the realized cohort;
- source_domain_cell is the primary realized metadata control;
- pair_log_size is the approved absolute pair-size parameterization;
- deterministic/compositional redundancy is removed before empirical
  collinearity diagnostics;
- predictive split / LR-01 grouping remains relocated to a PRE-NB10
  hard prerequisite.

What is superseded is only the previous orchestration-heavy parallel
execution style.

---

## 9. NB06 role

NB06 is the final unfinished Track-A measurement notebook.

Its purpose is:

D-05 Regex Chunk Measurement

and the RQ5 / M3 mechanism layer.

It must preserve the SSOT distinction:

linguistic morphology
!=
o200k_base regex chunking
!=
final subword tokenization

NB06 is not a second tokenizer outcome factory.

D-04 remains the authority for final token IDs/counts and TP.

---

## 10. NB06 engineering prerequisite

R1 execution-observability debt must be corrected before a new
full-population heavy run.

Required:

periodic telemetry throughout execution, not only start/end samples.

At minimum:

timestamp
elapsed
progress
RSS
MemAvailable
swap state
vmstat si/so
final status

NB06 design, coding and bounded pilot may occur before the full-run
telemetry gate is satisfied.

NB06 full-population execution may not.

---

## 11. G5 role

After D-05 is persisted and validated, formal G5 is closed before
canonical explanatory analysis.

Following the already-approved split-relocation decision, G5 requires:

1. analysis cohort freeze;
2. realized-model identifiability;
3. collinearity/composition diagnostics on the actual planned model
   matrices.

Predictive split / near-duplicate leakage control is handled at PRE-NB10,
not as a blocker for NB07/NB09.

G5 must not become an open-ended audit of every possible feature combination.

---

## 12. G5 realized-model contract

Primary realized M0:

logTP
~
pair_log_size
+
source_domain_cell
+
translation_direction

M1:

M0
+
approved nonredundant representation / surface block

M2:

M1
+
morpheme_density
+
particle_ratio
+
ending_ratio
+
deriv_affix_ratio

M2A sensitivity:

M1
+
morpheme_density
+
function_morpheme_ratio
+
deriv_affix_ratio

M3:

M2
+
validated D-05 tokenizer-mechanism block

No independent sentence_type coefficient is estimated.

logical_corpus and source_id are not jointly entered.

---

## 13. G5 diagnostic principle

Diagnostics are run only on the actual planned reduced matrices.

Before empirical diagnostics:

- exact identities removed;
- zero-variance variables removed;
- categorical bijections removed;
- composition constraints resolved.

Hard blocker:

rank deficiency after intended parameterization.

Existing Director review triggers remain:

condition number >= 100
→ reparameterization review

VIF/GVIF >= 20
→ strong redundancy review

|Spearman rho| >= 0.95 within the same construct family
→ representative-feature review

No feature is dropped merely because a p-value is small or because
sample size is large.

---

## 14. NB07 role

NB07 becomes the canonical descriptive science notebook.

It must compute directly from canonical D-02/D-03/D-04/D-05 artifacts.

EDA V1/V2 values may guide inspection but are not numerical authorities.

NB07 will canonicalize:

- TP / logTP distributions;
- exact decomposition;
- representation reversal;
- morphology distributions;
- tokenizer regex-chunk distributions;
- domain/source/direction/length descriptive heterogeneity;
- validated extreme-case audit;
- RQ1 result annotation.

No new inferential hypothesis is created in NB07.

---

## 15. NB09 role

NB09 provides the primary explanatory analysis.

The central questions are block-level:

RQ3:
M1 versus M0

RQ4:
M2 versus M1

RQ5:
M3 versus M2

Primary interpretation prioritizes:

incremental / partial R²
model-level improvement
coefficient magnitude
model stability

over individual coefficient p-values.

Morphology or regex-chunk features are interpreted as conditional
associations / explanatory information, not causal effects.

---

## 16. NB11 / NB10 order

Scientific priority after NB09 is robustness.

NB11 may be completed before NB10 even though the numeric filename of
NB10 precedes NB11.

This is an execution-priority decision, not a rename.

NB11 closes:

- direction sensitivity;
- short / one-eojeol boundary sensitivity;
- morphology-block specification sensitivity;
- source/dependence-sensitive inference;
- main explanatory-result stability.

Only then is predictive work prioritized.

---

## 17. PRE-NB10

Before NB10:

- near-duplicate/paraphrase grouping;
- leakage-group audit;
- split manifest;
- holdout/fold freeze;
- zero train/test group overlap

must be complete.

LR-01 remains fully binding.

The requirement has been moved, not removed.

---

## 18. No further orchestration expansion

The following are not authorized unless a concrete scientific need appears:

- new orchestration framework;
- EDA V3;
- new workflow matrix families;
- new primary metric;
- new tokenizer;
- new language;
- new corpus;
- new model family;
- broad feature fishing.

Each stage produces only the artifact needed by the next research stage.

---

## 19. Active ownership

Claude-B / Research-Statistics:

- NB08 RQ1 closeout;
- G5 research adjudication;
- NB09 explanatory statistics;
- NB11 robustness.

Claude-A / Engineering-Reproducibility:

- R1 runtime telemetry;
- NB06 implementation;
- D-05 full measurement;
- schema/hash/tests/reproducibility.

DataViz / Descriptive Research Agent:

- NB07 canonical descriptive analysis and figures,
  only after G5 PASS.

No agent edits another active stage's files.

---

## 20. Immediate stop conditions

All analysis stops only for:

- canonical artifact hash mismatch;
- pair-set mismatch;
- material measurement corruption;
- rank deficiency unresolved in the intended model;
- NB06 mechanism-validation failure;
- direct conflict with KOEN-TP-RS-001 or an approved Director decision.

Minor documentation debt does not block science execution.

---

## 21. Director verdict

APPROVED.

ORCHESTRATION-HEAVY FAST TRACK IS CLOSED.

THE PROJECT RETURNS TO THE SSOT CANONICAL RESEARCH PATH.

Immediate next action:

NB08 RQ1 closeout.

After NB08 is merged:

NB06 becomes the sole active canonical production stage.

---

---

# Verification notes — Claude-A, not part of the Director decision

Appended below the rule so it cannot be mistaken for Director text. The decision above is persisted
verbatim; all 21 sections are unmodified.

## V1. Git state in §2 — verified against the remote

| assertion | resolved ref | result |
|---|---|---|
| canonical main `79490b72…` | `origin/main` | MATCH |
| RQ1 branch HEAD `e893eef1…` | `origin/research/nb08-rq1-primary-20260817` | MATCH |
| decision `e7227408…` | commit subject `docs(rq1): freeze Director decision for first primary inference` | present |
| cohort `9b695307…` | `research(rq1): freeze primary analysis cohort` | present |
| protocol `86521fdf…` | `research(rq1): freeze NB08 inference protocol before execution` | present |
| primary result `502bc128…` | `research(nb08): execute RQ1 primary token-premium inference` | present |

The RQ1 branch is a descendant of `79490b72…` and is **not yet merged into `main`**, consistent with
§5 item 8 leaving the merge as remaining closeout work.

## V2. §4 figures — independently recomputed from the physical D-04 artifact

Recomputed directly from `TOKEN_O200K_BASE_v001.parquet`, not read from any report:

| quantity | decision | recomputed | result |
|---|---|---|---|
| N | 3,835,988 | 3,835,988 | MATCH |
| `Median(logTP)` | 0.28768207245178085 | 0.28768207245178085 | MATCH (bit-identical) |
| positive | 3,375,095 | 3,375,095 | MATCH |
| negative | 264,175 | 264,175 | MATCH |
| exact zero | 196,718 | 196,718 | MATCH |
| `share(TP > 1)` | 0.8798502498 | 0.8798502498 | MATCH |

Internal consistency also holds: 3,375,095 + 264,175 + 196,718 = 3,835,988, and the point estimate
is bit-identical to `math.log(4/3)`, so `exp(Median(logTP)) = 1.3333333333333333` as stated.

The 196,718 exact zeros are the reason §5 item 3 separates the zero-excluded sign test from a
median-with-ties statement, and they are the same discreteness that §6 identifies behind the
degenerate bootstrap interval. Both cautions are supported by the artifact.

## V3. §3 measurement foundation — re-verified

`REP_FEATURES_v002` `dfae8e01…`, `MORPH_FEATURES_KIWI_v001` `0fe5bd74…` and
`TOKEN_O200K_BASE_v001` `1c30e327…` all pass fail-closed identity assertion at N = 3,835,988 with
the shared pair-set hash. Nothing was regenerated; this decision authorizes no regeneration.

## V4. How this document was persisted

Written and committed in a dedicated isolated worktree branched from `origin/main`, per the standing
`ONE AGENT PER WORKING TREE` policy. The shared project working tree was not switched — it is
currently checked out on `research/nb08-rq1-primary-20260817`, where Claude-B is working — and no
other lane's files were staged, moved or modified.

Not merged to `main` by Claude-A.

## V5. Claude-A's lane under §19

Assigned: R1 runtime telemetry, NB06 implementation, D-05 full measurement, schema/hash/tests and
reproducibility. Current engineering status carried in: `R1 = NOT_FIXED`, `NB06 = NOT_STARTED`.

Per §7 and §21 the immediate next action belongs to Claude-B (NB08 RQ1 closeout), and NB06 becomes
the sole active canonical production stage after that merge. R1 telemetry is in Claude-A's lane and
is not blocked by the NB08 closeout; §10 permits NB06 design, coding and a bounded pilot before the
telemetry gate is satisfied, while prohibiting NB06 full-population execution until it is.
