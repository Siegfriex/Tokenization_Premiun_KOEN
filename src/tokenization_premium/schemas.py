"""D-01 pair registry와 source registry의 명시적 PyArrow schema를 정의한다."""

from __future__ import annotations  # Python 3.12 지연 annotation 평가를 사용한다.

import pyarrow as pa  # 대용량 registry의 nullable dtype과 Parquet schema를 고정한다.


def pair_registry_schema() -> pa.Schema:
    """
    /**
     * @purpose Phase-1 D-01 pair registry의 column 순서, dtype, nullable 계약을 고정한다.
     * @spec_ref SSOT §12.1, G1_PAIR_REGISTRY_PRECONTRACT_v1 §14-16
     * @return PAIR_REGISTRY_v001의 PyArrow schema
     * @raises 없음
     * @validation schema 단위 테스트와 저장 Parquet schema exact equality로 검사한다.
     * @artifact data/registry/PAIR_REGISTRY_v001.parquet
     */
    """
    return pa.schema(  # D-01 필드와 승인된 provenance/QC 보조 필드를 한 schema로 반환한다.
        [
            pa.field("pair_id", pa.string(), nullable=False),  # provenance 기반 project-wide primary key를 저장한다.
            pa.field("source_id", pa.string(), nullable=False),  # corpus family와 raw snapshot을 결합한 source identity를 저장한다.
            pa.field("source_tier", pa.string(), nullable=True),  # Director 승인 Tier를 저장하며 Legacy는 미배정이므로 null을 허용한다.
            pa.field("domain", pa.string(), nullable=False),  # 승인된 top-level canonical domain을 저장한다.
            pa.field("sentence_type", pa.string(), nullable=False),  # raw metadata 부재 시 계약값 other를 저장한다.
            pa.field("translation_direction", pa.string(), nullable=False),  # duplicate group 전체에서 resolve한 번역방향을 저장한다.
            pa.field("ko_text_raw", pa.string(), nullable=False),  # 정규화하지 않은 한국어 원문을 보존한다.
            pa.field("en_text_raw", pa.string(), nullable=False),  # 정규화하지 않은 영어 원문을 보존한다.
            pa.field("ko_text_nfc", pa.string(), nullable=True),  # Phase 2 전에는 생성하지 않아 null로 둔다.
            pa.field("en_text_nfc", pa.string(), nullable=True),  # Phase 2 전에는 생성하지 않아 null로 둔다.
            pa.field("ko_text_analysis", pa.string(), nullable=True),  # Phase 2 분석 텍스트가 아직 없어 null로 둔다.
            pa.field("en_text_analysis", pa.string(), nullable=True),  # Phase 2 분석 텍스트가 아직 없어 null로 둔다.
            pa.field("pair_quality_status", pa.string(), nullable=False),  # semantic QC 전 계약값 review를 저장한다.
            pa.field("pair_quality_score", pa.float64(), nullable=True),  # semantic score 미측정 상태를 null로 표현한다.
            pa.field("pair_version", pa.string(), nullable=False),  # zero-padded registry version v001을 저장한다.
            pa.field("source_license_note", pa.string(), nullable=False),  # raw license와 재배포 비승인 경계를 명시한다.
            pa.field("source_record_id", pa.string(), nullable=False),  # source-native 또는 locator 기반 record identity를 저장한다.
            pa.field("raw_locator", pa.string(), nullable=False),  # physical file/sheet/row를 canonical JSON으로 저장한다.
            pa.field("duplicate_group_id", pa.string(), nullable=False),  # raw KO+EN length-prefix SHA-256 content identity를 저장한다.
            pa.field("representative_pair_id", pa.string(), nullable=False),  # group 내 lexicographic minimum pair_id를 저장한다.
            pa.field("domain_raw", pa.string(), nullable=True),  # source top-level domain label을 원문 그대로 보존한다.
            pa.field("subdomain_raw", pa.string(), nullable=True),  # source subdomain label을 원문 그대로 보존한다.
            pa.field("source_provenance_raw", pa.string(), nullable=True),  # corpus 내부 raw source/publisher label을 보존한다.
            pa.field("is_validation_upstream", pa.bool_(), nullable=False),  # upstream split provenance만 보존하며 project split로 사용하지 않는다.
            pa.field("translation_direction_raw", pa.string(), nullable=False),  # group resolve 이전 record-level 방향을 보존한다.
            pa.field("translation_direction_review_flag", pa.bool_(), nullable=False),  # 약한/모순/혼합 방향 evidence를 표시한다.
            pa.field("mt_field_present", pa.bool_(), nullable=False),  # source record에 mt staging field가 존재했는지 저장한다.
            pa.field("sentence_type_raw", pa.string(), nullable=True),  # 명시적 raw sentence type이 없으면 null을 유지한다.
            pa.field("sentence_type_provenance_status", pa.string(), nullable=False),  # sentence type provenance 부재를 명시한다.
            pa.field("normalization_status", pa.string(), nullable=False),  # Phase 1 미생성 상태를 명시한다.
            pa.field("qc_stage_status", pa.string(), nullable=False),  # Phase 2 QC 대기 상태를 명시한다.
            pa.field("direction_conflict_flag", pa.bool_(), nullable=False),  # group 내 raw 방향 불일치를 표시한다.
            pa.field("domain_conflict_flag", pa.bool_(), nullable=False),  # group 내 canonical domain 불일치를 표시한다.
            pa.field("source_id_conflict_flag", pa.bool_(), nullable=False),  # group 내 source family 불일치를 표시한다.
            pa.field("source_provenance_raw_conflict_flag", pa.bool_(), nullable=False),  # group 내 non-null raw source 불일치를 표시한다.
            pa.field("logical_corpus", pa.string(), nullable=False),  # 025/026/LEGACY ingest family를 저장한다.
            pa.field("canonical_ingest_role", pa.string(), nullable=False),  # exact allowlist role을 저장한다.
            pa.field("raw_file_relative_path", pa.string(), nullable=False),  # raw root 기준 source file 경로를 저장한다.
            pa.field("raw_file_sha256", pa.string(), nullable=False),  # verified input file SHA-256을 각 행에 연결한다.
            pa.field("raw_sheet_name", pa.string(), nullable=True),  # XLSX worksheet를 저장하며 JSON은 null이다.
            pa.field("raw_physical_row_number", pa.int64(), nullable=True),  # XLSX 1-based physical row를 저장하며 JSON은 null이다.
            pa.field("source_native_id", pa.string(), nullable=True),  # Legacy ID 등 source-native ID를 문자열로 보존한다.
            pa.field("source_native_sid", pa.string(), nullable=True),  # Legacy SID 등 source-native SID를 문자열로 보존한다.
            pa.field("raw_metadata_json", pa.string(), nullable=False),  # text 외 전체 raw record metadata를 canonical JSON으로 보존한다.
        ]
    )


def staging_registry_schema() -> pa.Schema:
    """
    /**
     * @purpose group window 계산 전 streaming ingest staging schema를 고정한다.
     * @spec_ref G1_PAIR_REGISTRY_PRECONTRACT_v1 §7, §14-16
     * @return final schema에서 group-derived 5개 필드를 제외한 PyArrow schema
     * @raises 없음
     * @validation finalization SQL이 최종 schema와 동일한 열을 만드는지 검사한다.
     * @artifact data/interim/PAIR_REGISTRY_v001_staging.parquet
     */
    """
    derived = {"translation_direction", "representative_pair_id", "direction_conflict_flag", "domain_conflict_flag", "source_id_conflict_flag", "source_provenance_raw_conflict_flag"}  # group 계산으로 생성할 열 이름을 고정한다.
    return pa.schema([field for field in pair_registry_schema() if field.name not in derived])  # raw record 단계에 존재하는 열만 같은 순서와 dtype으로 반환한다.


def source_registry_schema() -> pa.Schema:
    """
    /**
     * @purpose acquisition-family 수준 source registry schema를 고정한다.
     * @spec_ref SSOT §9.3, §12.1, G1_PAIR_REGISTRY_PRECONTRACT_v1 §1-2
     * @return SOURCE_REGISTRY_v001의 PyArrow schema
     * @raises 없음
     * @validation source_id uniqueness와 3개 family row count를 검사한다.
     * @artifact data/registry/SOURCE_REGISTRY_v001.parquet
     */
    """
    return pa.schema(  # family provenance와 ingest summary를 명시적 dtype으로 반환한다.
        [
            pa.field("source_id", pa.string(), nullable=False),  # source registry primary key를 저장한다.
            pa.field("logical_corpus", pa.string(), nullable=False),  # local family label을 저장한다.
            pa.field("source_tier", pa.string(), nullable=True),  # 025/026=A, Legacy=null을 저장한다.
            pa.field("research_role", pa.string(), nullable=False),  # research config의 source role을 저장한다.
            pa.field("primary_analysis_eligible", pa.bool_(), nullable=False),  # 승인된 primary eligibility를 저장한다.
            pa.field("provenance_closure_status", pa.string(), nullable=False),  # official provenance closure 상태를 저장한다.
            pa.field("official_dataset_id", pa.string(), nullable=True),  # 확인되지 않은 AIHub dataSetSn을 조작하지 않고 null로 둔다.
            pa.field("raw_manifest_sha256", pa.string(), nullable=False),  # source identity에 사용한 raw snapshot hash를 저장한다.
            pa.field("source_license_note", pa.string(), nullable=False),  # family-level license evidence 경계를 저장한다.
            pa.field("expected_row_count", pa.int64(), nullable=False),  # ingest contract expected logical rows를 저장한다.
            pa.field("observed_row_count", pa.int64(), nullable=False),  # 실제 registry rows를 저장한다.
            pa.field("input_file_count", pa.int64(), nullable=False),  # canonical allowlist file 수를 저장한다.
            pa.field("input_files_json", pa.string(), nullable=False),  # relative path와 SHA-256 inventory를 canonical JSON으로 저장한다.
            pa.field("pair_version", pa.string(), nullable=False),  # 연결되는 registry version을 저장한다.
        ]
    )
