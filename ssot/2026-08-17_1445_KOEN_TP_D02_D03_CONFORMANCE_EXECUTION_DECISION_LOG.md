# KO-EN Tokenization Premium — D-02 / D-03 SSOT Conformance Restoration: Execution Decision Log

> **Snapshot:** 2026-08-17 14:45 KST
> **Decision ID:** `RD-20260817-D02D03-CONFORMANCE-01`
> **Project:** Korean–English Tokenization Premium
> **Authority SSOT:** `KOEN-TP-RS-001` — `Korean_English_Tokenization_Premium_Research_Spec_v1.0`
> **Canonical project root:** `/home/sieg/projects-wsl/Tokenization_KOEN`
> **Canonical remote:** `https://github.com/Siegfriex/Tokenization_Premiun_KOEN.git`
> **Trigger HEAD:** `a8e583ad268879697954e0d19ec9d626f8b7ba08`
> **Prepared by:** Claude-A (Data / Engineering Execution Steward)
> **Final authority:** Research Director

---

## 0. Classification

```
SSOT_CONFORMANCE_RESTORATION
```

This decision is **not**:

```
SSOT_CHANGE
NEW_ESTIMAND
NEW_ANALYZER
NEW_RESEARCH_DESIGN
CHANGE_REQUEST
```

No RQ, estimand, outcome definition, tokenizer, analyzer, QC rubric, seed, or Gate criterion is
altered. The frozen SSOT text and the frozen machine-readable contract
`configs/morphology_v1.yaml` are treated as correct; the **implementation had drifted from them**,
and this decision restores the implementation to the already-frozen contract.

Evidence that the contract itself was never in doubt: `configs/morphology_v1.yaml`
(`measurement_schema_ref.fields`, committed at `a609c63`) already enumerates every D-03 field that
the current implementation omits. The drift is one-sided — code, not contract.

---

## 1. Trigger

Claude-B's conformance review raised six findings (`M1`–`M6`) against the D-02 representation layer
and the D-03 morphology layer.

The immediately preceding commit on `main`:

```
a8e583a  explore(rep): add final-cohort representation diagnostics
```

was authored **before** the morphology conformance directive was issued. Its diff is EDA-only:

```
$ git diff cc6fb979 a8e583ad --name-only
notebooks/exploratory/03_representation_feature_diagnostics.ipynb
outputs/manifests/REPRESENTATION_EDA_MANIFEST_v001.json
```

It therefore **did not and could not** have repaired any of `M1`–`M6`. Before any edit was made,
each finding was re-proved directly against the current `main` tree.

---

## 2. Current-head defect confirmation

```
CURRENT_HEAD_CONFORMANCE_DEFECTS_CONFIRMED
```

Verified against `HEAD = a8e583ad268879697954e0d19ec9d626f8b7ba08`.

| ID | Finding | SSOT reference | Direct evidence at current HEAD | Verdict |
|---|---|---|---|---|
| **M1** | `morpheme_density` denominator is codepoint count, not eojeol count | §13.6: `MorphemeDensity_KO = MorphemeCount_KO / EojeolCount_KO` | `morphology.py:44` `"morpheme_density_denominator": "ko_codepoint_count"`; `morphology.py:117` `morpheme_count / codepoint_count`; `morphology.py:76` parameter is `codepoint_count` | **CONFIRMED** |
| **M2** | Derivational-affix mapping is exact-match and misses irregular tag families | §12.3: `Derivational affix: XSN, XSV, XSA` | `morphology.py:49` `_DERIV_AFFIX_TAGS = frozenset({"XSN","XSV","XSA"})`; `morphology.py:110` `elif tag in _DERIV_AFFIX_TAGS`. Empirically, Kiwi 0.23.2 emits `XSA-I` for ordinary text — `학생답게`→`('답','XSA-I')`, `사랑스럽다`→`('스럽','XSA-I')`, `어른스럽다`→`('스럽','XSA-I')`. All are silently dropped from `deriv_affix_count`. | **CONFIRMED** |
| **M3** | D-03 required schema fields absent from the canonical output | §12.3 D-03 field table; mirrored in `configs/morphology_v1.yaml:measurement_schema_ref.fields` | `morph_features_schema()` (`morphology.py:136–150`) emits 11 columns and omits `morph_measurement_id`, `analyzer_config_hash`, `morpheme_sequence`, `particle_count`, `ending_count`, `deriv_affix_count`, `analysis_warning_flag` | **CONFIRMED** |
| **M4** | Zero-morpheme rows get a silent denominator substitution | §13.7 ratios are defined over `MorphemeCount`; SSOT §11.2 forbids silent normalization | `morphology.py:114` `denominator = morpheme_count if morpheme_count > 0 else 1`, producing ratios of exactly `0.0` that are indistinguishable from a genuine zero-ratio analysis | **CONFIRMED** |
| **M5** | Superseded population constant hardcoded | Final cohort `N = 3,835,988` per `KOEN_G1_HUMAN_AUDIT_FINAL_ADJUDICATION.md` §7 | `morphology.py:250` `per_pair_latency_sec * 3_836_013`; `morphology.py:273–275` manifest keys literally named `projected_full_population_3836013_rows_*` | **CONFIRMED** |
| **M6** | D-02 lexical-length variable group missing | §12.2: `lexical length | ko_eojeol_count, en_word_count` | `rep_features_schema()` yields 47 fields; neither `ko_eojeol_count` nor `en_word_count` is present | **CONFIRMED** |

Two additional engineering defects were observed while proving the above. They are recorded here
because they block the authorized full run, not because they are new research findings:

| ID | Finding | Evidence |
|---|---|---|
| **E1** | Unbounded memory architecture | `morphology.py:226` `records = []` accumulates every row before a single write; at N = 3,835,988 with full `morpheme_sequence` retention this is not viable |
| **E2** | Scalar analyzer loop forgoes Kiwi's native parallelism | `morphology.py:227–237` calls `analyzer.analyze(single_string)` per pair. `Kiwi.analyze` accepts `Iterable[str]` and, per its own documentation, dispatches multithreaded work using the `num_workers` given at construction — the scalar path cannot reach it |

---

## 3. Research Director decisions

### RD-A — Complete D-02 to the SSOT text

`D-02 Representation Features` shall carry the SSOT §12.2 `lexical length` variable group.

### RD-B — Persist full sequences

D-03 `morpheme_sequence` and D-04 token ID arrays shall be stored in full for the entire
population, as **local canonical artifacts** (`data/registry/**`, already `.gitignore`-protected;
never committed to the public repository).

### RD-C — Execution flow

```
Representation conformance fix (REP_FEATURES_v002)
        ↓
Morphology corrected pilot (v002)
        ↓
Director manual morphology audit (N = 100)
        ↓
Claude-B re-adjudication
        ↓
resource-safe Full Kiwi + Full o200k
```

### RD-D — Runtime reduction under exact-equality precondition

Kiwi wall-clock shall be reduced as far as achievable, **conditional on exact equality of research
output semantics**. Any optimization candidate that changes a single analysed field is rejected
regardless of its speed.

### RD-E — Visualization lane

Visualization is delegated to a separate agent lane and is out of scope for this execution.

---

## 4. Operational clarification — eojeol / word counting rule

No higher authoritative operational rule for `ko_eojeol_count` / `en_word_count` exists in the SSOT,
the approved redline, or any frozen config; §12.2 names the fields without defining the
segmentation. The Director clarification adopted is therefore:

```
ko_eojeol_count
= number of non-empty orthographic segments obtained by splitting
  ko_text_analysis on Unicode whitespace

en_word_count
= number of non-empty surface segments obtained by splitting
  en_text_analysis on Unicode whitespace
```

Explicitly prohibited, consistent with SSOT §11.2 (금지되는 무음 정규화):

- normalizing or collapsing the source text before counting
- punctuation stripping
- NFKC folding
- lowercasing

In the accepted final cohort a count of `0` is `HARD_INVALID`.

This is an operational elaboration of an already-frozen SSOT field, recorded so the segmentation is
reproducible — not a new research variable.

---

## 5. Artifact lineage

| Stage | Artifact | Disposition |
|---|---|---|
| Preserved | `data/registry/REP_FEATURES_v001.parquet` — N = 3,835,988, SHA `335c20de…f819e45` | Immutable. The 47 existing features are **not** recomputed. |
| New | `data/registry/REP_FEATURES_v002.parquet` | v001 columns carried through by exact `pair_id` join + newly computed native D-02 fields only |
| New | `outputs/manifests/REP_FEATURES_MANIFEST_v002.json` | tracked |
| New | `data/registry/MORPH_FEATURES_PILOT_v002` (runtime) | corrected pilot |
| New | `ssot/HumanLebeled/[HUMAN]_MORPHOLOGY_AUDIT_100_v001.xlsx` | **local only — contains raw KO text; must never be committed** |
| New | `outputs/manual_audit/MORPHOLOGY_AUDIT_100_SAMPLING_KEY_v001.csv` | machine key, aggregate/id only |

`PAIR_REGISTRY_v002.parquet` (SHA `95f523d1…c426010bec52`) is read-only input throughout.

---

## 6. Gate impact

| Gate | Impact |
|---|---|
| G0 | None. Design freeze untouched. |
| G1 | None. `G1 = PASS` and the bounded 25-pair exclusion stand; the final cohort remains N = 3,835,988. |
| G2 — Representation Integrity | Not yet claimed. `REP_FEATURES_v002` is a prerequisite for a G2 adjudication that can honestly assert §12.2 field completeness. |
| G3 — Tokenizer Integrity | Unblocked but not entered; full o200k remains deferred. |
| G4 — Morphology Integrity | Directly affected. G4 requires `POS mapping table freeze` and `sample manual inspection`; `M2` means the previously frozen mapping was **not** faithfully implemented, and the N = 1,000 pilot plus its 85-row sanity sample were produced under the defective mapping. Both are superseded. |
| G5 / G6 | Not entered. |

**Consequence for prior evidence.** `MORPH_FEATURES_PILOT_MANIFEST_v001.json`, the pilot parquet
(SHA `41a28f44…`), and `MORPHOLOGY_SANITY_AUDIT_SAMPLE.json` (85 rows) are hereby marked
`SUPERSEDED_BY_CONFORMANCE_DEFECT`. They are retained as historical execution evidence and are
**not** deleted, but they may not be cited as G4 evidence. Claude-B's morphology review must be
re-run against the corrected pilot v002.

---

## 7. Acceptance criteria

The conformance restoration is complete only when **all** of the following hold.

**D-02 / REP_FEATURES_v002**

1. `row_count = distinct pair_id = 3,835,988`
2. pair-id set exactly equals the v001 pair-id set
3. zero of the 25 G1-excluded `pair_id`s present
4. all 47 v001 columns preserved with **exact value equality**
5. `ko_eojeol_count` and `en_word_count` present, null count `0`, minimum `> 0`
6. artifact SHA-256 and schema hash recorded in `REP_FEATURES_MANIFEST_v002.json`

**D-03 / morphology**

7. `morpheme_density = morpheme_count / eojeol_count` (§13.6); the `codepoint_count` denominator is
   removed from the API
8. tag classification uses `base_tag = tag.partition("-")[0]`, with regression coverage for `XSA-I`
9. `J*` and `E*` counts are provably unchanged by the base-tag normalization on previously passing
   cases
10. the canonical output carries the full D-03 field set, with `morpheme_sequence` stored as
    `list<struct<form:string, pos:string>>`
11. zero analyzer output retains the pair, sets `analysis_warning_flag`, and yields **null** ratios —
    never a substituted denominator
12. `eojeol_count = 0` in the accepted cohort is `HARD_INVALID`
13. no `3_836_013` literal remains; the expected population is derived from the actual input

**Performance**

14. exact output equality between the scalar reference path and the selected optimized path over a
    fixed deterministic sample of N = 20,000, across surface sequence, POS sequence, all four counts,
    density, all ratios and the warning flag — **mismatch count must be 0**; any candidate with a
    non-zero mismatch is rejected irrespective of throughput
15. the full-run pipeline is bounded-memory: per-chunk analyse → RecordBatch → streaming Parquet
    write → release, with RAM not scaling in row count

**Stop condition**

16. Execution halts at `MORPHOLOGY_REPILOT_READY_FOR_DIRECTOR_AUDIT`. Full Kiwi and full o200k
    population runs remain prohibited until the Director's manual N = 100 audit and Claude-B's
    re-adjudication are complete.

---

## 8. Claim boundary at this snapshot

Permitted:

- the six conformance findings are reproduced against the current `main` tree
- the frozen contract in `configs/morphology_v1.yaml` already specified the D-03 fields the code omitted
- `XSA-I` is emitted by Kiwi 0.23.2 on ordinary Korean text and is currently uncounted

Not permitted:

- that any morphology result is established
- that G4 has been entered, let alone passed
- that the superseded pilot's distributions describe the corrected feature layer
- that runtime optimization has been validated before the exact-equality gate returns 0 mismatches

---

**Snapshot closed:** 2026-08-17 14:45 KST
**Decision ID:** `RD-20260817-D02D03-CONFORMANCE-01`
**Classification:** `SSOT_CONFORMANCE_RESTORATION`
**Next checkpoint:** `MORPHOLOGY_REPILOT_READY_FOR_DIRECTOR_AUDIT`
