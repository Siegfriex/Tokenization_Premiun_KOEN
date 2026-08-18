# NB08 RQ1 — Canonical Closeout

> **Closeout ID**: `NB08_RQ1_SSOT_CLOSEOUT_v001`
> **Authority**: `KOEN-TP-RS-001` · `RD-SSOT-CANONICAL-RETURN-01`
> **Decision**: `RD-RQ1-FIRST-RESULT-01` · **Protocol**: `NB08_RQ1_PROTOCOL_v001`
> **성격**: canonical NB08의 *method closeout*. primary protocol은 변경되지 않았다.

---

## 1. Evidence of record — 변경되지 않은 것

RQ1의 primary result는 아래 commit에서 이미 확정되었으며, 이 closeout은 그 수치를 하나도
바꾸지 않는다. 닫은 것은 결과가 아니라 **방법의 기술(記述)** 이다.

```
primary result commit   502bc128f6b5855f1648802cc990b715808f26f3
primary result JSON     ssot_nb01/04_NB08_RQ1_RESULTS_v001.json
                        sha256 768a3bccc7d5d081e90e6b2e1bf0dbc7230f416fce824698aa6d97f718cfbb59
decision commit         e72274086a7e9c611c9014e6b5612df0e69dae30
cohort commit           9b695307c0551be84d4d6c374646bfe001b7b3a9
protocol commit         86521fdf04839d2e3e8e5db8e15a08ea067871e3
D-04 artifact           sha256 1c30e3276222dd94885ae4f79fc6ab5c45e4e26226de0afd91fc6b1f7d2c16e7
pair-set hash           d9660d654ee449e4d0c23a0070225274
```

`no_primary_protocol_change = true` ·
protocol cell 수정 = **0**

notebook 말미의 `POST-PROTOCOL SSOT CLOSEOUT` 섹션 첫 cell(C0)은 evidence-of-record 고정값
15항목을 살아 있는 변수와 대조하는 HARD STOP guard다. 하나라도 어긋나면 closeout은 계산을
시작하지 않는다. 이번 실행에서 15/15가 일치했다.

## 2. `CONDITIONAL_NONZERO_SIGN_TEST` — 재분류

first release가 "sign test"로 보고한 검정은 `logTP = 0`인 pair를 denominator에서 제외했다.
표준적인 zero-exclusion 관례이지만, 그 결과 검정이 추론하는 모수가 주변확률이 아니라
조건부 확률이 된다.

```
estimand   P(Y > 0 | Y != 0)
null       P(Y > 0 | Y != 0) = 0.5
alternative greater
```

| cohort | positive | negative | ties (제외) | n_effective | 추정치 |
|---|---:|---:|---:|---:|---:|
| PRIMARY | 3,375,095 | 264,175 | 196,718 | 3,639,270 | 0.927410 |
| KNOWN_DIRECTION | 3,330,539 | 260,818 | 194,084 | 3,591,357 | 0.927376 |

이 cohort에서 tie는 196,718건, 전체의
5.13%로 무시할 수 있는 규모가 아니다. 조건부 모수와
주변 모수가 실질적으로 갈라질 만큼의 질량이므로, 명칭을 정확히 하는 일은 형식적 손질이 아니라
추론 대상의 정정이다.

검정 자체는 삭제하지 않는다. 그것은 **non-zero observation 내부의 polarity robustness** 로서 유효하다. 다만
**tie가 존재하는 population median에 대한 distribution-free exact statement** 로 부르지 않는다. 수치는 first release와 동일하며, 변하는 것은 그 수치가
무엇에 대한 진술인지에 대한 기술이다.

## 3. `TIE_AWARE_MEDIAN_SIGN_ROBUSTNESS` — 추가

조건부 검정만으로는 `Median(logTP) > 0`이라는 **주변** 명제를 직접 지지할 수 없다.
`Median(Y) = 0`이면 `P(Y > 0) <= 1/2`이며, tie가 질량의 일부를 가져가므로 등호가 아니라
부등호가 된다. 따라서 귀무가설은 합성가설이고, 검정은 least-favourable null인
`Binomial(N, 0.5)`의 upper tail로 수행한다. **ties를 denominator에서 버리지 않는다.**

| cohort | K (positive) | N (denominator) | ties 유지 | P(Y>0) | 1/2 초과폭 | z |
|---|---:|---:|---:|---:|---:|---:|
| PRIMARY | 3,375,095 | 3,835,988 | 196,718 | 0.879850 | 0.379850 | 1,487.9 |
| KNOWN_DIRECTION | 3,330,539 | 3,785,441 | 194,084 | 0.879829 | 0.379829 | 1,478.0 |

이 검정은 조건부 검정보다 반드시 약한 증거를 준다. 조건부 추정치
0.927410가 보수적 추정치
0.879850로 내려간다. 그럼에도 방향은 두 cohort
모두에서 유지된다 — **tie 전량을 대립가설에 불리한 쪽에 세워도 결론이 바뀌지 않으므로,
zero-exclusion은 결론의 원인이 아니라 관례에 불과했다.**

## 4. `SOURCE_STRATIFIED_BOOTSTRAP_SENSITIVITY` — SSOT §17.2

SSOT §17.2는 *source 불균형이 큰 경우 source-stratified bootstrap을 기본으로 사용하고,
source cluster bootstrap은 source level 수가 충분할 때 보조로 수행한다*고 규정한다.

```
design   source composition 고정, 각 stratum 내부에서 stratum 크기만큼 복원추출 후 concatenate
statistic overall median(log_token_premium)
B         2000
seed      2856958648
          = uint32( first_8_hex( SHA256("NB08_RQ1_SSOT_CLOSEOUT_v001|SOURCE_STRATIFIED") ) )
          SHA256 aa49bab84f2aa5899c72777b35360d16e4cc0d5c0e508e5fcfac2af4367f0089
불균형     1.841 : 1   ·   source level 수 2
```

seed는 결과를 보기 전에 결정론적으로 도출했으며, notebook이 실행 시 재도출로 자기검증한다.

### 4.1 층별 프로필 (기술통계 — 인과·domain 해석 금지)

| source | n | median logTP | median TP | P(TP>1) | tie 비율 |
|---|---:|---:|---:|---:|---:|
| `025` | 2,485,963 (64.8%) | 0.2744368 | 1.315789 | 83.36% | 7.34% |
| `026` | 1,350,025 (35.2%) | 0.3087355 | 1.361702 | 96.50% | 1.06% |

두 층의 median과 `P(TP>1)`은 뚜렷이 다르며, pooled median
`0.2876821`은 **두 층 어느 쪽의 median과도 일치하지 않는다.** 층 간 이질성이
이 정도라면 재표집에서 층 비율이 흔들릴 때 pooled median도 함께 흔들릴 수 있고, 이것이
§17.2가 stratified를 기본으로 두라고 한 이유다.

### 4.2 행 정합 guard

층 라벨과 결과값을 서로 다른 질의로 읽으면 DuckDB가 행 순서를 보장하지 않아(병렬 스캔 +
`preserve_insertion_order=false`) 라벨이 값과 어긋나고, stratum이 사실상 무작위 분할이 된다.
**이 결함은 이번 closeout 작업 중 실제로 한 번 발생했고 검출·수정되었다.** 증상은 두 층의
통계가 pooled 값을 그대로 복제하는 것이었다.

수정 후에는 `y`와 `logical_corpus`를 단일 질의에서 `ORDER BY t.pair_id`로
함께 읽고, 아래 guard를 통과해야만 bootstrap이 실행된다.

```
loaded_in_single_query          True
explicit_order_by               t.pair_id
same_size                       True
same_multiset                   True
pooled_median_matches_protocol  True
```

### 4.3 결과

```
stratified 95% CI   [0.28768207245178085, 0.28768207245178085]
primary    95% CI   [0.28768207245178085, 0.28768207245178085]
두 CI 동일           True
결론 반전            False
replicate sd        5.553e-17
runtime             102.7s
```

**source cluster bootstrap**: `NOT_PERFORMED — source level 수 2로 §17.2의 '충분할 때' 조건 미달` — 생략이 아니라 §17.2의 조건
불충족에 따른 배제로 기록한다.

first release의 pair-level bootstrap은 그대로 유지되며 이 sensitivity가 그것을 대체하지 않는다.

## 5. 보고 규약 — p-value

```
raw underflow 보존       True
논문/대외 보고 형식       p < 1e-300
정규근사 로그값 라벨      APPROX_LOG10_P_NORMAL_DIAGNOSTIC
금지                     exact log p처럼 표현하는 것
```

`log10(p)`는 검정통계량의 정규근사 `z`에서 `log10 Φ̄(z)`를 계산한 값이다. 두 겹의 근사가
개입한다 — 검정통계량 표집분포의 정규근사, 그리고 그 근사가 |z| ~ 1.5e3 극단 tail에서 유효하다는 가정 (유한 표본으로 검증 불가). 후자는 어떤 유한
표본으로도 검증할 수 없다. 관측 가능한 사건이 그 영역에 존재하지 않기 때문이다.

따라서 이 수치는 "p가 10의 마이너스 몇십만 승"이라는 측정이 아니라, 검정통계량이 귀무분포
중심에서 얼마나 떨어져 있는지를 로그 척도로 옮긴 **진단 지표**다. 실질 정보는 지수의 자릿수가
아니라 `z` 그 자체에 있다.

| 검정 | z |
|---|---:|
| `conditional_nonzero_sign_primary` | 1,630.7 |
| `tie_aware_known` | 1,478.0 |
| `tie_aware_primary` | 1,487.9 |
| `wilcoxon_known` | 1,533.6 |
| `wilcoxon_primary` | 1,544.1 |

`§17.3 — p-value 단독 보고 금지 / effect size + CI 우선 / 대표본에서는 premium 크기 해석`

## 6. CI degeneracy 서술의 교정

기존 문구는 대안 방법이 non-degenerate CI를 **보장한다**는 함의를 남겼다. 그 보장은 성립하지
않는다. 교정된 문구는 다음과 같다.

> Alternative lattice-aware or dependence-aware intervals may provide a different uncertainty characterization, but may still collapse at the same point mass.

이는 추측이 아니라 계산으로 확인했다.

```
order-statistic 95% CI   순위 1,916,074 .. 1,919,915
                         [0.28768207245178085, 0.28768207245178085]
                         퇴화 = True
median point mass        123,040행, 순위 1,841,885 .. 1,964,924
두 끝점이 point mass 내부  True
source-stratified CI 퇴화 True
```

bootstrap과 무관한 exact 절차, 그리고 설계가 전혀 다른 stratified bootstrap이 같은 결론에
도달한다. **degeneracy는 방법의 산물이 아니라 자료가 격자 위에 놓여 있다는 사실의 성질이다.**
관측된 primary degenerate CI 자체는 수정하지 않는다. 그것이 자료에 충실한 답이다.

## 7. 해석 (SSOT §17.3)

§17.3은 표본이 매우 클 때 *"statistically significant"보다 실제 premium 크기를 해석*할 것을
요구한다.

**효과의 크기.** 중앙 pair는 Korean 4 / 3 token 비율, 곧
33.3%의 추가 token을 요구한다. 통계적 미세 편차가 아니라
실무적으로 즉시 체감되는 크기다. median TP가 작은 정수비에 정확히 놓인 것은 우연이 아니라
격자 구조의 직접적 귀결이며, 중앙 pair를 기술하는 가장 정직한 방식은 소수점 이하 여러 자리의
실수가 아니라 그 비율 자체다.

**분포적 크기.** `P(TP > 1) = 87.99%`는 premium이 중앙값에만 국한된 현상이
아님을 말한다. 대다수 pair가 같은 방향을 가리키므로 소수의 극단값이 중앙값을 끌어올린 결과가
아니며, tie를 전량 반대편에 세운 보수적 검정에서도 방향이 유지된다는 사실(§3)이 이를 다시
확인한다.

**층 간 이질성.** 가장 해석에 주의가 필요한 부분이다. 두 source의 기술통계는 뚜렷이 다르고
pooled median은 어느 층과도 일치하지 않는다. 이는 "한국어의 token premium이 얼마인가"라는
질문에 단일한 답이 없을 수 있음을 시사한다. 다만 이 관찰로부터 **source가 원인이라거나 domain
효과가 있다고 말해서는 안 된다.** 이 cohort에서 source와 domain은 분리 식별되지 않으며(SSOT
§20.2), 그 판정은 G5의 identifiability 작업에 속한다. 여기서 말할 수 있는 것은 층별
기술통계가 다르다는 사실뿐이다. 그럼에도 결론 자체는 층 구성을 고정한 stratified 재표집에서도
동일했다.

**유의성에 대하여.** 세 검정 모두 exact p가 underflow한다. `N = 3,835,988`에서 이는 놀라운
일이 아니며 정보량도 크지 않다. 결론을 지지하는 것은 지수의 자릿수가 아니라, 효과 크기가
33.3%이고 CI가 그 값에 고정되며 보수적 검정과 층 고정 재표집
모두에서 결론이 유지된다는 사실의 결합이다.

## 8. 판정

```
OK   D04 identity unchanged
OK   prespecified signed-rank direction positive
OK   primary median > 0
OK   source-stratified does not materially reverse
OK   tie-aware sign robustness same direction
```

CI가 동일 lattice value로 degenerate하는 것은 FAIL 조건이 아니다.

```
RQ1_PRIMARY_INFERENCE_PASS / NB08_RQ1_CLOSED
```

## 9. 최종 claim

허용되는 가장 강한 문장:

> Under the fixed o200k_base raw-text Track A configuration and the defined final paired KO-EN cohort, the pair-level median log tokenization premium was positive.

이 문장은 반드시 effect magnitude와 CI caveat를 동반해 보고한다. 중앙 pair의 premium은
33.3%(= 4 / 3)이며, 95% CI는 관측된
자료에서 동일 lattice 값으로 퇴화한다 — 정밀도가 아니라 결과변수가 정수비 격자 위에 놓여
있다는 사실의 표현이다.

**금지되는 진술**: causal · all-tokenizer generalization · morphology cause · domain cause · AI ability · fixed provider cost claim

## 10. NB11로 이관

- B >= 5000 bootstrap (CR-RQ1-BOOTSTRAP-FAST-2000-01은 first release 한정)
- source cluster bootstrap (§17.2 level 수 조건 미달)
- §17.2의 나머지 CI 대상: geometric mean TP, P(TP>1), median absolute token difference
- 층 간 이질성의 원인 규명 (G5 identifiability 선행 필요)

---

**Closeout 종료**: 2026-08-17T21:16:38+09:00, Claude-B (RQ1 Primary Inference Steward)
**다음 canonical stage**: NB06
