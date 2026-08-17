# G1 Pair Registry Precontract — v1

**Status: IMPLEMENTATION-READY (2026-08-16).** This still contains no code and is not itself the `01_build_pair_registry.ipynb` implementation — but every D-01 field's Phase-1 semantics are now frozen (§16), the config delta is applied to `configs/research_v1.yaml` on canonical `research/g1-claude` (§15), and the duplicate representative rule is finalized (§7). No further Research Director decision is expected before Codex implements `01_build_pair_registry.ipynb` against this contract. It draws on `docs/research/PAIR_IDENTITY_AND_DUPLICATE_CONTRACT_v1.md`, `docs/research/DIRECTION_AND_DOMAIN_MAPPING_PRECONTRACT_v1.md`, `docs/research/AIHUB_LOCAL_WEB_RECONCILIATION_v1.md`, and SSOT §9-12.

## 0. The 01 / 02 boundary (do not confuse)

- **`01_build_pair_registry` (ingest)**: move raw source records into a reproducible registry with stable identity and full provenance. Exclusions here are **structural/parsing failures only** — a record could not be read into the schema at all (e.g., missing required field, undecodable encoding, malformed JSON/XLSX row).
- **`02_normalize_and_qc` (QC)**: apply SSOT §10.1 hard exclusions (empty text, exact duplicates, language-ID failure, markup-dominant text, control-character anomalies, tokenizer round-trip failure, semantic-QC failure) and §10.2 soft flags.

A record that ingests successfully but is a duplicate, or has anomalous-but-parseable text, is **not** excluded at step 01 — it enters the registry with its full identity and gets excluded/flagged at step 02. Conflating these two exclusion reasons would make it impossible to later ask "how many raw records existed at all" independent of "how many passed QC."

## 1. Source acquisition identity

Each of the 3 currently-known local dataset families (025, 026, Legacy) gets one `source_id`. `source_id` must carry: local family label, ingest snapshot reference (pointing to the `RAW_FILE_MANIFEST_SHA` data-recon already computed — `9a546bc9...c1f0c`), and a placeholder for the official AIHub `dataSetSn` (still unconfirmed — `provenance_closure_status` tracks this separately from the now-resolved `source_tier`; do not fabricate a `dataSetSn`). D71693 has no `source_id` yet — it is `NOT_ACQUIRED`.

## 2. Source registry & license note

Per D-01 schema (§12.1): `source_id`, `source_tier`, `source_license_note`. **`source_tier` values are now Director-approved (D-RD-05, NOT withdrawn — Vice Director reconfirmed 2026-08-16) and APPLIED** — 025=A, 026=A, Legacy=`null`/UNASSIGNED (not B — the earlier tentative-B recommendation was explicitly withdrawn; Tier B must not be used as a provenance-shortfall fallback). **These values are now written into `configs/research_v1.yaml`** (`source_hierarchy.corpus_tier_assignment`, `source_portfolio`) on canonical `research/g1-claude` — see §15.

**New field (Vice Director addendum): `provenance_closure_status`** — separate from `source_tier`, tracks how closed the official-provenance loop is:
- 025, 026: `PENDING_OFFICIAL_SCHEMA_AND_RELEASE_LINK`
- Legacy: `PARTIAL_OFFICIAL_CONSTRUCTION_CONFIRMED_FIELD_AND_RELEASE_LINK_PENDING` (D87's general existence/scale is more corroborated by the official catalogue than 025/026's field-level schema is, even though Legacy's own schema/version link is weaker — the two facts don't contradict, they're different axes)

`source_license_note` must record the **self-asserted** raw `license` field value (`"open"` for 025/026 JSON) verbatim, plus an explicit annotation that this has not been checked against AIHub's official usage policy (application/approval requirement, redistribution restriction — per Perplexity's evidence audit U1-U3). Legacy has no license field at all — `source_license_note = "UNKNOWN — no license metadata in source"`.

**Forbidden inferences (Vice Director addendum, binding everywhere this precontract is applied)**: do not assert `mt` = confirmed MT draft; do not assert `ko`/`en` = confirmed human-final text; do not assert `ko_original`/`en_original` field semantics beyond "present/absent" before official confirmation; do not assert `license="open"` = redistribution permission.

## 3. Raw file hash linkage

Every `pair_id` must be traceable to the exact physical raw file(s) it came from via the already-computed per-file SHA-256 values in `AIHUB_RAW_RECON.md` §B. This is provenance linkage only — it does not imply re-verification of those hashes at registry-build time (though re-verification is cheap and recommended as a smoke test, that is Codex's implementation call).

## 4. Pair grain & stable pair identity

One registry row = one raw KO/EN record, per the identity design in `PAIR_IDENTITY_AND_DUPLICATE_CONTRACT_v1.md`: `pair_id` is provenance-derived (`source_id` + `source_record_id`), never a content hash. `duplicate_group_id` (content-based) is a **required** auxiliary field (Vice Director accepted).

## 5. Raw provenance / raw field selection

For JSON corpora, the registry must retain `sn`, `data_set`, `domain` (raw), `subdomain` (raw), `ko`, `en`, `ko_original`/`en_original` (whichever present), `mt`, `source_language`, `target_language`, `source` (raw), `license` (raw), `style`, `file_name` — i.e. the full core field set data-recon already enumerated, not a pre-filtered subset. For XLSX, retain the full workbook row plus `raw_locator` (`relative_path`, `sheet_name`, `physical_row_number`).

## 6. Translation direction & source/domain mapping

Apply the rules in `DIRECTION_AND_DOMAIN_MAPPING_PRECONTRACT_v1.md` §Task 5/6 exactly — **both are now Director-approved (D-RD-06/D-RD-07), not drafts**: Legacy `translation_direction = UNKNOWN` (not `HUMAN_PARALLEL_UNKNOWN`); the top-level domain mapping table is approved and may be applied at ingest for `domain` (canonical), while `domain_raw`/`subdomain_raw` are always captured alongside, unmodified — subdomains are never mapped to canonical form by design (not a pending item).

### 6a. Raw `source` field ≠ canonical `source_id` (new distinction, directive-mandated)

The JSON/XLSX raw `source` field (observed values: `SBS`, `크라우드 소싱`, `크라우드소싱`, `한국연구재단`, `특허정보원`, publisher names for Legacy news, etc.) is **not** the canonical `source_id`. It must be stored as a separate auxiliary field, `source_provenance_raw`, preserved verbatim (including literal-string variants like the "크라우드 소싱"/"크라우드소싱" space difference — never normalized away). Canonical `source_id` stays at corpus/acquisition-family granularity (`025-family`, `026-family`, `Legacy-family`, or the official AIHub `dataSetSn` once confirmed) — one level up from these fine-grained raw labels. Conflating the two would corrupt the Identifiability Gate below, since `source_provenance_raw` and `source_id` must be checked as **independent** axes, not collapsed into one.

## 7. Duplicate group semantics & exact-duplicate handling candidates

Registry construction computes `duplicate_group_id` (required, per `PAIR_IDENTITY_AND_DUPLICATE_CONTRACT_v1.md` status update) but does **not** perform hard-exclusion at step 01 — that is a `02_normalize_and_qc` decision per SSOT §10.1. Step 01's job is only to make duplicate membership *visible and queryable*. See the 6 scenario policies in `PAIR_IDENTITY_AND_DUPLICATE_CONTRACT_v1.md` §4.

**Analysis-Representative selection — FINALIZED (2026-08-16, targeted EDA/recon now sufficient per directive)**: `representative_pair_id = lexicographically minimum pair_id within duplicate_group_id` (or an equivalent stable canonical raw-locator ordering — the exact string-sort implementation is Codex's call, but it must be deterministic and carry **no semantic preference**). Explicitly **forbidden** as a selection criterion: preferring train over validation, a specific translation direction, a specific domain, a specific `source_provenance_raw`, a specific tier, or longer/shorter text — any of these would silently bias which record's provenance gets cited, even though (per the correction below) it doesn't bias the analysis covariates themselves.

**Vice Director correction — Analysis Representative ≠ semantic covariate source**: whichever record is chosen as Analysis Representative is a **provenance pointer only** (which raw row's lineage the accepted content-level pair cites). The content-level analysis pair's semantic covariates are **group-resolved** across every member of the `duplicate_group`, not inherited from the representative:
- `translation_direction`: all-`KO_TO_EN` → `KO_TO_EN`; all-`EN_TO_KO` → `EN_TO_KO`; mixed → `UNKNOWN` + `direction_conflict_flag=true`.
- `domain`, `source_id`, `source_provenance_raw`: no group-resolution value-selection rule is specified yet (only `translation_direction` has one) — instead, any group containing more than one distinct value on these axes must set the corresponding flag (`domain_conflict_flag`, `source_id_conflict_flag`, `source_provenance_raw_conflict_flag`) and **must not** be silently resolved from the representative row. Picking an actual resolved value for these three is a follow-on design question, not answered here.

**L4-verified evidence now available** (`data/g0-aihub-recon@6e89b9e`, git-remote-confirmed): 025 cross-direction (`EN_TO_KO`×`KO_TO_EN`) distinct-pair-digest overlap = 50,511 of 93,823 total duplicate groups (~54%, confirms direction-mirroring is real but only partially explains the duplication — the remaining ~46% needs separate investigation); project-wide train/validation distinct-digest overlap = 25,247; cross-corpus exact-pair overlap 025↔026=0, 025↔Legacy=35, 026↔Legacy=1; and a flagged Legacy-internal anomaly, `3_문어체_뉴스(2).xlsx`↔`4_문어체_한국문화.xlsx` sharing 2,469 distinct exact-pair digests — recorded as `POTENTIAL_SOURCE_REUSE / COMPOSITION_OVERLAP`, not asserted as an error, root cause not adjudicated here.

## 8. Split provenance

Registry must preserve the **upstream** split label as ingested (`is_validation` boolean, matching data-recon's own manifest field) as raw provenance — this is not the same as the project's own train/hold-out split (§23), which is constructed later and independently, using `GroupKFold(source_id)` or near-duplicate cluster grouping per Leakage Rule LR-01. Do not let the AIHub-provided train/valid split silently become the project's analysis split without applying LR-01 first (given the 15.8% training/validation pair-hash overlap already observed in 025).

## 9. Missing text / schema violation / ingest exclusion vs QC-later

- **Ingest exclusion** (01): record could not be parsed into the D-01 schema at all — e.g. malformed JSON object, unreadable XLSX row, required field structurally absent. Data-recon observed **zero** empty/null/absent `ko`/`en`/`sn`/원문/번역문 across all 23 files, so on current evidence ingest-exclusion volume should be at or near zero — but the registry build must still implement the check, not assume it.
- **QC-later exclusion** (02): record parsed fine but fails a §10.1 hard-exclusion rule (duplicate, anomalous, language-ID failure, etc.) — these records **do** enter the D-01 registry with `pair_quality_status` reflecting their eventual disposition, they are not silently dropped at 01.

## 10. Required row-count reconciliation

At minimum, the registry build must reconcile and report: physical file record counts (from data-recon: 025=2,700,345 unique-content / 026=1,350,162 / Legacy=1,602,418) against registry row counts, and explain any discrepancy (e.g., byte-identical source/label file pairs must not be double-ingested — data-recon's Risk #1 flags exactly this: "원천/라벨링 JSON이 byte-identical이다... 재귀 ingest하면 D025와 D026이 정확히 2배 집계"). A registry build that silently double-counts these would produce a false sense of scale.

## 11. D-01 required fields (per SSOT §12.1, unchanged, restated for traceability)

`pair_id, source_id, source_tier, domain, sentence_type, translation_direction, ko_text_raw, en_text_raw, ko_text_nfc, en_text_nfc, ko_text_analysis, en_text_analysis, pair_quality_status, pair_quality_score, pair_version, source_license_note`

## 12. Auxiliary fields (status: ACCEPTED, directive §2/§7 — no longer pending Director confirmation as a batch)

`source_record_id`, `raw_locator`, `duplicate_group_id` (required, §7), `domain_raw`, `subdomain_raw`, `source_provenance_raw` (§6a — the raw `source` label, distinct from `source_id`; preserves "크라우드 소싱" vs "크라우드소싱" distinctly), `is_validation_upstream` (AIHub-provided split flag, distinct from project split), `translation_direction_review_flag`, `mt_field_present` (whether an `mt` staging field existed in the source record). None are implemented yet — this is still semantics-only, no notebook/code written.

## 13. Downstream linkage to D-02/D-03/D-04

`pair_id` is the join key into D-02 (Representation Features), D-03 (Morphology Measurement), D-04 (Token Measurement) — this registry precontract does not change that join-key design, it only fixes what `pair_id` itself means (§4 above, and `PAIR_IDENTITY_AND_DUPLICATE_CONTRACT_v1.md`).

## 14. Identifiability Gate — minimum required diagnostics (directive §5, new)

Before G1/G5 allow any independent-effect interpretation of `domain`, `source_id`, or `translation_direction` coefficients, the following four contingency tables are **mandatory**, not optional:

1. `source_id × canonical_domain`
2. `source_id × translation_direction`
3. `source_provenance_raw × canonical_domain`
4. `source_provenance_raw × translation_direction`

**This is not a precautionary formality — near-perfect confounding is already confirmed in current evidence**:
- **026**: `domain=기술과학` (train 319,551 + valid 40,359) is **numerically identical** to `source_provenance_raw=특허정보원` (train 319,551 + valid 40,359) — every 특허정보원 row is 기술과학 and vice versa. The other four 026 domains (세계/경제/정치/기후) are correspondingly identical to `source_provenance_raw=한국연구재단`. Domain and raw-source are **not separably estimable** for 026 as currently structured.
- **025**: the `EN_TO_KO` validation split is **100% `domain=해외영업`** (all 150,038 rows), while `EN_TO_KO` training is mixed across all 3 domains — a direction×domain×split asymmetry that must be visible before any split-based generalization claim.

Per SSOT Gate G-ID (§20.2): if domain and source (raw or canonical) are structurally unidentifiable, do not force a coefficient table — redesign (e.g., treat `domain` and `source_provenance_raw` as a single composite factor for 026, or restrict domain-effect claims to 025 only where more variation exists). This redesign decision is **not made here** — it is deferred to whoever runs the actual M0-M3 model fitting, with this gate as a hard precondition.

## 15. G1_CONFIG_DELTA — APPLIED to `configs/research_v1.yaml` (2026-08-16, canonical `research/g1-claude`)

Now that G0 is canonical (merged to `main@f1b2a90`), the delta previously proposed on the diverged `research/g1-prep-claude` branch has been applied to `configs/research_v1.yaml` on this branch: `source_hierarchy.corpus_tier_assignment`, `source_portfolio` (role/eligibility/`provenance_closure_status`), `primary_cohort_policy`, `translation_direction_defaults`, `domain_mapping_top_level`, `d01_field_contract` (§16 below), `identifiability_gate_minimum_diagnostics`, and `auxiliary_notebook_namespace` are all live in that file — it is the authoritative machine-readable source, not this section. D-RD-05 through D-RD-08 are applied **exactly as approved, not reinterpreted**.

## 16. D-01 field-by-field Phase-1 semantics (directive-mandated, closes remaining D-01 gaps)

**A. `sentence_type`**: preserve `sentence_type_raw` verbatim if the source supplies explicit metadata; otherwise canonical `sentence_type = other`. A separate `sentence_type_provenance_status = UNAVAILABLE_IN_RAW_SOURCE` records when no source metadata exists. **Forbidden**: inferring sentence type from punctuation at ingest when the source provides no explicit metadata — none of 025/026/Legacy's schemas carry a sentence-type field, so on current evidence this will be `other`/`UNAVAILABLE_IN_RAW_SOURCE` for all three at Phase 1.

**B. `ko_text_nfc`/`en_text_nfc`/`ko_text_analysis`/`en_text_analysis`**: SSOT lists these as D-01 fields, but normalization is Phase 2's job (`02_normalize_and_qc`). **Design (chosen, not left implicit for Codex)**: Phase 1 creates these four columns **nullable**, with `normalization_status = NOT_GENERATED_PHASE1`. Phase 2 populates them into a **new pair-registry version** (or a deterministic derived artifact keyed by `pair_id`) — it does not mutate Phase 1's frozen registry file in place. This preserves Phase 1's reproducibility (re-running `01_build_pair_registry` alone always yields the same nullable-column registry) independent of whatever normalization rules Phase 2 later applies or revises.

**C. `pair_quality_status`**: SSOT allows only `accepted`/`review`/`rejected`. At Phase 1, full semantic QC (§10.3) has not run yet, so **no record may be `accepted` at this stage**. Phase 1 value = `review` for every structurally-ingestible record, plus an auxiliary `qc_stage_status = PENDING_PHASE2` making explicit that "review" here means "not yet QC'd," not "flagged for concern."

**D. `pair_quality_score`**: `null` at Phase 1 — populated only after semantic-alignment measurement (§10.3) runs in a later phase.

**E. `pair_version`**: syntax `v001` (zero-padded 3-digit integer, matching SSOT §38's file-naming convention, e.g. `PAIR_REGISTRY_v001.parquet`), incrementing on any registry-affecting schema or ingest-scope change.

## 17. Auxiliary notebook namespace

`notebooks/01_build_pair_registry.ipynb` remains the **only** canonical Phase-1 notebook. Any notebook named `notebooks/01_aihub_local_recon_evidence_export.ipynb` is **not** canonical Phase 1 — its sanctioned, sanitized destination is `notebooks/exploratory/evidence/AIHUB_LOCAL_RECON_EVIDENCE_EXPORT_20260816.ipynb`. As of this freeze, no such notebook exists in any fetched branch (`main`, `integration/g0`, `impl/g0-codex`, `data/g0-aihub-recon`, `eda/g0-raw-notebooks` all checked, read-only) — this is a naming contract for if/when one is created, not a correction of an existing file.
