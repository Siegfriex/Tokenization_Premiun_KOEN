# Pair Identity & Duplicate Semantics — Pre-G1 Design (v1)

Scope: **semantics only**. Hash algorithm choice, string canonicalization implementation, and code all belong to Codex. This document defines what each identity concept *means* and what policy candidate applies to each duplicate scenario — nothing here is written into a config yet.

**Status update (2026-08-16, Vice Director accepted, no longer proposal)**: the `pair_id`(provenance-based) vs `duplicate_group_id`(content-based) split in §1-3 and §5 below is **ACCEPTED** — it is not a further Research Director decision item. Binding restatement: Record Identity ≠ Pair Content Identity; raw records are preserved in the registry regardless of duplicate status (never deleted for being a duplicate); **one content identity (`duplicate_group_id`) can map to multiple `pair_id`s**; Analysis-Representative selection alone governs primary-cohort inclusion and remains the one open item (§4, still `WAIT_FOR_TARGETED_EDA_RECON`); `translation_direction` conflict within a group is a **QC signal**, never a key used to split the group.

**Vice Director addendum (2026-08-16, evidence-level correction applied)**: `data/g0-aihub-recon@6e89b9e` ("persist SHA-256 collision-resistant duplicate/identity recon v001") has been fetched and verified as an actual remote commit — the addendum's caution to keep new duplicate numbers at `EXECUTED_REPORTED/PERSISTENCE_PENDING` until remote commit confirmation is therefore **satisfied for this specific evidence**; the figures in §4a/§4b below are treated as **L4 (remote-git-verified)**, not merely reported. See §6 for the one item that genuinely remains unresolved.

## 0. Analysis Representative is a provenance pointer, not a semantic-covariate source (Vice Director correction)

An earlier draft of this contract implicitly risked treating "whichever raw row is selected as Analysis Representative" as also the source of that content-pair's analysis-time covariates (e.g., its `translation_direction`). **This is corrected**: the Analysis Representative row is *only* a provenance pointer (which physical raw row the accepted content-level pair traces back to for lineage/audit purposes). It does **not** determine the semantic covariates used in analysis. Those covariates are computed by **resolving across the whole `duplicate_group`**, not inherited from one member.

**Group-resolved `translation_direction` rule** (the concrete case the directive specifies):

```text
direction_set = { distinct translation_direction values observed across all records in the duplicate_group }

IF direction_set == {KO_TO_EN}          → resolved translation_direction = KO_TO_EN
IF direction_set == {EN_TO_KO}          → resolved translation_direction = EN_TO_KO
IF direction_set == {KO_TO_EN, EN_TO_KO} → resolved translation_direction = UNKNOWN
                                            AND direction_conflict_flag = true
```

This generalizes beyond direction — any covariate that could vary within a duplicate_group (not only direction) should, in principle, follow the same group-resolution discipline rather than "pick the representative's value." Direction is the only covariate the directive specifies a concrete rule for; extending this to `domain`/`source_id` conflicts within a group is **not yet specified** and is flagged as a follow-on design question, not resolved here.

## 1. Why `pair_id` should not be a plain content hash

If `pair_id = hash(ko_text, en_text)`, two things break:
1. **Record identity collapses into content identity.** Two raw rows that are genuinely different records (different source file, different `sn`, possibly different `translation_direction` label) but happen to share text would become indistinguishable — you could not tell "the same physical annotation appears twice" from "two independent annotators produced the same sentence."
2. **Provenance is not reconstructible.** SSOT §11 requires original text never be overwritten and full lineage to be traceable (§30.2: raw file hash, transformation manifest, rejected pair list, accepted pair hash). A content-hash `pair_id` cannot point back to "which physical file, which row" once duplicates exist.

**Recommended structure**:

```text
pair_id           = provenance-based stable record identity   (survives re-ingest of the same raw files)
duplicate_group_id = content-based exact-pair identity          (groups pair_ids whose KO+EN content match)
```

`pair_id` answers "which raw row is this." `duplicate_group_id` answers "which other raw rows say the same thing." Both are needed; neither substitutes for the other. This is exactly what the directive's own recommended structure states, and it is adopted as the working assumption below.

## 2. Four identity concepts (definitions)

| Concept | Definition | Local evidence anchor |
|---|---|---|
| **Record Identity** | The identity of one raw ingested row, preserved regardless of whether its content duplicates another row. Must never be merged away even if the row is excluded from primary analysis. | Every physical row in every one of the 23 raw files (JSON `data[]` objects, XLSX rows) has one. |
| **Pair Content Identity** | Whether the KO/EN raw content of two records is the same pair, independent of which records they came from. | The BLAKE2b-64 candidate hashing already run by data-recon (`aihub_duplicate_overlap_...json`) approximates this, but is explicitly flagged as collision-possible, not certified. |
| **Duplicate Group** | The set of all Record Identities sharing one Pair Content Identity. | e.g., the 93,823 distinct duplicate pair-hashes observed in 025 each define one group. |
| **Analysis Representative** | The single record from a Duplicate Group that is actually included in primary analysis (D-01 accepted cohort). All other group members are retained (not deleted) but excluded from primary analysis with a documented reason. | Not yet computed locally — this document only specifies the concept. |

`pair_id` = Record Identity. `duplicate_group_id` = Duplicate Group key. Analysis Representative selection is a QC-layer decision (which record to keep) that must be deterministic and logged, not silently "first row wins" without a stated rule — the rule itself (e.g., prefer curated-tier source, prefer non-validation split, prefer earliest `sn`) is left **open** pending Research Director input (see decision queue).

## 3. `duplicate_group_id` must be direction-agnostic

If `duplicate_group_id` is computed over `(ko_text, en_text, translation_direction)`, a pair with identical KO/EN content but conflicting direction labels would land in two different groups — **hiding** exactly the conflict SSOT and this contract most need visible (see scenario 6 below). Recommendation: compute `duplicate_group_id` over KO+EN content only. Direction is then an *attribute observed per member of the group*, and a group containing more than one distinct direction value is itself a QC signal, not something to engineer away.

## 4. Scenario-by-scenario policy candidates

Per directive: `HARD_EXCLUDE_DUPLICATE | RETAIN_PROVENANCE_ONLY | KEEP_AS_DISTINCT | REVIEW_REQUIRED`. **Status (2026-08-16): the final Analysis-Representative selection rule (which policy wins operationally for scenarios 1/2/3/6) remains explicitly OPEN — classification `WAIT_FOR_TARGETED_EDA_RECON` — pending other agents' in-progress work on 025 direction×split duplicate decomposition, exact-pair overlap, multiplicity, cross-corpus duplicates, and collision-resistant rechecking. Do not adopt any of earliest-`sn` / non-validation-preference / source-tier-preference / direction-preference / first-occurrence yet.** What IS already settled (not open): raw provenance is always preserved; one `duplicate_group_id` can span multiple `pair_id`s; the project split must prevent duplicate/near-duplicate leakage; an excluded exact duplicate must never contribute twice to the primary cohort.

| # | Scenario | Local evidence | Proposed policy candidate | Reasoning |
|---|---|---|---|---|
| 1 | Same source/direction exact duplicate | 025 TL1-internal 10,240 dup rows against prior unique content; 026 has near-zero equivalent | **RETAIN_PROVENANCE_ONLY** | Raw row is kept (never deleted, §11 "원문 절대 덮어쓰지 않음"); exactly one Analysis Representative per `duplicate_group_id` enters the accepted cohort; the rest carry `pair_quality_status=review`→ effectively SSOT §10.1's "완전 중복 pair" hard exclusion, applied at the analysis-inclusion layer, not the storage layer |
| 2 | Train/validation duplicate (cross-split) | 025: 47,385/300,038 (15.8%) validation rows share a training pair-hash; 026: 9/150,018 (negligible) | **REVIEW_REQUIRED → resolved by LR-01 at split-construction, not at ingest exclusion** | This is a *split-assignment* problem (§23 Leakage Rule LR-01: group by near-duplicate cluster, assign the whole cluster to one side), not a content-exclusion problem — the content itself is valid data, it just cannot appear on both sides of a held-out split |
| 3 | Cross-source coincidental identical KO/EN | **L4-verified** (`data/g0-aihub-recon@6e89b9e`): project-wide cross-corpus exact-pair-digest overlap — 025↔026=0, 025↔Legacy=35, 026↔Legacy=1. **Within-Legacy, file×file matrix flags an anomaly**: `3_문어체_뉴스(2).xlsx` ↔ `4_문어체_한국문화.xlsx` share **2,469** distinct exact-pair digests, sharply higher than other Legacy file pairs (mostly 0-7). Recorded as **`POTENTIAL_SOURCE_REUSE / COMPOSITION_OVERLAP`** — not asserted as an error; cause (same original text recompiled across workbooks, deliberate cross-referencing, etc.) is explicitly not adjudicated by this contract or by data-recon's own report. | **REVIEW_REQUIRED** | A `duplicate_group_id` spanning two different `source_id`s (or, within Legacy, two different `domain`-labeled workbooks) is legitimate provenance, not necessarily an error; silently picking one Analysis Representative would erase a source/domain data point. Needs an explicit domain-aware representative-selection rule before mechanization — root-cause investigation of the News(2)/Culture overlap is routed to data-recon/Codex, not resolved here. |
| 4 | Same KO, different EN | Not directly measured | **KEEP_AS_DISTINCT** | Pair Content Identity differs (EN differs) → not a duplicate pair by definition, just a case of translation variance; do not silently deduplicate on one language alone |
| 5 | Different KO, same EN | Not directly measured | **KEEP_AS_DISTINCT** | Symmetric to #4 |
| 6 | Same KO/EN content, conflicting `translation_direction` metadata | **Plausible mechanism identified**: 025 ships TL1 (영→한) and TL2 (한→영) as separate files; if these are direction-mirrored views of an overlapping sentence pool, that would materially explain 025's unusually high duplicate-pair rate — this is a **hypothesis, not confirmed** by current evidence | **REVIEW_REQUIRED; direction is never silently overwritten** | If confirmed, this duplication may be *by construction*, not an error (see AMB-style open question below). Either way, per Task 5's own rule, a content-identical pair with conflicting direction labels must route to manual review, never auto-resolved to one direction |

**Open question — now PARTIALLY answered by L4-verified evidence** (`data/g0-aihub-recon@6e89b9e`, §C of `PAIR_DUPLICATE_RECON_v001_20260816.md`): cross-direction (`EN_TO_KO`×`KO_TO_EN`) distinct-pair-digest overlap in 025 = **50,511**, out of 93,823 total distinct duplicate groups (~54%). This **confirms the direction-mirroring hypothesis is real and material** — roughly half of 025's duplicate groups are explained by TL1/TL2 covering overlapping content from both directions, which is a benign-by-construction pattern, not an error. **It does not fully resolve the question**: the remaining ~46% of duplicate groups (93,823 − 50,511 ≈ 43,312) are *not* cross-direction and still require the same same-direction-repetition-vs-data-quality-problem investigation originally flagged — this residual piece remains `WAIT_FOR_TARGETED_EDA_RECON`, not closed.

**Also L4-verified, new**: split×split (`TRAIN`↔`VALIDATION`) distinct-pair-digest overlap, project-wide (025+026 combined) = **25,247**. This is a complementary metric to the earlier row-level figures (025: 47,385/300,038 rows; 026: 9/150,018 rows) — it counts distinct content groups rather than rows, and confirms the leakage risk is not a row-counting artifact.

**`sn` uniqueness — resolved, no longer a caveat**: `data/g0-aihub-recon@6e89b9e` §E reports **zero** within-file and **zero** cross-sub-file `sn` collisions for both 025 (2,700,345 nonempty sn rows, 2,700,345 distinct sn digests) and 026 (1,350,162 / 1,350,162). `sn` is therefore confirmed **dataset-wide unique** for both JSON corpora, not merely "file-scoped" as earlier drafts of this contract cautioned — see §5 update below.

## 5. Pair ID / Source ID contract (Task 4)

| Concept | Semantics | Uniqueness scope | Local evidence basis |
|---|---|---|---|
| `source_id` | Stable identity reflecting dataset family + version/acquisition provenance. Must **not** rely on the (currently unconfirmed, AMB-12/OPEN) official AIHub `dataSetSn` — should carry a placeholder for it once confirmed. | Project-wide, one per (local dataset family × ingest snapshot) | 3 local families (025, 026, Legacy) each need a `source_id`; sub-files (TL1/TL2/VL1, or per-workbook) are **not** separate `source_id`s — they are `source_record_id` scope, see below |
| `source_record_id` | The raw in-file record identity, exactly as the source system encodes it. | JSON (025/026): **dataset-wide unique, L4-verified** (`data/g0-aihub-recon@6e89b9e` §E: 0 within-file and 0 cross-sub-file `sn` collisions for both). XLSX (Legacy): **file-scoped only, still requires a location qualifier** | JSON: `sn`. XLSX: `ID`/`SID` (confirmed **not** globally unique — 127,824 duplicate rows in Legacy when treated as global) |
| `raw_locator` | Exact re-traceable physical position. | N/A (always paired with `source_record_id`) | JSON: `{relative_path, sn}`. XLSX: `{relative_path, sheet_name, physical_row_number}` — required fallback for 대화체, which has no reliable in-file key at all (composite `Set Nr.`+`발화자` has 8 duplicate rows out of 100,000) |
| `pair_id` | Project-level stable key = **derived from `(source_id, source_record_id)`**, i.e., provenance-based, not content-based. Deterministic across re-ingest as long as source files are unchanged. | Project-wide unique by construction (one raw row → one `pair_id`) | — |
| `duplicate_group_id` | Content-based exact-pair identity (§3 above); **ACCEPTED as a required D-01 field** (Vice Director, 2026-08-16) | Project-wide, many `pair_id`s may share one `duplicate_group_id` | Populated informationally by data-recon's BLAKE2b-64 candidate hashing; **collision-possible, not a certified exact-match algorithm** — final hash scheme is Codex's to choose |

**Explicit rule for Legacy**: never use bare `ID`/`SID` as `source_record_id` without a workbook/file qualifier — this applies to **every** Legacy workbook, not only 대화체, given the 127,824-row global collision count spans the whole family.

---
See `docs/contracts/G1_PAIR_REGISTRY_PRECONTRACT_v1.md` for how these concepts map onto the D-01 registry, and `docs/research/G1_DECISION_QUEUE_v1.md` for which open items here need Research Director sign-off.
