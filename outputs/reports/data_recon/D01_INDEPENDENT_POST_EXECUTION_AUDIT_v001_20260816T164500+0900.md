# D-01 Independent Post-Execution Audit — v001

**Role:** Independent Data Integrity / Raw Reality Auditor (READ-ONLY)
**Canonical branch audited from:** `data/g1-recon` @ `617f6fdaf994f9496d97e15621a6921d49451015`
**Independent oracle:** `G1_INGEST_EXPECTATIONS_v001`
**Generated at:** 2026-08-16T16:51:39+0900

**This report does NOT assert G1 PASS.** It is a targeted, read-only re-verification of the Codex `impl/g1-codex` canonical `PAIR_REGISTRY_v001.parquet` / `SOURCE_REGISTRY_v001.parquet` against the independent ingest/duplicate oracle, plus the frozen Phase-1 field contract. No Codex artifact was modified or regenerated. No raw KO/EN text was exported; only counts, hashes, and aggregate metrics are persisted here.

---

## A. Artifact identities

| Artifact | Path | SHA-256 (independently recomputed) | Matches Codex manifest |
|---|---|---|---|
| Pair registry | `.agent_worktrees/codex-g1/data/registry/PAIR_REGISTRY_v001.parquet` | `eac9f4cc37d4a394d81d17c24b7910716c3bc511dbc15dd3929be1cb9393e2a4` | YES |
| Source registry | `.agent_worktrees/codex-g1/data/registry/SOURCE_REGISTRY_v001.parquet` | `4c359c072a8f27412b52db6fe334e25ca8e2a42b46c742ce1fadbf84e1b09a94` | YES |

Codex manifest referenced (read-only, for identity cross-check only): `outputs/manifests/PAIR_REGISTRY_MANIFEST_v001.json`, `code_commit=0b401d169b651a90efdab3fae8feef772982275f`, `created_at=2026-08-16T16:31:16.970290+09:00`.

Codex worktree HEAD at audit time: `impl/g1-codex` @ `66c8ef07958d74bb5040c952f12a82edc23ec860` (audit reads the persisted Parquet files, which are content-addressed by the SHA-256 above; worktree HEAD is recorded for provenance only).

Oracle referenced: `outputs/manifests/data_recon/G1_INGEST_EXPECTATIONS_v001.json` (`generated_at=2026-08-16T15:37:44+09:00`, this same `data/g1-recon` lineage).

## B. Resource settings

- Engine: DuckDB 1.5.5, invoked from the `impl/g1-codex` project `.venv` (dependency already vendored there; no packages installed for this audit).
- `PRAGMA memory_limit='4GB'`, `PRAGMA threads=4`, `SET preserve_insertion_order=false`.
- `temp_directory` pointed at the session scratchpad (outside any agent worktree) for any spill; no spill was actually required — max observed single-query wall time was 4.13s over the 5,652,925-row table.
- No full-table `pandas`/Arrow materialization was performed anywhere in this audit — every check is a bounded DuckDB aggregate (`COUNT`, `GROUP BY ... HAVING`, `DISTINCT`) against `read_parquet(...)`.
- No `NOT_RUN_RESOURCE_SAFETY` stops were needed — every checklist item completed within the 4GB bound.

## C. Independent checks (all bounded aggregate queries, re-derived from raw columns, not from Codex's self-reported manifest numbers)

| Check | Expected (oracle) | Observed (independent) | Result |
|---|---:|---:|---|
| Total rows | 5,652,925 | 5,652,925 | MATCH |
| 025 rows | 2,700,345 | 2,700,345 | MATCH |
| 026 rows | 1,350,162 | 1,350,162 | MATCH |
| Legacy rows | 1,602,418 | 1,602,418 | MATCH |
| `pair_id` null count | 0 | 0 | MATCH |
| `pair_id` distinct count | = total | 5,652,925 (= total) | MATCH |
| Source registry rows | 3 | 3 | MATCH |
| Canonical physical files | 16 | 16 (of 23 total; 7 excluded as `ARCHIVE_CONTAINER_ALIAS`/`BYTE_IDENTICAL_ALIAS`) | MATCH |
| 025 dup rows after first | 214,252 | 214,252 (raw-text GROUP BY) / 214,252 (`duplicate_group_id` cross-check) | MATCH |
| 025 dup distinct groups | 93,823 | 93,823 / 93,823 | MATCH |
| 026 dup rows after first | 44 | 44 / 44 | MATCH |
| 026 dup distinct groups | 44 | 44 / 44 | MATCH |
| 025 cross-direction (EN_TO_KO↔KO_TO_EN) distinct shared | 50,511 | 50,511 | MATCH |
| 025 vs 026 cross-corpus overlap | 0 | 0 | MATCH |
| 025 vs Legacy cross-corpus overlap | 35 | 35 | MATCH |
| 026 vs Legacy cross-corpus overlap | 1 | 1 | MATCH |
| Legacy News(2)↔Culture shared distinct | 2,469 | 2,469 | MATCH |
| 025 `sn` dataset-wide collisions | 0 | 0 (2,700,345 rows, 2,700,345 distinct `source_record_id`) | MATCH |
| 026 `sn` dataset-wide collisions | 0 | 0 (1,350,162 rows, 1,350,162 distinct `source_record_id`) | MATCH |

**Duplicate-identity method note:** every duplicate/overlap metric above was computed by `GROUP BY (ko_text_raw, en_text_raw)` directly on the persisted raw columns — this does **not** trust Codex's own `duplicate_group_id` SHA-256 hash. The 025/026 in-corpus duplicate metrics were then cross-checked a second way against the persisted `duplicate_group_id` column, and both methods agree exactly, which independently confirms Codex's hash implementation introduced no collisions or omissions relative to raw exact-string identity.

### Phase-1 frozen field contract

| Field | Frozen Phase-1 value | Observed | Result |
|---|---|---|---|
| `pair_quality_status` | constant `review` | only value present: `review` | MATCH |
| `pair_quality_score` | null for all rows | 0 non-null rows | MATCH |
| `normalization_status` | constant `NOT_GENERATED_PHASE1` | only value present | MATCH |
| `qc_stage_status` | constant `PENDING_PHASE2` | only value present | MATCH |
| `ko_text_nfc` / `en_text_nfc` / `ko_text_analysis` / `en_text_analysis` | null placeholders (Phase 2 not run) | 0 non-null rows for all four | MATCH |
| `representative_pair_id` | `= min(pair_id)` within `duplicate_group_id` | 0 violating rows | MATCH |
| `pair_version` | constant `v001` | only value present | MATCH |

## D. Codex-vs-Recon comparison

Codex's own `PAIR_REGISTRY_MANIFEST_v001.json` (`.validation.status = "PASS"`) reports the identical row counts, duplicate metrics, cross-corpus overlaps, and `pair_id` distinctness that this independent audit re-derived directly from the Parquet table via separate bounded queries (not by reading Codex's manifest numbers). No divergence was found between Codex's self-reported validation and this independent re-derivation on any of the checklist items above.

One item present in Codex's manifest but outside this audit's checklist: `LEGACY` internal duplicate metrics (`distinct_duplicate_pair_groups=2494`, `duplicate_pair_rows_after_first_occurrence=2494`). The oracle's frozen contract does not specify an expected Legacy-internal duplicate count (only the News(2)↔Culture cross-file anomaly, which matches), so this is reported as informational and not scored PASS/FAIL here.

## E. Discrepancies

**None.** Every checklist item in the task's audit scope matched the oracle exactly, with zero deviation.

## F. D-01 independent verdict

```
D-01 IMPLEMENTATION CONSISTENT WITH G1_INGEST_EXPECTATIONS_v001 ORACLE
ON ALL CHECKED ITEMS.
```

This is an **engineering-level D-01 consistency finding only**. It explicitly does **not** constitute a G1 PASS claim. Per the 2026-08-16 16:16 KST midpoint decision log, G1 PASS additionally requires an LID/QC pass-rate artifact (Phase 2 / `02_normalize_and_qc.ipynb`, SSOT §31) that has not yet been produced, plus source-tier/license/provenance closure that remains open. G1 PASS/OPEN adjudication remains the Vice Director's and Research Director's authority.

## G. Commit / push

Outputs of this audit (this report + its companion JSON manifest, both aggregate-only, no raw text) are committed to `data/g1-recon` from the `data-recon-g1` worktree and pushed to `origin/data/g1-recon`. See commit log for the exact SHA.

---

### Non-claims

1. No G1 PASS is claimed or implied.
2. LID/QC pass-rate (Phase 2 requirement) is not evaluated here.
3. Source-tier, license closure, and provenance-evidence completeness are not evaluated here.
4. No semantic/statistical review of pair content was performed.
5. Duplicate identity re-verified is raw exact-string identity only — a candidate identity, not a canonical duplicate/QC determination.
6. Codex artifacts were not modified, regenerated, or re-derived beyond read-only bounded aggregate queries.
