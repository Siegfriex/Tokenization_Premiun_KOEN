"""Phase-4 D-05 o200k_base regex chunk 측정 (NB06) 엔지니어링 구현.

SSOT 근거:
  §5    x -> b=UTF8(x) -> P_v(b) -> T_v(P_v(b)) -> N. P_v가 여기서 측정하는 1차 regex chunking이다.
  §5.1  형태소 분석 != regex chunking != 최종 subword tokenization. 세 경계는 같을 필요가 없다.
  §6.5  RQ5 mechanism feature. MN-02: post-treatment 성격이므로 mechanism audit으로 분리한다.
  §12.5 D-05 Regex Chunk Measurement 필드 계약 (아래 schema의 authority).
  §14   tokenizer 고정 규약. D-04와 동일한 o200k_base/tiktoken/hash를 쓴다.
  §25   raw text Track A, chat template/special token 없음.
  §38   canonical artifact 명명 = CHUNK_O200K_BASE_v001.parquet

범위 경계: 이 모듈은 최종 token 수의 authority가 아니다. D-04가 token ID/count/TP의
authority이며, 여기서는 chunk 경계와 chunk별 token 배분만 측정한다. NB06은 두 번째
tokenizer outcome factory가 아니다.
"""

from __future__ import annotations

import datetime as dt
import statistics
import time
from collections.abc import Iterator, Sequence
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import duckdb
import pyarrow as pa
import regex as _regex
import tiktoken

from tokenization_premium.hashing import canonical_json_bytes, sha256_bytes, sha256_file
from tokenization_premium.phase2 import _fetchone_required, write_parquet_batches_atomic
from tokenization_premium.telemetry import RuntimeTelemetry
from tokenization_premium.tokenizer_measurement import (
    ENCODING_FILE_SHA256,
    MERGEABLE_RANKS_HASH,
    PAT_STR_SHA256,
    SPECIAL_TOKENS_HASH,
    TIKTOKEN_VERSION,
    TOKENIZER_CONFIG_SHA256,
    TOKENIZER_ID,
    load_o200k_base_offline,
)

_KST = ZoneInfo("Asia/Seoul")

CHUNK_RULE_VERSION = "chunk_meas_v001"
CHUNK_SCHEMA_VERSION = "CHUNK_O200K_BASE_v001"
CHUNK_RELATIVE_PATH = Path("data/registry/CHUNK_O200K_BASE_v001.parquet")  # SSOT §38 명명이다.

# §12.5 "letter/number/punctuation/whitespace 등". o200k pat_str의 분기 구조를 그대로 반영한
# 우선순위 분류이며, 새 범주를 발명하지 않는다.
CHUNK_TYPES = ("letter", "number", "punctuation", "whitespace")

_HAS_LETTER = _regex.compile(r"\p{L}", flags=_regex.VERSION1)
_HAS_NUMBER = _regex.compile(r"\p{N}", flags=_regex.VERSION1)
_ALL_SPACE = _regex.compile(r"^\s+$", flags=_regex.VERSION1)

CHUNKING_CONFIG: dict[str, Any] = {
    "rule_version": CHUNK_RULE_VERSION,
    "spec_ref": "SSOT §5 P_v; §12.5 D-05; §14; §25",
    "tokenizer_id": TOKENIZER_ID,
    "tiktoken_version": TIKTOKEN_VERSION,
    "pat_str_sha256": PAT_STR_SHA256,
    "encoding_file_sha256": ENCODING_FILE_SHA256,
    "mergeable_ranks_hash": MERGEABLE_RANKS_HASH,
    "special_tokens_hash": SPECIAL_TOKENS_HASH,
    "tokenizer_config_sha256": TOKENIZER_CONFIG_SHA256,
    "chunk_source": "tiktoken Encoding._pat_str, regex.finditer over *_text_analysis",
    "chunk_types_priority": list(CHUNK_TYPES),
    "chunk_type_rule": (
        "letter: chunk에 \\p{L} 포함; number: \\p{L} 없고 \\p{N} 포함; "
        "whitespace: 전체가 \\s; 그 외 punctuation"
    ),
    "special_tokens_used": False,
    "chat_template_used": False,
    "authority_note": "D-04가 최종 token ID/count/TP의 authority다. D-05는 mechanism 측정이다.",
}
CHUNKING_CONFIG_SHA256 = sha256_bytes(canonical_json_bytes(CHUNKING_CONFIG))


class ChunkConfigMismatch(RuntimeError):
    """D-04에서 동결한 tokenizer 신원과 다르면 즉시 실패한다 (§4 config freeze)."""


class ChunkInvariantViolation(RuntimeError):
    """concat 재구성 또는 token 등가성 불변식이 깨졌다."""


_PAT: _regex.Pattern[str] | None = None


def chunk_pattern(encoding: tiktoken.Encoding) -> _regex.Pattern[str]:
    """
    /**
     * @purpose D-04와 동일한 pat_str을 encoder에서 직접 받아 compile한다.
     * @spec_ref SSOT §5 P_v; §14.1 pat_str 고정
     * @param encoding load_o200k_base_offline() 결과
     * @return compile된 regex pattern
     * @raises ChunkConfigMismatch pat_str hash가 D-04 frozen 값과 다른 경우
     * @validation pat_str을 문헌에서 옮겨 적지 않고 encoder에서 읽어 hash로 대조한다.
     * @artifact CHUNK_O200K_BASE_v001.parquet
     */
    """
    global _PAT
    pat_str = encoding._pat_str
    actual = sha256_bytes(pat_str.encode("utf-8"))
    if actual != PAT_STR_SHA256:
        raise ChunkConfigMismatch(
            f"pat_str hash가 D-04 frozen 값과 다르다\n  expected {PAT_STR_SHA256}\n  actual   {actual}")
    if _PAT is None:
        _PAT = _regex.compile(pat_str)
    return _PAT


def assert_tokenizer_identity(encoding: tiktoken.Encoding) -> dict[str, str]:
    """§4: D-04 frozen tokenizer 신원과 일치하는지 확인하고 그 값을 돌려준다."""
    chunk_pattern(encoding)                       # pat_str hash 검증
    return {
        "tokenizer_id": TOKENIZER_ID,
        "tiktoken_version": TIKTOKEN_VERSION,
        "pat_str_sha256": PAT_STR_SHA256,
        "encoding_file_sha256": ENCODING_FILE_SHA256,
        "mergeable_ranks_hash": MERGEABLE_RANKS_HASH,
        "special_tokens_hash": SPECIAL_TOKENS_HASH,
        "tokenizer_config_sha256": TOKENIZER_CONFIG_SHA256,
        "chunking_config_sha256": CHUNKING_CONFIG_SHA256,
    }


def regex_chunks(text: str, *, encoding: tiktoken.Encoding) -> list[str]:
    """
    /**
     * @purpose 문자열을 o200k_base의 1차 regex chunk로 분할한다 (SSOT §5의 P_v).
     * @spec_ref SSOT §5; §12.5
     * @param text ko_text_analysis 또는 en_text_analysis
     * @param encoding 검증된 o200k_base encoding
     * @return chunk 문자열 목록. 입력 순서를 보존하며 concat하면 원문이 된다.
     * @raises ChunkInvariantViolation concat(chunks) != text 인 경우
     * @validation lost/duplicated span이 0임을 offset으로 확인한다.
     * @artifact CHUNK_O200K_BASE_v001.parquet
     */
    """
    pattern = chunk_pattern(encoding)
    chunks: list[str] = []
    cursor = 0
    for match in pattern.finditer(text):
        start, end = match.span()
        if start != cursor:                       # 매치되지 않은 span은 손실이다
            raise ChunkInvariantViolation(
                f"lost span at [{cursor},{start}) — regex chunking이 입력을 모두 덮지 않았다")
        if end <= start:                          # 빈 chunk는 계약상 만들지 않는다
            raise ChunkInvariantViolation(f"empty chunk at offset {start}")
        chunks.append(match.group())
        cursor = end
    if cursor != len(text):
        raise ChunkInvariantViolation(
            f"trailing lost span at [{cursor},{len(text)}) — 입력 끝이 덮이지 않았다")
    if "".join(chunks) != text:
        raise ChunkInvariantViolation("concat(regex_chunks(text)) != text")
    return chunks


def classify_chunk(chunk: str) -> str:
    """§12.5 chunk_type_share_* 의 범주를 우선순위대로 결정한다."""
    if _HAS_LETTER.search(chunk):
        return "letter"
    if _HAS_NUMBER.search(chunk):
        return "number"
    if _ALL_SPACE.match(chunk):
        return "whitespace"
    return "punctuation"


def side_chunk_features(text: str, *, encoding: tiktoken.Encoding) -> dict[str, Any]:
    """
    /**
     * @purpose 한 언어 side에서 §12.5 D-05 chunk 측정값을 계산한다.
     * @spec_ref SSOT §12.5 (chunk_count / mean·p50·p90 chunk bytes / tokens_per_chunk /
     *           chunk_type_share)
     * @param text 해당 side의 분석 텍스트
     * @param encoding 검증된 o200k_base encoding
     * @return chunk 통계 dict와 flatten된 token id 목록
     * @raises ChunkInvariantViolation chunk 재구성 불변식이 깨진 경우
     * @validation flatten된 token id가 D-04 저장값과 exact match인지 호출자가 대조한다.
     * @artifact CHUNK_O200K_BASE_v001.parquet
     */
    """
    chunks = regex_chunks(text, encoding=encoding)
    byte_lengths = [len(c.encode("utf-8")) for c in chunks]
    per_chunk_tokens: list[int] = []
    flat_tokens: list[int] = []
    type_counts = dict.fromkeys(CHUNK_TYPES, 0)
    for chunk in chunks:
        ids = encoding.encode(chunk)
        per_chunk_tokens.append(len(ids))
        flat_tokens.extend(ids)
        type_counts[classify_chunk(chunk)] += 1

    n = len(chunks)
    total_tokens = sum(per_chunk_tokens)
    total_bytes = sum(byte_lengths)
    return {
        "chunk_count": n,
        "mean_chunk_bytes": total_bytes / n,
        "p50_chunk_bytes": float(statistics.median(byte_lengths)),
        "p90_chunk_bytes": float(_percentile(byte_lengths, 0.90)),
        "max_chunk_bytes": max(byte_lengths),
        "tokens_per_chunk": total_tokens / n,
        "max_tokens_per_chunk": max(per_chunk_tokens),
        "chunk_token_total": total_tokens,
        "chunk_byte_total": total_bytes,
        "chunk_type_share_letter": type_counts["letter"] / n,
        "chunk_type_share_number": type_counts["number"] / n,
        "chunk_type_share_punctuation": type_counts["punctuation"] / n,
        "chunk_type_share_whitespace": type_counts["whitespace"] / n,
        "_flat_tokens": flat_tokens,
    }


def _percentile(values: Sequence[int], q: float) -> float:
    """nearest-rank percentile. 작은 표본에서 보간으로 값을 만들지 않는다."""
    ordered = sorted(values)
    rank = max(1, min(len(ordered), int(-(-len(ordered) * q // 1))))
    return float(ordered[rank - 1])


def chunk_measurement_id(pair_id: str) -> str:
    """(config, pair)에 대해 결정적이고 유일한 D-05 측정 ID를 만든다."""
    payload = f"{CHUNK_SCHEMA_VERSION}|{CHUNKING_CONFIG_SHA256}|{pair_id}"
    return "chunk_" + sha256_bytes(payload.encode("utf-8"))


def chunk_schema() -> pa.Schema:
    """
    /**
     * @purpose CHUNK_O200K_BASE_v001 Parquet의 SSOT §12.5 D-05 계약을 고정한다.
     * @spec_ref SSOT §12.5; §38
     * @return D-05 필드와 provenance/warning을 포함한 PyArrow schema
     * @raises 없음
     * @validation 저장된 Parquet schema와 exact equality로 검사한다.
     * @artifact data/registry/CHUNK_O200K_BASE_v001.parquet
     */
    """
    per_side = [
        ("chunk_count", pa.int64()),
        ("mean_chunk_bytes", pa.float64()),
        ("p50_chunk_bytes", pa.float64()),
        ("p90_chunk_bytes", pa.float64()),
        ("max_chunk_bytes", pa.int64()),
        ("tokens_per_chunk", pa.float64()),
        ("max_tokens_per_chunk", pa.int64()),
        ("chunk_token_total", pa.int64()),
        ("chunk_byte_total", pa.int64()),
        ("chunk_type_share_letter", pa.float64()),
        ("chunk_type_share_number", pa.float64()),
        ("chunk_type_share_punctuation", pa.float64()),
        ("chunk_type_share_whitespace", pa.float64()),
    ]
    fields = [
        pa.field("chunk_measurement_id", pa.string(), nullable=False),
        pa.field("pair_id", pa.string(), nullable=False),
        pa.field("tokenizer_measurement_id", pa.string(), nullable=False),  # D-04 FK
    ]
    for prefix in ("ko_", "en_"):
        fields.extend(pa.field(f"{prefix}{name}", dtype, nullable=False) for name, dtype in per_side)
    fields.extend([
        pa.field("pair_chunk_ratio", pa.float64(), nullable=False),
        pa.field("tokenizer_id", pa.string(), nullable=False),
        pa.field("tiktoken_version", pa.string(), nullable=False),
        pa.field("pat_str_sha256", pa.string(), nullable=False),
        pa.field("encoding_file_sha256", pa.string(), nullable=False),
        pa.field("chunking_config_sha256", pa.string(), nullable=False),
        pa.field("chunk_reconstruction_ok", pa.bool_(), nullable=False),
        pa.field("token_equivalence_ok", pa.bool_(), nullable=False),
        pa.field("analysis_warning_flag", pa.bool_(), nullable=False),
        pa.field("analysis_warning_reason", pa.string(), nullable=False),
    ])
    return pa.schema(fields)


def build_chunk_record(
    pair_id: str,
    tokenizer_measurement_id: str,
    ko_text: str,
    en_text: str,
    ko_token_ids: Sequence[int],
    en_token_ids: Sequence[int],
    *,
    encoding: tiktoken.Encoding,
) -> dict[str, Any]:
    """
    /**
     * @purpose 한 pair의 D-05 record를 만들고 D-04 token id와의 등가성을 검증한다.
     * @spec_ref SSOT §5 (T_v(P_v(b))); §12.5
     * @param ko_token_ids/en_token_ids D-04에 저장된 token id (authority)
     * @param encoding 검증된 o200k_base encoding
     * @return chunk_schema() 순서의 record dict
     * @raises ChunkInvariantViolation chunk 재구성이 깨진 경우
     * @validation chunk별 encode를 flatten한 결과가 D-04 저장값과 exact match여야 한다.
     * @artifact CHUNK_O200K_BASE_v001.parquet
     */
    """
    ko = side_chunk_features(ko_text, encoding=encoding)
    en = side_chunk_features(en_text, encoding=encoding)

    ko_equiv = ko.pop("_flat_tokens") == list(ko_token_ids)
    en_equiv = en.pop("_flat_tokens") == list(en_token_ids)
    equivalence_ok = ko_equiv and en_equiv

    reasons = []
    if not ko_equiv:
        reasons.append("KO_TOKEN_FLATTEN_MISMATCH")
    if not en_equiv:
        reasons.append("EN_TOKEN_FLATTEN_MISMATCH")

    record: dict[str, Any] = {
        "chunk_measurement_id": chunk_measurement_id(pair_id),
        "pair_id": pair_id,
        "tokenizer_measurement_id": tokenizer_measurement_id,
    }
    record.update({f"ko_{k}": v for k, v in ko.items()})
    record.update({f"en_{k}": v for k, v in en.items()})
    record.update({
        "pair_chunk_ratio": ko["chunk_count"] / en["chunk_count"],
        "tokenizer_id": TOKENIZER_ID,
        "tiktoken_version": TIKTOKEN_VERSION,
        "pat_str_sha256": PAT_STR_SHA256,
        "encoding_file_sha256": ENCODING_FILE_SHA256,
        "chunking_config_sha256": CHUNKING_CONFIG_SHA256,
        "chunk_reconstruction_ok": True,   # regex_chunks가 위반 시 예외를 던지므로 여기 도달하면 True
        "token_equivalence_ok": equivalence_ok,
        "analysis_warning_flag": not equivalence_ok,
        "analysis_warning_reason": "|".join(reasons) if reasons else "NONE",
    })
    return record


def _sql_literal(path: Path) -> str:
    return "'" + str(path).replace("'", "''") + "'"


def cohort_reader(
    connection: duckdb.DuckDBPyConnection,
    *,
    token_path: Path,
    pair_registry_path: Path,
    batch_rows: int,
    limit: int | None = None,
    pair_ids: Sequence[str] | None = None,
) -> pa.RecordBatchReader:
    """D-04와 원문을 pair_id로 결합해 streaming으로 읽는다 (bounded memory)."""
    where = ""
    if pair_ids is not None:
        connection.execute("CREATE OR REPLACE TEMP TABLE _pilot_ids(pair_id VARCHAR)")
        connection.executemany("INSERT INTO _pilot_ids VALUES (?)", [(p,) for p in pair_ids])
        where = " JOIN _pilot_ids USING (pair_id)"
    limit_clause = f" LIMIT {int(limit)}" if limit is not None else ""
    query = (
        "SELECT t.pair_id, t.measurement_id AS tokenizer_measurement_id,"
        "       p.ko_text_analysis AS ko_text, p.en_text_analysis AS en_text,"
        "       t.ko_token_ids, t.en_token_ids"
        f" FROM read_parquet({_sql_literal(token_path)}) t"
        f" JOIN read_parquet({_sql_literal(pair_registry_path)}) p USING (pair_id)"
        f"{where}"
        " ORDER BY t.pair_id" + limit_clause
    )
    return connection.execute(query).fetch_record_batch(batch_rows)


def _chunk_batches(
    reader: pa.RecordBatchReader,
    *,
    schema: pa.Schema,
    encoding: tiktoken.Encoding,
    telemetry: RuntimeTelemetry,
    stats: dict[str, Any],
) -> Iterator[pa.RecordBatch]:
    """batch 단위로 chunk 측정 -> RecordBatch를 yield하고 즉시 참조를 놓는다."""
    for batch in reader:
        pair_ids = batch.column("pair_id").to_pylist()
        tok_ids = batch.column("tokenizer_measurement_id").to_pylist()
        ko_texts = batch.column("ko_text").to_pylist()
        en_texts = batch.column("en_text").to_pylist()
        ko_tokens = batch.column("ko_token_ids").to_pylist()
        en_tokens = batch.column("en_token_ids").to_pylist()
        records = []
        for pid, tid, kt, et, ktok, etok in zip(
                pair_ids, tok_ids, ko_texts, en_texts, ko_tokens, en_tokens, strict=True):
            record = build_chunk_record(pid, tid, kt, et, ktok, etok, encoding=encoding)
            if not record["token_equivalence_ok"]:
                stats["token_mismatch"] += 1
                stats["token_mismatch_pair_ids"].append(pid)
            if record["analysis_warning_flag"]:
                stats["warnings"] += 1
            records.append(record)
        stats["rows"] += len(records)
        yield pa.RecordBatch.from_pylist(records, schema=schema)
        telemetry.update(len(records))
        del pair_ids, tok_ids, ko_texts, en_texts, ko_tokens, en_tokens, records, batch


def execute_chunk_run(
    *,
    project_root: Path,
    token_path: Path,
    pair_registry_path: Path,
    output_path: Path,
    runtime_dir: Path,
    run_id: str,
    run_mode: str,
    limit: int | None,
    pair_ids: Sequence[str] | None = None,
    batch_rows: int = 2_500,
    cache_dir: Path | None = None,
    telemetry_interval_sec: float = 10.0,
) -> dict[str, Any]:
    """
    /**
     * @purpose bounded-memory streaming으로 D-05 chunk 측정 artifact를 생성한다.
     * @spec_ref SSOT §12.5; §38; R1 periodic telemetry
     * @param limit None이면 전체 cohort; pair_ids가 주어지면 그 부분집합만
     * @return manifest dict (row count, sha256, telemetry, invariant 통계)
     * @raises FileExistsError 목적지 또는 partial이 이미 존재하는 경우
     * @validation row/id 유일성, D-04 pair-set 일치, token 등가성을 promotion 전에 검사한다.
     * @artifact CHUNK_O200K_BASE parquet + manifest
     */
    """
    output_partial = output_path.with_suffix(output_path.suffix + ".partial")
    if output_path.exists() or output_partial.exists():
        raise FileExistsError("CHUNK_O200K 목적지 또는 partial이 이미 존재한다; 자동 재시작은 금지된다")

    schema = chunk_schema()
    start = dt.datetime.now(tz=_KST)
    runtime_dir.mkdir(parents=True, exist_ok=True)
    encoding = load_o200k_base_offline(cache_dir)
    identity = assert_tokenizer_identity(encoding)

    connection = duckdb.connect()
    try:
        total_available = int(
            _fetchone_required(
                connection.execute(f"SELECT count(*) FROM read_parquet({_sql_literal(token_path)})"))[0])
        if pair_ids is not None:
            expected_rows = len(pair_ids)
        elif limit is None:
            expected_rows = total_available
        else:
            expected_rows = min(limit, total_available)

        stage_started = time.monotonic()
        reader = cohort_reader(connection, token_path=token_path,
                               pair_registry_path=pair_registry_path,
                               batch_rows=batch_rows, limit=limit, pair_ids=pair_ids)
        stats: dict[str, Any] = {"rows": 0, "warnings": 0, "token_mismatch": 0,
                                 "token_mismatch_pair_ids": []}
        with RuntimeTelemetry(run_id=run_id, stage=f"D05_{run_mode}", total=expected_rows,
                              interval_sec=telemetry_interval_sec) as telemetry:
            def validate(path: Path) -> None:
                validate_chunk_measurements(path, expected_rows=expected_rows)

            write_result = write_parquet_batches_atomic(
                output_path, schema,
                _chunk_batches(reader, schema=schema, encoding=encoding,
                               telemetry=telemetry, stats=stats),
                validate=validate)
        stage_duration = round(time.monotonic() - stage_started, 3)
        telemetry.write(runtime_dir / f"telemetry_{run_id}.json")
    finally:
        connection.close()

    end = dt.datetime.now(tz=_KST)
    return {
        "artifact_id": f"CHUNK_O200K_BASE_MANIFEST_{run_mode}_v001",
        "run_id": run_id,
        "run_mode": run_mode,
        "ssot_naming_ref": "SSOT §38 CHUNK_O200K_BASE_v001.parquet",
        "input": {
            "token_o200k_base": {"path": str(token_path.relative_to(project_root)),
                                 "sha256": sha256_file(token_path)},
            "pair_registry": {"path": str(pair_registry_path.relative_to(project_root)),
                              "sha256": sha256_file(pair_registry_path)},
        },
        "output": {"path": str(output_path.relative_to(project_root)),
                   "sha256": sha256_file(output_path),
                   "row_count": write_result.row_count,
                   "column_count": len(schema.names),
                   "schema_version": CHUNK_SCHEMA_VERSION},
        "expected_rows": expected_rows,
        "tokenizer_identity": identity,
        "chunking_config": CHUNKING_CONFIG,
        "chunking_config_sha256": CHUNKING_CONFIG_SHA256,
        "batch_rows": batch_rows,
        "stage_duration_sec": stage_duration,
        "rows_per_sec": round(write_result.row_count / stage_duration, 1) if stage_duration else None,
        "warnings": stats["warnings"],
        "token_equivalence_mismatches": stats["token_mismatch"],
        "token_mismatch_pair_ids": stats["token_mismatch_pair_ids"][:100],
        "runtime_telemetry": telemetry.summary(),
        "start_kst": start.isoformat(timespec="seconds"),
        "end_kst": end.isoformat(timespec="seconds"),
        "validation_status": "PASS",
    }


def validate_chunk_measurements(path: Path, *, expected_rows: int) -> None:
    """row 수, id 유일성, share 합, token 등가성을 promotion 직전에 검사한다."""
    connection = duckdb.connect()
    try:
        relation = f"read_parquet({_sql_literal(path)})"
        rows, distinct_pair, distinct_id = _fetchone_required(connection.execute(
            f"SELECT count(*), count(DISTINCT pair_id), count(DISTINCT chunk_measurement_id)"
            f" FROM {relation}"))
        if not (int(rows) == int(distinct_pair) == int(distinct_id) == expected_rows):
            raise ValueError("CHUNK row count 또는 pair_id/measurement_id 유일성 검증 실패")

        bad = _fetchone_required(connection.execute(f"""
            SELECT count(*) FROM {relation}
            WHERE ko_chunk_count <= 0 OR en_chunk_count <= 0
               OR ko_chunk_token_total <= 0 OR en_chunk_token_total <= 0
               OR NOT chunk_reconstruction_ok
               OR NOT token_equivalence_ok
               OR abs((ko_chunk_type_share_letter + ko_chunk_type_share_number
                       + ko_chunk_type_share_punctuation + ko_chunk_type_share_whitespace) - 1.0) > 1e-9
               OR abs((en_chunk_type_share_letter + en_chunk_type_share_number
                       + en_chunk_type_share_punctuation + en_chunk_type_share_whitespace) - 1.0) > 1e-9
               OR abs(ko_tokens_per_chunk - ko_chunk_token_total::DOUBLE / ko_chunk_count) > 1e-12
               OR abs(en_tokens_per_chunk - en_chunk_token_total::DOUBLE / en_chunk_count) > 1e-12
               OR abs(ko_mean_chunk_bytes - ko_chunk_byte_total::DOUBLE / ko_chunk_count) > 1e-12
               OR abs(pair_chunk_ratio - ko_chunk_count::DOUBLE / en_chunk_count) > 1e-12
            """))[0]
        if int(bad) != 0:
            raise ValueError("CHUNK invariant 검증 실패")
    finally:
        connection.close()


__all__ = [
    "CHUNKING_CONFIG",
    "CHUNKING_CONFIG_SHA256",
    "CHUNK_RELATIVE_PATH",
    "CHUNK_RULE_VERSION",
    "CHUNK_SCHEMA_VERSION",
    "CHUNK_TYPES",
    "ChunkConfigMismatch",
    "ChunkInvariantViolation",
    "assert_tokenizer_identity",
    "build_chunk_record",
    "chunk_measurement_id",
    "chunk_pattern",
    "chunk_schema",
    "classify_chunk",
    "cohort_reader",
    "execute_chunk_run",
    "regex_chunks",
    "side_chunk_features",
    "validate_chunk_measurements",
]
