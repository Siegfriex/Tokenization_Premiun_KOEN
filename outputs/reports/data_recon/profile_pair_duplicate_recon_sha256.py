#!/usr/bin/env python3
"""PRE-G1 duplicate/identity reconnaissance re-audit using a collision-resistant
(SHA-256) candidate pair identity, in place of the baseline profiler's
BLAKE2b-64 triage hash.

Scope discipline (read this before editing):
  - Reconnaissance evidence only. Does NOT assert G1 PASS, QC acceptance, or
    any row/pair exclusion decision. Does NOT create a canonical duplicate
    registry. The final dedup implementation contract is Codex-owned.
  - No raw ko/en/sn text is persisted anywhere in this script's output --
    only counts, SHA-256 digests, and file/direction/split labels.
  - Does not modify, re-order, or extend the existing raw-profile baseline
    (profile_aihub_raw.py / profile_aihub_duplicate_overlap.py and their
    already-committed manifests). This script only *reads* the baseline
    manifest to recover the canonical (byte-deduplicated) file list, then
    re-streams the raw files directly for its own SHA-256 pass.

Identity scheme (explicit, so it is auditable and reproducible):
  pair_digest = SHA256( u64be(len(ko_utf8)) || ko_utf8 || u64be(len(en_utf8)) || en_utf8 )
  sn_digest   = SHA256( u64be(len(sn_utf8)) || sn_utf8 )
  This is the same length-prefixed framing the baseline used for its
  BLAKE2b-64 candidate hash (see profile_aihub_raw.short_hash), upgraded to
  a 256-bit digest so identity claims are not gated on a 64-bit collision
  budget. It remains a *candidate* identity: it says two rows are
  byte-identical in raw KO+EN content, not that they are semantically or
  canonically the same registry entry.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from profile_aihub_duplicate_overlap import json_rows, xlsx_rows


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def pair_digest(ko: str, en: str) -> bytes:
    digest = hashlib.sha256()
    ko_b = ko.encode("utf-8", errors="strict")
    en_b = en.encode("utf-8", errors="strict")
    digest.update(len(ko_b).to_bytes(8, "big"))
    digest.update(ko_b)
    digest.update(len(en_b).to_bytes(8, "big"))
    digest.update(en_b)
    return digest.digest()


def sn_digest(sn: str) -> bytes:
    digest = hashlib.sha256()
    sn_b = sn.encode("utf-8", errors="strict")
    digest.update(len(sn_b).to_bytes(8, "big"))
    digest.update(sn_b)
    return digest.digest()


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


def dataset_short(dataset_id: str) -> str:
    if dataset_id.startswith("025"):
        return "025"
    if dataset_id.startswith("026"):
        return "026"
    return "LEGACY"


class CategoryTracker:
    """Tracks distinct-digest set + row-level duplicate-after-first stats for one category value."""

    __slots__ = ("rows", "seen", "duplicate_rows_after_first")

    def __init__(self) -> None:
        self.rows = 0
        self.seen: set[bytes] = set()
        self.duplicate_rows_after_first = 0

    def add(self, digest: bytes) -> None:
        self.rows += 1
        if digest in self.seen:
            self.duplicate_rows_after_first += 1
        else:
            self.seen.add(digest)

    def summary(self) -> dict[str, int]:
        return {
            "rows": self.rows,
            "distinct_pair_digests": len(self.seen),
            "duplicate_rows_after_first_occurrence": self.duplicate_rows_after_first,
        }


def pairwise_matrix(trackers: dict[str, CategoryTracker]) -> dict[str, Any]:
    keys = sorted(trackers)
    cells = []
    for a, b in itertools.combinations_with_replacement(keys, 2):
        if a == b:
            cells.append({
                "a": a, "b": b,
                **trackers[a].summary(),
                "shared_distinct_pair_digest_count": None,
                "note": "diagonal cell: within-category stats, not an overlap count",
            })
        else:
            shared = len(trackers[a].seen & trackers[b].seen)
            cells.append({
                "a": a, "b": b,
                "shared_distinct_pair_digest_count": shared,
            })
    return {"categories": keys, "cells": cells}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("raw_root", type=Path)
    parser.add_argument("baseline_profile_manifest", type=Path)
    parser.add_argument("baseline_duplicate_overlap_manifest", type=Path)
    parser.add_argument("output_json", type=Path)
    parser.add_argument("output_csv", type=Path)
    args = parser.parse_args()

    baseline_profile = json.loads(args.baseline_profile_manifest.read_text(encoding="utf-8"))
    baseline_overlap = json.loads(args.baseline_duplicate_overlap_manifest.read_text(encoding="utf-8"))

    canonical_entries = [
        entry for entry in baseline_profile["files"]
        if entry["stability_state"] == "STABLE_FILE"
        and entry["format"] in ("JSON", "XLSX")
        and "byte_identical_to" not in entry
    ]

    file_trackers: dict[str, CategoryTracker] = {}
    direction_trackers: dict[str, CategoryTracker] = defaultdict(CategoryTracker)
    split_trackers: dict[str, CategoryTracker] = defaultdict(CategoryTracker)
    dataset_trackers: dict[str, CategoryTracker] = defaultdict(CategoryTracker)

    file_meta: dict[str, dict[str, Any]] = {}
    sn_first_seen_file: dict[str, dict[bytes, str]] = {"025": {}, "026": {}}
    sn_cross_subfile_collisions: dict[str, int] = {"025": 0, "026": 0}
    sn_within_file_collisions: dict[str, int] = {"025": 0, "026": 0}
    sn_total_rows: dict[str, int] = {"025": 0, "026": 0}
    sn_collision_file_pairs: dict[str, Counter] = {"025": Counter(), "026": Counter()}

    # Dataset-level ordered rescan of 025/026 for direct comparison against the
    # baseline BLAKE2b-64 candidate counts (same scan order: training files
    # before validation files, path-sorted within each).
    rescan_order: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for entry in canonical_entries:
        relative = entry["relative_path"]
        ds = dataset_short(entry["dataset_id"])
        direction = classify_direction(relative)
        split = classify_split(relative)
        file_id = f"{ds}|{direction}|{split}|{Path(relative).name}"
        file_meta[file_id] = {
            "dataset": ds, "direction": direction, "split": split,
            "relative_path": relative, "format": entry["format"],
        }
        file_trackers[file_id] = CategoryTracker()
        rescan_order[ds].append(entry)

    rescan_order["025"].sort(key=lambda e: ("Validation" in e["relative_path"], e["relative_path"].encode("utf-8")))
    rescan_order["026"].sort(key=lambda e: ("Validation" in e["relative_path"], e["relative_path"].encode("utf-8")))

    reverify: dict[str, Any] = {}
    for ds in ("025", "026"):
        seen_pairs: set[bytes] = set()
        seen_keys: set[bytes] = set()
        dup_pair_rows = 0
        dup_key_rows = 0
        distinct_dup_pair_digests: set[bytes] = set()
        for entry in rescan_order[ds]:
            path = args.raw_root / entry["relative_path"]
            for ko, en, sn in json_rows(path):
                pd = pair_digest(ko, en)
                if pd in seen_pairs:
                    dup_pair_rows += 1
                    distinct_dup_pair_digests.add(pd)
                else:
                    seen_pairs.add(pd)
                if sn is not None:
                    kd = sn_digest(sn)
                    if kd in seen_keys:
                        dup_key_rows += 1
                    else:
                        seen_keys.add(kd)
        reverify[ds] = {
            "duplicate_pair_rows_after_first_occurrence": dup_pair_rows,
            "distinct_pair_digests_with_duplicates": len(distinct_dup_pair_digests),
            "duplicate_nonempty_sn_rows_after_first_occurrence": dup_key_rows,
        }

    # Main single pass: per-file, per-direction, per-split, per-dataset digest sets,
    # plus sn cross-sub-file identity check for 025/026.
    for file_id, meta in file_meta.items():
        path = args.raw_root / meta["relative_path"]
        ds = meta["dataset"]
        is_json = meta["format"] == "JSON"
        iterator: Iterator[tuple[str, str, str | None]] = json_rows(path) if is_json else xlsx_rows(path)
        ftrack = file_trackers[file_id]
        dtrack = direction_trackers[meta["direction"]]
        strack = split_trackers[meta["split"]]
        cotrack = dataset_trackers[ds]
        for ko, en, sn in iterator:
            pd = pair_digest(ko, en)
            ftrack.add(pd)
            dtrack.add(pd)
            strack.add(pd)
            cotrack.add(pd)
            if is_json and ds in ("025", "026") and sn is not None:
                sn_total_rows[ds] += 1
                sd = sn_digest(sn)
                prior_file = sn_first_seen_file[ds].get(sd)
                if prior_file is None:
                    sn_first_seen_file[ds][sd] = file_id
                elif prior_file == file_id:
                    sn_within_file_collisions[ds] += 1
                else:
                    sn_cross_subfile_collisions[ds] += 1
                    pair_key = tuple(sorted((prior_file, file_id)))
                    sn_collision_file_pairs[ds][pair_key] += 1

    direction_matrix = pairwise_matrix(direction_trackers)
    split_matrix = pairwise_matrix(split_trackers)
    file_matrix = pairwise_matrix(file_trackers)

    dataset_pair_sets = {ds: tracker.seen for ds, tracker in dataset_trackers.items()}
    cross_corpus = {
        "025_vs_026": len(dataset_pair_sets.get("025", set()) & dataset_pair_sets.get("026", set())),
        "025_vs_legacy": len(dataset_pair_sets.get("025", set()) & dataset_pair_sets.get("LEGACY", set())),
        "026_vs_legacy": len(dataset_pair_sets.get("026", set()) & dataset_pair_sets.get("LEGACY", set())),
        "set_sizes": {ds: len(s) for ds, s in dataset_pair_sets.items()},
    }

    manifest = {
        "manifest_id": "PAIR_DUPLICATE_RECON_v001",
        "generated_at": now_iso(),
        "scope_note": (
            "PRE-G1 duplicate/identity reconnaissance evidence only. Does NOT assert "
            "G1 PASS, QC acceptance, or any row/pair exclusion decision. Does NOT "
            "define a canonical duplicate registry -- final dedup implementation "
            "contract is Codex-owned (see project ownership boundary memory)."
        ),
        "source_raw_root": str(args.raw_root),
        "source_raw_file_manifest_sha": baseline_profile["raw_file_manifest_sha"],
        "source_baseline_manifests": [
            args.baseline_profile_manifest.name,
            args.baseline_duplicate_overlap_manifest.name,
        ],
        "identity_method": {
            "pair_identity": (
                "SHA-256 over unambiguous length-prefixed UTF-8 byte serialization: "
                "u64be(len(ko_utf8)) || ko_utf8 || u64be(len(en_utf8)) || en_utf8"
            ),
            "sn_identity": "SHA-256 over u64be(len(sn_utf8)) || sn_utf8",
            "collision_resistance_note": (
                "Replaces the baseline profiler's BLAKE2b-64 (64-bit) candidate hash "
                "with a 256-bit digest for this re-audit. This reduces hash-collision "
                "risk to practically negligible levels but does not resolve identity- "
                "definition questions (normalization, whitespace, encoding variants) -- "
                "counts below remain a candidate identity, not a canonical duplicate "
                "determination."
            ),
            "raw_text_export": "NONE -- only digests, counts, and file/direction/split labels are persisted.",
        },
        "classification_rule": {
            "direction": "relative_path contains '영한' -> EN_TO_KO; '한영' -> KO_TO_EN; else UNKNOWN (Legacy XLSX has no direction field)",
            "split": "relative_path contains '/1.Training/' -> TRAIN; '/2.Validation/' -> VALIDATION; else UNKNOWN (Legacy XLSX has no split field)",
            "logical_file_dedup": "byte-identical physical copies (same whole-file SHA-256, per baseline raw profile) collapsed to one canonical logical file before this pass",
        },
        "canonical_logical_files": file_meta,
        "section_1_sha256_reverification_vs_blake2b64_baseline": {
            "baseline_blake2b64_candidate_counts": {
                "025": {
                    "duplicate_pair_rows_after_first_occurrence": baseline_overlap["datasets"]["025.일상생활 및 구어체 한-영 번역 병렬 말뭉치 데이터"]["duplicate_pair_rows_after_first_occurrence"],
                    "distinct_pair_hashes_with_duplicates": baseline_overlap["datasets"]["025.일상생활 및 구어체 한-영 번역 병렬 말뭉치 데이터"]["distinct_pair_hashes_with_duplicates"],
                },
                "026": {
                    "duplicate_pair_rows_after_first_occurrence": baseline_overlap["datasets"]["026.기술과학 분야 한-영 번역 병렬 말뭉치 데이터"]["duplicate_pair_rows_after_first_occurrence"],
                    "distinct_pair_hashes_with_duplicates": baseline_overlap["datasets"]["026.기술과학 분야 한-영 번역 병렬 말뭉치 데이터"]["distinct_pair_hashes_with_duplicates"],
                },
            },
            "sha256_recheck_counts": reverify,
            "counts_match": {
                ds: (
                    reverify[ds]["duplicate_pair_rows_after_first_occurrence"]
                    == baseline_overlap["datasets"][key]["duplicate_pair_rows_after_first_occurrence"]
                    and reverify[ds]["distinct_pair_digests_with_duplicates"]
                    == baseline_overlap["datasets"][key]["distinct_pair_hashes_with_duplicates"]
                )
                for ds, key in (
                    ("025", "025.일상생활 및 구어체 한-영 번역 병렬 말뭉치 데이터"),
                    ("026", "026.기술과학 분야 한-영 번역 병렬 말뭉치 데이터"),
                )
            },
        },
        "section_2_matrices": {
            "direction_x_direction": direction_matrix,
            "split_x_split": split_matrix,
            "file_x_file": file_matrix,
        },
        "section_3_sn_cross_subfile_identity": {
            ds: {
                "total_nonempty_sn_rows": sn_total_rows[ds],
                "distinct_sn_digests": len(sn_first_seen_file[ds]),
                "within_file_duplicate_sn_rows": sn_within_file_collisions[ds],
                "cross_subfile_duplicate_sn_rows": sn_cross_subfile_collisions[ds],
                "cross_subfile_colliding_file_pairs": [
                    {"file_a": pair[0], "file_b": pair[1], "collision_count": count}
                    for pair, count in sn_collision_file_pairs[ds].most_common()
                ],
            }
            for ds in ("025", "026")
        },
        "section_4_cross_corpus_raw_exact_pair_overlap": cross_corpus,
        "explicit_non_claims": [
            "This manifest does NOT assert G1 PASS.",
            "This manifest does NOT assert any row/pair exclusion decision.",
            "This manifest does NOT define a canonical duplicate registry.",
            "Canonical dedup implementation contract remains Codex-owned.",
        ],
    }

    args.output_json.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    csv_lines = ["section,dim_a,dim_b,rows_a,distinct_a,dup_rows_a,shared_distinct_pair_digest_count"]
    for section_name, matrix in (
        ("direction_x_direction", direction_matrix),
        ("split_x_split", split_matrix),
        ("file_x_file", file_matrix),
    ):
        for cell in matrix["cells"]:
            if cell["a"] == cell["b"]:
                csv_lines.append(
                    f"{section_name},{cell['a']},{cell['b']},{cell['rows']},{cell['distinct_pair_digests']},"
                    f"{cell['duplicate_rows_after_first_occurrence']},"
                )
            else:
                csv_lines.append(
                    f"{section_name},{cell['a']},{cell['b']},,,,{cell['shared_distinct_pair_digest_count']}"
                )
    csv_lines.append("cross_corpus,025,026,,,,{}".format(cross_corpus["025_vs_026"]))
    csv_lines.append("cross_corpus,025,LEGACY,,,,{}".format(cross_corpus["025_vs_legacy"]))
    csv_lines.append("cross_corpus,026,LEGACY,,,,{}".format(cross_corpus["026_vs_legacy"]))
    args.output_csv.write_text("\n".join(csv_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
