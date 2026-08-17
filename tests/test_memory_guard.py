"""Memory guard 등급 판정 단위 테스트.

핵심 회귀: si/so는 시스템 전역 카운터다. 다른 프로세스의 배경 paging만으로 RED가 찍히면
등급이 신호 역할을 잃는다 (D-05 전집단 실행에서 36표본 중 30개가 그렇게 RED였다).
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

import tokenization_premium.memory_guard as guard_module
from tokenization_premium.memory_guard import (
    RED_CONSECUTIVE_SWAP_IO_SAMPLES,
    STATUS_GREEN,
    STATUS_RED,
    STATUS_YELLOW,
    YELLOW_SWAP_DELTA_MIB,
    MemoryGuard,
)

_GIB = 2**30
_MIB = 2**20


@pytest.fixture
def fake_host(monkeypatch):
    """MemAvailable / swap / RSS / vmstat si·so를 제어하는 가짜 host."""
    state = {"available_gib": 9.0, "swap_used_mib": 1900.0, "rss_gib": 3.0,
             "swap_in": 0, "swap_out": 0}

    monkeypatch.setattr(guard_module.psutil, "virtual_memory",
                        lambda: SimpleNamespace(available=state["available_gib"] * _GIB))
    monkeypatch.setattr(guard_module.psutil, "swap_memory",
                        lambda: SimpleNamespace(used=state["swap_used_mib"] * _MIB))
    monkeypatch.setattr(guard_module.psutil, "Process",
                        lambda *a, **k: SimpleNamespace(
                            memory_info=lambda: SimpleNamespace(rss=state["rss_gib"] * _GIB)))
    monkeypatch.setattr(guard_module, "read_swap_io_counters",
                        lambda: (state["swap_in"], state["swap_out"]))
    return state


def test_healthy_run_with_ambient_background_paging_is_not_red(fake_host) -> None:
    """D-05 전집단 실측 재현: 340초 동안 45 MiB 배경 paging, 나머지 지표는 전부 여유."""
    fake_host.update({"available_gib": 6.33, "rss_gib": 3.28})
    guard = MemoryGuard("ambient")

    statuses = []
    for _ in range(12):
        fake_host["swap_in"] += 130          # 표본당 약 0.5 MiB — 배경 수준
        fake_host["swap_out"] += 200
        fake_host["swap_used_mib"] += 1.5    # baseline 대비 누적 19 MiB 수준
        statuses.append(guard.sample().status)

    assert STATUS_RED not in statuses, "배경 paging만으로 RED가 되면 등급이 신호를 잃는다"
    assert statuses[-1] == STATUS_YELLOW, "지속 swap io는 YELLOW로 기록되어야 한다"
    assert guard.worst_status == STATUS_YELLOW


def test_real_sustained_thrash_still_escalates_to_red(fake_host) -> None:
    """자기 footprint가 실제로 쌓이는 지속 swap io는 여전히 RED다."""
    fake_host.update({"available_gib": 6.5, "rss_gib": 3.0})
    guard = MemoryGuard("thrash")

    statuses = []
    for _ in range(RED_CONSECUTIVE_SWAP_IO_SAMPLES + 2):
        fake_host["swap_in"] += 20_000
        fake_host["swap_out"] += 30_000
        fake_host["swap_used_mib"] += 200    # baseline 대비 빠르게 누적
        statuses.append(guard.sample().status)

    assert STATUS_RED in statuses
    assert guard.worst_status == STATUS_RED


def test_swap_io_gate_requires_both_persistence_and_growing_footprint(fake_host) -> None:
    """두 조건 중 하나만으로는 RED가 되지 않는다."""
    # (a) footprint는 커지지만 swap io가 끊긴 경우 -> RED_SWAP_DELTA 규칙 전까지는 YELLOW
    fake_host.update({"available_gib": 7.0, "swap_used_mib": 1000.0})
    guard = MemoryGuard("delta-only")
    fake_host["swap_used_mib"] += YELLOW_SWAP_DELTA_MIB + 50   # si/so 증가 없음
    assert guard.sample().status == STATUS_YELLOW

    # (b) swap io는 지속되지만 footprint가 그대로인 경우
    fake_host.update({"available_gib": 7.0, "swap_used_mib": 1000.0})
    guard = MemoryGuard("io-only")
    for _ in range(RED_CONSECUTIVE_SWAP_IO_SAMPLES + 3):
        fake_host["swap_in"] += 50
        sample = guard.sample()
    assert sample.status == STATUS_YELLOW


def test_memory_exhaustion_rules_are_unchanged(fake_host) -> None:
    """swap io 규칙을 조정해도 메모리 고갈 판정은 그대로여야 한다."""
    fake_host.update({"available_gib": 4.31, "rss_gib": 3.0})   # 실제 abort를 유발했던 값
    guard = MemoryGuard("low-mem")
    sample = guard.sample()
    assert sample.status == STATUS_RED
    assert any("MemAvailable" in reason for reason in sample.reasons)

    fake_host["available_gib"] = 3.5
    assert guard.sample().status == "EMERGENCY"


def test_quiet_healthy_host_stays_green(fake_host) -> None:
    fake_host.update({"available_gib": 12.0, "rss_gib": 1.0})
    guard = MemoryGuard("quiet")
    assert guard.sample().status == STATUS_GREEN
