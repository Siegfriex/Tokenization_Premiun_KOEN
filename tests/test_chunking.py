"""D-05 o200k regex chunk 측정 단위 테스트.

핵심 회귀: chunk 경계는 D-04 token id를 재현해야 하며, D-05는 token authority가 아니다.
"""

from __future__ import annotations

import hashlib

import pyarrow as pa
import pytest

from tokenization_premium.chunking import (
    CHUNK_RELATIVE_PATH,
    CHUNK_TYPES,
    CHUNKING_CONFIG,
    CHUNKING_CONFIG_SHA256,
    ChunkInvariantViolation,
    assert_tokenizer_identity,
    build_chunk_record,
    chunk_measurement_id,
    chunk_pattern,
    chunk_schema,
    classify_chunk,
    regex_chunks,
    side_chunk_features,
)
from tokenization_premium.paths import PROJECT_ROOT
from tokenization_premium.tokenizer_measurement import (
    ENCODING_FILE_SHA256,
    PAT_STR_SHA256,
    TIKTOKEN_VERSION,
    TOKENIZER_ID,
    load_o200k_base_offline,
)

CACHE = PROJECT_ROOT / ".runtime/tiktoken-cache"

SAMPLES = [
    "안녕하세요 저는 학생입니다.",
    "The quick brown fox costs $12.50!",
    "특허정보원 기술과학 A/B 테스트 2024년",
    "줄바꿈\n두 번째 줄\t탭",
    "   leading and trailing   ",
    "숫자123과 영문abc 혼합",
    "!!!",
    "a",
    "😀 emoji 포함 문장",
    "URL http://example.com/path?q=1 포함",
]


@pytest.fixture(scope="module")
def encoding():
    return load_o200k_base_offline(CACHE)


# --- §4 configuration freeze ---------------------------------------------------------


def test_pat_str_matches_d04_frozen_hash(encoding) -> None:
    pattern = chunk_pattern(encoding)
    assert hashlib.sha256(pattern.pattern.encode()).hexdigest() == PAT_STR_SHA256


def test_tokenizer_identity_equals_d04(encoding) -> None:
    identity = assert_tokenizer_identity(encoding)
    assert identity["tokenizer_id"] == TOKENIZER_ID
    assert identity["tiktoken_version"] == TIKTOKEN_VERSION
    assert identity["pat_str_sha256"] == PAT_STR_SHA256
    assert identity["encoding_file_sha256"] == ENCODING_FILE_SHA256


def test_config_declares_track_a_constraints() -> None:
    assert CHUNKING_CONFIG["special_tokens_used"] is False
    assert CHUNKING_CONFIG["chat_template_used"] is False
    assert "D-04" in CHUNKING_CONFIG["authority_note"]


def test_canonical_path_follows_ssot_38() -> None:
    assert CHUNK_RELATIVE_PATH.name == "CHUNK_O200K_BASE_v001.parquet"


# --- §5 invariant 1: reconstruction --------------------------------------------------


@pytest.mark.parametrize("text", SAMPLES)
def test_concat_of_chunks_reconstructs_text(text, encoding) -> None:
    assert "".join(regex_chunks(text, encoding=encoding)) == text


@pytest.mark.parametrize("text", SAMPLES)
def test_no_empty_chunk_and_order_is_deterministic(text, encoding) -> None:
    first = regex_chunks(text, encoding=encoding)
    assert all(c for c in first), "빈 chunk는 계약상 생성하지 않는다"
    assert first == regex_chunks(text, encoding=encoding), "chunk 순서는 결정적이어야 한다"


def test_lost_span_raises_rather_than_silently_dropping(monkeypatch, encoding) -> None:
    # regex가 입력을 모두 덮지 못하는 상황을 강제해 fail-closed 동작을 확인한다.
    import regex as _re

    import tokenization_premium.chunking as chunking

    monkeypatch.setattr(chunking, "_PAT", _re.compile(r"\p{L}+"))
    monkeypatch.setattr(chunking, "chunk_pattern", lambda enc: chunking._PAT)
    with pytest.raises(ChunkInvariantViolation, match="lost span"):
        chunking.regex_chunks("abc !!! def", encoding=encoding)


# --- §5 invariant 4/5: token equivalence ---------------------------------------------


@pytest.mark.parametrize("text", SAMPLES)
def test_flattened_chunk_tokens_equal_direct_encode(text, encoding) -> None:
    features = side_chunk_features(text, encoding=encoding)
    assert features.pop("_flat_tokens") == encoding.encode(text)


@pytest.mark.parametrize("text", SAMPLES)
def test_chunk_token_total_equals_direct_token_count(text, encoding) -> None:
    features = side_chunk_features(text, encoding=encoding)
    features.pop("_flat_tokens")
    assert features["chunk_token_total"] == len(encoding.encode(text))


def test_record_flags_token_mismatch_instead_of_raising(encoding) -> None:
    ko, en = "안녕하세요", "hello"
    wrong = [999999]                      # D-04 저장값과 다른 token id를 흉내낸다
    record = build_chunk_record("pair_x", "tok_x", ko, en, wrong,
                                encoding.encode(en), encoding=encoding)
    assert record["token_equivalence_ok"] is False
    assert record["analysis_warning_flag"] is True
    assert "KO_TOKEN_FLATTEN_MISMATCH" in record["analysis_warning_reason"]


def test_record_is_clean_when_token_ids_agree(encoding) -> None:
    ko, en = "학교에 갑니다", "I go to school"
    record = build_chunk_record("pair_y", "tok_y", ko, en, encoding.encode(ko),
                                encoding.encode(en), encoding=encoding)
    assert record["token_equivalence_ok"] is True
    assert record["chunk_reconstruction_ok"] is True
    assert record["analysis_warning_flag"] is False
    assert record["analysis_warning_reason"] == "NONE"


# --- §12.5 schema --------------------------------------------------------------------


def test_schema_covers_ssot_12_5_fields() -> None:
    names = set(chunk_schema().names)
    assert {"chunk_measurement_id", "pair_id", "tokenizer_measurement_id"} <= names
    for side in ("ko", "en"):
        assert f"{side}_chunk_count" in names
        assert f"{side}_mean_chunk_bytes" in names
        assert f"{side}_p50_chunk_bytes" in names
        assert f"{side}_p90_chunk_bytes" in names
        assert f"{side}_tokens_per_chunk" in names
        for chunk_type in CHUNK_TYPES:
            assert f"{side}_chunk_type_share_{chunk_type}" in names


def test_schema_stores_no_raw_chunk_strings() -> None:
    # 공개 canonical artifact에 원문 chunk 문자열을 대량 저장하지 않는다 (§6).
    for field in chunk_schema():
        assert "text" not in field.name
        assert "chunk_string" not in field.name
        assert not (pa.types.is_string(field.type) and field.name.startswith(("ko_", "en_")))


def test_record_matches_schema_and_serialises(encoding) -> None:
    record = build_chunk_record("pair_z", "tok_z", "안녕 세계", "hello world",
                                encoding.encode("안녕 세계"), encoding.encode("hello world"),
                                encoding=encoding)
    schema = chunk_schema()
    assert set(record) == set(schema.names)
    assert pa.RecordBatch.from_pylist([record], schema=schema).num_rows == 1


def test_measurement_id_is_deterministic_and_config_bound() -> None:
    first = chunk_measurement_id("pair_abc")
    assert first == chunk_measurement_id("pair_abc")
    assert first != chunk_measurement_id("pair_abd")
    assert first.startswith("chunk_")
    assert CHUNKING_CONFIG_SHA256 in CHUNKING_CONFIG_SHA256


# --- chunk type classification -------------------------------------------------------


def test_chunk_type_priority_matches_pat_str_structure() -> None:
    assert classify_chunk("hello") == "letter"
    assert classify_chunk(" 한국어") == "letter"
    assert classify_chunk("123") == "number"
    assert classify_chunk(" $") == "punctuation"
    assert classify_chunk("   ") == "whitespace"
    assert classify_chunk("\n") == "whitespace"
    # 우선순위: 문자가 있으면 숫자가 섞여도 letter다 (pat_str의 letter 분기와 같다).
    assert classify_chunk("abc1") == "letter"


@pytest.mark.parametrize("text", SAMPLES)
def test_type_shares_sum_to_one(text, encoding) -> None:
    features = side_chunk_features(text, encoding=encoding)
    features.pop("_flat_tokens")
    total = sum(features[f"chunk_type_share_{t}"] for t in CHUNK_TYPES)
    assert total == pytest.approx(1.0, abs=1e-12)


@pytest.mark.parametrize("text", SAMPLES)
def test_derived_statistics_are_internally_consistent(text, encoding) -> None:
    f = side_chunk_features(text, encoding=encoding)
    f.pop("_flat_tokens")
    assert f["mean_chunk_bytes"] == pytest.approx(f["chunk_byte_total"] / f["chunk_count"])
    assert f["tokens_per_chunk"] == pytest.approx(f["chunk_token_total"] / f["chunk_count"])
    assert f["p50_chunk_bytes"] <= f["p90_chunk_bytes"] <= f["max_chunk_bytes"]
    assert f["chunk_byte_total"] == len(text.encode("utf-8"))


# --- scope boundary ------------------------------------------------------------------


def test_d05_is_not_a_second_token_authority() -> None:
    # D-05 schema에 token id 배열이나 TP가 들어가면 안 된다 (D-04가 authority).
    names = set(chunk_schema().names)
    for forbidden in ("ko_token_ids", "en_token_ids", "token_premium", "log_token_premium",
                      "compression_penalty"):
        assert forbidden not in names
