# AIHub Local × Web Evidence Reconciliation — v1

- Local evidence: `origin/data/g0-aihub-recon@15b9129e7dd2ab2ba7afeaa37ed890b15ff8f5a9` — `outputs/reports/data_recon/AIHUB_RAW_RECON_20260816T132650+0900.md` + `outputs/manifests/data_recon/aihub_{raw_profile,duplicate_overlap}_20260816T132650+0900.json`
- Web evidence: `origin/evidence/g0-perplexity@c5b704f4b534f4a5d4da5d3c3af78516f6814f6b` — `docs/evidence/aihub/AIHUB_KOEN_SOURCE_EVIDENCE_2026-08-16.md`
- Canonical authority: `KOEN-TP-RS-001` §9.3 (source hierarchy) + `research/g0-claude@51147e3` contract
- **This document is NOT G1 PASS, NOT a QC acceptance.** The evidentiary matrix below (§1-4) is unchanged factual reconciliation. **Task 2's tier/role recommendations have since been superseded by Research Director decision D-RD-05** (2026-08-16) — see `docs/research/G1_APPROVED_DECISIONS_2026-08-16.md` for the binding values. Task 2's table below is retained for its supporting-evidence reasoning but its `recommended_role`/`candidate_tier` fields are historical, not current.

**Key fact verified directly (grep over the raw profile manifest)**: no `71265`/`71266` string literal appears anywhere in the local raw JSON. The local↔official mapping below is a **title-string match only** — the local files never assert their own official AIHub `dataSetSn`. Treat every "identity confirmed" claim below as *title/domain/scale correspondence*, not a cryptographic or ID-field link.

**Vice Director addendum (2026-08-16) — WEB/OFFICIAL evidence vs LOCAL OBSERVED evidence stay separate tracks.** Perplexity's web/official-document audit (`evidence/g0-perplexity`) has no filesystem access and cannot verify local raw content; conversely, this reconciliation's local track cannot verify AIHub's official release/version metadata. Neither track substitutes for the other, and neither may silently overwrite the other's findings — disagreements are logged as `CONFLICT_FOR_RECONCILIATION`, not resolved by picking one side. As of this update, `origin/evidence/g0-perplexity` remains unchanged at `c5b704f` (no new official-document audit has actually been pushed yet, despite guidance anticipating one) — verified via `git fetch` rather than assumed.

**Forbidden inferences (explicit, apply everywhere in this document set)**: do not assert `mt` field = confirmed MT (machine-translation) draft; do not assert `ko`/`en` = confirmed human-final text; do not assert the meaning of `ko_original`/`en_original` fields beyond "present/absent" until officially confirmed; do not assert raw `license="open"` = redistribution permission. All four remain open/unconfirmed until an official source document says otherwise.

## 1. Dataset 025 ↔ D71265 candidate

| Field | Value |
|---|---|
| Official dataset ID | D71265, `일상생활 및 구어체 한-영 번역 병렬 말뭉치 데이터` |
| Local path/family | `data/raw/aigub/025.일상생활 및 구어체 한-영 번역 병렬 말뭉치 데이터/` (JSON+ZIP, 9 physical files / 5 unique SHA-256) |
| Raw manifest evidence | `aihub_raw_profile_...json` dataset_summaries; SHA-256 per physical file recorded in `AIHUB_RAW_RECON.md` §B |
| Record grain | top-level `data[]` object = one translation pair |
| Deterministic pairability | `ko`/`en` co-present in same object → direct pairable; `sn` nonempty & duplicate-free **within each file** (NOT verified across TL1 vs TL2 vs VL1 — see Task 3/4) |
| KO field | `ko` (+ `ko_original` in 한→영 files) |
| EN field | `en` (+ `en_original` in 영→한 files) |
| Pair/source key | `sn` — **file-scoped only**, not confirmed globally unique across sub-files |
| Translation direction observability | Both directions physically present (TL1=영→한, TL2=한→영); `source_language`/`target_language` observed consistent with file direction |
| Domain/subdomain metadata | 3 domains / 11 subdomains observed (exact label values not yet enumerated — pending Raw EDA); `source` field differs by direction: 영→한="크라우드 소싱", 한→영="크라우드소싱"(800,096)+"SBS"(399,904) in train — literal string variants, not normalized |
| Source metadata | Crowd-sourced translation + one broadcaster-labeled subset ("SBS") — raw label, not independently verified |
| License/acquisition evidence | JSON `license`="open" self-asserted in every unique-content record; Perplexity's official-policy audit (H3) shows AIHub requires application/approval and restricts external redistribution of raw files — **not a contradiction, but "open" must not be promoted to "verified redistribution clearance"** |
| Raw-text fidelity | Raw preserved; `mt`+`ko_original`/`en_original` fields imply an edit pipeline (source→MT draft→final) whose exact stage semantics are undocumented |
| Duplicate risk | **High** — 214,252 duplicate-pair rows after first occurrence; 93,823 distinct duplicate pair-hashes (BLAKE2b-64 candidate, collision-possible) out of 2,700,345 unique-content records (~8%) |
| Train/validation overlap | 47,385 / 300,038 validation rows (≈15.8%) share an exact pair-hash with training — material leakage risk if not handled at split-construction |
| Quality/provenance unknown | Official `dataSetSn`/version/build-date not linked; translator/reviewer identity unknown; whether duplication is by-design (TL1/TL2 direction-mirroring) or accidental repetition is **unresolved** (see Task 3) |
| Web/local consistency | Title, domain description (everyday/spoken), and bidirectionality all match Perplexity's D71265 record. No contradiction observed. |
| Unresolved conflict | None rising to `CONFLICT_FOR_RECONCILIATION` |
| **Status** | **CONSISTENT_BUT_INCOMPLETE** |

## 2. Dataset 026 ↔ D71266 candidate

| Field | Value |
|---|---|
| Official dataset ID | D71266, `기술과학 분야 한-영 번역 병렬 말뭉치 데이터`; web page states "1.5 million sentences" |
| Local path/family | `data/raw/aigub/026.기술과학 분야 한-영 번역 병렬 말뭉치 데이터/` (JSON only, 4 physical files / 2 unique SHA-256) |
| Record grain | top-level `data[]` object = one translation pair |
| Deterministic pairability | `ko`/`en` co-present; `sn` unique within file, 0 duplicates |
| KO/EN field | `ko` / `en` (+ `ko_original`, single direction only — see below) |
| Pair/source key | `sn`, file-scoped |
| Translation direction observability | **Single direction only — entirely 한→영 (KO_TO_EN).** No reverse-direction file exists locally for this family. |
| Domain/subdomain metadata | 5 domains / 15 subdomains; `source`=한국연구재단(880,593)+특허정보원(319,551) in train — both official Korean research/patent institutions, arguably stronger institutional provenance signal than 025's crowd-sourcing label |
| License/acquisition evidence | Same self-asserted `license`="open" caveat as 025 |
| Raw-text fidelity | Same edit-pipeline ambiguity as 025 (`mt`/`ko_original` present) |
| Duplicate risk | **Low** — only 44 duplicate-pair rows out of 1,350,162 (<0.01%) |
| Train/validation overlap | 9 / 150,018 (0.006%) — negligible |
| Quality/provenance unknown | Official ID link unverified (same as 025); **local unique-content count (1,350,162) is ~10% short of the web page's "1.5 million sentences" claim** — could be rounding/marketing language, an older baseline vs current archive, or a scope difference (sentences vs pairs); not resolved by this reconciliation |
| Web/local consistency | Domain description (technical/science) matches. The 1.35M vs "1.5M" scale gap is a **minor, non-blocking discrepancy** — logged, not silently reconciled |
| Unresolved conflict | Scale discrepancy noted above; does not rise to `CONFLICT_FOR_RECONCILIATION` (no explicit contradictory claim, just an approximate mismatch) |
| **Status** | **CONSISTENT_BUT_INCOMPLETE** |

**Domain-confounding flag (T-04 relevant)**: because 026 is 100% `KO_TO_EN` and 025 is mixed-direction, `domain` and `translation_direction` will be **partially confounded** the moment 026 enters the analysis cohort as the sole technology-domain source. This must be visible in the Identifiability Gate (§20.2), not silently absorbed.

## 3. Legacy `한국어-영어 번역(병렬) 말뭉치` ↔ D87 candidate

| Field | Value |
|---|---|
| Official dataset ID | D87, `한국어-영어 번역(병렬) 말뭉치`; web page states 1.6M KO-EN sentences: 1.1M written (news, government web, ordinances, Korean culture) + 0.5M spoken. Perplexity's own gate assessment: **H1/H2/H4 all "NOT YET PASSED"** (aggregate catalogue description only, no confirmed current schema/version/pair-key) |
| Local path/family | `data/raw/aigub/한국어-영어 번역(병렬) 말뭉치/` (10 XLSX workbooks, 10 unique SHA-256) |
| **Quantitative cross-check (new finding, not in either source document alone)** | Local unique-content total = **1,602,418** ≈ web's "1.6 million". Local "spoken" family (구어체×2 + 대화체) = 200,000+200,000+100,000 = **500,000** — matches web's "0.5m spoken" exactly. Local "written" family (뉴스×4 + 한국문화 + 조례 + 지자체웹사이트) = 801,387+100,646+100,298+100,087 = **1,102,418** ≈ web's "1.1m written". This is a materially stronger quantitative correspondence than either source alone established, and upgrades this pairing beyond Perplexity's standalone "NOT YET PASSED" disposition — **for scale/category composition only**, not for schema/version/pair-key, which remain unconfirmed. |
| Record grain | one spreadsheet row = one translation pair |
| Deterministic pairability | `원문`/`번역문` co-present per row → direct pairable. `ID`/`SID` are workbook-scoped only — **127,824 duplicate ID/SID rows** when treated as a global key; 대화체 has no single-column ID at all (`Set Nr.`+`발화자` composite has 8 duplicate rows, not unique either) |
| KO/EN field | `원문` / `번역문` — no column distinguishes which language was the translation source |
| Pair/source key | none reliable beyond `workbook_relative_path + sheet_name + physical_row_number` (data-recon's own recommended deterministic fallback) |
| Translation direction observability | **No `source_language`/`target_language` or original/translated-stage column exists.** Per directive instruction, filename convention alone must not be used to assert direction. |
| Domain/subdomain metadata | 대화체: 5 categories/59 subcategories/2,779 situations (여행/쇼핑, 비즈니스, 일상대화 top); 뉴스: 10-11 publishers + 3-tier auto-classification (many empty); 한국문화: 102 keywords; 조례: 54 municipalities; 지자체웹사이트: 4 municipalities |
| Source metadata | Publisher names for news (국민일보/서울경제/한겨레 etc.); no source/institution label for 구어체/대화체/한국문화/조례/지자체웹사이트 |
| License/acquisition evidence | No license field in any Legacy workbook — translation provenance and license are **UNKNOWN** (worse-documented than 025/026's self-asserted `license` field) |
| Raw-text fidelity | `원문`/`번역문` present with 0 empty rows across all workbooks; no MT/human/edit-stage distinction available at all |
| Duplicate risk | **Low-moderate** — 2,494 duplicate-pair rows out of 1,602,418 (~0.16%) |
| Train/validation overlap | N/A — Legacy has no train/validation split structure |
| Quality/provenance unknown | Annotator/reviewer identity, license, translation workflow (human vs MT vs post-edited) all unknown; official current-version/schema link unconfirmed |
| Web/local consistency | Title matches exactly; scale/category breakdown matches closely (see above); schema/version does not (Perplexity's own disposition) |
| Unresolved conflict | None rising to `CONFLICT_FOR_RECONCILIATION` — the schema/version gap is an absence of evidence on both sides, not a contradiction |
| **Status** | **CONSISTENT_BUT_INCOMPLETE** (stronger on scale, weaker on schema/version/provenance than 025/026) |

**Direct answer to directive's specific ask**: the local/official gap here (strong pairability locally, weak version/schema provenance officially) affects **sensitivity-only status and quality-anchor eligibility, not raw Tier assignment by itself** — see Task 2 §3 below for the reasoning split.

## 4. D71693 — professional conference interpretation/translation

| Field | Value |
|---|---|
| Official dataset ID | D71693, `국제 학술대회용 전문분야 한영/영한 통번역 데이터`; bidirectional KO-EN/EN-KO, 900,572 text sentences + 2,017 hours speech (Perplexity, all gates "NOT YET PASSED") |
| Local path/family | **None found.** Not present among the 3 identified local dataset families (025, 026, Legacy). |
| **Status** | **NOT_ACQUIRED / OUTSIDE_CURRENT_CORPUS** (per directive instruction — no new download proposed or started) → overall reconciliation label: **WEB_ONLY** |

---

# Task 2 — Source Role / Tier Recommendation (HISTORICAL — see D-RD-05 for the approved, binding version)

SSOT §9.3 tier definitions used verbatim:
- **Tier A** — curated/official parallel corpus, 명시적 번역쌍, 안정적 license/metadata
- **Tier B** — benchmark parallel corpus, 연구 benchmark 성격, 규모 작아도 품질 우수
- **Tier C** — web-mined parallel corpus, 대규모 확보용, semantic QC 강화 필요

## 025 / D71265

**Approved by D-RD-05, unchanged from this recommendation, NOT withdrawn (Vice Director reconfirmed 2026-08-16)**: `candidate_source_tier=A`, `research_role=PRIMARY_BACKBONE`, `primary_analysis_eligible=true`. New field: `provenance_closure_status = PENDING_OFFICIAL_SCHEMA_AND_RELEASE_LINK` (official dataSetSn/version/release link still unconfirmed — see grep finding above).

| Field | Value |
|---|---|
| recommended_role | Primary backbone |
| candidate_tier | A |
| confidence | MEDIUM |
| supporting_evidence | Official government-portal (AIHub) curated corpus; least domain-specialized of the three families → best general-language starting population; bidirectional coverage (both KO→EN and EN→KO) |
| blocking_unknown | License self-assertion not externally verified; official dataSetSn/version link not confirmed |

**Explicit ruling requested by directive — duplicate rate vs tier**: the 214,252 duplicate-pair rows / 15.8% train-validation overlap are **downstream QC/D-01 problems, not a reason to demote the Tier**. Tier A/B/C in SSOT §9.3 is about curation/officialness of provenance, not row-level hygiene — every tier can contain duplicates, and SSOT §10.1 already provides the mechanism (hard exclusion of "완전 중복 pair") to handle it at the QC layer. Recommend **keeping candidate_tier=A** and routing the duplicate/overlap problem entirely to Task 3/4 below and to `02_normalize_and_qc`.

**Bidirectional/duplicate distinction requested by directive**: whether 025's high duplicate-pair count reflects TL1/TL2 being direction-mirrored views of an overlapping sentence pool (by design) vs accidental repetition **cannot be determined from this evidence alone** — flagged as an open question in Task 3.

## 026 / D71266

**Approved by D-RD-05, unchanged from this recommendation, NOT withdrawn, with an explicit condition**: `candidate_source_tier=A`, `research_role=PRIMARY_DOMAIN_SUPPLEMENT`, `primary_analysis_eligible=true` — condition: domain-specialized/single-direction structure must stay explicit and 026 must never be pooled with 025 without a labeled stratum (see Identifiability Gate finding in `docs/contracts/G1_PAIR_REGISTRY_PRECONTRACT_v1.md` — 026's `domain=기술과학` is now confirmed near-perfectly confounded with `source=특허정보원`). New field: `provenance_closure_status = PENDING_OFFICIAL_SCHEMA_AND_RELEASE_LINK`.

| Field | Value |
|---|---|
| recommended_role | Domain supplement (**not** a generic backbone) |
| candidate_tier | A |
| confidence | MEDIUM-HIGH |
| supporting_evidence | Official research-institution sourcing (한국연구재단/특허정보원) — arguably stronger institutional provenance signal than 025; very low duplicate/overlap rate; explicit technical/science subdomain structure |
| blocking_unknown | Single-direction-only (KO_TO_EN) — domain/direction confounding risk (see §2 above); scale discrepancy vs web's "1.5M" claim |

**Why not a generic backbone**: 026 is domain-specialized by construction (technical/science) and single-direction; treating it as interchangeable with 025's general-purpose bidirectional population would silently introduce the exact domain-source confounding SSOT T-04 warns against. It must remain a labeled stratum.

## Legacy / D87

| Field | Value |
|---|---|
| recommended_role (historical, as of first draft) | Sensitivity-only candidate |
| candidate_tier (historical, as of first draft) | ~~B (tentative)~~ — **withdrawn by D-RD-05: Research Director ruled Tier B must not be used as a provenance-shortfall fallback category; SSOT Tier B specifically means "benchmark parallel corpus," which Legacy's undocumented construction does not establish.** Approved value: `source_tier = null / UNASSIGNED`. **D-RD-05 itself is NOT withdrawn (Vice Director reconfirmed 2026-08-16)** — this row only reflects that the Tier-B sub-recommendation within it was withdrawn; `research_role=SENSITIVITY_ONLY`/`primary_analysis_eligible=false` stand. New field: `provenance_closure_status = PARTIAL_OFFICIAL_CONSTRUCTION_CONFIRMED_FIELD_AND_RELEASE_LINK_PENDING` (the official D87 catalogue record confirms this corpus's general existence/scale category, per Perplexity's audit — that is the "partial" part — but current field-level schema and a specific release version are not linked; this is a real, distinct status from 025/026's `PENDING_OFFICIAL_SCHEMA_AND_RELEASE_LINK`, reflecting that Legacy has *more* official corroboration on scale/composition than 025/026 do, even though its schema/version confirmation is weaker). Perplexity's own web-audit disposition language (e.g. any "UNASSIGNED"-style gate wording it might use) is a **separate WEB-track status and must never overwrite this LOCAL/policy-track `candidate_tier` field** — see the WEB/LOCAL separation note above. |
| confidence | LOW-MEDIUM |
| supporting_evidence | Clean, structured, consistently-schema'd XLSX across all 10 workbooks (not a noisy web scrape); strong quantitative match to the official 1.1M/0.5M written/spoken breakdown |
| blocking_unknown | No license field at all; no translation-stage/annotator provenance; official current-version/schema link unconfirmed (Perplexity: all gates NOT YET PASSED) |

**Three-way distinction the directive asked for (original reasoning, tier conclusion superseded above)**:
- **Tier assignment**: **superseded** — see D-RD-05: `source_tier = null/UNASSIGNED`, not B.
- **Sensitivity-only status**: **still approved** (`research_role = SENSITIVITY_ONLY`, `primary_analysis_eligible = false`) — pairability is real but provenance/version is not officially anchored.
- **Quality-anchor status**: **not recommended**, unchanged — no documented QA/construction manual has been inspected for Legacy.

## D71693

| Field | Value |
|---|---|
| recommended_role | N/A |
| candidate_tier | **NOT_ACQUIRED / OUTSIDE_CURRENT_CORPUS** |
| confidence | N/A |
| supporting_evidence | N/A |
| blocking_unknown | No local raw data exists; no acquisition proposed here |

---

See `docs/research/PAIR_IDENTITY_AND_DUPLICATE_CONTRACT_v1.md` for the duplicate/overlap semantic design (Task 3/4), and `docs/research/G1_DECISION_QUEUE_v1.md` for which of the open items above require Research Director decision vs can wait for Raw EDA.
