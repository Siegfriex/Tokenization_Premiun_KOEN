# G5 Analysis Readiness — Entry Record

> Stage: `G5 — Analysis Readiness`
>
> Executor: Claude-B (Research / Statistics)
>
> Branch: `research/g5-analysis-readiness-20260818`
> Base: `origin/main` @ `4eaa35e8437fc9013305c2b3fcf53133f2a0bddf`
> (`merge: adopt audited G5 entry governance closeout`)
>
> Worktree: `/home/sieg/projects-wsl/KOEN_g5_readiness_20260818`
>
> Opened: 2026-08-18 13:12 KST

---

## 1. Authority chain

```
KOEN-TP-RS-001                        §12.2 D-02 · §12.3 D-03 · §12.5 D-05 · §13 features
                                      §16 EDA · §17 inference · §18 Outcome A/B · §19 M0–M3
                                      §20 source identifiability · §20.2 G-ID · §21 collinearity
                                      §31 G5 PASS conditions · §32 T-03/T-04/T-06

RD-FAST-G5-01                         §4 realized covariate decisions · §5 realized ladder
  CR-FAST-G5-REALIZED-MODEL-01        §4.1–4.4 · §5 · §6 fast collinearity policy · §7 cohort
  CR-FAST-G5-SPLIT-RELOCATION-01      §8 split relocation

RD-SSOT-CANONICAL-RETURN-01           §11 G5 role · §12 realized model contract · §13 diagnostic
                                      principle
RD-G5-ENTRY-GOVERNANCE-CLOSEOUT-01    governance prerequisites closed
```

Governance entry evidence on canonical `main`:

```
f786baa  canonical-return decision materialized (blob c7fdc7bf, byte-identical)
65ce14f  RQ1 evidence-of-record SHA corrected; three fail-closed lineage checks added
765f251  closeout §3.4 restored to primary RQ1 facts (audit finding M-01)
f8ff291  targeted re-audit — G5_ENTRY_GOVERNANCE_REAUDIT_PASS
4eaa35e  merge to main
```

---

## 2. Split-manifest override — recorded explicitly

`KOEN-TP-RS-001` §31 lists four G5 PASS conditions:

```
identifiability check
collinearity report
analysis cohort freeze
split manifest freeze          ← superseded for G5
```

`CR-FAST-G5-SPLIT-RELOCATION-01` (`RD-FAST-G5-01` §8, APPROVED) removes the split-manifest and
`LR-01` near-duplicate grouping requirement from the **universal G5 prerequisite** and relocates it
to **PRE-NB10 PREDICTIVE READINESS — HARD PREREQUISITE**, because NB07 descriptive, NB08 paired
inference and NB09 full-cohort explanatory analysis use no train/validation/test split.

Therefore, binding on this gate:

```
SPLIT_MANIFEST_IS_G5_PREREQUISITE = NO
SPLIT_MANIFEST_RELOCATED_TO       = PRE-NB10
LR-01_WEAKENED                    = NO
```

**The absence of a split manifest must not be scored as a G5 failure.** Before NB10 produces any
predictive result, leakage-group policy, near-duplicate grouping, holdout assignment, tuning/CV
assignment, split-manifest freeze and a train/test leakage audit all remain mandatory.

G5 therefore evaluates exactly three conditions:

```
1. analysis cohort freeze
2. realized-model identifiability
3. collinearity / composition on the actually planned model matrices
```

---

## 3. Prior scratch disclosure

A G5 working line was opened on 2026-08-17 and stopped uncommitted. It produced diagnostic numbers
and a `PASS_WITH_NOTES` adjudication draft that **were observed by this agent before the present
protocol was frozen.**

```
PRIOR_G5_SCRATCH_OBSERVED  = YES
PRIOR_G5_SCRATCH_EVIDENCE  = NO
PRIOR_G5_SCRATCH_LOCATION  = /home/sieg/projects-wsl/KOEN_g5
PRIOR_G5_SCRATCH_BRANCH    = scratch/g5-readiness-QUARANTINE-20260817  (renamed 2026-08-18)
PRIOR_G5_SCRATCH_STATE     = uncommitted · unpushed · no adjudication
CLASSIFICATION             = LOCAL_G5_SCRATCH_NOT_EVIDENCE
```

The project is **not result-blind** and this record does not pretend otherwise. Binding consequences:

- no scratch output, manifest, report or adjudication file is copied into this working line;
- no scratch numeric value is cited as evidence, quoted as a target, or used to decide whether a
  fresh number is acceptable;
- every predictor, removal, reference level and threshold in
  `02_G5_DIAGNOSTIC_PROTOCOL_v001.md` is derived from the authority chain in §1 and from the
  physical artifact schemas, and each carries its own citation;
- scratch **code** may be read only after this protocol is frozen and pushed, and only as an
  implementation reference — never as a source of specification.

If a fresh result disagrees with the observed scratch, the fresh result governs and the
disagreement is reported rather than reconciled.

---

## 4. Claim boundary at entry

Permitted at G5: statements about whether the approved design is estimable and numerically
acceptable on the frozen cohort.

Not permitted at G5 — no exception, regardless of what the diagnostics show:

```
any coefficient
any p-value narrative
partial R² · ΔR²
RQ3 / RQ4 / RQ5 substantive answers
any causal statement
any claim that morphology has or lacks incremental value
any claim that M3 explains fragmentation
```

`G5` does not fit the scientific explanatory model for interpretation. Fitting occurs at NB09.

---

## 5. Ownership and scope discipline

`RD-SSOT-CANONICAL-RETURN-01` §11: G5 must not become an open-ended audit of every possible feature
combination. Diagnostics run **only** on the actual planned reduced matrices defined in
`02_G5_DIAGNOSTIC_PROTOCOL_v001.md`. No feature is added, dropped or rescued on the basis of an
association with either outcome.

Working-tree isolation: this lane owns `/home/sieg/projects-wsl/KOEN_g5_readiness_20260818` only.
`/home/sieg/projects-wsl/KOEN_g5_v2` is a different active lane
(`results/eda-g5-candidate-v001-20260818`) and is not touched.
