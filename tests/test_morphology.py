"""D-04 한국어 형태소 feature 추출(NB04) 단위 테스트; synthetic 입력만 사용한다."""

from __future__ import annotations

import math

import pytest

from tokenization_premium.morphology import (
    MorphologyInputError,
    get_kiwi,
    morph_features_schema,
    morphology_features,
)


def test_particle_and_ending_ratio_known_sentence() -> None:
    text = "안녕하세요 저는 학생입니다"
    codepoint_count = len(text)
    features = morphology_features(text, codepoint_count=codepoint_count)
    # 안녕(NNG) 하(XSA) 세요(EF) 저(NP) 는(JX) 학생(NNG) 이(VCP) ᆸ니다(EF) = 8 형태소.
    assert features["morpheme_count"] == 8
    assert features["particle_ratio"] == pytest.approx(1 / 8)
    assert features["ending_ratio"] == pytest.approx(2 / 8)
    assert features["deriv_affix_ratio"] == pytest.approx(1 / 8)
    assert features["function_morpheme_ratio"] == pytest.approx(3 / 8)


def test_morpheme_density_uses_provided_codepoint_count() -> None:
    text = "학교에 갑니다"
    features = morphology_features(text, codepoint_count=100)
    assert features["morpheme_density"] == pytest.approx(features["morpheme_count"] / 100)


def test_no_particle_or_ending_sentence_fragment() -> None:
    # 명사만 나열된 조각: 조사/어미가 전혀 없을 수 있다.
    features = morphology_features("한국 대학교 도서관", codepoint_count=9)
    assert features["particle_ratio"] == 0.0
    assert features["ending_ratio"] == 0.0


def test_ratios_are_bounded_in_zero_one() -> None:
    for text in ("안녕하세요 반갑습니다", "이것은 테스트 문장입니다", "특허정보원에서 발표하였습니다"):
        features = morphology_features(text, codepoint_count=len(text))
        assert 0.0 <= features["particle_ratio"] <= 1.0
        assert 0.0 <= features["ending_ratio"] <= 1.0
        assert 0.0 <= features["deriv_affix_ratio"] <= 1.0
        assert 0.0 <= features["function_morpheme_ratio"] <= 1.0
        assert features["particle_ratio"] + features["ending_ratio"] <= 1.0 + 1e-9
        assert math.isfinite(features["morpheme_density"])


def test_function_morpheme_ratio_equals_particle_plus_ending() -> None:
    text = "학교에서 열심히 공부했습니다"
    features = morphology_features(text, codepoint_count=len(text))
    assert features["function_morpheme_ratio"] == pytest.approx(
        features["particle_ratio"] + features["ending_ratio"]
    )


def test_empty_input_is_rejected() -> None:
    with pytest.raises(MorphologyInputError):
        morphology_features("", codepoint_count=1)


def test_zero_codepoint_count_is_rejected() -> None:
    with pytest.raises(ValueError, match="codepoint_count"):
        morphology_features("안녕", codepoint_count=0)


def test_kiwi_reuse_gives_identical_result() -> None:
    kiwi = get_kiwi()
    text = "안녕하세요 저는 학생입니다"
    first = morphology_features(text, codepoint_count=len(text), kiwi=kiwi)
    second = morphology_features(text, codepoint_count=len(text))  # 기본 lazy singleton 경로도 동일 결과를 내야 한다.
    assert first == second


def test_morph_features_schema_shape() -> None:
    schema = morph_features_schema()
    assert schema.names[0] == "pair_id"
    for name in (
        "ko_morpheme_count",
        "ko_morpheme_density",
        "ko_particle_ratio",
        "ko_ending_ratio",
        "ko_deriv_affix_ratio",
        "ko_function_morpheme_ratio",
        "analyzer_name",
        "analyzer_package_version",
        "analyzer_model_version",
        "config_sha256",
    ):
        assert name in schema.names
    assert "pos_tag_distribution" not in schema.names  # POS zoo(전체 tag 목록)는 의도적으로 포함하지 않는다.
