# KO-EN Tokenization Premium — ENG-OBS-001 Long-Running Job Progress / Heartbeat Contract

> Effective request: 2026-08-16 17:32 KST  
> Scope: all long-running local research / data / model / tuning jobs  
> Classification: Engineering / observability / reproducibility; no research-semantic change  
> Applies prospectively; historical D-01 artifacts are not rewritten.

## 1. Core rule

Any local operation expected to run longer than 30 seconds MUST expose:

1. interactive progress (`tqdm`)
2. independent 10-second heartbeat
3. elapsed time
4. processed / total
5. percentage when total is known
6. throughput
7. ETA when estimable
8. current process RSS
9. host/WSL available memory
10. current stage
11. checkpoint / artifact state
12. final COMPLETED / FAILED / INTERRUPTED status

`tqdm` alone is insufficient because a single slow iteration or SQL query can block progress updates.

## 2. Standard environment variables

```text
TOKENIZATION_PREMIUM_PROGRESS_INTERVAL_SEC=10
TOKENIZATION_PREMIUM_PROGRESS_DIR=.runtime/progress
TOKENIZATION_PREMIUM_DUCKDB_MEMORY_LIMIT=8GB
```

The progress interval defaults to 10 seconds.

## 3. Runtime files

Ephemeral, non-Git:

```text
.runtime/progress/<run_id>/
├── progress.jsonl
├── latest.json
└── run.pid
```

Safe final aggregate summary:

```text
outputs/reports/runtime/RUN_SUMMARY_<run_id>.json
```

No raw KO/EN text, URL, PII, recoverable text samples, or raw provider responses may be written to progress logs.

## 4. Required heartbeat fields

```json
{
  "timestamp": "2026-08-16T17:32:40+09:00",
  "run_id": "P2_QC_20260816T173240",
  "phase": "02_normalize_and_qc",
  "stage": "lid_scan",
  "status": "RUNNING",
  "processed": 1250000,
  "total": 4050507,
  "percent": 30.86,
  "elapsed_sec": 67.4,
  "rate_per_sec": 18432.1,
  "eta_sec": 152.0,
  "rss_gib": 3.1,
  "mem_available_gib": 10.4,
  "pid": 12345,
  "git_sha": "...",
  "checkpoint": "batch_125"
}
```

If the total is unknown, `percent` and `eta_sec` MUST be null/NA. Never invent progress percentages.

## 5. Terminal format

Every ~10 seconds, emit a compact human-readable line:

```text
[17:32:40 KST] phase=02 stage=LID_SCAN | 1,250,000/4,050,507 30.86%
| 18,432 rows/s | ETA 00:02:32 | elapsed 00:01:07
| RSS 3.1GiB | mem_avail 10.4GiB | checkpoint=batch_125
```

For an indeterminate blocking stage:

```text
[17:35:10 KST] phase=02 stage=DUCKDB_GROUP_RESOLUTION
| progress=INDETERMINATE | elapsed 00:00:50
| RSS 5.8GiB | mem_avail 7.4GiB | spill=1.2GiB
```

## 6. Python implementation pattern

Use standard dependencies already present in the project:

```python
import json
import os
import threading
import time
from contextlib import AbstractContextManager
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import psutil
from tqdm.auto import tqdm
```

Recommended API:

```python
with ProgressHeartbeat(
    run_id=run_id,
    phase="02_normalize_and_qc",
    stage="lid_scan",
    total=n_rows,
    interval_sec=10.0,
) as progress:
    for batch in tqdm(
        batches,
        total=n_batches,
        desc="LID scan",
        mininterval=10.0,
        dynamic_ncols=True,
    ):
        result = process(batch)
        progress.update(len(batch))
```

`ProgressHeartbeat` MUST own a daemon heartbeat thread so that it still emits every 10 seconds when the current `process(batch)` or SQL call takes longer than 10 seconds.

The heartbeat thread reads counters only; it must not mutate research results.

## 7. Atomic persistence

`latest.json` MUST be written atomically:

```python
tmp = latest_path.with_suffix(".tmp")
tmp.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
os.replace(tmp, latest_path)
```

`progress.jsonl` is append-only and flushed every heartbeat.

On normal completion:
`status=COMPLETED`

On exception:
`status=FAILED`
plus exception class only; do not dump sensitive raw records.

On SIGINT / process interruption where detectable:
`status=INTERRUPTED`.

## 8. Agent monitoring rule

The orchestrator must not stay silent while a long-running job is active.

Preferred execution mode:

```bash
PYTHONUNBUFFERED=1 \
TOKENIZATION_PREMIUM_PROGRESS_INTERVAL_SEC=10 \
<command>
```

If the long command does not stream notebook-cell output, launch a separate monitor:

```bash
while kill -0 "$(cat .runtime/progress/<run_id>/run.pid)" 2>/dev/null; do
  cat .runtime/progress/<run_id>/latest.json
  sleep 10
done
```

The agent session must relay or summarize each heartbeat in the streaming transcript.

## 9. Liveness policy

```text
heartbeat age <= 20 sec  : HEALTHY
20 < age <= 30 sec       : LAGGING
30 < age <= 60 sec       : WARNING — inspect PID/memory
age > 60 sec             : STALLED — inspect process, do NOT auto-kill
process dead             : INTERRUPTED
```

No automatic kill/restart solely because a heartbeat is late.

## 10. Memory guardrails

For the current WSL environment:

```text
WSL visible RAM ≈ 15 GiB
swap            = 4 GiB
DuckDB default  = 8GB
concurrent safe = 6GB suggested
spill           = mandatory
```

Heartbeat should include current RSS and available memory.

Recommended warning thresholds:

```text
mem_available < 3 GiB : MEMORY_WARNING
mem_available < 2 GiB : MEMORY_CRITICAL
```

The job should not automatically terminate unless the task-specific contract says so.

## 11. Stage-specific instrumentation

### Phase 2 — normalization / QC
Report:
- rows processed / total
- normalization failures
- LID processed
- provisional flag counts
- semantic-QC batch counts
- do not present provisional accepted/rejected counts as final before stage completion

### Phase 3 — representation features
Report:
- pairs processed
- codepoints/bytes batches
- artifact rows written
- throughput / ETA

### Phase 4 — morphology
Report:
- pairs processed
- analyzer failures
- cache hits/misses if used
- batch latency
- RSS

### Phase 4/5 — tokenizer measurement
Report:
- pairs processed
- tokenizer roundtrip failures
- rows written
- pairs/sec
- ETA

### Bootstrap / robustness
For `B=5000`:
- completed replicates / 5000
- percentage
- replicate/sec
- ETA
- seed family / chunk index
- never stream raw bootstrap samples

### Hyperparameter tuning
Use hierarchical progress:

```text
TUNING 17/100 trials
CURRENT trial=17
CV fold=3/5
elapsed
ETA
best_cv_score_so_far
```

Rules:
- progress may show training/CV metrics only
- never expose held-out test performance during tuning
- the final holdout stays sealed under LR-01

### Model fit with one long blocking `.fit()`
The heartbeat thread continues every 10 seconds with:
- stage
- elapsed
- RSS
- available memory
- current trial/fold
- percent/ETA = NA unless the backend exposes a trustworthy progress counter

Never fabricate an ETA.

## 12. Nested progress

At most two visible progress levels:

1. parent stage / trial
2. current batch / fold

Avoid dozens of nested tqdm bars.

## 13. Notebook rule

Canonical notebooks retain visible progress.

Use:

```python
from tqdm.auto import tqdm
```

not `tqdm.notebook` as a hard dependency on widget rendering.

The notebook must still be reproducible under headless `nbclient/nbconvert`.

The progress utility belongs in:

```text
src/tokenization_premium/progress.py
```

The notebook imports it; implementation must not be hidden exclusively in `src/`—the notebook markdown must explain the stage and emitted artifacts.

## 14. Test requirements

Add tests for:

- 10-second interval configuration
- percent / ETA when total known
- null percent / ETA when total unknown
- atomic latest.json write
- JSONL append
- final COMPLETED state
- exception → FAILED state
- no raw-text fields in heartbeat schema
- current RSS is nonnegative
- progress dir respects current worktree root
- environment override parsing

Tests should use short intervals (e.g. 0.05 sec) and synthetic loops; never wait 10 seconds in unit tests.

## 15. Integration sequencing

Current direct Git snapshot:
- integration/g1 = e25f048...
- research/g1-gate-claude = 566f30b... (CR-003 proposal; not yet approved)
- impl/g1-runtime-safety-codex = f69fbf6... (ready)
- eda/g1-support = 2e11112... (remote still old; local work in progress)

Recommended:
1. merge runtime-safety branch now
2. branch `impl/g1-progress-observability-codex` from the new integration HEAD
3. implement ENG-OBS-001
4. unit/lint only; no 5.65M rerun in feature branch
5. merge observability after review
6. run future canonical long jobs with heartbeat enabled
7. CR-003 remains a Director decision before formal G1 closure
8. EDA joins later when its portability commit is pushed and validated

## 16. Research boundary

This contract does NOT change:
- RQ
- estimand
- source portfolio
- normalization definitions
- tokenizer
- morphology
- QC acceptance criteria
- statistical models
- hyperparameter search space
- holdout policy
- causal claim boundaries

It is an engineering observability and recovery contract only.
