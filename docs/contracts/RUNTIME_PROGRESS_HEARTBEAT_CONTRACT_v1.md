# Runtime Progress / Heartbeat Contract v1

**Contract ID:** `ENG-OBS-001`

**Scope:** 장시간 local execution의 engineering observability

**Research semantics:** 변경 없음

## 1. Observable state

`ProgressHeartbeat`는 run/phase/stage, 처리량, total, percent, elapsed, 관측 throughput, 계산 가능한 경우의 ETA, checkpoint, PID, Git SHA, process RSS, WSL/Linux available memory를 보고한다. Main thread의 `update()` 호출과 별개인 daemon thread가 기본 10초마다 같은 상태를 읽으므로 DuckDB SQL, `model.fit()`, tokenizer/morphology batch, 느린 파일 또는 API 호출 중에도 heartbeat를 남긴다.

Heartbeat thread는 연구 데이터, 모델, QC 결과 또는 분석 산출물을 변경하지 않는다. 상태를 읽고 observability 파일과 terminal 출력만 갱신한다.

## 2. API and tqdm

공개 API:

- `ProgressHeartbeat(run_id, phase, stage, total=None, interval_sec=10.0, progress_dir=None)`
- `update(n=1, **metrics)`
- `set_stage(stage, total=None)`
- `checkpoint(name, **metrics)`
- `set_metric(name, value)`
- `snapshot()`
- `close(status)`
- context manager: 정상 종료 `COMPLETED`, 예외 종료 `FAILED`

`progress_tqdm()`은 `tqdm.auto.tqdm`을 사용하고 `mininterval=10.0`, `dynamic_ncols=True`를 기본값으로 둔다. Notebook widget을 직접 import하지 않으므로 Jupyter, nbclient, nbconvert, terminal에서 동일 API를 사용한다.

## 3. Persistence and crash recovery

기본 ephemeral 경로:

```text
.runtime/progress/<run_id>/
├── progress.jsonl  # append-only, 매 record flush + fsync
├── latest.json     # same-directory temporary file + os.replace
└── run.pid
```

`latest.json`은 atomic replace하므로 monitor가 partial JSON을 읽지 않는다. `progress.jsonl`은 기존 record를 다시 쓰지 않으며 checkpoint와 heartbeat 이력을 보존한다. Process crash 이후 monitor는 마지막 valid `latest.json`, JSONL history, `run.pid`로 마지막 안전 상태를 확인한다.

최종 safe summary가 필요하면 stage owner가 `outputs/reports/runtime/RUN_SUMMARY_<run_id>.json`에 별도로 기록할 수 있다. Core heartbeat는 Git-tracked summary를 자동 생성하지 않는다.

## 4. Required fields

모든 snapshot은 다음을 포함한다.

```text
timestamp (Asia/Seoul), run_id, phase, stage, status,
processed, total, percent, elapsed_sec, rate_per_sec, eta_sec,
pid, git_sha, rss_gib, mem_available_gib, memory_status,
checkpoint, metrics
```

Optional `metrics` 값은 유한한 숫자만 허용한다.

## 5. Unknown-total behavior

`total=None`이면:

```text
progress=INDETERMINATE
percent=null / terminal NA
eta_sec=null / terminal NA
```

처리량은 실제 `update()`와 경과시간이 있을 때만 보고한다. Total 또는 양의 관측 rate가 없으면 ETA를 만들지 않는다.

## 6. Privacy boundary

Heartbeat에는 raw KO/EN text, sentence, prompt, response, content, payload, PII 또는 복원 가능한 source text를 기록하지 않는다. `run_id`, phase, stage, checkpoint는 제한된 identifier 문법만 허용한다. Optional metric은 숫자만 허용하며 raw/text/KO/EN/PII 계열 metric 이름을 거부한다.

Runtime JSONL/latest/PID는 `.runtime/` 아래에 있어 Git에서 제외된다. 연구 dataset row, exception message, API request/response body는 heartbeat에 복사하지 않는다.

## 7. Memory telemetry

- `rss_gib`: 현재 Python process RSS
- `mem_available_gib`: `psutil.virtual_memory().available`
- available `<3 GiB`: `MEMORY_WARNING`
- available `<2 GiB`: `MEMORY_CRITICAL`

Memory warning은 관측 신호다. Stage contract가 명시적으로 종료 권한을 부여하지 않는 한 heartbeat는 job을 자동 종료하지 않는다.

## 8. Liveness and agent monitoring

Monitor는 `latest.json` timestamp age와 `run.pid` process 상태를 함께 본다.

| Condition | State |
|---|---|
| age `<=20s` | `HEALTHY` |
| `20s < age <=30s` | `LAGGING` |
| `30s < age <=60s` | `WARNING` |
| age `>60s` | `STALLED` |
| process dead | `INTERRUPTED` |

Late heartbeat만으로 process를 kill하지 않는다. Agent는 먼저 PID 생존, memory 상태, checkpoint, JSONL 마지막 valid record, stage의 정상적인 blocking 특성을 확인한다.

## 9. Nested progress rule

한 run에는 하나의 authoritative `ProgressHeartbeat`만 둔다. Outer stage heartbeat가 liveness와 persistence를 소유한다. Nested loop는 같은 heartbeat에 numeric metric/checkpoint를 갱신하거나, 화면 표시만 필요한 경우 별도 tqdm bar를 `position`으로 구분한다. Nested bar가 별도 `latest.json`을 덮어쓰거나 동일 run ID로 두 heartbeat thread를 만들면 안 된다.

## 10. Runtime configuration

```text
TOKENIZATION_PREMIUM_PROGRESS_INTERVAL_SEC=10
TOKENIZATION_PREMIUM_PROGRESS_DIR=.runtime/progress
```

환경변수는 engineering runtime knob이며 `configs/research_v1.yaml`에 넣지 않는다. 상대 progress directory는 현재 import된 package의 worktree root 기준으로 해석한다.

## 11. Semantic boundary

ENG-OBS-001은 RQ, estimand, schema, QC 기준, normalization, tokenizer, morphology, statistical model, split, source policy를 변경하지 않는다. Progress와 heartbeat는 관측 및 crash-recovery metadata만 추가한다.
