"""Heavy-run periodic runtime telemetry (R1).

두 번(시작/종료)만 표본화하는 감시는 실패다. 실제 최소값을 놓치기 때문이다.
전집단 실행 중 관측된 사례: 기록된 최소 MemAvailable은 6.06 GiB였지만 외부 20초 모니터가
관측한 실제 최소값은 4.75 GiB였다.

이 모듈은 daemon thread로 실행 전 구간을 주기적으로 표본화하고, 표본 이력을 manifest에
실을 수 있는 형태로 보존한다. 표본 하나가 담는 항목(RD-SSOT-CANONICAL-RETURN-01 §10):

    timestamp · elapsed · rows_processed · rows_per_second · RSS ·
    MemAvailable · SwapUsed · vmstat si · vmstat so · stage · final status
"""

from __future__ import annotations

import contextlib
import datetime as dt
import json
import os
import threading
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import psutil

from tokenization_premium.memory_guard import (
    STATUS_GREEN,
    MemoryGuard,
    MemoryGuardAbort,
    read_swap_io_counters,
    read_swappiness,
)

_KST = ZoneInfo("Asia/Seoul")
_GIB = 2**30
_MIB = 2**20

DEFAULT_INTERVAL_SEC = 10.0
STATUS_RUNNING = "RUNNING"
STATUS_COMPLETED = "COMPLETED"
STATUS_FAILED = "FAILED"
STATUS_INTERRUPTED = "INTERRUPTED"


@dataclass
class TelemetrySample:
    """실행 중 한 시점의 런타임 관측치."""

    timestamp_kst: str
    elapsed_sec: float
    rows_processed: int
    rows_per_second: float | None
    rss_gib: float
    mem_available_gib: float
    swap_used_mib: float
    swap_delta_mib: float
    swap_in_pages: int
    swap_out_pages: int
    stage: str
    status: str
    memory_status: str


@dataclass
class RuntimeTelemetry:
    """
    /**
     * @purpose heavy run 전 구간을 주기적으로 표본화해 진짜 최소/최대값을 포착한다.
     * @spec_ref RD-SSOT-CANONICAL-RETURN-01 §10; RD-FAST-G5-01 §12 (R1)
     * @param run_id 실행 식별자
     * @param stage 현재 단계 이름 (실행 중 set_stage로 갱신 가능)
     * @param total 전체 행 수 (알 수 없으면 None; percent/ETA를 지어내지 않는다)
     * @param interval_sec 표본 주기. 기본 10초이며 환경변수로 재정의 가능하다.
     * @return context manager
     * @raises MemoryGuardAbort guard가 RED/EMERGENCY를 판정하고 abort_on_red=True인 경우
     * @validation 표본이 시작/종료 2개뿐이면 R1 조건 미달이다 (is_periodic 참조).
     * @artifact manifest의 runtime_telemetry 섹션
     */
    """

    run_id: str
    stage: str = "MAIN"
    total: int | None = None
    interval_sec: float = DEFAULT_INTERVAL_SEC
    abort_on_red: bool = True
    max_samples: int = 20_000

    samples: list[TelemetrySample] = field(default_factory=list, init=False)
    rows_processed: int = field(default=0, init=False)
    status: str = field(default=STATUS_RUNNING, init=False)

    def __post_init__(self) -> None:
        override = os.environ.get("TOKENIZATION_PREMIUM_PROGRESS_INTERVAL_SEC")
        if override:
            with contextlib.suppress(ValueError):   # 잘못된 값은 기본 주기를 유지한다
                self.interval_sec = max(0.01, float(override))
        self._process = psutil.Process()
        self._guard = MemoryGuard(self.run_id)
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._started = 0.0
        self._abort_reason: str | None = None
        self.swappiness = read_swappiness()
        self.baseline_swap_used_mib = round(psutil.swap_memory().used / _MIB, 2)

    # ---------------------------------------------------------------- lifecycle
    def __enter__(self) -> RuntimeTelemetry:
        self._started = time.monotonic()
        self.sample()                      # 시작 표본
        self._thread = threading.Thread(target=self._loop, name=f"telemetry-{self.run_id}",
                                        daemon=True)
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc_type is KeyboardInterrupt:
            self.status = STATUS_INTERRUPTED
        elif exc_type is not None:
            self.status = STATUS_FAILED
        else:
            self.status = STATUS_COMPLETED
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=self.interval_sec * 2 + 1.0)
        # 종료 표본은 관측만 한다. guard는 실행을 '시작하기 전'과 '진행 중'에 보호하기 위한
        # 장치이며, 이미 끝난 실행을 사후에 실패로 만들면 완료된 산출물의 manifest만 잃는다.
        # RED 판정은 버리지 않고 _abort_reason / worst_memory_status로 보존한다.
        try:
            self.sample()
        except MemoryGuardAbort as exc:
            self._abort_reason = str(exc)

    def _loop(self) -> None:
        while not self._stop.wait(self.interval_sec):
            try:
                self.sample()
            except MemoryGuardAbort as exc:  # guard 판정은 기록만 하고 thread를 죽이지 않는다
                self._abort_reason = str(exc)

    # ---------------------------------------------------------------- sampling
    def update(self, n: int = 1) -> None:
        """처리 행 수를 증가시킨다. 측정만 하며 연구 결과를 바꾸지 않는다."""
        with self._lock:
            self.rows_processed += int(n)

    def set_stage(self, stage: str) -> None:
        with self._lock:
            self.stage = stage

    def sample(self) -> TelemetrySample:
        """한 시점을 표본화한다. RED/EMERGENCY면 abort_on_red에 따라 예외를 던진다."""
        guard_sample = self._guard.sample()
        elapsed = time.monotonic() - self._started if self._started else 0.0
        with self._lock:
            rows = self.rows_processed
            stage = self.stage
        swap_in, swap_out = read_swap_io_counters()
        sample = TelemetrySample(
            timestamp_kst=dt.datetime.now(tz=_KST).isoformat(timespec="seconds"),
            elapsed_sec=round(elapsed, 3),
            rows_processed=rows,
            rows_per_second=round(rows / elapsed, 1) if elapsed > 0 and rows else None,
            rss_gib=guard_sample.rss_gib,
            mem_available_gib=guard_sample.mem_available_gib,
            swap_used_mib=round(psutil.swap_memory().used / _MIB, 2),
            swap_delta_mib=guard_sample.swap_delta_mib,
            swap_in_pages=max(0, swap_in - self._guard.baseline_swap_in),
            swap_out_pages=max(0, swap_out - self._guard.baseline_swap_out),
            stage=stage,
            status=self.status,
            memory_status=guard_sample.status,
        )
        with self._lock:
            if len(self.samples) < self.max_samples:
                self.samples.append(sample)
        if self.abort_on_red and guard_sample.status not in (STATUS_GREEN, "YELLOW"):
            raise MemoryGuardAbort(f"[{self.run_id}] {guard_sample.status}: "
                                   f"{'; '.join(guard_sample.reasons)}")
        return sample

    # ---------------------------------------------------------------- reporting
    @property
    def sample_count(self) -> int:
        return len(self.samples)

    def is_periodic(self, minimum: int = 3) -> bool:
        """시작/종료 2개만으로는 R1을 만족하지 못한다."""
        return self.sample_count >= minimum

    def summary(self) -> dict[str, Any]:
        """manifest에 실을 runtime_telemetry 요약."""
        if not self.samples:
            return {"run_id": self.run_id, "sample_count": 0,
                    "r1_periodic_sampling": False, "final_status": self.status}
        mem = [s.mem_available_gib for s in self.samples]
        rss = [s.rss_gib for s in self.samples]
        rates = [s.rows_per_second for s in self.samples if s.rows_per_second]
        last = self.samples[-1]
        return {
            "run_id": self.run_id,
            "interval_sec": self.interval_sec,
            "vm_swappiness": self.swappiness,
            "sample_count": self.sample_count,
            "r1_periodic_sampling": self.is_periodic(),
            "elapsed_sec": last.elapsed_sec,
            "rows_processed": last.rows_processed,
            "expected_rows": self.total,
            "mean_rows_per_second": round(sum(rates) / len(rates), 1) if rates else None,
            "min_mem_available_gib": min(mem),
            "max_mem_available_gib": max(mem),
            "peak_rss_gib": max(rss),
            "baseline_swap_used_mib": self.baseline_swap_used_mib,
            "peak_swap_used_mib": max(s.swap_used_mib for s in self.samples),
            "peak_swap_delta_mib": max(s.swap_delta_mib for s in self.samples),
            "total_swap_in_pages": last.swap_in_pages,
            "total_swap_out_pages": last.swap_out_pages,
            "worst_memory_status": self._guard.worst_status,
            "red_or_worse_sample_count": sum(
                1 for s in self.samples if s.memory_status not in (STATUS_GREEN, "YELLOW")),
            "guard_abort_reason": self._abort_reason,
            "final_status": self.status,
            "samples": [asdict(s) for s in self.samples],
        }

    def write(self, path: Path) -> Path:
        """텔레메트리 전문을 로컬 런타임 파일로 남긴다 (원문/PII 없음)."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.summary(), ensure_ascii=False, indent=1) + "\n",
                        encoding="utf-8")
        return path


__all__ = [
    "DEFAULT_INTERVAL_SEC",
    "STATUS_COMPLETED",
    "STATUS_FAILED",
    "STATUS_INTERRUPTED",
    "STATUS_RUNNING",
    "RuntimeTelemetry",
    "TelemetrySample",
]
