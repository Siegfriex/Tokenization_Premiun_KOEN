# KOEN — PRE-G5 Full-Population Reconnaissance (EDA V2)

```
Status:     NON_CANONICAL / PRE-G5 EXPLORATORY
Class:      FULL_POPULATION_RECONNAISSANCE_V2
Authority:  SUBORDINATE_TO KOEN-TP-RS-001
Final:      PRE_G5_EDA_V2_COMPLETE / G5_NOT_ADJUDICATED / NB06_NOT_EXECUTED
```

| Item | Value |
|---|---|
| Branch | `results/pre-g5-eda-v2-20260817` |
| Base SHA | `28d88ad40d85fa6067c6388fb8fbf8b2b6c5e329` (`docs(ssot): close G2-G4 and enter PRE-G5`) |
| Worktree | `/home/sieg/projects-wsl/Tokenization_KOEN_pre_g5_eda_v2` |
| Notebook | `notebooks/exploratory/EDA_preG5_fullstack_v2.ipynb` |
| `run_id` | `EDA_V2_PRE_G5_20260817T181311` |
| Adjudication basis | `441d5802bfebe178fd220d08b653c60dfad17faf` (Claude-B G2/G3/G4 forensic) |
| V1 freeze compared against | `aabd068a4eef1245420ba4cc0a510ca4e27deae2` |

## 1. The question this branch answers

> V1에서 `N=40` probe로 관측된 multilayer signal 중 **무엇이 full-population D-03/D-04에서
> 유지되고, 무엇이 약화·증폭·반전되며, 어떤 것은 식별불가능한가?**

## 2. Canonical inputs — fail closed

`src/tokenization_premium/lineage.py`의 `assert_canonical_artifact(..., verify_pair_set=True)`로
경로 · SHA-256 · 열수 · row count · distinct id · **정렬 pair-set 해시**를 전부 대조했다.
하나라도 어긋나면 실행이 중단되며, `pilot` / `synthetic` / `REP_FEATURES_v001` / 어떤 fallback도
사용하지 않는다.

| Artifact | Gate | Rows | Cols | SHA-256 (앞 20자) |
|---|---|---:|---:|---|
| `REP_FEATURES_v002` | G2 | 3,835,988 | 49 | `dfae8e01cd3fe2ca949d…` |
| `MORPH_FEATURES_KIWI_v001` | G4 | 3,835,988 | 19 | `0fe5bd74e3993a7141c5…` |
| `TOKEN_O200K_BASE_v001` | G3 | 3,835,988 | 28 | `1c30e3276222dd94885a…` |
| `PAIR_REGISTRY_v002` | G1 | 5,652,925 | 69 | `95f523d11b0e8fcfd761…` |

세 cohort artifact의 pair-set 해시는 모두 `d9660d654ee449e4d0c23a0070225274`로 일치한다.

## 3. Headline results

**표현층 역전은 다수 현상이지 보편이 아니다.** `pair_codepoint_ratio` 중앙값 0.4675(<1),
`pair_byte_ratio` 중앙값 1.1268(>1)이며, 두 조건을 동시에 만족하는 pair는 **71.05%**다.

**Token Premium (full cohort 최초 기술).** `TP` 중앙값 1.3333, `log TP` 중앙값 +0.2877.
`TP > 1` **87.99%** · `TP = 1` 5.13% · `TP < 1` 6.89%.
identity 오차 최대 8.88e-16, roundtrip 실패 0.

**분해 구조.** pair 단위로 계산했을 때 `|logCP| > |logCR + logBDR|`인 pair가 **54.04%**다.
성분 부호 조합의 74.64%가 `(CR−, BDR+, CP+, TP+)`이다.

**V1→V2 브리지 — 실행 편차 0.** V1이 동결한 40 pair를 canonical full artifact에 exact join한
결과, 네 성분 모두 **실행 편차가 정확히 0.0000**이었다. 즉 V1의 40건 재계산은 canonical 전수
측정과 완전히 일치했고, V1↔V2의 모든 차이는 **표본→모집단 확장 효과**다.

**설계 식별가능성.** `source_id ↔ logical_corpus`는 **1:1 대응**(`STRUCTURALLY_CONFOUNDED`)이며,
이는 V1 caveat **C3**이 "검증하지 못했다"고 유보한 지점을 해소한다 — V1의 corpus 교락 관측은
곧 source 교락 관측이었다. `domain × source_id`는 `PARTIALLY_IDENTIFIABLE`이다
(`other` domain만 두 source에 걸쳐 있어 유일한 within-domain source 대비를 제공한다).

**`sentence_type`은 `ZERO_VARIANCE`** — 3,835,988건 전량이 `other` 단일 수준, 엔트로피 0.000000 bits.

## 4. Two blockers surfaced for G5

1. **LR-01 group key 부재.** `duplicate_group_id`는 이 cohort에서 group 수 = 행 수 =
   3,835,988이고 최대 group 크기가 1이다 (cohort가 이미 exact-dedup 후이므로).
   즉 `GroupKFold(duplicate_group_id)`는 pair-level 무작위 분할과 동일하며 LR-01을
   실질적으로 만족시키지 못한다. **near-duplicate cluster key가 canonical artifact에 없다.**
2. **`sentence_type` 모형 항 처리 미결정** — `CHANGE_REQUEST_CANDIDATE`로만 제안했다.

## 5. Claim boundaries — 이 branch가 하지 **않은** 것

| 금지 항목 | 상태 |
|---|---|
| $\operatorname{Median}(\log TP)>0$ 추론적 결론 | 없음 |
| p-value · signed-rank · bootstrap CI · significance | **계산조차 하지 않음** |
| Gate 판정 (G5 포함) | 없음 |
| QC exclusion 생성 | 없음 |
| primary cohort 변경 | 없음 |
| split freeze | 없음 (seed도 신규 생성 없음) |
| regex chunking 실행 | 없음 |
| causal / "domain effect" 서술 | 없음 |
| o200k_base 밖으로의 일반화 | 없음 |
| raw KO/EN text · morpheme text · human workbook 렌더링 | 없음 |
| V1 branch 수정 | 없음 |

## 6. Documents

| File | Role |
|---|---|
| `README.md` | 이 파일 |
| `KOEN_EDA_V2_V1_COMPARISON_MATRIX.md` | V1 axis별 §6 어휘 판정 |
| `KOEN_EDA_V2_PRE_G5_DIAGNOSTICS.md` | 식별가능성 · 공선성 · cohort · split · 경계 구역 |
| `KOEN_EDA_V2_TRACEABILITY.md` | 질문 ↔ SSOT ↔ 입력 ↔ 방법 ↔ 산출 ↔ 주장 경계 |

## 7. Resource discipline

DuckDB `memory_limit=4GB` · `threads=6` · `preserve_insertion_order=false` · spill
`.runtime/eda-v2-spill`. full pandas load 없음. histogram/quantile은 전부 SQL binned aggregate.
scatter/상관은 결정론적 표본 `[V2-SAMPLE200000]` (seed `2995913794`, `ORDER BY md5(pair_id || seed)`).
nested `morpheme_sequence` 및 `ko_token_ids`/`en_token_ids`는 **읽지 않았다**.
프로세스 RSS 0.263 → 2.995 GiB.

## 8. Merge policy

```
NO PR · NO merge to main · V1 branch 불변
```
