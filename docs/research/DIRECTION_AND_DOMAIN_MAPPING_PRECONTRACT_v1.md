# Translation Direction & Domain Mapping — Pre-G1 Precontract (v1)

**Status (2026-08-16): APPROVED by Research Director as D-RD-06 (direction) and D-RD-07 (domain).** These are no longer drafts pending Raw EDA — `eda/g0-raw-notebooks@a55b86d` has since reported the actual enumerated domain labels for all three families (025: 해외영업/일상생활/해외고객과의채팅; 026: 기술과학/세계/경제/정치/기후), incorporated below. Subdomain-level mapping remains intentionally unmapped — subdomains are preserved as raw metadata only, by design, not because evidence is pending. See `docs/research/G1_APPROVED_DECISIONS_2026-08-16.md` for the compact decision record.

## Task 5 — Translation Direction Mapping Contract

SSOT taxonomy (fixed): `KO_TO_EN | EN_TO_KO | HUMAN_PARALLEL_UNKNOWN | UNKNOWN`

### Rule for JSON corpora (025, 026)

Provenance signals available per data-recon: `source_language`, `target_language`, `ko_original` (present only in 한→영 files), `en_original` (present only in 영→한 files). Data-recon confirmed `source_language`/`target_language` values are **consistent with file direction** in the observed data.

```text
IF en_original present AND source_language/target_language consistent with EN→KO:
    translation_direction = EN_TO_KO

IF ko_original present AND source_language/target_language consistent with KO→EN:
    translation_direction = KO_TO_EN

IF source_language/target_language present but neither ko_original nor en_original present:
    → fall back to filename/folder direction convention (영한/한영) as a WEAKER signal only
    → flag translation_direction_review_flag = true

IF source_language/target_language CONTRADICTS ko_original/en_original presence:
    translation_direction = UNKNOWN
    → route to manual review, do not silently pick one side
```

Applied to observed local data: 025 TL1/VL1 (영한 files) → `EN_TO_KO`; 025 TL2/VL1(한영) → `KO_TO_EN`; 026 (한영 only) → 100% `KO_TO_EN`, no reverse-direction subset exists.

### Rule for Legacy XLSX

No `source_language`/`target_language` column, no `ko_original`/`en_original` staging field exists in any of the 10 workbooks. Per directive instruction, filename convention alone (e.g., inferring direction from a workbook's topic name) must **not** be used to assert direction.

```text
Legacy 원문/번역문 rows → translation_direction = UNKNOWN
```

**D-RD-06 (approved, supersedes this document's earlier recommendation)**: use plain `UNKNOWN`, **not** `HUMAN_PARALLEL_UNKNOWN`. The earlier draft reasoned that 원문/번역문 column naming alone was sufficient evidence of "unambiguously human-parallel, direction merely unrecorded" — the Research Director ruled current evidence does not support that inference: without any translation-workflow/annotator documentation, "human parallel" itself is an unverified assumption, not just the direction within it. `HUMAN_PARALLEL_UNKNOWN` may be used later **only if** official construction documentation explicitly confirms human-parallel-translation methodology for this corpus.

## Task 6 — Domain Mapping Precontract (APPROVED — D-RD-07)

SSOT taxonomy (fixed): `general | administration | legal | news | technology | education | dialogue | other`

**Principles** (all four are binding, unchanged by approval):
1. Preserve the source's raw label (`domain_raw`, `subdomain_raw`) unmodified alongside the canonical `domain` field — never overwrite raw labels, including literal-string variants like "크라우드 소싱" vs "크라우드소싱" in 025.
2. `domain` (canonical) is a separate, additional field — not a renaming of the raw label.
3. When mapping confidence is low, map to `other` rather than forcing a fit.
4. Never conflate `source_id` and `domain` — a single source can span domains and a domain can span sources; do not let one stand in for the other (this is exactly the confounding SSOT T-04 and the Identifiability Gate §20.2 are designed to catch). **This is not theoretical**: `eda/g0-raw-notebooks` confirms 026's `domain=기술과학` (train 319,551 + valid 40,359) is numerically identical to `source=특허정보원` (train 319,551 + valid 40,359) — a **near-perfect confound**, see `docs/contracts/G1_PAIR_REGISTRY_PRECONTRACT_v1.md` §Identifiability Gate.

### Approved mapping table (top-level domain → canonical `domain`; subdomains stay raw-only)

| Corpus | Raw top-level domain label (with observed scale) | Canonical `domain` (D-RD-07) |
|---|---|---|
| 025 | 일상생활 (train 849,856 across directions) | `general` |
| 025 | 해외고객과의채팅 (train 510,232 across directions) | `dialogue` |
| 025 | 해외영업 (train 1,040,219 across directions) | `other` |
| 026 | 기술과학 (train 319,551 + valid 40,359 — **= source 특허정보원 exactly**) | `technology` |
| 026 | 세계 (train 400,123 + valid 49,818) | `other` |
| 026 | 경제 (train 240,439 + valid 29,705) | `other` |
| 026 | 정치 (train 160,064 + valid 20,175) | `other` |
| 026 | 기후 (train 79,967 + valid 9,961) | `other` |
| Legacy | 구어체 | `general` |
| Legacy | 대화체 | `dialogue` |
| Legacy | 뉴스 | `news` |
| Legacy | 한국문화 | `other` |
| Legacy | 조례 | `legal` |
| Legacy | 지자체웹사이트 | `administration` |

Both boundary cases previously flagged (한국문화 vs `general`/`other`; 조례 vs `legal`/`administration`) are **resolved by D-RD-07** as shown above (한국문화→`other`, 조례→`legal`). No further Director input needed on these two.

**Subdomain values are never mapped to canonical form** — 025's 11 subdomains (e.g. 도소매유통, 여행, 음식, 구매, 예약, "숙박,음식점", 정보통신, "연구개발,과학기술", "금융,보험", "기계장비,의료정밀", 부동산) and 026's 15 subdomains (e.g. IT, 빅데이터, 인공지능, 산업경제, 경제일반, 국제기구, 국제통상, 사회_의료, 사회_환경, 문화_문화재, 문화_예술, 정치일반, 국방외교, 북한, 기후) are retained exclusively as `subdomain_raw` — per directive: "subdomain은 별도 raw metadata로 우선 보존."

**New finding surfaced during this update (not previously visible)**: 025's `EN_TO_KO` validation split is **100% domain=해외영업** (all 150,038 valid rows), whereas `EN_TO_KO` training is mixed across all 3 domains. This is a direction×domain×split structural asymmetry, not just the direction×domain confound already noted — flagged for the Identifiability Gate alongside the 026 confound.
