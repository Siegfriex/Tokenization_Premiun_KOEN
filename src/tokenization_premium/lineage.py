"""Canonical artifact lineage — fail-closed identity assertion.

Canonical notebook은 artifact를 "있으면 쓰고 없으면 넘어가는" 방식으로 소비하지 않는다.
경로·SHA-256·schema·row count·pair-set 중 하나라도 어긋나면 조용히 pilot/이전 버전으로
내려가지 않고 CanonicalArtifactIdentityMismatch를 던진다.

pin된 값의 출처는 Claude-B의 독립 forensic 판정이다:
  ssot/2026-08-17_1730_KOEN_TP_G2_G3_G4_FINAL_ADJUDICATION.md
  commit 441d5802bfebe178fd220d08b653c60dfad17faf
  G2_REPRESENTATION_INTEGRITY_PASS / G3_TOKENIZER_INTEGRITY_PASS / G4_MORPHOLOGY_INTEGRITY_PASS

B가 물리 artifact에서 직접 재계산한 값이므로 A의 manifest 보고가 아니라 이 값을 기준으로 삼는다.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import duckdb

from tokenization_premium.hashing import sha256_file
from tokenization_premium.paths import PROJECT_ROOT

ADJUDICATION_COMMIT = "441d5802bfebe178fd220d08b653c60dfad17faf"
ADJUDICATION_DOC = "ssot/2026-08-17_1730_KOEN_TP_G2_G3_G4_FINAL_ADJUDICATION.md"

# B가 세 artifact 전부에서 동일함을 확인한 정렬 pair-set 해시다 (§3).
CANONICAL_PAIR_SET_MD5 = "d9660d654ee449e4d0c23a0070225274"
CANONICAL_COHORT_N = 3_835_988  # SSOT-frozen reference cohort; runtime 값은 artifact에서 derive한다.


@dataclass(frozen=True)
class CanonicalArtifact:
    """B가 검증한 canonical artifact 하나의 신원."""

    name: str
    relative_path: str
    sha256: str
    row_count: int
    column_count: int
    id_column: str
    gate: str
    manifest: str

    @property
    def path(self) -> Path:
        return PROJECT_ROOT / self.relative_path


CANONICAL_ARTIFACTS: dict[str, CanonicalArtifact] = {
    "PAIR_REGISTRY_v002": CanonicalArtifact(
        name="PAIR_REGISTRY_v002",
        relative_path="data/registry/PAIR_REGISTRY_v002.parquet",
        sha256="95f523d11b0e8fcfd761dee949f082e9b4590b919801441fbcfa3426010bec52",
        row_count=5_652_925, column_count=69, id_column="pair_id",
        gate="G1", manifest="outputs/manifests/QC_MANIFEST_v001.json",
    ),
    "REP_FEATURES_v002": CanonicalArtifact(
        name="REP_FEATURES_v002",
        relative_path="data/registry/REP_FEATURES_v002.parquet",
        sha256="dfae8e01cd3fe2ca949d8754678e508203ad1a7aa6abea418008a33ac650d309",
        row_count=CANONICAL_COHORT_N, column_count=49, id_column="pair_id",
        gate="G2", manifest="outputs/manifests/REP_FEATURES_MANIFEST_v002.json",
    ),
    "MORPH_FEATURES_KIWI_v001": CanonicalArtifact(
        name="MORPH_FEATURES_KIWI_v001",
        relative_path="data/registry/MORPH_FEATURES_KIWI_v001.parquet",
        sha256="0fe5bd74e3993a7141c5c33ea78e71b2c66e3ecd296544bde2615acb43e50f7d",
        row_count=CANONICAL_COHORT_N, column_count=19, id_column="morph_measurement_id",
        gate="G4", manifest="outputs/manifests/MORPH_FEATURES_KIWI_MANIFEST_v001.json",
    ),
    "TOKEN_O200K_BASE_v001": CanonicalArtifact(
        name="TOKEN_O200K_BASE_v001",
        relative_path="data/registry/TOKEN_O200K_BASE_v001.parquet",
        # B §2.1: 물리 28열 = manifest 28열. 92dc07a 커밋 본문의 "29 columns"는 prose 오기다.
        sha256="1c30e3276222dd94885ae4f79fc6ab5c45e4e26226de0afd91fc6b1f7d2c16e7",
        row_count=CANONICAL_COHORT_N, column_count=28, id_column="measurement_id",
        gate="G3", manifest="outputs/manifests/TOKEN_O200K_BASE_MANIFEST_v001.json",
    ),
}

# 과거 산출물. 재현 기록으로 보존하되 current evidence로 소비하지 않는다 (SSOT §24).
HISTORICAL_ARTIFACTS: dict[str, dict[str, str]] = {
    "REP_FEATURES_v001": {
        "relative_path": "data/registry/REP_FEATURES_v001.parquet",
        "sha256": "335c20deacb355dc1ca147547ae18e1a5ab1508fe5272508b62ee04ddf819e45",
        "status": "HISTORICAL_SUPERSEDED_BY_REP_FEATURES_v002",
        "reason": "SSOT §12.2 lexical length 변수군(ko_eojeol_count/en_word_count) 부재",
        "superseded_by": "REP_FEATURES_v002",
    },
    "MORPH_FEATURES_PILOT_v001": {
        "relative_path": ".runtime/nb04-pilot/MORPH_FEATURES_PILOT_v001.parquet",
        "sha256": "41a28f4444e1b346dd3948c106fe1ef34978e6eabcb1216be5a56ed0b833ac31",
        "status": "SUPERSEDED_BY_CONFORMANCE_DEFECT",
        "reason": "M1 codepoint 분모 / M2 exact-match 접사 매핑 하에서 생성됨. G4 증거로 인용 불가",
        "superseded_by": "MORPH_FEATURES_KIWI_v001",
    },
}


class CanonicalArtifactIdentityMismatch(RuntimeError):
    """canonical artifact의 신원이 pin된 값과 다르다. fallback 없이 즉시 실패한다."""


def _connect(memory_limit: str = "4GB", threads: int = 8) -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    con.execute(f"SET memory_limit='{memory_limit}'")
    con.execute(f"SET threads={threads}")
    con.execute("SET preserve_insertion_order=false")
    return con


def pair_set_md5(path: Path, con: duckdb.DuckDBPyConnection | None = None) -> str:
    """정렬된 pair_id 집합의 안정 해시 (B §3와 동일한 정의)."""
    owned = con is None
    con = con or _connect()
    try:
        return con.execute(
            f"SELECT md5(string_agg(pair_id, '' ORDER BY pair_id)) "
            f"FROM read_parquet('{path.as_posix()}')"
        ).fetchone()[0]
    finally:
        if owned:
            con.close()


def assert_canonical_artifact(
    name: str, *, verify_pair_set: bool = False, con: duckdb.DuckDBPyConnection | None = None
) -> dict[str, Any]:
    """
    /**
     * @purpose canonical artifact의 신원을 fail-closed로 검증하고 확인된 사실을 돌려준다.
     * @spec_ref SSOT §30.2 lineage; B G2/G3/G4 adjudication (441d580)
     * @param name CANONICAL_ARTIFACTS의 키
     * @param verify_pair_set True면 정렬 pair-set 해시까지 대조한다 (전체 스캔)
     * @return path/sha256/row_count/column_count/pair_set_md5 등 확인된 신원
     * @raises CanonicalArtifactIdentityMismatch 경로·해시·행수·열수·pair-set 중 하나라도 불일치
     * @validation pilot/synthetic/이전 버전으로의 암묵적 대체가 불가능하다.
     * @artifact 없음 (검증 전용)
     */
    """
    if name not in CANONICAL_ARTIFACTS:
        raise CanonicalArtifactIdentityMismatch(f"알 수 없는 canonical artifact: {name}")
    spec = CANONICAL_ARTIFACTS[name]

    if not spec.path.exists():
        raise CanonicalArtifactIdentityMismatch(
            f"CANONICAL_ARTIFACT_IDENTITY_MISMATCH: {name} 이 없다 ({spec.relative_path}). "
            "pilot/이전 버전으로 대체하지 않는다."
        )

    actual_sha = sha256_file(spec.path)
    if actual_sha != spec.sha256:
        raise CanonicalArtifactIdentityMismatch(
            f"CANONICAL_ARTIFACT_IDENTITY_MISMATCH: {name} SHA-256 불일치\n"
            f"  expected {spec.sha256}\n  actual   {actual_sha}"
        )

    owned = con is None
    con = con or _connect()
    try:
        columns = con.execute(
            f"DESCRIBE SELECT * FROM read_parquet('{spec.path.as_posix()}')").fetchall()
        rows, distinct_ids = con.execute(
            f"SELECT count(*), count(DISTINCT {spec.id_column}) "
            f"FROM read_parquet('{spec.path.as_posix()}')").fetchone()

        if len(columns) != spec.column_count:
            raise CanonicalArtifactIdentityMismatch(
                f"CANONICAL_ARTIFACT_IDENTITY_MISMATCH: {name} column count "
                f"expected {spec.column_count}, actual {len(columns)}")
        if rows != spec.row_count:
            raise CanonicalArtifactIdentityMismatch(
                f"CANONICAL_ARTIFACT_IDENTITY_MISMATCH: {name} row count "
                f"expected {spec.row_count:,}, actual {rows:,}")
        if distinct_ids != spec.row_count:
            raise CanonicalArtifactIdentityMismatch(
                f"CANONICAL_ARTIFACT_IDENTITY_MISMATCH: {name} distinct {spec.id_column} "
                f"expected {spec.row_count:,}, actual {distinct_ids:,}")

        confirmed: dict[str, Any] = {
            "name": name, "path": spec.relative_path, "sha256": actual_sha,
            "row_count": rows, "distinct_id": distinct_ids, "column_count": len(columns),
            "id_column": spec.id_column, "gate": spec.gate, "manifest": spec.manifest,
            "identity": "CANONICAL_ARTIFACT_IDENTITY_VERIFIED",
        }
        if verify_pair_set:
            actual_pair_set = pair_set_md5(spec.path, con)
            if actual_pair_set != CANONICAL_PAIR_SET_MD5:
                raise CanonicalArtifactIdentityMismatch(
                    f"CANONICAL_ARTIFACT_IDENTITY_MISMATCH: {name} pair-set hash "
                    f"expected {CANONICAL_PAIR_SET_MD5}, actual {actual_pair_set}")
            confirmed["pair_set_md5"] = actual_pair_set
        return confirmed
    finally:
        if owned:
            con.close()


def describe_historical(name: str) -> dict[str, str]:
    """과거 artifact를 current evidence와 섞이지 않게 명시적으로 기술한다 (SSOT §24)."""
    if name not in HISTORICAL_ARTIFACTS:
        raise KeyError(f"알 수 없는 historical artifact: {name}")
    record = dict(HISTORICAL_ARTIFACTS[name])
    path = PROJECT_ROOT / record["relative_path"]
    record["present_locally"] = str(path.exists())
    record["NOT_CURRENT_EVIDENCE"] = "true"
    return record


__all__ = [
    "ADJUDICATION_COMMIT",
    "ADJUDICATION_DOC",
    "CANONICAL_ARTIFACTS",
    "CANONICAL_COHORT_N",
    "CANONICAL_PAIR_SET_MD5",
    "CanonicalArtifact",
    "CanonicalArtifactIdentityMismatch",
    "HISTORICAL_ARTIFACTS",
    "assert_canonical_artifact",
    "describe_historical",
    "pair_set_md5",
]
