"""장시간 local research job의 진행률·heartbeat·memory 상태를 안전하게 기록한다."""

from __future__ import annotations

import datetime as dt
import json
import math
import numbers
import os
import re
import subprocess
import threading
import time
from collections.abc import Iterable, Mapping
from pathlib import Path
from types import TracebackType
from typing import Any, Literal
from zoneinfo import ZoneInfo

import psutil
from tqdm.auto import tqdm

from tokenization_premium.paths import PROJECT_ROOT

DEFAULT_PROGRESS_INTERVAL_SEC = 10.0
DEFAULT_PROGRESS_DIR = Path(".runtime/progress")
PROGRESS_INTERVAL_ENV = "TOKENIZATION_PREMIUM_PROGRESS_INTERVAL_SEC"
PROGRESS_DIR_ENV = "TOKENIZATION_PREMIUM_PROGRESS_DIR"
MEMORY_WARNING_GIB = 3.0
MEMORY_CRITICAL_GIB = 2.0

_KST = ZoneInfo("Asia/Seoul")
_SAFE_LABEL_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]*")
_SAFE_METRIC_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9_]*")
_FORBIDDEN_METRIC_TOKENS = frozenset({"content", "email", "en", "ko", "name", "payload", "phone", "pii", "prompt", "raw", "response", "sentence", "text"})
_RESERVED_FIELDS = frozenset(
    {
        "timestamp",
        "run_id",
        "phase",
        "stage",
        "status",
        "processed",
        "total",
        "percent",
        "elapsed_sec",
        "rate_per_sec",
        "eta_sec",
        "pid",
        "git_sha",
        "rss_gib",
        "mem_available_gib",
        "memory_status",
        "checkpoint",
        "metrics",
    }
)
def progress_tqdm[T](iterable: Iterable[T] | None = None, **kwargs: Any) -> Any:
    """Jupyter, nbclient, nbconvert, terminal에서 같은 기본값을 쓰는 tqdm wrapper다."""
    kwargs.setdefault("mininterval", DEFAULT_PROGRESS_INTERVAL_SEC)
    kwargs.setdefault("dynamic_ncols", True)
    return tqdm(iterable=iterable, **kwargs)


def classify_liveness(age_sec: float, process_alive: bool = True) -> str:
    """마지막 heartbeat age와 process 생존 여부를 표준 liveness 상태로 변환한다."""
    if not process_alive:
        return "INTERRUPTED"
    if age_sec < 0 or not math.isfinite(age_sec):
        raise ValueError("heartbeat age must be a finite nonnegative number")
    if age_sec <= 20:
        return "HEALTHY"
    if age_sec <= 30:
        return "LAGGING"
    if age_sec <= 60:
        return "WARNING"
    return "STALLED"


def snapshot_liveness(snapshot: Mapping[str, Any], *, now: dt.datetime | None = None, process_alive: bool | None = None) -> str:
    """Persisted snapshot에서 현재 liveness를 계산하며 late heartbeat만으로 process를 종료하지 않는다."""
    timestamp = dt.datetime.fromisoformat(str(snapshot["timestamp"]))
    reference = now or dt.datetime.now(tz=_KST)
    if reference.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    alive = psutil.pid_exists(int(snapshot["pid"])) if process_alive is None else process_alive
    return classify_liveness((reference - timestamp).total_seconds(), alive)


def _safe_label(field: str, value: str) -> str:
    if not isinstance(value, str) or len(value) > 128 or _SAFE_LABEL_PATTERN.fullmatch(value) is None:
        raise ValueError(f"{field} must be at most 128 characters and match {_SAFE_LABEL_PATTERN.pattern!r}")
    return value


def _normalized_total(total: int | float | None) -> int | float | None:
    if total is None:
        return None
    if isinstance(total, bool) or not isinstance(total, numbers.Real) or not math.isfinite(float(total)) or total <= 0:
        raise ValueError("total must be a finite positive number or None")
    return int(total) if isinstance(total, numbers.Integral) else float(total)


def _safe_metric(name: str, value: int | float) -> tuple[str, int | float]:
    if name in _RESERVED_FIELDS or _SAFE_METRIC_PATTERN.fullmatch(name) is None:
        raise ValueError(f"unsafe or reserved metric name: {name!r}")
    if _FORBIDDEN_METRIC_TOKENS.intersection(name.lower().split("_")):
        raise ValueError(f"raw-text or PII-like metric name is forbidden: {name!r}")
    if isinstance(value, bool) or not isinstance(value, numbers.Real) or not math.isfinite(float(value)):
        raise TypeError(f"metric {name!r} must be a finite numeric value")
    normalized = int(value) if isinstance(value, numbers.Integral) else float(value)
    return name, normalized


def _resolve_interval(interval_sec: float, environ: Mapping[str, str]) -> float:
    raw_value: str | float = environ.get(PROGRESS_INTERVAL_ENV, interval_sec)
    try:
        resolved = float(raw_value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{PROGRESS_INTERVAL_ENV} must be a positive number") from error
    if not math.isfinite(resolved) or resolved <= 0:
        raise ValueError(f"{PROGRESS_INTERVAL_ENV} must be a finite positive number")
    return resolved


def _resolve_progress_root(progress_dir: str | Path | None, environ: Mapping[str, str]) -> Path:
    configured = Path(progress_dir) if progress_dir is not None else Path(environ.get(PROGRESS_DIR_ENV, DEFAULT_PROGRESS_DIR))
    return configured.resolve() if configured.is_absolute() else (PROJECT_ROOT / configured).resolve()


def _git_sha(project_root: Path) -> str:
    completed = subprocess.run(
        ["git", "-C", str(project_root), "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip() if completed.returncode == 0 else "UNKNOWN"


def _memory_status(mem_available_gib: float) -> str:
    if mem_available_gib < MEMORY_CRITICAL_GIB:
        return "MEMORY_CRITICAL"
    if mem_available_gib < MEMORY_WARNING_GIB:
        return "MEMORY_WARNING"
    return "OK"


def _duration_text(seconds: float | None) -> str:
    if seconds is None:
        return "NA"
    whole = max(0, int(seconds))
    hours, remainder = divmod(whole, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


class ProgressHeartbeat:
    """연구 결과를 변경하지 않고 main-thread progress와 독립 heartbeat를 기록한다."""

    def __init__(
        self,
        run_id: str,
        phase: str,
        stage: str,
        total: int | float | None = None,
        interval_sec: float = DEFAULT_PROGRESS_INTERVAL_SEC,
        progress_dir: str | Path | None = None,
    ) -> None:
        self.run_id = _safe_label("run_id", run_id)
        self.phase = _safe_label("phase", phase)
        self._stage = _safe_label("stage", stage)
        self._total = _normalized_total(total)
        self.interval_sec = _resolve_interval(interval_sec, os.environ)
        self.project_root = PROJECT_ROOT
        self.progress_root = _resolve_progress_root(progress_dir, os.environ)
        self.run_dir = self.progress_root / self.run_id
        self.jsonl_path = self.run_dir / "progress.jsonl"
        self.latest_path = self.run_dir / "latest.json"
        self.pid_path = self.run_dir / "run.pid"
        self._git_sha = _git_sha(self.project_root)
        self._pid = os.getpid()
        self._processed: int | float = 0
        self._metrics: dict[str, int | float] = {}
        self._checkpoint: str | None = None
        self._status = "INITIALIZED"
        self._started_monotonic = time.monotonic()
        self._stage_started_monotonic = self._started_monotonic
        self._state_lock = threading.RLock()
        self._emit_lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._bar: Any = None
        self._entered = False
        self._closed = False

    def __enter__(self) -> ProgressHeartbeat:
        if self._entered:
            raise RuntimeError("ProgressHeartbeat cannot be entered more than once")
        self._entered = True
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self._atomic_write_text(self.pid_path, f"{self._pid}\n")
        with self._state_lock:
            self._status = "RUNNING"
        self._bar = progress_tqdm(total=self._total, desc=f"{self.phase}:{self._stage}")
        self._emit()
        self._thread = threading.Thread(target=self._heartbeat_loop, name=f"progress-heartbeat-{self.run_id}", daemon=True)
        self._thread.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        self.close("FAILED" if exc_type is not None else "COMPLETED")
        return False

    def update(self, n: int | float = 1, **metrics: int | float) -> None:
        if isinstance(n, bool) or not isinstance(n, numbers.Real) or not math.isfinite(float(n)) or n < 0:
            raise ValueError("progress increment must be a finite nonnegative number")
        normalized_metrics = dict(_safe_metric(name, value) for name, value in metrics.items())
        with self._state_lock:
            self._processed += n
            self._metrics.update(normalized_metrics)
        if self._bar is not None:
            self._bar.update(n)

    def set_stage(self, stage: str, total: int | float | None = None) -> None:
        normalized_stage = _safe_label("stage", stage)
        normalized_total = _normalized_total(total)
        with self._state_lock:
            self._stage = normalized_stage
            self._total = normalized_total
            self._processed = 0
            self._checkpoint = None
            self._metrics = {}
            self._stage_started_monotonic = time.monotonic()
        if self._bar is not None:
            self._bar.close()
            self._bar = progress_tqdm(total=normalized_total, desc=f"{self.phase}:{normalized_stage}")
        self._emit()

    def checkpoint(self, name: str, **metrics: int | float) -> None:
        normalized_name = _safe_label("checkpoint", name)
        normalized_metrics = dict(_safe_metric(metric_name, value) for metric_name, value in metrics.items())
        with self._state_lock:
            self._checkpoint = normalized_name
            self._metrics.update(normalized_metrics)
        self._emit()

    def set_metric(self, name: str, value: int | float) -> None:
        normalized_name, normalized_value = _safe_metric(name, value)
        with self._state_lock:
            self._metrics[normalized_name] = normalized_value

    def snapshot(self) -> dict[str, Any]:
        now_monotonic = time.monotonic()
        timestamp = dt.datetime.now(tz=_KST)
        process = psutil.Process(self._pid)
        rss_gib = process.memory_info().rss / 1024**3
        mem_available_gib = psutil.virtual_memory().available / 1024**3
        with self._state_lock:
            processed = self._processed
            total = self._total
            stage_elapsed = max(0.0, now_monotonic - self._stage_started_monotonic)
            rate = float(processed) / stage_elapsed if processed > 0 and stage_elapsed > 0 else None
            percent = float(processed) / float(total) * 100 if total is not None else None
            eta = max(float(total) - float(processed), 0.0) / rate if total is not None and rate is not None and rate > 0 else None
            payload: dict[str, Any] = {
                "timestamp": timestamp.isoformat(timespec="seconds"),
                "run_id": self.run_id,
                "phase": self.phase,
                "stage": self._stage,
                "status": self._status,
                "processed": processed,
                "total": total,
                "percent": round(percent, 6) if percent is not None else None,
                "elapsed_sec": round(max(0.0, now_monotonic - self._started_monotonic), 3),
                "rate_per_sec": round(rate, 6) if rate is not None else None,
                "eta_sec": round(eta, 3) if eta is not None else None,
                "pid": self._pid,
                "git_sha": self._git_sha,
                "rss_gib": round(rss_gib, 6),
                "mem_available_gib": round(mem_available_gib, 6),
                "memory_status": _memory_status(mem_available_gib),
                "checkpoint": self._checkpoint,
                "metrics": dict(self._metrics),
            }
        return payload

    def close(self, status: str) -> None:
        normalized_status = _safe_label("status", status.upper())
        with self._state_lock:
            if self._closed:
                return
            self._status = normalized_status
            self._closed = True
        self._stop_event.set()
        if self._thread is not None and self._thread is not threading.current_thread():
            self._thread.join(timeout=max(self.interval_sec * 2, 0.2))
        self._emit()
        if self._bar is not None:
            self._bar.close()

    def _heartbeat_loop(self) -> None:
        while not self._stop_event.wait(self.interval_sec):
            self._emit()

    def _emit(self) -> None:
        payload = self.snapshot()
        serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        with self._emit_lock:
            self.run_dir.mkdir(parents=True, exist_ok=True)
            with self.jsonl_path.open("a", encoding="utf-8") as stream:
                stream.write(serialized + "\n")
                stream.flush()
                os.fsync(stream.fileno())
            self._atomic_write_text(self.latest_path, serialized + "\n")
            tqdm.write(self._terminal_text(payload))

    def _atomic_write_text(self, destination: Path, text: str) -> None:
        temporary = destination.with_name(f".{destination.name}.{self._pid}.{threading.get_ident()}.tmp")
        with temporary.open("w", encoding="utf-8") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)

    @staticmethod
    def _terminal_text(payload: Mapping[str, Any]) -> str:
        timestamp = dt.datetime.fromisoformat(str(payload["timestamp"]))
        progress_line = "progress=INDETERMINATE\npercent=NA" if payload["total"] is None else f"{payload['processed']}/{payload['total']}\n{payload['percent']:.2f}%"
        rate_text = "NA" if payload["rate_per_sec"] is None else f"{payload['rate_per_sec']:.2f} items/s"
        return (
            f"[{timestamp:%H:%M:%S} KST]\n"
            f"phase={payload['phase']}\n"
            f"stage={payload['stage']}\n"
            f"{progress_line}\n"
            f"throughput={rate_text}\n"
            f"ETA {_duration_text(payload['eta_sec'])}\n"
            f"elapsed {_duration_text(payload['elapsed_sec'])}\n"
            f"RSS {payload['rss_gib']:.2f}GiB\n"
            f"mem_available {payload['mem_available_gib']:.2f}GiB\n"
            f"memory_status={payload['memory_status']}\n"
            f"checkpoint={payload['checkpoint'] or 'NONE'}"
        )


__all__ = [
    "DEFAULT_PROGRESS_DIR",
    "DEFAULT_PROGRESS_INTERVAL_SEC",
    "PROGRESS_DIR_ENV",
    "PROGRESS_INTERVAL_ENV",
    "ProgressHeartbeat",
    "classify_liveness",
    "progress_tqdm",
    "snapshot_liveness",
]
