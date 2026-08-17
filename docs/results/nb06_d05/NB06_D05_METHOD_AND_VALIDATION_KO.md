# NB06 / D-05 방법론 및 검증

engineering / methodology 문서입니다. 무엇을 고정했고, 무엇을 검사했고,
어떤 실패가 있었는지를 기록합니다.

관련 구현:

| 경로 | 역할 |
|---|---|
| `src/tokenization_premium/chunking.py` | D-05 측정 로직 (연구 로직의 단일 소재지) |
| `src/tokenization_premium/telemetry.py` | R1 주기 runtime telemetry |
| `src/tokenization_premium/memory_guard.py` | memory/swap 등급 판정 |
| `notebooks/06_regex_chunk_audit.ipynb` | canonical notebook (실측 재계산 포함) |
| `scripts/run_d05_pilot.py` | pilot 실행 |
| `scripts/run_d05_full.py` | 전집단 실행 wrapper |
| `scripts/validate_d05.py` | 전집단 독립 검증 |
| `tests/test_chunking.py` | 73개 단위/회귀 테스트 |

---

## 1. Configuration freeze

D-05는 새 tokenizer 설정을 도입하지 않습니다. D-04가 동결한 설정을 그대로 씁니다.

| 항목 | 값 |
|---|---|
| tokenizer | `o200k_base` |
| tiktoken | 0.13.0 (오프라인 캐시만 사용, 네트워크 접근 없음) |
| Track | **Track A** — raw text |
| chat template | 사용 안 함 (`chat_template_used = False`) |
| special tokens | 사용 안 함 (`special_tokens_used = False`) |
| `pat_str` sha256 | `2d1b8dc11e89af71459b36004f698ab3693f59fd84f63e8ec2b49564ab857420` |
| `chunking_config_sha256` | `b8f26abf3e64a1d7d91284e7ccdda0a27a1d615052d86c304c9f7196e7f7dbf5` |

`chunking_config_sha256`은 rule version, spec 참조, tokenizer 신원, chunk 유형 규칙,
Track A 제약, authority 주석을 모두 담은 정규화 JSON의 해시입니다. 이 값이 artifact의
모든 행에 기록되며, 검증 단계에서 단일 값인지 확인합니다.

---

## 2. pat_str freeze

정규식을 **문헌이나 다른 코드에서 옮겨 적지 않습니다.**

```python
pat_str = encoding._pat_str                      # 살아 있는 encoder에서 직접 읽는다
actual  = sha256(pat_str.encode("utf-8"))
if actual != PAT_STR_SHA256:                     # D-04가 동결한 값
    raise ChunkConfigMismatch(...)               # HARD FAIL — 진행하지 않는다
```

옮겨 적으면 오타 하나로 "같은 tokenizer를 썼다"는 전제가 조용히 무너집니다.
읽고 대조하면 그 전제가 주장이 아니라 검사가 됩니다.

노트북 §1도 실행 시점에 같은 대조를 다시 수행하고, 그 결과가 저장된 출력에 남습니다.

---

## 3. regex_chunks의 fail-closed 계약

`regex_chunks(text, encoding=...)`는 `pattern.finditer`를 커서와 함께 순회하며
다음 넷을 **모두** 검사합니다. 하나라도 어긋나면 `ChunkInvariantViolation`을 던집니다.

| 위반 | 검사 방식 |
|---|---|
| **덮이지 않은 span** | 매치 시작 위치가 커서와 다르면 그 사이 구간이 손실된 것 |
| **길이 0 매치** | `end <= start`이면 빈 chunk — 계약상 생성하지 않음 |
| **끝부분 손실** | 마지막 매치 이후 커서가 문자열 끝에 도달하지 못하면 실패 |
| **concat 불일치** | `"".join(chunks) != text`이면 실패 |

중복 span은 커서 검사에 의해 자동으로 걸립니다 — 이전 매치의 끝보다 앞에서 시작하는
매치는 `start != cursor`가 되기 때문입니다.

**조용히 넘어가는 경로가 없다**는 점이 핵심입니다. 손실된 문자를 무시하고 통계만 내면
"chunk가 원문을 설명한다"는 전제가 검증 없이 통과합니다.

---

## 4. Token equivalence invariant — 가장 중요한 검사

chunk 분할이 D-04의 최종 token을 실제로 설명하는지는 다음으로 판정합니다.

```
direct_ids = D-04에 저장된 token ID 배열            # 전체 텍스트를 한 번에 인코딩한 결과

chunk_ids  = concat(
                 encode(chunk_1),
                 encode(chunk_2),
                 ...,
                 encode(chunk_K)
             )                                       # 조각별로 따로 인코딩해 이어붙인 결과

assert direct_ids == chunk_ids                        # 완전 일치해야 한다
```

이 등식이 성립해야만 "이 chunk가 저 token들을 만들었다"고 말할 수 있습니다.
성립하지 않으면 D-05는 D-04와 무관한 두 번째 측정이 되어버립니다.

구현에서는 이 검사를 **행마다** 수행하고, 불일치 시 예외를 던지는 대신
`token_equivalence_ok = False`와 `analysis_warning_reason`으로 기록합니다.
전집단 실행이 한 행 때문에 멈추지 않게 하되, 검증 단계에서 그런 행이 하나라도 있으면
promotion을 막습니다. 실제 결과는 **전집단 0건**입니다.

단위 테스트에도 양방향이 들어 있습니다 — 일치할 때 clean으로 표시되는지,
불일치를 주입했을 때 raise가 아니라 flag로 잡히는지.

---

## 5. Pilot 설계

전집단 실행 전에 게이트로 둔 단계입니다.

| 항목 | 값 |
|---|---|
| N | 20,000 pairs |
| 검사한 chunk | 665,765 |
| 표본 추출 | `md5(pair_id || 'D05_PILOT_v001')` 정렬 상위 — 결정적 |
| 층위 커버리지 | `domain`, `length_stratum`, `translation_direction`을 canonical artifact에서 직접 읽어 기록 |

pilot이 검사한 여섯 불변식과 결과:

| 불변식 | 위반 |
|---|---|
| 1. concat 재구성 실패 | 0 |
| 1b. 빈 chunk | 0 |
| 2. 손실/중복 span | 0 |
| 3. chunk 순서 비결정성 | 0 |
| 4. KO / EN token ID 불일치 | 0 / 0 |
| 5. token 수 불일치 | 0 |
| 6. 미분류 chunk type | 0 |
| 6b. type share 합 ≠ 1 | 0 |
| warning 행 | 0 |

`full_run_authorized = (total_mismatch == 0 and r1_periodic_sampling)` —
두 조건이 모두 참일 때만 전집단 실행이 시작됩니다. 전집단 wrapper가 실행 첫머리에서
이 값을 다시 읽어 확인합니다.

표본 선정 시 V2 EDA의 `NB06_TARGET_STRATA`를 참고 자료로만 쓸 수 있게 했고,
V2의 숫자는 evidence로 사용하지 않았습니다.

---

## 6. 전집단 실행

| 항목 | 값 |
|---|---|
| N | 3,835,988 (canonical final cohort 전수) |
| batch | 2,500행 스트리밍 |
| DuckDB | `memory_limit=3GB`, `threads=8`, spill 디렉터리 지정 |
| 쓰기 | 원자적(atomic) — `.partial`에 쓰고 검증 통과 후 rename |
| 재시작 | 목적지 또는 `.partial`이 이미 있으면 `FileExistsError`. 자동 재시작 없음 |

promotion 직전에 `validate_chunk_measurements`가 행 수·id 유일성·type share 합·
파생 통계 정합성·token 등가성을 재확인합니다. 하나라도 어긋나면 rename하지 않습니다.

---

## 7. 노트북 독립 재검사

`notebooks/06_regex_chunk_audit.ipynb` §3은 manifest를 신뢰하지 않고 직접 계산합니다.

| 항목 | 값 |
|---|---|
| N | 3,000 pairs |
| salt | `NB06_LIVE_CHECK_v001` — **pilot과 다른 값** |
| 검사한 chunk | 98,222 |
| 위반 | **0** |

salt를 다르게 둔 이유는, pilot이 뽑은 표본을 그대로 다시 검사하면 "pilot이 자기 표본을
다시 승인하는" 구조가 되기 때문입니다.

노트북은 이후 전집단 artifact의 신원(sha256·pair-set md5·anti-join)을 재확인하고,
D-05 schema에 token ID 배열·`token_premium`·§8 분해항이 없음을 **assert로** 검사합니다.
범위 경계가 주장이 아니라 테스트여야 하기 때문입니다.

---

## 8. 검증 manifest — 17개 체크

`scripts/validate_d05.py`가 물리 parquet에서 다시 계산합니다.
결과: `outputs/manifests/CHUNK_O200K_BASE_VALIDATION_v001.json`, **17/17 PASS**.

| # | 체크 | 의미 |
|---|---|---|
| 1 | `row_count_equals_canonical_cohort` | 행 수 = 3,835,988 |
| 2 | `pair_id_unique` | pair 중복 없음 |
| 3 | `chunk_measurement_id_unique` | 측정 id 중복 없음 |
| 4 | `tokenizer_fk_unique` | D-04 외래키 중복 없음 |
| 5 | `no_missing_vs_d04` | D-04에 있는데 D-05에 없는 pair = 0 |
| 6 | `no_extra_vs_d04` | D-05에 있는데 D-04에 없는 pair = 0 |
| 7 | `no_orphan_tokenizer_fk` | 존재하지 않는 D-04 행을 가리키는 외래키 = 0 |
| 8 | `pair_set_md5_matches_canonical` | pair 집합 해시가 canonical 값과 동일 |
| 9 | `single_chunking_config` | 설정 해시가 단일 값이며 동결값과 일치 |
| 10 | `single_pat_str_in_artifact` | `pat_str` 해시가 단일 값이며 D-04와 일치 |
| 11 | `manifest_schema_version_matches` | schema version 일치 |
| 12 | `physical_columns_match_schema` | 물리 열 집합 = 선언된 schema |
| 13 | `zero_token_equivalence_failures` | token 등가성 실패 0 |
| 14 | `zero_reconstruction_failures` | 재구성 실패 0 |
| 15 | `manifest_sha256_matches_artifact` | manifest가 기록한 해시 = 실제 파일 해시 |
| 16 | `manifest_row_count_matches` | manifest 행 수 = 실제 행 수 |
| 17 | `r1_periodic_telemetry` | 주기 telemetry가 실제로 수행됨 |

5–7번(anti-join과 외래키)은 "행 수가 같다"보다 강한 조건입니다. 행 수가 같아도
서로 다른 pair 집합일 수 있기 때문입니다. 8번은 그보다도 강한 집합 동일성 검사입니다.

> **구현 주의** — pair-set 해시는 `lineage.pair_set_md5()` 하나만 사용합니다.
> 이 패키지 작업 중 검증기와 노트북에서 집계 SQL을 다시 작성하다가 구분자를
> canonical 정의(`''`) 대신 `'|'`로 쓴 오류가 있었고, 값이 달라 검증이 FAIL했습니다.
> 해시 정의를 두 번 적지 않는 것이 유일한 예방책입니다.

---

## 9. Artifact identity

| 항목 | 값 |
|---|---|
| path | `data/registry/CHUNK_O200K_BASE_v001.parquet` (SSOT §38 명명) |
| sha256 | `bfa98bd6cf7ee8b7254c469aed3e259ce43cc8f0529153347ca4c2c3fc1944ab` |
| schema version | `CHUNK_O200K_BASE_v001` |
| 행 / 열 | 3,835,988 / 39 |
| pair-set md5 | `d9660d654ee449e4d0c23a0070225274` |
| 상류 D-04 | `TOKEN_O200K_BASE_v001`, sha256 `1c30e3276222dd94…` |
| 상류 pair registry | `PAIR_REGISTRY_v002`, sha256 `95f523d11b0e8fcf…` |

상류 artifact의 신원은 `lineage.assert_canonical_artifact()`로 fail-closed 검증합니다.
이 값들은 Claude-B가 물리 parquet에서 독립적으로 재계산한 것이며
(adjudication `441d5802bfebe178fd220d08b653c60dfad17faf`), 파이프라인이 자기 자신에 대해
보고한 값이 아닙니다.

전집단 실행을 **세 번 독립적으로** 수행했고 세 번 모두 동일한 sha256이 나왔습니다.

---

## 10. 실행 중 발생한 실패와 그 처리

실패를 숨기지 않고 기록합니다.

### 10.1 두 번의 `MemoryGuardAbort` (실행 시작 지점)

```
MemoryGuardAbort: [D05_FULL_...] RED: MemAvailable 4.31 GiB < 5.0
MemoryGuardAbort: [D05_FULL_...] RED: MemAvailable 4.67 GiB < 5.0
```

**원인** — guard 임계값이 아니라 `execute_chunk_run`의 DuckDB 연결이었습니다.
`memory_limit`도 `temp_directory`도 지정하지 않아 DuckDB 기본값(RAM의 80%)이 적용되고
spill 경로가 없었습니다. cohort 읽기는 D-04와 pair registry를 join한 뒤 `pair_id`로
정렬하는데, 이 행에는 양쪽 token ID 배열과 양쪽 분석 텍스트가 함께 실려 있어
D-03/D-04의 같은 형태 읽기보다 행당 비용이 훨씬 큽니다.

**조치** — 임계값을 낮추지 않고 한도(`3GB`)와 spill 디렉터리를 명시했습니다.
이후 실행은 MemAvailable 6.19–6.5 GiB를 유지했습니다. 한도와 스레드 수는 manifest에
기록되어, 호스트가 우연히 허용한 만큼이 아니라 같은 예산에서 재현할 수 있습니다.

### 10.2 종료 표본이 완료된 실행을 사후에 실패시킨 문제

1차 전집단 실행은 3,835,988행의 write·검증·promotion을 **모두 마친 뒤**
`RuntimeTelemetry.__exit__`의 마지막 표본에서 `MemoryGuardAbort`를 던졌고,
그 결과 **manifest만** 유실됐습니다.

guard는 실행을 **시작하기 전**과 **진행 중**에 보호하는 장치입니다. 이미 끝난 실행을
실패로 만들면 아무것도 구하지 못하고 증거만 사라집니다. 종료 표본은 관측만 하도록 고쳤고,
판정은 버리지 않고 `guard_abort_reason`과 `worst_memory_status`에 보존합니다.

### 10.3 memory guard RED 오탐

연속 swap io 규칙이 `pswpin`/`pswpout` 증가분이 0보다 크기만 하면 RED로 올렸습니다.
이 둘은 `/proc/vmstat`의 **시스템 전역** 카운터라 다른 프로세스의 배경 paging까지 셉니다.

관측된 오탐:

| 규칙 | 실측 | 임계 | 발동 |
|---|---|---|---|
| MemAvailable | 최소 6.33 GiB | < 5.0 | 미발동 |
| 프로세스 RSS | 최대 3.28 GiB | > 6.0 | 미발동 |
| swap delta | 최대 19 MiB | ≥ 512 | 미발동 |
| 연속 swap io | 340초 동안 45.2 MiB | 3표본 연속 | **발동** |

36표본 중 30개가 RED로 기록됐습니다. 건강한 실행이 상시 RED가 되면 등급이 신호 역할을
잃습니다 — 이것은 주기 telemetry 작업이 없애려던 실패와 같은 종류입니다.

모듈의 계약("baseline 대비 판정")대로, 연속 swap io는 **자기 footprint가 YELLOW
임계를 넘어 실제로 누적될 때만** RED로 올리도록 고쳤습니다. 그렇지 않은 배경 paging은
페이지 수와 함께 YELLOW로 기록됩니다. 메모리 고갈 규칙(MemAvailable/RSS/swap delta)은
그대로입니다. 전용 테스트 5개가 양방향을 고정합니다 — 관측된 배경 패턴은 RED가 되면 안 되고,
실제로 누적되는 thrash는 여전히 RED여야 합니다.

교정 후 전집단 실행: `worst_memory_status = YELLOW`, RED 이상 표본 **0개**.

### 10.4 그 밖의 오류

- 검증 스크립트가 D-05에 없는 `chunk_schema_version` 열을 조회했습니다. D-03/D-04도
  schema version을 행에 넣지 않고 manifest와 config 해시로 고정하는 규약입니다.
  검증기를 그 규약에 맞췄습니다.
- pair-set 해시 구분자 오류 — §8의 주의 참조.

---

## 11. R1 runtime observability

| 항목 | 값 |
|---|---|
| telemetry 구간 | 347.21 초 |
| stage 전체 구간 | 349.857 초 |
| 평균 처리량 | 11,045.8 rows/sec |
| 표본 수 | 36 (10초 주기) |
| 최소 MemAvailable | 6.188 GiB |
| 최대 RSS | 3.28 GiB (실행 **직전** 표본 — pre-flight 잔여) |
| 실행 구간 RSS | 1.55 – 2.91 GiB |
| swap delta 최대 | 0 MiB |
| RED 이상 표본 | 0 |
| 최종 상태 | COMPLETED |

각 표본은 timestamp, 경과, 처리 행 수, rows/sec, RSS, MemAvailable, SwapUsed,
vmstat si/so, stage, status, memory_status를 담습니다.

R1의 핵심은 **표본이 시작/종료 두 개뿐이면 안 된다**는 것입니다. 실제 최소값은 양 끝점이
아니라 중간에 나오기 때문입니다. `is_periodic()`이 이를 강제하고, 명시적 negative 테스트
(`test_two_sample_run_is_reported_as_not_periodic`)가 2표본 실행을 R1 통과로 보고하지
않음을 고정합니다.

---

## 12. 테스트

| 파일 | 개수 | 대상 |
|---|---|---|
| `tests/test_chunking.py` | 73 | 설정 동결, 불변식, schema, 범위 경계 |
| `tests/test_telemetry.py` | 13 | 주기 표본, 종료 표본 동작, 요약 |
| `tests/test_memory_guard.py` | 5 | 등급 판정 양방향 |
| `tests/test_canonical_notebooks.py` | NB06 포함 | lineage 위생, 호출 시그니처, 저장된 출력 |

전체 스위트: **273 passed, 0 failed**.

특히 다음 두 테스트가 범위 경계를 지킵니다.

- `test_d05_is_not_a_second_token_authority` — D-05 schema에 token ID 배열,
  `token_premium`, `compression_penalty`가 없어야 한다.
- `test_flattened_chunk_tokens_equal_direct_encode` — chunk별 인코딩을 이어붙인 결과가
  직접 인코딩과 같아야 한다.
