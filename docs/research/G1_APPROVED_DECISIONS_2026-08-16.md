# G1 Approved Decisions — 2026-08-16

Research Director approved all four Vice Director recommendations below. **These apply SSOT taxonomy/contract to the current corpus — they do not change SSOT's research meaning, so no SSOT amendment or CHANGE_REQUEST is created for any of them.** `research/g0-claude@51147e3` remains frozen and untouched. `configs/research_v1.yaml` is **not** edited this round (see `docs/contracts/G1_PAIR_REGISTRY_PRECONTRACT_v1.md` §15 `PROPOSED_G1_CONFIG_DELTA` for the values to apply once Vice Director sequences G1 onto the canonical G0 base).

## D-RD-05 — Source Portfolio

| Corpus | `source_tier` | `research_role` | `primary_analysis_eligible` |
|---|---|---|---|
| 025 / D71265 | A | `PRIMARY_BACKBONE` | true |
| 026 / D71266 | A | `PRIMARY_DOMAIN_SUPPLEMENT` | true — condition: domain-specialized, `KO_TO_EN`-only, source/domain/direction structure kept explicit, **never pooled with 025 without a labeled stratum** |
| Legacy / D87 | `null` / **UNASSIGNED** (Tier B recommendation **withdrawn** — Tier B ≠ a fallback for weak provenance) | `SENSITIVITY_ONLY` | false |
| D71693 | — | `NOT_ACQUIRED` | `OUTSIDE_CURRENT_CORPUS` — no download proposed/started |

## D-RD-06 — Translation Direction

- 025: `KO_TO_EN` / `EN_TO_KO` per raw provenance (`ko_original`/`en_original` + `source_language`/`target_language` consistency)
- 026: `KO_TO_EN` (single direction, no reverse-direction file exists)
- Legacy: **`UNKNOWN`** — not `HUMAN_PARALLEL_UNKNOWN`; current evidence does not confirm human-parallel construction methodology. May upgrade to `HUMAN_PARALLEL_UNKNOWN` only if official construction documentation later confirms it.

## D-RD-07 — Canonical Domain Mapping

Top-level only; subdomains always stay `subdomain_raw`, never mapped:

- 025: 일상생활→`general`, 해외고객과의채팅→`dialogue`, 해외영업→`other`
- 026: 기술과학→`technology`, 세계→`other`, 경제→`other`, 정치→`other`, 기후→`other`
- Legacy: 구어체→`general`, 대화체→`dialogue`, 뉴스→`news`, 한국문화→`other`, 조례→`legal`, 지자체웹사이트→`administration`

Raw domain/subdomain labels are never overwritten — preserved verbatim in `domain_raw`/`subdomain_raw` alongside the canonical `domain` field.

## D-RD-08 — Primary Cohort Size Policy

AMB-05 is no longer "pick a target N." Primary analysis cohort = every 025+026 pair that is G1 ingest-valid, G2/QC-accepted, survives exact-duplicate policy, and is Tier-A eligible. **No arbitrary fixed cap, no pre-analysis 100k sampling, no 500k convenience cap.** SSOT's 100,000+ (§9.1) is a recommended floor, not a ceiling. Final numeric N is a realized value of the QC/dedup pipeline, not chosen in advance — and is not written anywhere yet.

## Still open (not resolved by the above)

- Duplicate Analysis-Representative selection rule — `WAIT_FOR_TARGETED_EDA_RECON` (other agents actively investigating 025 direction×split duplicate decomposition)
- AMB-13-adjacent: none remaining
- Full detail and rationale: `docs/research/G1_DECISION_QUEUE_v1.md`

## Vice Director Addendum — Evidence-Level / Duplicate Semantics (2026-08-16)

1. **WEB/OFFICIAL evidence and LOCAL OBSERVED evidence are separate tracks.** Perplexity has no filesystem access; this reconciliation has no official-release access. Neither overwrites the other — disagreements are `CONFLICT_FOR_RECONCILIATION`, not resolved by picking a side. Verified via `git fetch`: `evidence/g0-perplexity` is unchanged at `c5b704f` — no new official-document audit has actually landed yet, despite the addendum anticipating one.
2. **D-RD-05 is NOT withdrawn** — 025=A/`PRIMARY_BACKBONE`, 026=A/`PRIMARY_DOMAIN_SUPPLEMENT`, Legacy=`null`/`SENSITIVITY_ONLY` all stand. New field `provenance_closure_status` added (separate from `source_tier`): 025/026=`PENDING_OFFICIAL_SCHEMA_AND_RELEASE_LINK`, Legacy=`PARTIAL_OFFICIAL_CONSTRUCTION_CONFIRMED_FIELD_AND_RELEASE_LINK_PENDING`.
3. **Forbidden inferences, restated**: `mt`≠confirmed MT draft; `ko`/`en`≠confirmed human-final; `ko_original`/`en_original` semantics unconfirmed beyond presence; `license="open"`≠redistribution permission.
4. **Evidence-level discipline**: new Data Recon evidence is held at `EXECUTED_REPORTED/PERSISTENCE_PENDING` until a remote commit is verified. **Verified this round**: `data/g0-aihub-recon@6e89b9e` ("persist SHA-256 collision-resistant duplicate/identity recon v001") is confirmed pushed — its figures (item 5-7 below) are treated as **L4**, not pending.
5. **Duplicate contract correction**: Analysis Representative = provenance pointer only, never the source of analysis-time semantic covariates. `translation_direction` is **group-resolved**: direction_set={KO_TO_EN}→KO_TO_EN; ={EN_TO_KO}→EN_TO_KO; ={KO_TO_EN,EN_TO_KO}→UNKNOWN+`direction_conflict_flag=true`.
6. **025 cross-direction exact-content overlap = 50,511** (L4-verified) — confirms ~54% of 025's 93,823 duplicate groups are direction-mirroring (benign); ~46% remain unexplained, still `WAIT_FOR_TARGETED_EDA_RECON`.
7. **Legacy News(2)↔한국문화 exact overlap = 2,469** (L4-verified) — recorded as `POTENTIAL_SOURCE_REUSE / COMPOSITION_OVERLAP`, not an asserted error.
8. G0/`main` lineage untouched — confirmed, this worktree only ever writes to `research/g1-prep-claude`.

Full detail: `docs/research/PAIR_IDENTITY_AND_DUPLICATE_CONTRACT_v1.md` and `docs/research/AIHUB_LOCAL_WEB_RECONCILIATION_v1.md` (both updated in place with status banners, nothing rewritten silently).

## Canonical G1 Freeze (2026-08-16) — migration off `research/g1-prep-claude`

Per Director instruction, work moved off the diverged `research/g1-prep-claude` (last SHA `970a52e`) onto `research/g1-claude`, branched fresh from canonical `main@f1b2a90` (verified via `git fetch` before branching, not assumed). The three research-only commits (`a3d2c45`, `1ba3baa`, `970a52e` — all touching only `docs/contracts/**`/`docs/research/**`, verified before porting) were cherry-picked cleanly, zero conflicts. `research/g1-prep-claude` itself is retired, not merged.

**Now applied** (previously deferred as `PROPOSED_G1_CONFIG_DELTA` because G0 wasn't canonical yet): D-RD-05 through D-RD-08 are live in `configs/research_v1.yaml` on `research/g1-claude` — `source_hierarchy.corpus_tier_assignment`, `source_portfolio`, `primary_cohort_policy`, `translation_direction_defaults`, `domain_mapping_top_level`, applied exactly as approved, not reinterpreted.

**D-01 gaps closed** (`docs/contracts/G1_PAIR_REGISTRY_PRECONTRACT_v1.md` §16, mirrored in `configs/research_v1.yaml.d01_field_contract`): `sentence_type` (raw-preserve or `other`+`UNAVAILABLE_IN_RAW_SOURCE`, never punctuation-inferred), the four NFC/analysis text fields (nullable at Phase 1, `normalization_status=NOT_GENERATED_PHASE1`, populated by Phase 2 into a new registry version — not an in-place mutation), `pair_quality_status` (`review` + `qc_stage_status=PENDING_PHASE2`, never `accepted` pre-QC), `pair_quality_score` (`null` until semantic-alignment measurement), `pair_version` (`v001` syntax per SSOT §38).

**Duplicate representative rule finalized**: `representative_pair_id = lexicographically minimum pair_id` within a `duplicate_group_id`, deterministic, explicitly barred from preferring train/validation, direction, domain, source, tier, or text length. New conflict flags added for group-level `domain`/`source_id`/`source_provenance_raw` disagreement (no resolution rule for these yet — only `translation_direction` has one).

**`docs/contracts/G1_PAIR_REGISTRY_PRECONTRACT_v1.md` is now IMPLEMENTATION-READY** — no further Director decision is expected before Codex begins `01_build_pair_registry.ipynb`. `docs/research/G1_DECISION_QUEUE_v1.md` was trimmed to the three genuinely unresolved categories: official provenance closure, Legacy composition interpretation, and later Phase 2 semantic QC outcomes.
