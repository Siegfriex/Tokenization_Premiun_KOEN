# KOEN EDA V2 — V1 → V2 Comparison Matrix

```
V1 freeze : aabd068a4eef1245420ba4cc0a510ca4e27deae2  (results/preliminary-eda-v1-20260817)
V2 base   : 28d88ad40d85fa6067c6388fb8fbf8b2b6c5e329  (results/pre-g5-eda-v2-20260817)
V2 run_id : EDA_V2_PRE_G5_20260817T181311
```

V1 값은 **branch에서 직접 파싱**했다 (`git show <V1>:docs/results/preliminary_v1/…`).
기억으로 재작성한 값은 하나도 없다.

## 0. 판정 어휘 (§6) — "confirmed"는 사용하지 않는다

| 판정 | 의미 |
|---|---|
| `UNCHANGED_BY_CONSTRUCTION` | V1이 이미 같은 artifact를 썼으므로 동어반복 |
| `PRESERVED_DIRECTION` | 부호·방향 유지 |
| `AMPLIFIED` / `ATTENUATED` | 크기 증가 / 감소 |
| `REVERSED` | 부호 반전 |
| `STRUCTURALLY_NOT_IDENTIFIABLE` | support 구조상 분리 불가 |
| `NOT_TESTABLE_YET` | 이 notebook의 권한/데이터 밖 |

---

## 1. V1 row-level 복원 판정

```
V1_ROWLEVEL_STATUS = NOT_RECOVERABLE_FROM_FROZEN_OUTPUT
```

frozen notebook 출력에 per-pair 40행 metric 표가 **없다** (기계적으로 확인: `[40 rows x` 부재).
출력된 것은 domain 단위 중앙값 표뿐이다. 따라서 V1과의 비교는 **aggregate-level(전체·domain
중앙값)로만** 수행했고, row-level 값을 재구성하지 않았다.

## 2. 복제 브리지 — 실행 편차와 표본 확장의 분리

같은 40 `pair_id`(집합 해시 `5b4393fb541c3a6dc347fa2422ed25fbfb384eed45a4b98b652ed3f85c8e0ac1`)를
canonical full artifact에 exact join(40/40 매칭)한 결과:

| 성분 | V1 frozen 40 | same-40 full artifact | full cohort N=3,835,988 | Δ 실행편차 | Δ 표본확장 |
|---|---:|---:|---:|---:|---:|
| `log TP` | +0.2007 | +0.2007 | **+0.2877** | **0.0000** | +0.0870 |
| `log CR` | −0.8113 | −0.8113 | **−0.7605** | **0.0000** | +0.0509 |
| `log BDR` | +0.9004 | +0.9004 | **+0.8961** | **0.0000** | −0.0043 |
| `log CP` | +0.1360 | +0.1360 | **+0.1752** | **0.0000** | +0.0392 |

**해석.** 실행 편차가 네 성분 모두 정확히 0이다. V1의 40건 재계산(canonical
`pair_token_measurement()` 호출)이 full-population 측정과 **완전히 동일한 값**을 냈다는 뜻이다.
따라서 V1↔V2의 모든 차이는 execution drift가 아니라 **sampling expansion**이다.

이는 V1의 `SAMPLE_RECOMPUTED_FOR_VISUALIZATION` 표기가 정확했음을 사후적으로 확인해 준다 —
V1은 "이 값은 canonical과 같은지 모른다"고 유보했고, 실제로는 같았다.

---

## 3. Comparison matrix

| V1 axis | V1 evidence class | V1 value / signal | same-40 full artifact | full-pop result | **V2 verdict** | interpretation | remaining dependency |
|---|---|---|---|---|---|---|---|
| **AXIS1** Representation reversal | `[R-FULL]` | code point 비 median 0.4675 < 1, byte 비 median 1.1268 > 1 | n/a (표현층은 V1이 이미 전수) | REVERSAL share = **71.05%** | **`UNCHANGED_BY_CONSTRUCTION`** | V1이 이미 동일 `REP_FEATURES_v002`(sha 일치)를 썼다. 같은 값은 재확인이 아니라 동어반복이다. V2가 새로 더한 것은 "역전이 보편이 아니라 다수 현상"이라는 share 수치다. | 없음 — 표현층은 G2 PASS로 닫혀 있다 |
| **AXIS2** · `log CP` | `[T-SAMPLE40]` | median +0.1360 | +0.1360 (편차 0) | **+0.1752** (확장 +0.0392) | **`AMPLIFIED`** | 실행 편차 0. V1↔V2 차이는 전부 표본 확장 효과. 크기 비교이지 유의성이 아니다. | NB08 §17.1 primary inference |
| **AXIS2** · `log TP` | `[T-SAMPLE40]` | median +0.2007 | +0.2007 (편차 0) | **+0.2877** (확장 +0.0870) | **`AMPLIFIED`** | 동일 | NB08 §17.1 |
| **AXIS2** · `log CR` | `[T-SAMPLE40]` | median −0.8113 | −0.8113 (편차 0) | **−0.7605** (확장 +0.0509) | **`ATTENUATED`** | 부호 유지, 크기 감소 | NB08 §17.1 |
| **AXIS2** · `log BDR` | `[T-SAMPLE40]` | median +0.9004 | +0.9004 (편차 0) | **+0.8961** (확장 −0.0043) | **`ATTENUATED`** | 사실상 불변 (−0.0043) | NB08 §17.1 |
| **AXIS3** Morphology 관계 | `[M-SAMPLE40]` | raw \|ρ\| ≤ 0.192 (n=40, 통제 없음) | n/a (row-level 미복원) | `[V2-SAMPLE200,000]` logTP 대비 형태소 \|ρ\|max = **0.124**; 모집단 조건부 중앙값은 V2-M02 | **`NOT_TESTABLE_YET`** | V1도 V2도 통제변수 없는 raw 관계만 계산했다. RQ4는 M1 대비 M2의 증분 설명력이며 회귀 비교에서만 답할 수 있다. **표본을 5,000배 키워도 질문이 바뀌지 않는다.** | NB09 §19.1–19.2 M1 vs M2 |
| **AXIS4** Heterogeneity / Identifiability | `[DESIGN-FULL]` | domain × logical_corpus 교락 관측. **source_id는 미검증(caveat C3)** | n/a | `source_id × logical_corpus` = `STRUCTURALLY_CONFOUNDED` (1:1); `domain × source_id` = `PARTIALLY_IDENTIFIABLE`; `sentence_type` = `ZERO_VARIANCE` | **`STRUCTURALLY_NOT_IDENTIFIABLE`** | V1이 유보했던 지점이 해소된다: 두 축이 같은 분할이므로 V1의 corpus 교락 관측은 곧 source 교락 관측이었다. V1은 이를 알 수 없었고 알 수 없다고 정직하게 기록했다. | Gate G-ID formal verdict (§20.2) — 이 lane 권한 밖 |
| **AXIS5** Boundary regions | `[R-FULL]` | 표현층만으로 제안된 구역 (짧은 pair, 혼합 스크립트, script switch 등) | n/a | 11개 구역에 morphology/token 층 부착; `eojeol_count = 1` = **42,096건** (1.0974%) | **`PRESERVED_DIRECTION`** | V1이 표현층만으로 지목한 구역이 morphology/token 층에서도 측정량이 다른 구역으로 재확인된다. 새로 추가된 것은 어절 1개 측정 경계 구역이다. | NB06 D-05 regex chunk 층 |

**사용된 판정 집합**: `AMPLIFIED`, `ATTENUATED`, `NOT_TESTABLE_YET`, `PRESERVED_DIRECTION`,
`STRUCTURALLY_NOT_IDENTIFIABLE`, `UNCHANGED_BY_CONSTRUCTION`.
`confirmed`는 한 번도 사용하지 않았다.

---

## 4. V1 caveat 별 사후 상태

| V1 caveat | 내용 | V2 결과 |
|---|---|---|
| **C1** | o200k layer는 n=40 probe, population inference 아님 | 유효했다. V2가 처음으로 모집단 share를 제공한다 (`TP>1` 87.99%). |
| **C2** | morphology layer는 full D-03 artifact가 아님 | 유효했다. V2는 `[M-FULL]`을 쓴다. V1의 pilot 미소비 기록도 정확했다. |
| **C3** | domain patterns가 source/corpus/direction과 교락 가능; **`logical_corpus ≠ source_id`이며 V1은 `source_id`를 검증하지 않았다** | **해소.** 두 축은 1:1 대응이므로 V1의 관측은 source 교락 관측과 동일한 사실이었다. |
| **C4** | `sentence_type`이 degenerate일 가능성 | **확정.** 3,835,988건 전량 단일 수준, 엔트로피 0.000000 bits. |
| **C5** | 짧은 조각에서 형태소 값 불안정 — 극단값을 언어 복잡도로 자동 해석 금지 | 유효했다. `eojeol_count = 1` 구역 42,096건을 별도 라벨(`MEASUREMENT_BOUNDARY_REGION`)로 분리했다. |
| **C6** | V1 pattern이 full에서 유지되는지는 V2에서 검증 | 본 문서 §3이 그 검증이다. `log CP`는 `AMPLIFIED`, `log CR`은 `ATTENUATED`. |
| **C7** | V1 figure ID는 canonical SSOT F01–F09와 다름 | 유효. V2도 `V2-` 접두 자체 ID를 쓰며 canonical 도판 번호를 주장하지 않는다. |

## 5. 이 표가 말하지 않는 것

- 어떤 판정도 **통계적 유의성**을 뜻하지 않는다. 전부 기술 통계량의 크기·부호 비교다.
- `AMPLIFIED`는 "모집단에서 더 크다"이지 "유의하게 크다"가 아니다.
- $\operatorname{Median}(\log TP) > 0$ 이라는 **추론적 결론은 이 branch에 없다** (§17.1 → NB08).
