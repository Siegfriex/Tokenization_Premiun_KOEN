"""Canonical artifact lineage의 fail-closed 동작 단위 테스트.

pin된 값의 출처는 Claude-B의 독립 forensic 판정(441d580)이다.
"""

from __future__ import annotations

import pytest

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
