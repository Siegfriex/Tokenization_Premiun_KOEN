# KO-EN Tokenization Premium — G2–G4 Closeout & PRE-G5 Entry Decision Log

> **Snapshot:** 2026-08-17 17:40 KST
> **Decision ID:** `RD-20260817-G2G4-CLOSEOUT-01`
> **Authority SSOT:** `KOEN-TP-RS-001` — `Korean_English_Tokenization_Premium_Research_Spec_v1.0`
> **Canonical project root:** `/home/sieg/projects-wsl/Tokenization_KOEN`
> **Canonical remote:** `https://github.com/Siegfriex/Tokenization_Premiun_KOEN.git`
> **Gate authority:** Claude-B independent forensic adjudication
> `441d5802bfebe178fd220d08b653c60dfad17faf` —
> `ssot/2026-08-17_1730_KOEN_TP_G2_G3_G4_FINAL_ADJUDICATION.md`
> **Prepared by:** Claude-A (Data / Engineering Execution Steward)
> **Final authority:** Research Director

---

## 1. Gate status

```
G0 — Design Freeze              PASS / CLOSED
G1 — Data Integrity             PASS / CLOSED
G2 — Representation Integrity   PASS / CLOSED
G3 — Tokenizer Integrity        PASS / CLOSED
G4 — Morphology Integrity       PASS / CLOSED

MEASUREMENT_FOUNDATION_CLOSED_THROUGH_G4
```

G2/G3/G4 were adjudicated by Claude-B against the physical Parquet artifacts and a live
reconstructed encoder, not against this pipeline's own reports. Claude-A reproduced the same
evidence from the artifacts in the canonical notebooks; that reproduction is corroboration, not a
second adjudication.

**Current formal phase:** `PRE-G5`.

---

## 2. Frozen measurement layer

| dataset | artifact | SHA-256 | rows | columns |
|---|---|---|---:|---:|
| D-01 / P2 | `data/registry/PAIR_REGISTRY_v002.parquet` | `95f523d1…c426010bec52` | 5,652,925 | 69 |
| **D-02** | `data/registry/REP_FEATURES_v002.parquet` | `dfae8e01…c650d309` | 3,835,988 | 49 |
| **D-03** | `data/registry/MORPH_FEATURES_KIWI_v001.parquet` | `0fe5bd74…43e50f7d` | 3,835,988 | 19 |
| **D-04** | `data/registry/TOKEN_O200K_BASE_v001.parquet` | `1c30e327…7d2c16e7` | 3,835,988 | 28 |

Final analysis cohort `N = 3,835,988`. Sorted pair-set hash `d9660d654ee449e4d0c23a0070225274`,
identical across D-02, D-03 and D-04.

```
D02_FROZEN
D03_FROZEN
D04_FROZEN
```

These three artifacts are the measurement basis for every downstream phase. Regenerating any of them
requires an explicit Director-authorized rebuild; the canonical notebooks default to
`REBUILD_CANONICAL_ARTIFACT = False` and fail closed on any identity mismatch
(`CANONICAL_ARTIFACT_IDENTITY_MISMATCH`), with no silent descent to a pilot, synthetic or earlier
version.

Superseded and retained as provenance only, never as current evidence (SSOT §24):
`REP_FEATURES_v001` (47 columns, missing the §12.2 lexical length group) and the N=1,000 morphology
pilot with its 85-row sanity sample (`SUPERSEDED_BY_CONFORMANCE_DEFECT`).

---

## 3. Version policy

```
V1  FROZEN
```

V1 is the canonical measurement line: `PAIR_REGISTRY_v002 → REP_FEATURES_v002 →
{MORPH_FEATURES_KIWI_v001, TOKEN_O200K_BASE_v001}`. All Gate evidence, all downstream statistics and
any release derive from V1.

```
V2  EXPLORATORY — AUTHORIZED, NON-CANONICAL
```

V2 exploratory work may proceed in its own lane. It is explicitly **not** canonical: it may not be
cited as Gate evidence, may not replace a canonical notebook, may not write into `data/registry/`,
and may not be promoted into V1 without a separate Director decision. The V2 EDA lane remains on
HOLD pending that decision.

---

## 4. Still required before G5

**NB06 — `06_regex_chunk_audit.ipynb` is still required.** SSOT §12.5 D-05 and the RQ5 tokenizer
mechanism line are not satisfied by D-04 alone. NB06 has not been started, and neither have
NB07–NB13; none of those notebooks exist yet, which is why there is no downstream legacy debt to
correct.

**G5 — Analysis Readiness** requires, per SSOT §31:

- identifiability check (§20.2, including the known 026 `특허정보원 ↔ 기술과학` biconditional,
  N = 359,910, exception 0 — domain and source are not separately identifiable within 026)
- collinearity report (VIF warning ≥ 5, severe ≥ 10, no automatic deletion, per D-RD-01)
- analysis cohort freeze
- train/hold-out split manifest freeze under LR-01

The redundancy findings in the exploratory representation diagnostics are **not** a G5 collinearity
result and must not be cited as one.

---

## 5. Carried debt

| id | item | classification | owner | condition |
|---|---|---|---|---|
| **R1** | Memory guard sampled twice per run; recorded minima are not true minima. External monitoring observed `MemAvailable` reaching 4.75 GiB during the concurrent full run, below the RED threshold, while the substantive failure signal stayed clean (swap delta 0.25 MiB, 64 pages out, 0 in, no OOM). | `EXECUTION_MONITORING_DEFECT` | Claude-A | **Must be fixed before the next heavy population run.** Periodic sampling inside the execution loop, not just at entry and exit. |
| **R2** | `scripts/` holds canonical research execution logic, but SSOT §36's IA lists no `scripts/` directory. | IA debt | Claude-A | **Deferred.** Migration into `src/` with the notebook as narrating surface is the correct end state, but it touches the exact code lineage that produced the adjudicated artifacts, so it must be a separate change with artifact hashes asserted unchanged on both sides. **No new canonical logic may be added to `scripts/` in the meantime.** |
| **R3** | 42,096 rows (1.0974%) with `eojeol_count = 1` carry the maximum `morpheme_density` and `particle_ratio`. Whitespace-free strings make the §13.6 denominator 1. | reporting caveat, `PLAUSIBLE_EXTREME` | NB07/NB08 | Must be handled as an analyzer artifact of short input in distribution and extreme-case panels, not as a linguistic signal. |
| **R4** | `92dc07a` commit body states "29 columns"; the artifact, manifest and schema builder all carry 28. | immutable prose error, `REPORT_TYPO_ONLY` | — | Do not propagate. 28 is authoritative. |
| **R5** | mypy reports 75 errors across 8 files, concentrated in `scripts/`. | pre-existing hygiene | Claude-A | Non-blocking. |

---

## 6. Decisions recorded

1. **G0–G4 are CLOSED.** No further work is permitted under those gates except factual correction to
   the closeout record.
2. **D-02, D-03 and D-04 are FROZEN** at the hashes in §2. Any change requires a Director-authorized
   rebuild and a new gate adjudication.
3. **The project enters PRE-G5.**
4. **V1 is frozen**; **V2 is authorized as exploratory and non-canonical** and may not be cited as
   Gate evidence.
5. **NB06 is still required** before the tokenizer-mechanism line can be closed.
6. **G5 will not be entered** until identifiability, collinearity, cohort freeze and split manifest
   freeze are all satisfied.
7. **R1 must be closed before the next heavy population run.**
8. **R2 is deferred, with a standing constraint:** no new canonical research logic may be placed in
   `scripts/`.

---

## 7. Claim boundary at this snapshot

Permitted:

- the measurement foundation is closed through G4 and the three measurement artifacts are frozen
- `TP` and its exact decomposition are measured over all 3,835,988 pairs with 0 identity violations
  and 100% round-trip
- the corrected morphology mapping counts 28,492 irregular derivational affixes that the previous
  mapping dropped

Not permitted:

- that G5 has been entered or that analysis readiness is established
- that any RQ has been answered — `median(logTP)` is an NB08 inference and no test, interval or
  effect claim exists yet
- that the exploratory redundancy findings constitute a collinearity gate result
- that the regex chunk mechanism has been examined; NB06 does not exist
- any causal language

---

**Snapshot closed:** 2026-08-17 17:40 KST
**Decision ID:** `RD-20260817-G2G4-CLOSEOUT-01`
**Gate state:** `G0–G4 CLOSED` · `PRE_G5_ENTRY`
**Next formal checkpoint:** `NB06 regex chunk audit` → `G5 Analysis Readiness`
