# KOEN — Pre-G5 Legacy Reference Audit (Phase A, read-only census)

> **Artifact ID**: `LEGACY_REFERENCE_AUDIT_PRE_G5_v001`
> **Phase**: `A_READ_ONLY_CENSUS` — no file under `main` was modified, no notebook was executed,
> no artifact was rewritten.
> **Branch**: `impl/g2-g4-notebook-reconciliation-20260817` (from `92dc07a`)
> **Audited main**: `92dc07a6f2c5af3c3161d7f7a615dc7211e27559`
> **Machine-readable companion**: `outputs/reports/LEGACY_REFERENCE_AUDIT_PRE_G5_v001.json`
> **Status**: `LEGACY_RECONCILIATION_PLAN_READY` / `WAITING_FOR_B_GATE_VERDICT`

---

## 1. Current canonical lineage (to be re-pinned from B's verdict)

```
PAIR_REGISTRY_v002.parquet      95f523d11b0e8fcfd761dee949f082e9b4590b919801441fbcfa3426010bec52
        ↓
REP_FEATURES_v002.parquet       dfae8e01cd3fe2ca949d8754678e508203ad1a7aa6abea418008a33ac650d309
        ↓
MORPH_FEATURES_KIWI_v001.parquet  0fe5bd74e3993a7141c5c33ea78e71b2c66e3ecd296544bde2615acb43e50f7d
TOKEN_O200K_BASE_v001.parquet     1c30e3276222dd94885ae4f79fc6ab5c45e4e26226de0afd91fc6b1f7d2c16e7

N = 3,835,988
```

These values are transcribed from the manifests committed at `92dc07a`. **They are provisional for
this document.** Per the directive they will be re-pinned from Claude-B's final G2/G3/G4 verdict
before any edit is made, and B's corrected manifests — if any — become authoritative over these.

---

## 2. Census method and scope

`scripts/audit_legacy_references.py` walks the repository and, for `.ipynb`, parses cell-by-cell so
each hit is attributed to where it actually lives.

| location | meaning | base severity |
|---|---|---|
| `SOURCE_CODE` | executable statement in a `.py` file or notebook code cell | P0 |
| `EXECUTED_OUTPUT` | stored output of an executed notebook cell | P1 |
| `MARKDOWN` | notebook markdown or a `.md` file | P2 |
| `COMMENT_OR_DOCSTRING` | Python comment or docstring (not executed) | P2 |
| `NOTEBOOK_METADATA` | `.ipynb` metadata block | P2 |
| `EXECUTION_RECORD` | JSON/CSV under `outputs/` — provenance, preserved per SSOT §24 | P3 |

A hit whose surrounding context is explicitly marked historical (`SUPERSEDED`, `HISTORICAL`,
changelog, conformance-finding note, negative regression test) is demoted to **P3** unless it is a
`FALLBACK` pattern, which stays P0 regardless.

**Scope corrections made during the census, recorded because they changed the counts materially:**

1. `data/` was initially scanned and produced **424 pure false positives** — the raw AIHub corpus
   contains ordinary English words that match the dictionary (`"scaffolding accidents…"`,
   `"…10 bar in 15…"` matching the ETA pattern). `data/` holds immutable raw corpus and derived
   artifacts, not repository logic, and is now excluded.
2. The census was scanning **its own output and its own pattern dictionary** (726 + 15 hits), which
   by construction contain every legacy string. Both are now self-excluded.
3. `outputs/**.json` was being graded as executable source. These are execution records; they are
   now `EXECUTION_RECORD`/P3 and are **not** to be rewritten.

Post-correction: **227 files scanned, 243 findings.**

---

## 3. Finding counts

| severity | count | meaning |
|---|---:|---|
| **P0 BLOCKING** | 45 | executable code consuming an old artifact, old API, or a silent fallback |
| **P1 HIGH** | 38 | executed output presenting an obsolete result as if current |
| **P2 MEDIUM** | 60 | stale narrative in markdown, comments, or docstrings |
| **P3 HISTORICAL_OK** | 100 | correctly-labelled provenance; **do not delete** (SSOT §24) |

Of the 45 P0s, hand triage separates them into genuinely blocking versus correct-by-design:

| P0 group | count | verdict |
|---|---:|---|
| **NB04 canonical — broken API + pilot artifact consumption** | 11 | **GENUINELY BLOCKING** |
| **NB03 canonical — v001-only path + `if exists()` fallback** | 3 | **GENUINELY BLOCKING** |
| exploratory notebooks (`03_representation_feature_diagnostics`, `EDA_..._casebook`) | 15 | HOLD — V2 EDA is on hold; not canonical |
| `scripts/**` referencing v001/pilot as *inputs to a migration* | 9 | correct by design (they exist to read the old thing) |
| `src/representation.py` v001 constants | 2 | correct by design — that function *does* emit v001 |
| `src/representation.py` `codepoint_count = len(text)` | 1 | **false positive** — D-02 feature, unrelated to the D-03 denominator |
| `tests/test_morphology.py` old-cohort/API literals | 3 | correct by design — negative regression tests |
| `outputs/eda_raw/.../build_sanitized_notebooks.py` "Interpretation scaffold" | 1 | **false positive** — prose word |

**Genuinely blocking P0: 14, all inside `notebooks/03` and `notebooks/04`.**

---

## 4. Legacy risk matrix — the blocking set

| id | path | cell/line | legacy reference | canonical replacement | type | sev | runtime impact | scientific impact | auto-fix safe? | B dep | planned action |
|---|---|---|---|---|---|---|---|---|---|---|---|
| L015 | `notebooks/04` | cell 2 L16 | `REP_FEATURES_v001.parquet` | `REP_FEATURES_v002.parquet` | SOURCE | P0 | reads pre-lexical D-02 | eojeol denominator unavailable | yes | pin hash | rewrite input block |
| L016 | `notebooks/04` | cell 2 L19 | `.runtime/nb04-pilot/MORPH_FEATURES_PILOT_v001.parquet` | `data/registry/MORPH_FEATURES_KIWI_v001.parquet` | SOURCE | P0 | consumes superseded pilot | pilot was produced under the M1–M5 defects | yes | pin hash | repoint to full artifact |
| L017 | `notebooks/04` | cell 2 L21 | `MORPH_FEATURES_PILOT_MANIFEST_v001.json` | `MORPH_FEATURES_KIWI_MANIFEST_v001.json` | SOURCE | P0 | same | same | yes | pin hash | repoint |
| L018/L019 | `notebooks/04` | cell 2 L19–20 | `.runtime/nb04-pilot` | `.runtime/morph-full/<run_id>` | SOURCE | P0 | same | same | yes | — | repoint |
| L021/L022 | `notebooks/04` | cell 4 L19 | `projected_full_population_3836013_rows_min` | measured 187.9 s | SOURCE | P0 | key no longer emitted → `KeyError` | superseded cohort N and ETA | yes | — | delete, read actual runtime |
| L023 | `notebooks/04` | cell 4 L1 | `if PILOT_OUTPUT.exists():` | fail-closed identity assert | FALLBACK | P0 | **silently degrades to pilot** | could present pilot numbers as final | yes | — | fail-closed |
| L028 | `notebooks/04` | cell 11 L14 | `morphology_features(..., codepoint_count=…)` | `eojeol_count=…` | API | P0 | **`TypeError` on re-run** | M1 defect: codepoint denominator | yes | — | rewrite call |
| — | `notebooks/04` | cell 2 L34 | `execute_morphology_run(input_path=…)` | `rep_features_v002_path=`, `pair_registry_path=`, `run_mode=` | API | P0 | **`TypeError` on re-run** | signature replaced in conformance fix | yes | — | rewrite call |
| L029/L030 | `notebooks/04` | cell 16 L3 | `MORPHOLOGY_SANITY_AUDIT_SAMPLE.json` (85 rows) | Director N=100 audit | SOURCE | P0 | reads superseded evidence | 85-row sample is `SUPERSEDED_BY_CONFORMANCE_DEFECT` | yes | B verdict | replace with N=100 evidence |
| L007 | `notebooks/03` | cell 9 L2 | `REP_FEATURES_v001.parquet` | v002 | SOURCE | P0 | — | v001 is historical, not final | partial | pin hash | keep as historical stage, add v002 stage |
| L008 | `notebooks/03` | cell 9 L1 | `if REP_FEATURES_V001.exists():` | fail-closed identity assert | FALLBACK | P0 | **skips silently** | can look like a pass without producing anything | yes | — | fail-closed |
| L005 | `notebooks/03` | cell 6 L3 | `if PILOT_OUTPUT.exists():` | fail-closed | FALLBACK | P0 | pilot-vs-full ambiguity | — | yes | — | fail-closed |

### Signature evidence (independent of grep)

An AST call-signature check against the *current* `src` confirms the API breakage is real and is
confined to one notebook:

```
00_environment_repro.ipynb        signatures OK
01_build_pair_registry.ipynb      signatures OK
02_normalize_and_qc.ipynb         signatures OK
03_representation_features.ipynb  signatures OK
04_morphology_features.ipynb      BROKEN
   execute_morphology_run(): unknown=['input_path']
                             missing_required=['rep_features_v002_path','pair_registry_path','run_mode']
   morphology_features():    unknown=['codepoint_count'] missing_required=['eojeol_count']
05_o200k_measurement.ipynb        signatures OK
```

Note the census's own import-graph check reported `unresolved imports: NONE` — every imported symbol
still exists. The breakage is in the **call contract**, not the import, which is exactly why a
grep-or-import-only audit would have missed it.

---

## 5. P1 — executed output presenting obsolete results as current

38 total; the canonical-notebook subset is what matters.

| id | notebook | cell | stored output | why it is P1 |
|---|---|---|---|---|
| L020 | `04` | cell 2 out 0 | `'config_sha256': 'c056dd7a…'` | config hash **no longer exists** in the codebase (now `6f48802a…`) — §30.2 lineage break |
| L024/L025 | `04` | cell 4 out 3 | `'projected_full_population_3836013_rows_min': 151.2` | superseded cohort N *and* superseded ETA |
| L026/L027 | `04` | cell 8 out 0 | `PILOT_ONLY_FULL_RUN_DEFERRED` | contradicts the executed full run |
| L031/L032 | `04` | cell 16 out 0 | 85-row sanity sample path | superseded evidence |
| L004/L009–L011 | `03` | cells 4, 11 | `3836013` row counts / fingerprint | pre-exclusion cohort, before the G1 25-pair exclusion |
| L001/L002 | `02` | cell 20 out 0 | `3836013` denominators | correct **at the time**; P2/G1 are closed, so this is historical, not to be re-run |

The most serious single item remains `04` cell 16: the notebook stores
`'deriv_affix_tags_observed': ['XSA','XSN','XSV']` and `'pos_contract_mismatch_rows': 0` — a green
PASS produced *by* the M2 defect. The full run has since counted **28,492 `XSA-I` occurrences** that
this stored output implies do not exist.

---

## 6. Old cohort literals (§12)

| context | occurrences | disposition |
|---|---:|---|
| `3_836_013` in executable code | **0** in `src/` (asserted by an AST regression test) | already clean |
| `3836013` in NB02/NB03 stored output | 6 | historical, do not re-run NB02 |
| `projected_full_population_3836013_rows_min` in NB04 executable code | 1 | **P0, remove** |
| `3_835_988` hard-coded in executable code | 3 (`bench_kiwi_morphology.py`, `bench_o200k_concurrency.py`, exploratory EDA) | benchmarks/EDA only; not canonical. Canonical runners already derive N from the input artifact |
| `3_835_988` in `tests/test_morphology.py` | 1 | negative test asserting the literal is *absent* from the module — correct |

Canonical execution paths (`execute_morphology_run`, `execute_token_measurement_run`) already derive
`expected_rows` from the input artifact and contain no population literal.

---

## 7. Column-count literals (§13)

| literal | where | note |
|---|---|---|
| `47` | NB03 stored output, exploratory EDA `EXPECTED_COLS`, `REP_FEATURES_MANIFEST_v001` | v001 truth; historical |
| `49` | `REP_FEATURES_MANIFEST_v002` | current D-02 |
| `19` | `MORPH_FEATURES_KIWI_MANIFEST_v001` | current D-03 |
| `28` | `token_measurement_schema()`, physical parquet, `TOKEN_O200K_BASE_MANIFEST_v001.column_count` | current D-04; **all three agree on 28** |
| `29` | commit body of `92dc07a` only | **my own prose error.** Claude-B resolved this as `REPORT_TYPO_ONLY` and I verified it directly: the schema builder emits 28 fields, the stored parquet has 28 columns, and the manifest records 28. The `29` exists nowhere except that one immutable commit message. It is not a manifest defect and not a schema-contract defect. Do not propagate it. |

---

## 8. Hash references (§14)

| hash | meaning | status |
|---|---|---|
| `c056dd7a…` | morphology config, pre-conformance | appears in NB04 stored output (P1) and 2 execution records (P3). **Do not delete the records**; the notebook output must be regenerated |
| `6f48802a…` | morphology config, current | in `MORPH_FEATURES_KIWI_MANIFEST_v001` |
| `335c20de…` | `REP_FEATURES_v001` | historical, correctly labelled |
| `dfae8e01…` | `REP_FEATURES_v002` | current |
| `41a28f44…` | superseded pilot parquet | recorded as `SUPERSEDED_BY_CONFORMANCE_DEFECT` — correct |
| `75dcecb4…` | representation config | **unchanged** across v001→v002 by deliberate design, so NB03's stored value remains valid |

---

## 9. Script / src ownership (§8)

| file | class | note |
|---|---|---|
| `run_full_measurement.py` | `CANONICAL_LOGIC_HIDDEN_IN_SCRIPT` | **produced the current canonical D-03/D-04 artifacts** |
| `validate_full_measurement.py` | `CANONICAL_LOGIC_HIDDEN_IN_SCRIPT` | G2/G3 evidence validation |
| `build_rep_features_v002.py` | `CANONICAL_LOGIC_HIDDEN_IN_SCRIPT` | produced the current D-02 |
| `build_token_audit_sample.py` | `CANONICAL_LOGIC_HIDDEN_IN_SCRIPT` | G3 audit sample |
| `run_morphology_pilot_v002.py` | `ONE_OFF_MIGRATION` | corrected pilot + superseded comparison |
| `build_morphology_audit_100.py` | `ONE_OFF_MIGRATION` | Director audit pack |
| `bench_kiwi_morphology.py`, `bench_o200k_concurrency.py` | `ENGINEERING_BENCHMARK` | not research output |
| `audit_legacy_references.py` | `ENGINEERING_BENCHMARK` | this census |

**Structural finding (P1, repository-level).** SSOT §36's IA lists `notebooks/`, `src/`, `tests/`,
`configs/`, `docs/`, `data/`, `outputs/` — there is **no `scripts/`**. Four files carrying canonical
research execution logic therefore sit outside the SSOT information architecture, and ENG-OBS-001
§13 requires that implementation not live exclusively outside the notebook that narrates it.

Per the directive this is **inventory only**. The exact code lineage that produced the current
artifacts and B's validation is **not** deleted or moved in Phase A.

---

## 10. Dangerous fallback logic (§11)

Three `if <artifact>.exists():` guards in canonical notebooks, all in NB03/NB04. Their effect is
that a Run All on a machine missing the canonical artifact **silently skips or silently downgrades to
the pilot** instead of failing. No `glob(...)[0]`, `sorted(...)[-1]`, `latest_manifest`, or
`fallback_to_pilot` pattern was found anywhere.

Planned Phase-B replacement, fail-closed:

```
CANONICAL_ARTIFACT_IDENTITY_MISMATCH
```
raised explicitly when path, SHA-256, schema hash, row count, or pair set does not match the pinned
manifest. No silent descent to a pilot, synthetic, or older version.

---

## 11. Downstream NB06–NB13 preflight (§25)

```
06_regex_chunk_audit.ipynb      ABSENT
07_eda_and_decomposition.ipynb  ABSENT
08_primary_inference.ipynb      ABSENT
09_explanatory_models.ipynb     ABSENT
10_predictive_models.ipynb      ABSENT
11_robustness.ipynb             ABSENT
12_gpt_oss_serving.ipynb        ABSENT
13_release_tables_figures.ipynb ABSENT
```

**None of the downstream notebooks exist yet.** There is therefore no old filename, old feature
count, old morphology schema, old N, or old TP artifact naming to correct downstream — the entire
class of PRE-G5 downstream blockers is empty. They will be authored against the canonical lineage
frozen after B's verdict.

---

## 12. What Phase A deliberately did **not** touch

- `main` — unmodified; all work is on `impl/g2-g4-notebook-reconciliation-20260817`
- no notebook executed, no artifact regenerated, no manifest edited
- `outputs/manifests/**` execution records — preserved as provenance (SSOT §24)
- the V2 EDA notebook and `notebooks/exploratory/**` — **HOLD** per the directive
- NB06 — **HOLD**
- the TOKEN 28/29 question — left open for B

---

## 13. Planned Phase-B sequence (after B's G2/G3/G4 verdict)

Commits stay small and each carries tests (§29):

1. `audit(repo): inventory legacy references before G5` ← this document
2. `fix(nb03): align canonical representation notebook with D02 v002`
3. `fix(nb04): align canonical morphology notebook with full D03 evidence`
4. `fix(nb05): align canonical tokenizer notebook with full D04 evidence`
5. `test(notebooks): enforce canonical artifact fail-closed lineage`

Regression tests to add (§27): no obsolete artifact path in a canonical notebook; no old cohort
literal in executable code; no `codepoint_count` morphology API; no synthetic-only final state in
NB05; no fallback to pilot; current artifact SHA recorded; schema counts match B's verdict.

Notebooks will default to `REBUILD_CANONICAL_ARTIFACT = False` and validate/reuse rather than
regenerate (§23), so a headless Run All must leave every artifact SHA unchanged.

---

## 14. Decision required

1. ~~**TOKEN schema 28 vs 29**~~ — **RESOLVED** by Claude-B as `REPORT_TYPO_ONLY` and independently
   re-verified here: schema builder, physical parquet and manifest all say **28**. The `29` was my
   own error in the `92dc07a` commit body. This document's earlier statement that the repository
   "contains only 29" was wrong and has been corrected in §7 above.
2. **`scripts/` versus SSOT §36 IA** — canonical execution logic currently lives outside the SSOT
   information architecture. Phase B can migrate it into `src/` with the notebook as the narrating
   execution surface, but that touches the exact lineage that produced the artifacts under B's
   review. Recommend deferring until B's verdict is in, then migrating with artifact hashes asserted
   unchanged before and after.

```
LEGACY_RECONCILIATION_PLAN_READY
WAITING_FOR_B_GATE_VERDICT
```
