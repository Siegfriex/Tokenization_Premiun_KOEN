# NB11 — Robustness / Sensitivity

NB11 tests the stability of the NB09 primary results. It does not redefine them.
Conditional associations only; no causal claim.

```
N = 3,835,988   pair-set d9660d654ee449e4d0c23a0070225274
subsets  FULL=3,835,988, KNOWN_DIR=3,785,441, NO_ANOMALY=3,728,608, CENTRAL_LENGTH=2,387,120, SOURCE_025=2,485,963, SOURCE_026=1,350,025
variants V0, V1_SM01, V2_M3DENS, V3_M3DENS_LOGMCB, V4_B_SSOT182, V5_SRC_DOM, V6_SPEC01
```

## Claim register

| claim | direction | magnitude | effect range |
|---|---|---|---|
| RQ1 — Median(log_token_premium) > 0 | DIRECTION_STABLE | MAGNITUDE_STABLE | median TP 1.3158–1.3617, P(TP>1) 0.8336–0.9650 |
| RQ3 — M1 - M0 representation/surface block | DIRECTION_STABLE | MAGNITUDE_STABLE | A ΔR² 0.604706–0.711574, partial 0.621022–0.733965 (31 specs) |
| RQ4 — M2 - M1 morphology block | DIRECTION_STABLE | MAGNITUDE_STABLE | A ΔR² 0.004990–0.007767, partial 0.015893–0.023507 (31 specs) |
| RQ5 — M3 - M2 regex-chunk mechanism block | DIRECTION_STABLE | MAGNITUDE_ATTENUATED | A ΔR² 0.077425–0.179427, partial 0.307417–0.496678 (26 specs) |

## Structural pruning and non-identifiability

- zero-variance / unsupported columns removed before fitting: **215**
- designs still not identifiable after pruning: **35** of 210
- subsets where the primary specification V0 is not identifiable: **SOURCE_026**
- `SOURCE_026` lacks the frozen reference cell, so the remaining cell dummies saturate the intercept. That is a consequence of the frozen coding, not an empty column, and is not repaired here by re-referencing.
- `V3_M3DENS_LOGMCB` at M3 fails on the exact byte identity and is stopped, not repaired by deleting a substantive variable.

## Not testable / bounded

- **SSOT_24_1_raw_text** — `NOT_TESTABLE_AT_NB11`: requires regenerating D-02 and D-04 on ko/en_text_raw; no approved decision authorizes artifact regeneration, and NB11 may not create a new measurement artifact.
- **SSOT_24_2_nfc_only** — `NOT_TESTABLE_AT_NB11`: requires regenerating D-02 and D-04 on ko/en_text_raw; no approved decision authorizes artifact regeneration, and NB11 may not create a new measurement artifact.
- **SSOT_24_3_curated_source** — `REALIZED_SUPPORT_ABSENT`: source_tier has a single realized level 'A' over the whole cohort, so no curated-vs-full contrast exists. The per-source subsets SOURCE_025 / SOURCE_026 are run as the closest realized analogue and are labelled as such, not as a curated-tier contrast.
- **SSOT_24_9_source_random** — `FEASIBLE_SUPPORT_IS_FIXED_ONLY`: two realized source levels; the additive source_id + domain specification (V5_SRC_DOM) is run as the feasible fixed alternative to source_domain_cell.
- **dependence** — `DEPENDENCY_PENDING_PRE_NB10_GROUPING`: duplicate_group_id is all-singleton (3,835,988 distinct of 3,835,988) and therefore does not implement LR-01. No grouping key is invented here.

## Binding restrictions

```
M3_INTERNAL_COLLINEARITY_REVIEW = YES
PAIR_LEVEL_MULTIPLIER_BOOTSTRAP = != DUPLICATE_CLUSTER_DEPENDENCE_CORRECTION
RAW_CHUNK_COUNT_COEFFICIENT_SUBSTANTIVE_INTERPRETATION = PROHIBITED
RQ5_PRIMARY = BLOCK_LEVEL_M3_MINUS_M2
SCRIPT_MIXING_BLOCK_INTERNAL_REDUNDANCY = YES
causal_language = PROHIBITED
coefficient_p_values = secondary inferential detail; never used to rank predictors
outcome_A_and_B_narratives = never merged; B is not the cause of A; the decomposition is an accounting identity, not causal mediation
source_domain_cell = OBSERVED_STRATUM_CONTROL — no pure source effect, no pure domain effect
translation_direction = identified primarily from within-025 support; 026 has no EN_TO_KO
NB11_ROLE = stability testing only; NB09 primary results are not redefined
SENSITIVITY_SELECTION = pre-registered before fitting; never chosen for a larger fit
NB11_BOOTSTRAP_CI = NOT_USED — pending Claude-A review A6
```

