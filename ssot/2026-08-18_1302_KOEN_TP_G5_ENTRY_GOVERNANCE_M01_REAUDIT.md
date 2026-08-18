# KOEN — `M-01` 타겟 재감사

> Audit ID: `AUDIT-G5-ENTRY-GOVERNANCE-02`
>
> Auditor: Claude-B (Research / Statistics Independent Auditor)
>
> Subject: `RD-G5-ENTRY-GOVERNANCE-CLOSEOUT-01` §3.4 시정분
>
> Audited range: `65ce14f2ca616738054e7f0f787e05d563c3fbb3` .. `765f2514892bd729c40716f42160b0fbfa60f487`
>
> Audit worktree: `/home/sieg/projects-wsl/KOEN_reaudit_20260818`
> Audit branch: `audit/g5-governance-reaudit-20260818`
>
> Executed: 2026-08-18 13:02 KST

---

## 0. 감사 계보

```
PRIOR_AUDIT_SHA   = 0b5105c17a301c1b4f4c1f31c4bfbeca1c640839
PRIOR_AUDIT_DOC   = ssot/2026-08-18_1136_KOEN_TP_G5_ENTRY_GOVERNANCE_INDEPENDENT_AUDIT.md
PRIOR_AUDIT_BRANCH= audit/g5-governance-closeout-20260818   (remote 보존, main 병합 금지)
PRIOR_VERDICT     = FAIL_M01

REMEDIATION_SHA   = 765f2514892bd729c40716f42160b0fbfa60f487
REMEDIATION_TITLE = fix(governance): restore primary RQ1 facts in G5 closeout
REMEDIATION_PARENT= 65ce14f2ca616738054e7f0f787e05d563c3fbb3   (EXPECTED 일치)
```

선행 감사는 **취소되지 않으며 정정되지 않는다.** 그 FAIL 판정은 시정 이전 상태에 대한
사실이고, remote에 역사적 증거로 남는다. 본 문서는 별도의 후속 감사다.

---

## 1. Base drift

```
origin/main                          a31a4c27417b93567bb6e261b6225813aaa5f66e   불변
origin/docs/g5-governance-closeout   765f2514892bd729c40716f42160b0fbfa60f487   EXPECTED 일치
origin/audit/g5-governance-closeout  0b5105c17a301c1b4f4c1f31c4bfbeca1c640839   EXPECTED 일치

parent(765f251) = 65ce14f                                                       EXPECTED 일치

chain (선형, merge commit 없음)
  a31a4c2 → f786baa → 65ce14f → 765f251
```

```
TARGETED_REAUDIT_BASE_DRIFT = NONE
```

---

## 2. 시정 범위 감사

```
git diff --name-status 65ce14f 765f251

M   ssot/2026-08-18_1116_KOEN_TP_G5_ENTRY_GOVERNANCE_CLOSEOUT.md

파일 수 = 1   (요구: 정확히 1)
+56 / −7
```

승인 hunk 밖 접촉 없음:

```
ssot_nb01/ 접촉        NONE
tests/ 접촉            NONE
src/ 접촉              NONE
scripts/ · notebooks/  NONE
data/ · outputs/       NONE
```

**절 경계 대조** — 문서 내 `### 3.4 Classification`은 227행, `### 3.5`는 294행에서 시작한다.
`-U0` hunk header 실측:

```
@@ -230,0 +231,3 @@
@@ -233   +236,7 @@
@@ -237,6 +246,29 @@
@@ -244,0 +277,17 @@
```

모든 hunk가 231–293행 구간, 즉 **§3.4 내부에 완전히 포함**된다.

```
REMEDIATION_SCOPE = ONE_DOCUMENT_ONE_SUBSECTION
SCOPE_VERDICT = PASS
```

---

## 3. `M-01` 시정 내용 대조

권위 원본에서 독립 재계산했다. 인용 출처는 `04_NB08_RQ1_RESULTS_v001.json`(sha256
`768a3bcc…`, 본 감사에서 재해시 확인)과 `03_NB08_RQ1_PROTOCOL_v001.md` §1이다.

### 3.1 PRIMARY 블록

| 항목 | 시정된 §3.4 | 권위 실측 | 출처 | 판정 |
|---|---|---|---|---|
| estimand | `theta = Median(log_token_premium)` | `"estimand": "Median(log_token_premium)"` | `04` | **일치** |
| 가설 | `H0: theta = 0` · `H1: theta > 0` (one-sided, greater) | `{"H0":"theta = 0","H1":"theta > 0","alternative":"greater"}` | `04` / `03` §1 | **일치** |
| cohort label | `PRIMARY_FINAL_COHORT` | `primary.cohort = "PRIMARY_FINAL_COHORT"` | `04` | **일치** |
| N | 3,835,988 | `primary.n = 3835988` | `04` · `02` `primary_cohort_n` | **일치** |
| pair-set | `d9660d654ee449e4d0c23a0070225274` | 동일 | `02` (N=3,835,988 manifest) | **일치** |
| median log TP | 0.28768207245178085 | `primary.median_logTP` 동일 | `04` | **일치** |
| Wilcoxon W | 6405551963244.0 | `primary.wilcoxon.statistic` 동일 | `04` | **일치** |
| sign positive | 3,375,095 | `primary.sign_test.positive` 동일 | `04` | **일치** |
| sign negative | 264,175 | `primary.sign_test.negative` 동일 | `04` | **일치** |
| ties | 196,718 | `primary.sign_test.ties` 동일 | `04` | **일치** |
| bootstrap B | 2000 | `bootstrap.B = 2000` | `04` | **일치** |
| bootstrap seed | 969634713 | `bootstrap.seed = 969634713` | `04` | **일치** |
| protocol | `NB08_RQ1_PROTOCOL_v001`, cells modified = 0 | `protocol_id` 동일 · `06` `primary_protocol_cells_modified = 0` | `04` / `06` | **일치** |
| verdict | `RQ1_PRIMARY_INFERENCE_PASS / NB08_RQ1_CLOSED` | `06` `verdict` 동일 | `06` | **일치** |

선행 감사가 지적한 네 오기 — estimand, N, Wilcoxon W, sign + — 가 **전부 primary 값으로
교체**됐다.

### 3.2 KNOWN_DIRECTION_ONLY 블록 — 분리 확인

```
label    KNOWN_DIRECTION_ONLY
role     sensitivity cohort reported beside the primary result
N        3,785,441          = 04 sensitivity_known_direction.n
W        6237534311943.0    = 04 sensitivity_known_direction.wilcoxon.statistic
sign +   3,330,539          = 04 sensitivity_known_direction.sign_test.positive
```

문서 전체 grep 결과, 이 세 값은 **오직 이 블록 안에서만** 등장한다.

```
3,785,441 / 3785441       → 272행 1회 (KNOWN_DIRECTION_ONLY 블록 내부)
6237534311943             → 273행 1회 (동)
3330539 / 3,330,539       → 274행 1회 (동)
```

블록 직후 "These figures are computed on a smaller cohort than the primary one and do not
replace any primary value." 가 명시된다.

```
SENSITIVITY_SEPARATION = PASS
```

### 3.3 CONDITIONAL_NONZERO_SIGN_TEST 블록 — 분리 확인

```
label     CONDITIONAL_NONZERO_SIGN_TEST
estimand  P(Y > 0 | Y != 0)
null      P(Y > 0 | Y != 0) = 0.5
role      polarity robustness among non-zero observations only
```

`06` closeout의 `CONDITIONAL_NONZERO_SIGN_TEST.null` = `"P(Y > 0 | Y != 0) = 0.5"`,
`role` = `"non-zero observation 내부의 polarity robustness"` 와 정합.

문서 전체에서 `P(Y > 0` 은 284·285행 **두 곳뿐**이며 모두 이 블록 내부다. 블록 말미에
명시적 비대체 선언이 있다.

> **It does not replace, restate or stand in for the primary estimand
> `Median(log_token_premium)`.**

`RD-SSOT-CANONICAL-RETURN-01` §5-3(조건부 검정과 median-with-ties 진술의 분리)이
문서 수준에서 이행됐다.

```
CONDITIONAL_ESTIMAND_SEPARATION = PASS
```

### 3.4 pair-set hash 귀속

문서 내 `d9660d654ee449e4d0c23a0070225274` 등장 2회.

| 행 | 위치 | 귀속 | 판정 |
|---|---|---|---|
| 169 | §2.4 D-05 validation 인용 | D-05 전집단(N=3,835,988) | **정당** |
| 251 | §3.4 PRIMARY 블록 | `PRIMARY_FINAL_COHORT` N=3,835,988 | **정당** |

민감도 부분집합에 부착된 사례 **없음**. 추가로 §3.4에 다음 문장이 삽입됐다.

> The pair-set hash above belongs to the primary cohort of N = 3,835,988. It is not
> the identity of any sensitivity subset.

선행 감사가 지적한 "N = 3,785,441과 전체 pair-set 해시를 같은 줄에 병기" 내부모순이 해소됐다.

```
PAIR_SET_ATTACHMENT = PASS
```

### 3.5 header 모순 해소

§3.4 classification fence에 다음이 추가됐다.

```
FACTUAL_LINEAGE_CORRECTION
NO_NEW_PRIMARY_ESTIMAND      ← 신규
NO_RQ1_REOPEN                ← 신규
RQ1_RESULT_BYTES_UNCHANGED = YES   ← 신규
```

문서 header의 `NO_NEW_PRIMARY_ESTIMAND` 선언과 §3.4 본문이 이제 같은 방향을 말한다.
선행 감사 §7.2-2가 지적한 자기모순이 해소됐다.

```
M01_STATUS = RESOLVED
```

---

## 4. 선행 PASS 클래스 — 계보 참조

`65ce14f..765f251`이 `ssot/2026-08-18_1116_..._CLOSEOUT.md` §3.4 외에는 아무것도
건드리지 않았음이 §2에서 확인됐으므로, 선행 감사 `0b5105c`의 다음 PASS 판정을
**재실행 없이 계보로 승계**한다. 근거는 대상 객체가 동일하다는 사실이다.

| 클래스 | 선행 판정 | 승계 근거 |
|---|---|---|
| A — canonical-return exact blob | PASS (`c7fdc7bf`, diff EMPTY) | 해당 파일 미접촉 |
| C — RQ1 lineage 정정 (`06`/`07` 2 sites) | PASS | `ssot_nb01/` 미접촉 |
| D — fail-closed lineage 테스트 3종 | PASS (3/3 주입 시나리오 발화) | `tests/` 미접촉 |
| memory-guard governance ↔ 코드 대응 | PASS | `src/` · §2 미접촉 |
| scope / 위생 | PASS | §2에서 재확인 |

### 4.1 그럼에도 독립 재확인한 항목

계보 승계에 의존하지 않고 이번 재감사에서 직접 재계산했다.

```
ssot_nb01/04_NB08_RQ1_RESULTS_v001.json
  sha256 = 768a3bccc7d5d081e90e6b2e1bf0dbc7230f416fce824698aa6d97f718cfbb59
  EXPECTED 일치 · 변경 없음

tiktoken offline cache
  sha256 = 446a9538cb6c348e3516120d7c08b09f57c36495e2acfffe59a5bf8b0cfb1a2d
  = CHUNK_O200K_BASE_MANIFEST_v001.json encoding_file_sha256 · 배치 전 검증

import root (PYTHONPATH 강제, stale editable install 배제)
  /home/sieg/projects-wsl/KOEN_reaudit_20260818/src/tokenization_premium/__init__.py

pytest -q tests/test_lineage.py       11 passed
ruff check tests/test_lineage.py      All checks passed
pytest -q (full)                      276 passed
ruff check src tests scripts          All checks passed
git status --short                    empty (clean)
```

---

## 5. 판정

```
TARGETED_REAUDIT_STATUS = G5_ENTRY_GOVERNANCE_REAUDIT_PASS

M01_STATUS              = RESOLVED
REMEDIATION_SCOPE       = ONE_DOCUMENT_ONE_SUBSECTION
SCOPE_VIOLATION         = NONE
NEW_DEFECT              = NONE

TESTS          = 276 passed
RUFF           = PASS
WORKTREE_CLEAN = YES
```

시정은 승인된 hunk를 벗어나지 않았고, `M-01`의 네 오기와 두 구조적 모순(header 충돌,
pair-set 오귀속)이 모두 해소됐으며, primary / sensitivity / conditional 세 층이 문서 안에서
명시적으로 분리됐다. 새로운 결함은 발견되지 않았다.

**canonical merge 권고.**

병합 대상은 이 PASS 감사 branch이며, 선행 FAIL 감사 commit `0b5105c`는
**main에 병합하지 않는다** — remote branch로 보존한다.

---

## 6. 감사가 하지 않은 것

```
subject branch 수정        없음
코드 / artifact 수정       없음
ssot_nb01 수정             없음
선행 FAIL 감사 문서 정정   없음 (별도 문서로 후속)
KOEN_g5 scratch 접근       없음
canonical worktree 변경    없음
```

---

**재감사 종료**: 2026-08-18 13:02 KST, Claude-B.
