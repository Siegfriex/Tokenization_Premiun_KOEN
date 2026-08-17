"""G1 D-01 identity, schema, contract loading의 fail-fast 단위 테스트다."""

from __future__ import annotations  # Python 3.12 지연 annotation 평가를 사용한다.

import hashlib  # independent identity reference digest를 계산한다.
import json  # temporary ingest contract를 UTF-8 JSON으로 저장한다.
import struct  # independent u64be length prefix를 만든다.
from pathlib import Path  # pytest temporary file 경로를 처리한다.

import pytest  # invalid runtime override의 fail-fast contract를 검사한다.
import yaml  # temporary research config를 YAML로 저장한다.

from tokenization_premium.registry import (  # D-01 pure functions와 runtime safety setting을 검증한다.
    DUCKDB_MEMORY_LIMIT_ENV,
    canonical_json_text,
    duplicate_group_id,
    load_contracts,
    provenance_pair_id,
    resolve_duckdb_memory_limit,
    source_id_for,
)
from tokenization_premium.schemas import pair_registry_schema, source_registry_schema, staging_registry_schema  # registry schema 계약을 검증한다.


def test_duplicate_group_id_matches_independent_length_prefix_reference() -> None:
    """
    /**
     * @purpose duplicate_group_id가 Recon의 u64be length-prefixed KO+EN SHA-256 정의와 일치하는지 검사한다.
     * @spec_ref G1_INGEST_EXPECTATIONS_v001 identity_method
     * @return None
     * @raises AssertionError digest 불일치 시
     * @validation independent hashlib construction exact equality
     * @artifact 없음
     */
    """
    ko_text = "한글🙂"  # multi-byte UTF-8 길이 계산을 검증할 한국어 예시를 만든다.
    en_text = "English"  # 두 번째 field boundary를 검증할 영어 예시를 만든다.
    ko_bytes = ko_text.encode("utf-8")  # reference KO UTF-8 bytes를 만든다.
    en_bytes = en_text.encode("utf-8")  # reference EN UTF-8 bytes를 만든다.
    reference = hashlib.sha256(struct.pack(">Q", len(ko_bytes)) + ko_bytes + struct.pack(">Q", len(en_bytes)) + en_bytes).hexdigest()  # contract 수식을 함수와 독립적으로 구현한다.
    assert duplicate_group_id(ko_text, en_text) == reference  # production digest가 independent reference와 같은지 확인한다.


def test_provenance_pair_id_is_not_content_identity() -> None:
    """
    /**
     * @purpose 같은 content라도 source record provenance가 다르면 pair_id가 다름을 검사한다.
     * @spec_ref PAIR_IDENTITY_AND_DUPLICATE_CONTRACT_v1 Record Identity != Pair Content Identity
     * @return None
     * @raises AssertionError provenance 분리가 깨진 경우
     * @validation two record IDs yield two pair IDs
     * @artifact 없음
     */
    """
    source_id = source_id_for("025", "a" * 64)  # 동일 source snapshot identity를 만든다.
    first = provenance_pair_id(source_id, "SN-1")  # 첫 raw record provenance key를 계산한다.
    second = provenance_pair_id(source_id, "SN-2")  # 둘째 raw record provenance key를 계산한다.
    assert first.startswith("pair_") and len(first) == 69  # 명시적 prefix와 64자리 digest 형식을 확인한다.
    assert first != second  # source_record_id 차이가 pair_id에 반영되는지 확인한다.


def test_canonical_json_text_preserves_korean_and_key_order() -> None:
    """
    /**
     * @purpose raw locator JSON이 key order와 ASCII escaping에 의존하지 않는지 검사한다.
     * @spec_ref SSOT §30.2
     * @return None
     * @raises AssertionError canonical text 불일치 시
     * @validation 두 mapping order의 exact equality와 한글 glyph 보존
     * @artifact 없음
     */
    """
    first = canonical_json_text({"나": 2, "가": 1})  # 역순 insertion mapping을 canonicalize한다.
    second = canonical_json_text({"가": 1, "나": 2})  # 정순 insertion mapping을 canonicalize한다.
    assert first == second == '{"가":1,"나":2}'  # key sort와 literal Korean 보존을 확인한다.


def test_pair_registry_schema_contains_d01_and_group_contract() -> None:
    """
    /**
     * @purpose final schema가 16개 D-01 fields와 required group/provenance fields를 포함하는지 검사한다.
     * @spec_ref SSOT §12.1; G1_PAIR_REGISTRY_PRECONTRACT_v1 §14
     * @return None
     * @raises AssertionError field 누락/중복 시
     * @validation required set subset 및 unique names
     * @artifact 없음
     */
    """
    schema = pair_registry_schema()  # production final schema를 읽는다.
    required = {  # SSOT D-01 canonical fields를 exact set으로 만든다.
        "pair_id",
        "source_id",
        "source_tier",
        "domain",
        "sentence_type",
        "translation_direction",
        "ko_text_raw",
        "en_text_raw",
        "ko_text_nfc",
        "en_text_nfc",
        "ko_text_analysis",
        "en_text_analysis",
        "pair_quality_status",
        "pair_quality_score",
        "pair_version",
        "source_license_note",
    }
    assert required.issubset(schema.names)  # D-01 field가 모두 final schema에 있는지 확인한다.
    assert {"duplicate_group_id", "representative_pair_id", "raw_locator"}.issubset(schema.names)  # required auxiliary identity fields를 확인한다.
    assert len(schema.names) == len(set(schema.names))  # 중복 column 이름이 없는지 확인한다.
    assert "translation_direction" not in staging_registry_schema().names  # group-resolved direction이 staging에 조기 생성되지 않는지 확인한다.
    assert len(source_registry_schema()) == 14  # source registry fixed column 수를 확인한다.


def test_load_contracts_requires_exact_g1_bundle(tmp_path: Path) -> None:
    """
    /**
     * @purpose implementation이 unresolved semantics를 invent하지 않고 exact G1 contract bundle만 받는지 검사한다.
     * @spec_ref G1 contract dependency directive
     * @param tmp_path pytest temporary directory
     * @return None
     * @raises AssertionError contract validation 실패 시
     * @validation minimal exact config/oracle parse
     * @artifact 없음
     */
    """
    research_path = tmp_path / "research_v1.yaml"  # temporary authoritative config path를 정한다.
    ingest_path = tmp_path / "G1_INGEST_EXPECTATIONS_v001.json"  # temporary data contract path를 정한다.
    research = {  # load_contracts가 소비하는 exact frozen keys를 최소 fixture로 만든다.
        "source_hierarchy": {"corpus_tier_assignment": {"025": "A", "026": "A", "legacy": None}},
        "translation_direction_defaults": {"legacy": "UNKNOWN"},
        "d01_field_contract": {"pair_quality_status": {"phase1_value": "review"}, "pair_version": {"syntax": "v001 (zero-padded)"}},
    }
    ingest = {"expected_logical_record_counts": {"025": 2_700_345, "026": 1_350_162, "LEGACY": 1_602_418, "total": 5_652_925}}  # Director exact count oracle fixture를 만든다.
    research_path.write_text(yaml.safe_dump(research, allow_unicode=True), encoding="utf-8")  # UTF-8 research YAML fixture를 저장한다.
    ingest_path.write_text(json.dumps(ingest, ensure_ascii=False), encoding="utf-8")  # UTF-8 ingest JSON fixture를 저장한다.
    observed_research, observed_ingest = load_contracts(research_path, ingest_path)  # production loader로 두 fixture를 읽는다.
    assert observed_research == research  # research config가 임의 변형되지 않았는지 확인한다.
    assert observed_ingest == ingest  # ingest contract가 임의 변형되지 않았는지 확인한다.


def test_duckdb_memory_limit_resolution_is_safe_and_overridable() -> None:
    """
    /**
     * @purpose DuckDB memory policy가 8GB 기본값, 6GB override, invalid fail-fast를 지키는지 검사한다.
     * @spec_ref INC-001 post-incident runtime safety hardening
     * @return None
     * @raises AssertionError 또는 ValueError contract가 깨진 경우
     * @validation pure environment-mapping resolution; DuckDB/registry ingest 미실행
     * @artifact 없음
     */
    """
    assert resolve_duckdb_memory_limit({}) == "8GB"  # override가 없으면 새 research-job 기본 상한을 확인한다.
    assert resolve_duckdb_memory_limit({DUCKDB_MEMORY_LIMIT_ENV: " 6gb "}) == "6GB"  # 보수적 동시 실행 override의 공백/case를 정규화한다.
    with pytest.raises(ValueError, match=DUCKDB_MEMORY_LIMIT_ENV):  # 임의 SQL 또는 단위 없는 값은 실행 전에 거부해야 한다.
        resolve_duckdb_memory_limit({DUCKDB_MEMORY_LIMIT_ENV: "12GB; DROP TABLE registry"})
