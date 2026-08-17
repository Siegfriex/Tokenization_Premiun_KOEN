# KOEN EDA V2 — PRE-G5 Reconnaissance Checkpoint

```
NON_CANONICAL
PRE-G5 EXPLORATORY
NOT GATE EVIDENCE

PRE_G5_EDA_V2_COMPLETE
G5_NOT_ADJUDICATED
NB06_NOT_EXECUTED
```

이 문서는 **checkpoint 전용**이다. 새 계산 · 새 그림 · 새 해석을 담지 않는다.
아래 caveat은 `adf1eaf`의 산출물을 **재계산 없이** 읽는 방법을 한정한다.

## 1. Checkpoint identity

| Item | Value |
|---|---|
| Branch | `results/pre-g5-eda-v2-20260817` |
| Base SHA | `28d88ad40d85fa6067c6388fb8fbf8b2b6c5e329` |
| Reconnaissance commit | `adf1eafab9110172cb63312db9636256478bdc6d` |
| Notebook | `notebooks/exploratory/EDA_preG5_fullstack_v2.ipynb` |
| `run_id` | `EDA_V2_PRE_G5_20260817T181311` |
| V1 freeze (unchanged) | `aabd068a4eef1245420ba4cc0a510ca4e27deae2` |
| Adjudication basis | `441d5802bfebe178fd220d08b653c60dfad17faf` (G2/G3/G4) |
| Canonical cohort | N = 3,835,988 · pair-set `d9660d654ee449e4d0c23a0070225274` |

---

## 2. Known method caveats

### CAVEAT-01 — same-40 비교는 집계 수준이다

V1의 same-40 **row-level 값은 persist되지 않았다**
(`V1_ROWLEVEL_STATUS = NOT_RECOVERABLE_FROM_FROZEN_OUTPUT`; frozen notebook 출력에
per-pair 40행 metric 표가 없다).

따라서:

- **per-row 실행 동일성(exact per-row execution equality)은 검증 대상이 아니었고, 검증되지 않았다.**
- 지지되는 진술은 여기까지다:
  > **same-40 집계 중앙값이 기록된 정밀도(소수 4자리)에서 frozen V1 값과 일치한다.**

`README.md` §3과 `KOEN_EDA_V2_V1_COMPARISON_MATRIX.md` §2의 "Δ 실행편차 0"은
**집계 수준의 진술**로 읽어야 하며, 40건 각각의 값이 같았다는 뜻이 **아니다**.
두 문서는 이 checkpoint에서 그 범위를 명시하도록 문구를 교정했다(수치 재계산 없음).

### CAVEAT-02 — 설계 축 중복성의 현재 지위

- `source_id ↔ logical_corpus`는 **구조적으로 중복(structurally redundant)**이다 —
  2×2 교차표에서 1:1 대응이며 동시 투입 시 완전 공선이다.
- `domain ↔ source`는 **support가 고르지 않다**(`other`만 두 source에 걸쳐 있고 나머지
  세 domain은 단일 source 전용).

그러나:

> **formal reduced-model rank / Gate G-ID 판정은 여전히 pending이다.**

이 branch가 산출한 것은 support 구조와 provisional classification까지이며,
축소모형의 rank 계산이나 G-ID의 형식적 판정은 수행하지 않았다.

### CAVEAT-03 — 분해 성분은 기술자이지 추론 대상이 아니다

`logCR` · `logBDR` · `logCP`는 §8 exact decomposition의 **descriptor**다.

> **NB08의 primary inference는 `logTP`에 적용되며, 각 성분에 자동으로 적용되지 않는다.**

따라서 `AMPLIFIED` / `ATTENUATED` 판정은 성분별 **기술 통계량의 크기 비교**일 뿐이며,
성분 수준의 추론적 결론이나 유의성 진술로 승격될 수 없다.

---

## 3. Boundaries reaffirmed

| 항목 | 상태 |
|---|---|
| 추론 · p-value · CI · signed-rank | **계산되지 않음** |
| Gate 판정 (G5 포함) | 없음 |
| QC exclusion | 없음 |
| primary cohort 변경 | 없음 |
| split freeze | 없음 (`BLOCKER_FOR_G5_SPLIT_FREEZE` 기록됨) |
| regex chunking (D-05) | 미실행 |
| main merge / PR | 없음 |
| V1 branch | 불변 (`aabd068`) |
| canonical NB03–NB05 · SSOT · `src` · `data/registry` | 미변경 |

## 4. Outstanding for G5

1. **LR-01 group key 부재** — `duplicate_group_id`가 post-dedup cohort에서 100% singleton이라
   grouping을 제공하지 못한다. near-duplicate cluster key가 canonical artifact에 없다.
2. **`sentence_type` 모형 항 처리 미결정** — `ZERO_VARIANCE`,
   `CHANGE_REQUEST_CANDIDATE`로만 제안됨.
3. **`source_id` / `logical_corpus` 중복 해소 방식 미결정** — composite / restriction /
   축 선택 중 무엇인지는 연구 설계 결정이다.
4. **formal reduced-model rank 및 G-ID 판정** — CAVEAT-02 참조.

---

```
EDA_V2_CHECKPOINT_PERSISTED
```
