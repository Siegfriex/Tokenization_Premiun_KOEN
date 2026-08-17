"""실행 중 memory/swap backpressure guard.

Addendum §1-§4: swap은 여분의 RAM이 아니라 실패 신호로 취급한다. host/global
memory policy(vm.swappiness, .wslconfig 등)는 절대 변경하지 않고, swap이 실제로
발생하기 전에 pipeline 쪽에서 backpressure/abort 하도록 만든다.

판정은 absolute SwapUsed가 아니라 baseline 대비 swap_delta와 vmstat si/so를
중심으로 한다 (실행 시작 시점에 이미 swap이 조금 쓰이고 있을 수 있다).
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import psutil

_KST = ZoneInfo("Asia/Seoul")
_GIB = 2**30
_MIB = 2**20

STATUS_GREEN = "GREEN"
STATUS_YELLOW = "YELLOW"
STATUS_RED = "RED"
STATUS_EMERGENCY = "EMERGENCY"

# Addendum §3 memory safety envelope (15 GiB-class WSL 기준).
GREEN_MIN_AVAILABLE_GIB = 8.0
YELLOW_MIN_AVAILABLE_GIB = 6.0
RED_MIN_AVAILABLE_GIB = 5.0
EMERGENCY_MIN_AVAILABLE_GIB = 4.0
YELLOW_SWAP_DELTA_MIB = 128.0
RED_SWAP_DELTA_MIB = 512.0
EMERGENCY_SWAP_DELTA_MIB = 1024.0
RED_RSS_GIB = 6.0
RED_CONSECUTIVE_SWAP_IO_SAMPLES = 3


def read_swap_io_counters() -> tuple[int, int]:
    """/proc/vmstat에서 누적 swap-in/swap-out page 수를 읽는다 (vmstat si/so의 원천)."""
    counters = {"pswpin": 0, "pswpout": 0}
    try:
        for line in Path("/proc/vmstat").read_text(encoding="utf-8").splitlines():
            key, _, value = line.partition(" ")
            if key in counters:
                counters[key] = int(value)
    except OSError:
        pass
    return counters["pswpin"], counters["pswpout"]


def read_swappiness() -> int | None:
    """vm.swappiness를 읽기 전용으로 관측한다 (절대 수정하지 않는다)."""
    try:
        return int(Path("/proc/sys/vm/swappiness").read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None


@dataclass
class MemorySample:
    """한 시점의 memory/swap 관측치와 그에 따른 등급."""

    timestamp_kst: str
    mem_available_gib: float
    swap_used_gib: float
    swap_delta_mib: float
    rss_gib: float
    swap_in_pages: int
    swap_out_pages: int
    status: str
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp_kst": self.timestamp_kst,
            "mem_available_gib": self.mem_available_gib,
            "swap_used_gib": self.swap_used_gib,
            "swap_delta_mib": self.swap_delta_mib,
            "rss_gib": self.rss_gib,
            "swap_in_pages": self.swap_in_pages,
            "swap_out_pages": self.swap_out_pages,
            "status": self.status,
            "reasons": self.reasons,
        }


class MemoryGuardAbort(RuntimeError):
    """RED/EMERGENCY 상태에서 현재 candidate를 중단시키기 위한 신호."""


class MemoryGuard:
    """
    /**
     * @purpose Kiwi/o200k 실행 중 memory/swap 상태를 표본화하고 backpressure 등급을 판정한다.
     * @spec_ref Addendum §1-§4 memory safety envelope; ENG-OBS-001 §10
     * @param label 이 guard가 감시하는 실행 단위 이름 (benchmark candidate id 등)
     * @return MemoryGuard 인스턴스
     * @raises 없음 (판정만 하며 host 정책은 변경하지 않는다)
     * @validation baseline 대비 swap_delta와 si/so 증가를 함께 본다.
     * @artifact benchmark/full-run manifest의 MEMORY_GUARD 섹션
     */
    """

    def __init__(self, label: str = "run") -> None:
        self.label = label
        self.process = psutil.Process()
        self.swappiness = read_swappiness()
        swap = psutil.swap_memory()
        self.baseline_swap_used = swap.used
        self.baseline_swap_in, self.baseline_swap_out = read_swap_io_counters()
        self._last_swap_in, self._last_swap_out = self.baseline_swap_in, self.baseline_swap_out
        self._consecutive_swap_io = 0
        self.samples: list[MemorySample] = []
        self.min_mem_available_gib = float("inf")
        self.peak_swap_delta_mib = 0.0
        self.peak_rss_gib = 0.0

    def sample(self) -> MemorySample:
        """현재 상태를 한 번 표본화하고 등급을 매긴다."""
        vm = psutil.virtual_memory()
        swap = psutil.swap_memory()
        rss = self.process.memory_info().rss
        swap_in, swap_out = read_swap_io_counters()
        delta_in = max(0, swap_in - self._last_swap_in)
        delta_out = max(0, swap_out - self._last_swap_out)
        self._last_swap_in, self._last_swap_out = swap_in, swap_out

        mem_available_gib = vm.available / _GIB
        swap_delta_mib = max(0.0, (swap.used - self.baseline_swap_used) / _MIB)
        rss_gib = rss / _GIB

        self.min_mem_available_gib = min(self.min_mem_available_gib, mem_available_gib)
        self.peak_swap_delta_mib = max(self.peak_swap_delta_mib, swap_delta_mib)
        self.peak_rss_gib = max(self.peak_rss_gib, rss_gib)

        swap_io_active = (delta_in + delta_out) > 0
        self._consecutive_swap_io = self._consecutive_swap_io + 1 if swap_io_active else 0

        reasons: list[str] = []
        status = STATUS_GREEN
        if mem_available_gib < EMERGENCY_MIN_AVAILABLE_GIB:
            status, _ = STATUS_EMERGENCY, reasons.append(
                f"MemAvailable {mem_available_gib:.2f} GiB < {EMERGENCY_MIN_AVAILABLE_GIB}")
        if swap_delta_mib >= EMERGENCY_SWAP_DELTA_MIB:
            status, _ = STATUS_EMERGENCY, reasons.append(
                f"swap delta {swap_delta_mib:.0f} MiB >= {EMERGENCY_SWAP_DELTA_MIB}")
        if status != STATUS_EMERGENCY:
            if mem_available_gib < RED_MIN_AVAILABLE_GIB:
                status, _ = STATUS_RED, reasons.append(
                    f"MemAvailable {mem_available_gib:.2f} GiB < {RED_MIN_AVAILABLE_GIB}")
            if swap_delta_mib >= RED_SWAP_DELTA_MIB:
                status, _ = STATUS_RED, reasons.append(
                    f"swap delta {swap_delta_mib:.0f} MiB >= {RED_SWAP_DELTA_MIB}")
            if rss_gib > RED_RSS_GIB:
                status, _ = STATUS_RED, reasons.append(f"process RSS {rss_gib:.2f} GiB > {RED_RSS_GIB}")
            # si/so는 /proc/vmstat의 시스템 전역 카운터라 다른 프로세스의 배경 paging까지
            # 센다. 지속적인 swap io만으로 RED를 매기면 이 host에서는 건강한 실행도 상시
            # RED가 되어 등급이 신호 역할을 잃는다 (D-05 전집단 실측: 36표본 중 30개 RED,
            # 그때 MemAvailable 6.33 GiB / RSS 3.28 GiB / swap delta 19 MiB로 나머지 세
            # RED 규칙은 모두 미발동이었다).
            # 이 모듈 docstring이 정한 대로 baseline 대비 자기 footprint가 실제로 쌓일 때만
            # RED로 올린다. 그렇지 않은 지속 swap io는 아래 YELLOW 규칙이 그대로 기록한다.
            if (self._consecutive_swap_io >= RED_CONSECUTIVE_SWAP_IO_SAMPLES
                    and swap_delta_mib > YELLOW_SWAP_DELTA_MIB):
                status, _ = STATUS_RED, reasons.append(
                    f"swap io active for {self._consecutive_swap_io} consecutive samples "
                    f"with swap delta {swap_delta_mib:.0f} MiB > {YELLOW_SWAP_DELTA_MIB}")
        if status == STATUS_GREEN:
            if mem_available_gib < GREEN_MIN_AVAILABLE_GIB:
                status, _ = STATUS_YELLOW, reasons.append(
                    f"MemAvailable {mem_available_gib:.2f} GiB < {GREEN_MIN_AVAILABLE_GIB}")
            if swap_delta_mib > YELLOW_SWAP_DELTA_MIB:
                status, _ = STATUS_YELLOW, reasons.append(
                    f"swap delta {swap_delta_mib:.0f} MiB > {YELLOW_SWAP_DELTA_MIB}")
            if swap_io_active:
                status, _ = STATUS_YELLOW, reasons.append(
                    f"swap io observed (si={delta_in} pages, so={delta_out} pages)")

        sample = MemorySample(
            timestamp_kst=dt.datetime.now(tz=_KST).isoformat(timespec="seconds"),
            mem_available_gib=round(mem_available_gib, 3),
            swap_used_gib=round(swap.used / _GIB, 4),
            swap_delta_mib=round(swap_delta_mib, 2),
            rss_gib=round(rss_gib, 3),
            swap_in_pages=delta_in,
            swap_out_pages=delta_out,
            status=status,
            reasons=reasons,
        )
        self.samples.append(sample)
        return sample

    def check(self) -> MemorySample:
        """표본화 후 RED/EMERGENCY면 MemoryGuardAbort를 던진다 (무한 retry 금지)."""
        sample = self.sample()
        if sample.status in (STATUS_RED, STATUS_EMERGENCY):
            raise MemoryGuardAbort(f"[{self.label}] {sample.status}: {'; '.join(sample.reasons)}")
        return sample

    @property
    def worst_status(self) -> str:
        order = {STATUS_GREEN: 0, STATUS_YELLOW: 1, STATUS_RED: 2, STATUS_EMERGENCY: 3}
        return max((s.status for s in self.samples), key=lambda s: order[s], default=STATUS_GREEN)

    def summary(self) -> dict[str, Any]:
        """manifest에 실을 MEMORY_GUARD 요약을 만든다."""
        return {
            "label": self.label,
            "vm_swappiness": self.swappiness,
            "baseline_swap_used_mib": round(self.baseline_swap_used / _MIB, 2),
            "peak_swap_delta_mib": round(self.peak_swap_delta_mib, 2),
            "min_mem_available_gib": (
                round(self.min_mem_available_gib, 3) if self.samples else None
            ),
            "peak_rss_gib": round(self.peak_rss_gib, 3),
            "total_swap_in_pages": max(0, self._last_swap_in - self.baseline_swap_in),
            "total_swap_out_pages": max(0, self._last_swap_out - self.baseline_swap_out),
            "sample_count": len(self.samples),
            "worst_status": self.worst_status,
            "yellow_or_worse_samples": [s.to_dict() for s in self.samples if s.status != STATUS_GREEN],
        }


__all__ = [
    "MemoryGuard",
    "MemoryGuardAbort",
    "MemorySample",
    "STATUS_EMERGENCY",
    "STATUS_GREEN",
    "STATUS_RED",
    "STATUS_YELLOW",
    "read_swap_io_counters",
    "read_swappiness",
]
