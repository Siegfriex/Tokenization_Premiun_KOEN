"""D-04 o200k_base tokenizer measurement(NB05) 단위 테스트; synthetic 입력만 사용한다."""

from __future__ import annotations

import math

import pytest
import tiktoken

from tokenization_premium.paths import PROJECT_ROOT
from tokenization_premium.tokenization import load_o200k_base_offline
from tokenization_premium.tokenizer_measurement import (
    EXACT_DECOMPOSITION_EPSILON,
    pair_token_measurement,
)

SYNTHETIC_PAIRS = [
    ("안녕하세요 반갑습니다", "Hello nice to meet you"),
    ("한국어 토큰화 재현성 검사", "Korean tokenization reproducibility check"),
    ("공백  두 개와\n줄바꿈", "two  spaces and\na line break"),
    ("NFC 한글과 emoji 😀 123", "NFC Hangul and emoji 😀 123"),
    ("짧다", "short"),
]


@pytest.fixture(scope="module")
def encoding() -> tiktoken.Encoding:
    return load_o200k_base_offline(PROJECT_ROOT / ".runtime/tiktoken-cache")


@pytest.mark.parametrize(("ko_text", "en_text"), SYNTHETIC_PAIRS)
def test_exact_decomposition_identity_within_epsilon(
    ko_text: str, en_text: str, encoding: tiktoken.Encoding
) -> None:
    measurement = pair_token_measurement(ko_text, en_text, encoding=encoding)
    assert measurement["identity_abs_error"] < EXACT_DECOMPOSITION_EPSILON
    reconstructed = (
        measurement["logCodePointRatio"] + measurement["logByteDensityRatio"] + measurement["logCompressionPenalty"]
    )
    assert measurement["logTP"] == pytest.approx(reconstructed, abs=EXACT_DECOMPOSITION_EPSILON)


@pytest.mark.parametrize(("ko_text", "en_text"), SYNTHETIC_PAIRS)
def test_roundtrip_ok_true_for_clean_text(ko_text: str, en_text: str, encoding: tiktoken.Encoding) -> None:
    measurement = pair_token_measurement(ko_text, en_text, encoding=encoding)
    assert measurement["roundtrip_ok"] is True


def test_token_difference_and_tp_consistency(encoding: tiktoken.Encoding) -> None:
    measurement = pair_token_measurement("안녕하세요 반갑습니다", "Hello nice to meet you", encoding=encoding)
    assert measurement["token_difference"] == measurement["T_KO"] - measurement["T_EN"]
    assert measurement["TP"] == pytest.approx(measurement["T_KO"] / measurement["T_EN"])
    assert measurement["logTP"] == pytest.approx(math.log(measurement["TP"]))


def test_identical_text_gives_tp_one(encoding: tiktoken.Encoding) -> None:
    measurement = pair_token_measurement("hello world", "hello world", encoding=encoding)
    assert measurement["TP"] == pytest.approx(1.0)
    assert measurement["logTP"] == pytest.approx(0.0, abs=1e-12)


def test_empty_input_is_rejected(encoding: tiktoken.Encoding) -> None:
    with pytest.raises(ValueError, match="empty"):
        pair_token_measurement("", "hello", encoding=encoding)
    with pytest.raises(ValueError, match="empty"):
        pair_token_measurement("안녕", "", encoding=encoding)


def test_code_point_ratio_matches_raw_lengths(encoding: tiktoken.Encoding) -> None:
    ko_text, en_text = "안녕하세요", "hello"
    measurement = pair_token_measurement(ko_text, en_text, encoding=encoding)
    assert measurement["CodePointRatio"] == pytest.approx(len(ko_text) / len(en_text))
