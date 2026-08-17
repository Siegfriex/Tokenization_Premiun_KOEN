"""Phase-3 D-02 surface representation feature 추출 (NB03) 엔지니어링 구현.

SSOT 범위: UTF-8 byte, code point, grapheme, 공백, 문자군, 숫자·구두점 등
representation feature만 다룬다. 형태소(NB04)·tokenizer/BPE(NB05/NB06)·
semantic embedding·QC·모델링은 이 모듈의 범위 밖이다.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import time
import unicodedata
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import duckdb
import pyarrow as pa
import regex

from tokenization_premium.hashing import canonical_json_bytes, sha256_bytes, sha256_file
from tokenization_premium.phase2 import _fetchone_required, write_parquet_batches_atomic
from tokenization_premium.progress import ProgressHeartbeat

_KST = ZoneInfo("Asia/Seoul")

REPRESENTATION_RULE_VERSION = "rep_v001"  # 이 추출 규칙의 고정 버전 문자열이다.
REP_FEATURES_SCHEMA_VERSION = "REP_FEATURES_v001"  # 출력 schema 버전을 고정한다.
REP_FEATURES_RELATIVE_PATH = Path("data/registry/REP_FEATURES_v001.parquet")  # canonical 출력 경로를 고정한다.
COHORT_FILTER_SQL = (
    "pair_quality_status = 'accepted' AND analysis_eligible_exact_dedup "
    "AND logical_corpus IN ('025', '026')"
)  # D-RD-05 primary_analysis_eligible=true 소스만 후보 cohort로 인정한다.

_GRAPHEME_IMPLEMENTATION = f"regex=={regex.__version__} (UAX#29 extended grapheme clusters via \\X)"  # grapheme 구현 provenance를 고정한다.

# 6개 그룹이 모든 code point를 배타적으로 분할한다 (순서가 우선순위를 결정한다):
# hangul → latin → digit → punctuation → whitespace → other(symbol/mark/기타 문자 전부).
_CLASSIFY_PATTERN = regex.compile(
    r"(?P<hangul>\p{Script=Hangul})"
    r"|(?P<latin>\p{Script=Latin})"
    r"|(?P<digit>\p{Nd})"
    r"|(?P<punct>\p{P})"
    r"|(?P<space>\s)"
    r"|(?P<other>.)",
    flags=regex.VERSION1 | regex.DOTALL,
)
_GRAPHEME_PATTERN = regex.compile(r"\X", flags=regex.VERSION1)  # extended grapheme cluster 단위로 분할한다.
_URL_PATTERN = regex.compile(r"(?:https?://|www\.)\S+", flags=regex.IGNORECASE)  # http(s)/www 형태만 URL로 인정한다.
_EMAIL_PATTERN = regex.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")  # 표준적인 user@domain.tld 형태만 인정한다.
_EMOJI_PATTERN = regex.compile(r"\p{Extended_Pictographic}", flags=regex.VERSION1)  # 순수 digit/#/*는 제외하는 좁은 emoji 판정이다.
_CODE_LIKE_PATTERN = regex.compile(
    r"[{};]|=>|\b(?:function|def|import|class|return|const|let|var)\b|\w+\([^)]*\)",
    flags=regex.IGNORECASE,
)  # 중괄호/세미콜론/화살표/키워드/함수호출형 토큰 중 하나라도 있으면 code-like로 본다.

_SCRIPT_SWITCH_GROUPS = frozenset({"hangul", "latin", "other"})  # digit/punct/space는 switch 판정에서 중립으로 제외한다.

# SSOT §12.2 "lexical length" 변수군(ko_eojeol_count / en_word_count)의 분절 규칙이다.
# _CLASSIFY_PATTERN의 (?P<space>\s)와 동일한 regex VERSION1 Unicode whitespace class를 재사용해
# whitespace_count/space_run_count와 정의적으로 일관된 분절을 보장한다.
_LEXICAL_SPLIT_PATTERN = regex.compile(r"\s+", flags=regex.VERSION1)

REPRESENTATION_V2_LEXICAL_CONFIG: dict[str, Any] = {
    "rule_version": "rep_lexical_v002",
    "spec_ref": "SSOT §12.2 lexical length (ko_eojeol_count, en_word_count)",
    "decision_id": "RD-20260817-D02D03-CONFORMANCE-01",
    "ko_eojeol_count": "ko_text_analysis를 Unicode whitespace로 분리한 non-empty orthographic segment 수",
    "en_word_count": "en_text_analysis를 Unicode whitespace로 분리한 non-empty surface segment 수",
    "split_pattern": r"\s+",
    "split_engine": f"regex=={regex.__version__} VERSION1 (Unicode whitespace)",
    "prohibited": [
        "source text normalization or collapsing before counting",
        "punctuation stripping",
        "NFKC folding",
        "lowercasing",
    ],
    "hard_invalid_rule": "accepted final cohort에서 count == 0 이면 HARD_INVALID",
}  # v001의 REPRESENTATION_CONFIG는 변경하지 않는다; 신규 규칙만 별도 hash로 고정한다.
REPRESENTATION_V2_LEXICAL_CONFIG_SHA256 = sha256_bytes(canonical_json_bytes(REPRESENTATION_V2_LEXICAL_CONFIG))

REP_FEATURES_V2_SCHEMA_VERSION = "REP_FEATURES_v002"  # v002 출력 schema 버전을 고정한다.
REP_FEATURES_V2_RELATIVE_PATH = Path("data/registry/REP_FEATURES_v002.parquet")  # v002 canonical 경로를 고정한다.


def lexical_segment_count(text: str) -> int:
    """
    /**
     * @purpose SSOT §12.2 lexical length를 계산한다 (ko_eojeol_count / en_word_count 공용).
     * @spec_ref SSOT §12.2 lexical length; RD-20260817-D02D03-CONFORMANCE-01 §4
     * @param text ko_text_analysis 또는 en_text_analysis 원문 (정규화·치환 없이 그대로 사용)
     * @return Unicode whitespace로 분리한 non-empty segment 수
     * @raises RepresentationInputError 빈 문자열이 전달된 경우
     * @validation accepted cohort에서 결과가 0이면 HARD_INVALID로 판정한다.
     * @artifact REP_FEATURES_v002.parquet의 ko_eojeol_count / en_word_count 열
     */
    """
    if text == "":
        raise RepresentationInputError(
            "accepted cohort의 텍스트는 empty일 수 없다: lexical_segment_count는 빈 문자열을 거부한다"
        )
    return sum(1 for segment in _LEXICAL_SPLIT_PATTERN.split(text) if segment)


def rep_features_v002_schema() -> pa.Schema:
    """
    /**
     * @purpose REP_FEATURES_v002 = v001 47개 열 + SSOT §12.2 lexical length 2개 열의 계약을 고정한다.
     * @spec_ref SSOT §12.2; RD-20260817-D02D03-CONFORMANCE-01 §5
     * @return v001 field를 순서·dtype 그대로 보존하고 lexical length를 side별 grapheme_count 뒤에 삽입한 schema
     * @raises 없음
     * @validation v001 열 이름/dtype 집합이 v002에 그대로 포함되는지 단위 테스트로 검사한다.
     * @artifact data/registry/REP_FEATURES_v002.parquet
     */
    """
    lexical_field_by_side = {"ko_": "ko_eojeol_count", "en_": "en_word_count"}
    fields: list[pa.Field] = []
    for field in rep_features_schema():
        fields.append(field)
        if field.name in ("ko_grapheme_count", "en_grapheme_count"):
            side = field.name[:3]
            fields.append(pa.field(lexical_field_by_side[side], pa.int64(), nullable=False))
    return pa.schema(fields)

REPRESENTATION_CONFIG: dict[str, Any] = {
    "rule_version": REPRESENTATION_RULE_VERSION,
    "input_text_fields": ["ko_text_analysis", "en_text_analysis"],
    "classification_groups_in_priority_order": ["hangul", "latin", "digit", "punct", "space", "other"],
    "script_switch_groups": sorted(_SCRIPT_SWITCH_GROUPS),
    "grapheme_pattern": r"\X",
    "url_pattern": _URL_PATTERN.pattern,
    "email_pattern": _EMAIL_PATTERN.pattern,
    "emoji_pattern": _EMOJI_PATTERN.pattern,
    "code_like_pattern": _CODE_LIKE_PATTERN.pattern,
    "cohort_filter_sql": COHORT_FILTER_SQL,
}  # feature 정의를 하나의 dict로 고정해 config_sha256으로 provenance를 남긴다.
REPRESENTATION_CONFIG_SHA256 = sha256_bytes(canonical_json_bytes(REPRESENTATION_CONFIG))  # config 변경 여부를 hash 하나로 검증 가능하게 한다.


class RepresentationInputError(ValueError):
    """빈 문자열 등 accepted cohort에서 나타날 수 없는 입력을 명시적으로 거부한다."""


def side_features(text: str) -> dict[str, int | float | bool]:
    """
    /**
     * @purpose 한 언어 side 원문에서 D-02 surface representation feature를 계산한다.
     * @spec_ref SSOT §3.1 in-scope representation feature; Directive Task 3
     * @param text ko_text_analysis 또는 en_text_analysis 문자열 (accepted cohort는 empty 불가)
     * @return codepoint/grapheme/byte/공백/script share/flag 19개 feature dict
     * @raises RepresentationInputError 빈 문자열이 전달된 경우
     * @validation share 합이 1.0에 근접하는지, ratio 분모가 0이 아닌지 단위 테스트로 검사한다.
     * @artifact REP_FEATURES_v001.parquet의 ko_*/en_* 열
     */
    """
    if text == "":
        raise RepresentationInputError("accepted cohort의 텍스트는 empty일 수 없다: side_features는 빈 문자열을 거부한다")

    codepoint_count = len(text)  # Python str은 code point 단위 sequence이므로 len()이 정확한 code point 수다.
    utf8_bytes = len(text.encode("utf-8"))  # UTF-8 인코딩 후 byte 수를 계산한다.
    grapheme_count = len(_GRAPHEME_PATTERN.findall(text))  # UAX#29 extended grapheme cluster 수를 계산한다.

    counts = {"hangul": 0, "latin": 0, "digit": 0, "punct": 0, "space": 0, "other": 0}  # 6개 배타적 그룹의 code point 수를 누적한다.
    space_run_count = 0  # 연속 공백의 maximal run 개수를 누적한다.
    previous_group: str | None = None  # 직전 문자의 그룹을 기억해 공백 run과 script switch를 판정한다.
    switch_sequence: list[str] = []  # script switch 판정용으로 hangul/latin/other만 순서대로 남긴다.
    for match in _CLASSIFY_PATTERN.finditer(text):  # 문자열을 한 번만 순회하며 모든 code point를 분류한다.
        group = match.lastgroup or "other"  # 매칭된 named group 이름을 그룹 라벨로 사용한다.
        counts[group] += 1
        if group == "space" and previous_group != "space":  # 공백이 아닌 문자 뒤에 처음 나온 공백만 새 run으로 센다.
            space_run_count += 1
        if group in _SCRIPT_SWITCH_GROUPS:
            switch_sequence.append(group)
        previous_group = group
    script_switch_count = sum(
        1 for previous, current in zip(switch_sequence, switch_sequence[1:], strict=False) if previous != current
    )  # hangul/latin/other 사이의 인접 전환 횟수만 switch로 센다.
    script_type_count = len({group for group in switch_sequence})  # 실제로 등장한 script 그룹 종류 수를 센다.

    return {
        "codepoint_count": codepoint_count,
        "grapheme_count": grapheme_count,
        "utf8_bytes": utf8_bytes,
        "bytes_per_codepoint": utf8_bytes / codepoint_count,
        "bytes_per_grapheme": utf8_bytes / grapheme_count,
        "whitespace_count": counts["space"],
        "whitespace_density": counts["space"] / codepoint_count,
        "space_run_count": space_run_count,
        "hangul_share": counts["hangul"] / codepoint_count,
        "latin_share": counts["latin"] / codepoint_count,
        "digit_share": counts["digit"] / codepoint_count,
        "punctuation_share": counts["punct"] / codepoint_count,
        "symbol_other_share": counts["other"] / codepoint_count,
        "script_type_count": script_type_count,
        "script_switch_count": script_switch_count,
        "url_flag": bool(_URL_PATTERN.search(text)),
        "email_flag": bool(_EMAIL_PATTERN.search(text)),
        "emoji_flag": bool(_EMOJI_PATTERN.search(text)),
        "code_like_flag": bool(_CODE_LIKE_PATTERN.search(text)),
    }


def pair_cross_features(ko: dict[str, int | float | bool], en: dict[str, int | float | bool]) -> dict[str, float | int]:
    """
    /**
     * @purpose ko/en side feature에서 pair 수준 length-관련 representation 수량을 계산한다.
     * @spec_ref Directive Task 3 length-related representation quantities
     * @param ko side_features(ko_text_analysis) 결과
     * @param en side_features(en_text_analysis) 결과
     * @return pair_codepoint_ratio/pair_grapheme_ratio/pair_byte_ratio/pair_codepoint_diff
     * @raises 없음 (accepted cohort는 en 분모가 0이 될 수 없다)
     * @validation ratio가 codepoint_count 비율과 정확히 일치하는지 단위 테스트로 검사한다.
     * @artifact REP_FEATURES_v001.parquet의 pair_* 열
     */
    """
    return {
        "pair_codepoint_ratio": ko["codepoint_count"] / en["codepoint_count"],
        "pair_grapheme_ratio": ko["grapheme_count"] / en["grapheme_count"],
        "pair_byte_ratio": ko["utf8_bytes"] / en["utf8_bytes"],
        "pair_codepoint_diff": ko["codepoint_count"] - en["codepoint_count"],
    }


def rep_features_schema() -> pa.Schema:
    """
    /**
     * @purpose REP_FEATURES_v001 Parquet의 명시적 column 순서·dtype 계약을 고정한다.
     * @spec_ref Directive Task 3
     * @return pair_id, ko_*/en_* 19개씩, pair_* 4개, provenance 4개를 포함하는 PyArrow schema
     * @raises 없음
     * @validation 저장된 Parquet의 schema와 exact equality로 검사한다.
     * @artifact data/registry/REP_FEATURES_v001.parquet
     */
    """
    side_fields = [
        ("codepoint_count", pa.int64()),
        ("grapheme_count", pa.int64()),
        ("utf8_bytes", pa.int64()),
        ("bytes_per_codepoint", pa.float64()),
        ("bytes_per_grapheme", pa.float64()),
        ("whitespace_count", pa.int64()),
        ("whitespace_density", pa.float64()),
        ("space_run_count", pa.int64()),
        ("hangul_share", pa.float64()),
        ("latin_share", pa.float64()),
        ("digit_share", pa.float64()),
        ("punctuation_share", pa.float64()),
        ("symbol_other_share", pa.float64()),
        ("script_type_count", pa.int64()),
        ("script_switch_count", pa.int64()),
        ("url_flag", pa.bool_()),
        ("email_flag", pa.bool_()),
        ("emoji_flag", pa.bool_()),
        ("code_like_flag", pa.bool_()),
    ]
    fields = [pa.field("pair_id", pa.string(), nullable=False)]  # D-01/P2와 동일한 join key를 유지한다.
    for prefix in ("ko_", "en_"):
        fields.extend(pa.field(f"{prefix}{name}", dtype, nullable=False) for name, dtype in side_fields)
    fields.extend(
        [
            pa.field("pair_codepoint_ratio", pa.float64(), nullable=False),
            pa.field("pair_grapheme_ratio", pa.float64(), nullable=False),
            pa.field("pair_byte_ratio", pa.float64(), nullable=False),
            pa.field("pair_codepoint_diff", pa.int64(), nullable=False),
            pa.field("feature_extractor_version", pa.string(), nullable=False),
            pa.field("unicode_version", pa.string(), nullable=False),
            pa.field("grapheme_implementation", pa.string(), nullable=False),
            pa.field("config_sha256", pa.string(), nullable=False),
        ]
    )
    return pa.schema(fields)


def _row_to_record(pair_id: str, ko_text: str, en_text: str) -> dict[str, Any]:
    """단일 pair의 raw record dict를 rep_features_schema() 순서로 조립한다."""
    ko = side_features(ko_text)
    en = side_features(en_text)
    record: dict[str, Any] = {"pair_id": pair_id}
    record.update({f"ko_{name}": value for name, value in ko.items()})
    record.update({f"en_{name}": value for name, value in en.items()})
    record.update(pair_cross_features(ko, en))
    record["feature_extractor_version"] = REP_FEATURES_SCHEMA_VERSION
    record["unicode_version"] = unicodedata.unidata_version
    record["grapheme_implementation"] = _GRAPHEME_IMPLEMENTATION
    record["config_sha256"] = REPRESENTATION_CONFIG_SHA256
    return record


def _cohort_reader(
    connection: duckdb.DuckDBPyConnection,
    input_path: Path,
    *,
    limit: int | None,
    batch_size: int,
) -> pa.RecordBatchReader:
    """cohort filter를 적용한 pair_id/ko_text_analysis/en_text_analysis streaming reader를 연다."""
    limit_clause = f"LIMIT {int(limit)}" if limit is not None else ""
    query = f"""
        SELECT pair_id, ko_text_analysis, en_text_analysis
        FROM read_parquet({_sql_literal(input_path)})
        WHERE {COHORT_FILTER_SQL}
        ORDER BY pair_id
        {limit_clause}
    """
    return connection.execute(query).to_arrow_reader(batch_size=batch_size)


def _sql_literal(path: Path) -> str:
    return "'" + str(path).replace("'", "''") + "'"


def compute_cohort_fingerprint(input_path: Path, *, project_root: Path) -> dict[str, Any]:
    """
    /**
     * @purpose NB03 실행 전 candidate cohort를 재현 가능하게 fingerprint한다.
     * @spec_ref Directive Task 2 (operational fingerprint, 새 dataset version이 아님)
     * @param input_path PAIR_REGISTRY_v002.parquet 경로
     * @param project_root 상대경로 기록에 사용할 project root
     * @return input SHA, filter expression, N, sorted pair_id set hash, source/direction/domain 분포
     * @raises 없음
     * @validation N과 개별 dimension 합이 N과 일치하는지 단위 테스트로 검사한다.
     * @artifact outputs/manifests/CANDIDATE_COHORT_FINGERPRINT_v001.json
     */
    """
    connection = duckdb.connect()
    try:
        relation = f"read_parquet({_sql_literal(input_path)})"
        n_pairs = _fetchone_required(connection.execute(f"SELECT count(*) FROM {relation} WHERE {COHORT_FILTER_SQL}"))[0]
        source_counts = dict(
            connection.execute(
                f"SELECT logical_corpus, count(*) FROM {relation} WHERE {COHORT_FILTER_SQL} GROUP BY 1 ORDER BY 1"
            ).fetchall()
        )
        direction_counts = dict(
            connection.execute(
                f"SELECT translation_direction, count(*) FROM {relation} WHERE {COHORT_FILTER_SQL} GROUP BY 1 ORDER BY 1"
            ).fetchall()
        )
        domain_counts = dict(
            connection.execute(
                f"SELECT domain, count(*) FROM {relation} WHERE {COHORT_FILTER_SQL} GROUP BY 1 ORDER BY 1"
            ).fetchall()
        )
        pair_id_digest = hashlib.sha256()  # sorted pair_id 전체를 streaming으로 hash해 cohort identity를 만든다.
        reader = connection.execute(
            f"SELECT pair_id FROM {relation} WHERE {COHORT_FILTER_SQL} ORDER BY pair_id"
        ).to_arrow_reader(batch_size=200_000)
        for batch in reader:
            for pair_id in batch.column("pair_id"):
                pair_id_digest.update(pair_id.as_py().encode("utf-8"))
                pair_id_digest.update(b"\n")
    finally:
        connection.close()

    return {
        "artifact_id": "CANDIDATE_COHORT_FINGERPRINT_v001",
        "generated_at_kst": dt.datetime.now(tz=_KST).isoformat(timespec="seconds"),
        "input": {"path": str(input_path.relative_to(project_root)), "sha256": sha256_file(input_path)},
        "filter_expression": COHORT_FILTER_SQL,
        "n_pairs": int(n_pairs),
        "sorted_pair_id_set_sha256": pair_id_digest.hexdigest(),
        "source_counts": {str(k): int(v) for k, v in source_counts.items()},
        "direction_counts": {str(k): int(v) for k, v in direction_counts.items()},
        "domain_counts": {str(k): int(v) for k, v in domain_counts.items()},
        "note": "operational fingerprint only; not a new research dataset version",
    }


def execute_representation_population(
    *,
    project_root: Path,
    input_path: Path,
    output_path: Path,
    runtime_dir: Path,
    run_id: str,
    limit: int | None = None,
    batch_size: int = 20_000,
) -> dict[str, Any]:
    """
    /**
     * @purpose candidate cohort 전체(또는 pilot limit)에 D-02 representation feature를 계산해
     *          REP_FEATURES_v001.parquet을 atomic하게 생성한다.
     * @spec_ref Directive Task 3, Task 6-7; SSOT §3.1
     * @param input_path PAIR_REGISTRY_v002.parquet 경로
     * @param output_path REP_FEATURES_v001.parquet 목적지 (pilot은 별도 경로 사용)
     * @param limit pilot 실행 시 처리할 최대 행 수 (None이면 full population)
     * @return row_count, output sha256, stage duration, 기본 검증 결과를 포함하는 실행 요약
     * @raises FileExistsError 목적지 또는 partial이 이미 존재하는 경우
     * @raises ValueError 검증 invariant가 깨진 경우
     * @validation row/pair_id 유일성, share 범위, ratio 유한성을 promotion 전에 검사한다.
     * @artifact data/registry/REP_FEATURES_v001.parquet, outputs/manifests/REP_FEATURES_MANIFEST_v001.json
     */
    """
    output_partial = output_path.with_suffix(output_path.suffix + ".partial")
    if output_path.exists() or output_partial.exists():
        raise FileExistsError("canonical REP_FEATURES 또는 partial이 이미 존재한다; 자동 재시작은 금지된다")

    schema = rep_features_schema()
    start = dt.datetime.now(tz=_KST)
    stage_started = time.monotonic()
    runtime_dir.mkdir(parents=True, exist_ok=True)
    progress_dir = runtime_dir.parent / "progress"

    connection = duckdb.connect()
    try:
        relation = f"read_parquet({_sql_literal(input_path)})"
        total_rows = _fetchone_required(
            connection.execute(f"SELECT count(*) FROM {relation} WHERE {COHORT_FILTER_SQL}")
        )[0]
        total = min(int(total_rows), int(limit)) if limit is not None else int(total_rows)
        reader = _cohort_reader(connection, input_path, limit=limit, batch_size=batch_size)

        with ProgressHeartbeat(
            run_id=run_id,
            phase="NB03",
            stage="REPRESENTATION_TRANSFORM_WRITE",
            total=total,
            progress_dir=progress_dir,
        ) as heartbeat:

            def batches() -> Any:
                for record_batch in reader:
                    pair_ids = record_batch.column("pair_id").to_pylist()
                    ko_texts = record_batch.column("ko_text_analysis").to_pylist()
                    en_texts = record_batch.column("en_text_analysis").to_pylist()
                    records = [
                        _row_to_record(pair_id, ko_text, en_text)
                        for pair_id, ko_text, en_text in zip(pair_ids, ko_texts, en_texts, strict=True)
                    ]
                    heartbeat.update(len(records))
                    yield pa.RecordBatch.from_pylist(records, schema=schema)

            def validate(path: Path) -> None:
                _validate_rep_features(path, expected_rows=total)

            write_result = write_parquet_batches_atomic(output_path, schema, batches(), validate=validate)
            heartbeat.checkpoint("REP_FEATURES_WRITTEN", rows=write_result.row_count)
    finally:
        connection.close()

    stage_duration = round(time.monotonic() - stage_started, 3)
    output_sha256 = sha256_file(output_path)
    end = dt.datetime.now(tz=_KST)
    manifest = {
        "artifact_id": "REP_FEATURES_MANIFEST_v001",
        "run_id": run_id,
        "run_mode": "PILOT" if limit is not None else "FULL_POPULATION",
        "input": {"path": str(input_path.relative_to(project_root)), "sha256": sha256_file(input_path)},
        "output": {
            "path": str(output_path.relative_to(project_root)),
            "sha256": output_sha256,
            "row_count": write_result.row_count,
            "column_count": len(schema.names),
            "schema_version": REP_FEATURES_SCHEMA_VERSION,
        },
        "feature_extractor_version": REP_FEATURES_SCHEMA_VERSION,
        "unicode_version": unicodedata.unidata_version,
        "grapheme_implementation": _GRAPHEME_IMPLEMENTATION,
        "config_sha256": REPRESENTATION_CONFIG_SHA256,
        "start_kst": start.isoformat(timespec="seconds"),
        "end_kst": end.isoformat(timespec="seconds"),
        "stage_duration_sec": stage_duration,
        "validation_status": "PASS",
        "status": "PROVISIONAL_ENGINEERING_OUTPUT",
    }
    return manifest


def _validate_rep_features(path: Path, *, expected_rows: int) -> None:
    """row 수, pair_id 유일성, share/ratio invariant를 promotion 직전에 검사한다."""
    connection = duckdb.connect()
    try:
        relation = f"read_parquet({_sql_literal(path)})"
        row_count, distinct_pair_id = _fetchone_required(
            connection.execute(f"SELECT count(*), count(DISTINCT pair_id) FROM {relation}")
        )
        if int(row_count) != expected_rows or int(distinct_pair_id) != expected_rows:
            raise ValueError("REP_FEATURES row count 또는 pair_id 유일성 검증 실패")
        bad_share_rows = _fetchone_required(
            connection.execute(
                f"""
                SELECT count(*) FROM {relation}
                WHERE ko_hangul_share < 0 OR ko_hangul_share > 1
                   OR en_hangul_share < 0 OR en_hangul_share > 1
                   OR ko_codepoint_count <= 0 OR en_codepoint_count <= 0
                   OR ko_grapheme_count <= 0 OR en_grapheme_count <= 0
                   OR NOT isfinite(ko_bytes_per_codepoint) OR NOT isfinite(en_bytes_per_codepoint)
                   OR NOT isfinite(pair_codepoint_ratio) OR NOT isfinite(pair_byte_ratio)
                """
            )
        )[0]
        if int(bad_share_rows) != 0:
            raise ValueError("REP_FEATURES share/ratio invariant 검증 실패")
    finally:
        connection.close()


__all__ = [
    "COHORT_FILTER_SQL",
    "REPRESENTATION_CONFIG",
    "REPRESENTATION_CONFIG_SHA256",
    "REPRESENTATION_RULE_VERSION",
    "REPRESENTATION_V2_LEXICAL_CONFIG",
    "REPRESENTATION_V2_LEXICAL_CONFIG_SHA256",
    "REP_FEATURES_RELATIVE_PATH",
    "REP_FEATURES_SCHEMA_VERSION",
    "REP_FEATURES_V2_RELATIVE_PATH",
    "REP_FEATURES_V2_SCHEMA_VERSION",
    "RepresentationInputError",
    "compute_cohort_fingerprint",
    "execute_representation_population",
    "lexical_segment_count",
    "pair_cross_features",
    "rep_features_schema",
    "rep_features_v002_schema",
    "side_features",
]
