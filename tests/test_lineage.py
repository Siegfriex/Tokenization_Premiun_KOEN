"""Canonical artifact lineage의 fail-closed 동작 단위 테스트.

pin된 값의 출처는 Claude-B의 독립 forensic 판정(441d580)이다.
"""

from __future__ import annotations

import json

import pytest

from tokenization_premium.hashing import sha256_file
from tokenization_premium.lineage import (
    ADJUDICATION_COMMIT,
    CANONICAL_ARTIFACTS,
    CANONICAL_COHORT_N,
    CANONICAL_PAIR_SET_MD5,
    HISTORICAL_ARTIFACTS,
    CanonicalArtifactIdentityMismatch,
    assert_canonical_artifact,
    describe_historical,
)
from tokenization_premium.paths import PROJECT_ROOT


def test_canonical_registry_pins_b_adjudicated_values() -> None:
    assert ADJUDICATION_COMMIT == "441d5802bfebe178fd220d08b653c60dfad17faf"
    assert CANONICAL_PAIR_SET_MD5 == "d9660d654ee449e4d0c23a0070225274"
    assert CANONICAL_COHORT_N == 3_835_988


def test_cohort_artifacts_share_the_final_row_count() -> None:
    for name in ("REP_FEATURES_v002", "MORPH_FEATURES_KIWI_v001", "TOKEN_O200K_BASE_v001"):
        assert CANONICAL_ARTIFACTS[name].row_count == CANONICAL_COHORT_N


def test_column_counts_match_the_adjudicated_physical_schemas() -> None:
    # Claude-B §2: REP 49 / MORPH 19 / TOKEN 28. 28-vs-29는 REPORT_TYPO_ONLY로 종결됐다.
    assert CANONICAL_ARTIFACTS["REP_FEATURES_v002"].column_count == 49
    assert CANONICAL_ARTIFACTS["MORPH_FEATURES_KIWI_v001"].column_count == 19
    assert CANONICAL_ARTIFACTS["TOKEN_O200K_BASE_v001"].column_count == 28


def test_canonical_names_follow_ssot_38() -> None:
    assert CANONICAL_ARTIFACTS["MORPH_FEATURES_KIWI_v001"].relative_path.endswith(
        "MORPH_FEATURES_KIWI_v001.parquet")
    assert CANONICAL_ARTIFACTS["TOKEN_O200K_BASE_v001"].relative_path.endswith(
        "TOKEN_O200K_BASE_v001.parquet")


def test_unknown_artifact_fails_closed() -> None:
    with pytest.raises(CanonicalArtifactIdentityMismatch):
        assert_canonical_artifact("REP_FEATURES_v001")   # historical, not canonical
    with pytest.raises(CanonicalArtifactIdentityMismatch):
        assert_canonical_artifact("does_not_exist")


def test_missing_artifact_raises_rather_than_falling_back(tmp_path, monkeypatch) -> None:
    import tokenization_premium.lineage as lineage

    absent = lineage.CanonicalArtifact(
        name="ABSENT", relative_path="data/registry/__absent__.parquet",
        sha256="0" * 64, row_count=1, column_count=1, id_column="pair_id",
        gate="Gx", manifest="none")
    monkeypatch.setitem(lineage.CANONICAL_ARTIFACTS, "ABSENT", absent)
    with pytest.raises(CanonicalArtifactIdentityMismatch, match="CANONICAL_ARTIFACT_IDENTITY_MISMATCH"):
        assert_canonical_artifact("ABSENT")


def test_historical_artifacts_are_marked_not_current_evidence() -> None:
    for name in HISTORICAL_ARTIFACTS:
        record = describe_historical(name)
        assert record["NOT_CURRENT_EVIDENCE"] == "true"
        assert "SUPERSEDED" in record["status"]
        assert record["superseded_by"] in CANONICAL_ARTIFACTS


def test_superseded_pilot_is_not_reachable_as_canonical() -> None:
    # M1-M5 결함 하에서 만들어진 pilot이 canonical 경로로 소비될 수 없어야 한다.
    assert "MORPH_FEATURES_PILOT_v001" not in CANONICAL_ARTIFACTS
    assert HISTORICAL_ARTIFACTS["MORPH_FEATURES_PILOT_v001"]["status"] == (
        "SUPERSEDED_BY_CONFORMANCE_DEFECT")


# RD-G5-ENTRY-GOVERNANCE-CLOSEOUT-01 §3.5 — frozen RQ1 evidence-of-record.
# 04 result JSON은 502bc12에서 한 번 쓰인 뒤 변경된 적이 없다. closeout이 기록한 SHA가
# 실제 파일과 어긋난 채 동결됐던 사고를 재발시키지 않으려고, 기록값과 물리 파일을
# CI에서 대조한다. artifact를 읽지 않으므로 데이터 없는 환경에서도 돈다.
RQ1_RESULT_JSON = "ssot_nb01/04_NB08_RQ1_RESULTS_v001.json"
RQ1_CLOSEOUT_JSON = "ssot_nb01/06_NB08_RQ1_SSOT_CLOSEOUT_v001.json"
RQ1_CLOSEOUT_MD = "ssot_nb01/07_NB08_RQ1_CANONICAL_CLOSEOUT.md"
RQ1_SUPERSEDED_RESULT_SHA256 = (
    "5daaa164061a0bbeda39ae823ce000a9e986c26baf9cc27c2f2c9479f0993562")


def _recorded_rq1_result_sha256() -> str:
    closeout = json.loads((PROJECT_ROOT / RQ1_CLOSEOUT_JSON).read_text(encoding="utf-8"))
    return closeout["evidence_of_record"]["primary_result_json_sha256"]


def test_rq1_evidence_of_record_sha_matches_the_physical_result() -> None:
    recorded = _recorded_rq1_result_sha256()
    actual = sha256_file(PROJECT_ROOT / RQ1_RESULT_JSON)
    assert recorded == actual, (
        "RQ1_EVIDENCE_OF_RECORD_SHA_MISMATCH: "
        f"{RQ1_CLOSEOUT_JSON} records {recorded} for {RQ1_RESULT_JSON}, "
        f"which actually hashes to {actual}")


def test_rq1_canonical_closeout_prose_quotes_the_same_sha() -> None:
    recorded = _recorded_rq1_result_sha256()
    prose = (PROJECT_ROOT / RQ1_CLOSEOUT_MD).read_text(encoding="utf-8")
    assert recorded in prose, (
        f"{RQ1_CLOSEOUT_MD} must quote the evidence-of-record SHA {recorded}")


def test_superseded_rq1_result_sha_is_not_reachable_in_the_frozen_record() -> None:
    for name in (RQ1_RESULT_JSON, RQ1_CLOSEOUT_JSON, RQ1_CLOSEOUT_MD):
        text = (PROJECT_ROOT / name).read_text(encoding="utf-8")
        assert RQ1_SUPERSEDED_RESULT_SHA256 not in text, (
            f"{name} still carries the superseded RQ1 result SHA")
