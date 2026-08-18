# NB09 — Explanatory Models

Conditional associations only. No causal claim. `o200k_base`, Track A raw text.

```
N = 3,835,988   pair-set d9660d654ee449e4d0c23a0070225274
estimator  fixed-effects OLS   SE  HC1 (scale = N/(N-p))
bootstrap  wild/Rademacher B=2000  seeds {'NB09_COEF_BOOTSTRAP_A': 1222524615, 'NB09_COEF_BOOTSTRAP_B': 1018984010, 'NB09_GLOBAL': 2703484264}
```

## Model fit

| outcome | model | p | rank | R² | adj R² | AIC | BIC | HC1 scale |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| A | M0 | 8 | 8 | 0.028625 | 0.028623 | -768948.1 | -768829.7 | 1.000002086 |
| A | M1 | 23 | 23 | 0.649578 | 0.649576 | -4679998.2 | -4679682.4 | 1.000005996 |
| A | M2 | 27 | 27 | 0.656169 | 0.656166 | -4752819.4 | -4752450.9 | 1.000007039 |
| A | M2A | 26 | 26 | 0.655423 | 0.655421 | -4744511.1 | -4744155.8 | 1.000006778 |
| A | M3 | 45 | 45 | 0.806939 | 0.806936 | -6966697.3 | -6966092.0 | 1.000011731 |
| B | M0 | 8 | 8 | 0.182000 | 0.181999 | -2720483.3 | -2720364.8 | 1.000002086 |
| B | M1 | 23 | 23 | 0.509203 | 0.509200 | -4679998.2 | -4679682.4 | 1.000005996 |
| B | M2 | 27 | 27 | 0.518433 | 0.518430 | -4752819.4 | -4752450.9 | 1.000007039 |
| B | M2A | 26 | 26 | 0.517389 | 0.517386 | -4744511.1 | -4744155.8 | 1.000006778 |
| B | M3 | 45 | 45 | 0.729600 | 0.729597 | -6966697.3 | -6966092.0 | 1.000011731 |

## Primary block comparisons

| outcome | comparison | ΔR² | partial R² | bootstrap 95% CI | df | LR χ² |
|---|---|---:|---:|---|---:|---:|
| A | RQ3 (M0→M1) | 0.620954 | 0.639252 | [0.620290, 0.621596] | 15 | 3911080.1 |
| A | RQ4 (M1→M2) | 0.006590 | 0.018807 | [0.006419, 0.006757] | 4 | 72829.2 |
| A | RQ5 (M2→M3) | 0.150770 | 0.438500 | [0.150350, 0.151202] | 18 | 2213913.9 |
| A | SENS_M2A (M1→M2A) | 0.005845 | 0.016679 | [0.005693, 0.005988] | 3 | 64518.9 |
| B | RQ3 (M0→M1) | 0.327203 | 0.400004 | [0.325909, 0.328480] | 15 | 1959545.0 |
| B | RQ4 (M1→M2) | 0.009230 | 0.018807 | [0.008991, 0.009467] | 4 | 72829.2 |
| B | RQ5 (M2→M3) | 0.211167 | 0.438500 | [0.210591, 0.211731] | 18 | 2213913.9 |
| B | SENS_M2A (M1→M2A) | 0.008186 | 0.016679 | [0.007978, 0.008398] | 3 | 64518.9 |

## B-N01 — Outcome A / Outcome B are the same fit above M0

For every model containing both log_code_point_ratio and log_byte_density_ratio (M1, M2, M2A, M3), the Outcome B fit is the Outcome A fit with those two coefficients shifted by exactly -1 and every other coefficient unchanged. The residual vector, and therefore SSR, AIC, BIC and every nested test statistic, are identical between the two outcomes.

- RQ4 and RQ5 partial R-squared are IDENTICAL across the two outcomes by construction; they are not two independent confirmations.
- Delta R-squared differs between outcomes only through the SST denominator, because the numerator SSR difference is the same quantity.
- AIC and BIC coincide for M1, M2, M2A and M3; only M0 differs, because M0 omits the two decomposition components.
- Only RQ3 (M1 - M0) carries genuinely different information between the outcomes.

SSOT 18.2's illustrative Outcome B form omits logCR and logBDR; PRE_NB09_PROTOCOL_v001 SPEC-02 recorded that the approved common ladder includes them and flagged the divergence for NB09 interpretation. This is the measured consequence of that divergence. No protocol change is made here - the protocol is audited and closed, and it was executed as frozen.

Whether Outcome B should be re-specified without the two representation ratios, so that it carries information M1 does not already contain, is a decision for the Director. Registered as an NB11 sensitivity candidate; NOT actioned here.

This is not an implementation error and not outcome leakage: neither outcome is reconstructible from its own right-hand side, which G5 verified and this run re-confirms through full rank at every model.


## Binding restrictions

```
SCRIPT_MIXING_BLOCK_INTERNAL_REDUNDANCY = YES
M3_INTERNAL_COLLINEARITY_REVIEW = YES
RAW_CHUNK_COUNT_COEFFICIENT_SUBSTANTIVE_INTERPRETATION = PROHIBITED
RQ5_PRIMARY = BLOCK_LEVEL_M3_MINUS_M2
source_domain_cell = OBSERVED_STRATUM_CONTROL — no pure source effect, no pure domain effect
translation_direction = identified primarily from within-025 support; 026 has no EN_TO_KO
PAIR_LEVEL_MULTIPLIER_BOOTSTRAP = != DUPLICATE_CLUSTER_DEPENDENCE_CORRECTION
coefficient_p_values = secondary inferential detail; never used to rank predictors
causal_language = PROHIBITED
outcome_A_and_B_narratives = never merged; B is not the cause of A; the decomposition is an accounting identity, not causal mediation
```

