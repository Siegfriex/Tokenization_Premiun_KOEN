# P2 Minimal-QC Engineering Handoff v1

This implementation consumes the revised research precontract at
`research/p2-qc-claude@b9990afbf3fc0ed2a5e80fb4def1565e9ba3ebf4` without merging or rewriting the Claude-owned contract.

## Implemented boundary

- Normalization is NFC, edge-only U+FEFF stripping, then outer whitespace trimming. Internal whitespace, internal U+FEFF, and zero-width evidence remain observable.
- D-01 handoff validation reads the existing manifest and ingest oracle. It checks recorded PASS status, row count, pair-ID cardinality, canonical input inventory, and raw SHA linkage without rescanning the population.
- Batch/synthetic row validation checks `pair_id`, `raw_locator`, `canonical_ingest_role`, source path, and raw SHA linkage.
- Language-side smoke is a deterministic Unicode count assertion. It emits only `lang_side_anomaly_review_flag` and a reason; it has no confidence score and cannot reject a row.
- Manual semantic work is represented only by the nullable import interface: `manual_semantic_score`, `manual_language_side_status`, and `manual_audit_status`.
- D-01 `representative_pair_id` remains an immutable provenance pointer. The separate `analysis_representative_pair_id` prefers `primary_analysis_eligible=true`, then stable minimum `pair_id`.
- Runtime execution keeps the 8GB DuckDB default, mandatory spill directory, and ENG-OBS heartbeat architecture.

## Leakage boundary

`duplicate_group_id` is an exact identity of raw Korean and English text only. It is not a near-duplicate group, paraphrase cluster, or Phase-5 split-group implementation. No fuzzy matching or leakage clustering is implemented here.

## Excluded

- No LID package, LID model, or language-confidence score.
- No NER model or proxy heuristic.
- No population embedding similarity and no fabricated manual labels.
- No Phase-2 tokenizer roundtrip; full tokenizer measurement remains in G3.
- No 5,652,925-row execution and no final `PAIR_REGISTRY_v002` or QC artifact.

Manual-audit logistics and formal full-run authorization remain external decisions. Heartbeat observability does not authorize population execution.
