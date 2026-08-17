# KOEN G4 — Corrected Morphology Manual Audit Final Adjudication

> **Adjudicator**: Claude-B (Research / Statistics / Gate Steward)
> **Date**: 2026-08-17
> **Adjudicated HEAD**: `2e63359224c690972dbe681895e079d6aac2e7cc` (= `origin/main`)
> **Authority order**: `KOEN-TP-RS-001` (SSOT) → approved redline → `RD-20260817-D02D03-CONFORMANCE-01` → `configs/morphology_v1.yaml` → execution evidence
> **Decision reference**: `ssot/2026-08-17_1445_KOEN_TP_D02_D03_CONFORMANCE_EXECUTION_DECISION_LOG.md`

No raw KO/EN sentence text, no morpheme surface sequence, and no workbook cell content is reproduced
in this document (repository hygiene policy, consistent with OPS-DR-01 and the G1 adjudication).
Only `pair_id`, counts, categorical labels, hashes and aggregate distributions are recorded.

---

## 1. Completed workbook identity

```
path   : ssot/HumanLebeled/[HUMAN_confirmed1606]_MORPHOLOGY_AUDIT_100_v001.xlsx
size   : 39,782 bytes
mtime  : 2026-08-17 16:06:07 +0900 KST
SHA-256: 5f6dd073554582227ab781a084fe6e1c144617c0a42ef1335a4c4491b023dca1
sheets : audit (101×5) · 참고_메트릭 (101×20) · 기준 (14×2) · X_재판정 (1×8, header only)
git    : IGNORED by .gitignore:57 (*.xlsx) — never committed (contains raw KO text)
```

The blank/request workbook is a **different artifact and was not used**:

```
ssot/HumanLebeled/MORPHOLOGY_AUDIT_100_v001/[HUMAN]_MORPHOLOGY_AUDIT_100_v001.xlsx
SHA-256: 06446b1c91ea291e7e8cc84e0e46ccbca5e1f296485c6d7f2d404f2f68687f7e
mtime  : 2026-08-17 15:12:39 +0900 KST
```

The two SHA-256 values differ, and the completed workbook's mtime (16:06) is consistent with the
`confirmed1606` filename marker. Identity is established by hash, not by filename.

## 2. Sample identity validation

```
sampling key: outputs/manual_audit/MORPHOLOGY_AUDIT_100_SAMPLING_KEY_v001.csv
workbook rows            = 100     workbook distinct pair_id = 100
sampling key rows        = 100     key distinct pair_id      = 100
workbook − key           = 0
key − workbook           = 0
PAIR-ID SET EQUALITY     = TRUE
```

Row order was not used as a criterion. `DIRECTOR_AUDIT_IDENTITY_VALIDATED`.

## 3. First-pass completeness

```
N reviewed   = 100 / 100  (complete)
O            = 94   (94.0%)
X            = 6    (6.0%)
blank        = 0
invalid label= 0
```

Canonicalisation applied: whitespace trim only. No inference, no substitution.

**Interpretation boundary.** The 6 % X rate is **not** a population morphology error rate and must
not be reported as one. The N=100 frame deliberately over-samples domain coverage, metric extremes,
structural stress, punctuation-heavy rows, length strata and irregular-affix examples
(`has_irregular_affix = TRUE` in 4 of 100 rows against a population-scale incidence far below that).

## 4. Second-look status

```
SECOND_LOOK_NOT_STRUCTURALLY_RECORDED
SECOND_LOOK_NOT_REQUIRED_FOR_THIS_ADJUDICATION
```

The `X_재판정` sheet contains a header row and **zero** data rows, and the `audit` sheet carries a
single `O/X` column with no dedicated final-adjudication column. The `confirmed` filename marker was
therefore **not** accepted as evidence of a completed second look.

No additional human work is requested, because a second look could not change this adjudication:
the first pass is 100 % complete with zero blanks and zero invalid labels, and Claude-B independently
reviewed **all six** X rows in full (§5), finding zero implementation defects. Under §6 of the
governing directive none of the six belongs to a blocker class.

## 5. X row mechanism review (all 6 reviewed by Claude-B)

| # | pair_id | stratum | sample_reason | mechanism | bucket impact |
|---|---|---|---|---|---|
| 21 | `pair_0008a76a6b7ed2d5030ac0cc6f0853b7c9c7985a0d69972786962a7e697bcdfc` | 025 / KO_TO_EN / general / Q1 | `A_domain_general` | **ANALYZER_LIMITATION** — OOV colloquial neologism tagged `NNP`; contracted copula+final-ending analysed as a single `EC` | none (stays in `E*`) |
| 47 | `pair_0003f3844de2e14d74faeba07ac582e325a47ac983489adf5fd26e152fee84c8` | 025 / UNKNOWN / dialogue / Q1 | `D_direction_fill_UNKNOWN` | **NATURAL_AMBIGUITY** — `EF`/`EC` boundary on a comma-joined clause | none (stays in `E*`) |
| 49 | `pair_000c668d8baef52d4f748acaf3073c9f3410cc31b38e0ace8fe7fe311fd1b540` | 026 / KO_TO_EN / other / Q5 | `B_morpheme_count_top` | **ANALYZER_LIMITATION** — subject particle after a percentage token re-analysed as a verb stem + connective ending | 1 morpheme of 74 moves `particle`→`ending` (1.4 % of that row) |
| 75 | `pair_000e1a1688cdf16ce3999b6c97f17a83718bd90f39fa3b7ed1b495e9e92d807d` | 025 / KO_TO_EN / general / Q1 | `B_density_top` | **ANALYZER_LIMITATION** — repeated 1-eojeol interjection re-analysed as pronoun+genitive ×3 | spurious `particle_count = 3` |
| 80 | `pair_0005d3169b4b3f4c16194c11f7a72dd6af9e06d175b30b57dc0524d8749b04d6` | 025 / KO_TO_EN / general / Q1 | `C_punctuation` | **ANALYZER_LIMITATION** — 1-eojeol interjection analysed as copula + final ending | none material |
| 92 | `pair_0001107486f843e06468b97b40434702fe58654cb93284eb7a0b1d637ad51cf3` | 025 / KO_TO_EN / general / Q1 | `B_particle_top` | **ANALYZER_LIMITATION** — 1-eojeol interjection tagged as vocative particle `JKV` | spurious `particle_count = 1` |

```
ANALYZER_LIMITATION   = 5
NATURAL_AMBIGUITY     = 1
IMPLEMENTATION_DEFECT = 0
MEASUREMENT_WARNING   = 0
OTHER                 = 0
```

**Pattern.** Four of six (rows 21, 75, 80, 92) are ultra-short, quote-marker-prefixed dialogue
fragments of 1–2 eojeol in `length_stratum = Q1`. This is a coherent, bounded region, not a
mechanism defect. It is the same short-length instability region already characterised in
`REPRESENTATION_EDA_MANIFEST_v001` (`pair_codepoint_ratio` Tukey outlier rate Q1 9.20 % → Q5 0.05 %).

**Carried caveat for G4 / NB07 (not a blocker).** Both pilot-v002 maxima —
`morpheme_density = 8.0` and `particle_ratio = 0.375` — originate from row 75, i.e. from an analyzer
artefact on a single-eojeol interjection. Extreme values of the morphology features in the Q1
ultra-short region may be analyzer artefacts rather than linguistic signal, and must be handled as
such in distributional reporting and in any extreme-case audit panel.

## 6. Systematic implementation defect verdict

```
SYSTEMATIC_IMPLEMENTATION_DEFECT = NO
```

Claude-B mechanically re-derived every audited construct from the workbook's own stored morpheme
sequence, independently of the pipeline that produced it, over all **100** rows:

| construct | check | violations |
|---|---|---|
| C — eojeol denominator | `eojeol_count == len(ko_text.split())` | **0** |
| D — count ↔ sequence | `morpheme_count == len(sequence)` | **0** |
| E — particle bucket | `particle_count == Σ base_tag startswith "J"` | **0** |
| F — ending bucket | `ending_count == Σ base_tag startswith "E"` | **0** |
| G — deriv-affix bucket | `deriv_affix_count == Σ base_tag ∈ {XSN,XSV,XSA}` (incl. `XSA-I`) | **0** |
| §13.6 density | `morpheme_density == morpheme_count / eojeol_count` | **0** |
| §13.7 ratios | each `ratio == count / morpheme_count` | **0** |
| function-morpheme ratio | `== (particle+ending) / morpheme_count` | **0** |
| H — warning mechanism | `analysis_warning_flag ⟺ morpheme_count == 0` | **0** |

Irregular-affix coverage in the audit sample: 4 rows carry `XSA-I`, all four counted as derivational
affixes, matching the 4 rows declared `has_irregular_affix = TRUE` in the sampling key. Variant tag
inventory observed across the 100 rows: `VA-I` 7, `VA-R` 1, `VV-I` 2, `VV-R` 2, `XSA-I` 4.

None of the §6 blocker classes is present: no systematically wrong denominator, no sequence/count
mismatch, no POS bucket implementation error, no silent warning failure, no pair-output alignment
corruption.

## 7. D-02 acceptance result — `REP_FEATURES_v002`

Independently verified by Claude-B against the artifact, not against the producer's manifest.

| # | criterion | observed | verdict |
|---|---|---|---|
| D2-1 | `row_count = distinct pair_id = 3,835,988` | 3,835,988 / 3,835,988 | **PASS** |
| D2-2 | pair-id **set** equality with v001 | `v001−v002 = 0`, `v002−v001 = 0` | **PASS** |
| D2-3 | 47 v001 columns preserved, exact values | 46 non-key columns compared over the **full population**, mismatch rows = **0**; all 47 v001 names present in v002 | **PASS** |
| D2-4 | `ko_eojeol_count` present, non-null, > 0 | null = 0, min = 1, max = 158, mean = 10.951 | **PASS** |
| D2-5 | `en_word_count` present, non-null, > 0 | null = 0, min = 1, max = 331, mean = 16.856 | **PASS** |
| D2-6 | segmentation rule documented | `rep_lexical_v002`, split `\s+` (`regex==2026.7.19` VERSION1), prohibited-normalisation list, `lexical_rule_sha256 = c1dc9dc7…45b8c`. Independently recomputed by Claude-B on a deterministic 1 % sample (n = 38,049): **0 mismatches** | **PASS** |
| D2-7 | artifact hash / lineage | `sha256 = dfae8e01cd3fe2ca949d8754678e508203ad1a7aa6abea418008a33ac650d309`, `schema_sha256 = 76894e4e…2ad68`, 49 columns, v001+registry input hashes recorded | **PASS** |
| D2-8 | v001 retained as historical | `recomputed_v001_features = false`; v001 parquet and manifest intact | **PASS** |

Cross-checks additionally reported and confirmed: `g1_excluded_present = 0`,
`ko_eojeol_ne_spacerun_plus1 = 0`, `en_word_ne_spacerun_plus1 = 0`, `*_gt_codepoints = 0`.

```
D-02 CONFORMANCE = PASS   (REP_FEATURES_v002 is the canonical successor; v001 is historical)
```

G2 Representation Integrity is **not** claimed here.

## 8. M1–M5 acceptance result

| ID | criterion | evidence at `2e63359` | verdict |
|---|---|---|---|
| **M1** | `morpheme_density = morpheme_count / eojeol_count`; codepoint denominator removed from the API | `morphology.py` density expression and `morpheme_density_denominator = "eojeol_count"`; the only remaining `codepoint_count` occurrences are a changelog docstring and a **negative** test asserting the old keyword argument is now rejected | **PASS** |
| **M2** | base-tag normalisation `tag.partition("-")[0]`; `XSA-I/R` counted; `J*`/`E*` unchanged | `base_tag()` + `classify_tag()`; regression tests cover `XSA-I`, `XSA-R`, `XSV-I`, `XSN-R` and J/E invariance (`JKS-X`, `EF-Y`); real-Kiwi test asserts an `XSA-*` tag is emitted and counted | **PASS** |
| **M3** | full D-03 field set incl. `morpheme_sequence` as `list<struct<form,pos>>` | 19-column schema carries `morph_measurement_id`, `analyzer_config_hash`, `morpheme_sequence`, all four counts, `analysis_warning_flag` (+ `analysis_warning_reason`, beyond contract) | **PASS** |
| **M4** | zero analyzer output keeps the pair, sets the flag, yields **null** ratios | silent `denominator = 1` removed; the four `morpheme_count`-denominated ratios are **nullable** in the schema while `morpheme_density` is `not null` (eojeol > 0 always); `zero_morpheme_policy` recorded in the config hash | **PASS** |
| **M5** | no `3_836_013` literal; population derived from input | zero occurrences in `src/`, `scripts/`; a guard test asserts the literal is absent | **PASS** |

`M6` is closed by §7 (D2-4 / D2-5).

## 9. Corrected pilot v002 result

`.runtime/nb04-pilot-v002/MORPH_FEATURES_PILOT_v002.parquet` ·
`sha256 = d4a31a79ea5beaf37a70a1dc64540d4eb8158dfdcda9193c1287c555797ba733` ·
`morphology_config_sha256 = 6f48802a07d984cab18c5cf6c1df2a3e3e778f1825dd0be17438d3d4fb48f23d`

```
N = 1,000     distinct pair_id = 1,000     same pair set as superseded v001 = TRUE
zero_morpheme = 0   analysis_warning rows = 0   null particle_ratio = 0   min eojeol_count = 1
analyzer: kiwipiepy 0.23.2 / model 0.23.0 / no user dictionary / no domain dictionary / top_n = 1
```

Claude-B's frozen M2 expectations, **recomputed independently from the two parquet artifacts**
(v001 counts reconstructed as `round(ratio × morpheme_count)` since v001 did not persist counts):

| expected | value | observed | match |
|---|---:|---:|---|
| `particle_count` changed rows | 0 | 0 | ✔ |
| `ending_count` changed rows | 0 | 0 | ✔ |
| `XSA-I` occurrences | 8 | 8 | ✔ |
| `deriv_affix` total (old) | 1,692 | 1,692 | ✔ |
| `deriv_affix` total (corrected) | 1,700 | 1,700 | ✔ |
| changed pair rows | 8 | 8 | ✔ |

```
6 / 6 EXACT MATCH
```

Additional invariants confirmed by Claude-B: `morpheme_count` changed rows = 0;
`len(morpheme_sequence) ≠ morpheme_count` rows = 0; `morpheme_density ≠ morpheme_count/eojeol_count`
rows = 0. `morpheme_density` changed in all 1,000 rows, which is the expected and required
consequence of the §13.6 denominator correction.

`MORPH_FEATURES_PILOT_MANIFEST_v001.json`, the v001 pilot parquet (`41a28f44…`) and the 85-row
`MORPHOLOGY_SANITY_AUDIT_SAMPLE.json` remain `SUPERSEDED_BY_CONFORMANCE_DEFECT` and may not be cited
as G4 evidence.

## 10. Execution equivalence result

Selected engine: `num_workers = 24`, `analysis_batch = 2500`, `arrow_write_batch = 2500`,
`checkpoint_part_rows = 50,000`.

```
stage A comparisons  =  35,000
stage B comparisons  = 240,000
TOTAL                = 275,000

mismatch rows          = 0
sequence mismatch rows = 0
POS mismatch rows      = 0
mismatch_fields        = {}       (no derived field differs)
```

The selected configuration's own equality gate is evidenced at stage B
(`num_workers = 24`, `analysis_batch = 2500`, compared_rows = 20,000, all mismatch counters 0,
status `ACCEPTED`). The final 100,000-row stage measures sustained throughput only and re-runs no
equality check; its configuration is identical to the stage-B-verified one.

Invariants held constant across the scalar reference path and the optimized path: kiwipiepy 0.23.2,
model 0.23.0, analyzer configuration hash, dictionary policy (none), input field `ko_text_analysis`,
`top_n = 1`. Comparison was `pair_id`-keyed, so result-to-pair alignment under multiworker dispatch
is positively evidenced rather than assumed.

```
EXECUTION_EQUIVALENT_OPTIMIZATION = PASS
```

## 11. Memory safety result

| metric | selected config (final stage) | selected config (stage B) | corrected pilot v002 |
|---|---:|---:|---:|
| peak RSS | 0.845 GiB | 1.081 GiB | 0.751 GiB |
| min mem available | 9.167 GiB | 9.003 GiB | 9.104 GiB |
| peak swap delta | 0.0 MiB | 0.0 MiB | 0.0 MiB |
| swap in / out pages | 0 / 0 | 0 / 0 | 0 / 0 |
| worst status | GREEN | GREEN | GREEN |

`throttle.verdict = NO_THROTTLE_DETECTED`; sustained/first-decile ratio 1.428 (no degradation).
Peak RSS is far inside the memory envelope Claude-B froze for this WSL host (15.34 GiB total,
≈ 9–10 GiB available, one heavy job at a time). The architecture is bounded-memory: per-chunk
analyse → RecordBatch → streaming Parquet part write → release.

```
MEMORY_SAFE_EXECUTION_CONFIG = PASS
```

**Canonical ETA.** Derived from the final selected end-to-end benchmark, not from the superseded
scalar figure:

```
sustained end-to-end  = 24,122.9 rows/sec
final cohort N        = 3,835,988
optimized ETA         ≈ 2.7 min
measured scalar ETA   ≈ 22.5 min   (speedup 8.5×)
prior 151.2 min       = historical artefact of the superseded pilot; not a baseline for selection
```

## 12. Authorization

All gating conditions are satisfied:

```
D-02 conformance ................ PASS
M1–M5 ........................... PASS
corrected pilot v002 ............ PASS (6/6 exact)
Director N=100 audit complete ... PASS (100/100, O=94 / X=6)
systematic implementation defect  NO
execution equivalence ........... PASS (275,000 comparisons, 0 mismatch)
memory safety ................... PASS (peak RSS ≤ 1.1 GiB, swap delta 0)
```

```
MORPHOLOGY_SANITY_REVIEW_PASS
MORPHOLOGY_FULL_RUN_AUTHORIZED
```

Scope of this authorization: the full-population D-03/D-04 morphology run over the final cohort
`N = 3,835,988`, using the frozen analyzer (kiwipiepy 0.23.2 / model 0.23.0 / no dictionary /
`top_n = 1`), the corrected `morph_v002` rules, and the benchmarked engine configuration recorded in
§10, consuming `REP_FEATURES_v002` for `ko_eojeol_count`.

**This is not G4 PASS.** `MORPHOLOGY_FULL_RUN_AUTHORIZED ≠ G4 PASS`. G4 Morphology Integrity will be
adjudicated only after the full 3,835,988-row artifact exists, against population failure rate,
artifact hash and lineage, full feature distributions, analyzer/version/config provenance, and this
manual audit evidence — and will be issued together with G2 Representation Integrity and G3
Tokenizer Integrity.

## 13. Non-blocking items recorded for A

1. **Repository hygiene.** `ssot/HumanLebeled/MORPHOLOGY_AUDIT_100_v001/[HUMAN_confirmed1606]_MORPHOLOGY_AUDIT_100_v001.xlsx:Zone.Identifier`
   is untracked and **not** matched by the `*.xlsx` ignore rule. It is a Windows NTFS alternate-data-stream
   marker carrying no research content, but it should not enter the repository.
2. **Q1 extreme-value caveat.** Carry §5's caveat into the full-run distribution report and into any
   extreme-case audit panel: the morphology feature maxima in the ultra-short Q1 region can be
   analyzer artefacts.
3. **Second-look record.** If the Director intends the N=100 first pass to be final, recording that
   explicitly (a filled `X_재판정` sheet or an equivalent marker) would remove the structural
   ambiguity noted in §4 for future audits.

---

**Adjudication closed**: 2026-08-17, Claude-B (Research / Statistics / Gate Steward).
**Adjudicated HEAD**: `2e63359224c690972dbe681895e079d6aac2e7cc`
**Next checkpoint**: full Kiwi population run → then G2 / G3 / G4 joint adjudication → NB06.
