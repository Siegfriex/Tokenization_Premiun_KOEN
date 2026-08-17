"""D-03 한국어 형태소 측정(NB04) 단위 테스트; synthetic 입력만 사용한다.

Conformance regression scope: RD-20260817-D02D03-CONFORMANCE-01 (M1-M5).
"""

from __future__ import annotations

import math
from types import SimpleNamespace

import pyarrow as pa
import pytest

from tokenization_premium.morphology import (
    MORPHOLOGY_CONFIG,
    MORPHOLOGY_CONFIG_SHA256,
    WARNING_NONE,
    WARNING_ZERO_MORPHEME,
    MorphologyHardInvalidError,
    MorphologyInputError,
    analyze_batch,
    base_tag,
    build_record,
    classify_tag,
    compare_feature_dicts,
    features_from_morphs,
    get_kiwi,
    morph_features_schema,
    morph_measurement_id,
    morphology_features,
)


def morph(form: str, tag: str) -> SimpleNamespace:
    """Kiwi Token의 form/tag 속성만 흉내내는 경량 stub."""
    return SimpleNamespace(form=form, tag=tag)


# --- M2: base tag normalization -------------------------------------------------------


def test_base_tag_strips_irregular_suffix() -> None:
    assert base_tag("XSA") == "XSA"
    assert base_tag("XSA-I") == "XSA"
    assert base_tag("XSA-R") == "XSA"
    assert base_tag("VA-I") == "VA"
    assert base_tag("JKS") == "JKS"


def test_irregular_derivational_affix_is_classified() -> None:
    # M2 회귀: exact-match 매핑은 XSA-I를 놓쳤다.
    for tag in ("XSN", "XSV", "XSA", "XSA-I", "XSA-R", "XSV-I", "XSN-R"):
        assert classify_tag(tag) == "deriv_affix", tag


def test_particle_and_ending_classification() -> None:
    for tag in ("JKS", "JKO", "JKB", "JX", "JC"):
        assert classify_tag(tag) == "particle"
    for tag in ("EF", "EC", "EP", "ETN", "ETM"):
        assert classify_tag(tag) == "ending"


def test_non_function_tags_are_unclassified() -> None:
    for tag in ("NNG", "NNP", "VV", "VA", "VA-I", "MAG", "SF", "SL", "SN", "W_URL"):
        assert classify_tag(tag) is None, tag


def test_base_normalization_does_not_change_particle_or_ending_membership() -> None:
    # J*/E* 판정은 base 정규화 전후로 동일해야 한다 (기존 count 안정성 보장).
    for tag in ("JKS", "JX", "EF", "EC", "ETN", "JKS-X", "EF-Y", "NNG", "XSA-I", "VA-I"):
        assert tag.startswith("J") == base_tag(tag).startswith("J")
        assert tag.startswith("E") == base_tag(tag).startswith("E")


def test_real_kiwi_output_contains_irregular_affix_and_is_counted() -> None:
    # 실제 Kiwi 0.23.2 출력에 XSA-I가 등장하며, 그것이 deriv_affix_count에 반영되어야 한다.
    kiwi = get_kiwi()
    text = "사랑스럽고 어른스럽다"
    tags = [token.tag for token in kiwi.analyze(text, top_n=1)[0][0]]
    assert any(tag.startswith("XSA-") for tag in tags), tags
    features = morphology_features(text, eojeol_count=2, kiwi=kiwi)
    assert features["deriv_affix_count"] >= 2


# --- M1: morpheme_density denominator -------------------------------------------------


def test_morpheme_density_uses_eojeol_count() -> None:
    morphs = [morph("학교", "NNG"), morph("에", "JKB"), morph("가", "VV"), morph("ᆸ니다", "EF")]
    features = features_from_morphs(morphs, eojeol_count=2)
    # SSOT §13.6: MorphemeDensity = MorphemeCount / EojeolCount
    assert features["morpheme_density"] == pytest.approx(4 / 2)


def test_morpheme_density_config_declares_eojeol_denominator() -> None:
    assert MORPHOLOGY_CONFIG["morpheme_density_denominator"] == "eojeol_count"
    assert "codepoint" not in MORPHOLOGY_CONFIG["morpheme_density_denominator"]


def test_morphology_features_requires_eojeol_count_keyword() -> None:
    with pytest.raises(TypeError):
        morphology_features("학교에 갑니다", codepoint_count=7)  # type: ignore[call-arg]


# --- M4: zero-morpheme contract -------------------------------------------------------


def test_zero_morpheme_yields_null_ratios_and_warning() -> None:
    features = features_from_morphs([], eojeol_count=1)
    assert features["morpheme_count"] == 0
    assert features["analysis_warning_flag"] is True
    assert features["analysis_warning_reason"] == WARNING_ZERO_MORPHEME
    # 대체 분모 금지: morpheme_count 분모 ratio는 0.0이 아니라 null이어야 한다.
    for key in ("particle_ratio", "ending_ratio", "deriv_affix_ratio", "function_morpheme_ratio"):
        assert features[key] is None, key
    # density 분모는 eojeol_count이므로 정의되며 0.0이 정확한 값이다.
    assert features["morpheme_density"] == 0.0


def test_genuine_zero_ratio_is_distinguishable_from_zero_morpheme() -> None:
    # 조사/어미가 없는 정상 분석은 ratio가 0.0이고 warning이 없다.
    features = features_from_morphs([morph("한국", "NNP"), morph("대학교", "NNG")], eojeol_count=2)
    assert features["particle_ratio"] == 0.0
    assert features["analysis_warning_flag"] is False
    assert features["analysis_warning_reason"] == WARNING_NONE


def test_zero_eojeol_count_is_hard_invalid() -> None:
    with pytest.raises(MorphologyHardInvalidError):
        features_from_morphs([morph("가", "VV")], eojeol_count=0)


def test_empty_input_is_rejected() -> None:
    with pytest.raises(MorphologyInputError):
        morphology_features("", eojeol_count=1)


# --- M3: full D-03 schema -------------------------------------------------------------


def test_schema_covers_every_d03_required_field() -> None:
    names = set(morph_features_schema().names)
    required = {
        "morph_measurement_id",
        "pair_id",
        "analyzer_name",
        "analyzer_package_version",
        "analyzer_model_version",
        "analyzer_config_hash",
        "morpheme_sequence",
        "morpheme_count",
        "particle_count",
        "ending_count",
        "deriv_affix_count",
        "analysis_warning_flag",
    }
    assert required <= names
    for name in ("morpheme_density", "particle_ratio", "ending_ratio", "deriv_affix_ratio",
                 "function_morpheme_ratio", "eojeol_count"):
        assert name in names
    assert "pos_tag_distribution" not in names  # POS zoo(전체 tag 목록)는 의도적으로 포함하지 않는다.


def test_morpheme_sequence_is_structured_list_of_form_pos() -> None:
    field = morph_features_schema().field("morpheme_sequence")
    assert pa.types.is_list(field.type)
    struct_type = field.type.value_type
    assert pa.types.is_struct(struct_type)
    assert {struct_type.field(i).name for i in range(struct_type.num_fields)} == {"form", "pos"}


def test_ratio_fields_are_nullable_and_counts_are_not() -> None:
    schema = morph_features_schema()
    for name in ("particle_ratio", "ending_ratio", "deriv_affix_ratio", "function_morpheme_ratio"):
        assert schema.field(name).nullable is True, name
    for name in ("morpheme_count", "particle_count", "ending_count", "deriv_affix_count",
                 "eojeol_count", "morpheme_density", "analysis_warning_flag"):
        assert schema.field(name).nullable is False, name


def test_build_record_matches_schema_and_is_writable() -> None:
    morphs = [morph("학생", "NNG"), morph("답", "XSA-I"), morph("게", "EC")]
    record = build_record("pair_x", morphs, eojeol_count=1)
    schema = morph_features_schema()
    assert set(record) == set(schema.names)
    batch = pa.RecordBatch.from_pylist([record], schema=schema)  # schema 적합성을 실제 직렬화로 확인한다.
    assert batch.num_rows == 1
    assert record["deriv_affix_count"] == 1
    assert record["ending_count"] == 1
    assert record["morpheme_sequence"] == [
        {"form": "학생", "pos": "NNG"}, {"form": "답", "pos": "XSA-I"}, {"form": "게", "pos": "EC"}
    ]


def test_morph_measurement_id_is_deterministic_and_config_bound() -> None:
    first = morph_measurement_id("pair_abc")
    assert first == morph_measurement_id("pair_abc")
    assert first != morph_measurement_id("pair_abd")
    assert first.startswith("morph_")
    # config hash가 record에 analyzer_config_hash로 실려 provenance가 닫히는지 확인한다.
    record = build_record("pair_abc", [morph("가", "VV")], eojeol_count=1)
    assert record["morph_measurement_id"] == first
    assert record["analyzer_config_hash"] == MORPHOLOGY_CONFIG_SHA256


# --- ratios / invariants --------------------------------------------------------------


def test_ratios_are_bounded_and_function_ratio_is_additive() -> None:
    for text, eojeol in (("안녕하세요 반갑습니다", 2), ("이것은 테스트 문장입니다", 3), ("학교에서 열심히 공부했습니다", 3)):
        features = morphology_features(text, eojeol_count=eojeol)
        for key in ("particle_ratio", "ending_ratio", "deriv_affix_ratio", "function_morpheme_ratio"):
            assert 0.0 <= features[key] <= 1.0
        assert features["function_morpheme_ratio"] == pytest.approx(
            features["particle_ratio"] + features["ending_ratio"]
        )
        assert math.isfinite(features["morpheme_density"])


def test_counts_never_exceed_morpheme_count() -> None:
    features = morphology_features("학교에서 열심히 공부했습니다", eojeol_count=3)
    total = features["particle_count"] + features["ending_count"] + features["deriv_affix_count"]
    assert total <= features["morpheme_count"]


# --- M5 / optimization equivalence ----------------------------------------------------


def test_no_superseded_population_constant_in_module() -> None:
    # M5 회귀: 코드 상수로서의 3,836,013이 사라졌는지 AST로 검사한다
    # (docstring에 남은 수정 이력 서술은 상수가 아니므로 통과해야 한다).
    import ast
    from pathlib import Path

    import tokenization_premium.morphology as module

    tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
    literals = [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, int) and not isinstance(node.value, bool)
    ]
    assert 3_836_013 not in literals
    assert 3_835_988 not in literals  # 신규 population 값도 코드에 박아넣지 않는다.


def test_batch_path_matches_scalar_path_exactly() -> None:
    kiwi = get_kiwi()
    texts = ["안녕하세요 저는 학생입니다", "사랑스럽고 어른스럽다", "특허정보원에서 발표하였습니다", "한국 대학교 도서관"]
    eojeols = [3, 2, 2, 3]
    batch = analyze_batch(texts, kiwi=kiwi)
    for text, morphs, eojeol in zip(texts, batch, eojeols, strict=True):
        scalar = morphology_features(text, eojeol_count=eojeol, kiwi=kiwi)
        candidate = features_from_morphs(morphs, eojeol_count=eojeol)
        assert compare_feature_dicts(scalar, candidate) == []


def test_compare_feature_dicts_detects_difference() -> None:
    assert compare_feature_dicts({"a": 1}, {"a": 1}) == []
    assert compare_feature_dicts({"a": 1}, {"a": 2}) == ["a"]
    assert compare_feature_dicts({"a": 1}, {"b": 1}) == ["a", "b"]
