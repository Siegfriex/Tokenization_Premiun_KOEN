#!/usr/bin/env python3
"""Builds G1_INGEST_EXPECTATIONS_v001 (json+csv) from the already-ported
PRE-G1 recon evidence (aihub_raw_profile, aihub_duplicate_overlap,
PAIR_DUPLICATE_RECON_v001).

Scope discipline:
  - This is a reconnaissance-derived EXPECTATIONS contract for Codex's
    canonical G1 ingest implementation. It is NOT a G1 PASS claim, NOT a
    QC/exclusion decision, NOT a source-tier ruling, and performs no
    normalization/tokenization/morphology.
  - Every number below is extracted programmatically from the three
    already-committed evidence manifests, not hand-transcribed, so this
    script is the audit trail for how each expected value was derived.
  - Reads only outputs/manifests/data_recon/** artifacts already in this
    repo; does not touch data/raw/** and does not re-run any raw file scan.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
MANIFEST_DIR = HERE.parent.parent / "manifests" / "data_recon"

RAW_PROFILE = json.loads((MANIFEST_DIR / "aihub_raw_profile_20260816T132650+0900.json").read_text(encoding="utf-8"))
DUP_OVERLAP = json.loads((MANIFEST_DIR / "aihub_duplicate_overlap_20260816T132650+0900.json").read_text(encoding="utf-8"))
PAIR_RECON = json.loads((MANIFEST_DIR / "PAIR_DUPLICATE_RECON_v001_20260816T143558+0900.json").read_text(encoding="utf-8"))

DATASET_025 = "025.일상생활 및 구어체 한-영 번역 병렬 말뭉치 데이터"
DATASET_026 = "026.기술과학 분야 한-영 번역 병렬 말뭉치 데이터"
DATASET_LEGACY = "한국어-영어 번역(병렬) 말뭉치"


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def dataset_short(dataset_id: str) -> str:
    if dataset_id == DATASET_025:
        return "025"
    if dataset_id == DATASET_026:
        return "026"
    return "LEGACY"


def classify_direction(relative_path: str) -> str:
    if "영한" in relative_path:
        return "EN_TO_KO"
    if "한영" in relative_path:
        return "KO_TO_EN"
    return "UNKNOWN"


def classify_split(relative_path: str) -> str:
    if "/1.Training/" in f"/{relative_path}":
        return "TRAIN"
    if "/2.Validation/" in f"/{relative_path}":
        return "VALIDATION"
    return "UNKNOWN"


def json_missing_counts(schema: dict[str, Any]) -> dict[str, Any]:
    fields = ["ko", "en", "sn", "ner"]
    return {f: schema[f] for f in fields if f in schema}


def xlsx_missing_counts(sheet_schema: dict[str, Any]) -> dict[str, Any]:
    interesting = ["원문", "번역문", "ID", "SID", "URL", "자동분류1", "자동분류2", "자동분류3", "날짜", "지자체", "키워드"]
    return {f: sheet_schema[f] for f in interesting if f in sheet_schema}


def main() -> None:
    files_by_path = {e["relative_path"]: e for e in RAW_PROFILE["files"]}
    sha_to_canonical_path: dict[str, str] = {}
    allowlist_entries: list[dict[str, Any]] = []
    physical_allowlist: list[dict[str, Any]] = []
    logical_record_counts: dict[str, int] = {"025": 0, "026": 0, "LEGACY": 0}

    # First pass: register canonical (non-alias, non-archive) files.
    for rel, entry in files_by_path.items():
        if entry["format"] not in ("JSON", "XLSX"):
            continue
        if "byte_identical_to" in entry:
            continue
        sha_to_canonical_path[entry["sha256"]] = rel

    for rel, entry in sorted(files_by_path.items()):
        ds = dataset_short(entry["dataset_id"])
        direction = classify_direction(rel)
        split = classify_split(rel)
        base_row = {
            "relative_path": rel,
            "sha256": entry["sha256"],
            "format": entry["format"],
            "logical_corpus": ds,
            "direction": direction,
            "split": split,
        }

        if entry["format"] == "ZIP":
            members = entry.get("archive_inventory", {}).get("members", [])
            member_relationship = []
            for member in members:
                canonical = sha_to_canonical_path.get(member["sha256"], "UNRESOLVED")
                member_relationship.append({
                    "member_path": member["member_path"],
                    "member_sha256": member["sha256"],
                    "byte_identical_canonical_file": canonical,
                })
            physical_allowlist.append({
                **base_row,
                "canonical_ingest_role": "ARCHIVE_CONTAINER_DO_NOT_EXTRACT",
                "alias_status": "ARCHIVE_CONTAINER_ALIAS",
                "alias_of": None,
                "record_count": None,
                "archive_member_relationship": member_relationship,
            })
            continue

        if "byte_identical_to" in entry:
            physical_allowlist.append({
                **base_row,
                "canonical_ingest_role": "DUPLICATE_PHYSICAL_COPY_SKIP",
                "alias_status": "BYTE_IDENTICAL_ALIAS",
                "alias_of": entry["byte_identical_to"],
                "record_count": None,
                "archive_member_relationship": None,
            })
            continue

        # Canonical file.
        profile = entry["profile"]
        if entry["format"] == "JSON":
            record_count = profile["record_count"]
            structural_missing = json_missing_counts(profile["schema"])
        else:
            record_count = sum(sheet["record_count"] for sheet in profile["sheets"])
            structural_missing = {
                sheet["sheet_name"]: xlsx_missing_counts(sheet["schema"])
                for sheet in profile["sheets"]
            }

        role = f"{ds}_{direction}_{split}" if ds != "LEGACY" else f"LEGACY_{Path(rel).stem}"
        logical_record_counts[ds] += record_count

        row = {
            **base_row,
            "canonical_ingest_role": role,
            "alias_status": "CANONICAL",
            "alias_of": None,
            "record_count": record_count,
            "archive_member_relationship": None,
            "structural_missing_counts": structural_missing,
        }
        physical_allowlist.append(row)
        allowlist_entries.append({
            "relative_path": rel,
            "sha256": entry["sha256"],
            "format": entry["format"],
            "logical_corpus": ds,
            "canonical_ingest_role": role,
            "record_count": record_count,
        })

    expected_logical_record_counts = {**logical_record_counts, "total": sum(logical_record_counts.values())}

    source_record_id_rules = {
        "025": {
            "field": "sn",
            "scope": "dataset-wide across all 4 canonical sub-files (EN_TO_KO x TRAIN/VALIDATION, KO_TO_EN x TRAIN/VALIDATION)",
            "collision_status": "VERIFIED 0 within-file and 0 cross-sub-file collisions",
            "evidence": "PAIR_DUPLICATE_RECON_v001 section_3_sn_cross_subfile_identity.025",
        },
        "026": {
            "field": "sn",
            "scope": "dataset-wide across both canonical sub-files (KO_TO_EN x TRAIN/VALIDATION)",
            "collision_status": "VERIFIED 0 within-file and 0 cross-sub-file collisions",
            "evidence": "PAIR_DUPLICATE_RECON_v001 section_3_sn_cross_subfile_identity.026",
        },
        "LEGACY": {
            "field": None,
            "rule": "composite key: workbook/file namespace + sheet name + deterministic 1-based physical data-row locator (post-header). Bare ID/SID MUST NOT be used as a global key.",
            "reason": (
                "Legacy ID/SID values are file-scoped only; the raw recon baseline "
                "(AIHUB_RAW_RECON_20260816T132650+0900.md, section E) found 127,824 "
                "duplicate-key candidates when ID/SID values are pooled across "
                "workbooks without namespacing, and the 대화체 workbook has no "
                "single-column unique ID at all (Set Nr. + 발화자 has 8 duplicate "
                "composite rows out of 100,000)."
            ),
            "raw_id_preservation": "original ID/SID/SID-equivalent column MUST be retained as raw auxiliary metadata, never used as the primary key",
        },
    }

    expected_pairability = {
        "025": "DIRECT: ko and en coexist in each JSON data[] object; sn is nonempty and dataset-wide unique in this snapshot",
        "026": "DIRECT: ko and en coexist in each JSON data[] object; sn is nonempty and dataset-wide unique in this snapshot",
        "LEGACY": "DIRECT: 원문 and 번역문 coexist in each worksheet data row; no dataset-wide-safe bare ID -- use the composite key above",
    }

    dir_matrix = {c["a"] + "|" + c["b"]: c for c in PAIR_RECON["section_2_matrices"]["direction_x_direction"]["cells"]}
    split_matrix = {c["a"] + "|" + c["b"]: c for c in PAIR_RECON["section_2_matrices"]["split_x_split"]["cells"]}
    file_matrix_cells = PAIR_RECON["section_2_matrices"]["file_x_file"]["cells"]
    legacy_anomaly = next(
        c for c in file_matrix_cells
        if {"3_문어체_뉴스(2).xlsx", "4_문어체_한국문화.xlsx"} <= {c["a"].rsplit("|", 1)[-1], c["b"].rsplit("|", 1)[-1]}
        and c["a"] != c["b"]
    )

    duplicate_baseline_oracle = {
        "identity_method": PAIR_RECON["identity_method"],
        "025": {
            "duplicate_pair_rows_after_first_occurrence": PAIR_RECON["section_1_sha256_reverification_vs_blake2b64_baseline"]["sha256_recheck_counts"]["025"]["duplicate_pair_rows_after_first_occurrence"],
            "distinct_duplicate_pair_groups": PAIR_RECON["section_1_sha256_reverification_vs_blake2b64_baseline"]["sha256_recheck_counts"]["025"]["distinct_pair_digests_with_duplicates"],
        },
        "026": {
            "duplicate_pair_rows_after_first_occurrence": PAIR_RECON["section_1_sha256_reverification_vs_blake2b64_baseline"]["sha256_recheck_counts"]["026"]["duplicate_pair_rows_after_first_occurrence"],
            "distinct_duplicate_pair_groups": PAIR_RECON["section_1_sha256_reverification_vs_blake2b64_baseline"]["sha256_recheck_counts"]["026"]["distinct_pair_digests_with_duplicates"],
        },
        "cross_direction_distinct_shared_pair_digests": dir_matrix["EN_TO_KO|KO_TO_EN"]["shared_distinct_pair_digest_count"],
        "train_valid_distinct_shared_pair_digests_project_wide": split_matrix["TRAIN|VALIDATION"]["shared_distinct_pair_digest_count"],
        "cross_corpus_raw_exact_pair_overlap": PAIR_RECON["section_4_cross_corpus_raw_exact_pair_overlap"],
        "legacy_news2_culture_anomaly": {
            "file_a": legacy_anomaly["a"],
            "file_b": legacy_anomaly["b"],
            "shared_distinct_pair_digest_count": legacy_anomaly["shared_distinct_pair_digest_count"],
        },
        "sn_dataset_wide_collision": {
            ds: {
                "within_file": PAIR_RECON["section_3_sn_cross_subfile_identity"][ds]["within_file_duplicate_sn_rows"],
                "cross_subfile": PAIR_RECON["section_3_sn_cross_subfile_identity"][ds]["cross_subfile_duplicate_sn_rows"],
            }
            for ds in ("025", "026")
        },
        "evidence_source": "PAIR_DUPLICATE_RECON_v001_20260816T143558+0900.json (this repo, same commit lineage)",
        "usage_note": "These are independent expected values for Codex to validate its own canonical registry/dedup implementation against -- not a re-derivation target to match by construction.",
    }

    double_ingest_prevention = {
        "rule": (
            "The canonical ingester MUST read exactly the relative_path values in "
            "ingest_allowlist below and MUST NOT recursively rglob data/raw/aigub and "
            "load every JSON/XLSX file it finds. Any physical_file_allowlist entry "
            "with alias_status != 'CANONICAL' MUST be skipped entirely: this "
            "includes not extracting the VS1.zip archive (its 2 members are "
            "byte-identical to already-canonical VL1 JSON files) and not re-reading "
            "원천데이터(TS/VS) label copies that are byte-identical to their "
            "라벨링데이터(TL/VL) counterparts."
        ),
        "verification": (
            "sum(record_count for entries where logical_corpus == X and alias_status "
            "== 'CANONICAL') MUST equal expected_logical_record_counts[X]. A naive "
            "recursive ingest without this allowlist would double-count 025 to "
            f"{2 * expected_logical_record_counts['025']:,} and 026 to "
            f"{2 * expected_logical_record_counts['026']:,} via label+source copies, "
            "and would further inflate 025 validation counts by re-reading VS1.zip "
            "members already present as VL1 JSON."
        ),
        "ingest_allowlist": allowlist_entries,
    }

    manifest = {
        "manifest_id": "G1_INGEST_EXPECTATIONS_v001",
        "generated_at": now_iso(),
        "scope_note": (
            "Reconnaissance-derived G1 canonical ingest EXPECTATIONS for Codex's "
            "ingest implementation. Does NOT assert G1 PASS. Does NOT perform or "
            "authorize normalization, QC exclusion, source-tier revision, "
            "tokenization, or morphology. Does NOT define the canonical registry "
            "itself -- that implementation remains Codex-owned."
        ),
        "raw_root": RAW_PROFILE["raw_root"],
        "raw_manifest_sha": RAW_PROFILE["raw_file_manifest_sha"],
        "source_evidence_manifests": [
            "aihub_raw_profile_20260816T132650+0900.json",
            "aihub_duplicate_overlap_20260816T132650+0900.json",
            "PAIR_DUPLICATE_RECON_v001_20260816T143558+0900.json",
        ],
        "physical_file_allowlist": physical_allowlist,
        "expected_logical_record_counts": expected_logical_record_counts,
        "source_record_id_rules": source_record_id_rules,
        "expected_pairability": expected_pairability,
        "duplicate_baseline_oracle": duplicate_baseline_oracle,
        "double_ingest_prevention_contract": double_ingest_prevention,
        "non_claims": [
            "No normalization was performed or authorized.",
            "No QC exclusion decision is made or implied.",
            "No source-tier (Tier A/B/C, per SSOT SS9.3) revision is made or implied.",
            "No tokenization was performed.",
            "No morphology analysis was performed.",
            "No G1 PASS is claimed. G1 PASS conditions (unique pair IDs, null/duplicate checks, LID/QC pass rate, source/license metadata completeness) remain to be evaluated by the canonical ingest + QC implementation.",
        ],
    }

    (MANIFEST_DIR / "G1_INGEST_EXPECTATIONS_v001.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    csv_lines = [
        "relative_path,sha256,format,logical_corpus,direction,split,canonical_ingest_role,alias_status,alias_of,record_count"
    ]
    for row in physical_allowlist:
        csv_lines.append(",".join([
            f'"{row["relative_path"]}"',
            row["sha256"],
            row["format"],
            row["logical_corpus"],
            row["direction"],
            row["split"],
            row["canonical_ingest_role"],
            row["alias_status"],
            f'"{row["alias_of"]}"' if row["alias_of"] else "",
            str(row["record_count"]) if row["record_count"] is not None else "",
        ]))
    (MANIFEST_DIR / "G1_INGEST_EXPECTATIONS_v001.csv").write_text("\n".join(csv_lines) + "\n", encoding="utf-8")

    print(json.dumps(expected_logical_record_counts, ensure_ascii=False))


if __name__ == "__main__":
    main()
