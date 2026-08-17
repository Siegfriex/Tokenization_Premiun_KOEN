# KOEN EDA V2 — PRE-G5 Diagnostics

```
Status:  G-ID CANDIDATE EVIDENCE — formal G5 verdict 아님
Basis:   final cohort N = 3,835,988 (전수)
run_id:  EDA_V2_PRE_G5_20260817T181311
```

G5 판정 권한은 이 lane에 없다. 아래는 **§20.2 Gate G-ID가 회귀 실행 전에 확인하라고 지시한
항목의 증거**이며, 판정은 Claude-B / Director의 몫이다.

---

## 1. Identifiability — support 구조

### 1.1 교차표 (전수)

**`domain × source_id`** (= `domain × logical_corpus`와 동일 구조)

| domain | 025-family | 026-family |
|---|---:|---:|
| dialogue | 516,162 | **0** |
| general | 804,291 | **0** |
| other | 1,165,510 | 990,120 |
| technology | **0** | 359,905 |

**`domain × translation_direction`**

| domain | EN_TO_KO | KO_TO_EN | UNKNOWN |
|---|---:|---:|---:|
| dialogue | 254,955 | 247,947 | 13,260 |
| general | 449,606 | 354,654 | 31 |
| other | 568,728 | 1,549,646 | 37,256 |
| technology | **0** | 359,905 | **0** |

**`source_id × logical_corpus`**

| source_id | 025 | 026 |
|---|---:|---:|
| 025-family | 2,485,963 | **0** |
| 026-family | **0** | 1,350,025 |

### 1.2 Provisional classification

| 교차 | shape | zero cells | min support | provisional | 근거 |
|---|---|---:|---:|---|---|
| `domain × source_id` | 4×2 | 3 | 359,905 | `PARTIALLY_IDENTIFIABLE` | 일부 수준(3개)만 배타적 support |
| `domain × logical_corpus` | 4×2 | 3 | 359,905 | `PARTIALLY_IDENTIFIABLE` | 동일 |
| `domain × translation_direction` | 4×3 | 2 | 31 | `PARTIALLY_IDENTIFIABLE` | 일부 수준(1개)만 배타적 support |
| `source_id × translation_direction` | 2×3 | 1 | 1 | `PARTIALLY_IDENTIFIABLE` | 일부 수준(1개)만 배타적 support |
| **`source_id × logical_corpus`** | 2×2 | 2 | 1,350,025 | **`STRUCTURALLY_CONFOUNDED`** | 한 축의 모든 수준이 다른 축의 단일 수준에만 support |

### 1.3 읽는 법 — 무엇이 실제로 문제인가

1. **`source_id`와 `logical_corpus`는 같은 분할이다** (1:1 대응). 두 변수를 동시에 모형에 넣으면
   완전 공선이다. 둘 중 하나만 쓰거나 composite로 다뤄야 한다.
   → 이것이 V1 caveat C3이 유보했던 지점의 해소다.
2. **`other`만이 유일한 within-domain source 대비를 제공한다** (025 1,165,510 / 026 990,120).
   나머지 세 domain은 단일 source에만 존재하므로, `other`를 제외하면 domain과 source는
   완전 교락이다.
3. **`technology`는 방향까지 고정**(KO_TO_EN 359,905 / EN_TO_KO 0)이라
   domain·source·direction 세 축이 동시에 묶인다.
4. `translation_direction = UNKNOWN`은 50,547건(1.32%)이며 `general`에는 31건뿐이다 —
   방향 통제 시 이 수준의 support가 층마다 극단적으로 불균형이다.

### 1.4 zero variance

| 변수 | 수준 수 | 엔트로피 | 상태 |
|---|---:|---:|---|
| `sentence_type` | **1** (`other`) | **0.000000 bits** | **`ZERO_VARIANCE`** |

`REALIZED_DESIGN_LIMITATION` — SSOT §9.2는 7개 수준을 설계했으나 realized cohort는 전량이
`other`다. 이는 D-01 필드 계약(source 값 없으면 `other`)의 귀결이며 데이터 결함이 아니다.
§18 모형에서 이 항은 어떤 대비도 만들 수 없다.

`CHANGE_REQUEST_CANDIDATE` (제안일 뿐 — 이 lane에 승인 권한 없음):
**"§18 모형 명세에서 `sentence_type` 항의 처리를 Director가 명시적으로 결정할 것"**
(제거 / 유보 / 원천 재수집 중 무엇인지는 연구 설계 결정이다).

또한 `en_bytes_per_codepoint`는 IQR = 0 (p01–p99 전부 1.0)이며 사실상 상수다.

---

## 2. Collinearity / deterministic overlap (§21, §32 T-06)

**두 종류를 반드시 분리한다.** 아래 1군은 상관계수로 "발견"되는 것이 아니라 **정의상 성립**한다.

### 2.1 결정론적 종속성 (모형 투입 전 반드시 해소)

| 관계 | 종류 | SSOT | 모형 함의 |
|---|---|---|---|
| `logTP = logCR + logBDR + logCP` | `EXACT_IDENTITY` | §8 | 네 변수 중 셋만 자유. 넷 동시 투입 = 완전 공선 |
| `TP = CR × BDR × CP` | `EXACT_IDENTITY` | §8 | 위의 지수 형태 |
| `bytes_per_codepoint = utf8_bytes / codepoint_count` | `EXACT_DEFINITION` | §13.3 | 셋 중 둘만 자유 |
| `BDR = (B_KO/C_KO)/(B_EN/C_EN)` | `EXACT_DEFINITION` | §8.3 | 양측 bytes/cp에서 완전 결정 |
| `CR = C_KO / C_EN` | `EXACT_DEFINITION` | §8.2 | 양측 codepoint에서 완전 결정 |
| `CP = (T_KO/B_KO)/(T_EN/B_EN)` | `EXACT_DEFINITION` | §8.4 | token·byte에서 완전 결정 |
| `morpheme_density = morpheme_count / eojeol_count` | `EXACT_DEFINITION` | §13.6 | 셋 중 둘만 자유 |
| `particle/ending/deriv_affix_ratio` | `COMPOSITIONAL` | §13.7, §21 | 분모 공유. `function_morpheme_ratio = particle + ending` → **동시 투입 금지** |
| script share 6종 | `COMPOSITIONAL` | §12.2, §21 | 합 = 1. 참조 범주 제외 또는 compositional transform 필요 |

### 2.2 경험적 상관 `[V2-SAMPLE200,000]`

정의상 독립인 변수들 사이의 Spearman ρ는 `V2-C01` figure에 있다. **p-value는 계산하지 않았다**
(§17.3). `logCR`·`logBDR`이 `logTP`와 갖는 큰 \|ρ\|는 §8 항등식의 귀결이므로 발견이 아니다.

---

## 3. Exact decomposition — population 구조

| 성분 | p01 | p05 | p25 | median | p75 | p95 | p99 | min | max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `log CR` | −1.2796 | −1.0986 | −0.8954 | **−0.7605** | −0.6190 | −0.3868 | −0.1823 | −3.8080 | 4.0943 |
| `log BDR` | +0.6466 | +0.7571 | +0.8561 | **+0.8961** | +0.9163 | +0.9445 | +0.9651 | −0.4055 | 1.0986 |
| `log CP` | −0.3254 | −0.1671 | +0.0416 | **+0.1752** | +0.2901 | +0.4407 | +0.5549 | −1.5404 | 1.6376 |
| `log TP` | −0.2877 | −0.0870 | +0.1542 | **+0.2877** | +0.4274 | +0.6360 | +0.8109 | −2.7486 | 3.6376 |

### 3.1 성분 부호 조합 (상위 8)

| CR | BDR | CP | TP | n | share |
|---:|---:|---:|---:|---:|---:|
| − | + | + | + | 2,863,051 | **74.64%** |
| − | + | − | + | 490,267 | 12.78% |
| − | + | − | − | 138,813 | 3.62% |
| − | + | + | − | 123,550 | 3.22% |
| − | + | + | 0 | 99,801 | 2.60% |
| − | + | − | 0 | 85,034 | 2.22% |
| − | + | 0 | 0 | 10,505 | 0.27% |
| − | + | 0 | + | 10,369 | 0.27% |

상위 8개 조합 전부에서 `CR < 0`, `BDR > 0`이다. 변동은 사실상 `CP`의 부호에서 온다.

### 3.2 pair 단위 상쇄 구조

**중앙값 합을 중앙값 분해로 쓰지 않았다.** 각 pair에서 `CR + BDR`을 직접 계산했다.

| 수량 | p25 | median | p75 |
|---|---:|---:|---:|
| `logCR + logBDR` (상쇄분) | −0.0153 | **+0.1193** | +0.2624 |
| `logCP` | +0.0416 | **+0.1752** | +0.2901 |
| `logTP` | +0.1542 | +0.2877 | +0.4274 |

**`|logCP| > |logCR + logBDR|`인 pair = 54.04%** — 과반이다.
V1이 n=40에서 관측한 "CP가 표현층 상쇄분보다 크다"는 신호가 모집단에서 다수 사례로 확인된다.

---

## 4. Morphology (full D-03)

| 항목 | 값 |
|---|---:|
| N | 3,835,988 |
| `eojeol_count = 1` (`MEASUREMENT_BOUNDARY_REGION`) | **42,096** (1.0974%) |
| `analysis_warning_flag` | **0** |
| `morpheme_count = 0` | **0** |
| ratio NULL | **0** |
| `morpheme_density` median | 2.2143 |
| `particle_ratio` median | 0.1579 |
| `ending_ratio` median | 0.1754 |
| `deriv_affix_ratio` median | 0.0667 |
| `function_morpheme_ratio` median | 0.3421 |

`morpheme_density` 분모는 SSOT §13.6대로 `eojeol_count`다.
density 극댓값을 **linguistic complexity라고 부르지 않는다** — 경계 구역의 척도 차이일 수 있다.

---

## 5. Analysis cohort diagnostic

4-way join(REP ⋈ MORPH ⋈ TOKEN ⋈ registry) 결과 정확히 3,835,988행.

| check | n | share |
|---|---:|---:|
| logTP NULL / 비유한 | 0 | 0% |
| logCP 비유한 | 0 | 0% |
| token count ≤ 0 | 0 | 0% |
| roundtrip 실패 | 0 | 0% |
| identity 오차 ≥ 1e-10 | 0 | 0% |
| morpheme_density NULL | 0 | 0% |
| eojeol_count ≤ 0 | 0 | 0% |
| analyzer warning | 0 | 0% |
| codepoint ≤ 0 | 0 | 0% |
| domain / source_id / length_stratum NULL | 0 | 0% |
| **direction UNKNOWN** | **50,547** | **1.3177%** |

**모형 소비 차단 요인: 없음.** 극단값만으로 어떤 행도 제외하지 않았고 primary cohort를
변경하지 않았다 (§16.3 / D-RD-08).

### 5.1 Sensitivity subset 후보 (제안일 뿐 — 적용하지 않음)

| subset | 조건 | n | share |
|---|---|---:|---:|
| known-direction only | `translation_direction <> 'UNKNOWN'` | 3,785,441 | 98.68% |
| `eojeol_count > 1` | 측정 경계 제외 | 3,793,892 | 98.90% |
| short-text 제외 | `ko_codepoint_count > 11` (p05) | 3,637,590 | 94.83% |
| 두 corpus 모두 있는 domain만 | `domain = 'other'` | 2,155,630 | 56.19% |
| length Q2–Q4 | 길이 극단 제외 | 2,387,120 | 62.23% |

---

## 6. Split manifest preview — **BLOCKER**

| 항목 | 값 |
|---|---:|
| `duplicate_group_id` group 수 | 3,835,988 |
| cohort 행수 | 3,835,988 |
| 최대 group 크기 | **1** |
| 단일 원소 group | 3,835,988 (**100.00%**) |

**이 결과는 "중복이 없어 안전하다"가 아니라 "이 열로는 group을 만들 수 없다"는 뜻이다.**
final cohort가 이미 `analysis_eligible_exact_dedup`(정확 중복 대표 1건)으로 구성되어 있어
중복 그룹당 한 행만 남았다. 따라서 `GroupKFold(duplicate_group_id)`는 pair-level 무작위 분할과
완전히 동일하며 **LR-01을 실질적으로 만족시키지 못한다.**

LR-01(§23.2)이 요구하는 것은 exact duplicate가 아니라 **near-duplicate / paraphrase cluster**다.
현재 canonical artifact에 그 열이 **없다.**

```
BLOCKER_FOR_G5_SPLIT_FREEZE
```

후보 경로 (제안일 뿐 — 연구 설계 결정이며 이 lane 권한 밖):

1. `ko/en analysis text`의 near-duplicate clustering을 D-01/D-02 lineage에 추가
2. 025의 cross-direction 재사용(50,511 groups)과 TRAIN↔VALID 중복(25,247 pairs)을 group key로 승격
3. source-held-out을 secondary OOD test로 분리

split은 **freeze하지 않았고**, seed도 새로 만들지 않았다
(D-RD-01 `split_seed = 1456095166`을 참조만 했다).

---

## 7. Boundary regions & NB06 target candidates

11개 구역을 정의하고 전수에서 크기·premium 분포를 산출했다 (notebook cell "boundary" 참조).
각 구역은 SQL 조건식으로 명시되어 있어 NB06/NB07이 동일 정의를 재사용할 수 있다.

```
NB06_TARGET_STRATA_CANDIDATE
```

**regex chunking을 실행하지 않았다.** 이 표는 sample-selection aid이며 **D-05 evidence가 아니다.**
morpheme–chunk–token 세 경계의 비교는 NB06 이후에만 가능하다 (§5.1).

---

## 8. G5로 넘기는 것 / 넘기지 않는 것

**넘기는 것 (candidate evidence)**
- §1 identifiability support 구조 + provisional classification
- §1.4 `sentence_type` zero variance + CHANGE_REQUEST_CANDIDATE
- §2 결정론적 종속성 목록 (모형 투입 전 해소 대상)
- §5 cohort 무결성 (차단 요인 없음)
- §6 split blocker

**넘기지 않는 것**
- G5 PASS/FAIL 판정 — 이 lane 권한 밖
- 어떤 QC exclusion, cohort 변경, split freeze
- 어떤 추론적 결론 (p-value / CI / signed-rank 미계산)
