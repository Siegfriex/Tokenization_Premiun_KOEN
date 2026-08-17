"""Phase-3 D-04 한국어 형태소 feature 추출 (NB04) 엔지니어링 구현.

SSOT 범위: 형태소 분석은 tokenizer pipeline 내부 단계가 아니며, 한국어 표면형의
문법적·구조적 특징(조사·어미·파생접사 밀도)만 정량화한다. tokenizer/BPE 경계,
POS 전체 목록, 도메인별 custom dictionary, analyzer 정규화 텍스트의 tokenizer
재사용은 이 모듈의 범위 밖이다.
"""

from __future__ import annotations

import datetime as dt
import time
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import duckdb
import kiwipiepy
import pyarrow as pa
from kiwipiepy import Kiwi

from tokenization_premium.hashing import canonical_json_bytes, sha256_bytes, sha256_file
from tokenization_premium.phase2 import _fetchone_required, write_parquet_batches_atomic
from tokenization_premium.progress import ProgressHeartbeat
from tokenization_premium.representation import COHORT_FILTER_SQL

_KST = ZoneInfo("Asia/Seoul")

MORPHOLOGY_RULE_VERSION = "morph_v001"  # 이 추출 규칙의 고정 버전 문자열이다.
MORPH_FEATURES_SCHEMA_VERSION = "MORPH_FEATURES_v001"  # 출력 schema 버전을 고정한다.
MORPH_FEATURES_RELATIVE_PATH = Path("data/registry/MORPH_FEATURES_v001.parquet")  # canonical 출력 경로를 고정한다.
ANALYZER_PACKAGE_VERSION = kiwipiepy.__version__  # 실제 설치된 kiwipiepy 버전을 provenance로 남긴다.
ANALYZER_MODEL_VERSION = "0.23.0"  # outputs/manifests/KIWI_MODEL_ARTIFACT_v001.json의 검증된 model version과 동일하다.
ANALYZER_MODEL_MANIFEST_SHA256 = "3baa52f40876b78dab7e9428f2e488ca2ae3ed6b3d813df17f72e15a61fc516a"  # Phase-0에서 검증된 model manifest hash다.

MORPHOLOGY_CONFIG: dict[str, Any] = {
    "rule_version": MORPHOLOGY_RULE_VERSION,
    "input_text_field": "ko_text_analysis",
    "analyzer": "kiwipiepy.Kiwi() default constructor, custom_dictionary_used=False",
    "particle_tag_rule": "tag.startswith('J')",
    "ending_tag_rule": "tag.startswith('E')",
    "deriv_affix_tags": ["XSN", "XSV", "XSA"],
    "function_morpheme_rule": "particle OR ending",
    "morpheme_density_denominator": "ko_codepoint_count",
    "cohort_filter_sql": COHORT_FILTER_SQL,
}  # feature 정의를 하나의 dict로 고정해 config_sha256으로 provenance를 남긴다.
MORPHOLOGY_CONFIG_SHA256 = sha256_bytes(canonical_json_bytes(MORPHOLOGY_CONFIG))  # config 변경 여부를 hash 하나로 검증 가능하게 한다.

_DERIV_AFFIX_TAGS = frozenset({"XSN", "XSV", "XSA"})  # 명사파생/동사파생/형용사파생 접미사 tag다.


class MorphologyInputError(ValueError):
    """빈 문자열 등 accepted cohort에서 나타날 수 없는 입력을 명시적으로 거부한다."""


_KIWI_SINGLETON: Kiwi | None = None  # process당 한 번만 model을 로드해 pilot/full 실행 비용을 낮춘다.


def get_kiwi() -> Kiwi:
    """
    /**
     * @purpose 승인된 기본 구성(custom dictionary 없음)의 Kiwi analyzer를 lazily 로드한다.
     * @spec_ref Directive Task 9 (POS zoo/custom dictionary 금지)
     * @return kiwipiepy.Kiwi 싱글턴 인스턴스
     * @raises 없음
     * @validation analyzer_package_version이 kiwipiepy.__version__과 일치하는지 검사한다.
     * @artifact MORPH_FEATURES_v001.parquet
     */
    """
    global _KIWI_SINGLETON
    if _KIWI_SINGLETON is None:
        _KIWI_SINGLETON = Kiwi()  # 기본 생성자만 사용하고 도메인별 custom dictionary를 추가하지 않는다.
    return _KIWI_SINGLETON


def morphology_features(text: str, *, codepoint_count: int, kiwi: Kiwi | None = None) -> dict[str, int | float]:
    """
    /**
     * @purpose 한국어 원문에서 D-04 형태소 밀도/조사/어미/파생접사 비율 feature를 계산한다.
     * @spec_ref SSOT §3.1 형태소 밀도·조사·어미·접사; Directive Task 9 primary/alternative feature
     * @param text ko_text_analysis 문자열 (accepted cohort는 empty 불가)
     * @param codepoint_count representation.py의 ko_codepoint_count (밀도 분모로 재사용, 이중 계산 방지)
     * @param kiwi 재사용할 Kiwi 인스턴스 (없으면 get_kiwi()로 lazy 로드)
     * @return morpheme_count/density, particle/ending/deriv_affix/function_morpheme ratio
     * @raises MorphologyInputError 빈 문자열이 전달된 경우
     * @raises ValueError codepoint_count가 0 이하인 경우
     * @validation particle_ratio+ending_ratio<=1, 각 ratio가 [0,1] 범위인지 단위 테스트로 검사한다.
     * @artifact MORPH_FEATURES_v001.parquet의 ko_morph_* 열
     */
    """
    if text == "":
        raise MorphologyInputError("accepted cohort의 텍스트는 empty일 수 없다: morphology_features는 빈 문자열을 거부한다")
    if codepoint_count <= 0:
        raise ValueError("codepoint_count는 0보다 커야 한다")

    analyzer = kiwi if kiwi is not None else get_kiwi()
    result = analyzer.analyze(text, top_n=1)  # 최상위 1개 분석만 사용하며 대안 분석은 사용하지 않는다.
    morphs = result[0][0] if result else []  # 분석 결과가 비어 있으면 형태소 0개로 처리한다.
    morpheme_count = len(morphs)

    particle_count = 0
    ending_count = 0
    deriv_affix_count = 0
    for morph in morphs:  # 전체 POS tag를 나열하지 않고 3개 그룹만 분류한다 (POS zoo 금지).
        tag = morph.tag
        if tag.startswith("J"):
            particle_count += 1
        elif tag.startswith("E"):
            ending_count += 1
        elif tag in _DERIV_AFFIX_TAGS:
            deriv_affix_count += 1
    function_morpheme_count = particle_count + ending_count

    denominator = morpheme_count if morpheme_count > 0 else 1  # 형태소가 0개인 극단적 입력에서도 0-division을 피한다.
    return {
        "morpheme_count": morpheme_count,
        "morpheme_density": morpheme_count / codepoint_count,
        "particle_ratio": particle_count / denominator,
        "ending_ratio": ending_count / denominator,
        "deriv_affix_ratio": deriv_affix_count / denominator,
        "function_morpheme_ratio": function_morpheme_count / denominator,
    }


def morph_features_schema() -> pa.Schema:
    """
    /**
     * @purpose MORPH_FEATURES_v001 Parquet의 명시적 column 순서·dtype 계약을 고정한다.
     * @spec_ref Directive Task 9
     * @return pair_id, ko_morph_* 6개, provenance 4개를 포함하는 PyArrow schema
     * @raises 없음
     * @validation 저장된 Parquet의 schema와 exact equality로 검사한다.
     * @artifact data/registry/MORPH_FEATURES_v001.parquet
     */
    """
    return pa.schema(
        [
            pa.field("pair_id", pa.string(), nullable=False),
            pa.field("ko_morpheme_count", pa.int64(), nullable=False),
            pa.field("ko_morpheme_density", pa.float64(), nullable=False),
            pa.field("ko_particle_ratio", pa.float64(), nullable=False),
            pa.field("ko_ending_ratio", pa.float64(), nullable=False),
            pa.field("ko_deriv_affix_ratio", pa.float64(), nullable=False),
            pa.field("ko_function_morpheme_ratio", pa.float64(), nullable=False),
            pa.field("analyzer_name", pa.string(), nullable=False),
            pa.field("analyzer_package_version", pa.string(), nullable=False),
            pa.field("analyzer_model_version", pa.string(), nullable=False),
            pa.field("config_sha256", pa.string(), nullable=False),
        ]
    )


def _sql_literal(path: Path) -> str:
    return "'" + str(path).replace("'", "''") + "'"


def execute_morphology_run(
    *,
    project_root: Path,
    input_path: Path,
    output_path: Path,
    runtime_dir: Path,
    run_id: str,
    limit: int,
    batch_size: int = 500,
) -> dict[str, Any]:
    """
    /**
     * @purpose bounded pilot(또는 향후 full population) 범위에서 D-04 형태소 feature를 계산해
     *          MORPH_FEATURES 후보 Parquet을 atomic하게 생성하고 pair당 latency를 측정한다.
     * @spec_ref Directive Task 9 (pilot ~1,000행, full 3.8M 예상 runtime 보고)
     * @param input_path PAIR_REGISTRY_v002.parquet 경로 (representation feature와 동일 cohort)
     * @param output_path 목적지 Parquet (pilot은 별도 경로 사용, canonical 경로 아님)
     * @param limit 처리할 행 수 (반드시 명시; 이 함수 호출만으로 3.8M full run이 우발 실행되지 않는다)
     * @return row_count, output sha256, pair당 평균 latency, 3.8M 기준 예상 전체 runtime
     * @raises FileExistsError 목적지 또는 partial이 이미 존재하는 경우
     * @validation row/pair_id 유일성, ratio 범위를 promotion 전에 검사한다.
     * @artifact MORPH_FEATURES pilot candidate parquet
     */
    """
    output_partial = output_path.with_suffix(output_path.suffix + ".partial")
    if output_path.exists() or output_partial.exists():
        raise FileExistsError("MORPH_FEATURES 목적지 또는 partial이 이미 존재한다; 자동 재시작은 금지된다")

    schema = morph_features_schema()
    start = dt.datetime.now(tz=_KST)
    stage_started = time.monotonic()
    runtime_dir.mkdir(parents=True, exist_ok=True)
    progress_dir = runtime_dir.parent / "progress"
    kiwi = get_kiwi()

    connection = duckdb.connect()
    try:
        relation = f"read_parquet({_sql_literal(input_path)})"
        query = f"""
            SELECT pair_id, ko_codepoint_count
            FROM (
                SELECT r.pair_id, r.ko_codepoint_count
                FROM read_parquet({_sql_literal(project_root / 'data/registry/REP_FEATURES_v001.parquet')}) r
                JOIN {relation} p USING (pair_id)
                WHERE {COHORT_FILTER_SQL.replace('pair_quality_status', 'p.pair_quality_status').replace('analysis_eligible_exact_dedup', 'p.analysis_eligible_exact_dedup').replace('logical_corpus', 'p.logical_corpus')}
                ORDER BY r.pair_id
            )
            LIMIT {int(limit)}
        """
        # pair_id/ko_codepoint_count는 representation feature에서 재사용하고, 원문은 별도 조회한다.
        id_and_len = connection.execute(query).fetchall()
        text_query = f"""
            SELECT pair_id, ko_text_analysis
            FROM {relation}
            WHERE pair_id IN (SELECT unnest(?))
        """
        pair_ids = [row[0] for row in id_and_len]
        codepoint_by_id = {row[0]: row[1] for row in id_and_len}
        text_rows = connection.execute(text_query, [pair_ids]).fetchall()
        text_by_id = {row[0]: row[1] for row in text_rows}

        total = len(pair_ids)
        with ProgressHeartbeat(
            run_id=run_id,
            phase="NB04",
            stage="MORPHOLOGY_PILOT",
            total=total,
            progress_dir=progress_dir,
        ) as heartbeat:
            records = []
            for pair_id in pair_ids:
                features = morphology_features(
                    text_by_id[pair_id], codepoint_count=codepoint_by_id[pair_id], kiwi=kiwi
                )
                record = {"pair_id": pair_id, **{f"ko_{name}": value for name, value in features.items()}}
                record["analyzer_name"] = "Kiwi"
                record["analyzer_package_version"] = ANALYZER_PACKAGE_VERSION
                record["analyzer_model_version"] = ANALYZER_MODEL_VERSION
                record["config_sha256"] = MORPHOLOGY_CONFIG_SHA256
                records.append(record)
                heartbeat.update(1)

            def validate(path: Path) -> None:
                _validate_morph_features(path, expected_rows=total)

            batch = pa.RecordBatch.from_pylist(records, schema=schema)
            write_result = write_parquet_batches_atomic(output_path, schema, [batch], validate=validate)
            heartbeat.checkpoint("MORPH_FEATURES_WRITTEN", rows=write_result.row_count)
    finally:
        connection.close()

    stage_duration = round(time.monotonic() - stage_started, 3)
    per_pair_latency_sec = stage_duration / total if total > 0 else None
    projected_full_population_sec = per_pair_latency_sec * 3_836_013 if per_pair_latency_sec is not None else None
    output_sha256 = sha256_file(output_path)
    end = dt.datetime.now(tz=_KST)
    return {
        "artifact_id": "MORPH_FEATURES_PILOT_MANIFEST_v001",
        "run_id": run_id,
        "run_mode": "PILOT",
        "input": {"path": str(input_path.relative_to(project_root)), "sha256": sha256_file(input_path)},
        "output": {
            "path": str(output_path.relative_to(project_root)),
            "sha256": output_sha256,
            "row_count": write_result.row_count,
            "column_count": len(schema.names),
            "schema_version": MORPH_FEATURES_SCHEMA_VERSION,
        },
        "analyzer_package_version": ANALYZER_PACKAGE_VERSION,
        "analyzer_model_version": ANALYZER_MODEL_VERSION,
        "analyzer_model_manifest_sha256": ANALYZER_MODEL_MANIFEST_SHA256,
        "config_sha256": MORPHOLOGY_CONFIG_SHA256,
        "start_kst": start.isoformat(timespec="seconds"),
        "end_kst": end.isoformat(timespec="seconds"),
        "stage_duration_sec": stage_duration,
        "per_pair_latency_sec": per_pair_latency_sec,
        "projected_full_population_3836013_rows_sec": projected_full_population_sec,
        "projected_full_population_3836013_rows_min": (
            round(projected_full_population_sec / 60, 2) if projected_full_population_sec is not None else None
        ),
        "validation_status": "PASS",
        "status": "PILOT_ONLY_FULL_RUN_DEFERRED",
    }


def _validate_morph_features(path: Path, *, expected_rows: int) -> None:
    """row 수, pair_id 유일성, ratio invariant를 promotion 직전에 검사한다."""
    connection = duckdb.connect()
    try:
        relation = f"read_parquet({_sql_literal(path)})"
        row_count, distinct_pair_id = _fetchone_required(
            connection.execute(f"SELECT count(*), count(DISTINCT pair_id) FROM {relation}")
        )
        if int(row_count) != expected_rows or int(distinct_pair_id) != expected_rows:
            raise ValueError("MORPH_FEATURES row count 또는 pair_id 유일성 검증 실패")
        bad_rows = _fetchone_required(
            connection.execute(
                f"""
                SELECT count(*) FROM {relation}
                WHERE ko_morpheme_count < 0
                   OR ko_particle_ratio < 0 OR ko_particle_ratio > 1
                   OR ko_ending_ratio < 0 OR ko_ending_ratio > 1
                   OR ko_deriv_affix_ratio < 0 OR ko_deriv_affix_ratio > 1
                   OR ko_function_morpheme_ratio < 0 OR ko_function_morpheme_ratio > 1
                   OR NOT isfinite(ko_morpheme_density)
                """
            )
        )[0]
        if int(bad_rows) != 0:
            raise ValueError("MORPH_FEATURES ratio invariant 검증 실패")
    finally:
        connection.close()


__all__ = [
    "ANALYZER_MODEL_MANIFEST_SHA256",
    "ANALYZER_MODEL_VERSION",
    "ANALYZER_PACKAGE_VERSION",
    "MORPHOLOGY_CONFIG",
    "MORPHOLOGY_CONFIG_SHA256",
    "MORPHOLOGY_RULE_VERSION",
    "MORPH_FEATURES_RELATIVE_PATH",
    "MORPH_FEATURES_SCHEMA_VERSION",
    "MorphologyInputError",
    "execute_morphology_run",
    "get_kiwi",
    "morph_features_schema",
    "morphology_features",
]
