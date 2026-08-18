# KOEN — G5 Analysis Readiness · Independent Audit

> Audit ID: `G5_INDEPENDENT_AUDIT_20260818`
>
> Auditor: Claude-A (Engineering / Reproducibility Auditor)
>
> Subject: `research/g5-analysis-readiness-20260818` @ `35a40e7c3541eff7a41ce853204409b128a6d676`
> Subject executor: Claude-B (Research / Statistics)
> Subject verdict under audit: `G5_ANALYSIS_READINESS_PASS_WITH_NOTES`
>
> Base: `origin/main` @ `4eaa35e8437fc9013305c2b3fcf53133f2a0bddf`
> Audit worktree: `/home/sieg/projects-wsl/KOEN_audit_g5_20260818`
> Executed: 2026-08-18 13:34–13:44 KST

Every number in §4, §6, §7 and §8 was recomputed by this auditor from the canonical parquet
artifacts. `scripts/g5_diagnostics_v001.py` was not imported, invoked or used as a specification
source; the design matrices were rebuilt from `ssot_g5/02_G5_DIAGNOSTIC_PROTOCOL_v001.md` §3, §4
and §8 alone. B's script was read only afterwards, and only to explain one non-trigger divergence
(§6.4).

---

## 1. SSOT reload and gate definition

Read for this audit: `KOEN-TP-RS-001` (REDLINE), `RD-FAST-G5-01` §4–§8,
`CR-FAST-G5-REALIZED-MODEL-01`, `CR-FAST-G5-SPLIT-RELOCATION-01`,
`RD-SSOT-CANONICAL-RETURN-01` §10–§13, `RD-G5-ENTRY-GOVERNANCE-CLOSEOUT-01`,
and B's `ssot_g5/01`, `ssot_g5/02`, `ssot_g5/03` plus the adjudication.

`KOEN-TP-RS-001` §31 lists four G5 PASS conditions. `CR-FAST-G5-SPLIT-RELOCATION-01`
(`RD-FAST-G5-01` §8, APPROVED) removes the fourth — split manifest and `LR-01` near-duplicate
grouping — from the universal G5 prerequisite and relocates it to PRE-NB10, because NB07, NB08 and
NB09 use no train/validation/test split. `RD-SSOT-CANONICAL-RETURN-01` §11 states the same three
remaining conditions.

```
G5 = analysis cohort freeze
   + realized-model identifiability
   + collinearity / composition on the actually planned matrices

predictive split / leakage grouping = PRE-NB10, NOT a G5 condition
LR-01 weakened = NO
```

**Audited:** B's `ssot_g5/01` §2 states this override explicitly and does not score the absent split
manifest as a failure. Correct. `SPLIT_MANIFEST_OVERRIDE = CORRECTLY_APPLIED`.

---

## 2. Chronology — protocol precedes results

```
4e9bab8  2026-08-18 13:16:00 +0900  research(g5): freeze realized analysis-readiness protocol
5edb784  2026-08-18 13:28:09 +0900  research(g5): execute fresh analysis-readiness diagnostics
35a40e7  2026-08-18 13:28:32 +0900  research(g5): adjudicate G5 analysis readiness
```

Ancestry verified with `git merge-base --is-ancestor`:

| ref | ancestor of G5 head |
|---|---|
| `4eaa35e` governance-final main | **YES** |
| `4e9bab8` pre-diagnostic protocol | **YES** |
| `5edb784` result | **YES** |

The protocol commit tree was enumerated in full. `4e9bab8` adds exactly three files —
`ssot_g5/01`, `ssot_g5/02`, `ssot_g5/03` — and `outputs/reports/G5_*` and
`outputs/manifests/ANALYSIS_COHORT_v001.json` are **absent** from it. `ssot_g5/03` is an artifact
SHA-256 identity check, a prerequisite verification, not a diagnostic result: it contains no rank,
condition number, VIF or correlation.

```
NO_RESULT_IN_PRE_DIAGNOSTIC_COMMIT = CONFIRMED
G5_AUDIT_FAIL_POSTHOC_PROTOCOL     = NOT TRIGGERED
```

This auditor separately observed the working tree at 13:33, before the result commits were
examined, and found the cohort script and its manifest carrying mtimes of 13:18–13:19 — after the
13:16 protocol freeze. The ordering is corroborated by filesystem state, not only by commit dates.

---

## 3. Old-scratch contamination

The 2026-08-17 line is at `/home/sieg/projects-wsl/KOEN_g5`, branch renamed to
`scratch/g5-readiness-QUARANTINE-20260817`, still five untracked files, undamaged and uncommitted.

Provenance audit — equality was not used as the test; origin was:

| check | result |
|---|---|
| old adjudication copied into the new line | **NO** — old `fe298388…`, new `51c55db0…`, different filename and date |
| old cohort manifest carried forward | **NO** — old `fa2eaee7…` 3,794 B, new `88a5e17d…` 11,190 B |
| old scripts carried forward | **NO** — old `g5_cohort_and_screening.py` / `g5_diagnostics.py` / `g5_emit_outputs.py`; new `g5_build_cohort.py` / `g5_diagnostics_v001.py`, different hashes |
| any new artifact citing the scratch path, file or value | **NO** — grep over `ssot_g5/`, the three G5 reports, the cohort manifest and both scripts returns nothing |
| fresh run IDs and telemetry | **YES** — `G5_DIAG_PASS1` / `G5_DIAG_PASS2` / `G5_DIAG_SPEARMAN`, three fresh telemetry blocks |

The disclosure in `ssot_g5/01` §3 — that the scratch numbers **were seen** before the protocol was
frozen — is the honest statement, and the audit does not treat prior observation as contamination.
What matters is whether the frozen protocol is derivable from authority independently of what was
seen. It is: this auditor reconstructed every column list in §4 of the protocol from
`RD-FAST-G5-01` §5, `CR-FAST-G5-REALIZED-MODEL-01` §4.1–§4.4 and SSOT §18.1 without consulting the
scratch, and obtained the same lists.

Two divergences from the scratch are load-bearing evidence *against* contamination:

- the scratch ran M1/M2/M2A at 21/25/24 columns; the fresh protocol runs 23/27/26. This auditor
  independently derived 23 for M1 (8 + 15 §18.1/§12.2 terms) from the authority chain;
- the scratch removed `log_pair_chunk_ratio` **after** observing a rank deficiency of 1; the fresh
  protocol excludes `pair_chunk_ratio` structurally in §6.2 ex ante, on the identity
  `ln(pair_chunk_ratio) = ko_chunk_count_log − en_chunk_count_log`, which this auditor verified to
  8.88e-16.

Fresh code is not a copy of scratch code, so the "old code reuse" allowance is not even exercised.

```
OLD_SCRATCH_USED_AS_EVIDENCE = NO
OLD_G5_SCRATCH_CLASSIFICATION = LOCAL_G5_SCRATCH_NOT_EVIDENCE
```

---

## 4. Artifact identity — independently rehashed

`sha256sum` run by this auditor on the physical files, not read from any manifest:

| | expected | measured | |
|---|---|---|---|
| D-01 `PAIR_REGISTRY_v002` | `95f523d1…10bec52` | `95f523d1…10bec52` | **MATCH** |
| D-02 `REP_FEATURES_v002` | `dfae8e01…50d309` | `dfae8e01…50d309` | **MATCH** |
| D-03 `MORPH_FEATURES_KIWI_v001` | `0fe5bd74…3e50f7d` | `0fe5bd74…3e50f7d` | **MATCH** |
| D-04 `TOKEN_O200K_BASE_v001` | `1c30e327…2c16e7` | `1c30e327…2c16e7` | **MATCH** |
| D-05 `CHUNK_O200K_BASE_v001` | `bfa98bd6…1944ab` | `bfa98bd6…1944ab` | **MATCH** |

All three physical D-05 copies on this host (`KOEN_nb06_d05`, `KOEN_g5_readiness_20260818`,
`KOEN_g5_v2`) hash identically. This audit read the `KOEN_nb06_d05` copy — a different physical file
from the one B read — and reached the same numbers.

Cohort, recomputed from the D-04 spine:

```
N                     3,835,988      matches
distinct pair_id      3,835,988      equals N
pair-set md5          d9660d654ee449e4d0c23a0070225274      matches
join D-04 × D-01/D-02/D-03/D-05      3,835,988 each — every join preserves N exactly
non-finite over all 39 design columns 0
min ko/en_codepoint_count             1, 1   (> 0)
min ko/en_chunk_count                 1, 1   (> 0)
```

```
ARTIFACT_IDENTITY_5_OF_5 = YES
```

---

## 5. Model contract

The approved column lists were reconstructed from `RD-FAST-G5-01` §5 and
`CR-FAST-G5-REALIZED-MODEL-01` §4, then compared to B's protocol §4.

| requirement | authority | audited |
|---|---|---|
| `sentence_type` absent | `CR` §4.1 | **PASS** — absent from all five matrices; re-measured: one realized level over 3,835,988 rows |
| `logical_corpus` absent with source control present | `CR` §4.2 | **PASS** — absent; re-measured bijective with `source_id`, 2 ↔ 2 |
| `source_domain_cell` the primary metadata control | `CR` §4.3 | **PASS** — 5 realized cells, no independent `source_id` or `domain` main effect anywhere |
| `pair_log_size` exact formula | `CR` §4.4 | **PASS** — `0.5·(ln C_KO + ln C_EN)`, no `+1` smoothing; auditor rebuilt the column from this formula |
| `function_morpheme_ratio` never with `particle_ratio` + `ending_ratio` | `CR` §5, SSOT §12.3 | **PASS** — M2 and M2A are disjoint alternatives; the universe column is present but never selected into the same design |
| reference-coded script composition | SSOT §21 | **PASS** — `ko_hangul_share` and `en_latin_share` excluded definitionally as each side's native script; `*_chunk_type_share_letter` as the base chunk class |
| no deterministic accounting identity duplicated | `CR` §6 Step 1 | **PASS** — see below |
| no outcome leakage | `RD-FAST-G5-01` §5 M1 | **PASS** — see below |
| no outcome-driven feature removal | `CR` §6 | **PASS** — every §5/§6 exclusion is justified by an identity this auditor verified numerically, never by an association with either outcome |

Ladder dimensions independently derived and confirmed: M0 = 1 + 1 + 4 + 2 = 8; M1 = 8 + 15 = 23;
M2 = 23 + 4 = 27; M2A = 23 + 3 = 26; M3 = 27 + 18 = 45.

### 5.1 Identity verification behind the structural exclusions

Recomputed over the full cohort by this auditor:

| identity | max abs error | consequence had it been ignored |
|---|---|---|
| `logCR + logBDR + logCP = log_token_premium` | 8.88e-16 | G2 decomposition still holds |
| `ln(ko_tpb) − ln(en_tpb) = log_compression_penalty` | 4.44e-16 | admitting `*_tokens_per_byte` **is** Outcome B on the RHS |
| `ln(pair_byte_ratio) = logCR + logBDR` | 8.88e-16 | exact duplicate of two M1 terms |
| `ln(pair_chunk_ratio) = ko_chunk_count_log − en_chunk_count_log` | 8.88e-16 | exact duplicate inside M3 |
| `ko_chunk_token_total = ko_token_count` | **0.0** | admitting it puts the token count, hence `logTP`, on the RHS |
| `en_chunk_token_total = en_token_count` | **0.0** | same |
| `ko_chunk_byte_total = ko_utf8_bytes` | **0.0** | deterministic duplicate of D-02 |
| `ko_tokens_per_chunk × ko_chunk_count = ko_chunk_token_total` | 5.68e-14 | with `chunk_count` in M3, admits the token total |
| `ko_whitespace_count = ko_whitespace_density × ko_codepoint_count` | 1.42e-14 | deterministic duplicate |

Leakage direction check: Outcome A's design carries `logCR` and `logBDR` but not `logCP`, so `Y_A`
is not reconstructible; Outcome B's design carries the same two but not `logTP`, so `Y_B` is not
reconstructible. The two outcomes share one right-hand side. **Neither self-reconstructs.**

### 5.2 Composition closure

| composition | max abs deviation |
|---|---|
| KO script shares + `ko_whitespace_density` = 1 | 2.22e-16 |
| EN script shares + `en_whitespace_density` = 1 | 2.22e-16 |
| KO chunk-type shares = 1 | 2.22e-16 |
| EN chunk-type shares = 1 | 2.22e-16 |

The five D-02 script shares alone sum to as little as 0.545 (KO) — whitespace is a separate share of
the codepoint total. B's cohort manifest records the closure in the correct
`shares + whitespace_density == 1` form. The collinearity report's one-line
`"VALID (reference-coded; see cohort manifest closure errors)"` is a pointer, not the statement, and
resolves correctly. `COMPOSITION_STATUS = VALID`, confirmed.

```
MODEL_CONTRACT_MATCH = YES
```

---

## 6. Independent numerical recomputation

Method deliberately different from B's. B used a streaming Householder QR on the standardized
design and took singular values from the `R` factor. This auditor accumulated the **centred
cross-product matrix** in two streaming passes (means, then `Σ(z−z̄)(z−z̄)ᵀ`) and derived rank,
condition number, VIF and GVIF from the exact Gram of the standardized design. Two different
numerical routes over the same artifacts.

### 6.1 Rank and condition number

| model | p | A rank | B rank | A cond (std) | B cond (std) | rel. diff |
|---|---|---|---|---|---|---|
| M0 | 8 | **8** | 8 | 10.23754405 | 10.23754422 | 1.6e-08 |
| M1 | 23 | **23** | 23 | 20.10054416 | 20.10054675 | 1.3e-07 |
| M2 | 27 | **27** | 27 | 20.97573207 | 20.97573477 | 1.3e-07 |
| M2A | 26 | **26** | 26 | 20.97189644 | 20.97189915 | 1.3e-07 |
| M3 | 45 | **45** | 45 | 134.5679826 | 134.5679824 | 1.3e-09 |

Rank deficiency is **0** in every model, by exact integer agreement. `RANK_DEFICIENT` — the only
HARD FAIL in the threshold table — is not present.

### 6.2 VIF and GVIF

| model | A max VIF | B max VIF | rel. diff | A GVIF^(1/2df) cell | B | A dir | B |
|---|---|---|---|---|---|---|---|
| M0 | 3.246452195 | 3.246452195 | 2.9e-12 | 1.188503142 | 1.188503142 | 1.095643526 | 1.095643526 |
| M1 | 12.95115335 | 12.95115333 | 1.6e-09 | 1.276681192 | 1.276681192 | 1.147107106 | 1.147107106 |
| M2 | 17.46649919 | 17.46649916 | 2.1e-09 | 1.283764924 | 1.283764924 | 1.149488246 | 1.149488246 |
| M2A | 16.68963671 | 16.68963668 | 1.9e-09 | 1.281987969 | 1.281987969 | 1.148638860 | 1.148638860 |
| M3 | 1252.608678 | 1252.608683 | 4.1e-09 | 1.343590729 | 1.343590730 | 1.155075868 | 1.155075868 |

All 30 per-column VIF entries B reports in `top_vif` were recomputed; maximum relative difference
**4.1e-09**. Categorical GVIF^(1/2df) stays in 1.10–1.34 across all five models: the categorical
coding is not a source of collinearity pressure.

### 6.3 Same-construct Spearman

All 49 within-family pairs across the 11 families of protocol §9 were recomputed with mid-rank tie
handling on the full cohort. **Maximum absolute difference from B: 5.7e-14.**

Exactly one family crosses `|ρ| ≥ 0.95`, in both computations:

```
script_mixing   en_script_type_count ~ en_script_switch_count   +0.9993520546
                ko_script_type_count ~ ko_script_switch_count   +0.9910090163
```

No other family fires. `d05_chunk_scale` at 0.9367639283 is the nearest miss and is correctly not
triggered.

A caution on this auditor's own first pass: an initial run used DuckDB `rank()`, which is
competition ranking, and produced 0.9998 / 0.9952 — inflated, because these are heavily tied integer
counts. Mid-rank is the correct Spearman definition and reproduces B exactly. **B's tie handling is
right and this auditor's first attempt was not.** Recorded so the correction is visible rather than
silently dropped.

### 6.4 The one divergence — `condition_number_raw_coding_not_a_trigger`

| model | A (intercept included) | B | A (intercept excluded) |
|---|---|---|---|
| M0 | 44.91305629 | 36.57617768 | **36.57617768** |
| M1 | 5240.628638 | 5110.546491 | **5110.546491** |
| M2 | 5836.825328 | 5712.991407 | **5712.991407** |
| M2A | 5841.983595 | 5719.033858 | **5719.033858** |
| M3 | 33633.72123 | 33381.30793 | **33381.30793** |

Fully explained: B computes this quantity on the design **without** the intercept column
(`Graw = G[np.ix_(ii, ii)]`, `ii` being the non-intercept indices). Under that convention this
auditor reproduces every value to ten significant figures.

Protocol §8 defines the standardized figure as the trigger quantity and says the raw-coding figure
is "also reported, explicitly **not** a trigger", without specifying intercept treatment. B's choice
is therefore not a protocol violation, and it cannot move any verdict — the trigger quantity agrees
to 1.3e-07. Recorded as **`A-01` (NOTE)**: state the intercept convention if this figure is quoted
in a later document.

```
NUMERICAL_RECOMPUTATION_MATCH = YES
  all trigger quantities agree; rank agrees exactly;
  the single non-trigger divergence reconciles exactly under B's stated-in-code convention
```

### 6.5 Independent characterization of the M3 trigger

Not required by the audit brief, but it settles whether M3-01 is a defect or a parameterization
question. `chunk_count × mean_chunk_bytes = utf8_bytes` holds to 1.14e-13, so on the log scale
`ln(chunk_count) + ln(mean_chunk_bytes) = ln(utf8_bytes)` holds to 8.88e-16. M3 carries
`*_chunk_count_log` on the log scale but `*_mean_chunk_bytes` on its native scale, so the relation
is near-exact yet **not linear** — which is precisely why VIF reaches 1,252 while the design stays
full rank. B's classification of `M3-01` as a reparameterization question rather than a structural
defect is correct.

---

## 7. Identifiability — recomputed

| measurement | A independently measured | B reported | |
|---|---|---|---|
| sources / domains / directions | 2 / 4 / 3 | 2 / 4 / 3 | match |
| observed `source × domain` cells | 5 | 5 | match |
| domains shared across all sources | `['other']` | `['other']` | match |
| additive `source + domain` design over observed cells | 5 params, rank 5, **0 residual df** | `separately_identifiable = false` | match |
| reference `source_domain_cell` | `025-…-other` (n 1,165,510, largest) | same | match |
| reference `translation_direction` | `KO_TO_EN` (n 2,512,152, largest) | same | match |
| empty `cell × direction` combinations | 3 | 3 | match |
| near-singleton `cell × direction` | `025-…-general × UNKNOWN` n=31; `026-…-other × UNKNOWN` n=1 | same | match |
| `sentence_type` zero variance | true (single level `other`) | true | match |
| `logical_corpus` bijection | true, 2/2/2 | true, 2/2/2 | match |
| zero-variance design columns | none | `[]` | match |

The additive `source + domain` design is exactly saturated on the 5 observed cells — 5 parameters,
rank 5, nothing left over. Source and domain therefore cannot be separated from the composite cell,
which is what `COMPOSITE_CELL_CONTROL_ONLY` asserts. `026` contains **zero** `EN_TO_KO` rows, so the
direction contrast is identified from within-`025` variation only, and `cell × direction` is not
estimable. Both are correctly filed as `NOTE` (`ID-03`, `ID-04`), not as HARD FAIL: the approved
design already uses the composite cell, and no interaction was introduced.

---

## 8. Threshold and register semantics

Thresholds reconstructed from `RD-FAST-G5-01` §6 Step 3 and compared to protocol §10 and to what the
adjudication actually did:

| threshold | authority | protocol §10 | applied as |
|---|---|---|---|
| rank deficient | HARD STOP | HARD FAIL / HARD STOP | not triggered |
| condition ≥ 100 | reparameterization trigger | `REPARAMETERIZATION_REVIEW` | M3 → `M3-01` REVIEW |
| VIF/GVIF ≥ 20 | strong review trigger | `STRONG_REDUNDANCY_REVIEW` | M3 → `M3-01` REVIEW |
| \|ρ\| ≥ 0.95 same construct | redundancy review | `REPRESENTATIVE_FEATURE_REVIEW` | `script_mixing` → `SM-01` REVIEW |

Audited behaviour:

- **no review trigger was promoted to a failure.** M3 fires both collinearity triggers and is still
  recorded `PASS` on rank with a pre-fit resolution requirement;
- **no variable was deleted on a VIF, a condition number or a correlation.** Every removal in §5/§6
  of the protocol is an identity this auditor verified numerically, frozen before execution;
- **no reference level was re-selected in response to a diagnostic.** Composition references are
  definitional (native script, base chunk class); categorical references follow the "largest
  realized level" rule frozen in §8, and this auditor obtained the same two levels from the counts;
- the four registers — HARD FAIL / REVIEW TRIGGER / NOTE / OPERATIONAL DEBT — are kept separate in
  §8.1 with no automatic promotion between them.

No separate scientific non-identifiability accompanies either review trigger: M3 is full rank, and
the script-mixing pair is near rank-equivalent but not rank-equivalent (VIF ≈ 9). Escalating either
to a G5 failure would be unsupported.

---

## 9. Science boundary

Scanned the adjudication, all three `ssot_g5` documents and the three G5 report JSONs for
coefficient, p-value, R², ΔR², predictive-performance and causal language. Every hit is a
prohibition or a boundary statement; none is a claim.

```
RQ3 coefficient interpretation      NOT PRESENT
RQ4 morphology conclusion           NOT PRESENT
RQ5 causal / mechanism conclusion   NOT PRESENT
p-value fishing                     NOT PRESENT — no p-value anywhere
ΔR² result                          NOT PRESENT
predictive performance              NOT PRESENT
```

The adjudication's §9 explicitly denies that any explanatory result exists, that morphology has or
lacks incremental value, that any coefficient was estimated, that source and domain were separated,
that M3 is ready to fit, or that regex chunking explains fragmentation. `SCIENCE_BOUNDARY = CLEAN`.

---

## 10. Tests, lint, hygiene

Run in this isolated audit worktree with `PYTHONPATH` forced to
`/home/sieg/projects-wsl/KOEN_audit_g5_20260818/src`; import root verified to resolve there, not to
the stale canonical tree.

```
pytest -q                    276 passed
ruff check src tests scripts All checks passed   (ruff 0.16.3)
```

Change-set hygiene over `4eaa35e..35a40e7` — 11 files, all text:

```
no parquet · no xlsx · no csv · no jsonl · no binary
no raw KO/EN text     — 0 Hangul characters across the three G5 report JSONs
no pair_id list       — the string "pair_id" occurs 0 times in the three reports
no token / chunk string, no numeric array longer than 60 elements
```

### 10.1 The `.gitignore` line — reviewed as requested

```
+# G5 analysis-readiness reports: aggregate diagnostics only — no raw text, no pair_id,
+# no token/chunk string. Required as G5 evidence by G5_DIAGNOSTIC_PROTOCOL_v001 §12.
+!outputs/reports/G5_*
```

**Justified.** `outputs/**` is ignored wholesale and re-admitted family by family
(`ENVIRONMENT_*`, `PAIR_REGISTRY_RECONCILIATION_*`, `LEGACY_REFERENCE_AUDIT_*`); this line follows
that established pattern rather than widening it. It currently admits exactly the three files
protocol §12 requires as evidence, and the content scan above confirms the comment's claim. It does
not reach `outputs/manual_audit/`, which stays ignored, nor any parquet. Approved.

---

## 11. Findings

**HARD FAIL — none.**

**NOTE**

| id | finding |
|---|---|
| `A-01` | `condition_number_raw_coding_not_a_trigger` is computed without the intercept column. Protocol §8 does not specify the convention, and the quantity is explicitly not a trigger. Reproduced exactly under B's convention. State the convention if the figure is quoted downstream. |
| `A-02` | The `G5_DIAG_SPEARMAN` telemetry block records `rows_processed = 3,835,986` against `expected_rows = 3,835,988` — a two-row counter artifact in the telemetry accounting, not in the analysis. This auditor's independent Spearman ran over the full 3,835,988-row join and matched B to 5.7e-14, so no correlation is affected. Worth a look before the next heavy run so the counter is not mistaken for cohort loss. |

**CONFIRMED, addressed to Claude-A** — B's operational debt items are accepted as this auditor's
own queue and are correctly classified as having no bearing on estimability:

| id | item |
|---|---|
| `OPS-G5-01` | D-05 is absent from the canonical working tree; place it there before NB09 executes from that tree |
| `OPS-G5-02` | the canonical working tree is still at `07d132e` with three preserved untracked recovery files; fast-forward when convenient |

**B's own registers are confirmed as filed:** `M3-01` and `SM-01` as REVIEW TRIGGERS requiring
resolution before the affected model is fitted; `ID-03`, `ID-04`, `SPEC-01`, `SPEC-02` as NOTEs
carried to NB09.

---

## 12. Verdict

Every condition B claims was independently re-derived from the canonical artifacts by a different
numerical route. Rank agrees exactly. Every trigger quantity agrees to at worst 1.3e-07. All 49
Spearman pairs agree to 5.7e-14. Artifact identity is 5/5 on files rehashed by this auditor,
including a physically different D-05 copy. The protocol demonstrably precedes the results in both
Git ancestry and filesystem state, the quarantined scratch contributed no file and no cited value,
the review triggers were not promoted to failures, no variable was removed for a diagnostic, and no
scientific claim beyond estimability was made.

```
G5_INDEPENDENT_AUDIT_PASS

subject verdict G5_ANALYSIS_READINESS_PASS_WITH_NOTES = UPHELD
```

This audit certifies analysis readiness and estimability only. It does not evaluate, endorse or
anticipate any explanatory result, and NB09 remains the only stage at which a coefficient may be
produced.
