# NB07 — Canonical Descriptive EDA and Exact Decomposition

```
NOTEBOOK_ID          = notebooks/07_eda_and_decomposition.ipynb
RUN_ID               = NB07_CANONICAL_EDA_v001
EXECUTION_BASE_TYPE  = AUDITED_G5_HEAD
EXECUTION_BASE_SHA   = 9d99e13026b89dcf7d8846d0c105a811f64274bc
                       (origin/audit/g5-analysis-readiness-20260818)
G5_RESEARCH_HEAD     = 35a40e7c3541eff7a41ce853204409b128a6d676
BRANCH               = research/nb07-closeout-20260818
PRIOR_HANDOFF_SHA    = 8a1c5695d13604b38d842a6bde93208d1cfbce3e
                       (research/nb07-canonical-eda-20260818 — left immutable, §13)
WORKTREE             = /home/sieg/projects-wsl/KOEN_nb07_20260818
G5_STATUS            = G5_INDEPENDENT_AUDIT_PASS · G5_ANALYSIS_READINESS_PASS_WITH_NOTES
HEADLESS_STATUS      = PASS (jupyter nbconvert --execute, 85 cells, 0 error outputs, 129 s)
KOREAN_PLOT_FONT     = Noto Sans CJK KR
```

이 패키지는 **기술 통계 전용**이다. 모형을 적합하지 않고, 계수를 산출하지 않으며, RQ를
재검정하지 않는다. RQ1은 NB08의 동결 결과를 주석(annotate)만 한다. 인과 표현은 금지된다.

Default-branch publish는 로컬 harness 제약으로 `CANONICALIZATION_PENDING_OPERATIONAL_ONLY`
상태다. 이는 과학/Gate blocker가 아니며, 본 실행은 stale local main이 아니라 **감사된 G5 head**
에서 분기했다.

---

## 1. RQ map

| RQ | SSOT §6 원문 요지 | NB07의 역할 | 조건부·증분·mechanism 판단 |
|---|---|---|---|
| RQ1 | KO‑EN 문장쌍에서 o200k_base 기준 한국어 TP는 1보다 큰가 | NB08 동결 결과 **주석만** (bit-identical 재확인) | NB08 (CLOSED) |
| RQ2 | 세 성분(CodePointRatio · ByteDensityRatio · CompressionPenalty)의 분포 | **canonical NB07 결과** — 전수 항등식 검증 | 해당 없음 |
| RQ3 | 표면형 구조와 log TP·log CP의 조건부 연관 | 표면형 기술 구조만 | NB09 M1 vs M0 |
| RQ4 | 형태소 feature block의 증분 설명력 | 형태소 주변 분포만 | NB09 M2 vs M1 |
| RQ5 | regex chunk mechanism feature와 premium의 연결 | regex chunk 구조만 | NB09 M3 vs M2 |
| RQ6 | 도메인·방향·출처·길이 strata에 따른 이질성 | 기술적 이질성만 | NB09 이후 모형 기반 |
| RQ7 | Serving-level 차이 (Track B) | 범위 밖 | `DEFERRED_NOT_EXECUTED` |

## 2. SSOT map

이번 실행에서 **PDF 원문(`ssot/KOEN-TP-RS-001_v1.0_REDLINE_2026-08-16_1711KST.pdf`)을 직접
재추출해 section 번호를 재확인**했다. 인용 번호를 이전 세션에서 계승하지 않았다.

| 참조 | 내용 |
|---|---|
| §5 | 핵심 개념과 처리 모형 — 형태소 / regex chunking / subword tokenization 계층 구분 |
| §6.1–§6.7 | RQ1–RQ7 원문 정의 |
| §7.2 | Primary `log_token_premium`, Secondary `token_premium` · `log_compression_penalty` · `token_difference` |
| §8.1–§8.4 | TP · CodePointRatio · ByteDensityRatio · CompressionPenalty 정의와 정확 분해식 |
| §9.1 · §9.2 | 표본 규모 원칙(effect size 우선), 층화 변수 |
| §12.1–§12.5 | D‑01 … D‑05 스키마 |
| §15.3 | 형태소 feature block (primary / alternative) |
| **§16.2** | **필수 시각화 F01–F09 — figure 계약의 근거 조항** |
| **§16.3** | **Extreme-case audit — "극단값은 먼저 삭제하지 않는다"** |
| §17 | RQ1 통계 추론 및 보고 원칙 |
| §20.1 · §20.2 | Source effect와 식별 가능성 · Identifiability Gate |
| §21 | 공선성 및 compositional feature 처리 |
| §35 | 최종 표·그림 설계 (F01–F09 재기술) |
| Decision D‑01 | 주 검정을 ΔT가 아닌 log TP에 대해 수행 |
| IR‑01 | ByteDensityRatio와 CompressionPenalty를 분리 보고 |
| MN‑02 | chunk feature는 post-treatment — mechanism audit로 분리 |
| RR‑01 | 일반명 "pre-tokenization" 대신 `o200k_base regex chunking` 으로 기록 |

거버넌스: `RD-FAST-G5-01` · `RD-SSOT-CANONICAL-RETURN-01` ·
`RD-G5-ENTRY-GOVERNANCE-CLOSEOUT-01` · `ssot_g5/02_G5_DIAGNOSTIC_PROTOCOL_v001.md` ·
G5 adjudication (`ssot/2026-08-18_1325_…`) · G5 independent audit (`ssot/2026-08-18_1344_…`).

## 3. Artifact identity (fail-closed, 이 실행에서 재해싱)

| artifact | SHA-256 | 결과 | 배치 |
|---|---|---|---|
| D‑01 `PAIR_REGISTRY_v002` | `95f523d1…10bec52` | MATCH | symlink → canonical store |
| D‑02 `REP_FEATURES_v002` | `dfae8e01…50d309` | MATCH | symlink → canonical store |
| D‑03 `MORPH_FEATURES_KIWI_v001` | `0fe5bd74…3e50f7d` | MATCH | symlink → canonical store |
| D‑04 `TOKEN_O200K_BASE_v001` | `1c30e327…2c16e7` | MATCH | symlink → canonical store |
| D‑05 `CHUNK_O200K_BASE_v001` | `bfa98bd6…1944ab` | MATCH | **독립 복사본** (inode 1703860, link count 1 — hardlink 아님) |

```
ARTIFACT_IDENTITY = 5 / 5
COHORT_N          = 3,835,988
PAIR_SET_HASH     = d9660d654ee449e4d0c23a0070225274
null / non-finite = 0 / 0   (78개 열 전체)
rows deleted      = 0
```

## 4. 핵심 결과

### RQ2 — exact decomposition (canonical)

```
RQ2_DECOMPOSITION_STATUS = EXACT_IDENTITY_VERIFIED_FULL_COHORT
log TP = log CR + log BDR + log CP
max |error| = 8.882e-16   mean |error| = 9.704e-17   tolerance = 1e-12   rows outside = 0
```

| 성분 | 평균 | 중앙값 | 표준편차 | 양수 비율 |
|---|---:|---:|---:|---:|
| log TP (합계) | +0.285177 | +0.287682 | 0.222096 | 0.87985 |
| log CR (문자 수 비) | −0.753588 | −0.760451 | 0.222000 | 0.00193 |
| log BDR (byte 밀도 비) | +0.878476 | +0.896088 | 0.066225 | 0.99965 |
| log CP (압축 penalty) | +0.160289 | +0.175154 | 0.187665 | 0.80536 |

한국어의 premium은 "글자가 많아서"가 아니다. **문자 수 우위(log CR ≈ −0.75)가 UTF‑8 byte
밀도 열위(log BDR ≈ +0.88)에 의해 상쇄되고도 남고, 거기에 tokenizer 압축 열위
(log CP ≈ +0.16)가 더해져** 순 premium(+0.29)이 남는다. 문자 수는 적은데 token 수는 많은
**표현 역전**이 3,363,717쌍(87.6884%)으로 다수 사례다.

IR‑01 관련 관찰: `log BDR`과 `log CP`의 전수 Spearman ρ는 **−0.0507** — 사실상 무연관이다.
UTF‑8 표현 부담과 tokenizer 압축 성능은 이 자료에서 서로 다른 축으로 움직인다.

### RQ1 — annotation only

```
RQ1_ANNOTATION = ANNOTATED_ONLY (closed in NB08, not re-tested here)
median log TP  = 0.2876820724517808     median TP = 4/3 = 1.3333…     premium 33.33%
P(TP > 1)      = 0.8798502498           median CI = degenerate (점질량 123,040)
p 보고 형식     = p < 1e-300
```

NB07이 독립적으로 재계산한 기술통계가 NB08 값과 정확히 일치했다(median log TP 차이 0,
TP = 1 개수 196,718 대 196,718). 이는 재현성 확인이며 독립 증거의 추가가 아니다.

## 5. Figure map

계약: **SSOT §16.2 · §35**. NB07이 dependency-ready로 생성한 canonical figure는
`F01 · F02 · F03 · F04 · F05 · F07` 이다.

| figure_id | 제목 | RQ | 계약 | PNG SHA-256 |
|---|---|---|---|---|
| `NB07-S01_cohort_composition_v001` | 분석 cohort 구성 | RQ6 | SUPPORTING_DESCRIPTIVE | `e9878958cbac…` |
| `NB07-REF-ID-03_source_domain_support_v001` | 출처 × 도메인 관측 support | RQ6 | G5_REVIEW_REGISTER | `926fd9dd07d2…` |
| `NB07-REF-ID-04_cell_direction_support_v001` | 출처-도메인 셀 × 번역 방향 support | RQ6 | G5_REVIEW_REGISTER | `1e4b7596e66b…` |
| `F01_token_count_relationship_v001` | 한국어–영어 token 수 관계 | RQ1 | SSOT_§16.2_F01 — KO vs EN paired token scatter, identity line | `07cd8e33503f…` |
| `F02_tp_distribution_ecdf_v001` | Tokenization Premium 분포와 ECDF | RQ1 | SSOT_§16.2_F02 — TP histogram + ECDF | `36d5fe0f9c70…` |
| `NB07-S02_token_difference_v001` | 절대 token 차이 ΔT 기술 | RQ1 | SUPPORTING_DESCRIPTIVE | `8a65189785e5…` |
| `F04_exact_decomposition_v001` | 정확 분해 성분 분포 | RQ2 | SSOT_§16.2_F04 — exact decomposition component distribution | `da415362a7fb…` |
| `F05_byte_density_vs_compression_v001` | UTF-8 표현 부담 대 압축 penalty | RQ3 | SSOT_§16.2_F05 — ByteDensityRatio vs CompressionPenalty | `27b6ef435ebc…` |
| `NB07-S03_representation_structure_v001` | 표현 구조 기술 | RQ3 | SUPPORTING_DESCRIPTIVE | `8b7b1750da9f…` |
| `NB07-S04_morphology_distributions_v001` | 형태소 분포 | RQ4 | SUPPORTING_DESCRIPTIVE | `d6fc1d1187f4…` |
| `NB07-S05_chunk_mechanism_v001` | regex chunk mechanism 기술자 | RQ5 | SUPPORTING_DESCRIPTIVE | `9b048c415c30…` |
| `NB07-REF-M3-01_chunk_scale_vs_length_v001` | chunk 규모 대 절대 길이 | RQ5 | G5_REVIEW_REGISTER | `280d9ba57807…` |
| `NB07-REF-M3-01B_chunk_density_constructs_v001` | chunk 밀도 재모수화 후보 구조 | RQ5 | G5_REVIEW_REGISTER_ADDENDUM | `46d658b80c18…` |
| `NB07-REF-M3-01C_chunk_density_by_length_v001` | 길이 층별 chunk 밀도 | RQ5 | G5_REVIEW_REGISTER_ADDENDUM | `3bfc26da9c34…` |
| `NB07-REF-SM-01_script_mixing_structure_v001` | script mixing 기술자 구조 | RQ3 | G5_REVIEW_REGISTER | `0a43b360f1bd…` |
| `NB07-S06_analysis_layer_boundary_v001` | 분석 계층 경계표 | RQ4/RQ5 | SUPPORTING_DESCRIPTIVE_ADDENDUM | `32dd9a3533d9…` |
| `F03_domain_tp_descriptive_v001` | 도메인별 TP 기술 분포 | RQ6 | SSOT_§16.2_F03 — domain별 TP violin/box | `e349525efded…` |
| `NB07-S07_heterogeneity_v001` | 층별 기술적 이질성 | RQ6 | SUPPORTING_DESCRIPTIVE | `704b3f3f8848…` |
| `F07_extreme_case_audit_v001` | 극단 TP 사례 audit | RQ1/RQ5 | SSOT_§16.2_F07 — extreme TP case audit panel | `23e8866ed5b5…` |
| `NB07-S08_eojeol_count_one_v001` | eojeol_count = 1 재검토 | RQ4 | SUPPORTING_DESCRIPTIVE | `e46aaa24938b…` |
### Dependency-deferred

| figure_id | 내용 | 상태 | 의존 |
|---|---|---|---|
| `F06` | 형태소 밀도와 log TP의 부분 관계 | `DEFERRED_BY_DEPENDENCY` | NB09 M2 vs M1 |
| `F08` | 출처·도메인 설명 forest plot | `DEFERRED_BY_DEPENDENCY` | NB09 설명모형 계수 |
| `F09` | gpt‑oss serving 비교 | `DEFERRED_BY_DEPENDENCY` | NB12 Track B (D‑06 · D‑07) |

### 명명 규칙

- `Fxx` 는 SSOT §16.2 계약 figure 전용이다.
- 보조 기술 figure는 `NB07-Sxx`, G5 review figure는 `NB07-REF-xx` 접두사를 쓴다.
- **`NB08-RQ1-Vxx` 와 `NB06_D05_Vxx` 는 reference 전용이며 절대 `Fxx` 로 개명하지 않는다.**

## 6. G5 review references

이 항목들은 NB07의 추론적 결론이 **아니다**. G5가 등록한 검토 항목이 어떤 자료 구조에서
나왔는지를 보이게 만든 기술 증거다.

### `M3-01` — chunk 규모 대 절대 길이 (`NB07-REF-M3-01` / `-01B` / `-01C`)

G5 관측: M3 condition number 134.57, 최대 VIF 1,252.61. 신선 재계산:

```
ρ(pair_log_size, ko_chunk_count_log) = 0.962502
ρ(pair_log_size, en_chunk_count_log) = 0.969426
ρ(ko_chunk_count_log, en_chunk_count_log) = 0.936764   ← G5 0.9368 과 일치
```

애드덤(재모수화 후보 construct 확인): 밀도 형태로 바꾸면 규모 의존이 크게 약해지고 부호가
뒤집힌다 — `ko_chunk_per_codepoint` ρ = −0.3241, `en_chunk_per_codepoint` ρ = −0.5946,
`ko_chunk_per_byte` ρ = −0.2396, `en_chunk_per_byte` ρ = −0.5949,
`ko_chunk_per_eojeol` ρ = −0.3111, `en_chunk_per_word` ρ = −0.3000.
다만 밀도는 **완전한 규모 불변이 아니다**: 한국어 밀도 중앙값이 Q1 0.3333 → Q5 0.2841,
영어가 Q1 0.2432 → Q5 0.1795로 길이 층을 따라 단조 감소한다.

```
M3_REPARAMETERIZATION_DECISION = NOT_MADE_HERE
NB09_MATRIX_CHANGED = NO
ROUTED_TO = NB11 sensitivity   (VD-BASELINE-20260818-1520 §3)
```

### Carry-forward 운영 배치 (VD-BASELINE-20260818-1520 §3)

아래 `M3-01` · `SM-01` 은 **REVIEW** 이며 **G5를 재개방하지 않는다**. 운영 배치는 Vice Director
baseline이 정한 것이고 NB07의 판단이 아니다. NB07은 그 배치의 **근거가 되는 기술 증거**를
제공할 뿐이다.

| 항목 | primary span | 해석 제약 | 대안 모수화 |
|---|---|---|---|
| `SM-01` | M1 **FROZEN** | `script_type_count` 와 `script_switch_count` 를 **두 개의 독립적 실질 효과로 해석하지 않는다** | **NB11 sensitivity** |
| `M3-01` | M3 **FROZEN** | raw chunk-count 계수를 **개별 실질 mechanism 효과로 해석하지 않는다**. RQ5 primary 증거는 **M3−M2 block 비교** | **NB11 sensitivity** |

**VIF만을 근거로 한 feature 삭제는 없다.** NB07은 대표 feature를 고르지도, 재모수화를
결정하지도 않았다.

### `SM-01` — script mixing 기술자 (`NB07-REF-SM-01`)

신선 Spearman이 G5 참조값과 일치한다: **영어 0.9993520546** (G5 0.9994),
**한국어 0.9910090163** (G5 0.9910). 물질적 불일치 없음.

애드덤 구조 확인 결과, 높은 전체 상관은 **구성개념의 동일성이 아니라 support 희소성**에서
나온다. `type_count = 1` 이면 `switch_count = 0` 이 대수적으로 강제되고, 관측의
77.6783%(KO) · 93.0430%(EN)가 그 단일 셀에 있다. 실제로 script가 섞인 `type ≥ 2`
부분집합 안에서는 ρ가 **한국어 0.2038, 영어 0.0522**로 급락한다.

| 측 | type=0 | type=1 | type=2 | type=3 | `I(type≥2)` prevalence |
|---|---:|---:|---:|---:|---:|
| 한국어 | 183 | 2,979,730 | 837,261 | 18,814 | 856,075 (22.3169%) |
| 영어 | 217 | 3,569,117 | 266,575 | 79 | 266,654 (6.9514%) |

`script_type_count` 는 **script 종류의 존재 다양성**을, `script_switch_count` 는
**문자열을 따라가며 일어나는 전환 빈도**를 센다. 같은 두 종류라도 전환 1회와 34회는
다른 텍스트다.

```
SM01_REPRESENTATIVE_FEATURE_CHOICE = NOT_MADE_HERE
ROUTED_TO = NB11 sensitivity   (VD-BASELINE-20260818-1520 §3)
```

### `ID-03` — source × domain support (`NB07-REF-ID-03`)

실현 셀 5 / 8, 빈 셀 3. 두 출처 모두에서 관측되는 도메인은 `other` 하나뿐이다.

| source | dialogue | general | other | technology |
|---|---:|---:|---:|---:|
| 025 | 516,162 | 804,291 | 1,165,510 | **0** |
| 026 | **0** | **0** | 990,120 | 359,905 |

따라서 **`025-other` 대 `026-other` 만이 "동일 도메인 내 출처 층 대비
(same-domain source-stratum contrast)"** 로 성립한다. 이것조차 **순수 source 효과가 아니다**.
source와 domain은 분리 식별되지 않으며, `source_domain_cell` 은 관측 층 조건부 통제일 뿐이다.

### `ID-04` — source_domain_cell × translation_direction support (`NB07-REF-ID-04`)

| cell | KO_TO_EN | EN_TO_KO | UNKNOWN |
|---|---:|---:|---:|
| 025-dialogue | 247,947 | 254,955 | 13,260 |
| 025-general | 354,654 | 449,606 | **31** |
| 025-other | 559,527 | 568,728 | 37,255 |
| 026-other | 990,119 | **0** | **1** |
| 026-technology | 359,905 | **0** | **0** |

빈 셀 3 / 15, near-singleton(n ≤ 100) 2개. **026 계열에는 `EN_TO_KO` 관측이 하나도 없다.**
`UNKNOWN` 50,547쌍은 **제거하지 않고 보존**한다. 방향 대비는 025 내부 변동에서만 식별되며,
`cell × direction` 상호작용은 추정 불가능하므로 도입하지 않는다.

### 분석 계층 경계표 (`NB07-S06`)

| 계층 | 산출 단위 | 산출 주체 | 버전 민감도 | 한국어 중앙값 | 영어 중앙값 |
|---|---|---|---|---:|---:|
| ① 언어학적 형태소 분석 | 어절 / 형태소 | Kiwi (D‑03) | 분석기·모델 의존 | 9 / 19 | 13 (표층 단어) |
| ② `o200k_base` regex chunking | regex chunk | tiktoken `pat_str` (D‑05) | tokenizer 구현 의존 | 11 | 15 |
| ③ 최종 subword tokenization | o200k_base token | tiktoken BPE merge (D‑04) | 매우 큼 | 21 | 16 |

세 계층은 단조 정렬조차 되지 않는다(한국어: 9 → 19 → 11 → 21). **계층 사이에 포함 관계가
없다.** SSOT §5에 따라 언어학적 경계는 ①에서만 중요하며 ②·③에서는 보장되지 않는다.

## 7. Anomaly references

정책: **자동 삭제 없음.** 모든 극단은 등록되며 제거되지 않는다 (SSOT §16.3).

```
ANOMALY_TOTAL = 17
  EXPECTED_BOUNDARY = 7 · PLAUSIBLE_EXTREME = 4 · REVIEW_REQUIRED = 5 · POSSIBLE_DEFECT = 1
rows deleted = 0
```

| ref | 관측 | n | 비율 | 상태 | primary cohort |
|---|---|---:|---:|---|---|
| `EDA-REF-A01` | TP ≤ 1 — 한국어 token 수가 영어 이하 | 460,893 | 12.0150% | `EXPECTED_BOUNDARY` | INCLUDED |
| `EDA-REF-A02` | TP = 1 정확 일치 (이산 격자의 점질량) | 196,718 | 5.1282% | `EXPECTED_BOUNDARY` | INCLUDED |
| `EDA-REF-A03` | 상위 꼬리 TP ≥ 3 | 3,647 | 0.0951% | `PLAUSIBLE_EXTREME` | INCLUDED |
| `EDA-REF-A04` | 하위 꼬리 TP < 0.5 | 1,203 | 0.0314% | `PLAUSIBLE_EXTREME` | INCLUDED |
| `EDA-REF-A05` | eojeol_count = 1 — 어절 1개 텍스트 | 42,096 | 1.0974% | `EXPECTED_BOUNDARY` | INCLUDED |
| `EDA-REF-A06` | script_type_count = 0 (KO 또는 EN 측) | 243 | 0.0063% | `REVIEW_REQUIRED` | INCLUDED |
| `EDA-REF-A07` | ko_hangul_share < 0.1 — 한국어 측에 한글이 거의 없음 | 1,400 | 0.0365% | `REVIEW_REQUIRED` | INCLUDED |
| `EDA-REF-A08` | en_hangul_share > 0.1 — 영어 측에 한글이 남아 있음 | 14 | 0.0004% | `POSSIBLE_DEFECT` | INCLUDED |
| `EDA-REF-A09` | log ByteDensityRatio < 0 — 한국어 byte 밀도가 영어보다 낮음 | 21 | 0.0005% | `PLAUSIBLE_EXTREME` | INCLUDED |
| `EDA-REF-A10` | regex chunk 수 = 1 (KO 또는 EN 측) | 568 | 0.0148% | `EXPECTED_BOUNDARY` | INCLUDED |
| `EDA-REF-A11` | translation_direction = UNKNOWN | 50,547 | 1.3177% | `EXPECTED_BOUNDARY` | INCLUDED |
| `EDA-REF-A12` | particle_ratio = 0 — 조사가 하나도 없는 문장 | 292,186 | 7.6170% | `EXPECTED_BOUNDARY` | INCLUDED |
| `EDA-REF-A13` | morpheme_density > 10 — 어절당 형태소 10개 초과 | 9 | 0.0002% | `PLAUSIBLE_EXTREME` | INCLUDED |
| `EDA-REF-A14` | en_max_chunk_bytes > 200 — 극단적으로 긴 단일 regex chunk | 2 | 0.0001% | `REVIEW_REQUIRED` | INCLUDED |
| `EDA-REF-A15` | 표현 역전 — log CR < 0 이면서 log TP > 0 | 3,363,717 | 87.6884% | `EXPECTED_BOUNDARY` | INCLUDED |
| `EDA-REF-M3-01` | G5 REVIEW M3-01 — chunk 규모와 절대 길이의 근접 비례 | 3,835,988 | 100.0000% | `REVIEW_REQUIRED` | N/A (구조 검토 항목) |
| `EDA-REF-SM-01` | G5 REVIEW SM-01 — script_type_count 과 script_switch_count 의 near rank-equivalence | 3,835,988 | 100.0000% | `REVIEW_REQUIRED` | N/A (구조 검토 항목) |
명시적 재검토 항목 `eojeol_count = 1`:

```
EOJEOL1_COUNT = 42,096
EOJEOL1_SHARE = 1.097397%
```

D‑02 `ko_eojeol_count` 와 D‑03 `eojeol_count` 가 같은 개수를 준다. 이 집단은 매우 짧은
텍스트(제목·항목·짧은 구)로, 025·general에 40,587건이 집중되어 있다. log TP 중앙값 0.0,
`TP > 1` 비율 49.40%, `TP = 1` 비율 27.20%로 나머지 집단(88.41% · 4.88%)과 크게 다르다.
어절이 1개이므로 `morpheme_density = morpheme_count` 가 되어 밀도 상단 꼬리를 만든다.
**이것을 "언어적 복잡도"라고 부르지 않는다.** 텍스트 길이·형식 지표이지 복잡도 척도가 아니다.

## 8. Claim boundary

**허용된 주장** — 실현 cohort의 기술통계·분포·결합밀도·층별 요약, exact decomposition
항등식의 전수 성립, G5 검토 항목과 식별 support의 기술적 가시화, NB08 RQ1 결과의 인용.

**성립하지 않는 것** — 이 패키지의 어떤 내용도 다음을 확립하지 않는다:

```
어떤 설명 결과도 존재한다는 것
형태소 block이 증분 설명력을 갖거나 갖지 않는다는 것
어떤 계수도 추정되었다는 것
출처와 도메인 효과가 분리되었다는 것
M3가 적합 가능한 상태라는 것
regex chunking이 fragmentation을 설명한다는 것
NB09 대표 feature 또는 재모수화의 선택
어떤 인과 진술
```

**PRE-NB09 애드덤 증거의 지위**: §07 · §15 · §16 · §17의 추가 결과는
`DESCRIPTIVE EVIDENCE FOR PRE-NB09 REVIEW` 이며, NB09 decision이나 feature selection으로
승격되지 않는다. **NB09 matrix는 이 노트북에서 변경되지 않았다.**

## 9. Privacy

```
RAW_TEXT_COMMITTED               = NO
TOKEN_ID_ARRAYS_COMMITTED        = NO
RECOVERABLE_PAIR_EXAMPLES        = NO
LEGACY_CASEBOOK_NUMERICAL_SOURCE = NO
```

극단 사례 개별 점검이 필요한 경우를 위해 로컬 전용 private audit 파일
`outputs/manual_audit/nb07_private/NB07_EXTREME_CASE_PRIVATE_v001.csv` (968행)을 남긴다.
이 파일은 `.gitignore` 대상이며 **원문 문장도 token ID도 포함하지 않는다**.
공개 artifact에는 집계·sanitize된 기술자만 들어간다.

`notebooks/exploratory/EDA_representation_kiwi_o200k_casebook.ipynb` 는
`LEGACY_UNTRACKED_REFERENCE_ONLY` 다. 이 실행은 그 파일을 열지 않았고, 어떤 수치도
그 파일에서 가져오지 않았다.

## 10. Validation

| 검증 | 결과 |
|---|---|
| exact decomposition 전수 tolerance | **PASS** (max 8.882e-16 ≤ 1e-12, 3,835,988행) |
| artifact SHA-256 재해싱 | **PASS** (5/5) |
| cohort 신원 (N · pair-set hash) | **PASS** |
| 한글 glyph smoke (저장된 SVG 재검사) | **PASS** (20/20 figure에 한글 text 존재, missing-glyph warning 0) |
| manifest ↔ figure 일치 + SHA 재확인 | **PASS** (20 PNG ↔ 20 manifest 항목) |
| 원문 유출 검사 | **PASS** (`pair_id` 목록 없음, 공개 artifact에 원문·token ID 없음) |
| headless 실행 | **PASS** (85 cells, 0 error outputs) |

**figure 재현성**: 서로 다른 **세** 번의 headless 실행에서 20개 PNG 전체가 **bit-identical**
(집합 md5 `5711dbeabf3cf0aac679389a5c36e8ad`)이었다. `svg.hashsalt` 와 figure metadata가
고정되어 있기 때문이다.

**Long-run observability**: 30초를 넘길 수 있는 모든 단계는 `RuntimeTelemetry`
(ENG-OBS-001 · R1) 10초 주기 heartbeat 아래에서 실행되었다 —
stage · elapsed · processed/total · throughput · RSS · MemAvailable · status.
cohort 조립 단계에서 3표본, 최악 상태 `YELLOW`, peak RSS 3.465 GiB,
최소 MemAvailable 7.321 GiB. 신뢰할 수 있는 분모가 없는 percent/ETA는 생성하지 않았다.

## 11. Reproduction

```bash
git worktree add /home/sieg/projects-wsl/KOEN_nb07_20260818 \
    -b research/nb07-canonical-eda-20260818 origin/audit/g5-analysis-readiness-20260818
cd /home/sieg/projects-wsl/KOEN_nb07_20260818

# D-05 는 검증된 NB06/G5 원본에서 read-only 복사본으로 배치한다 (hardlink 금지)
cp --reflink=auto /home/sieg/projects-wsl/KOEN_g5_readiness_20260818/data/registry/CHUNK_O200K_BASE_v001.parquet \
   data/registry/CHUNK_O200K_BASE_v001.parquet

export PYTHONPATH=$PWD/src
jupyter nbconvert --to notebook --execute --inplace \
    --ExecutePreprocessor.timeout=1800 notebooks/07_eda_and_decomposition.ipynb
```

노트북은 `.runtime/nb07/nb07_matrix.parquet` (약 430 MB, `.gitignore` 대상)를 매 실행마다
새로 조립한다. 어떤 canonical 수치도 캐시에서 재사용되지 않는다.

## 12. Superseded artifacts

이 branch의 선행 commit `1adfa93` (`research(nb07): execute canonical EDA and exact
decomposition`, 2026-08-18 14:42 KST)에는 **다른 실행선(working line)이 만든 NB07 산출물**이
들어 있다 (`EDA_REF_*`, `_v001` 접미사가 없는 `F0x_*`, `NB07_KOREAN_FONT_SMOKE`).

현재 commit이 그 산출물을 **대체(supersede)** 한다. 대체된 파일은 삭제된 것이 아니라
`1adfa93` 에 그대로 보존되어 있으므로 언제든 복원·대조할 수 있다. 대체 사유:

- figure 계약 근거 조항을 **PDF 원문에서 재추출해 §16.2 · §35 로 정정**했다
  (선행 실행선은 `§16.2` 를 재검증 없이 계승했다고 자체 기록했다).
- 애드덤이 요구한 증거 — SM-01 결합 빈도·support·`I(type≥2)`·부분집합 내부 구조,
  M3-01 밀도 재모수화 후보와 길이 quantile별 분포, 분석 계층 경계표 — 를 포함한다.
- manifest ↔ figure 일치 검증이 하나의 canonical figure 집합을 요구한다.

두 실행선이 같은 worktree에서 동시에 진행된 결과이며, 과학적 판정의 충돌이 아니다.

## 13. Closeout corrections (this branch)

`research/nb07-canonical-eda-20260818` @ `8a1c569` 로 handoff를 선언한 뒤, 스스로 재검증하는
과정에서 **본문 해석 markdown의 결함 3건**을 발견했다. Branch immutability (VD baseline §8)에
따라 그 SHA를 수정하지 않고 **새 branch에서 정정**했다. 그림·표·수치 산출 코드는 바뀌지
않았으며, 20개 figure는 정정 전후로 **bit-identical**이다.

| # | 위치 | 결함 | 정정 |
|---|---|---|---|
| C‑01 | §12 분포 해석 | "(b)의 두 봉우리(한국어 ≈ **2.57**, 영어 ≈ 1.00)" — 2.57은 최빈값이 아니라 95 분위다 | 실측 최빈 구간으로 정정: 한국어 ≈ **2.50**, 영어 = 1.0000 (3,821,117쌍 · 99.61%) |
| C‑02 | §12 · §11 | "…결정한다" · "…압축하지 못해서 발생한다" — 항등식·주변분포에 대한 기술에 결정론적/인과적 동사 사용 | 산술적 구성에 대한 진술로 재작성하고, 인과 진술이 아님을 명시 |
| C‑03 | §16 해석 한계 | "G5는 **두 변수**의 VIF가 약 9.1로…" — G5가 보고한 9.11–9.16은 `en_script_type_count` 기준이다 | 출처를 정확히 귀속하고, G5가 짝의 두 변수 각각을 별도 보고하지는 않았음을 명시 |

추가로 carry-forward 배치를 `VD-BASELINE-20260818-1520` §3에 맞춰 기록했다
(이전 표기 `PRE_NB09_*_REVIEW_REQUIRED` → **NB11 sensitivity**). 이는 NB07의 결정이 아니라
상위 baseline의 운영 배치를 인용한 것이다.

**과학적 결과는 하나도 바뀌지 않았다.** cohort, 항등식 검증, 모든 분위·상관·빈도, anomaly
register(17건), figure 20종의 SHA-256이 전부 동일하다.

---

```
NB07_CANONICAL_EXECUTION_COMPLETE
NB07_CLOSEOUT_COMPLETE
READY_FOR_CLAUDE_B_NB07_SCIENCE_SCOPE_AUDIT
DO_NOT_MERGE_MAIN
```
