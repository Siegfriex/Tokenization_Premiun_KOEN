# KOEN — PRE-NB09 Independent Audit Harness

> Artifact ID: `PRE_NB09_AUDIT_HARNESS_v001`
>
> Status: `READY` · `AWAITING_EXECUTOR_PROTOCOL` · `NOT_A_PROTOCOL` · `NOT_A_DECISION`
>
> Prepared by: Claude-A (Engineering / Reproducibility Auditor)
> Prepared: 2026-08-18 14:55 KST
>
> Base: `origin/main` @ `9fbcf0c127c804e8682edf1a1f14c3eea0e423a0`
> Branch: `audit/pre-nb09-harness-20260818`
> Worktree: `/home/sieg/projects-wsl/KOEN_audit_prenb09_20260818`
>
> Authority: `KOEN-TP-RS-001` §19 · §20 · §20.2 · §21 · §31 · §32 →
> `RD-FAST-G5-01` §6 · `CR-FAST-G5-REALIZED-MODEL-01` ·
> `RD-SSOT-CANONICAL-RETURN-01` §11 · §13 · `RD-G5-ENTRY-GOVERNANCE-CLOSEOUT-01`

---

## 0. What this is, and what it deliberately is not

Claude-B will freeze a PRE-NB09 protocol. This document and
`scripts/audit_pre_nb09.py` are the machinery that will let that protocol be audited
independently, on the day it appears, without the auditor having to invent anything under
time pressure.

```
PREDICTOR CHOSEN            = NO
VARIABLE REMOVED            = NO
THRESHOLD SET BY AUDITOR    = NO
REFERENCE LEVEL FIXED       = NO
NUMERIC RESULT ASSERTED     = NO
MODEL FITTED                = NO
CANONICAL SCIENCE STATE     = UNCHANGED
```

The harness contains **no default variable list**. Run without a spec it refuses to start.
That is deliberate: an auditor who ships a default column inventory has pre-decided the thing
being audited, and would then be checking B's protocol against the auditor's own guess rather
than against the authority chain.

This is also not a review of `ssot_g5/04_PRE_NB09_REVIEW_PREPARATION.md` (`dd525ef`). That
document is `NOT_FROZEN · NOT_A_DECISION` by its own header, sits off canonical `main`, and
postdates the audited `35a40e7`. Nothing here evaluates it.

---

## 1. Branch immutability

Per the standing rule, the SHA an audit starts on is immutable for that audit.

```
AUDITED_G5_SHA        = 9d99e13026b89dcf7d8846d0c105a811f64274bc
AUDITED_SUBJECT_SHA   = 35a40e7c3541eff7a41ce853204409b128a6d676
G5 branch tip now     = dd525ef019c9dfe019db667799ce726f4943ce0f
```

`research/g5-analysis-readiness-20260818` moved past `35a40e7` after the audit closed. **That
is not a change of audit subject and does not reopen the G5 audit.** The audited chain is
pinned by SHA and is an ancestor of canonical `main`; the branch tip is free to move. Any
future audit of `dd525ef` or its successors is a new audit with its own subject SHA.

---

## 2. The seven checks

Fixed here, before B's protocol exists, so the audit cannot be shaped around what it finds.

| id | check | how it is decided |
|---|---|---|
| `C1` | exact predictor column inventory | every declared term must evaluate against the physical artifacts; every declared physical column must exist in that artifact's schema; realized categorical levels and the resulting reference level are reported; zero-variance design columns are a HARD FAIL |
| `C2` | outcome leakage | every structurally excluded column must be absent from the design; every identity cited to justify an exclusion is measured over the full cohort against a declared tolerance; no outcome expression may appear as a design term |
| `C3` | matrix rank | rank of the standardized design from the exact Gram; deficiency > 0 is HARD FAIL |
| `C4` | standardized condition number | `σ_max/σ_min` of the standardized design; threshold from the spec |
| `C5` | VIF / GVIF | `VIF_j = [R⁻¹]_jj`; Fox–Monette `GVIF^(1/(2·df))` per categorical block |
| `C6` | same-construct structural relationship | Spearman within declared families only, full cohort, no sampling and therefore no seed |
| `C7` | block nesting consistency | each declared chain must be a strict subset ladder; declared mutually-exclusive column sets must never co-occur in one model |

`C0` prerequisites run first: artifact SHA-256 rehash, cohort N, distinct id count, pair-set
hash, join preservation, non-finite scan.

### 2.1 Why `C2` is structural and not a projection test

The obvious leakage test — project the outcome onto the design's column space and look at the
residual — produces a fit statistic. A readiness gate may not produce one
(`RD-SSOT-CANONICAL-RETURN-01` §13; the G5 claim boundary). So `C2` tests the *algebra*:
every exclusion must be justified by an identity, and that identity is measured on the full
cohort. If a column reconstructs the outcome, the identity says so at machine precision and
no fit is required.

The projection test is therefore **available but not implemented**. If the Director wants it,
it needs explicit authorization and should be classed as a fit, not as a readiness check.

---

## 3. The audit spec — the interface B's protocol must survive

The harness reads one JSON file that transcribes B's frozen protocol. `--emit-schema` prints
the full JSON Schema. The required top-level keys:

```
spec_id · protocol_id · protocol_commit · base_main_sha
artifacts   logical name -> {path, sha256}          rehashed before anything else
spine       which artifact defines the cohort
cohort      id column, expected N, expected pair-set hash
columns     term -> {kind, sql, artifact, physical_column, derived_from,
                     reference_rule, reference_level}
models      model name -> list of column keys       (intercept implicit)
outcomes    outcome -> {sql, models}
leakage     excluded[] with reason and class; identities[] with sql and tolerance
families    same-construct family -> column keys
nesting     chains[] and mutually_exclusive[]
conventions condition_number_includes_intercept · spearman_tie_handling ·
            standardize_dummies
thresholds  rank_deficient · condition_number · vif · abs_spearman
```

Fail-closed behaviour on the spec itself: unknown top-level keys, missing required keys, a
model referencing an undeclared column, a family referencing an undeclared column, or an
outcome referencing an unknown model all raise `SpecError` before any data is read.

### 3.1 Conventions are declared, not assumed

The G5 audit produced note `A-01`: B's raw-coding condition number excluded the intercept
column while the auditor's included it, because protocol §8 did not say. The values reconciled
exactly once the convention was known, and it was a non-trigger quantity, so nothing moved —
but the ambiguity cost a reconciliation step.

The spec now forces three such choices to be stated up front, and the harness echoes them into
its own output:

```
condition_number_includes_intercept   true | false
spearman_tie_handling                 midrank | competition
standardize_dummies                   true | false
```

`spearman_tie_handling` earns its place. During the G5 audit this auditor's first pass used
DuckDB `rank()` — competition ranking — on heavily tied integer counts and produced 0.9998 and
0.9952 where mid-rank gives 0.9994 and 0.9910. Both crossed 0.95, so the verdict was
unaffected, but on a closer pair the tie rule alone could decide whether a trigger fires. It
is now an explicit term of the contract rather than an implementation detail.

---

## 4. Harness validation against a known-good baseline

A harness that has never produced a correct number is not evidence. This one is regression-
tested against the **already audited and merged** G5 protocol v001, whose values are fixed on
canonical `main` and were independently confirmed at `9d99e13`.

```
scripts/audit_specs/G5_v001_regression.spec.json     protocol v001 transcribed
scripts/audit_specs/G5_v001_regression.expect.json   expected values from the closed audit
```

Result:

```
verdict = PRE_NB09_AUDIT_PASS_WITH_REVIEW    N = 3,835,988

model   p   rank  def   condition      max VIF
M0      8      8    0     10.2375       3.2465
M1     23     23    0     20.1005      12.9512
M2     27     27    0     20.9757      17.4665
M2A    26     26    0     20.9719      16.6896
M3     45     45    0    134.5680    1252.6087

review triggers: 3
  C4  M3 condition number 134.57 >= 100
  C5  M3 max VIF 1252.61 >= 20
  C6  script_mixing en_script_type_count ~ en_script_switch_count  rho 0.99935 >= 0.95

SELF_TEST = PASS
```

Every check fired at least once, all on `PASS` except the three known G5 review triggers:

```
C0_artifact_identity      5 PASS      C2_excluded_stays_out   23 PASS
C0_cohort_n               1 PASS      C2_identity_holds       11 PASS
C0_join_preserves_n       4 PASS      C2_outcome_not_on_rhs   10 PASS
C0_pair_set_md5           1 PASS      C3_rank                  5 PASS
C0_nonfinite              1 PASS      C4_condition_number      4 PASS / 1 REVIEW
C1_column_evaluable      41 PASS      C5_vif_gvif              4 PASS / 1 REVIEW
C1_physical_column_exists 36 PASS     C6_same_construct       10 PASS / 1 REVIEW
C1_reference_level        2 PASS      C7_nesting               5 PASS
C1_zero_variance          1 PASS      C7_mutual_exclusion     10 PASS

hard_fail = []      model_fitted = false      coefficient_produced = false
```

The fixture reproduces the closed audit's figures to the tolerances the self-test enforces —
rank exactly, condition number and max VIF to 1e-6 relative, family correlations to 1e-9
absolute. **This validates the harness. It does not re-audit G5, and it asserts nothing about
NB09.**

One correction made during preparation: the first expectation file recorded the `pair_scale`
correlation truncated to six decimals, which the 1e-9 comparison correctly rejected. The
expectation now carries full precision. Recorded rather than quietly fixed.

---

## 5. What is still unknown, by design

The harness cannot be pointed at anything until B's protocol exists, because these are all
B's to declare:

- which predictors enter NB09's matrices, and in what blocks;
- whether `M3-01` is resolved by reparameterization, by a representative rule, or by an
  interpretation restriction;
- which of `script_type_count` / `script_switch_count` represents the script-mixing construct,
  if either;
- whether the model ladder keeps the M0–M3 shape or changes;
- the reference-level rule and any change to thresholds.

The auditor will transcribe whatever B freezes and run the seven checks against it. If a
transcription is ambiguous the auditor asks rather than guesses, because a spec written from
the auditor's assumption audits the assumption.

---

## 6. Operating procedure when B's protocol lands

1. Pin the executor SHA. That SHA is the audit subject and is immutable for the audit; later
   tips do not change it.
2. Verify the protocol commit precedes the first result commit, in Git ancestry and in tree
   contents.
3. Transcribe the protocol into a spec JSON. Every value must trace to a protocol clause.
   Nothing gets filled in from memory of G5.
4. Fresh isolated audit worktree; `PYTHONPATH` forced to it; artifacts symlinked; offline
   tokenizer cache provisioned.
5. Run the harness. Compare its output to the executor's report field by field, not by
   invoking the executor's parser.
6. Report `HARD FAIL` / `REVIEW TRIGGER` / `NOTE` / `OPERATIONAL DEBT` separately, with no
   automatic promotion between registers.

---

## 7. Standing prohibitions for this lane

```
NO NB07 EXECUTION
NO NB09 FIT
NO COEFFICIENT
NO VARIABLE SELECTION BY THE AUDITOR
NO PROTOCOL AUTHORSHIP BY THE AUDITOR
NO RE-AUDIT OF CLOSED G5 SCIENCE
```

The auditor prepares the instrument. The executor writes the protocol. The Director decides.

---

## 8. Operational state at preparation time

Both G5 operational-debt items are closed:

| id | item | state |
|---|---|---|
| `OPS-G5-01` | D-05 absent from the canonical artifact store | **CLOSED** — independent copy placed, SHA `bfa98bd6…1944ab` reverified, distinct inode, link count 1, gitignored |
| `OPS-G5-02` | canonical working tree 17 commits behind | **CLOSED** — fast-forwarded to `9fbcf0c`; three preserved untracked recovery files intact with unchanged hashes |

Consequences confirmed in the canonical tree after the fast-forward: the editable install now
resolves `tokenization_premium.chunking` and `.telemetry` without any `PYTHONPATH` override,
276 tests pass, ruff is clean, and `scripts/validate_d05.py` — blocked since the first session
of this lane — runs unmodified and returns 17/17 `PASS`, rewriting its manifest byte-identically.
