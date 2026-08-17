# KOEN EDA V2 — Traceability

```
Notebook : notebooks/exploratory/EDA_preG5_fullstack_v2.ipynb
run_id   : EDA_V2_PRE_G5_20260817T181311
Base SHA : 28d88ad40d85fa6067c6388fb8fbf8b2b6c5e329
Branch   : results/pre-g5-eda-v2-20260817
```

각 산출물을 **질문 ↔ SSOT ↔ 입력 ↔ population/sample ↔ 방법 ↔ 주장 경계 ↔ V1 링크**로 고정한다.
notebook의 모든 주요 cell은 같은 8개 태그(`@cell @question @ssot @input @population_or_sample
@method @output @claim_boundary @v1_link`)를 markdown/JSDoc 헤더에 달고 있다.

---

## 1. Evidence classes

| Class | 의미 | N |
|---|---|---:|
| `[R-FULL]` | full-population Representation (D-02) | 3,835,988 |
| `[M-FULL]` | full-population Morphology (D-03) — **V1에 없던 층** | 3,835,988 |
| `[T-FULL]` | full-population Tokenizer (D-04) — **V1에 없던 층** | 3,835,988 |
| `[DESIGN-FULL]` | full-cohort 설계 축 metadata | 3,835,988 |
| `[V2-SAMPLE200000]` | 결정론적 표본 (scatter/상관 전용) | 200,000 |
| `[V1-FROZEN40]` | V1이 동결한 40 pair (aggregate만 복원 가능) | 40 |
| `[NOT-ESTABLISHED]` | 이 branch가 지지하지 않는 진술 | — |

---

## 2. Traceability matrix

| Claim ID | 질문 | SSOT | 입력 | basis | 방법 | 산출 | 주장 경계 | V1 링크 |
|---|---|---|---|---|---|---|---|---|
| `V2-A01` | artifact 신원이 B 판정 대상과 동일한가 | §30.2; adj `441d580` | 4 parquet | 전수 | `assert_canonical_artifact(verify_pair_set=True)` | `ARTIFACT_IDENTITY` | 신원 검증이지 품질 판정 아님 | V1은 REP만 full |
| `V2-A02` | V1 값 중 row-level 복원 가능한 것은 | Directive §5 | V1 branch objects | `[V1-FROZEN40]` | frozen 출력 정규식 스캔 | `NOT_RECOVERABLE_FROM_FROZEN_OUTPUT` | 재구성 금지 | V1 §4 |
| `V2-A03` | V1↔V2 차이가 실행편차인가 표본확장인가 | Directive §5/§10; §8 | V1 40 pair ⋈ full | 40 / 40 / 3.84M | exact join, 동일 통계량 3열 비교 | `BRIDGE`, `V2-D01` | 40건 중앙값은 모집단 추정치 아님 | AXIS2 |
| `V2-R01` | 표현층 두 비율의 결합 분포 | §8.2, §8.3, §13.3, §13.5 | REP | `[R-FULL]` | 120×120 SQL binned density | REVERSAL share 71.05% | token·인과로 확대 금지 | AXIS1 |
| `V2-T01` | full cohort TP/logTP 분포 | §13.1, §12.4 | TOK | `[T-FULL]` | 정확 분위수 + 부호 share | median logTP +0.2877, TP>1 87.99% | **descriptive only.** p-value/CI/signed-rank 미계산 | AXIS2 |
| `V2-D02` | 성분 부호 조합과 상쇄 구조 | §8, IR-01, §32 T-06 | TOK | `[T-FULL]` | 부호 교차표 + pair 단위 offset | 74.64% `(−,+,+,+)`; \|CP\|>\|CR+BDR\| 54.04% | **중앙값 합 = 중앙값 분해 아님** | AXIS2 |
| `V2-M01` | 형태소 분포와 측정 경계 | §12.3, §13.6, §13.7, §32 T-05 | MORPH | `[M-FULL]` | 전체 / 경계 / 본 구역 3벌 분위수 | `eojeol_count=1` 42,096건 | density 극값 ≠ linguistic complexity | AXIS3 (V1엔 층 없음) |
| `V2-M02` | 형태소 ↔ premium 조건부 관계 | §6.4(검정 아님), §19 | MORPH ⋈ TOK | `[M-FULL]×[T-FULL]` | ntile(20) 구간별 median | 조건부 중앙값 곡선 | **RQ4에 답하지 않음** (통제 없음) | AXIS3 |
| `V2-M03` | 순위 상관 강도 | §32 T-06, §17.3 | 3-way ⋈ | `[V2-SAMPLE200000]` | Spearman ρ (p-value 미계산) | 형태소 \|ρ\|max 0.124 | 표본이며 모집단 상관 아님 | AXIS3 |
| `V2-ID01` | 설계 축 support 구조 | §20.1, §20.2, §32 T-04 | registry ⋈ cohort | `[DESIGN-FULL]` | 5개 교차표 + 함수적 종속 검사 | `IDENT` provisional | **G-ID candidate evidence. formal G5 verdict 아님** | AXIS4 / caveat C3 |
| `V2-ST01` | `sentence_type` 실현 수준 | §9.2, §18 | registry ⋈ cohort | `[DESIGN-FULL]` | GROUP BY + Shannon entropy | 1 level, 0.000000 bits | SSOT 모형 명세 수정 금지 → CR 후보만 | caveat C4 |
| `V2-C01` | 결정론적 vs 경험적 중복 | §21, §32 T-06 | 정의 + 표본 | 정의는 population-invariant | 정의 목록 + Spearman 군집 | `DEPENDENCY`, `EMP_CORR`, `NZV` | VIF/조건수는 candidate. 모형 적합 아님 | — |
| `V2-H01` | 층별 logTP 분포 | §6.6, §20.2 | TOK ⋈ metadata | `[T-FULL]×[DESIGN-FULL]` | 층별 분위수 + 교락 라벨 부착 | `STRATA` | **"domain effect" 용어 금지** | AXIS4 |
| `V2-B01` | short-text 구간의 위치·산포 | §16.3, §13.6 | 3-way ⋈ | 전수 | 어절 수 구간별 분위수 | `LENGTH_BINS` | 산포 확대가 측정불안정인지 이질성인지 구분 못 함 | AXIS5 / caveat C5 |
| `V2-N01` | NB06이 볼 구역 | §12.5 D-05, §6.5 RQ5, §5.1 | BOUNDARY | 전수 | 구역 크기 + Δ 정렬 | `NB06_TARGET_STRATA_CANDIDATE` | **sample-selection aid. D-05 evidence 아님** | AXIS5 |
| `V2-Q01` | cohort가 모형 소비 가능한가 | §23, §31 G5, D-RD-08 | 4-way ⋈ | 전수 | NULL/비유한/정의역 검사 | 차단 요인 0 | primary cohort 변경 금지 | — |
| `V2-S01` | LR-01 group key가 존재하는가 | §23.2 LR-01, §30.3 | registry ⋈ cohort | 전수 | group 수·최대 크기·singleton 비율 | **`BLOCKER_FOR_G5_SPLIT_FREEZE`** | split freeze 안 함, seed 신규 생성 없음 | — |

---

## 3. `[NOT-ESTABLISHED]` register

이 branch가 **지지하지 않는** 진술 — 인용 시 반드시 이 목록을 함께 본다.

| # | 비-주장 |
|---|---|
| N1 | $\operatorname{Median}(\log TP) > 0$ 이라는 추론적 결론 (§17.1 → NB08) |
| N2 | 어떤 통계적 유의성 / 신뢰구간 / p-value — **계산조차 하지 않았다** |
| N3 | 형태소 block의 증분 설명력 (RQ4) — 통제변수 없음 → NB09 |
| N4 | "domain effect" — 대부분 축이 support-confounded |
| N5 | Gate G5 판정 (또는 어떤 Gate 판정) |
| N6 | morpheme / regex chunk / final token 경계 사이의 관계 — D-05 부재 (§5.1) |
| N7 | 인과 진술 (MN-01, §3.2) |
| N8 | o200k_base 밖으로의 일반화 (§32 T-07) |
| N9 | `AMPLIFIED` / `ATTENUATED` 판정이 유의성을 뜻한다는 해석 — 크기 비교일 뿐 |
| N10 | 경계 구역 라벨이 QC exclusion 근거라는 해석 — 라벨링일 뿐 |

---

## 4. Reproduction

```bash
git worktree add <path> results/pre-g5-eda-v2-20260817
# data/registry/*.parquet 는 gitignore 대상 — canonical 위치를 심볼릭 링크로 연결
jupyter nbconvert --to notebook --execute --inplace \
  notebooks/exploratory/EDA_preG5_fullstack_v2.ipynb
```

notebook 첫 cell이 자원 한도를, 두 번째 cell 그룹이 artifact 신원을 fail-closed로 검증한다.
신원이 어긋나면 실행이 그 지점에서 멈추므로, 잘못된 입력으로 산출된 결과가 나올 수 없다.

**결정론성**: 모든 표본은 `ORDER BY md5(pair_id || '2995913794')` — 난수 없음.
동일 artifact + 동일 코드 ⇒ 동일 수치.

## 5. Resource record

| 항목 | 값 |
|---|---|
| DuckDB | `memory_limit=4GB`, `threads=6`, `preserve_insertion_order=false` |
| spill | `.runtime/eda-v2-spill` |
| full pandas load | 없음 |
| nested 열 독출 | 없음 (`morpheme_sequence`, `ko_token_ids`, `en_token_ids`) |
| scatter/상관 표본 | 200,000 (결정론적) |
| histogram/quantile | 전수 SQL binned aggregate |
| 프로세스 RSS | 0.263 → 2.995 GiB |
| multi-process concurrency | 없음 (memory guard defect 미해소 고려) |

## 6. Hygiene

public branch에 raw KO / raw EN / morpheme surface text / human workbook을 **렌더링하지 않았다**.
case 정보는 `pair_id` · 수치 metric · 범주 metadata까지만이다.
