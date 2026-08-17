# KOEN EDA V1 — Traceability Matrix

```
Scope:      PRELIMINARY_RESULTS_DISCOVERY_V1
Authority:  NON_CANONICAL / SUBORDINATE_TO KOEN-TP-RS-001
Notebook:   notebooks/exploratory/EDA_representation_kiwi_o200k_casebook_v1.ipynb
run_id:     VIZ_CASEBOOK_20260817T151317
Base SHA:   2d99c906c7c94a9ce2ee2e0ff9dc01cf61998c3a
```

Purpose: pin the chain **RQ ↔ estimand ↔ data ↔ notebook ↔ validation ↔ claim** so that
no V1 statement can later be quoted at a strength it never had.

---

## 1. Evidence classes

| Class | Meaning | Population basis |
|---|---|---|
| `[R-FULL]` | Full-population Representation (D-02) | `REP_FEATURES_v002.parquet`, N = 3,835,988 |
| `[M-PILOT1000]` | Corrected morphology pilot context | **present in the repo at the V1 base, but NOT consumed by V1** — see note below |
| `[M-SAMPLE40]` | V1 fixed 40-pair morphology measurement | n = 40 (10 × 4 domains) |
| `[T-SAMPLE40]` | V1 fixed 40-pair o200k measurement | n = 40 (same pair set) |
| `[DESIGN-FULL]` | Full-cohort metadata / design structure | N = 3,835,988 cross-tabulations |
| `[HYPOTHESIS]` | Stated for future canonical test | none — not evidence |
| `[NOT-ESTABLISHED]` | Not supported at V1 | none |

> **Note on `[M-PILOT1000]`.** The V1 artifact census detected
> `.runtime/nb04-pilot/MORPH_FEATURES_PILOT_v001.parquet` and recorded its existence,
> but the notebook set `M_morphology = SAMPLE_RECOMPUTE_ALLOWED` and computed its own
> 40-pair values through the canonical `morphology_features()` function. **No pilot row
> was read into any V1 figure or table.** `[M-PILOT1000]` therefore denotes *surrounding
> context at the V1 base commit*, not a data source of V1. Any claim tagged
> `[M-PILOT1000]` alone is context, not evidence.

## 2. Artifact versions and hashes as recorded by V1

| Artifact | Version | Hash / provenance recorded in notebook |
|---|---|---|
| Pair registry | `PAIR_REGISTRY_v002.parquet` | manifest sha256 `95f523d11b0e8fcfd761dee949f082e9b4590b919801441fbcfa3426010bec52` |
| Representation | `REP_FEATURES_v002.parquet` (49 cols, N = 3,835,988) | manifest sha256 `dfae8e01cd3fe2ca949d8754678e508203ad1a7aa6abea418008a33ac650d309`; status `CONFORMANCE_RESTORED`; decision `RD-20260817-D02D03-CONFORMANCE-01` |
| Morphology full | **absent at V1** | — |
| Tokenizer full | **absent at V1** | — |
| Tokenizer freeze | o200k_base / tiktoken 0.13.0 | encoding `446a9538…`, `pat_str` `2d1b8dc1…`, mergeable ranks `f2f61460…` |
| Analyzer freeze | Kiwi 0.23.2 / model 0.23.0 | model manifest `3baa52f4…`, `custom_dictionary_used = false` |
| Sample | n = 40, seed `2995913794` | pair-set sha256 `5b4393fb541c3a6dc347fa2422ed25fbfb384eed45a4b98b652ed3f85c8e0ac1` |

Because `src/` was partly uncommitted at execution time, V1 additionally pinned the
**content hashes of the four imported modules** (`representation.py` `2b21ee1e…`,
`morphology.py` `d632eee3…`, `tokenizer_measurement.py` `0eebab61…`,
`tokenization.py` `152bad21…`). Those hashes, not the base Git SHA alone, identify the
code V1 actually ran.

---

## 3. Traceability matrix

### V1-C01 — Code-point length direction

| Field | Value |
|---|---|
| **RQ** | RQ3 (surface-form structure); input to RQ2 |
| **SSOT** | §8.2 CodePointRatio; §13.5 Pair Length Ratio; §12.2 |
| **Construct / estimand** | distribution of $C_{i,\mathrm{KO}}/C_{i,\mathrm{EN}}$ over the final cohort |
| **Artifact** | `REP_FEATURES_v002.parquet` |
| **Basis** | `[R-FULL]` N = 3,835,988 |
| **Notebook** | §05 population summary (`POP_SUMMARY`), §06 figure C |
| **Validation** | DuckDB streaming quantiles; no sampling |
| **V1 interpretation** | `pair_codepoint_ratio` median **0.4675**, p99 **0.8333** — Korean is shorter in code points across essentially the whole cohort |
| **Limitation** | descriptive distribution only; no inference, no model |
| **V2 promotion test** | recompute on the V2 universe; confirm quantiles unchanged |

### V1-C02 — Byte-ratio reversal

| Field | Value |
|---|---|
| **RQ** | RQ2 / RQ3 |
| **SSOT** | §8.3 ByteDensityRatio; §13.3 Byte Density |
| **Construct / estimand** | joint behaviour of `pair_codepoint_ratio` and `pair_byte_ratio` |
| **Artifact** | `REP_FEATURES_v002.parquet` |
| **Basis** | `[R-FULL]` |
| **Notebook** | §05 `POP_SUMMARY`; §06 figure C |
| **Validation** | full-population quantiles |
| **V1 interpretation** | code-point ratio median 0.4675 (<1) while byte ratio median **1.1268** (>1); byte-ratio p25 = 0.9848, so the crossing of 1.0 lies between p25 and the median — the reversal holds for the **majority, not all**, of the cohort |
| **Limitation** | a representation-level fact; says nothing about tokens |
| **V2 promotion test** | unchanged under V2 universe; then relate to full `logCP` |

### V1-C03 — Exact-decomposition direction (probe)

| Field | Value |
|---|---|
| **RQ** | RQ2 |
| **SSOT** | §8 / §8.1–8.4; Decision D-04; IR-01 |
| **Construct / estimand** | sign and relative size of $\log CR$, $\log BDR$, $\log CP$ |
| **Artifact** | 40-pair recompute; `pair_token_measurement()` |
| **Basis** | `[T-SAMPLE40]` + `[R-FULL]` context |
| **Notebook** | §09 (waterfall, component dot matrix) |
| **Validation** | identity $\lvert \log TP - (\log CR + \log BDR + \log CP)\rvert$ max **2.78e-16** < $\varepsilon = 10^{-10}$ |
| **V1 interpretation** | **PRELIMINARY SIGNAL** — sample medians $\log CR = -0.8113$, $\log BDR = +0.9004$, $\log CP = +0.1360$ |
| **Limitation** | n = 40 equal-domain probe; medians are not additive; **no population TP estimate, no $P(TP>1)$, no primary inference** |
| **V2 promotion test** | full-population $\log CP$ distribution; §17.1 signed-rank + bootstrap in NB08 |

### V1-C04 — Identity / roundtrip evidence

| Field | Value |
|---|---|
| **RQ** | measurement integrity (not an RQ) |
| **SSOT** | §31 G2 (numerical identity), G3 (roundtrip); §14.2 |
| **Construct / estimand** | identity error; encode/decode roundtrip |
| **Basis** | `[T-SAMPLE40]` |
| **Notebook** | §08, §09 |
| **Validation** | 0 / 40 roundtrip failures; identity max 2.78e-16 |
| **Evidence class** | **evidence for** G2 / G3 conditions |
| **V1 interpretation** | consistent with the Gate conditions on this sample |
| **Limitation** | `[NOT-ESTABLISHED]` as a Gate verdict — §25.4 requires *all accepted pairs*; V1 covers 40 |
| **V2 promotion test** | full-cohort roundtrip and identity sweep |

### V1-C05 — Morphology ↔ premium raw concordance

| Field | Value |
|---|---|
| **RQ** | RQ4 — **but V1 does not test it** |
| **SSOT** | §13.6, §13.7, §12.3; §19 (M1 vs M2); §6.4 |
| **Construct / estimand** | Spearman rank concordance, **unconditional** |
| **Basis** | `[M-SAMPLE40]` + `[T-SAMPLE40]` |
| **Notebook** | §11 |
| **Validation** | rank statistic only; **p-values not computed** (§17.3) |
| **V1 interpretation** | all morphology associations weak: $\lvert\rho_s\rvert \le 0.192$ (largest: $\rho_s(\log TP, \text{ending ratio}) = -0.192$) |
| **Limitation** | **no controls** ⇒ this is not the conditional / incremental association RQ4 asks for; $\rho_s(\log TP, \log CR) = +0.647$ is a deterministic consequence of the §8 identity (§32 T-06), not a finding |
| **V2 promotion test** | M1 surface model vs M2 + morphology block, per §19.1–19.2 |

### V1-C06 — Domain heterogeneity, and its confounding

| Field | Value |
|---|---|
| **RQ** | RQ6 (heterogeneity) |
| **SSOT** | §9.2; §20.1–20.2 (Gate G-ID); §32 T-04 |
| **Construct / estimand** | strata structure of the final cohort |
| **Basis** | `[DESIGN-FULL]` + `[T-SAMPLE40]` |
| **Notebook** | §13 (population cross-tabulations), §10 triptych |
| **Validation** | full-cohort cross-tabs computed in DuckDB |
| **V1 interpretation** | in the **population**: `dialogue` and `general` occur only in `logical_corpus` 025, `technology` only in 026, `other` in both; `technology` direction is KO_TO_EN 359,905 / EN_TO_KO 0; `sentence_type` has exactly **one level** across all 3,835,988 rows |
| **Limitation** | `logical_corpus` **is not** `source_id`; V1 did **not** cross-tabulate `source_id`, so V1 has **not** fully characterised source confounding — see `[NOT-ESTABLISHED]` below |
| **V2 promotion test** | Gate G-ID on `domain × source_id`, `domain × direction`, `source_id × direction`, plus condition number / VIF |

### V1-C07 — Extreme / boundary regions

| Field | Value |
|---|---|
| **RQ** | supports §16.3 extreme-case audit |
| **SSOT** | §16.3; §10.2 soft flags |
| **Construct / estimand** | tail regions of the representation distribution |
| **Basis** | `[R-FULL]` |
| **Notebook** | §05, §12 |
| **Validation** | percentile placement against full-population quantile grid |
| **V1 interpretation** | rubric outcome 38 `EXPECTED` / 2 `PLAUSIBLE_EXTREME` / 0 warning / 0 suspicious / 0 hard-invalid; **no pair removed** (§16.3) |
| **Limitation** | rubric is a triage label, not a QC disposition; V1 created no exclusion |
| **V2 promotion test** | canonical NB07 extreme audit over the full cohort with token/chunk layers attached |

### V1-C08 — `[NOT-ESTABLISHED]` register

Statements V1 **does not** support and which must not be attributed to it:

| # | Non-claim |
|---|---|
| N1 | Population Tokenization Premium, $\operatorname{Median}(\log TP)$, or $P(TP>1)$ |
| N2 | Any Gate verdict (G2 / G3 / G4 / G5) |
| N3 | Incremental explanatory value of the morphology block (RQ4) |
| N4 | Significance of any domain difference (n = 10 per domain) |
| N5 | Full characterisation of source confounding — `source_id` was never cross-tabulated |
| N6 | Any relation between morpheme boundaries and tokenizer chunk/token boundaries — D-05 / NB06 absent (§5.1) |
| N7 | Any causal statement (MN-01, §3.2) |
| N8 | Generalisation beyond o200k_base (§32 T-07) |

---

## 4. Figure identifier caveat

The notebook's internal figure identifiers (`F05`, `F06A/B`, `F06C/D`, `F07`, `F08`,
`F09A`, `F09B`, `F10`, `F11`, `F12A`, `F12B`) are **local to V1 and do not correspond to
the canonical SSOT figure IDs F01–F09** defined in §16.2 / §35. The strings collide but
the contents do not. Canonical figure IDs are frozen only at release (§39 checklist item
"Figure/table IDs freeze"), which has not occurred. See caveat **C7**.
