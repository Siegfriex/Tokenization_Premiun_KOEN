# Research Contract v1 — KO-EN Tokenization Premium

- Source of truth: `ssot/Korean_English_Tokenization_Premium_Research_Spec_v1.0-2.pdf` (KOEN-TP-RS-001, v1.0, FINAL DESIGN/PRE-ANALYSIS, 2026-08-16)
- Status: **DRAFT freeze proposal** — every item below is a direct transcription of the SSOT with its section cited. No value here that is not in the SSOT has been invented; anything the SSOT leaves unspecified is marked `DECISION REQUIRED` rather than guessed.
- Owner: Claude Orchestrator (Research/Data Contract/Statistics). Do not edit `src/**`, `tests/**`, `pyproject.toml` from this document's authority — those are Codex's.

## 1. Research Questions (RQ1–RQ7) — §6

| RQ | Question | Primary estimand / method |
|---|---|---|
| RQ1 | o200k_base 기준 KO-EN 의미대응쌍에서 Tokenization Premium(TP)이 1보다 큰가 | θ_TP = Median(log TP_i); H0: θ=0 vs H1: θ>0; one-sample signed-rank test + bootstrap CI |
| RQ2 | 전체 premium을 CodePointRatio × ByteDensityRatio × CompressionPenalty로 분해했을 때 각 성분의 분포는 어떤가 | exact multiplicative decomposition (§8), descriptive distribution |
| RQ3 | 공백밀도/grapheme구조/script비율/문장길이/숫자·기호가 log(TP), log(CompressionPenalty)와 어떤 조건부 연관을 갖는가 | Model M1 regression |
| RQ4 | 형태소밀도/조사비율/어미비율/접사비율이 길이·byte·공백·문자군·도메인·출처 통제 후에도 추가 설명력을 갖는가 | Model M2 vs M1, block-level incremental value (개별 p-value 아님) |
| RQ5 | o200k_base regex chunk count/length/token-per-chunk/token-per-byte 등 mechanism feature가 최종 premium과 어떻게 연결되는가 | Model M3, **mechanism audit** (post-treatment, causal 통제로 사용 금지 — MN-02) |
| RQ6 | 도메인/문장유형/번역방향/출처/길이 strata별로 TP와 설명요인 크기가 달라지는가 | interaction / forest plot |
| RQ7 | gpt-oss-20b vs 120b에서 KO/EN 요청의 request/analysis/final/total token, TTFT, latency, throughput, cost가 어떻게 다른가 | paired serving analysis (Track B) |

**Interpretive constraint (전 RQ 공통, MN-01)**: 모든 회귀계수는 문자열 구조와 tokenizer 산출량 간 조건부 통계적 연관성이다. 인과 언어(causal language) 사용 금지.

## 2. Estimand / Outcome — Primary vs Secondary (§7.2, §18)

| 계층 | 변수 | 역할 |
|---|---|---|
| **Primary** | `log_token_premium` | RQ1 및 메인 설명모형 Outcome A |
| Secondary | `token_premium` | 해석 가능한 ratio 보고용 |
| Secondary | `log_compression_penalty` | Outcome B — byte량을 분리한 tokenizer compression 비대칭 설명 |
| Secondary | `token_difference` (ΔT) | 절대 token 차이, 문장길이 의존적이므로 보조로만 |
| Descriptive | `ko/en_tokens_per_byte`, `ko/en_tokens_per_codepoint` | 언어별 compression/fertility 보조 지표 |

**IR-02 (불변 규칙)**: Outcome A(logTP)와 Outcome B(logCompressionPenalty)는 서로 다른 모형이며 같은 표/그림에 섞어 보고하지 않는다.

## 3. Source Hierarchy — §9.3

```
Tier A — curated/official parallel corpus (명시적 번역쌍, 안정적 license/metadata)
Tier B — benchmark parallel corpus (연구 benchmark 성격, 규모는 작아도 품질 우수)
Tier C — web-mined parallel corpus (대규모 확보용, semantic QC 강화 필요)
```
민감도 분석은 Tier A/B만으로 별도 수행한다.

> **DECISION REQUIRED / NOT YET RESOLVED**: 이 시점에 실제 corpus를 Tier A/B/C 어디에도 배정하지 않는다. AIHub 등 raw 데이터가 아직 canonical ingest되지 않았으므로, 이 계약은 **tier 정의 스키마만** freeze하고 실제 source_id ↔ tier 매핑은 data-recon 트랙의 ingest 완료 후 별도 CR(Change Request)로 확정한다.

## 4. Source Registry Fields — §12.1 (D-01 Pair Registry, 발췌)

`pair_id, source_id, source_tier(A/B/C), domain, sentence_type, translation_direction, ko_text_raw, en_text_raw, ko_text_nfc, en_text_nfc, ko_text_analysis, en_text_analysis, pair_quality_status(accepted/review/rejected), pair_quality_score, pair_version, source_license_note`

층화 변수(§9.2)로 추가 관리: `domain`, `sentence_type`, `translation_direction`, `source_id`, `length_stratum`(영어 word/code point 또는 pair mean byte 기준 분위수).

## 5. Domain Taxonomy — §9.2

`general, administration, legal, news, technology, education, dialogue, other`

## 6. Sentence Type Taxonomy — §9.2

`declarative, interrogative, imperative, title, list_item, short_phrase, other`

## 7. Translation Direction Taxonomy — §9.2

`KO_TO_EN, EN_TO_KO, HUMAN_PARALLEL_UNKNOWN, UNKNOWN`

## 8. Pair Unit (분석 단위) — §7.1

기본 분석 단위는 `(x_i,KO, x_i,EN)`, i = 1..N — 의미적으로 대응되는 KO-EN 문장쌍. 동일 pair 내부 언어 비교로 topic/의도는 pair matching으로 통제하되, 번역문은 완전한 동일 semantics가 아니므로 `translation_direction`과 pair quality를 별도 관리한다.

## 9. Pair QC — Hard Exclusion — §10.1

다음 pair는 분석에서 **제외**한다:
- KO 또는 EN이 empty/null
- 완전 중복 pair
- 언어 식별이 명백히 잘못된 pair
- HTML/code/URL/table markup이 텍스트 대부분을 차지하는 pair
- zero-width/control character가 비정상적으로 과다한 pair
- decoder 오류 또는 tokenizer round-trip 검증 실패
- 자동 또는 수동 audit에서 의미 대응이 명백히 실패한 pair

## 10. Pair QC — Soft Flags — §10.2

삭제하지 않고 flag만 생성: `short_text_flag, long_text_flag, high_digit_ratio_flag, high_punctuation_ratio_flag, script_mix_flag, unicode_anomaly_flag, translation_quality_review_flag, named_entity_heavy_flag`

## 11. Semantic QC — §10.3

1. source-level metadata에서 병렬쌍 여부 확인
2. multilingual semantic similarity/alignment score를 **보조** QC로 계산 (주 결과변수 생성에 직접 사용 금지 — T-01 QC model bias)
3. strata 기반 300–500 pair 수동 audit

수동 audit rubric: `2=의미·정보량 실질적 동등`, `1=핵심의미 대응하나 경미한 누락/추가/의역`, `0=다른 의미/심각한 누락/정렬오류`. Primary cohort는 score 2 목표, score 1 포함 결과는 별도 sensitivity로 분리 가능.

## 12. Normalization — §11

원문은 절대 덮어쓰지 않는다. 저장 필드: `*_text_raw`(원문), `*_text_nfc`(NFC만), `*_text_analysis`(NFC+BOM제거+외곽 whitespace trim, 내부 whitespace 보존), `normalization_rule_version`, `normalization_ops`, `unicode_anomaly_flag`.

**금지되는 무음 정규화 (§11.2)** — primary analysis text에 적용 금지: 내부 whitespace collapse, punctuation ASCII 치환, lowercasing, full-width/half-width 통합, NFKC 변환, 숫자 치환, emoji 제거, 조사/어미 분리. (NFKC·whitespace collapse·raw text 기준 결과는 별도 sensitivity track에서만 허용.)

## 13. Morphology Block — §12.3, §15

- Primary analyzer: Kiwi/`kiwipiepy` (design-freeze `kiwipiepy==0.23.2`) — 세부는 `configs/morphology_v1.yaml` 참조.
- **Primary feature block**: `morpheme_density, particle_ratio, ending_ratio, deriv_affix_ratio`
- **Alternative feature block**: `morpheme_density, function_morpheme_ratio, deriv_affix_ratio`
- 두 block을 동일 primary regression에 동시 투입 금지 (공선성, §12.3 "POS feature mapping 원칙").
- 분석 금지 사항(§15.2): 형태소 분절 결과를 tokenizer input으로 재조합 금지, analyzer가 교정한 문자열을 Track A tokenizer 입력으로 사용 금지, custom dictionary 도메인별 임의 추가 후 타 source와 비교 금지.

## 14. Main vs Sensitivity Boundary — §19, §24

**Main (confirmatory) model blocks**:
```
M0: Y ~ length + domain + sentence_type + translation_direction + source
M1: Y ~ M0 + byte/whitespace/script/surface features
M2: Y ~ M1 + morphology block           ← RQ4의 핵심 검정 (M2-M1 incremental value)
M3: Y ~ M2 + regex-chunk/tokenizer mechanism features   ← mechanism audit, NOT a stricter causal control (MN-02)
```

**Sensitivity (robustness) analyses — §24, 최소 다음 10종**:
1. raw text vs analysis-normalized text
2. NFC-only vs primary analysis text
3. full accepted cohort vs curated-source-only cohort
4. anomaly flag 포함 vs 제외
5. extreme length 상/하위 strata 제외
6. translation direction known-only subset
7. morphology primary block vs alternative block
8. OLS/mixed model vs Huber/quantile regression
9. source fixed vs random specification
10. sign test vs signed-rank test (RQ1)

다중비교: secondary feature-level/interaction-level hypothesis family에 Benjamini-Hochberg FDR 적용. **단일 primary RQ1에는 FDR 보정 미적용** (§24, §29).

## 15. Cohort / Split Requirements — §23

- **설명모형**: 전체 analysis cohort에서 계수 추론 + bootstrap + model diagnostics.
- **예측모형**: final hold-out 15–20%; tuning은 training partition 내부에서만; source 수 충분 시 `GroupKFold(source_id)`; source 수 적고 domain과 결합 시 pair-level split + near-duplicate cluster group을 primary, source-held-out test를 secondary OOD test로 분리.
- **Leakage Rule LR-01**: 같은 원문에서 파생된 paraphrase/duplicate cluster가 train/test 양쪽에 들어가지 않도록 text hash + near-duplicate cluster를 group key로 사용.

## 16. Threats T-01 ~ T-08 — §10.3, §26.5, §32

| ID | 위협 | 대응 |
|---|---|---|
| T-01 | QC model bias — 자동 semantic similarity 모델도 언어별 tokenizer/representation bias 가능 | 자동 QC score를 주 결과변수 생성에 미사용, curated-subset + 수동 audit로 방향 검증 |
| T-02 | Output length confounding (자연 생성에서 output token 차이가 tokenizer 외 verbosity/reasoning/style에 기인) | B2 controlled generation과 B3 natural generation 분리 |
| T-03 | Translationese (번역방향에 따른 표현길이/어순 차이) | direction stratification/interaction, known-direction subset |
| T-04 | Domain-source confounding | identifiability gate + source-domain composite sensitivity |
| T-05 | Analyzer measurement error (형태소 analyzer가 domain/신조어/고유명사에서 오류) | analyzer version freeze, sample audit, curated subset, warning feature |
| T-06 | Deterministic feature overlap (byte density/code point length/token-per-byte가 수학적으로 연결) | exact decomposition을 descriptive accounting으로 우선, 회귀에 동일 항등식 구성요소 무비판적 중복 투입 금지 |
| T-07 | Tokenizer-specific generalization (o200k_base 결과는 타 tokenizer에 자동 일반화 안됨) | 결론에 "o200k_base 기준" 명시 |
| T-08 | Cost generalization (가격은 시간/provider/deployment에 따라 변동) | 비용은 snapshot으로만 보고 |

## 17. Table / Figure Traceability Matrix — §34–35

| RQ | Primary data | Estimand/outcome | Method | 산출물 |
|---|---|---|---|---|
| RQ1 | D-01+D-04 | median logTP | signed-rank + bootstrap | T01, F01–F03 |
| RQ2 | D-02+D-04 | exact decomposition identity | distribution | T02, F04–F05 |
| RQ3 | D-02+D-04 | logTP/logCompressionPenalty | M1 regression | T03, F06 |
| RQ4 | D-03+D-04 | incremental morphology value | M2 vs M1 | T04, coefficient plot |
| RQ5 | D-05+D-04 | chunk/token mechanism | M3 mechanism audit | T05, extreme audit |
| RQ6 | D-01..D-05 | strata-specific effects | interactions/forest plot | T06, F08 |
| RQ7 | D-06+D-07 | request/output/latency/cost ratios | paired serving analysis | T07, F09 |

**Tables**: T01 Sample composition/QC flow · T02 Overall KO-EN stats · T03 Exact premium decomposition · T04 Main explanatory models M0-M2 · T05 Mechanism audit M3 · T06 Domain/source heterogeneity · T07 Serving experiment · T08 Robustness summary.

**Figures**: F01 KO/EN token scatter · F02 TP distribution+ECDF · F03 Domain TP · F04 Log decomposition components · F05 ByteDensity vs CompressionPenalty · F06 Morphology partial effects · F07 Case audit panel · F08 Source/domain forest plot · F09 gpt-oss serving comparison.

---
See `docs/research/AMBIGUITIES_g0.md` for items the SSOT leaves numerically unspecified and therefore NOT frozen here.
