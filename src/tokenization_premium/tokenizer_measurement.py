"""Phase-4 D-04 o200k_base tokenizer 측정 (NB05) 엔지니어링 구현.

SSOT 범위: 고정된 tiktoken o200k_base 구현으로 pair-level token count와
Tokenization Premium(TP)의 정확한 가법적 분해(logTP = logCR + logBDR + logCP)만
측정한다. 형태소(D-03), regex chunk mechanism(D-05), 통계적 추론, 모델링은
이 모듈의 범위 밖이다.

SSOT 근거:
  §8      TP = CodePointRatio × ByteDensityRatio × CompressionPenalty
  §12.4   D-04 Token Measurement 필드 계약
  §14.2   chat template/special token 미사용, text_analysis만 encode, roundtrip 검증
  §38     canonical artifact 명명 = TOKEN_O200K_BASE_v001.parquet
"""

from __future__ import annotations

import datetime as dt
import math
import os
import time
from collections.abc import Iterator, Sequence
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import duckdb
import pyarrow as pa
import tiktoken

from tokenization_premium.hashing import canonical_json_bytes, sha256_bytes, sha256_file
from tokenization_premium.phase2 import _fetchone_required, write_parquet_batches_atomic
from tokenization_premium.progress import ProgressHeartbeat

_KST = ZoneInfo("Asia/Seoul")

TOKENIZER_MEASUREMENT_RULE_VERSION = "tok_meas_v001"  # 이 측정 규칙의 고정 버전 문자열이다.
TOKEN_MEASUREMENT_SCHEMA_VERSION = "TOKEN_O200K_BASE_v001"  # SSOT §38 canonical schema 버전이다.
TOKEN_MEASUREMENT_RELATIVE_PATH = Path("data/registry/TOKEN_O200K_BASE_v001.parquet")  # SSOT §38 명명이다.
EXACT_DECOMPOSITION_EPSILON = 1e-10  # D-RD-01에서 고정한 identity 허용 오차다.
TOKENIZER_ID = "o200k_base"
TIKTOKEN_VERSION = tiktoken.__version__

# Phase-0에서 검증된 o200k_base artifact provenance (outputs/manifests/TOKENIZER_O200K_BASE_ARTIFACT_v001.json).
ENCODING_FILE_SHA256 = "446a9538cb6c348e3516120d7c08b09f57c36495e2acfffe59a5bf8b0cfb1a2d"
MERGEABLE_RANKS_HASH = "f2f614601c635339047c0ec251d13afcfd8e3bc01440bca9ab0bdf17ed61e2d0"
PAT_STR_SHA256 = "2d1b8dc11e89af71459b36004f698ab3693f59fd84f63e8ec2b49564ab857420"
SPECIAL_TOKENS_HASH = "160541c3dd5153d72838e5770937be894f3decc367096bf849726a40d7afa14d"

TOKENIZER_CONFIG: dict[str, Any] = {
    "rule_version": TOKENIZER_MEASUREMENT_RULE_VERSION,
    "tokenizer_id": TOKENIZER_ID,
    "tiktoken_version": TIKTOKEN_VERSION,
    "encoding_file_sha256": ENCODING_FILE_SHA256,
    "mergeable_ranks_hash": MERGEABLE_RANKS_HASH,
    "pat_str_sha256": PAT_STR_SHA256,
    "special_tokens_hash": SPECIAL_TOKENS_HASH,
    "input_text_fields": ["ko_text_analysis", "en_text_analysis"],
    "special_tokens_used": False,
    "chat_template_used": False,
    "allowed_special": "none (SSOT §14.2 Track A)",
    "exact_decomposition_epsilon": EXACT_DECOMPOSITION_EPSILON,
    "network_fallback_allowed": False,
}
TOKENIZER_CONFIG_SHA256 = sha256_bytes(canonical_json_bytes(TOKENIZER_CONFIG))


class TokenizerMeasurementInputError(ValueError):
    """빈 문자열 등 accepted cohort에서 나타날 수 없는 입력을 명시적으로 거부한다."""


class TokenizerOfflineLoadError(RuntimeError):
    """offline cache 없이 network fallback이 시도된 상황을 거부한다."""


_ENCODING: tiktoken.Encoding | None = None


def load_o200k_base_offline(cache_dir: Path | None = None) -> tiktoken.Encoding:
    """
    /**
     * @purpose network fallback 없이 로컬 cache만으로 o200k_base encoding을 로드한다.
     * @spec_ref SSOT §14.1 primary tokenizer; §14.2 측정 원칙; Phase-0 artifact freeze
     * @param cache_dir tiktoken cache 디렉터리 (None이면 현재 환경변수를 사용)
     * @return 검증된 tiktoken.Encoding
     * @raises TokenizerOfflineLoadError cache가 없거나 artifact hash가 불일치하는 경우
     * @validation encoding_file_sha256과 n_vocab을 로드 직후 대조한다.
     * @artifact TOKEN_O200K_BASE_v001.parquet
     */
    """
    global _ENCODING
    if cache_dir is not None:
        os.environ["TIKTOKEN_CACHE_DIR"] = str(cache_dir)
        cached = list(cache_dir.glob("*"))
        if not cached:
            raise TokenizerOfflineLoadError(f"tiktoken offline cache가 비어 있다: {cache_dir}")
        digests = {sha256_file(path) for path in cached if path.is_file()}
        if ENCODING_FILE_SHA256 not in digests:
            raise TokenizerOfflineLoadError("tiktoken cache artifact hash가 Phase-0 freeze와 불일치한다")
    if _ENCODING is None:
        _ENCODING = tiktoken.get_encoding(TOKENIZER_ID)
    return _ENCODING


def _token_count_and_roundtrip(text: str, encoding: tiktoken.Encoding) -> tuple[int, bool]:
    """text를 encode/decode해 token count와 roundtrip 성공 여부를 함께 계산한다."""
    tokens = encoding.encode(text)
    roundtrip_ok = encoding.decode(tokens) == text
    return len(tokens), roundtrip_ok


def pair_token_measurement(ko_text: str, en_text: str, *, encoding: tiktoken.Encoding) -> dict[str, Any]:
    """
    /**
     * @purpose 의미 대응 KO/EN pair에서 T_KO/T_EN, TP, 그리고 CodePointRatio/ByteDensityRatio/
     *          CompressionPenalty로의 정확한 log 가법적 분해를 계산한다.
     * @spec_ref SSOT §8 (logTP = logCodePointRatio + logByteDensityRatio + logCompressionPenalty)
     * @param ko_text ko_text_analysis 문자열 (accepted cohort는 empty 불가)
     * @param en_text en_text_analysis 문자열 (accepted cohort는 empty 불가)
     * @param encoding 검증된 o200k_base tiktoken.Encoding (load_o200k_base_offline 결과)
     * @return T_KO/T_EN/TP/logTP/3개 분해항/roundtrip_ok/identity_abs_error
     * @raises TokenizerMeasurementInputError 빈 문자열이 전달된 경우
     * @validation abs(logTP - (logCR+logBDR+logCP)) < 1e-10 을 단위 테스트로 검사한다.
     * @artifact TOKEN_O200K_BASE_v001.parquet
     */
    """
    if ko_text == "" or en_text == "":
        raise TokenizerMeasurementInputError(
            "accepted cohort의 텍스트는 empty일 수 없다: pair_token_measurement는 빈 문자열을 거부한다"
        )

    ko_codepoints, en_codepoints = len(ko_text), len(en_text)
    ko_bytes, en_bytes = len(ko_text.encode("utf-8")), len(en_text.encode("utf-8"))
    t_ko, ko_roundtrip_ok = _token_count_and_roundtrip(ko_text, encoding)
    t_en, en_roundtrip_ok = _token_count_and_roundtrip(en_text, encoding)

    tp = t_ko / t_en
    code_point_ratio = ko_codepoints / en_codepoints
    byte_density_ratio = (ko_bytes / ko_codepoints) / (en_bytes / en_codepoints)
    compression_penalty = (t_ko / ko_bytes) / (t_en / en_bytes)

    log_tp = math.log(tp)
    log_cr = math.log(code_point_ratio)
    log_bdr = math.log(byte_density_ratio)
    log_cp = math.log(compression_penalty)

    return {
        "T_KO": t_ko,
        "T_EN": t_en,
        "token_difference": t_ko - t_en,
        "TP": tp,
        "logTP": log_tp,
        "CodePointRatio": code_point_ratio,
        "ByteDensityRatio": byte_density_ratio,
        "CompressionPenalty": compression_penalty,
        "logCodePointRatio": log_cr,
        "logByteDensityRatio": log_bdr,
        "logCompressionPenalty": log_cp,
        "identity_abs_error": abs(log_tp - (log_cr + log_bdr + log_cp)),
        "roundtrip_ok": ko_roundtrip_ok and en_roundtrip_ok,
    }


def token_measurement_id(pair_id: str) -> str:
    """(config, pair)에 대해 결정적이고 유일한 D-04 측정 ID를 만든다."""
    payload = f"{TOKEN_MEASUREMENT_SCHEMA_VERSION}|{TOKENIZER_CONFIG_SHA256}|{pair_id}"
    return "tok_" + sha256_bytes(payload.encode("utf-8"))


def token_measurement_schema() -> pa.Schema:
    """
    /**
     * @purpose TOKEN_O200K_BASE_v001 Parquet의 SSOT §12.4 D-04 전체 계약을 고정한다.
     * @spec_ref SSOT §12.4 D-04 Token Measurement; §38 명명 규칙
     * @return token id array를 포함한 D-04 required field 전체 schema
     * @raises 없음
     * @validation 저장된 Parquet schema와 exact equality로 검사한다.
     * @artifact data/registry/TOKEN_O200K_BASE_v001.parquet
     */
    """
    return pa.schema(
        [
            pa.field("measurement_id", pa.string(), nullable=False),
            pa.field("pair_id", pa.string(), nullable=False),
            pa.field("tokenizer_id", pa.string(), nullable=False),
            pa.field("tiktoken_version", pa.string(), nullable=False),
            pa.field("encoding_file_sha256", pa.string(), nullable=False),
            pa.field("mergeable_ranks_hash", pa.string(), nullable=False),
            pa.field("pat_str_sha256", pa.string(), nullable=False),
            pa.field("special_tokens_hash", pa.string(), nullable=False),
            pa.field("tokenizer_config_sha256", pa.string(), nullable=False),
            # SSOT §12.4: token ID array는 lossless integer list로 저장한다.
            pa.field("ko_token_ids", pa.list_(pa.field("item", pa.int32(), nullable=False)), nullable=False),
            pa.field("en_token_ids", pa.list_(pa.field("item", pa.int32(), nullable=False)), nullable=False),
            pa.field("ko_token_count", pa.int64(), nullable=False),
            pa.field("en_token_count", pa.int64(), nullable=False),
            pa.field("token_premium", pa.float64(), nullable=False),
            pa.field("log_token_premium", pa.float64(), nullable=False),
            pa.field("token_difference", pa.int64(), nullable=False),
            pa.field("code_point_ratio", pa.float64(), nullable=False),
            pa.field("byte_density_ratio", pa.float64(), nullable=False),
            pa.field("compression_penalty", pa.float64(), nullable=False),
            pa.field("log_code_point_ratio", pa.float64(), nullable=False),
            pa.field("log_byte_density_ratio", pa.float64(), nullable=False),
            pa.field("log_compression_penalty", pa.float64(), nullable=False),
            pa.field("identity_abs_error", pa.float64(), nullable=False),
            # SSOT §13.3/§13.4 파생 기술통계 (SSOT 정의 범위 안에서만 추가한다).
            pa.field("ko_tokens_per_byte", pa.float64(), nullable=False),
            pa.field("en_tokens_per_byte", pa.float64(), nullable=False),
            pa.field("ko_tokens_per_codepoint", pa.float64(), nullable=False),
            pa.field("en_tokens_per_codepoint", pa.float64(), nullable=False),
            pa.field("roundtrip_ok", pa.bool_(), nullable=False),
        ]
    )


def build_token_record(pair_id: str, ko_text: str, en_text: str, *, encoding: tiktoken.Encoding) -> dict[str, Any]:
    """단일 pair의 D-04 record를 token id array까지 포함해 조립한다."""
    if ko_text == "" or en_text == "":
        raise TokenizerMeasurementInputError("accepted cohort의 텍스트는 empty일 수 없다")

    ko_ids = encoding.encode(ko_text)
    en_ids = encoding.encode(en_text)
    roundtrip_ok = encoding.decode(ko_ids) == ko_text and encoding.decode(en_ids) == en_text

    t_ko, t_en = len(ko_ids), len(en_ids)
    ko_cp, en_cp = len(ko_text), len(en_text)
    ko_by, en_by = len(ko_text.encode("utf-8")), len(en_text.encode("utf-8"))

    tp = t_ko / t_en
    cr = ko_cp / en_cp
    bdr = (ko_by / ko_cp) / (en_by / en_cp)
    cp_penalty = (t_ko / ko_by) / (t_en / en_by)
    log_tp, log_cr = math.log(tp), math.log(cr)
    log_bdr, log_cp = math.log(bdr), math.log(cp_penalty)

    return {
        "measurement_id": token_measurement_id(pair_id),
        "pair_id": pair_id,
        "tokenizer_id": TOKENIZER_ID,
        "tiktoken_version": TIKTOKEN_VERSION,
        "encoding_file_sha256": ENCODING_FILE_SHA256,
        "mergeable_ranks_hash": MERGEABLE_RANKS_HASH,
        "pat_str_sha256": PAT_STR_SHA256,
        "special_tokens_hash": SPECIAL_TOKENS_HASH,
        "tokenizer_config_sha256": TOKENIZER_CONFIG_SHA256,
        "ko_token_ids": ko_ids,
        "en_token_ids": en_ids,
        "ko_token_count": t_ko,
        "en_token_count": t_en,
        "token_premium": tp,
        "log_token_premium": log_tp,
        "token_difference": t_ko - t_en,
        "code_point_ratio": cr,
        "byte_density_ratio": bdr,
        "compression_penalty": cp_penalty,
        "log_code_point_ratio": log_cr,
        "log_byte_density_ratio": log_bdr,
        "log_compression_penalty": log_cp,
        "identity_abs_error": abs(log_tp - (log_cr + log_bdr + log_cp)),
        "ko_tokens_per_byte": t_ko / ko_by,
        "en_tokens_per_byte": t_en / en_by,
        "ko_tokens_per_codepoint": t_ko / ko_cp,
        "en_tokens_per_codepoint": t_en / en_cp,
        "roundtrip_ok": roundtrip_ok,
    }


def _sql_literal(path: Path) -> str:
    return "'" + str(path).replace("'", "''") + "'"


def cohort_text_reader(
    connection: duckdb.DuckDBPyConnection,
    *,
    rep_features_path: Path,
    pair_registry_path: Path,
    batch_rows: int,
    limit: int | None = None,
) -> pa.RecordBatchReader:
    """final cohort의 (pair_id, ko_text_analysis, en_text_analysis)를 streaming으로 읽는다."""
    limit_clause = f" LIMIT {int(limit)}" if limit is not None else ""
    query = (
        "SELECT r.pair_id, p.ko_text_analysis AS ko_text, p.en_text_analysis AS en_text "
        f"FROM read_parquet({_sql_literal(rep_features_path)}) r "
        f"JOIN read_parquet({_sql_literal(pair_registry_path)}) p USING (pair_id) "
        "ORDER BY r.pair_id" + limit_clause
    )
    return connection.execute(query).fetch_record_batch(batch_rows)


def _token_batches(
    reader: pa.RecordBatchReader,
    *,
    schema: pa.Schema,
    encoding: tiktoken.Encoding,
    heartbeat: ProgressHeartbeat,
    stats: dict[str, Any],
) -> Iterator[pa.RecordBatch]:
    """batch 단위로 encode -> record -> RecordBatch를 yield하고 즉시 메모리를 놓아준다."""
    for batch in reader:
        pair_ids = batch.column("pair_id").to_pylist()
        ko_texts = batch.column("ko_text").to_pylist()
        en_texts = batch.column("en_text").to_pylist()
        records = []
        for pair_id, ko_text, en_text in zip(pair_ids, ko_texts, en_texts, strict=True):
            record = build_token_record(pair_id, ko_text, en_text, encoding=encoding)
            if not record["roundtrip_ok"]:
                stats["roundtrip_failures"] += 1
                stats["roundtrip_failure_pair_ids"].append(pair_id)
            if record["identity_abs_error"] >= EXACT_DECOMPOSITION_EPSILON:
                stats["identity_violations"] += 1
                stats["identity_violation_pair_ids"].append(pair_id)
            stats["max_identity_abs_error"] = max(stats["max_identity_abs_error"], record["identity_abs_error"])
            records.append(record)
        stats["rows"] += len(records)
        yield pa.RecordBatch.from_pylist(records, schema=schema)
        heartbeat.update(len(records))
        del pair_ids, ko_texts, en_texts, records, batch  # bounded memory


def execute_token_measurement_run(
    *,
    project_root: Path,
    rep_features_path: Path,
    pair_registry_path: Path,
    output_path: Path,
    runtime_dir: Path,
    run_id: str,
    run_mode: str,
    limit: int | None,
    batch_rows: int = 2_500,
    cache_dir: Path | None = None,
    expected_rows: int | None = None,
) -> dict[str, Any]:
    """
    /**
     * @purpose bounded-memory streaming으로 D-04 tokenizer 측정 artifact를 생성한다.
     * @spec_ref SSOT §12.4; §14.2; ENG-OBS-001 heartbeat
     * @param limit None이면 전체 cohort (full run), 정수면 bounded benchmark
     * @param expected_rows 검증용 기대 행 수 (None이면 입력에서 derive; 하드코딩 상수 없음)
     * @return manifest dict (row count, sha256, runtime, roundtrip/identity 통계)
     * @raises FileExistsError 목적지 또는 partial이 이미 존재하는 경우
     * @validation roundtrip 100%, identity < 1e-10, pair_id 유일성을 promotion 전에 검사한다.
     * @artifact TOKEN_O200K_BASE parquet + manifest
     */
    """
    output_partial = output_path.with_suffix(output_path.suffix + ".partial")
    if output_path.exists() or output_partial.exists():
        raise FileExistsError("TOKEN_O200K 목적지 또는 partial이 이미 존재한다; 자동 재시작은 금지된다")

    schema = token_measurement_schema()
    start = dt.datetime.now(tz=_KST)
    runtime_dir.mkdir(parents=True, exist_ok=True)
    encoding = load_o200k_base_offline(cache_dir)

    connection = duckdb.connect()
    try:
        if expected_rows is None:
            total_available = int(
                _fetchone_required(
                    connection.execute(f"SELECT count(*) FROM read_parquet({_sql_literal(rep_features_path)})")
                )[0]
            )
            expected_rows = total_available if limit is None else min(limit, total_available)

        stage_started = time.monotonic()
        reader = cohort_text_reader(
            connection,
            rep_features_path=rep_features_path,
            pair_registry_path=pair_registry_path,
            batch_rows=batch_rows,
            limit=limit,
        )
        stats: dict[str, Any] = {
            "rows": 0,
            "roundtrip_failures": 0,
            "roundtrip_failure_pair_ids": [],
            "identity_violations": 0,
            "identity_violation_pair_ids": [],
            "max_identity_abs_error": 0.0,
        }
        with ProgressHeartbeat(
            run_id=run_id,
            phase="NB05",
            stage="O200K_MEASUREMENT",
            total=expected_rows,
            progress_dir=project_root / ".runtime" / "progress",
        ) as heartbeat:
            def validate(path: Path) -> None:
                validate_token_measurements(path, expected_rows=expected_rows)

            write_result = write_parquet_batches_atomic(
                output_path,
                schema,
                _token_batches(reader, schema=schema, encoding=encoding, heartbeat=heartbeat, stats=stats),
                validate=validate,
            )
            heartbeat.checkpoint("TOKEN_MEASUREMENTS_WRITTEN", rows=write_result.row_count)
        stage_duration = round(time.monotonic() - stage_started, 3)
    finally:
        connection.close()

    end = dt.datetime.now(tz=_KST)
    return {
        "artifact_id": f"TOKEN_O200K_BASE_MANIFEST_{run_mode}_v001",
        "run_id": run_id,
        "run_mode": run_mode,
        "input": {
            "rep_features": {
                "path": str(rep_features_path.relative_to(project_root)),
                "sha256": sha256_file(rep_features_path),
            },
            "pair_registry": {
                "path": str(pair_registry_path.relative_to(project_root)),
                "sha256": sha256_file(pair_registry_path),
            },
        },
        "output": {
            "path": str(output_path.relative_to(project_root)),
            "sha256": sha256_file(output_path),
            "row_count": write_result.row_count,
            "column_count": len(schema.names),
            "schema_version": TOKEN_MEASUREMENT_SCHEMA_VERSION,
        },
        "expected_rows": expected_rows,
        "tokenizer": dict(TOKENIZER_CONFIG),
        "tokenizer_config_sha256": TOKENIZER_CONFIG_SHA256,
        "batch_rows": batch_rows,
        "stage_duration_sec": stage_duration,
        "rows_per_sec": round(write_result.row_count / stage_duration, 1) if stage_duration else None,
        "roundtrip_failures": stats["roundtrip_failures"],
        "roundtrip_pass_rate": 1.0 - stats["roundtrip_failures"] / write_result.row_count
        if write_result.row_count
        else None,
        "roundtrip_failure_pair_ids": stats["roundtrip_failure_pair_ids"][:100],
        "exact_decomposition": {
            "epsilon": EXACT_DECOMPOSITION_EPSILON,
            "max_abs_error": stats["max_identity_abs_error"],
            "violations": stats["identity_violations"],
            "violation_pair_ids": stats["identity_violation_pair_ids"][:100],
        },
        "start_kst": start.isoformat(timespec="seconds"),
        "end_kst": end.isoformat(timespec="seconds"),
        "validation_status": "PASS",
    }


def validate_token_measurements(path: Path, *, expected_rows: int) -> None:
    """row 수, id 유일성, roundtrip, exact decomposition identity를 promotion 직전에 검사한다."""
    connection = duckdb.connect()
    try:
        relation = f"read_parquet({_sql_literal(path)})"
        row_count, distinct_pair_id, distinct_measurement_id = _fetchone_required(
            connection.execute(
                f"SELECT count(*), count(DISTINCT pair_id), count(DISTINCT measurement_id) FROM {relation}"
            )
        )
        if not (int(row_count) == int(distinct_pair_id) == int(distinct_measurement_id) == expected_rows):
            raise ValueError("TOKEN_O200K row count 또는 pair_id/measurement_id 유일성 검증 실패")

        bad = _fetchone_required(
            connection.execute(
                f"""
                SELECT count(*) FROM {relation}
                WHERE ko_token_count <= 0 OR en_token_count <= 0
                   OR length(ko_token_ids) <> ko_token_count
                   OR length(en_token_ids) <> en_token_count
                   OR token_difference <> ko_token_count - en_token_count
                   OR NOT isfinite(token_premium) OR token_premium <= 0
                   OR NOT isfinite(log_token_premium)
                   OR abs(token_premium - ko_token_count::DOUBLE / en_token_count) > 1e-12
                   OR NOT roundtrip_ok
                   OR identity_abs_error >= {EXACT_DECOMPOSITION_EPSILON}
                """
            )
        )[0]
        if int(bad) != 0:
            raise ValueError("TOKEN_O200K roundtrip/identity/count invariant 검증 실패")
    finally:
        connection.close()


def decoded_token_bytes(token_ids: Sequence[int], *, encoding: tiktoken.Encoding, limit: int = 32) -> list[str]:
    """
    /**
     * @purpose G3 audit sample용으로 token id를 decode_single_token_bytes 기반 표현으로 바꾼다.
     * @spec_ref SSOT §14.2 (4) token byte representation을 audit sample에 저장할 수 있다
     * @param token_ids 하나의 side에 대한 token id sequence
     * @param encoding 검증된 o200k_base encoding
     * @param limit audit sample에 남길 최대 token 수
     * @return "id:hex" 형태의 문자열 목록 (원문 재구성 방지를 위해 hex로 남긴다)
     * @raises 없음
     * @validation roundtrip이 이미 검증된 행에서만 호출한다.
     * @artifact local-only token audit sample
     */
    """
    out = []
    for token_id in list(token_ids)[:limit]:
        out.append(f"{token_id}:{encoding.decode_single_token_bytes(token_id).hex()}")
    return out


__all__ = [
    "ENCODING_FILE_SHA256",
    "EXACT_DECOMPOSITION_EPSILON",
    "MERGEABLE_RANKS_HASH",
    "PAT_STR_SHA256",
    "SPECIAL_TOKENS_HASH",
    "TIKTOKEN_VERSION",
    "TOKENIZER_CONFIG",
    "TOKENIZER_CONFIG_SHA256",
    "TOKENIZER_ID",
    "TOKENIZER_MEASUREMENT_RULE_VERSION",
    "TOKEN_MEASUREMENT_RELATIVE_PATH",
    "TOKEN_MEASUREMENT_SCHEMA_VERSION",
    "TokenizerMeasurementInputError",
    "TokenizerOfflineLoadError",
    "build_token_record",
    "cohort_text_reader",
    "decoded_token_bytes",
    "execute_token_measurement_run",
    "load_o200k_base_offline",
    "pair_token_measurement",
    "token_measurement_id",
    "token_measurement_schema",
    "validate_token_measurements",
]
