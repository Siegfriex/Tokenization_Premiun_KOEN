"""PRE-NB10 leakage grouping — fail-closed unit tests.

의도: LR-01 검사가 실제로 위반을 잡는지 증명한다. 통과만 확인하는 테스트는 증거가 아니므로
각 검사마다 위반 케이스를 만들어 raise하는지 확인한다. artifact를 읽지 않으므로 데이터가 없는
환경에서도 돌아간다.

계약: ssot_nb10/01_PRE_NB10_GROUPING_CONTRACT_v001.md
"""

from __future__ import annotations

import json

import pytest

from tokenization_premium.leakage import (
    HOLDOUT,
    TRAIN,
    LeakageBoundaryViolation,
    assert_assignment_complete,
    assert_no_crossing,
    assert_share_within_band,
    assign_all,
    assign_split,
    build_groups,
    canonical_group_ids,
    crossing_keys,
    group_sizes,
    holdout_share,
    normalise_text,
    text_key,
)
from tokenization_premium.paths import PROJECT_ROOT

SALT = "PRE_NB10_TEST_SALT"

# contract §3.1 — deliberately inside the SSOT §23.2 band, not at its edge
TARGET_HOLDOUT_SHARE = 0.19


# --- normalisation ----------------------------------------------------------------

def test_normalisation_absorbs_case_punctuation_and_whitespace() -> None:
    assert normalise_text("Hello, World!") == normalise_text("hello world")
    assert normalise_text("안녕하세요, 반갑습니다.") == normalise_text("안녕하세요 반갑습니다")
    assert normalise_text("A  B\tC\n") == "abc"


def test_normalisation_does_not_collapse_different_content() -> None:
    assert normalise_text("cat") != normalise_text("cats")
    assert normalise_text("한국어") != normalise_text("한국")


def test_tier1_and_tier2_keys_differ_where_normalisation_bites() -> None:
    a, b = "Hello, World!", "hello world"
    assert text_key(a, normalised=False) != text_key(b, normalised=False)
    assert text_key(a, normalised=True) == text_key(b, normalised=True)


# --- grouping ---------------------------------------------------------------------

def test_shared_ko_side_puts_pairs_in_one_group() -> None:
    rows = [("p1", "ko_A", "en_1"), ("p2", "ko_A", "en_2")]
    g = build_groups(rows)
    assert g["p1"] == g["p2"]


def test_shared_en_side_puts_pairs_in_one_group() -> None:
    rows = [("p1", "ko_1", "en_A"), ("p2", "ko_2", "en_A")]
    g = build_groups(rows)
    assert g["p1"] == g["p2"]


def test_grouping_is_transitive_across_sides() -> None:
    # p1~p2 through KO, p2~p3 through EN -> all three must be one family
    rows = [("p1", "ko_A", "en_1"), ("p2", "ko_A", "en_B"), ("p3", "ko_C", "en_B")]
    g = build_groups(rows)
    assert g["p1"] == g["p2"] == g["p3"]


def test_unrelated_pairs_stay_singleton() -> None:
    rows = [("p1", "ko_1", "en_1"), ("p2", "ko_2", "en_2")]
    g = build_groups(rows)
    assert g["p1"] != g["p2"]
    assert set(group_sizes(g).values()) == {1}


def test_canonical_group_id_is_order_independent() -> None:
    rows = [("p1", "ko_A", "en_1"), ("p2", "ko_A", "en_2"), ("p3", "ko_B", "en_3")]
    forward = canonical_group_ids(build_groups(rows))
    reverse = canonical_group_ids(build_groups(list(reversed(rows))))
    assert forward == reverse


# --- assignment -------------------------------------------------------------------

def test_assignment_is_deterministic() -> None:
    assert assign_split("g1", SALT, 0.2) == assign_split("g1", SALT, 0.2)


def test_assignment_depends_on_the_salt() -> None:
    """A different salt must be able to move a group; otherwise the salt is decorative."""
    labels = {assign_split("g1", f"salt{i}", 0.5) for i in range(40)}
    assert labels == {TRAIN, HOLDOUT}


def test_a_group_is_never_split() -> None:
    rows = [("p1", "ko_A", "en_1"), ("p2", "ko_A", "en_2"), ("p3", "ko_A", "en_3")]
    groups = canonical_group_ids(build_groups(rows))
    assignment = assign_all(groups, SALT, 0.2)
    assert len(set(assignment.values())) == 1


def test_holdout_share_lands_near_target_over_many_groups() -> None:
    groups = {f"p{i}": f"g{i}" for i in range(20_000)}
    share = holdout_share(assign_all(groups, SALT, 0.20))
    assert 0.19 < share < 0.21, share


def test_invalid_holdout_share_is_rejected() -> None:
    for bad in (0.0, 1.0, -0.1, 1.5):
        with pytest.raises(ValueError):
            assign_split("g1", SALT, bad)


# --- LR-01 checks: each must FAIL on a real violation ------------------------------

def test_crossing_keys_detects_a_boundary_violation() -> None:
    assignment = {"p1": TRAIN, "p2": HOLDOUT}
    key_of = {"p1": "shared_ko", "p2": "shared_ko"}
    assert crossing_keys(assignment, key_of) == ["shared_ko"]


def test_crossing_keys_is_silent_when_clean() -> None:
    assignment = {"p1": TRAIN, "p2": TRAIN, "p3": HOLDOUT}
    key_of = {"p1": "k1", "p2": "k1", "p3": "k2"}
    assert crossing_keys(assignment, key_of) == []


def test_assert_no_crossing_raises_on_violation() -> None:
    assignment = {"p1": TRAIN, "p2": HOLDOUT}
    with pytest.raises(LeakageBoundaryViolation, match="LR01_VIOLATION"):
        assert_no_crossing(assignment, {"ko_hash": {"p1": "kA", "p2": "kA"}})


def test_assert_no_crossing_returns_zero_counts_when_clean() -> None:
    assignment = {"p1": TRAIN, "p2": TRAIN, "p3": HOLDOUT}
    counts = assert_no_crossing(
        assignment,
        {
            "ko_hash": {"p1": "kA", "p2": "kA", "p3": "kB"},
            "en_hash": {"p1": "eA", "p2": "eB", "p3": "eC"},
        },
    )
    assert counts == {"ko_hash": 0, "en_hash": 0}


def test_end_to_end_grouped_assignment_has_no_crossing() -> None:
    rows = [
        ("p1", "koA", "en1"), ("p2", "koA", "en2"),   # linked by KO
        ("p3", "koB", "en3"), ("p4", "koC", "en3"),   # linked by EN
        ("p5", "koD", "en5"),                          # singleton
    ]
    groups = canonical_group_ids(build_groups(rows))
    assignment = assign_all(groups, SALT, 0.20)
    counts = assert_no_crossing(
        assignment,
        {
            "group_id": groups,
            "ko_hash": {p: k for p, k, _ in rows},
            "en_hash": {p: e for p, _, e in rows},
        },
    )
    assert counts == {"group_id": 0, "ko_hash": 0, "en_hash": 0}


def test_ungrouped_assignment_leaks_which_is_why_grouping_exists() -> None:
    """Assigning by pair_id instead of group_id must be caught by the same check."""
    rows = [("p1", "koA", "en1"), ("p2", "koA", "en2")]
    leaky = {"p1": TRAIN, "p2": HOLDOUT}          # same KO text, opposite sides
    with pytest.raises(LeakageBoundaryViolation):
        assert_no_crossing(leaky, {"ko_hash": {p: k for p, k, _ in rows}})


# --- completeness and band --------------------------------------------------------

def test_incomplete_assignment_is_rejected() -> None:
    with pytest.raises(LeakageBoundaryViolation, match="ASSIGNMENT_INCOMPLETE"):
        assert_assignment_complete({"p1": TRAIN}, ["p1", "p2"])


def test_unexpected_pair_is_rejected() -> None:
    with pytest.raises(LeakageBoundaryViolation, match="ASSIGNMENT_INCOMPLETE"):
        assert_assignment_complete({"p1": TRAIN, "pX": TRAIN}, ["p1"])


def test_unknown_split_label_is_rejected() -> None:
    with pytest.raises(LeakageBoundaryViolation, match="UNKNOWN_SPLIT_LABEL"):
        assert_assignment_complete({"p1": "VALIDATION"}, ["p1"])


def test_complete_assignment_passes() -> None:
    assert_assignment_complete({"p1": TRAIN, "p2": HOLDOUT}, ["p1", "p2"])


def test_share_outside_the_ssot_band_is_rejected() -> None:
    with pytest.raises(LeakageBoundaryViolation, match="HOLDOUT_SHARE_OUT_OF_BAND"):
        assert_share_within_band({"p1": HOLDOUT, "p2": HOLDOUT, "p3": TRAIN})


def test_share_inside_the_ssot_band_passes() -> None:
    groups = {f"p{i}": f"g{i}" for i in range(20_000)}
    assert 0.15 <= assert_share_within_band(assign_all(groups, SALT, TARGET_HOLDOUT_SHARE)) <= 0.20


def test_targeting_the_band_edge_is_unsafe_and_the_contract_does_not_do_it() -> None:
    """Realised share fluctuates about the target, so targeting 0.20 exactly overshoots half the
    time. On this cohort the fluctuation is dominated by the 37,849-row giant component, which
    moves the share by about +0.8pp when it lands in holdout. The contract therefore targets
    TARGET_HOLDOUT_SHARE, not the band edge."""
    assert TARGET_HOLDOUT_SHARE < 0.20
    giant_share = 37_849 / 3_835_988
    worst = TARGET_HOLDOUT_SHARE + giant_share * (1 - TARGET_HOLDOUT_SHARE)
    best = TARGET_HOLDOUT_SHARE - giant_share * TARGET_HOLDOUT_SHARE
    assert worst <= 0.20, worst
    assert best >= 0.15, best
    # and the edge target would in fact violate the band
    assert 0.20 + giant_share * 0.80 > 0.20


# --- schema -----------------------------------------------------------------------

def test_split_manifest_schema_is_present_and_wellformed() -> None:
    path = PROJECT_ROOT / "ssot_nb10" / "02_SPLIT_MANIFEST_SCHEMA_v001.json"
    schema = json.loads(path.read_text(encoding="utf-8"))
    assert schema["$id"] == "PRE_NB10_SPLIT_MANIFEST_SCHEMA_v001"
    for block in ("grouping", "split", "lr01_checks", "source_ood", "claim_restrictions"):
        assert block in schema["required"], block
        assert block in schema["properties"], block


def test_schema_pins_the_split_unit_and_forbids_outcome_use() -> None:
    path = PROJECT_ROOT / "ssot_nb10" / "02_SPLIT_MANIFEST_SCHEMA_v001.json"
    split = json.loads(path.read_text(encoding="utf-8"))["properties"]["split"]["properties"]
    assert split["unit_of_assignment"]["const"] == "group_id"
    assert split["outcome_used_in_assignment"]["const"] is False
    assert split["target_holdout_share"]["minimum"] == 0.15
    assert split["target_holdout_share"]["maximum"] == 0.20


def test_schema_requires_every_lr01_check_to_be_zero() -> None:
    path = PROJECT_ROOT / "ssot_nb10" / "02_SPLIT_MANIFEST_SCHEMA_v001.json"
    checks = json.loads(path.read_text(encoding="utf-8"))["properties"]["lr01_checks"]["properties"]
    for name in (
        "group_id_crossings",
        "normalised_ko_hash_crossings",
        "normalised_en_hash_crossings",
        "exact_ko_hash_crossings",
        "exact_en_hash_crossings",
        "duplicate_group_id_crossings",
        "analysis_representative_crossings",
    ):
        assert checks[name]["const"] == 0, name
    assert checks["status"]["const"] == "LR01_PASS"


def test_schema_forbids_predictive_results_in_this_stage() -> None:
    path = PROJECT_ROOT / "ssot_nb10" / "02_SPLIT_MANIFEST_SCHEMA_v001.json"
    cr = json.loads(path.read_text(encoding="utf-8"))["properties"]["claim_restrictions"]["properties"]
    assert cr["predictive_model_fitted"]["const"] is False
    assert cr["test_set_result_produced"]["const"] is False
    assert cr["holdout_consumed"]["const"] is False
    assert cr["raw_text_persisted"]["const"] is False


def test_schema_separates_execution_parent_from_code_of_record() -> None:
    """The NB09 code_sha ambiguity must not recur: both commits are required, separately."""
    schema = json.loads(
        (PROJECT_ROOT / "ssot_nb10" / "02_SPLIT_MANIFEST_SCHEMA_v001.json").read_text(encoding="utf-8")
    )
    assert "execution_parent_sha" in schema["required"]
    assert "grouping_code_sha" in schema["required"]
    assert "artifact_record_commit" in schema["required"]
