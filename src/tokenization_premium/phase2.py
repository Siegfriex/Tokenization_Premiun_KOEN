"""Phase-2 minimal-QC engineering primitives fixed by the v1.1 contract."""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import os
import subprocess
import time
import unicodedata
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Protocol
from zoneinfo import ZoneInfo

import duckdb
import pyarrow as pa
import pyarrow.parquet as pq

from tokenization_premium.progress import ProgressHeartbeat
from tokenization_premium.registry import provenance_pair_id, resolve_duckdb_memory_limit

P2_CONTRACT_COMMIT = "b9990afbf3fc0ed2a5e80fb4def1565e9ba3ebf4"
P2_CONTRACT_GIT_OBJECT = f"{P2_CONTRACT_COMMIT}:docs/contracts/P2_NORMALIZE_QC_PRECONTRACT_v1.md"
BLOCKED_BY_P2_CONTRACT = "BLOCKED_BY_P2_CONTRACT"
PAIR_REGISTRY_V001_RELATIVE_PATH = Path("data/registry/PAIR_REGISTRY_v001.parquet")
PAIR_REGISTRY_V002_RELATIVE_PATH = Path("data/registry/PAIR_REGISTRY_v002.parquet")
EXPECTED_D01_ROW_COUNT = 5_652_925
NORMALIZATION_RULE_VERSION = "p2_norm_v001"
NORMALIZATION_OPERATIONS = ("NFC", "BOM_STRIP", "OUTER_TRIM")
LANGUAGE_MIN_EVIDENCE = 5
LANGUAGE_SUBSTANTIAL_EVIDENCE = 5
EXACT_DUPLICATE_IDENTITY_SCOPE = "EXACT_RAW_KO_EN_ONLY_NOT_NEAR_DUPLICATE_OR_PARAPHRASE"
P2_OUTPUT_SCHEMA_VERSION = "PAIR_REGISTRY_v002"
P2_THREADS = 4
P2_DUCKDB_MEMORY_LIMIT = "6GB"
P2_NORMALIZATION_OPS_JSON = '["NFC","BOM_STRIP","OUTER_TRIM"]'
_KST = ZoneInfo("Asia/Seoul")

type QCFlags = Mapping[str, pa.Array | pa.ChunkedArray]
type ArtifactValidator = Callable[[Path], None]
type LanguageSide = Literal["KO", "EN"]
type LanguageSideReason = Literal[
    "KO_NO_HANGUL_LATIN_DOMINANT",
    "EN_NO_LATIN_HANGUL_DOMINANT",
    "INSUFFICIENT_LINGUISTIC_EVIDENCE",
    "NONE",
]


@dataclass(frozen=True)
class NormalizationResult:
    """SSOT raw→NFC→analysis result plus raw-based anomaly visibility."""

    nfc_text: str
    analysis_text: str
    operations: tuple[str, ...]
    unicode_anomaly_flag: bool
    unicode_anomaly_reasons: tuple[str, ...]


@dataclass(frozen=True)
class LanguageSideReview:
    """Model-free advisory result; this type cannot encode a rejection."""

    lang_side_anomaly_review_flag: bool
    lang_side_anomaly_reason: LanguageSideReason
    hangul_count: int
    latin_count: int
    alphabetic_evidence: int


@dataclass(frozen=True)
class D01HandoffSummary:
    """Safe manifest/oracle assertions without a population rescan."""

    status: Literal["PASS"]
    row_count: int
    pair_id_distinct: int
    canonical_input_count: int


@dataclass(frozen=True)
class D01RowLinkage:
    """Synthetic/batch-level D-01 lineage assertions without retaining text."""

    pair_id_integrity: bool
    raw_locator_present: bool
    canonical_ingest_linked: bool
    raw_sha_linked: bool


@dataclass(frozen=True)
class AtomicParquetWriteResult:
    """Validated partial artifact promoted to its final path."""

    path: Path
    row_count: int
    batch_count: int


@dataclass(frozen=True)
class Phase2PopulationResult:
    """Safe aggregate evidence returned to the canonical notebook."""

    run_id: str
    input_sha256: str
    output_sha256: str
    row_count: int
    output_column_count: int
    execution_code_commit: str
    start_kst: str
    end_kst: str
    peak_rss_gib: float
    minimum_available_memory_gib: float
    stage_durations_sec: Mapping[str, float]
    qc_counts: Mapping[str, int]
    language_side_counts: Mapping[str, int]
    output_path: str
    validation_status: str


class QCFlagComputer(Protocol):
    """Batch-to-flags extension point for the future authorized full run."""

    def compute(self, batch: pa.RecordBatch) -> QCFlags: ...


class StatusDeriver(Protocol):
    """Flags-to-status extension point for the future authorized full run."""

    def derive(self, flags: QCFlags) -> pa.Array: ...


class AuditSummaryBuilder(Protocol):
    """Raw-text-free numeric audit summary extension point."""

    def summarize(self, *, processed: int, metrics: Mapping[str, int | float]) -> Mapping[str, int | float]: ...


def manual_audit_import_schema() -> pa.Schema:
    """Return the nullable manual-only interface without fabricating labels."""
    return pa.schema(
        [
            pa.field("pair_id", pa.string(), nullable=False),
            pa.field("manual_semantic_score", pa.int8(), nullable=True),
            pa.field("manual_language_side_status", pa.string(), nullable=True),
            pa.field("manual_audit_status", pa.string(), nullable=True),
        ]
    )


def named_entity_deferred_fields() -> Mapping[str, bool | str | None]:
    """Expose the contract-required nullable NER fields without a heuristic or model."""
    return {"named_entity_heavy_flag": None, "named_entity_evaluation_status": "DEFERRED"}


def _unicode_anomaly_reasons(raw_text: str) -> tuple[str, ...]:
    reasons: list[str] = []
    edge_bom_stripped = raw_text.strip("\ufeff")
    if any(character in edge_bom_stripped for character in ("\u200b", "\u200c", "\u200d", "\ufeff")):
        reasons.append("INTERNAL_ZERO_WIDTH")
    if any(unicodedata.category(character) == "Cc" and character not in "\t\n" for character in raw_text):
        reasons.append("CONTROL_CHARACTER")
    previous_is_base = False
    for character in raw_text:
        if unicodedata.combining(character):
            if not previous_is_base:
                reasons.append("ORPHAN_COMBINING_MARK")
                break
        else:
            previous_is_base = not character.isspace()
    return tuple(reasons)


def normalize_ssot_text(text: str) -> NormalizationResult:
    """Apply NFC, edge-only U+FEFF stripping, then outer whitespace trim."""
    if not isinstance(text, str):
        raise TypeError("normalization input must be str")
    nfc_text = unicodedata.normalize("NFC", text)
    without_edge_bom = nfc_text.strip("\ufeff")
    analysis_text = without_edge_bom.strip()
    anomaly_reasons = _unicode_anomaly_reasons(text)
    return NormalizationResult(
        nfc_text=nfc_text,
        analysis_text=analysis_text,
        operations=NORMALIZATION_OPERATIONS,
        unicode_anomaly_flag=bool(anomaly_reasons),
        unicode_anomaly_reasons=anomaly_reasons,
    )


def empty_text_flag(ko_text_raw: object, en_text_raw: object) -> bool:
    """Flag null/non-string input or either side empty after frozen normalization."""
    if not isinstance(ko_text_raw, str) or not isinstance(en_text_raw, str):
        return True
    return not normalize_ssot_text(ko_text_raw).analysis_text or not normalize_ssot_text(en_text_raw).analysis_text


def _script_counts(text: str) -> tuple[int, int]:
    hangul = sum("\uac00" <= character <= "\ud7a3" for character in text)
    latin = sum(("A" <= character <= "Z") or ("a" <= character <= "z") for character in text)
    return hangul, latin


def language_side_anomaly_review(text: str, *, expected_side: LanguageSide) -> LanguageSideReview:
    """Run the conservative Unicode-script wiring smoke check from P2 v1.1."""
    if not isinstance(text, str):
        raise TypeError("language-side input must be str")
    if expected_side not in {"KO", "EN"}:
        raise ValueError("expected_side must be 'KO' or 'EN'")
    hangul, latin = _script_counts(text)
    evidence = hangul + latin
    if evidence < LANGUAGE_MIN_EVIDENCE:
        reason: LanguageSideReason = "INSUFFICIENT_LINGUISTIC_EVIDENCE"
    elif expected_side == "KO" and hangul == 0 and latin >= LANGUAGE_SUBSTANTIAL_EVIDENCE:
        reason = "KO_NO_HANGUL_LATIN_DOMINANT"
    elif expected_side == "EN" and latin == 0 and hangul >= LANGUAGE_SUBSTANTIAL_EVIDENCE:
        reason = "EN_NO_LATIN_HANGUL_DOMINANT"
    else:
        reason = "NONE"
    return LanguageSideReview(
        lang_side_anomaly_review_flag=reason != "NONE",
        lang_side_anomaly_reason=reason,
        hangul_count=hangul,
        latin_count=latin,
        alphabetic_evidence=evidence,
    )


def derive_pair_quality_status(structural_flags: Mapping[str, bool]) -> Literal["accepted", "rejected"]:
    """Gate only on the five contract-frozen structural flags, never advisory review flags."""
    hard_flags = (
        "empty_text_flag",
        "decode_integrity_flag",
        "markup_dominant_flag",
        "control_char_excess_flag",
        "exact_duplicate_flag",
    )
    return "rejected" if any(bool(structural_flags.get(name, False)) for name in hard_flags) else "accepted"


def decode_integrity_ok(text: str) -> bool:
    """Check Unicode readability only; tokenizer roundtrip belongs to G3."""
    if "\ufffd" in text:
        return False
    return not any(0xD800 <= ord(character) <= 0xDFFF for character in text)


def select_analysis_representative_pair_id(candidates: Sequence[Mapping[str, object]]) -> str:
    """Choose primary-analysis-eligible first, then stable min(pair_id)."""
    if not candidates:
        raise ValueError("duplicate group candidates must not be empty")
    pair_ids = [candidate.get("pair_id") for candidate in candidates]
    if any(not isinstance(pair_id, str) or not pair_id for pair_id in pair_ids):
        raise ValueError("every candidate must have a non-empty string pair_id")
    if len(set(pair_ids)) != len(pair_ids):
        raise ValueError("candidate pair_id values must be unique")
    eligible = [
        str(candidate["pair_id"])
        for candidate in candidates
        if candidate.get("primary_analysis_eligible") is True
    ]
    return min(eligible) if eligible else min(str(pair_id) for pair_id in pair_ids)


def validate_d01_manifest_handoff(
    manifest: Mapping[str, object], ingest_contract: Mapping[str, object]
) -> D01HandoffSummary:
    """Assert the already-recorded D-01 manifest and canonical ingest oracle agree."""
    validation = manifest.get("validation")
    pair_registry = manifest.get("pair_registry")
    expected_counts = ingest_contract.get("expected_logical_record_counts")
    prevention = ingest_contract.get("double_ingest_prevention_contract")
    if not all(isinstance(item, Mapping) for item in (validation, pair_registry, expected_counts, prevention)):
        raise ValueError("D-01 manifest or ingest contract structure is invalid")
    assert isinstance(validation, Mapping)
    assert isinstance(pair_registry, Mapping)
    assert isinstance(expected_counts, Mapping)
    assert isinstance(prevention, Mapping)
    row_count = int(pair_registry["row_count"])
    expected_total = int(expected_counts["total"])
    pair_id_distinct = int(validation["pair_id_distinct"])
    if manifest.get("cross_agent_contract") != "PASS" or validation.get("status") != "PASS":
        raise ValueError("D-01 manifest is not PASS")
    if row_count != EXPECTED_D01_ROW_COUNT or expected_total != row_count:
        raise ValueError("D-01 row count does not match the canonical oracle")
    if pair_id_distinct != row_count:
        raise ValueError("D-01 pair_id integrity is not PASS")
    manifest_inputs = manifest.get("input_file_hashes")
    oracle_inputs = prevention.get("ingest_allowlist")
    if not isinstance(manifest_inputs, list) or not isinstance(oracle_inputs, list):
        raise ValueError("canonical input inventories are missing")
    manifest_links = {(item["relative_path"], item["sha256"]) for item in manifest_inputs}
    oracle_links = {(item["relative_path"], item["sha256"]) for item in oracle_inputs}
    if manifest_links != oracle_links:
        raise ValueError("D-01 raw SHA linkage differs from the canonical ingest oracle")
    return D01HandoffSummary("PASS", row_count, pair_id_distinct, len(oracle_links))


def validate_d01_row_linkage(row: Mapping[str, object], ingest_contract: Mapping[str, object]) -> D01RowLinkage:
    """Validate one row's pair identity, locator, allowlist role, and raw SHA linkage."""
    required_strings = (
        "pair_id",
        "source_id",
        "source_record_id",
        "raw_locator",
        "canonical_ingest_role",
        "raw_file_relative_path",
        "raw_file_sha256",
    )
    if any(not isinstance(row.get(name), str) or not row[name] for name in required_strings):
        raise ValueError("D-01 row is missing required provenance linkage")
    pair_id_valid = row["pair_id"] == provenance_pair_id(str(row["source_id"]), str(row["source_record_id"]))
    try:
        locator = json.loads(str(row["raw_locator"]))
    except json.JSONDecodeError as error:
        raise ValueError("raw_locator is not valid JSON") from error
    locator_present = isinstance(locator, Mapping) and bool(locator)
    prevention = ingest_contract.get("double_ingest_prevention_contract")
    if not isinstance(prevention, Mapping) or not isinstance(prevention.get("ingest_allowlist"), list):
        raise ValueError("canonical ingest allowlist is missing")
    matching = [
        item
        for item in prevention["ingest_allowlist"]
        if item["relative_path"] == row["raw_file_relative_path"]
    ]
    canonical_linked = len(matching) == 1 and matching[0]["canonical_ingest_role"] == row["canonical_ingest_role"]
    raw_sha_linked = len(matching) == 1 and matching[0]["sha256"] == row["raw_file_sha256"]
    result = D01RowLinkage(pair_id_valid, locator_present, canonical_linked, raw_sha_linked)
    if not all((result.pair_id_integrity, result.raw_locator_present, result.canonical_ingest_linked, result.raw_sha_linked)):
        raise ValueError("D-01 row linkage validation failed")
    return result


def iter_parquet_batches(path: Path, *, batch_size: int = 25_000) -> Iterator[pa.RecordBatch]:
    """Iterate over Parquet with bounded record batches."""
    if isinstance(batch_size, bool) or not isinstance(batch_size, int) or batch_size <= 0:
        raise ValueError("batch_size must be a positive integer")
    parquet_file = pq.ParquetFile(path)
    yield from parquet_file.iter_batches(batch_size=batch_size)


def write_parquet_batches_atomic(
    destination: Path,
    schema: pa.Schema,
    batches: Iterable[pa.RecordBatch],
    *,
    validate: ArtifactValidator,
) -> AtomicParquetWriteResult:
    """Write bounded batches to partial, validate, then atomically promote."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_suffix(destination.suffix + ".partial")
    if partial.exists():
        partial.unlink()
    row_count = 0
    batch_count = 0
    writer = pq.ParquetWriter(partial, schema=schema, compression="zstd")
    try:
        for batch in batches:
            if batch.schema != schema:
                raise ValueError("record batch schema does not match declared output schema")
            writer.write_batch(batch)
            row_count += batch.num_rows
            batch_count += 1
    finally:
        writer.close()
    validate(partial)
    os.replace(partial, destination)
    return AtomicParquetWriteResult(path=destination, row_count=row_count, batch_count=batch_count)


def open_phase2_duckdb(runtime_dir: Path, environ: Mapping[str, str] | None = None) -> duckdb.DuckDBPyConnection:
    """Open Phase-2 DuckDB with the 8GB default and mandatory spill directory."""
    runtime_dir.mkdir(parents=True, exist_ok=True)
    runtime_literal = str(runtime_dir.resolve()).replace("'", "''")
    memory_limit = resolve_duckdb_memory_limit(environ)
    connection = duckdb.connect()
    try:
        connection.execute("SET preserve_insertion_order = false")
        connection.execute(f"SET memory_limit = '{memory_limit}'")
        connection.execute(f"SET temp_directory = '{runtime_literal}'")
    except Exception:
        connection.close()
        raise
    return connection


def _sql_literal(value: str | Path) -> str:
    return "'" + str(value).replace("'", "''") + "'"


def _git_head(project_root: Path) -> str:
    completed = subprocess.run(
        ["git", "-C", str(project_root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _fetchone_required(connection: duckdb.DuckDBPyConnection) -> tuple[Any, ...]:
    row = connection.fetchone()
    if row is None:
        raise RuntimeError("DuckDB query unexpectedly returned no row")
    return row


def _sha256_file(path: Path, *, heartbeat: ProgressHeartbeat, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(chunk_size):
            digest.update(chunk)
            heartbeat.update(len(chunk))
    return digest.hexdigest()


def _atomic_csv(path: Path, fieldnames: Sequence[str], rows: Sequence[Mapping[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_suffix(path.suffix + ".partial")
    if partial.exists():
        raise FileExistsError(f"refusing to overwrite partial report: {partial}")
    with partial.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(partial, path)


def _atomic_json(path: Path, payload: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_suffix(path.suffix + ".partial")
    if partial.exists():
        raise FileExistsError(f"refusing to overwrite partial report: {partial}")
    with partial.open("w", encoding="utf-8") as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(partial, path)


def _population_sql(input_path: Path, output_partial_path: Path, original_columns: Sequence[str]) -> str:
    replacements = {
        "ko_text_nfc": "__ko_nfc",
        "en_text_nfc": "__en_nfc",
        "ko_text_analysis": "__ko_analysis",
        "en_text_analysis": "__en_analysis",
        "pair_quality_status": "__pair_quality_status",
        "pair_quality_score": "NULL::DOUBLE",
        "pair_version": "'v002'",
        "normalization_status": "'NORMALIZED_PHASE2'",
        "qc_stage_status": "'PHASE2_COMPLETE'",
    }
    original_select = ",\n                ".join(
        f"{replacements.get(column, f'\"{column}\"')} AS \"{column}\"" for column in original_columns
    )
    markup_pattern = r"</?[A-Za-z][^>]*>|https?://[^[:space:]]+|www\.[^[:space:]]+|[A-Za-z_][A-Za-z0-9_]*\([^)]*\)"
    return f"""
        COPY (
            WITH normalized AS (
                SELECT
                    *,
                    nfc_normalize(ko_text_raw) AS __ko_nfc,
                    nfc_normalize(en_text_raw) AS __en_nfc
                FROM read_parquet({_sql_literal(input_path)})
            ), analyzed AS (
                SELECT
                    *,
                    trim(trim(__ko_nfc, chr(65279))) AS __ko_analysis,
                    trim(trim(__en_nfc, chr(65279))) AS __en_analysis
                FROM normalized
            ), ranked AS (
                SELECT
                    *,
                    ntile(5) OVER (ORDER BY length(__en_analysis), pair_id) AS __length_quintile,
                    coalesce(
                        min(pair_id) FILTER (WHERE logical_corpus IN ('025', '026'))
                            OVER (PARTITION BY duplicate_group_id),
                        min(pair_id) OVER (PARTITION BY duplicate_group_id)
                    ) AS __analysis_rep
                FROM analyzed
            ), measured AS (
                SELECT
                    *,
                    length(__ko_analysis) AS __ko_len,
                    length(__en_analysis) AS __en_len,
                    length(regexp_replace(__ko_analysis, '[^\\p{{N}}]', '', 'g')) AS __ko_digit,
                    length(regexp_replace(__en_analysis, '[^\\p{{N}}]', '', 'g')) AS __en_digit,
                    length(regexp_replace(__ko_analysis, '[^\\p{{P}}]', '', 'g')) AS __ko_punct,
                    length(regexp_replace(__en_analysis, '[^\\p{{P}}]', '', 'g')) AS __en_punct,
                    length(regexp_replace(__ko_analysis, '[^가-힣]', '', 'g')) AS __ko_hangul,
                    length(regexp_replace(__en_analysis, '[^가-힣]', '', 'g')) AS __en_hangul,
                    length(regexp_replace(__ko_analysis, '[^A-Za-z]', '', 'g')) AS __ko_latin,
                    length(regexp_replace(__en_analysis, '[^A-Za-z]', '', 'g')) AS __en_latin,
                    length(regexp_replace(__ko_analysis, '[^\\p{{L}}\\p{{N}}]', '', 'g')) AS __ko_alnum,
                    length(regexp_replace(__en_analysis, '[^\\p{{L}}\\p{{N}}]', '', 'g')) AS __en_alnum,
                    length(regexp_replace(__ko_analysis, '[^\\p{{Cc}}]', '', 'g'))
                        - length(regexp_replace(__ko_analysis, '[^\\t\\n]', '', 'g')) AS __ko_control,
                    length(regexp_replace(__en_analysis, '[^\\p{{Cc}}]', '', 'g'))
                        - length(regexp_replace(__en_analysis, '[^\\t\\n]', '', 'g')) AS __en_control,
                    list_reduce(
                        list_transform(regexp_extract_all(__ko_analysis, {_sql_literal(markup_pattern)}), x -> length(x)),
                        (x, y) -> x + y, 0
                    ) AS __ko_markup,
                    list_reduce(
                        list_transform(regexp_extract_all(__en_analysis, {_sql_literal(markup_pattern)}), x -> length(x)),
                        (x, y) -> x + y, 0
                    ) AS __en_markup
                FROM ranked
            ), flags AS (
                SELECT
                    *,
                    (__ko_analysis = '' OR __en_analysis = '') AS __empty,
                    (contains(__ko_analysis, chr(65533)) OR contains(__en_analysis, chr(65533))) AS __decode,
                    (coalesce(__ko_markup / nullif(__ko_len, 0), 0) > 0.5
                        OR coalesce(__en_markup / nullif(__en_len, 0), 0) > 0.5) AS __markup,
                    ((coalesce(__ko_control, 0)
                        + length(regexp_replace(__ko_analysis, '[^​‌‍﻿]', '', 'g'))) / greatest(__ko_len, 1) > 0.05
                        OR (coalesce(__en_control, 0)
                        + length(regexp_replace(__en_analysis, '[^​‌‍﻿]', '', 'g'))) / greatest(__en_len, 1) > 0.05) AS __control,
                    pair_id <> __analysis_rep AS __exact_duplicate,
                    (
                        contains(trim(ko_text_raw, chr(65279)), chr(65279))
                        OR regexp_matches(ko_text_raw, '[​‌‍]')
                        OR coalesce(__ko_control, 0) > 0
                        OR regexp_matches(ko_text_raw, '(^|\\s)\\p{{M}}')
                        OR contains(trim(en_text_raw, chr(65279)), chr(65279))
                        OR regexp_matches(en_text_raw, '[​‌‍]')
                        OR coalesce(__en_control, 0) > 0
                        OR regexp_matches(en_text_raw, '(^|\\s)\\p{{M}}')
                    ) AS __unicode_anomaly,
                    (coalesce(__ko_digit / nullif(__ko_len, 0), 0) > 0.20
                        OR coalesce(__en_digit / nullif(__en_len, 0), 0) > 0.20) AS __high_digit,
                    (coalesce(__ko_punct / nullif(__ko_len, 0), 0) > 0.20
                        OR coalesce(__en_punct / nullif(__en_len, 0), 0) > 0.20) AS __high_punct,
                    ((coalesce(__ko_hangul / nullif(__ko_alnum, 0), 0) >= 0.10
                        AND coalesce(__ko_latin / nullif(__ko_alnum, 0), 0) >= 0.10)
                        OR (coalesce(__en_hangul / nullif(__en_alnum, 0), 0) >= 0.10
                        AND coalesce(__en_latin / nullif(__en_alnum, 0), 0) >= 0.10)) AS __script_mix,
                    CASE
                        WHEN __ko_hangul + __ko_latin < 5 THEN 'INSUFFICIENT_LINGUISTIC_EVIDENCE'
                        WHEN __ko_hangul = 0 AND __ko_latin >= 5 THEN 'KO_NO_HANGUL_LATIN_DOMINANT'
                        ELSE 'NONE'
                    END AS __ko_side_reason,
                    CASE
                        WHEN __en_hangul + __en_latin < 5 THEN 'INSUFFICIENT_LINGUISTIC_EVIDENCE'
                        WHEN __en_latin = 0 AND __en_hangul >= 5 THEN 'EN_NO_LATIN_HANGUL_DOMINANT'
                        ELSE 'NONE'
                    END AS __en_side_reason
                FROM measured
            ), rejected AS (
                SELECT
                    *,
                    CASE
                        WHEN __empty THEN 'empty_text_flag'
                        WHEN __decode THEN 'decode_integrity_flag'
                        WHEN __markup THEN 'markup_dominant_flag'
                        WHEN __control THEN 'control_char_excess_flag'
                        WHEN __exact_duplicate THEN 'exact_duplicate_flag'
                        ELSE NULL
                    END AS __primary_rejection_reason,
                    CASE WHEN __empty OR __decode OR __markup OR __control OR __exact_duplicate
                        THEN 'rejected' ELSE 'accepted' END AS __pair_quality_status
                FROM flags
            )
            SELECT
                {original_select},
                '{NORMALIZATION_RULE_VERSION}' AS normalization_rule_version,
                {_sql_literal(P2_NORMALIZATION_OPS_JSON)} AS normalization_ops,
                __unicode_anomaly AS unicode_anomaly_flag,
                __empty AS empty_text_flag,
                __markup AS markup_dominant_flag,
                __control AS control_char_excess_flag,
                __decode AS decode_integrity_flag,
                __length_quintile = 1 AS short_text_flag,
                __length_quintile = 5 AS long_text_flag,
                __high_digit AS high_digit_ratio_flag,
                __high_punct AS high_punctuation_ratio_flag,
                __script_mix AS script_mix_flag,
                NULL::BOOLEAN AS translation_quality_review_flag,
                (__ko_side_reason <> 'NONE' OR __en_side_reason <> 'NONE') AS lang_side_anomaly_review_flag,
                CASE WHEN __ko_side_reason <> 'NONE' THEN __ko_side_reason ELSE __en_side_reason END
                    AS lang_side_anomaly_reason,
                __ko_side_reason AS ko_lang_side_anomaly_reason,
                __en_side_reason AS en_lang_side_anomaly_reason,
                NULL::BOOLEAN AS named_entity_heavy_flag,
                'DEFERRED' AS named_entity_evaluation_status,
                __primary_rejection_reason AS primary_rejection_reason,
                to_json(list_filter([
                    CASE WHEN __empty AND __primary_rejection_reason <> 'empty_text_flag' THEN 'empty_text_flag' END,
                    CASE WHEN __decode AND __primary_rejection_reason <> 'decode_integrity_flag' THEN 'decode_integrity_flag' END,
                    CASE WHEN __markup AND __primary_rejection_reason <> 'markup_dominant_flag' THEN 'markup_dominant_flag' END,
                    CASE WHEN __control AND __primary_rejection_reason <> 'control_char_excess_flag' THEN 'control_char_excess_flag' END,
                    CASE WHEN __exact_duplicate AND __primary_rejection_reason <> 'exact_duplicate_flag' THEN 'exact_duplicate_flag' END
                ], x -> x IS NOT NULL)) AS secondary_rejection_flags,
                __analysis_rep AS analysis_representative_pair_id,
                CASE WHEN pair_id = __analysis_rep THEN 'REPRESENTATIVE'
                    ELSE 'NON_REPRESENTATIVE_DUPLICATE' END AS duplicate_disposition,
                pair_id = __analysis_rep AS analysis_eligible_exact_dedup,
                'Q' || cast(__length_quintile AS VARCHAR) AS length_stratum
            FROM rejected
        ) TO {_sql_literal(output_partial_path)} (FORMAT PARQUET, COMPRESSION ZSTD, ROW_GROUP_SIZE 100000)
    """


def execute_phase2_population(
    *,
    project_root: Path,
    input_path: Path,
    output_path: Path,
    d01_manifest_path: Path,
    contract_path: Path,
    runtime_dir: Path,
    run_id: str,
) -> Phase2PopulationResult:
    """Execute the authorized population QC once, fail-closed, with safe evidence only."""
    output_partial = output_path.with_suffix(output_path.suffix + ".partial")
    if output_path.exists() or output_partial.exists():
        raise FileExistsError("canonical v002 or its partial already exists; automatic restart is forbidden")
    manifest = json.loads(d01_manifest_path.read_text(encoding="utf-8"))
    expected_sha = str(manifest["pair_registry"]["sha256"])
    expected_rows = int(manifest["pair_registry"]["row_count"])
    if expected_rows != EXPECTED_D01_ROW_COUNT:
        raise ValueError("D-01 manifest row count differs from the frozen population")

    start = dt.datetime.now(tz=_KST)
    stage_started = time.monotonic()
    stage_durations: dict[str, float] = {}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    runtime_dir.mkdir(parents=True, exist_ok=True)
    progress_dir = runtime_dir.parent / "progress"
    with ProgressHeartbeat(
        run_id=run_id,
        phase="P2",
        stage="INPUT_SHA256",
        total=input_path.stat().st_size,
        progress_dir=progress_dir,
    ) as heartbeat:
        input_sha = _sha256_file(input_path, heartbeat=heartbeat)
        stage_durations["input_sha256"] = round(time.monotonic() - stage_started, 3)
        heartbeat.checkpoint("INPUT_SHA256_VERIFIED", verified=1)
        if input_sha != expected_sha:
            raise ValueError(f"D-01 input SHA mismatch: expected {expected_sha}, observed {input_sha}")

        original_columns = pq.ParquetFile(input_path).schema_arrow.names
        stage_started = time.monotonic()
        heartbeat.set_stage("POPULATION_TRANSFORM_WRITE", total=EXPECTED_D01_ROW_COUNT)
        connection = open_phase2_duckdb(runtime_dir / "duckdb-spill", {"TOKENIZATION_PREMIUM_DUCKDB_MEMORY_LIMIT": P2_DUCKDB_MEMORY_LIMIT})
        try:
            connection.execute(f"SET threads = {P2_THREADS}")
            connection.execute(_population_sql(input_path, output_partial, original_columns))
        finally:
            connection.close()
        heartbeat.update(EXPECTED_D01_ROW_COUNT)
        heartbeat.checkpoint("V002_PARTIAL_WRITTEN", rows=EXPECTED_D01_ROW_COUNT)
        stage_durations["population_transform_write"] = round(time.monotonic() - stage_started, 3)

        stage_started = time.monotonic()
        heartbeat.set_stage("V002_VALIDATION", total=EXPECTED_D01_ROW_COUNT)
        connection = open_phase2_duckdb(runtime_dir / "duckdb-spill-validation", {"TOKENIZATION_PREMIUM_DUCKDB_MEMORY_LIMIT": P2_DUCKDB_MEMORY_LIMIT})
        try:
            connection.execute(f"SET threads = {P2_THREADS}")
            input_literal = _sql_literal(input_path)
            output_literal = _sql_literal(output_partial)
            row_count, pair_distinct = _fetchone_required(connection.execute(
                f"SELECT count(*), count(DISTINCT pair_id) FROM read_parquet({output_literal})"
            ))
            if int(row_count) != EXPECTED_D01_ROW_COUNT or int(pair_distinct) != EXPECTED_D01_ROW_COUNT:
                raise ValueError("v002 row or pair_id cardinality validation failed")
            raw_differences = _fetchone_required(connection.execute(
                f"""
                SELECT count(*) FROM read_parquet({input_literal}) i
                JOIN read_parquet({output_literal}) o USING (pair_id)
                WHERE i.ko_text_raw IS DISTINCT FROM o.ko_text_raw
                   OR i.en_text_raw IS DISTINCT FROM o.en_text_raw
                   OR i.raw_locator IS DISTINCT FROM o.raw_locator
                   OR i.raw_file_sha256 IS DISTINCT FROM o.raw_file_sha256
                """
            ))[0]
            if int(raw_differences) != 0:
                raise ValueError("v002 raw immutability validation failed")
            null_required = _fetchone_required(connection.execute(
                f"""
                SELECT count(*) FROM read_parquet({output_literal})
                WHERE ko_text_nfc IS NULL OR en_text_nfc IS NULL
                   OR ko_text_analysis IS NULL OR en_text_analysis IS NULL
                   OR analysis_representative_pair_id IS NULL
                   OR pair_quality_status NOT IN ('accepted', 'rejected')
                   OR qc_stage_status <> 'PHASE2_COMPLETE'
                """
            ))[0]
            if int(null_required) != 0:
                raise ValueError("v002 required Phase-2 fields validation failed")
        finally:
            connection.close()
        heartbeat.update(EXPECTED_D01_ROW_COUNT)
        heartbeat.checkpoint("V002_VALIDATED", rows=EXPECTED_D01_ROW_COUNT)
        os.replace(output_partial, output_path)
        stage_durations["v002_validation"] = round(time.monotonic() - stage_started, 3)

        stage_started = time.monotonic()
        heartbeat.set_stage("V002_SHA256", total=output_path.stat().st_size)
        output_sha = _sha256_file(output_path, heartbeat=heartbeat)
        stage_durations["v002_sha256"] = round(time.monotonic() - stage_started, 3)
        heartbeat.checkpoint("V002_SHA256_COMPLETE", verified=1)

        stage_started = time.monotonic()
        heartbeat.set_stage("SAFE_AGGREGATE_REPORTS", total=None)
        connection = open_phase2_duckdb(runtime_dir / "duckdb-spill-reporting", {"TOKENIZATION_PREMIUM_DUCKDB_MEMORY_LIMIT": P2_DUCKDB_MEMORY_LIMIT})
        try:
            connection.execute(f"SET threads = {P2_THREADS}")
            relation = f"read_parquet({_sql_literal(output_path)})"
            count_names = [
                "empty_text_flag", "decode_integrity_flag", "markup_dominant_flag",
                "control_char_excess_flag", "exact_duplicate_flag", "unicode_anomaly_flag",
                "high_digit_ratio_flag", "high_punctuation_ratio_flag", "script_mix_flag",
                "lang_side_anomaly_review_flag",
            ]
            aggregates = ", ".join(f"count(*) FILTER (WHERE {name})" for name in count_names)
            values = _fetchone_required(connection.execute(
                f"""
                SELECT count(*), count(DISTINCT duplicate_group_id),
                       count(*) FILTER (WHERE logical_corpus IN ('025','026')),
                       count(*) FILTER (WHERE logical_corpus IN ('025','026')
                           AND analysis_eligible_exact_dedup AND pair_quality_status='accepted'),
                       count(*) FILTER (WHERE pair_quality_status='accepted'),
                       count(*) FILTER (WHERE pair_quality_status='rejected'),
                       {aggregates}
                FROM {relation}
                """
            ))
            metric_names = [
                "raw_record_denominator", "exact_unique_content_denominator",
                "primary_eligible_denominator", "final_analysis_denominator",
                "accepted", "rejected", *count_names,
            ]
            qc_counts = {name: int(value) for name, value in zip(metric_names, values, strict=True)}
            language_rows = connection.execute(
                f"""
                SELECT side, reason, count
                FROM (
                    SELECT 'KO' AS side, ko_lang_side_anomaly_reason AS reason, count(*) AS count
                    FROM {relation} GROUP BY reason
                    UNION ALL
                    SELECT 'EN' AS side, en_lang_side_anomaly_reason AS reason, count(*) AS count
                    FROM {relation} GROUP BY reason
                ) ORDER BY side, reason
                """
            ).fetchall()
            language_counts = {f"{side}:{reason}": int(count) for side, reason, count in language_rows}
            sampling_rows = connection.execute(
                f"""
                SELECT source_id, domain, translation_direction, length_stratum, count(*) AS eligible_count
                FROM {relation}
                WHERE logical_corpus IN ('025','026')
                  AND analysis_eligible_exact_dedup
                  AND pair_quality_status='accepted'
                GROUP BY source_id, domain, translation_direction, length_stratum
                ORDER BY source_id, domain, translation_direction, length_stratum
                """
            ).fetchall()
        finally:
            connection.close()

        reports_dir = project_root / "outputs/reports"
        manifests_dir = project_root / "outputs/manifests"
        qc_flow_rows: list[dict[str, object]] = []
        for name, count in qc_counts.items():
            denominator = qc_counts["raw_record_denominator"]
            qc_flow_rows.append(
                {
                    "metric": name,
                    "count": count,
                    "denominator": denominator,
                    "rate": round(count / denominator, 12),
                    "interpretation": "aggregate_only_no_raw_text",
                }
            )
        _atomic_csv(
            reports_dir / "QC_FLOW_v001.csv",
            ["metric", "count", "denominator", "rate", "interpretation"],
            qc_flow_rows,
        )
        lid_rows = [
            {
                "report_scope": "language-side sanity / SSOT traceability; NOT model-based language identification",
                "side": key.split(":", 1)[0],
                "reason_category": key.split(":", 1)[1],
                "count": value,
                "denominator": EXPECTED_D01_ROW_COUNT,
                "rate": round(value / EXPECTED_D01_ROW_COUNT, 12),
                "disposition": "review_only_not_automatic_rejection",
            }
            for key, value in sorted(language_counts.items())
        ]
        _atomic_csv(
            reports_dir / "LID_QC_PASS_RATE_v001.csv",
            ["report_scope", "side", "reason_category", "count", "denominator", "rate", "disposition"],
            lid_rows,
        )
        _atomic_csv(
            reports_dir / "MANUAL_QC_SAMPLING_FRAME_SUMMARY_v001.csv",
            ["source_id", "domain", "translation_direction", "length_stratum", "eligible_count"],
            [
                {
                    "source_id": row[0], "domain": row[1], "translation_direction": row[2],
                    "length_stratum": row[3], "eligible_count": int(row[4]),
                }
                for row in sampling_rows
            ],
        )
        heartbeat.checkpoint("SAFE_REPORTS_WRITTEN", reports=3)
        stage_durations["safe_aggregate_reports"] = round(time.monotonic() - stage_started, 3)

    progress_jsonl = progress_dir / run_id / "progress.jsonl"
    snapshots = [json.loads(line) for line in progress_jsonl.read_text(encoding="utf-8").splitlines()]
    peak_rss = max(float(snapshot["rss_gib"]) for snapshot in snapshots)
    minimum_available = min(float(snapshot["mem_available_gib"]) for snapshot in snapshots)
    end = dt.datetime.now(tz=_KST)
    execution_code_commit = _git_head(project_root)
    contract_sha = hashlib.sha256(contract_path.read_bytes()).hexdigest()
    output_columns = len(pq.ParquetFile(output_path).schema_arrow.names)
    manifest_payload: dict[str, object] = {
        "artifact_id": "QC_MANIFEST_v001",
        "input": {"path": str(input_path.relative_to(project_root)), "sha256": input_sha},
        "output": {
            "path": str(output_path.relative_to(project_root)), "sha256": output_sha,
            "row_count": EXPECTED_D01_ROW_COUNT, "column_count": output_columns,
            "schema_version": P2_OUTPUT_SCHEMA_VERSION,
        },
        "contract": {"path": str(contract_path.relative_to(project_root)), "sha256": contract_sha,
                     "git_commit": P2_CONTRACT_COMMIT},
        "execution_code_commit": execution_code_commit,
        "runtime": {
            "duckdb_memory_limit": P2_DUCKDB_MEMORY_LIMIT, "threads": P2_THREADS,
            "spill_directory": str((runtime_dir / "duckdb-spill").relative_to(project_root)),
            "heartbeat_interval_sec": 10,
        },
        "resource_observation": {"peak_rss_gib": peak_rss, "minimum_available_memory_gib": minimum_available},
        "start_kst": start.isoformat(timespec="seconds"),
        "end_kst": end.isoformat(timespec="seconds"),
        "validation_status": "PASS",
        "manual_audit_status": "LOGISTICS_PENDING_SAMPLE_NOT_DRAWN",
        "language_side_note": "LID historical filename means language-side sanity / SSOT traceability, not model-based language identification",
        "stage_durations_sec": stage_durations,
    }
    _atomic_json(manifests_dir / "QC_MANIFEST_v001.json", manifest_payload)
    execution_report: dict[str, object] = {
        "artifact_id": "P2_EXECUTION_REPORT_v001",
        "run_id": run_id,
        "start_kst": start.isoformat(timespec="seconds"), "end_kst": end.isoformat(timespec="seconds"),
        "stage_durations_sec": stage_durations,
        "resource_observation": manifest_payload["resource_observation"],
        "qc_counts": qc_counts,
        "language_side_counts": language_counts,
        "normalization": {
            "rule_version": NORMALIZATION_RULE_VERSION,
            "operations": list(NORMALIZATION_OPERATIONS),
            "raw_columns_immutable": True,
            "internal_whitespace_preserved": True,
            "internal_u_fe_ff_observable": True,
        },
        "exact_duplicate_disposition": {
            "provenance_pointer_unchanged": True,
            "analysis_survivor_field": "analysis_representative_pair_id",
            "near_duplicate_claim": False,
        },
        "input_sha256": input_sha, "output_sha256": output_sha,
        "validation_status": "PASS",
        "manual_audit_status": "LOGISTICS_PENDING_SAMPLE_NOT_DRAWN",
    }
    _atomic_json(reports_dir / "P2_EXECUTION_REPORT_v001.json", execution_report)
    return Phase2PopulationResult(
        run_id=run_id, input_sha256=input_sha, output_sha256=output_sha,
        row_count=EXPECTED_D01_ROW_COUNT, output_column_count=output_columns,
        execution_code_commit=execution_code_commit,
        start_kst=start.isoformat(timespec="seconds"), end_kst=end.isoformat(timespec="seconds"),
        peak_rss_gib=peak_rss, minimum_available_memory_gib=minimum_available,
        stage_durations_sec=stage_durations, qc_counts=qc_counts,
        language_side_counts=language_counts,
        output_path=str(output_path.relative_to(project_root)), validation_status="PASS",
    )


__all__ = [
    "BLOCKED_BY_P2_CONTRACT",
    "EXACT_DUPLICATE_IDENTITY_SCOPE",
    "EXPECTED_D01_ROW_COUNT",
    "LANGUAGE_MIN_EVIDENCE",
    "LANGUAGE_SUBSTANTIAL_EVIDENCE",
    "NORMALIZATION_OPERATIONS",
    "NORMALIZATION_RULE_VERSION",
    "P2_CONTRACT_COMMIT",
    "P2_CONTRACT_GIT_OBJECT",
    "P2_DUCKDB_MEMORY_LIMIT",
    "P2_OUTPUT_SCHEMA_VERSION",
    "P2_THREADS",
    "PAIR_REGISTRY_V001_RELATIVE_PATH",
    "PAIR_REGISTRY_V002_RELATIVE_PATH",
    "AtomicParquetWriteResult",
    "Phase2PopulationResult",
    "AuditSummaryBuilder",
    "D01HandoffSummary",
    "D01RowLinkage",
    "LanguageSideReview",
    "NormalizationResult",
    "QCFlagComputer",
    "QCFlags",
    "StatusDeriver",
    "decode_integrity_ok",
    "derive_pair_quality_status",
    "empty_text_flag",
    "execute_phase2_population",
    "iter_parquet_batches",
    "language_side_anomaly_review",
    "manual_audit_import_schema",
    "named_entity_deferred_fields",
    "normalize_ssot_text",
    "open_phase2_duckdb",
    "select_analysis_representative_pair_id",
    "validate_d01_manifest_handoff",
    "validate_d01_row_linkage",
    "write_parquet_batches_atomic",
]
