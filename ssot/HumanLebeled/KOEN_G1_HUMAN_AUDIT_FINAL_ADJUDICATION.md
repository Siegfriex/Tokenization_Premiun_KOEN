# KOEN G1 — Human Semantic Audit Final Adjudication

> **Adjudicator**: Claude-B (Research / Statistics / Gate Steward)
> **Date**: 2026-08-17
> **Authority order**: `KOEN-TP-RS-001` (original SSOT) → approved redline / Director decisions → this adjudication
> **Canonical human evidence artifact** (declared, per Research Director directive):
> `ssot/HumanLebeled/[HUMAN]_AUDIT_500_REJUDGED.xlsx`
> `outputs/manual_audit/KOEN_MANUAL_AUDIT_500.xlsx` (blank/near-empty distribution template) is **NOT** authoritative and is superseded by the above for all G1 evidence purposes.

No raw KO/EN sentence text is reproduced in this document (repository hygiene policy, consistent with prior OPS-DR-01 remediation). Only `pair_id`, counts, categorical metadata, and aggregate distributions are recorded.

---

## 1. Workbook Identity

```
File:    ssot/HumanLebeled/[HUMAN]_AUDIT_500_REJUDGED.xlsx
SHA-256: 8d8f5daa8b6823d4473336ae948ca5bea9d1c974dfff9f01e85bb26b0665a22d
Sheets:  audit (A1:D501), X_재판정 (A1:H26), 요약 (A1:D15)
```

## 2. Sampling Frame (unchanged, D-HUM-01/02 — carried forward, not re-litigated)

```
frame:      pair_quality_status='accepted' AND analysis_eligible_exact_dedup
            AND logical_corpus IN ('025','026')
population: 3,836,013   (= P2 final_analysis_denominator, cross-verified)
seed:       2995913794  (auxiliary_seed, frozen D-RD-01)
n:          500
```

## 3. First-Pass Result

```
N reviewed = 500 / 500  (complete)
O          = 475  (95.0%)
X          = 25   (5.0%)
```

## 4. X Second-Look (Rejudication) Result

```
X second-look: 25 / 25 complete (100%)
X retained as X: 25 / 25 (100%)
O upgrades:      0 / 25 (0%)
Confidence: 높음(high) = 24, 중간(medium) = 1
```

### 4.1 X reason-category distribution

| 사유 | 건수 | 비율 |
|---|---:|---:|
| 핵심 사건·주장·행위 불일치 | 9 | 36.0% |
| 주체·대상·관계 불일치 | 7 | 28.0% |
| 문장 손상·의미 모호 | 4 | 16.0% |
| 수치·날짜·고유명사 불일치 | 3 | 12.0% |
| 핵심 정보 누락·추가 | 2 | 8.0% |

### 4.2 X pair_id → source/direction/domain/length mapping

| pair_id | reason | confidence | logical_corpus | direction | domain | length_stratum |
|---|---|---|---|---|---|---|
| pair_a0c29d50d959c73e745dbb7d68807c37ea658e12ef7ab7289c76fe8f1a0a74a3 | 핵심 사건·주장·행위 불일치 | 높음 | 025 | KO_TO_EN | general | Q1 |
| pair_bf0d7dadb48ec9dbadb6ac16c820447a32edf1ee65d51af65dc96789fec5a2ed | 핵심 정보 누락·추가 | 높음 | 026 | KO_TO_EN | other | Q5 |
| pair_d0843268c8a2443a3f2a1a33501ec9018d4da3cb8326e4b14d6531c53c9ee2c8 | 핵심 사건·주장·행위 불일치 | 높음 | 025 | EN_TO_KO | general | Q1 |
| pair_e5ea0be70f0d46c9f61ea5328f6d05307e19a31459893d02e71864f72614aa61 | 주체·대상·관계 불일치 | 높음 | 026 | KO_TO_EN | other | Q4 |
| pair_c5d64dac165f66b5310b2cf49e47a4a314bf2e8132ad4202493d05b8338bca82 | 주체·대상·관계 불일치 | 높음 | 026 | KO_TO_EN | technology | Q4 |
| pair_ef7830e5459d7dd9de06867a1ea570fb5c143070acad516c041b7877e6e208ac | 핵심 사건·주장·행위 불일치 | 높음 | 025 | EN_TO_KO | general | Q2 |
| pair_abbf089451be8538bd9d6bb4e933bddddefe908350017f4be165bba15ecc48d2 | 핵심 사건·주장·행위 불일치 | 높음 | 025 | EN_TO_KO | general | Q1 |
| pair_19824774007712c7017fcc891e3f99a1fdea1c849b846be3a4ec64b5daf3fe98 | 주체·대상·관계 불일치 | 높음 | 026 | KO_TO_EN | other | Q4 |
| pair_dc0427be7a656d6509aa216a21d0666043b0a3b0e29934f51a52e3553b6d0ca1 | 주체·대상·관계 불일치 | 중간 | 025 | EN_TO_KO | other | Q3 |
| pair_81c96196738ee4fb212d0800174322bbcef04c13fd3de2f3d8610f8ffa6ddaa3 | 핵심 사건·주장·행위 불일치 | 높음 | 026 | KO_TO_EN | other | Q4 |
| pair_504865b0359a83a90736e0a7f12a109b46befe3a69ffb20ab677b957c6956923 | 핵심 사건·주장·행위 불일치 | 높음 | 025 | EN_TO_KO | other | Q3 |
| pair_19fd9b4354a3c133fab90ae974468e089869577895be916099f51505aebc854b | 주체·대상·관계 불일치 | 높음 | 026 | KO_TO_EN | technology | Q4 |
| pair_39d286be8c347cdf9bb21e3ce2e8b64bda48001b651c36bee3cb3bf657882ebe | 문장 손상·의미 모호 | 높음 | 025 | KO_TO_EN | other | Q1 |
| pair_fc5d8c8cfdc723f511151f6693b72ce983ba117c2defba216c3143241f9c60d0 | 주체·대상·관계 불일치 | 높음 | 026 | KO_TO_EN | other | Q4 |
| pair_78f5702ccbc9a34456ea185415882693158041077a4495145cdd83648189a126 | 핵심 사건·주장·행위 불일치 | 높음 | 026 | KO_TO_EN | other | Q5 |
| pair_0c2a2a48ac1c7bea678078c1e5bade4bdf3800ec08f96ff62c9361036bf5e632 | 핵심 정보 누락·추가 | 높음 | 025 | KO_TO_EN | general | Q1 |
| pair_febabc3e5d784b180530ee272f53963c16149fbb71faded6af71d56125489367 | 주체·대상·관계 불일치 | 높음 | 026 | KO_TO_EN | other | Q5 |
| pair_407fbd3ec75d821b312d2603e913d76fc395a8d2af345d65454e4c2df43fbb82 | 문장 손상·의미 모호 | 높음 | 026 | KO_TO_EN | other | Q5 |
| pair_6b971caee55877673be6edcbb0a7f322a64ae184011e308b81f5293f01a3ccf7 | 수치·날짜·고유명사 불일치 | 높음 | 025 | KO_TO_EN | dialogue | Q2 |
| pair_c112efa7b7a1fc9f493d95f16d2a03379c9340809be041a369324f645b69485a | 문장 손상·의미 모호 | 높음 | 026 | KO_TO_EN | other | Q5 |
| pair_03e3f0ea3c1fc31928688de9efc4e6009112a5bf86ea6f2c943dde3da5e12d2d | 핵심 사건·주장·행위 불일치 | 높음 | 026 | KO_TO_EN | other | Q4 |
| pair_bc44bf00b4831d6c37ee6150eb5a13b73cd2db2382710f8b2c77e264ab59e188 | 수치·날짜·고유명사 불일치 | 높음 | 026 | KO_TO_EN | other | Q4 |
| pair_85af604c5b6c875c94e560ba181a4f47559cf31e8246d00943ecf3db94d6d92e | 수치·날짜·고유명사 불일치 | 높음 | 026 | KO_TO_EN | other | Q4 |
| pair_357cc4b2e26edc5f3f9e2bd557a5060263ea36912a4dd6096f8f795bc671538a | 핵심 사건·주장·행위 불일치 | 높음 | 025 | KO_TO_EN | dialogue | Q1 |
| pair_b8d3e2b90424388efa6afd0d1ffb08d43b6a2af315510a3e4c065560bc49791e | 문장 손상·의미 모호 | 높음 | 025 | KO_TO_EN | dialogue | Q2 |

### 4.3 X aggregate distribution (mechanism-concentration check)

```
source:    025 = 11 (44%)   026 = 14 (56%)          — no single-source concentration
direction: KO_TO_EN = 20 (80%)   EN_TO_KO = 5 (20%) — tracks base sample direction mix
                                                        (base allocation: KO_TO_EN ≈ 63%,
                                                        EN_TO_KO ≈ 32%, UNKNOWN ≈ 4%);
                                                        mild enrichment, not exclusive to one direction
domain:    other=15 general=5 dialogue=3 technology=2 — spread across 4 of the 5 populated domains
length:    Q1=6 Q2=3 Q3=2 Q4=9 Q5=5                    — concentrated at length extremes (Q1/Q4/Q5 = 20/25),
                                                        consistent with judgment difficulty at very
                                                        short/long pairs, not a pairing-mechanism signature
```

## 5. SSOT Reconciliation

`docs/contracts/RESEARCH_CONTRACT_v1.md:75` (mirrors SSOT §10.1 hard exclusion list):

> "자동 또는 수동 audit에서 의미 대응이 명백히 실패한 pair" → 제외 대상

This is a distinct, SSOT-explicit hard-exclusion category, separate from the five P2-automated structural flags. `P2_NORMALIZE_QC_PRECONTRACT_v1.md` §1/§7 deliberately removed automatic `semantic_qc_fail_flag` from population-wide computation and deferred this exact category to the manual audit's findings — the population rule (`accepted`/`rejected`) is **not** individually gated by audit for the 3,835,513 unaudited rows ("Unaudited rows are not downgraded merely because they were not manually inspected"), but for the 500 rows that **were** actually audited, a `X` outcome confirmed twice (first-pass + independent second-look, both times X, 24/25 high confidence) **is** the SSOT §10.1 criterion being directly, individually evidenced — not inferred, not extrapolated.

**Reconciliation rule applied**: exclude exactly the 25 individually-audited-and-confirmed pair_ids from the primary analysis cohort. Do **not** infer or apply any population-wide exclusion rate, flag, or QC threshold change to the remaining 3,835,513 unaudited members of the frame — that would exceed what the evidence supports and contradicts the Q0-resolved population rule design.

## 6. Systematic Threat Judgment

Checked against the four frozen material-threat patterns (D-HUM-03):

| Pattern | Evidence | Verdict |
|---|---|---|
| Repeated clear misalignment concentrated in one mechanism | 5 distinct reason categories, no single category >36% | NOT OBSERVED |
| Repeated translation-side swap | 0 of 25 reasons describe a side-swap pattern | NOT OBSERVED |
| Source-specific wiring error | 025=11 / 026=14, no single-source concentration | NOT OBSERVED |
| Repeated ingest/pairing defect (same mechanism) | No shared raw_locator/ingest signature; distributed across corpora, directions, domains, and length strata | NOT OBSERVED |
| Reproducible defect requiring primary cohort redefinition | None found; failures explained by ordinary content-level translation-quality variance, mildly concentrated at length extremes (expected judgment-difficulty effect) | NOT OBSERVED |

**Verdict: CONFIRMED — NO MATERIAL_SYSTEMATIC_THREAT.** (This confirms, not reverses, the prior working judgment; confirmation is now based on individually-reviewed X-pool evidence, not merely absence of a numeric threshold breach.)

## 7. Final Cohort Directive

```
FINAL_COHORT_BOUNDED_EXCLUSION
excluded_pair_ids = [ the 25 pair_ids listed in §4.2 ]
new_N = 3,836,013 - 25 = 3,835,988
```

Rationale: SSOT §10.1's audit-confirmed-semantic-failure hard-exclusion criterion is directly evidenced for exactly these 25 pair_ids and only these 25. No other row in the 3,836,013-row frame has been audited; none may be excluded on this basis without direct evidence. This is an `ENGINEERING_BUGFIX`-equivalent, narrowly-scoped, evidence-bound application of an already-frozen SSOT rule — **not** a new QC rule, not a new threshold, not a SSOT amendment, not a CHANGE_REQUEST.

## 8. G1 Verdict

```
G1 = PASS
```

All prior conditions (pair ID uniqueness, null/duplicate integrity, QC/pass-rate reporting, source/license operational metadata, P2 lineage/reporting) were already closed. Human N=500 audit is complete, second-look complete, no systematic threat found, and the sole required action — bounded exclusion of 25 individually-confirmed pairs — has been applied per SSOT §10.1.

```
DATA_FOUNDATION_ACCEPTED_FOR_ANALYSIS
PREPROCESSING_MAINTENANCE_MODE
```

Downstream analysis notebooks (NB05 exact-decomposition eligible-pair filters, NB07/NB08) must apply `excluded_pair_ids` (§7) when constructing the final primary analysis cohort.

---

**Adjudication closed**: 2026-08-17, Claude-B (Research / Statistics / Gate Steward).
