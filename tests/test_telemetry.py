"""R1 periodic runtime telemetry 단위 테스트.

핵심 회귀: 시작/종료 2회 표본만으로는 R1을 만족하지 못한다.
"""

from __future__ import annotations

import json
import time

import pytest

from tokenization_premium.telemetry import (
    DEFAULT_INTERVAL_SEC,
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_INTERRUPTED,
    RuntimeTelemetry,
    TelemetrySample,
)

REQUIRED_FIELDS = (
    "timestamp_kst", "elapsed_sec", "rows_processed", "rows_per_second", "rss_gib",
    "mem_available_gib", "swap_used_mib", "swap_in_pages", "swap_out_pages",
    "stage", "status",
)


def test_sample_carries_every_field_required_by_the_decision() -> None:
    # RD-SSOT-CANONICAL-RETURN-01 §10 최소 항목.
    for field_name in REQUIRED_FIELDS:
        assert field_name in TelemetrySample.__dataclass_fields__, field_name


def test_periodic_sampling_produces_more_than_start_and_end() -> None:
    # R1의 본질: 실행 구간 내부에 표본이 존재해야 한다.
    with RuntimeTelemetry(run_id="T_PERIODIC", interval_sec=0.05, total=100) as tel:
        for _ in range(10):
            tel.update(10)
            time.sleep(0.03)
    assert tel.sample_count > 2, "start/end 2 samples는 R1 FAIL"
    assert tel.is_periodic()
    assert tel.summary()["r1_periodic_sampling"] is True


def test_two_sample_run_is_reported_as_not_periodic() -> None:
    # 명시적 negative: 주기 표본이 없으면 R1을 통과했다고 보고해서는 안 된다.
    tel = RuntimeTelemetry(run_id="T_TWO", interval_sec=3600.0)
    with tel:
        pass
    assert tel.sample_count == 2
    assert tel.is_periodic() is False
    assert tel.summary()["r1_periodic_sampling"] is False


def test_interior_samples_observe_progress_between_start_and_end() -> None:
    with RuntimeTelemetry(run_id="T_PROGRESS", interval_sec=0.05) as tel:
        for _ in range(8):
            tel.update(25)
            time.sleep(0.03)
    rows = [s.rows_processed for s in tel.samples]
    assert rows[0] == 0 and rows[-1] == 200
    interior = rows[1:-1]
    assert any(0 < r < 200 for r in interior), "중간 표본이 진행 상황을 포착하지 못했다"
    assert rows == sorted(rows), "rows_processed는 단조 증가해야 한다"


def test_stage_changes_are_recorded() -> None:
    with RuntimeTelemetry(run_id="T_STAGE", interval_sec=0.05) as tel:
        tel.set_stage("PILOT")
        time.sleep(0.12)
        tel.set_stage("FULL")
        time.sleep(0.12)
    stages = {s.stage for s in tel.samples}
    assert {"PILOT", "FULL"} <= stages


def test_final_status_completed_failed_interrupted() -> None:
    with RuntimeTelemetry(run_id="T_OK", interval_sec=0.05) as ok:
        time.sleep(0.06)
    assert ok.status == STATUS_COMPLETED
    assert ok.samples[-1].status == STATUS_COMPLETED

    failed = RuntimeTelemetry(run_id="T_FAIL", interval_sec=0.05)
    with pytest.raises(ValueError), failed:
        raise ValueError("boom")
    assert failed.status == STATUS_FAILED

    interrupted = RuntimeTelemetry(run_id="T_INT", interval_sec=0.05)
    with pytest.raises(KeyboardInterrupt), interrupted:
        raise KeyboardInterrupt
    assert interrupted.status == STATUS_INTERRUPTED


def test_summary_reports_true_extremes_not_just_endpoints() -> None:
    with RuntimeTelemetry(run_id="T_EXTREME", interval_sec=0.05) as tel:
        time.sleep(0.2)
    summary = tel.summary()
    mem = [s.mem_available_gib for s in tel.samples]
    rss = [s.rss_gib for s in tel.samples]
    assert summary["min_mem_available_gib"] == min(mem)
    assert summary["peak_rss_gib"] == max(rss)
    # 진짜 최소값은 양 끝점이 아니라 전체 표본에서 나와야 한다.
    assert summary["min_mem_available_gib"] <= min(mem[0], mem[-1])


def test_swap_counters_are_baseline_relative_and_nonnegative() -> None:
    with RuntimeTelemetry(run_id="T_SWAP", interval_sec=0.05) as tel:
        time.sleep(0.12)
    for sample in tel.samples:
        assert sample.swap_in_pages >= 0
        assert sample.swap_out_pages >= 0
        assert sample.swap_delta_mib >= 0
    summary = tel.summary()
    assert summary["vm_swappiness"] is None or isinstance(summary["vm_swappiness"], int)


def test_environment_override_sets_interval() -> None:
    import os

    os.environ["TOKENIZATION_PREMIUM_PROGRESS_INTERVAL_SEC"] = "0.02"
    try:
        tel = RuntimeTelemetry(run_id="T_ENV")
        assert tel.interval_sec == pytest.approx(0.02)
    finally:
        del os.environ["TOKENIZATION_PREMIUM_PROGRESS_INTERVAL_SEC"]
    assert RuntimeTelemetry(run_id="T_DEFAULT").interval_sec == DEFAULT_INTERVAL_SEC


def test_summary_is_json_serialisable_and_carries_no_text(tmp_path) -> None:
    with RuntimeTelemetry(run_id="T_JSON", interval_sec=0.05) as tel:
        tel.update(5)
        time.sleep(0.08)
    path = tel.write(tmp_path / "telemetry.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["sample_count"] == tel.sample_count
    assert payload["final_status"] == STATUS_COMPLETED
    # 원문/PII가 실릴 자리가 없어야 한다.
    text = path.read_text(encoding="utf-8")
    import re

    assert not re.search(r"[가-힣]{4,}", text)


def test_thread_does_not_mutate_research_counters() -> None:
    # heartbeat thread는 카운터를 읽기만 한다: update로 넣은 값만 관측돼야 한다.
    with RuntimeTelemetry(run_id="T_READONLY", interval_sec=0.05) as tel:
        tel.update(7)
        time.sleep(0.15)
    assert tel.rows_processed == 7
    assert tel.samples[-1].rows_processed == 7
