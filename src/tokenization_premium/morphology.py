"""Phase-3 D-03 한국어 형태소 측정 (NB04) 엔지니어링 구현.

SSOT 범위: 형태소 분석은 tokenizer pipeline 내부 단계가 아니며, 한국어 표면형의
문법적·구조적 특징(조사·어미·파생접사 밀도)만 정량화한다. tokenizer/BPE 경계,
POS 전체 목록, 도메인별 custom dictionary, analyzer 정규화 텍스트의 tokenizer
재사용은 이 모듈의 범위 밖이다.

Conformance decision: RD-20260817-D02D03-CONFORMANCE-01
  M1  morpheme_density 분모를 codepoint_count -> eojeol_count (SSOT §13.6)
  M2  tag 분류를 base_tag = tag.partition("-")[0] 기준으로 정규화 (XSA-I 등 포함)
  M3  D-03 required schema 전체 구현 (measurement id / config hash / sequence / counts / warning)
  M4  zero-morpheme silent denominator=1 제거, ratio는 null
  M5  3_836_013 하드코딩 제거, expected population을 실제 입력에서 derive
"""

from __future__ import annotations

import datetime as dt
import time
from collections import Counter
from collections.abc import Iterable, Iterator, Sequence
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

MORPHOLOGY_RULE_VERSION = "morph_v002"  # conformance 복원 이후의 규칙 버전이다.
MORPH_FEATURES_SCHEMA_VERSION = "MORPH_FEATURES_v002"  # 출력 schema 버전을 고정한다.
MORPH_FEATURES_RELATIVE_PATH = Path("data/registry/MORPH_FEATURES_v002.parquet")  # canonical 출력 경로를 고정한다.
ANALYZER_NAME = "Kiwi"
ANALYZER_PACKAGE_VERSION = kiwipiepy.__version__  # 실제 설치된 kiwipiepy 버전을 provenance로 남긴다.
ANALYZER_MODEL_VERSION = "0.23.0"  # outputs/manifests/KIWI_MODEL_ARTIFACT_v001.json의 검증된 model version과 동일하다.
ANALYZER_MODEL_MANIFEST_SHA256 = "3baa52f40876b78dab7e9428f2e488ca2ae3ed6b3d813df17f72e15a61fc516a"  # Phase-0 검증 hash다.

_DERIV_AFFIX_BASE_TAGS = frozenset({"XSN", "XSV", "XSA"})  # 명사/동사/형용사 파생 접미사 base tag다.

MORPHOLOGY_CONFIG: dict[str, Any] = {
    "rule_version": MORPHOLOGY_RULE_VERSION,
    "decision_id": "RD-20260817-D02D03-CONFORMANCE-01",
    "input_text_field": "ko_text_analysis",
    "analyzer": "kiwipiepy.Kiwi() default constructor, custom_dictionary_used=False",
    "analyze_top_n": 1,
    "tag_base_rule": 'base_tag = tag.partition("-")[0]',
    "particle_tag_rule": 'base_tag.startswith("J")',
    "ending_tag_rule": 'base_tag.startswith("E")',
    "deriv_affix_base_tags": sorted(_DERIV_AFFIX_BASE_TAGS),
    "deriv_affix_rule": "base_tag in {XSN, XSV, XSA} (XSA-I / XSA-R 등 irregular variant 포함)",
    "function_morpheme_rule": "particle OR ending",
    "morpheme_density_denominator": "eojeol_count",
    "morpheme_density_spec_ref": "SSOT §13.6 MorphemeDensity = MorphemeCount / EojeolCount",
    "ratio_denominator": "morpheme_count",
    "ratio_spec_ref": "SSOT §13.7 ParticleRatio/EndingRatio = Count / MorphemeCount",
    "zero_morpheme_policy": (
        "pair를 유지하고 analysis_warning_flag=true를 기록한다. "
        "분모가 morpheme_count인 ratio는 null이며 대체 분모를 쓰지 않는다."
    ),
    "zero_eojeol_policy": "accepted cohort에서 eojeol_count == 0 이면 HARD_INVALID로 거부한다",
    "cohort_filter_sql": COHORT_FILTER_SQL,
}  # feature 정의를 하나의 dict로 고정해 analyzer_config_hash로 provenance를 남긴다.
MORPHOLOGY_CONFIG_SHA256 = sha256_bytes(canonical_json_bytes(MORPHOLOGY_CONFIG))

WARNING_NONE = "NONE"
WARNING_ZERO_MORPHEME = "ZERO_MORPHEME_OUTPUT"


class MorphologyInputError(ValueError):
    """빈 문자열 등 accepted cohort에서 나타날 수 없는 입력을 명시적으로 거부한다."""


class MorphologyHardInvalidError(ValueError):
    """accepted cohort에서 성립할 수 없는 분모(eojeol_count == 0)를 HARD_INVALID로 거부한다."""


_KIWI_SINGLETON: Kiwi | None = None
_KIWI_SINGLETON_WORKERS: int | None = None


def get_kiwi(num_workers: int | None = None) -> Kiwi:
    """
    /**
     * @purpose 승인된 기본 구성(custom dictionary 없음)의 Kiwi analyzer를 lazily 로드한다.
     * @spec_ref SSOT §15.1 primary analyzer; §15.2 분석 금지 사항
     * @param num_workers Kiwi가 iterable 입력을 처리할 때 사용할 thread 수 (None이면 kiwipiepy 기본값)
     * @return kiwipiepy.Kiwi 싱글턴 인스턴스
     * @raises 없음
     * @validation num_workers가 바뀌면 새 instance를 만들어 benchmark 간 오염을 막는다.
     * @artifact MORPH_FEATURES_v002.parquet
     */
    """
    global _KIWI_SINGLETON, _KIWI_SINGLETON_WORKERS
    if _KIWI_SINGLETON is None or num_workers != _KIWI_SINGLETON_WORKERS:
        _KIWI_SINGLETON = Kiwi() if num_workers is None else Kiwi(num_workers=num_workers)
        _KIWI_SINGLETON_WORKERS = num_workers
    return _KIWI_SINGLETON


def base_tag(tag: str) -> str:
    """
    /**
     * @purpose Kiwi tag에서 irregular variant suffix를 제거한 base tag를 얻는다.
     * @spec_ref SSOT §12.3 POS feature mapping; conformance finding M2
     * @param tag Kiwi Token.tag (예: "XSA", "XSA-I", "VA-I", "JKS")
     * @return "-" 앞부분의 base tag
     * @raises 없음
     * @validation XSA-I/XSA-R이 XSA family로 분류되는지 회귀 테스트로 검사한다.
     * @artifact MORPH_FEATURES_v002.parquet의 deriv_affix_count
     */
    """
    return tag.partition("-")[0]


def classify_tag(tag: str) -> str | None:
    """
    /**
     * @purpose 하나의 Kiwi tag를 particle/ending/deriv_affix 중 하나로 분류한다 (POS zoo 금지).
     * @spec_ref SSOT §12.3 (Particle J*, Ending E*, Derivational affix XSN/XSV/XSA)
     * @param tag Kiwi Token.tag
     * @return "particle" | "ending" | "deriv_affix" | None (세 group 어디에도 속하지 않음)
     * @raises 없음
     * @validation base_tag 정규화가 J*/E* 분류를 바꾸지 않음을 테스트로 검사한다.
     * @artifact MORPH_FEATURES_v002.parquet의 particle/ending/deriv_affix_count
     */
    """
    base = base_tag(tag)
    if base.startswith("J"):
        return "particle"
    if base.startswith("E"):
        return "ending"
    if base in _DERIV_AFFIX_BASE_TAGS:
        return "deriv_affix"
    return None


def features_from_morphs(morphs: Sequence[Any], *, eojeol_count: int) -> dict[str, Any]:
    """
    /**
     * @purpose 이미 분석된 형태소 sequence에서 D-03 count/ratio/warning을 계산한다.
     * @spec_ref SSOT §12.3 D-03; §13.6 MorphemeDensity; §13.7 Particle/Ending Ratio
     * @param morphs Kiwi Token sequence (form/tag 속성을 가진 객체)
     * @param eojeol_count D-02 ko_eojeol_count (SSOT §13.6 density 분모)
     * @return morpheme_sequence, 4개 count, density, 4개 ratio, analysis_warning_flag/reason
     * @raises MorphologyHardInvalidError eojeol_count가 0 이하인 경우
     * @validation morpheme_count == 0 이면 morpheme_count 분모 ratio가 모두 null인지 검사한다.
     * @artifact MORPH_FEATURES_v002.parquet
     */
    """
    if eojeol_count <= 0:
        raise MorphologyHardInvalidError(
            "HARD_INVALID: accepted cohort에서 eojeol_count는 0보다 커야 한다 (SSOT §13.6 density 분모)"
        )

    sequence: list[dict[str, str]] = []
    particle_count = ending_count = deriv_affix_count = 0
    for morph in morphs:
        tag = morph.tag
        sequence.append({"form": morph.form, "pos": tag})
        kind = classify_tag(tag)
        if kind == "particle":
            particle_count += 1
        elif kind == "ending":
            ending_count += 1
        elif kind == "deriv_affix":
            deriv_affix_count += 1

    morpheme_count = len(sequence)
    function_morpheme_count = particle_count + ending_count
    zero_output = morpheme_count == 0

    # 분모가 morpheme_count인 ratio는 형태소가 0개일 때 정의되지 않는다 -> null (대체 분모 금지).
    def ratio(numerator: int) -> float | None:
        return None if zero_output else numerator / morpheme_count

    return {
        "morpheme_sequence": sequence,
        "morpheme_count": morpheme_count,
        "particle_count": particle_count,
        "ending_count": ending_count,
        "deriv_affix_count": deriv_affix_count,
        # density 분모는 eojeol_count이며 accepted cohort에서 항상 > 0 이므로 언제나 정의된다.
        "morpheme_density": morpheme_count / eojeol_count,
        "particle_ratio": ratio(particle_count),
        "ending_ratio": ratio(ending_count),
        "deriv_affix_ratio": ratio(deriv_affix_count),
        "function_morpheme_ratio": ratio(function_morpheme_count),
        "analysis_warning_flag": zero_output,
        "analysis_warning_reason": WARNING_ZERO_MORPHEME if zero_output else WARNING_NONE,
    }


def morphology_features(text: str, *, eojeol_count: int, kiwi: Kiwi | None = None) -> dict[str, Any]:
    """
    /**
     * @purpose 단일 한국어 원문에서 D-03 형태소 측정값을 계산한다 (scalar reference path).
     * @spec_ref SSOT §12.3 D-03; §13.6; §13.7
     * @param text ko_text_analysis 문자열 (accepted cohort는 empty 불가)
     * @param eojeol_count D-02 ko_eojeol_count (REP_FEATURES_v002에서 전달)
     * @param kiwi 재사용할 Kiwi 인스턴스 (없으면 get_kiwi()로 lazy 로드)
     * @return features_from_morphs와 동일한 dict
     * @raises MorphologyInputError 빈 문자열이 전달된 경우
     * @raises MorphologyHardInvalidError eojeol_count가 0 이하인 경우
     * @validation optimized batch path와 exact equality를 갖는 reference로 사용한다.
     * @artifact MORPH_FEATURES_v002.parquet
     */
    """
    if text == "":
        raise MorphologyInputError("accepted cohort의 텍스트는 empty일 수 없다: morphology_features는 빈 문자열을 거부한다")
    analyzer = kiwi if kiwi is not None else get_kiwi()
    result = analyzer.analyze(text, top_n=1)  # 최상위 1개 분석만 사용하며 대안 분석은 사용하지 않는다.
    morphs = result[0][0] if result else []
    return features_from_morphs(morphs, eojeol_count=eojeol_count)


def analyze_batch(texts: Sequence[str], *, kiwi: Kiwi) -> list[list[Any]]:
    """
    /**
     * @purpose Kiwi native iterable API로 batch를 멀티스레드 분석한다 (optimized path).
     * @spec_ref Directive §11 우선순위 1 (Kiwi native iterable/multiworker API)
     * @param texts 분석할 원문 sequence
     * @param kiwi num_workers가 설정된 Kiwi 인스턴스
     * @return 입력 순서와 동일한 Token list의 list
     * @raises 없음
     * @validation scalar path와 exact output equality gate로 검증한다.
     * @artifact MORPH_FEATURES_v002.parquet
     */
    """
    # Kiwi 문서: Iterable[str]을 주면 생성 시 num_workers로 멀티스레드 분배하며, 결과는 입력 순서를 유지한다.
    return [result[0][0] if result else [] for result in kiwi.analyze(list(texts), top_n=1)]


def morph_measurement_id(pair_id: str) -> str:
    """
    /**
     * @purpose (config, pair)에 대해 결정적이고 유일한 D-03 측정 ID를 만든다.
     * @spec_ref SSOT §12.3 morph_measurement_id
     * @param pair_id D-01 pair key
     * @return 재실행해도 동일한 deterministic ID
     * @raises 없음
     * @validation pilot에서 distinct id == row count인지 검사한다.
     * @artifact MORPH_FEATURES_v002.parquet의 morph_measurement_id
     */
    """
    payload = f"{MORPH_FEATURES_SCHEMA_VERSION}|{MORPHOLOGY_CONFIG_SHA256}|{pair_id}"
    return "morph_" + sha256_bytes(payload.encode("utf-8"))


def morph_features_schema() -> pa.Schema:
    """
    /**
     * @purpose MORPH_FEATURES_v002 Parquet의 SSOT §12.3 D-03 전체 계약을 고정한다.
     * @spec_ref SSOT §12.3 D-03 Morphology Measurement; conformance finding M3
     * @return D-03 required field를 모두 포함하는 PyArrow schema
     * @raises 없음
     * @validation configs/morphology_v1.yaml measurement_schema_ref.fields를 모두 포함하는지 검사한다.
     * @artifact data/registry/MORPH_FEATURES_v002.parquet
     */
    """
    morpheme_struct = pa.list_(
        pa.field(
            "item",
            pa.struct([pa.field("form", pa.string(), nullable=False), pa.field("pos", pa.string(), nullable=False)]),
            nullable=False,
        )
    )
    return pa.schema(
        [
            pa.field("morph_measurement_id", pa.string(), nullable=False),
            pa.field("pair_id", pa.string(), nullable=False),
            pa.field("analyzer_name", pa.string(), nullable=False),
            pa.field("analyzer_package_version", pa.string(), nullable=False),
            pa.field("analyzer_model_version", pa.string(), nullable=False),
            pa.field("analyzer_config_hash", pa.string(), nullable=False),
            pa.field("morpheme_sequence", morpheme_struct, nullable=False),
            pa.field("eojeol_count", pa.int64(), nullable=False),
            pa.field("morpheme_count", pa.int64(), nullable=False),
            pa.field("particle_count", pa.int64(), nullable=False),
            pa.field("ending_count", pa.int64(), nullable=False),
            pa.field("deriv_affix_count", pa.int64(), nullable=False),
            pa.field("morpheme_density", pa.float64(), nullable=False),
            # morpheme_count 분모 ratio는 zero-morpheme 행에서 null이어야 하므로 nullable이다.
            pa.field("particle_ratio", pa.float64(), nullable=True),
            pa.field("ending_ratio", pa.float64(), nullable=True),
            pa.field("deriv_affix_ratio", pa.float64(), nullable=True),
            pa.field("function_morpheme_ratio", pa.float64(), nullable=True),
            pa.field("analysis_warning_flag", pa.bool_(), nullable=False),
            pa.field("analysis_warning_reason", pa.string(), nullable=False),
        ]
    )


def build_record(pair_id: str, morphs: Sequence[Any], *, eojeol_count: int) -> dict[str, Any]:
    """분석 결과를 morph_features_schema() 순서의 record dict로 조립한다."""
    features = features_from_morphs(morphs, eojeol_count=eojeol_count)
    return {
        "morph_measurement_id": morph_measurement_id(pair_id),
        "pair_id": pair_id,
        "analyzer_name": ANALYZER_NAME,
        "analyzer_package_version": ANALYZER_PACKAGE_VERSION,
        "analyzer_model_version": ANALYZER_MODEL_VERSION,
        "analyzer_config_hash": MORPHOLOGY_CONFIG_SHA256,
        "eojeol_count": eojeol_count,
        **features,
    }


def _sql_literal(path: Path) -> str:
    return "'" + str(path).replace("'", "''") + "'"


def cohort_reader(
    connection: duckdb.DuckDBPyConnection,
    *,
    rep_features_v002_path: Path,
    pair_registry_path: Path,
    batch_rows: int,
    limit: int | None = None,
) -> pa.RecordBatchReader:
    """
    /**
     * @purpose final cohort의 (pair_id, ko_text_analysis, ko_eojeol_count)를 streaming으로 읽는다.
     * @spec_ref Directive §16 bounded-memory pipeline
     * @param rep_features_v002_path ko_eojeol_count를 제공하는 D-02 v002 artifact
     * @param pair_registry_path ko_text_analysis 원문을 제공하는 P2 artifact
     * @param batch_rows 한 번에 가져올 행 수 (RAM 상한을 결정한다)
     * @return Arrow RecordBatchReader (전체를 RAM에 올리지 않는다)
     * @raises 없음
     * @validation row count를 호출자가 expected population과 대조한다.
     * @artifact 없음 (reader)
     */
    """
    limit_clause = f" LIMIT {int(limit)}" if limit is not None else ""
    query = (
        "SELECT r.pair_id, p.ko_text_analysis AS ko_text, r.ko_eojeol_count AS eojeol_count "
        f"FROM read_parquet({_sql_literal(rep_features_v002_path)}) r "
        f"JOIN read_parquet({_sql_literal(pair_registry_path)}) p USING (pair_id) "
        "ORDER BY r.pair_id" + limit_clause
    )
    return connection.execute(query).fetch_record_batch(batch_rows)


def _record_batches(
    reader: pa.RecordBatchReader,
    *,
    schema: pa.Schema,
    kiwi: Kiwi,
    heartbeat: ProgressHeartbeat,
    stats: dict[str, Any],
) -> Iterator[pa.RecordBatch]:
    """batch 단위로 분석 -> record -> RecordBatch를 yield하고 즉시 메모리를 놓아준다."""
    tag_counter: Counter[str] = stats["base_tag_counter"]
    raw_tag_counter: Counter[str] = stats["raw_tag_counter"]
    for batch in reader:
        pair_ids = batch.column("pair_id").to_pylist()
        texts = batch.column("ko_text").to_pylist()
        eojeol_counts = batch.column("eojeol_count").to_pylist()
        analyses = analyze_batch(texts, kiwi=kiwi)
        records = []
        for pair_id, morphs, eojeol_count in zip(pair_ids, analyses, eojeol_counts, strict=True):
            for morph in morphs:
                raw_tag_counter[morph.tag] += 1
                tag_counter[base_tag(morph.tag)] += 1
            record = build_record(pair_id, morphs, eojeol_count=eojeol_count)
            if record["analysis_warning_flag"]:
                stats["zero_morpheme_rows"] += 1
            records.append(record)
        stats["rows"] += len(records)
        yield pa.RecordBatch.from_pylist(records, schema=schema)
        heartbeat.update(len(records))
        del pair_ids, texts, eojeol_counts, analyses, records, batch  # bounded memory


def execute_morphology_run(
    *,
    project_root: Path,
    rep_features_v002_path: Path,
    pair_registry_path: Path,
    output_path: Path,
    runtime_dir: Path,
    run_id: str,
    run_mode: str,
    limit: int | None,
    num_workers: int | None = None,
    batch_rows: int = 10_000,
    expected_rows: int | None = None,
) -> dict[str, Any]:
    """
    /**
     * @purpose bounded-memory streaming으로 D-03 형태소 측정 artifact를 생성한다.
     * @spec_ref SSOT §12.3; Directive §16 memory architecture; ENG-OBS-001 heartbeat
     * @param limit None이면 전체 cohort (full run), 정수면 pilot 범위
     * @param num_workers Kiwi iterable 분석에 쓸 thread 수
     * @param expected_rows 검증에 쓸 기대 행 수 (None이면 입력에서 derive; 하드코딩 상수 없음)
     * @return manifest dict (row count, sha256, runtime, warning/tag 통계)
     * @raises FileExistsError 목적지 또는 partial이 이미 존재하는 경우
     * @validation row/pair_id 유일성, ratio 범위, warning 규약을 promotion 전에 검사한다.
     * @artifact MORPH_FEATURES parquet + manifest
     */
    """
    output_partial = output_path.with_suffix(output_path.suffix + ".partial")
    if output_path.exists() or output_partial.exists():
        raise FileExistsError("MORPH_FEATURES 목적지 또는 partial이 이미 존재한다; 자동 재시작은 금지된다")

    schema = morph_features_schema()
    start = dt.datetime.now(tz=_KST)
    runtime_dir.mkdir(parents=True, exist_ok=True)
    progress_dir = project_root / ".runtime" / "progress"

    connection = duckdb.connect()
    try:
        # M5: 기대 행 수는 실제 입력에서 derive하며 population 상수를 코드에 두지 않는다.
        if expected_rows is None:
            total_available = int(
                _fetchone_required(
                    connection.execute(
                        f"SELECT count(*) FROM read_parquet({_sql_literal(rep_features_v002_path)})"
                    )
                )[0]
            )
            expected_rows = total_available if limit is None else min(limit, total_available)

        kiwi = get_kiwi(num_workers)
        # warm-up: lazy initialization 비용을 측정 구간에서 제외한다.
        warm_start = time.monotonic()
        analyze_batch(["형태소 분석기 워밍업 문장입니다"], kiwi=kiwi)
        warmup_sec = round(time.monotonic() - warm_start, 3)

        stage_started = time.monotonic()
        reader = cohort_reader(
            connection,
            rep_features_v002_path=rep_features_v002_path,
            pair_registry_path=pair_registry_path,
            batch_rows=batch_rows,
            limit=limit,
        )
        stats: dict[str, Any] = {
            "rows": 0,
            "zero_morpheme_rows": 0,
            "base_tag_counter": Counter(),
            "raw_tag_counter": Counter(),
        }
        with ProgressHeartbeat(
            run_id=run_id,
            phase="NB04",
            stage="MORPHOLOGY",
            total=expected_rows,
            progress_dir=progress_dir,
        ) as heartbeat:
            def validate(path: Path) -> None:
                validate_morph_features(path, expected_rows=expected_rows)

            write_result = write_parquet_batches_atomic(
                output_path,
                schema,
                _record_batches(reader, schema=schema, kiwi=kiwi, heartbeat=heartbeat, stats=stats),
                validate=validate,
            )
            heartbeat.checkpoint("MORPH_FEATURES_WRITTEN", rows=write_result.row_count)
        stage_duration = round(time.monotonic() - stage_started, 3)
    finally:
        connection.close()

    per_pair_latency_sec = stage_duration / write_result.row_count if write_result.row_count else None
    raw_tags: Counter[str] = stats["raw_tag_counter"]
    base_tags: Counter[str] = stats["base_tag_counter"]
    irregular = {tag: count for tag, count in raw_tags.items() if "-" in tag}
    end = dt.datetime.now(tz=_KST)

    return {
        "artifact_id": f"MORPH_FEATURES_MANIFEST_{run_mode}_v002",
        "run_id": run_id,
        "run_mode": run_mode,
        "decision_id": "RD-20260817-D02D03-CONFORMANCE-01",
        "input": {
            "rep_features_v002": {
                "path": str(rep_features_v002_path.relative_to(project_root)),
                "sha256": sha256_file(rep_features_v002_path),
            },
            "pair_registry_v002": {
                "path": str(pair_registry_path.relative_to(project_root)),
                "sha256": sha256_file(pair_registry_path),
            },
        },
        "output": {
            "path": str(output_path.relative_to(project_root)),
            "sha256": sha256_file(output_path),
            "row_count": write_result.row_count,
            "column_count": len(schema.names),
            "schema_version": MORPH_FEATURES_SCHEMA_VERSION,
        },
        "expected_rows": expected_rows,
        "analyzer_name": ANALYZER_NAME,
        "analyzer_package_version": ANALYZER_PACKAGE_VERSION,
        "analyzer_model_version": ANALYZER_MODEL_VERSION,
        "analyzer_model_manifest_sha256": ANALYZER_MODEL_MANIFEST_SHA256,
        "analyzer_config_hash": MORPHOLOGY_CONFIG_SHA256,
        "num_workers": num_workers,
        "batch_rows": batch_rows,
        "warmup_sec": warmup_sec,
        "stage_duration_sec": stage_duration,
        "per_pair_latency_sec": per_pair_latency_sec,
        "rows_per_sec": round(write_result.row_count / stage_duration, 1) if stage_duration else None,
        "zero_morpheme_rows": stats["zero_morpheme_rows"],
        "zero_morpheme_rate": stats["zero_morpheme_rows"] / write_result.row_count if write_result.row_count else None,
        "distinct_raw_tags": len(raw_tags),
        "distinct_base_tags": len(base_tags),
        "irregular_tag_counts": dict(sorted(irregular.items())),
        "deriv_affix_family_counts": {
            tag: count for tag, count in sorted(raw_tags.items()) if base_tag(tag) in _DERIV_AFFIX_BASE_TAGS
        },
        "base_tag_counts": dict(sorted(base_tags.items())),
        "start_kst": start.isoformat(timespec="seconds"),
        "end_kst": end.isoformat(timespec="seconds"),
        "validation_status": "PASS",
    }


def validate_morph_features(path: Path, *, expected_rows: int) -> None:
    """row 수, id/pair_id 유일성, ratio invariant, zero-morpheme 규약을 promotion 직전에 검사한다."""
    connection = duckdb.connect()
    try:
        relation = f"read_parquet({_sql_literal(path)})"
        row_count, distinct_pair_id, distinct_measurement_id = _fetchone_required(
            connection.execute(
                f"SELECT count(*), count(DISTINCT pair_id), count(DISTINCT morph_measurement_id) FROM {relation}"
            )
        )
        if not (int(row_count) == int(distinct_pair_id) == int(distinct_measurement_id) == expected_rows):
            raise ValueError("MORPH_FEATURES row count 또는 pair_id/measurement_id 유일성 검증 실패")

        bad_rows = _fetchone_required(
            connection.execute(
                f"""
                SELECT count(*) FROM {relation}
                WHERE morpheme_count < 0 OR particle_count < 0 OR ending_count < 0 OR deriv_affix_count < 0
                   OR particle_count + ending_count + deriv_affix_count > morpheme_count
                   OR eojeol_count <= 0
                   OR NOT isfinite(morpheme_density)
                   OR abs(morpheme_density - morpheme_count::DOUBLE / eojeol_count) > 1e-12
                   OR (particle_ratio IS NOT NULL AND (particle_ratio < 0 OR particle_ratio > 1))
                   OR (ending_ratio IS NOT NULL AND (ending_ratio < 0 OR ending_ratio > 1))
                   OR (deriv_affix_ratio IS NOT NULL AND (deriv_affix_ratio < 0 OR deriv_affix_ratio > 1))
                   OR (function_morpheme_ratio IS NOT NULL
                       AND (function_morpheme_ratio < 0 OR function_morpheme_ratio > 1))
                """
            )
        )[0]
        if int(bad_rows) != 0:
            raise ValueError("MORPH_FEATURES count/ratio invariant 검증 실패")

        # zero-morpheme 규약: warning=true <-> morpheme_count=0 <-> morpheme_count 분모 ratio가 null.
        contract_violations = _fetchone_required(
            connection.execute(
                f"""
                SELECT count(*) FROM {relation}
                WHERE (morpheme_count = 0) <> analysis_warning_flag
                   OR (morpheme_count = 0 AND (particle_ratio IS NOT NULL OR ending_ratio IS NOT NULL
                       OR deriv_affix_ratio IS NOT NULL OR function_morpheme_ratio IS NOT NULL))
                   OR (morpheme_count > 0 AND (particle_ratio IS NULL OR ending_ratio IS NULL
                       OR deriv_affix_ratio IS NULL OR function_morpheme_ratio IS NULL))
                   OR (analysis_warning_flag AND analysis_warning_reason = 'NONE')
                   OR (NOT analysis_warning_flag AND analysis_warning_reason <> 'NONE')
                   OR length(morpheme_sequence) <> morpheme_count
                """
            )
        )[0]
        if int(contract_violations) != 0:
            raise ValueError("MORPH_FEATURES zero-morpheme/warning 규약 검증 실패")
    finally:
        connection.close()


def compare_feature_dicts(reference: dict[str, Any], candidate: dict[str, Any]) -> list[str]:
    """
    /**
     * @purpose scalar reference와 optimized candidate의 분석 결과를 field 단위로 exact 비교한다.
     * @spec_ref Directive §14 exact output equivalence (absolute gate)
     * @param reference scalar path 결과 dict
     * @param candidate optimized path 결과 dict
     * @return 불일치한 field 이름 목록 (빈 목록이면 완전 일치)
     * @raises 없음
     * @validation mismatch가 하나라도 있으면 해당 optimization을 거부한다.
     * @artifact benchmark report
     */
    """
    mismatches = []
    for key in sorted(set(reference) | set(candidate)):
        if reference.get(key) != candidate.get(key):
            mismatches.append(key)
    return mismatches


def iter_morph_records(
    pair_ids: Sequence[str],
    texts: Sequence[str],
    eojeol_counts: Sequence[int],
    *,
    kiwi: Kiwi,
) -> Iterable[dict[str, Any]]:
    """benchmark/pilot에서 optimized batch path의 record를 생성한다."""
    analyses = analyze_batch(texts, kiwi=kiwi)
    for pair_id, morphs, eojeol_count in zip(pair_ids, analyses, eojeol_counts, strict=True):
        yield build_record(pair_id, morphs, eojeol_count=eojeol_count)


__all__ = [
    "ANALYZER_MODEL_MANIFEST_SHA256",
    "ANALYZER_MODEL_VERSION",
    "ANALYZER_NAME",
    "ANALYZER_PACKAGE_VERSION",
    "MORPHOLOGY_CONFIG",
    "MORPHOLOGY_CONFIG_SHA256",
    "MORPHOLOGY_RULE_VERSION",
    "MORPH_FEATURES_RELATIVE_PATH",
    "MORPH_FEATURES_SCHEMA_VERSION",
    "MorphologyHardInvalidError",
    "MorphologyInputError",
    "WARNING_NONE",
    "WARNING_ZERO_MORPHEME",
    "analyze_batch",
    "base_tag",
    "build_record",
    "classify_tag",
    "cohort_reader",
    "compare_feature_dicts",
    "execute_morphology_run",
    "features_from_morphs",
    "get_kiwi",
    "iter_morph_records",
    "morph_features_schema",
    "morph_measurement_id",
    "morphology_features",
    "validate_morph_features",
]
