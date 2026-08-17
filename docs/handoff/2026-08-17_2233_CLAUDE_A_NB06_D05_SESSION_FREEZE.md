# Claude-A Session Freeze — NB06 / D-05

**2026-08-17 22:33 KST** · Engineering / Reproducibility Steward

---

## 1. Authority

| 문서 | 역할 |
|---|---|
| `KOEN-TP-RS-001` | SSOT. §5 처리 단계, §5.1 세 경계 구분, §12.5 D-05 계약, §14 tokenizer 고정, §25 Track A, §38 명명 |
| `RD-FAST-G5-01` | fast-track 결정. §12 R1 (periodic runtime telemetry) 요구 |
| `RD-SSOT-CANONICAL-RETURN-01` | canonical return 결정. §10 telemetry 표본 최소 항목 |

Lineage authority: Claude-B 독립 재계산
`441d5802bfebe178fd220d08b653c60dfad17faf`
(`ssot/2026-08-17_1730_KOEN_TP_G2_G3_G4_FINAL_ADJUDICATION.md`)

---

## 2. Git at close

| | |
|---|---|
| canonical science main | `a31a4c27417b93567bb6e261b6225813aaa5f66e` (`merge: close Phase-4 regex chunk measurement`) |
| current branch | `results/nb06-d05-reproducibility-20260817` |
| branch base | `a31a4c27417b93567bb6e261b6225813aaa5f66e` |
| starting branch SHA (세션 시작 시 remote) | `9ed4b799115f7b12994d0b2833e69669714dae24` |
| final local SHA | 이 freeze checkpoint commit — commit이 자기 SHA를 담을 수 없어 터미널 보고에 기록 |
| final remote SHA | 위와 동일 (push 후 확인) |

**main은 이 세션에서 수정하지 않았습니다.** 병합도 하지 않았습니다.

NB06 canonical result commit: `c9aa4796f8157b9025deee33ef6504f5921aaf59`
R1 initial close: `164b2fa801032b06a18237fc501ea52288b5457f`

---

## 3. What I completed today

| # | 항목 | 커밋 |
|---|---|---|
| 1 | R1 periodic runtime telemetry 구현 (`telemetry.py`, daemon 표본 스레드) | `164b2fa` |
| 2 | frozen `o200k_base` regex-chunk 측정 구현 (`chunking.py`) | `b7eb754` |
| 3 | token-ID equivalence validation + 73개 단위/회귀 테스트, deterministic pilot | `b82ac1c` |
| 4 | runtime guard correction (종료 표본 오작동, 전역 vmstat 기반 RED 오탐) | `0ae4c21` |
| 5 | DuckDB bounded-memory fix (`memory_limit=3GB` + spill) | `8005c52` |
| 6 | full D-05 population run + D-05 canonical notebook + 독립 validation + manifests | `c9aa479` |
| 7 | Phase-4 병합 (`--no-ff`) | `a31a4c2` |
| 8 | 한국어 interpretation package (README / RESULT_CARD / INTERPRETATION / METHOD) + figures + 집계 JSON | `b31c12c` |
| 9 | Level A/B/C 재현성 구분, deterministic figure hashing, package verifier, repro manifest | `9ed4b79` |
| 10 | session freeze (이 문서 + README freeze section) | 이 커밋 |

세부:

- **R1 periodic runtime telemetry** — 10초 주기 daemon 표본. 표본당
  timestamp · elapsed · rows · rows/sec · RSS · MemAvailable · SwapUsed ·
  vmstat si/so · stage · status · memory_status. 시작/종료 2표본만으로는 R1을
  통과했다고 보고하지 않음을 negative 테스트로 고정.
- **runtime guard correction** — §6 참조.
- **DuckDB bounded-memory fix** — §6 참조.
- **frozen o200k regex-chunk implementation** — `pat_str`을 live encoder에서 읽어
  D-04 동결 해시와 대조. 불일치 시 `ChunkConfigMismatch`. `regex_chunks`는 커서
  기반 fail-closed(덮이지 않은 span / 길이 0 매치 / 끝부분 손실 / concat 불일치).
- **deterministic pilot** — 20,000 pair, salt `D05_PILOT_v001`, 665,765 chunk,
  전 불변식 0. `full_run_authorized`가 전집단 실행의 게이트.
- **token-ID equivalence validation** — chunk별 encode를 이어붙인 결과가 D-04에
  저장된 token ID 배열과 완전 일치해야 함. 전집단 실패 0.
- **full D05 population run** — N=3,835,988. 독립 3회 실행 모두 동일 SHA256.
- **D05 canonical notebook** — `notebooks/06_regex_chunk_audit.ipynb`. pilot과
  다른 salt(`NB06_LIVE_CHECK_v001`)로 3,000 pair를 새로 뽑아 여섯 불변식 재계산
  (98,222 chunk, 위반 0). schema 침범 여부를 assert로 검사.
- **independent validation** — `scripts/validate_d05.py`, 17/17 PASS.
- **artifact / manifest hashes** — §4 참조.
- **Korean interpretation package / README / RESULT_CARD / figures** — 용어는
  `한국어 설명(Original English Term)` 병기, schema identifier는 미번역.
  figure는 `NB06_D05_Vxx` (canonical `F01`–`F09` 미사용).
- **Level A/B/C reproducibility distinction** — §7 참조.
- **deterministic figure hashing** — `svg.hashsalt` 고정 + SVG/PNG metadata에서
  실행 시각 제거. 이것 없이는 "figure 재현" 검사가 성립하지 않았음.
- **package verifier** — 파일 존재 / 내부 링크 / figure hash 재현 / 문서 수치와
  집계 JSON 기계 대조 / canonical figure id 미사용 / claim boundary / 공개 위생
  (parquet·원문·chunk 문자열·token id 배열 없음)을 30개 체크로 확인.

---

## 4. Scientific evidence

| 항목 | 값 |
|---|---|
| artifact | `data/registry/CHUNK_O200K_BASE_v001.parquet` (SSOT §38 명명) |
| N | 3,835,988 |
| columns | 39 |
| schema version | `CHUNK_O200K_BASE_v001` |
| SHA256 | `bfa98bd6cf7ee8b7254c469aed3e259ce43cc8f0529153347ca4c2c3fc1944ab` |
| pair-set md5 | `d9660d654ee449e4d0c23a0070225274` |
| `chunking_config_sha256` | `b8f26abf3e64a1d7d91284e7ccdda0a27a1d615052d86c304c9f7196e7f7dbf5` |
| `pat_str` sha256 | `2d1b8dc11e89af71459b36004f698ab3693f59fd84f63e8ec2b49564ab857420` |
| 상류 D-04 | `TOKEN_O200K_BASE_v001`, sha256 `1c30e3276222dd94885ae4f79fc6ab5c45e4e26226de0afd91fc6b1f7d2c16e7` |
| 상류 pair registry | `PAIR_REGISTRY_v002`, sha256 `95f523d11b0e8fcf…` |

검증 결과 (`outputs/manifests/CHUNK_O200K_BASE_VALIDATION_v001.json`, 17/17 PASS):

- reconstruction failures = **0**
- token equivalence failures = **0**
- analysis warning rows = **0**
- D-04 대비 anti-join 양방향 = **0 / 0**
- 고아 외래키 = **0**
- chunking config / `pat_str` 단일값, 물리 열 = 선언 schema

Pilot: 20,000 pair · 665,765 chunk · 전 항목 0.
Notebook 독립 재검사: 3,000 pair · 98,222 chunk · 위반 0 (pilot과 다른 salt).

Runtime (R1): telemetry 347.21초 · stage 349.857초 · 평균 11,045.8 rows/sec ·
표본 36개(10초 주기) · 최소 MemAvailable 6.188 GiB · 최대 RSS 3.28 GiB(실행 직전
표본의 pre-flight 잔여; 실행 구간은 1.55–2.91 GiB) · swap delta 0 MiB ·
RED 이상 표본 0 · COMPLETED.

---

## 5. Headline descriptive finding

| | KO | EN |
|---|---|---|
| mean regex chunks / pair-side (`chunk_count`) | **13.56** | **19.50** |
| `tokens_per_chunk` | **2.02** | **1.04** |
| `mean_chunk_bytes` | 8.12 | 4.94 |

로그 분해 (두 항의 부호가 반대):

```
ln(N_ko/N_en) = ln(C_ko/C_en) + ln(density ratio)
   +0.2852    =    -0.3672    +    +0.6523          잔차 max 4.7e-16
```

**해석 경계**

허용:

> Under the measured `o200k_base` Track A configuration, Korean and English
> exhibit different regex-chunk and tokens-per-chunk profiles.
>
> The Korean side formed fewer regex chunks but exhibited substantially greater
> final-token expansion per chunk. This is a descriptive tokenizer-mechanism
> measurement; its conditional explanatory contribution is evaluated later in M3.

금지 (문서 어디에도 쓰지 않았음):

- regex chunking이 TP를 유발한다
- 한국어 morphology 때문에 chunk가 이렇게 된다
- `o200k`가 한국어를 차별한다
- byte encoding이 token premium을 유발한다
- 모델 품질상의 불이익

상태: `DESCRIPTIVE MECHANISM MEASUREMENT` / `NOT CAUSAL`.
D-04가 token 수·TP의 유일한 authority이며, D-05 schema에는 token ID 배열도
`token_premium`도 §8 분해항도 없습니다 (회귀 테스트로 강제).

---

## 6. Engineering incidents resolved

숨기지 않고 기록합니다.

### 6.1 DuckDB no `memory_limit` induced memory pressure

전집단 실행이 두 번 `MemoryGuardAbort`로 중단
(`MemAvailable 4.31 GiB < 5.0`, 이어서 `4.67 GiB < 5.0`).

원인은 guard 임계값이 아니라 `execute_chunk_run`의 DuckDB 연결이었습니다.
`memory_limit`도 `temp_directory`도 지정하지 않아 기본값(RAM의 80%)이 적용되고
spill 경로가 없었습니다. cohort 읽기는 D-04와 pair registry를 join한 뒤 `pair_id`로
정렬하는데, 이 행에는 양쪽 token ID 배열과 양쪽 분석 텍스트가 함께 실려 있어
D-03/D-04의 같은 형태 읽기보다 행당 비용이 훨씬 큽니다.

### 6.2 3GB DuckDB memory limit / spill fix

임계값을 낮추는 대신 `memory_limit='3GB'` + spill 디렉터리를 명시했습니다. 이후
실행은 MemAvailable 6.19–6.5 GiB를 유지하며 완주. 한도와 스레드 수를 manifest에
기록해 같은 예산에서 재현 가능하게 했습니다.

### 6.3 Telemetry closing-sample false abort

1차 전집단 실행은 3,835,988행의 write·검증·promotion을 **모두 마친 뒤**
`RuntimeTelemetry.__exit__`의 마지막 표본에서 `MemoryGuardAbort`를 던져
**manifest만** 유실시켰습니다.

guard는 실행 전·중을 보호하는 장치입니다. 이미 끝난 실행을 실패로 만들면 아무것도
구하지 못하고 증거만 사라집니다. 종료 표본은 관측만 하도록 고쳤고, 판정은
`guard_abort_reason` / `worst_memory_status`에 보존합니다.

### 6.4 Ambient vmstat paging false RED

연속 swap io 규칙이 `pswpin`/`pswpout` 증가분이 0보다 크기만 하면 RED로 올렸습니다.
이 둘은 `/proc/vmstat`의 **시스템 전역** 카운터라 다른 프로세스의 배경 paging까지
셉니다. 36표본 중 30개가 RED였고, 그때 나머지 세 RED 규칙은 모두 미발동이었습니다
(MemAvailable 최소 6.33 GiB / RSS 최대 3.28 GiB / swap delta 최대 19 MiB,
340초 동안 45.2 MiB paging).

모듈 계약("baseline 대비 판정")대로, 연속 swap io는 자기 footprint가 YELLOW 임계를
넘어 실제로 누적될 때만 RED로 올리도록 고쳤습니다. 메모리 고갈 규칙은 그대로이며,
전용 테스트 5개가 양방향을 고정합니다. 교정 후 전집단 실행은
`worst_memory_status = YELLOW`, RED 이상 표본 0.

> **Director 검토 요청** — 6.3과 6.4는 guard의 판정 의미를 바꾼 변경입니다.
> 되돌리려면 `memory_guard.py`의 조건절 하나와 `telemetry.py`의 `__exit__`
> try/except만 되돌리면 됩니다.

### 6.5 그 밖의 자체 오류 (수정 완료)

- 검증 스크립트와 노트북에서 pair-set 해시 집계 SQL을 다시 작성하다가 구분자를
  canonical 정의(`''`) 대신 `'|'`로 사용 → 검증 FAIL. `lineage.pair_set_md5()`
  하나만 쓰도록 교체.
- 검증 스크립트가 D-05에 없는 `chunk_schema_version` 열을 조회. D-03/D-04도
  schema version을 행에 넣지 않는 규약이므로 검증기를 규약에 맞춤.
- matplotlib이 SVG 요소 id를 실행마다 무작위화하고 두 포맷에 타임스탬프를 삽입해
  figure hash가 매번 달랐음 → `svg.hashsalt` 고정 + metadata 제거.
- canonical notebook 스캐너가 IPython magic을 파싱하지 못함 (NB06이 magic을 쓰는
  첫 canonical notebook) → 스캔 전 magic 줄을 빈 줄로 치환.

---

## 7. Reproducibility status

| 수준 | 필요한 것 | 상태 |
|---|---|---|
| **LEVEL A** 문서/figure | Git checkout만 | **PASS** — SVG/PNG 8개 hash 동일 |
| **LEVEL B** D-05 검증 | + 로컬 `CHUNK_O200K_BASE_v001.parquet`, `TOKEN_O200K_BASE_v001.parquet` | **PASS** — 17/17 |
| **LEVEL C** 전집단 재실행 | + `PAIR_REGISTRY_v002.parquet`(2.8 GB), tiktoken 오프라인 캐시, MemAvailable ≥ 5 GiB | **NOT_RUN TODAY** |

**Git만으로 raw source부터 full reconstruction 가능한가 — 불가능합니다.**

`data/registry/**`가 `.gitignore`로 제외되어 있어 `PAIR_REGISTRY_v002.parquet`와
`TOKEN_O200K_BASE_v001.parquet`가 저장소에 없습니다. 두 파일은 Phase 2–3 파이프라인의
산출물이며, 그 단계까지 거슬러 재생성하려면 원본 코퍼스가 필요합니다.

확인된 것은 **결정성**입니다 — 입력이 갖춰진 호스트에서 3회 독립 실행이 동일한
SHA256을 냈습니다. 이는 "Git만으로 재현된다"와 다른 주장이며, 문서에도 그렇게
구분해 적었습니다.

동결 시점 재검증: `FIGURE_REPRODUCTION=PASS` · `PACKAGE_VERIFICATION=PASS` ·
`D05_VALIDATION=PASS`.

---

## 8. Files owned / modified (이 branch)

### `docs/results/nb06_d05/` (패키지, 이번 세션 신규)

```
README.md
RESULT_CARD.md
NB06_D05_INTERPRETATION_KO.md
NB06_D05_METHOD_AND_VALIDATION_KO.md
REPRODUCE.md
NB06_D05_REPRO_MANIFEST_v001.json
extract_visual_data.py
build_nb06_figures.py
verify_nb06_d05.py
reproduce.sh
data/NB06_D05_VISUAL_DATA_v001.json
figures/NB06_D05_V01_pipeline_boundary.{svg,png}
figures/NB06_D05_V02_chunk_vs_token_expansion.{svg,png}
figures/NB06_D05_V03_validation.{svg,png}
figures/NB06_D05_V04_runtime.{svg,png}
```

### 이미 main에 병합된 측정 산출물 (`a31a4c2` 이하)

```
src/tokenization_premium/chunking.py
src/tokenization_premium/telemetry.py
src/tokenization_premium/memory_guard.py
notebooks/06_regex_chunk_audit.ipynb
scripts/run_d05_pilot.py
scripts/run_d05_full.py
scripts/validate_d05.py
tests/test_chunking.py
tests/test_telemetry.py
tests/test_memory_guard.py
tests/test_canonical_notebooks.py
outputs/manifests/CHUNK_O200K_BASE_MANIFEST_v001.json
outputs/manifests/CHUNK_O200K_BASE_PILOT_MANIFEST_v001.json
outputs/manifests/CHUNK_O200K_BASE_VALIDATION_v001.json
```

### `docs/handoff/`

```
2026-08-17_2233_CLAUDE_A_NB06_D05_SESSION_FREEZE.md   (이 문서)
```

전체 테스트 273 passed / 0 failed. ruff (`src`, `tests`, `scripts`,
`docs/results/nb06_d05`, NB06) clean.

---

## 9. Remaining known issues

새로 고치지 않고 기록만 합니다.

### 9.1 `RD-SSOT-CANONICAL-RETURN-01` 미통합 — **Director / 다음 세션 검토 필요**

```
branch : docs/ssot-canonical-return-20260817
commit : e92701289edec339fc2f6eb7b7a8c1292190815e
```

동결 시점 `origin/main`(`a31a4c2`)의 조상이 아님을 확인했습니다.
이 결정 문서는 R1 telemetry 요구(§10)의 근거이므로, canonical main에 반영되지 않은
상태가 유지되면 근거 문서와 구현이 서로 다른 브랜치에 존재하게 됩니다.

**DIRECTOR / NEXT SESSION INTEGRATION REVIEW REQUIRED.**

### 9.2 Guard 판정 의미 변경 (§6.3, §6.4) — Director 승인 대기

측정 결과에는 영향이 없으나(데이터 무결성 검사와 무관) 향후 heavy run의 등급 표기가
달라집니다. 되돌리는 방법은 §6.4에 기재.

### 9.3 지시 문서 손상 구간

`NB06 / D-05 REPRODUCIBLE RESEARCH RESULT PACKAGE` 지시의 §10 LEVEL C 중반부터
§15까지가 전송 중 손상되어(`"필수 canonical upstoken으로 확장되는 정도는 훨씬 컸다."`)
판독 불가했습니다. LEVEL C는 저장소를 직접 조사해 실제 전제조건을 기술했으나,
§11–§15에 있었을 지시는 **수행하지 못했습니다.** 재전송 시 보완 가능합니다.

### 9.4 관측 사항 (조치하지 않음)

동결 시점에 `KOEN_g5` worktree가 `a31a4c2`,
branch `research/g5-analysis-readiness-20260817`로 열려 있음을 관측했습니다.
A는 접근하지 않았습니다.

---

## 10. Next handoff

1. `git fetch origin --prune` 후 canonical main remote 재확인.
2. `RD-SSOT-CANONICAL-RETURN-01`(`e927012`) integration 상태 확인 및 판정.
3. A documentation branch (`results/nb06-d05-reproducibility-20260817`)는
   **frozen 유지**. 이 branch에서 추가 작업하지 않는다.
4. G5는 그 결과로 확정된 canonical main에서 **fresh branch**로 연다.
5. **A는 G5를 시작하지 않는다.** A의 다음 역할은 대기 또는 engineering support.

```
DO_NOT_START = G5, NB07, NB09
```
