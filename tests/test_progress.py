"""ENG-OBS-001 progress/heartbeat의 synthetic engineering contract를 검증한다."""

from __future__ import annotations

import datetime as dt
import json
import subprocess
import time
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

import tokenization_premium.progress as progress_module
from tokenization_premium.paths import PROJECT_ROOT
from tokenization_premium.progress import (
    PROGRESS_DIR_ENV,
    PROGRESS_INTERVAL_ENV,
    ProgressHeartbeat,
    classify_liveness,
    snapshot_liveness,
)


def _jsonl_rows(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_known_total_percent_eta_and_memory_are_observed(tmp_path: Path) -> None:
    with ProgressHeartbeat("known-total", "02", "LID_SCAN", total=10, interval_sec=0.05, progress_dir=tmp_path) as heartbeat:
        heartbeat.update(2, accepted_rows=2)
        snapshot = heartbeat.snapshot()
        assert snapshot["processed"] == 2
        assert snapshot["total"] == 10
        assert snapshot["percent"] == 20.0
        assert snapshot["rate_per_sec"] is not None and snapshot["rate_per_sec"] > 0
        assert snapshot["eta_sec"] is not None and snapshot["eta_sec"] >= 0
        assert snapshot["rss_gib"] >= 0
        assert snapshot["mem_available_gib"] >= 0


def test_unknown_total_never_fabricates_percent_or_eta(tmp_path: Path) -> None:
    with ProgressHeartbeat("unknown-total", "03", "TOKENIZER_BATCH", interval_sec=0.05, progress_dir=tmp_path) as heartbeat:
        heartbeat.update(3)
        snapshot = heartbeat.snapshot()
        assert snapshot["processed"] == 3
        assert snapshot["total"] is None
        assert snapshot["percent"] is None
        assert snapshot["eta_sec"] is None


def test_heartbeat_continues_without_main_thread_updates(tmp_path: Path) -> None:
    with ProgressHeartbeat("blocked-main", "04", "DUCKDB_SQL", total=5, interval_sec=0.05, progress_dir=tmp_path) as heartbeat:
        time.sleep(0.13)
        rows_during_run = _jsonl_rows(heartbeat.jsonl_path)
        assert len(rows_during_run) >= 3
        assert {row["processed"] for row in rows_during_run} == {0}


def test_checkpoint_jsonl_atomic_latest_and_completed_final(tmp_path: Path) -> None:
    heartbeat = ProgressHeartbeat("persistence", "02", "QC", total=4, interval_sec=0.05, progress_dir=tmp_path)
    with heartbeat:
        heartbeat.update(1)
        heartbeat.checkpoint("BATCH_1", valid_rows=1)
        heartbeat.checkpoint("BATCH_2", valid_rows=2)
    latest = json.loads(heartbeat.latest_path.read_text(encoding="utf-8"))
    rows = _jsonl_rows(heartbeat.jsonl_path)
    assert latest["status"] == "COMPLETED"
    assert latest["checkpoint"] == "BATCH_2"
    assert len(rows) >= 4
    assert heartbeat.pid_path.read_text(encoding="utf-8").strip().isdigit()
    assert list(heartbeat.run_dir.glob(".latest.json.*.tmp")) == []


def test_context_exception_persists_failed_and_propagates(tmp_path: Path) -> None:
    heartbeat = ProgressHeartbeat("failed-run", "02", "SLOW_API", interval_sec=0.05, progress_dir=tmp_path)
    with pytest.raises(RuntimeError, match="synthetic failure"), heartbeat:
        raise RuntimeError("synthetic failure")
    latest = json.loads(heartbeat.latest_path.read_text(encoding="utf-8"))
    assert latest["status"] == "FAILED"


def test_worktree_root_and_environment_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(PROGRESS_INTERVAL_ENV, "0.05")
    monkeypatch.setenv(PROGRESS_DIR_ENV, ".runtime/progress-test-relative")
    heartbeat = ProgressHeartbeat("root-resolution", "01", "SYNTHETIC")
    expected_sha = subprocess.run(
        ["git", "-C", str(PROJECT_ROOT), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert heartbeat.project_root == PROJECT_ROOT
    assert heartbeat.progress_root == (PROJECT_ROOT / ".runtime/progress-test-relative").resolve()
    assert heartbeat.interval_sec == 0.05
    assert heartbeat.snapshot()["git_sha"] == expected_sha


def test_default_runtime_configuration_and_tqdm_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(PROGRESS_INTERVAL_ENV, raising=False)
    monkeypatch.delenv(PROGRESS_DIR_ENV, raising=False)
    heartbeat = ProgressHeartbeat("default-config", "01", "SYNTHETIC")
    captured: dict[str, object] = {}
    sentinel = object()

    def fake_tqdm(*, iterable: object | None = None, **kwargs: object) -> object:
        captured["iterable"] = iterable
        captured.update(kwargs)
        return sentinel

    monkeypatch.setattr(progress_module, "tqdm", fake_tqdm)
    assert progress_module.progress_tqdm([1, 2]) is sentinel
    assert heartbeat.interval_sec == 10.0
    assert heartbeat.progress_root == (PROJECT_ROOT / ".runtime/progress").resolve()
    assert captured == {"iterable": [1, 2], "mininterval": 10.0, "dynamic_ncols": True}


def test_stage_reset_metrics_are_numeric_and_raw_text_fields_are_rejected(tmp_path: Path) -> None:
    with ProgressHeartbeat("privacy", "02", "FIRST", total=3, interval_sec=0.05, progress_dir=tmp_path) as heartbeat:
        heartbeat.update(2, error_count=1)
        heartbeat.set_stage("SECOND", total=None)
        snapshot = heartbeat.snapshot()
        assert snapshot["stage"] == "SECOND"
        assert snapshot["processed"] == 0
        assert snapshot["total"] is None
        with pytest.raises(ValueError, match="raw-text"):
            heartbeat.set_metric("ko_text_raw", 1)
        with pytest.raises(TypeError, match="finite numeric"):
            heartbeat.set_metric("safe_metric", "secret sentence")  # type: ignore[arg-type]
    persisted = heartbeat.latest_path.read_text(encoding="utf-8")
    assert "secret sentence" not in persisted
    assert "ko_text_raw" not in persisted


@pytest.mark.parametrize(
    ("age_sec", "process_alive", "expected"),
    [(20, True, "HEALTHY"), (25, True, "LAGGING"), (45, True, "WARNING"), (61, True, "STALLED"), (0, False, "INTERRUPTED")],
)
def test_liveness_thresholds(age_sec: float, process_alive: bool, expected: str) -> None:
    assert classify_liveness(age_sec, process_alive) == expected


def test_snapshot_liveness_uses_kst_timestamp() -> None:
    timestamp = dt.datetime(2026, 8, 16, 17, 0, tzinfo=ZoneInfo("Asia/Seoul"))
    snapshot = {"timestamp": timestamp.isoformat(), "pid": 12345}
    assert snapshot_liveness(snapshot, now=timestamp + dt.timedelta(seconds=21), process_alive=True) == "LAGGING"
