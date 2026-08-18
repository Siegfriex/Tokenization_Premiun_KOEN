# KOEN — G5 Entry Governance Closeout · 독립 감사

> Audit ID: `AUDIT-G5-ENTRY-GOVERNANCE-01`
>
> Auditor: Claude-B (Research / Statistics Auditor)
>
> Subject: `RD-G5-ENTRY-GOVERNANCE-CLOSEOUT-01` — Claude-A 집행분
>
> Audited range: `a31a4c27417b93567bb6e261b6225813aaa5f66e` .. `65ce14f2ca616738054e7f0f787e05d563c3fbb3`
>
> Audit worktree: `/home/sieg/projects-wsl/KOEN_audit_gov_20260818`
> Audit branch: `audit/g5-governance-closeout-20260818`
>
> Executed: 2026-08-18 11:36 KST
>
> Authority: `KOEN-TP-RS-001` · `RD-FAST-G5-01` · `CR-FAST-G5-REALIZED-MODEL-01` ·
> `CR-FAST-G5-SPLIT-RELOCATION-01` · `RD-SSOT-CANONICAL-RETURN-01`

---

## 0. 감사 원칙

Claude-A의 자체 보고(`276 passed`, `ruff check PASS`, blob 동일성, hash 정정)는 **입력으로만
취급하고 근거로 채택하지 않았다.** 모든 수치는 격리된 audit worktree에서 재계산했다.

이 감사는 다음 한 가지만 묻는다.

> canonical history에 병합될 문서들이 **자기 자신에 대해 참을 말하는가.**

측정, estimand, cohort, 결과는 이 감사의 대상이 아니며 감사 과정에서 변경하지 않았다.

```
CODE_MODIFIED_BY_AUDIT      = NONE
ARTIFACT_MODIFIED_BY_AUDIT  = NONE
SUBJECT_BRANCH_MODIFIED     = NONE
```

---

## 1. Base / ancestry 검증

```
origin/main                          a31a4c27417b93567bb6e261b6225813aaa5f66e   EXPECTED 일치
origin/docs/g5-governance-closeout   65ce14f2ca616738054e7f0f787e05d563c3fbb3   EXPECTED 일치

chain (선형, merge commit 없음)
  a31a4c2  merge: close Phase-4 regex chunk measurement
    └─ f786baa  docs(ssot): canonicalize return decision and approve G5 entry governance
         └─ 65ce14f  fix(lineage): correct frozen RQ1 result hash reference

git merge-base --is-ancestor a31a4c2 f786baa   → 0
git merge-base --is-ancestor f786baa 65ce14f   → 0
git merge-base --is-ancestor a31a4c2 65ce14f   → 0

f786baa parents = a31a4c2  (단일)
65ce14f parents = f786baa  (단일)
```

```
BASE_DRIFT = NONE
```

---

## 2. Scope 감사 — `a31a4c2..65ce14f` 전량

| 파일 | 변경 | 클래스 |
|---|---|---|
| `ssot/2026-08-17_2042_KOEN_TP_SSOT_CANONICAL_RETURN_DECISION_LOG.md` | A · +613 | **A** canonical-return 실체화 |
| `ssot/2026-08-18_1116_KOEN_TP_G5_ENTRY_GOVERNANCE_CLOSEOUT.md` | A · +312 | **B** 신규 결정문서 |
| `ssot_nb01/06_NB08_RQ1_SSOT_CLOSEOUT_v001.json` | M · 1 line | **C** 사실 정정 |
| `ssot_nb01/07_NB08_RQ1_CANONICAL_CLOSEOUT.md` | M · 1 line | **C** 사실 정정 |
| `tests/test_lineage.py` | M · +43 | **D** lineage 회귀 테스트 |

총 5 files · +970 / −2.

금지 클래스 스캔:

```
research data 변경        NONE
D02/D03/D04/D05 변경      NONE
RQ1 result(04) 변경       NONE
notebook science 변경     NONE
model code 변경           NONE
data/ · .runtime/ 접촉    NONE
parquet/xlsx/csv 등       NONE
raw KO/EN · pair_id 노출  NONE  (신규 문서 2건 스캔 0건)
```

```
SCOPE_VERDICT = PASS
UNEXPECTED_SCIENCE_SCOPE_FILE = NONE
```

---

## 3. Class A — canonical-return blob 감사

```
path   ssot/2026-08-17_2042_KOEN_TP_SSOT_CANONICAL_RETURN_DECISION_LOG.md

blob @ e927012 (원본)   c7fdc7bf10b7f4c0b4d5d5a65da87f0192519232
blob @ 65ce14f (실체화) c7fdc7bf10b7f4c0b4d5d5a65da87f0192519232
EXPECTED                c7fdc7bf10b7f4c0b4d5d5a65da87f0192519232

git diff e927012 65ce14f -- <path>      → EMPTY
sha256 (양쪽 동일)  7c5a4949c421bb718f9d2a4f413d9d20d3564cf98daa098e5bb2473c00ee2bdd
lines               613
```

git object id가 동일하므로 재작성·재번호·재날짜 가능성은 **구조적으로 배제**된다.
Director 21개 절과 하단 `Verification notes — Claude-A` 블록 모두 byte-identical.

```
CLASS_A_VERDICT = PASS
DOCUMENT_MATERIALIZATION_ONLY = CONFIRMED
```

---

## 4. Class C/D — RQ1 lineage 감사

### 4.1 결과 파일 불변성

```
ssot_nb01/04_NB08_RQ1_RESULTS_v001.json

git log --follow --all   → 502bc12 단 1건. 이후 수정 이력 없음.

blob id at 502bc12 / e893eef / 3f4e821 / 07d132e / a31a4c2 / f786baa / 65ce14f
  = cfbe1d46d12bafe3e55f10c9d913627971228d30   (7개 commit 전부 동일)

sha256 on disk @ audit worktree
  = 768a3bccc7d5d081e90e6b2e1bf0dbc7230f416fce824698aa6d97f718cfbb59   EXPECTED 일치
```

```
RQ1_RESULT_BYTES_UNCHANGED = YES
```

`5daaa164…`가 어떤 commit의 어떤 버전과도 대응하지 않는다는 A의 판정은 재확인됐다.
전 세션에서 파일 bytes 및 `json.dumps` 정규화 7종을 대조했을 때도 재현되지 않았다.
**transcription error이며 결과 변조가 아니다.**

### 4.2 정정 위치

`06` `evidence_of_record.primary_result_json_sha256`와 `07` §1 evidence-of-record 블록,
**두 곳만** 1줄씩 변경됐다. `04`는 손대지 않았다 — 가리키는 대상을 고쳐 포인터를 맞추는
역행 수정이 아니다.

### 4.3 superseded hash 잔존 스캔

```
git grep 5daaa164 @ 65ce14f

  ssot/2026-08-18_1116_..._CLOSEOUT.md:190,208,254   사실정정 서술 (허용)
  tests/test_lineage.py:93                            negative assertion 상수 (허용)

  ssot_nb01/ 하위                                     NONE  ✅
```

frozen evidence-of-record 필드에는 잔존하지 않는다.

### 4.4 신규 lineage 테스트 — 독립 fail-closed 검증

repository 외부 복사본에 3가지 공격 시나리오를 주입해 직접 확인했다.

| 시나리오 | 주입 | 결과 |
|---|---|---|
| 1 | `04` result JSON 1바이트 변조 | `test_rq1_evidence_of_record_sha_matches_the_physical_result` **FAIL** ✅ |
| 2 | `06` 기록값을 `5daaa164…`로 되돌림 | 위 test + `test_superseded_..._not_reachable` **동시 FAIL** ✅ |
| 3 | `07` 산문 hash를 `06`과 불일치시킴 | `test_rq1_canonical_closeout_prose_quotes_the_same_sha` **FAIL** ✅ |
| 복원 | — | 11 passed ✅ |

A는 "checks 1 and 3 fire"라고 보고했으나, 실제로는 **3개 검사 전부가 각자의 시나리오에서
발화**한다. A의 보고보다 강한 커버리지다. artifact를 읽지 않으므로 parquet 없는 환경에서도
돈다는 주장도 확인됐다(audit worktree의 `data/registry/`는 비어 있다).

```
CLASS_C_VERDICT = PASS
CLASS_D_VERDICT = PASS
```

---

## 5. Class B — memory-guard governance 감사

### 5.1 분류 문구 존재 확인

`ssot/2026-08-18_1116_..._CLOSEOUT.md` §2.4:

```
APPROVED_ENGINEERING_GUARD_CORRECTION
NO_MEASUREMENT_SEMANTIC_CHANGE
NO_PRIOR_D05_RESULT_CHANGE
```

세 토큰 모두 명시적으로 기록되어 있다.

### 5.2 서술이 실제 코드를 정확히 대표하는가

`0ae4c214155c50860ac2a6f7390b08d1f398ee61` diff를 직접 읽었다. **코드는 변경하지 않았다.**

| 문서 주장 | 코드 실측 | 판정 |
|---|---|---|
| A: 종료 표본이 abort하지 않고 관측만 하며 판정은 `guard_abort_reason`에 보존 | `telemetry.py:129-135` `try: self.sample() except MemoryGuardAbort as exc: self._abort_reason = str(exc)` | **정확** |
| B: 연속 swap io는 자기 footprint가 YELLOW 임계 초과 시에만 RED | `memory_guard.py` `if (self._consecutive_swap_io >= RED_CONSECUTIVE_SWAP_IO_SAMPLES and swap_delta_mib > YELLOW_SWAP_DELTA_MIB)` | **정확** |
| 메모리 고갈 임계 불변 | `EMERGENCY_MIN_AVAILABLE_GIB` · `RED_MIN_AVAILABLE_GIB 5.0` · `RED_SWAP_DELTA_MIB 512.0` · `RED_RSS_GIB 6.0` — 0ae4c21 diff에 미포함, 전부 원형 | **정확** |
| in-flight abort 경로 불변 | `check()`가 여전히 RED/EMERGENCY에서 `MemoryGuardAbort` raise (`memory_guard.py:198-201`) | **정확** |
| guard가 측정에 관여하지 않음 | guard는 chunking/encoding/reconstruction/기록 컬럼 어디에도 진입하지 않음 | **정확** |

### 5.3 D-05 결과 불변 주장 대조

`outputs/manifests/CHUNK_O200K_BASE_VALIDATION_v001.json` 실측:

```
validation_status   PASS
checks              17/17 True
artifact_sha256     bfa98bd6cf7ee8b7254c469aed3e259ce43cc8f0529153347ca4c2c3fc1944ab
row_count           3,835,988
column_count        39
pair_set_md5        d9660d654ee449e4d0c23a0070225274
```

문서 §2.4의 인용과 전 항목 일치. 이 manifest는 감사 범위 diff에 포함되지 않는다(미접촉).

부수 확인 — §2.3이 인용한 `30/36 RED · MemAvailable 6.33 GiB · swap delta 19 MiB`는
**교정 이전 실행**의 관측치이고, 현재 persist된 manifest는 교정 이후 실행
(`36 samples · worst_memory_status YELLOW · red_or_worse_sample_count 0 · min MemAvailable 6.188`)이다.
서로 다른 실행이며, §2.4의 "이전 등급은 소급 재기술하지 않는다"와 정합한다. **모순 아님.**

```
MEMORY_GUARD_GOVERNANCE_VERDICT = PASS
```

---

## 6. 테스트 / 위생 — 독립 재실행

stale editable install에 의존하지 않고 audit worktree source root를 강제했다.

```
PYTHONPATH=/home/sieg/projects-wsl/KOEN_audit_gov_20260818/src

import 해소 위치 (전부 audit worktree)
  tokenization_premium            .../KOEN_audit_gov_20260818/src/tokenization_premium/__init__.py
  tokenization_premium.chunking   .../src/tokenization_premium/chunking.py
  tokenization_premium.telemetry  .../src/tokenization_premium/telemetry.py
  tokenization_premium.memory_guard .../src/tokenization_premium/memory_guard.py
```

tiktoken offline cache는 **hash 검증 후에만** 배치했다.

```
.runtime/tiktoken-cache/fb374d419588a4632f3f557e76b4b70aebbca790
sha256  446a9538cb6c348e3516120d7c08b09f57c36495e2acfffe59a5bf8b0cfb1a2d   EXPECTED 일치
        (= CHUNK_O200K_BASE_MANIFEST_v001.json encoding_file_sha256)
gitignore 대상(.gitignore:14) — staging 불가
```

결과:

```
pytest -q                      276 passed in 5.30s        (A 보고와 독립 일치)
ruff check src tests scripts   All checks passed  exit 0   (ruff 0.16.3)
git status --short             empty (clean)
```

staging 위생: parquet · xlsx · raw KO/EN · audit workbook · runtime cache **전무**.
diff에 등장하는 5개 객체는 전부 11–14 KB 텍스트 파일이다.

```
TESTS = 276 passed
RUFF  = PASS
WORKTREE_CLEAN = YES
HYGIENE = PASS
```

---

## 7. 발견 — `M-01` (MATERIAL)

### 7.1 사실

`ssot/2026-08-18_1116_KOEN_TP_G5_ENTRY_GOVERNANCE_CLOSEOUT.md` §3.4,
"Unchanged by this correction — **stated exhaustively**" 블록:

```
RQ1 estimand   unchanged   P(Y > 0 | Y != 0), and the pair-level median log TP
RQ1 cohort     unchanged   N = 3,785,441 analysed; pair-set d9660d654ee449e4d0c23a0070225274
RQ1 statistics unchanged   median 0.28768207245178085 · Wilcoxon W 6237534311943.0
                           · sign + 3330539 · bootstrap B 2000 seed 969634713
```

frozen record 실측:

| 항목 | 문서 §3.4 | 권위 artifact | 출처 |
|---|---|---|---|
| primary estimand | `P(Y > 0 \| Y != 0)`를 **먼저** 제시 | `theta = Median(Y)`, `H1: theta > 0` | `03_..._PROTOCOL_v001.md` §1 |
| 분석 cohort N | **3,785,441** | **3,835,988** | `02_ANALYSIS_COHORT_RQ1_v001.json` `primary_cohort_n` |
| Wilcoxon W | **6237534311943.0** | **6405551963244.0** | `06_..._CLOSEOUT_v001.json` `primary_unchanged` |
| sign + | **3330539** | **3375095** | 동일 |

인용된 세 값 `3,785,441 / 6237534311943.0 / 3330539`은 `06` JSON에서 각각
`known N` · `known Wilcoxon W` · `known sign +`, 즉 **known-direction 민감도 부분집합**의
값이다. protocol은 이를 "primary result **곁에** 보고하며 대체하지 않는다"고 규정한다.

`median 0.28768207245178085`은 두 cohort에서 동일하므로 이 오류를 가리지 못한다.
`bootstrap B 2000 / seed 969634713`은 primary 값으로 정확하다.

내부 모순도 있다 — `N = 3,785,441`을 **전체 3,835,988 pair-set의 해시**
`d9660d654ee449e4d0c23a0070225274`와 같은 줄에 병기했다.

### 7.2 왜 material인가

1. **문서 자신의 목적과 충돌한다.** §0은 이 closeout의 존재 이유를 "canonical history가
   자기 자신에 대해 참을 말하는가"로 규정한다. §3은 RQ1 metadata의 transcription error
   1건을 고치는 절이다. 그 절의 결론 블록이 RQ1 metadata 3건을 새로 틀리게 적는다.

2. **문서 자신의 classification과 충돌한다.** header가
   `NO_NEW_PRIMARY_ESTIMAND`를 선언하는데, §3.4는 primary estimand를
   `P(Y > 0 | Y != 0)`로 제시한다.

3. **SSOT가 명시적으로 금지한 혼동이다.** `06` JSON은
   `CONDITIONAL_NONZERO_SIGN_TEST`에 대해
   `not_a: "tie가 존재하는 population median에 대한 distribution-free exact statement"`,
   `role: "non-zero observation 내부의 polarity robustness"`를 못박았다.
   `RD-SSOT-CANONICAL-RETURN-01` §5-3은 이 분리를 closeout 필수 항목으로 요구했다.
   §3.4는 그 분리를 역전시킨다.

4. **canonical에 병합되면 내부 모순이 된다.** 병합 후 canonical main에서
   "RQ1 cohort N"을 조회하면 `ssot_nb01/02`·`06`은 3,835,988을,
   `ssot/2026-08-18_1116` §3.4는 3,785,441을 답한다.

5. **신규 테스트가 잡지 못한다.** `tests/test_lineage.py`의 3개 검사는 hash만 대조한다.
   서술 수준의 estimand/cohort 오기는 CI에 걸리지 않는다.

### 7.3 material이 **아닌** 것

명확히 한다. 다음은 이 발견의 함의가 아니다.

```
RQ1 결과 변조             아니다 — 04 blob은 7개 commit에서 동일
RQ1 재개(reopen)          아니다 — 04/02/03 미접촉
측정 무효                 아니다 — D02–D05 identity 및 D05 17/17 전부 유효
class A / C / D 결함      아니다 — 세 클래스 모두 PASS
memory-guard 판정 오류    아니다 — §5 전 항목 정확
```

`M-01`은 **class B 문서의 서술 결함 1건**이며, frozen artifact는 전부 정확하다.

### 7.4 시정 범위

`ssot/2026-08-18_1116_..._CLOSEOUT.md` §3.4 블록 3줄. 코드·테스트·artifact 무관.

권고 문안:

```
RQ1 result     unchanged
RQ1 estimand   unchanged   theta = Median(Y), H1: theta > 0 (one-sided).
                           P(Y > 0 | Y != 0)는 CONDITIONAL_NONZERO_SIGN_TEST의
                           conditional estimand이며 primary estimand가 아니다.
RQ1 cohort     unchanged   primary N = 3,835,988; pair-set d9660d654ee449e4d0c23a0070225274
                           (known-direction 민감도 부분집합 N = 3,785,441은 별개이며
                            primary를 대체하지 않는다)
RQ1 protocol   unchanged   NB08_RQ1_PROTOCOL_v001, protocol cells modified = 0
RQ1 statistics unchanged   primary median 0.28768207245178085 · primary Wilcoxon W 6405551963244.0
                           · primary sign + 3375095 / − 264175 / tie 196718
                           · bootstrap B 2000 seed 969634713
RQ1 verdict    unchanged   RQ1_PRIMARY_INFERENCE_PASS / NB08_RQ1_CLOSED
```

추가 권고(선택) — `tests/test_lineage.py`에 서술 수준 pin을 1건 더 두면 이 클래스가
CI에서 걸린다: 결정문서가 `primary N`을 언급할 때 `06`의 `primary_unchanged["primary N"]`과
일치해야 한다는 검사.

---

## 8. 판정

| 클래스 | 대상 | 판정 |
|---|---|---|
| A | canonical-return 실체화 | **PASS** — blob c7fdc7bf 동일, diff EMPTY |
| B | `RD-G5-ENTRY-GOVERNANCE-CLOSEOUT-01` | **FAIL** — `M-01` (§3.4) |
| C | RQ1 SHA 사실 정정 | **PASS** — 2개 site만, 04 미접촉 |
| D | lineage 회귀 테스트 | **PASS** — 3/3 fail-closed 독립 확인 |
| — | scope / 위생 / 테스트 / ruff | **PASS** |

```
G5_ENTRY_GOVERNANCE_AUDIT_FAIL

사유 : M-01 — RD-G5-ENTRY-GOVERNANCE-CLOSEOUT-01 §3.4가 RQ1 primary estimand,
       primary cohort N, primary Wilcoxon W, primary sign + 를 known-direction
       민감도 부분집합의 값으로 오기. 문서 자신의 NO_NEW_PRIMARY_ESTIMAND 선언 및
       06 closeout의 CONDITIONAL_NONZERO_SIGN_TEST 분리 규정과 충돌.

조치 : DO_NOT_MERGE_MAIN
       DO_NOT_RUN_G5
       Claude-A 또는 Director 승인 하의 §3.4 3줄 정정 후 재감사(해당 hunk 한정)
```

시정은 문서 1개 절이며, class A/C/D와 테스트·위생이 이미 통과했으므로
재감사는 `65ce14f..<fix>` 범위의 단일 hunk 확인으로 끝난다.

---

## 9. 감사가 하지 않은 것

```
main 병합                 하지 않음
G5 실행                   하지 않음
subject branch 수정       하지 않음
코드 / artifact 수정      하지 않음
KOEN_g5 scratch 접근      열람만, commit/reset/clean 없음
canonical worktree 변경   하지 않음 (07d132e 상태 유지, untracked 3건 보존)
```

---

**감사 종료**: 2026-08-18 11:36 KST, Claude-B.
**다음 조치권자**: Research Director → Claude-A (§3.4 정정).
