"""D-02 representation feature 추출(NB03) 단위 테스트; synthetic 입력만 사용한다."""

from __future__ import annotations

import math

import pyarrow as pa
import pytest

from tokenization_premium.representation import (
    RepresentationInputError,
    lexical_segment_count,
    pair_cross_features,
    rep_features_schema,
    rep_features_v002_schema,
    side_features,
)


def test_ascii_only() -> None:
    features = side_features("Hello World 123!")
    assert features["codepoint_count"] == len("Hello World 123!")
    assert features["grapheme_count"] == features["codepoint_count"]
    assert features["hangul_share"] == 0.0
    assert features["latin_share"] > 0
    assert features["digit_share"] > 0
    assert features["punctuation_share"] > 0
    assert features["script_type_count"] == 1  # latin만 등장한다.
    assert features["script_switch_count"] == 0


def test_hangul_syllable_only() -> None:
    features = side_features("안녕하세요")
    assert features["codepoint_count"] == 5
    assert features["grapheme_count"] == 5
    assert features["hangul_share"] == 1.0
    assert features["latin_share"] == 0.0
    assert features["script_type_count"] == 1
    assert features["script_switch_count"] == 0


def test_hangul_latin_mixed_script_switch() -> None:
    features = side_features("안녕hello세계")
    assert features["script_type_count"] == 2
    # 안녕(hangul) -> hello(latin) -> 세계(hangul): 전환 2회.
    assert features["script_switch_count"] == 2


def test_digit_and_punct_are_neutral_for_switch_counting() -> None:
    features = side_features("안녕123, hello")
    # hangul -> latin 전환 1회만 세고, 중간 digit/punct/space는 switch로 세지 않는다.
    assert features["script_switch_count"] == 1
    assert features["digit_share"] > 0
    assert features["punctuation_share"] > 0


def test_emoji_extended_grapheme_cluster() -> None:
    text = "안녕👍🏽"
    features = side_features(text)
    # 👍🏽 = THUMBS UP + skin tone modifier, 하나의 extended grapheme cluster이지만 2 code point다.
    assert features["codepoint_count"] > features["grapheme_count"]
    assert features["emoji_flag"] is True
    assert features["grapheme_count"] == 3  # 안, 녕, 👍🏽


def test_digits_and_punctuation_symbols_are_not_emoji() -> None:
    features = side_features("2024/01#01*")
    assert features["emoji_flag"] is False


def test_combining_sequence_codepoint_vs_grapheme() -> None:
    combining_e = "e" + "́"  # NFD e + combining acute accent = 1 grapheme, 2 code point.
    features = side_features(combining_e)
    assert features["codepoint_count"] == 2
    assert features["grapheme_count"] == 1


def test_nfc_case_codepoint_equals_grapheme() -> None:
    precomposed_e = "é"  # NFC é = 1 code point = 1 grapheme.
    features = side_features(precomposed_e)
    assert features["codepoint_count"] == 1
    assert features["grapheme_count"] == 1


def test_whitespace_runs_counted_as_maximal_runs() -> None:
    features = side_features("a  b   c")
    assert features["whitespace_count"] == 5
    assert features["space_run_count"] == 2  # "  "와 "   " 두 개의 run.


def test_punctuation_and_digit_shares_are_disjoint() -> None:
    features = side_features("3.14, 100%")
    assert features["digit_share"] > 0
    assert features["punctuation_share"] > 0
    # 두 share가 겹치지 않고 codepoint 분모 위에서 합리적으로 분해된다.
    assert 0 < features["digit_share"] + features["punctuation_share"] < 1.0


def test_empty_input_is_rejected() -> None:
    with pytest.raises(RepresentationInputError):
        side_features("")


def test_utf8_byte_count_correctness() -> None:
    text = "한글é$"
    features = side_features(text)
    assert features["utf8_bytes"] == len(text.encode("utf-8"))
    assert features["utf8_bytes"] == 3 + 3 + 2 + 1  # 한(3)+글(3)+é(2)+$(1) UTF-8 bytes.


def test_feature_ratio_denominators_are_correct() -> None:
    features = side_features("안녕 hello")
    assert features["bytes_per_codepoint"] == pytest.approx(features["utf8_bytes"] / features["codepoint_count"])
    assert features["bytes_per_grapheme"] == pytest.approx(features["utf8_bytes"] / features["grapheme_count"])
    assert features["whitespace_density"] == pytest.approx(features["whitespace_count"] / features["codepoint_count"])


def test_shares_partition_the_full_codepoint_set() -> None:
    for text in ("안녕 hello123!@#", "동해물과 백두산이", "The quick brown fox 123.", "👍🏽 test #1"):
        features = side_features(text)
        total_share = (
            features["hangul_share"]
            + features["latin_share"]
            + features["digit_share"]
            + features["punctuation_share"]
            + features["symbol_other_share"]
            + features["whitespace_density"]
        )
        assert total_share == pytest.approx(1.0, abs=1e-9)


def test_url_email_code_like_flags() -> None:
    assert side_features("see http://example.com for details")["url_flag"] is True
    assert side_features("no link here")["url_flag"] is False
    assert side_features("contact me at test@example.com")["email_flag"] is True
    assert side_features("not an email at all")["email_flag"] is False
    assert side_features("def f(x): return x + 1;")["code_like_flag"] is True
    assert side_features("이것은 평범한 한국어 문장입니다")["code_like_flag"] is False


def test_pair_cross_features_use_side_feature_ratios() -> None:
    ko = side_features("안녕하세요 반갑습니다")
    en = side_features("Hello nice to meet you")
    cross = pair_cross_features(ko, en)
    assert cross["pair_codepoint_ratio"] == pytest.approx(ko["codepoint_count"] / en["codepoint_count"])
    assert cross["pair_grapheme_ratio"] == pytest.approx(ko["grapheme_count"] / en["grapheme_count"])
    assert cross["pair_byte_ratio"] == pytest.approx(ko["utf8_bytes"] / en["utf8_bytes"])
    assert cross["pair_codepoint_diff"] == ko["codepoint_count"] - en["codepoint_count"]
    assert math.isfinite(cross["pair_codepoint_ratio"])


def test_rep_features_schema_pair_id_and_column_shape() -> None:
    schema = rep_features_schema()
    assert schema.field("pair_id").type.equals(schema.field("pair_id").type)
    assert schema.names[0] == "pair_id"
    ko_cols = [name for name in schema.names if name.startswith("ko_")]
    en_cols = [name for name in schema.names if name.startswith("en_")]
    assert len(ko_cols) == len(en_cols) == 19  # side_features가 반환하는 19개 feature와 1:1 대응한다.
    for name in ("pair_codepoint_ratio", "pair_grapheme_ratio", "pair_byte_ratio", "pair_codepoint_diff"):
        assert name in schema.names
    for name in ("feature_extractor_version", "unicode_version", "grapheme_implementation", "config_sha256"):
        assert name in schema.names


# --- SSOT §12.2 lexical length (RD-20260817-D02D03-CONFORMANCE-01) -------------------


def test_lexical_segment_count_basic_ko_and_en() -> None:
    assert lexical_segment_count("나는 학교에 간다") == 3
    assert lexical_segment_count("I go to school") == 4


def test_lexical_segment_count_collapses_runs_and_ignores_edges() -> None:
    # 연속 공백/개행/탭과 앞뒤 공백은 빈 segment를 만들지 않는다.
    assert lexical_segment_count("  나는   학교에\t\n간다  ") == 3


def test_lexical_segment_count_uses_unicode_whitespace() -> None:
    # NBSP(U+00A0)와 ideographic space(U+3000)도 Unicode whitespace로 분리한다.
    assert lexical_segment_count("나는 학교에　간다") == 3


def test_lexical_segment_count_does_not_normalize_source_text() -> None:
    # punctuation stripping / lowercasing / NFKC 금지: 표면형 그대로 세는지 확인한다.
    assert lexical_segment_count("Hello, World! -- OK") == 4
    assert lexical_segment_count("ＡＢＣ ①②③") == 2
    assert lexical_segment_count("...") == 1


def test_lexical_segment_count_single_token_and_punctuation_only() -> None:
    assert lexical_segment_count("안녕") == 1
    assert lexical_segment_count("!!!") == 1


def test_lexical_segment_count_rejects_empty_input() -> None:
    with pytest.raises(RepresentationInputError):
        lexical_segment_count("")


def test_lexical_segment_count_consistent_with_space_run_count() -> None:
    # 앞뒤 공백이 없는 텍스트에서는 eojeol_count == space_run_count + 1 이어야 한다.
    for text in ("나는 학교에 간다", "I go to school", "특허정보원 기술과학 분야 데이터", "a b c d e"):
        assert lexical_segment_count(text) == side_features(text)["space_run_count"] + 1


def test_rep_features_v002_schema_extends_v001_without_altering_it() -> None:
    v1 = rep_features_schema()
    v2 = rep_features_v002_schema()
    assert len(v2) == len(v1) + 2
    # v001의 모든 열이 이름·dtype·nullability 그대로 보존되어야 한다.
    v2_by_name = {f.name: f for f in v2}
    for field in v1:
        assert v2_by_name[field.name].type.equals(field.type)
        assert v2_by_name[field.name].nullable == field.nullable
    for name in ("ko_eojeol_count", "en_word_count"):
        assert v2_by_name[name].type.equals(pa.int64())
        assert v2_by_name[name].nullable is False
    # SSOT §12.2 순서(Unicode length -> lexical length)를 따르도록 grapheme_count 뒤에 놓는다.
    assert v2.names.index("ko_eojeol_count") == v2.names.index("ko_grapheme_count") + 1
    assert v2.names.index("en_word_count") == v2.names.index("en_grapheme_count") + 1
