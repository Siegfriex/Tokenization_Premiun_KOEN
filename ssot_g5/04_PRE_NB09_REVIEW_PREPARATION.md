# PRE-NB09 Review Preparation — Decision Template

> **Status**: `NOT_FROZEN` · `NOT_A_DECISION` · `PREPARATION_ONLY`
>
> **Prepared by**: Claude-B (Research / Statistics)
> **Date**: 2026-08-18 KST
> **Reads**: `G5_ANALYSIS_READINESS_PASS_WITH_NOTES` (`35a40e7`), diagnostics (`5edb784`),
> protocol (`4e9bab8`), base main `4eaa35e`
>
> **Authority**: `KOEN-TP-RS-001` §12.2 · §13 · §18 · §19.1–19.3 · §20 · §20.2 · §21 · §32 →
> `RD-FAST-G5-01` / `CR-FAST-G5-REALIZED-MODEL-01` · `RD-SSOT-CANONICAL-RETURN-01` §14–§15

```
NB09_EXECUTED            = NO
M0_M3_FITTED             = NO
COEFFICIENT_PRODUCED     = NO
MODEL_RESULT_PRODUCED    = NO
FEATURE_CHOSEN           = NO      ← every option below is unresolved by design
OUTCOME_ASSOCIATION_USED = NO      ← no option is ranked by any relationship to Y_A or Y_B
CANONICAL_SCIENCE_STATE  = UNCHANGED
```

Nothing in this document selects a feature, states a preference derived from data, or anticipates a
result. Where a recommendation appears it is grounded in construct definition or in SSOT
interpretation rules, and it is marked as a recommendation for the Director to accept or reject.

---

## 0. What the two review triggers do — and do not — threaten

This framing governs everything below and should be settled first, because it changes how much work
`M3-01` and `SM-01` actually require.

`KOEN-TP-RS-001` §19.2 defines the core questions as **block-level nested comparisons**:

```
RQ3   M1 − M0     representation / surface block
RQ4   M2 − M1     morphology block          ← the primary morphology question
RQ5   M3 − M2     regex-chunk mechanism block
```

and §19.3 states that M3 is a **mechanism audit**, that a high R² for M3 is expected, and that its
purpose is "not a predictive win". `RD-SSOT-CANONICAL-RETURN-01` §15 repeats the ordering:
incremental / partial R², model-level improvement, coefficient magnitude and model stability —
**over individual coefficient p-values**.

Collinearity within a block inflates the variance of **individual coefficients inside that block**.
It does not bias the fitted values, and it does not invalidate the nested block comparison, which
depends on the span of the block rather than on its basis.

Therefore:

| affected | `M3-01` | `SM-01` |
|---|---|---|
| block-level RQ5 (`M3 − M2`) | **not invalidated** | n/a |
| block-level RQ3 (`M1 − M0`) | n/a | **not invalidated** |
| block-level RQ4 (`M2 − M1`) | n/a | **not invalidated** — both terms sit in M1, on both sides of the comparison |
| individual coefficient on a chunk-scale term | **at risk** | n/a |
| individual coefficient on a script-mixing term | n/a | **at risk** |
| model stability / reproducibility of the fit | at risk if reported per-coefficient | at risk if reported per-coefficient |

**Consequence for RQ4, the primary morphology question.** `M2 − M1` differences out everything in
M1. `SM-01` lives entirely inside M1 and therefore cancels. `M3-01` lives entirely inside the M3
block and is downstream. **Neither open review blocks RQ4.**

This is the single most important thing for the Director to rule on, because option `R0` below may
close both reviews without changing a single column.

---

## 1. `SM-01` — script-mixing representative feature

### 1.1 What was measured (G5, already persisted)

```
Spearman  en_script_type_count ~ en_script_switch_count   0.9994
          ko_script_type_count ~ ko_script_switch_count   0.9910
VIF       en_script_type_count   9.11 (M1) · 9.16 (M2, M2A, M3)
rank      M1 23/23 full — no estimability problem
```

### 1.2 Construct derivation — this is not merely an empirical correlation

Read from the frozen extractor (`src/tokenization_premium/representation.py`, rule
`rep_v001`, `config_sha256 75dcecb4…`, recorded in every D-02 row):

- code points are classified into six exclusive groups `hangul · latin · digit · punct · space · other`;
- `_SCRIPT_SWITCH_GROUPS = {hangul, latin, other}` — digit, punct and space are **neutral** and are
  dropped before either statistic is computed;
- `script_type_count` = number of **distinct** groups present in that filtered sequence → range 0–3;
- `script_switch_count` = number of **adjacent transitions** in that same sequence → unbounded.

From those definitions alone, without touching data:

```
script_type_count ≤ 1   ⟹   script_switch_count = 0     (no pair of differing neighbours can exist)
script_type_count ≥ 2   ⟹   script_switch_count ≥ 1     (the sequence must change at least once)

therefore   1{script_switch_count ≥ 1}  ≡  1{script_type_count ≥ 2}      exactly
```

**The indicator is a logical identity, not an observed association.** The two variables carry
independent information only *within* the multi-script subpopulation, where `switch_count` adds
"how often the scripts alternate" on top of "how many scripts are present".

The realized distributions (persisted in `G5_REALIZED_MODEL_CONTRACT_v001.json`) show that
subpopulation is thin:

| column | mean | sd | min | max |
|---|---:|---:|---:|---:|
| `ko_script_type_count` | 1.2280 | 0.4312 | 0 | 3 |
| `ko_script_switch_count` | 0.4802 | 1.1571 | 0 | 34 |
| `en_script_type_count` | 1.0695 | 0.2546 | 0 | 3 |
| `en_script_switch_count` | 0.0816 | 0.3415 | 0 | 42 |

The modal EN side has one script group and zero switches. That tie mass is what drives ρ to 0.9994.

**Process note, stated plainly.** G5's structural-removal pass caught exact identities between
variables. This is a *partial* determinism — the indicator is deterministic, the values are not —
so the pair survived structural pruning and surfaced only in the correlation screen. That is a real
gap in the structural step, not a discovery the screen was designed to make. It is recorded here so
the same class is checked structurally at PRE-NB10 rather than left to a screen.

**Incidental observation for NB07, not part of `SM-01`.** `script_type_count` has a realized
minimum of 0, which occurs when a side contains no hangul, latin or other code point — i.e. digits,
punctuation and whitespace only. NB07 should report how many such sides exist and on which side.
This is a descriptive question about the cohort, not a modelling decision.

### 1.3 Decision alternatives

| id | option | construct meaning retained | construct meaning lost | changes M1 columns |
|---|---|---|---|---|
| `SM-A` | keep **both**, interpret the script-mixing block only at block level | variety and interleaving intensity | per-term reading | no |
| `SM-B` | keep `script_type_count` only | script **variety** — how many writing systems are present | interleaving intensity within multi-script text | −2 columns |
| `SM-C` | keep `script_switch_count` only | **interleaving intensity** — how often the writing system alternates | the presence/variety distinction at 0 vs 1 script | −2 columns |
| `SM-D` | keep both but reparameterize as `1{type ≥ 2}` plus `switch_count` | the deterministic indicator is made explicit; the second term then carries only within-multi-script intensity | nothing; this is a re-basis of the same span | rebasis, same count |

Construct commentary, offered to the Director rather than decided here:

- SSOT §12.2 names the variable group **"mixing"** and lists both members, so neither is outside
  specification. §21's rule is that feature **semantics** are examined before any automatic removal,
  which is what §1.2 does.
- `SM-B` is the more conservative reading if the scientific interest is "does script mixing occur at
  all", since `type_count` is bounded, length-independent and directly interpretable.
- `SM-C` is preferable if the interest is fragmentation-relevant alternation, but note that
  `switch_count` is a **count** and therefore scales with text length, which puts it in partial
  competition with `pair_log_size` — the same failure mode as `M3-01`. It is not currently
  length-normalized.
- `SM-D` is the only option that removes the deterministic overlap **by construction** rather than
  by choosing a side. It costs no information and makes the two constructs orthogonal in meaning:
  an indicator for "multi-script at all", and an intensity term whose variation lives entirely
  inside that indicator's support.

`SM-D` is the preparer's recommendation **on construct grounds only**. It has not been evaluated
against any outcome and must not be adopted on the basis of fit.

### 1.4 Evidence NB07 must supply to resolve `SM-01`

NB07 is the canonical descriptive notebook (`RD-SSOT-CANONICAL-RETURN-01` §14) and computes directly
from D-02/D-03/D-04/D-05. To close this review it must report, per side:

1. the joint distribution of `script_type_count × script_switch_count` — the full contingency,
   which will make the deterministic step visible rather than inferred;
2. `P(script_type_count ≥ 2)` per side, and per `source_domain_cell`;
3. within the `type_count ≥ 2` subpopulation only, the conditional Spearman `ρ` between the two
   terms — this is the quantity that decides whether `switch_count` carries usable independent
   variation at all;
4. the count of sides with `script_type_count = 0` and what those texts are composed of;
5. the length dependence of `script_switch_count` — its distribution across length strata — so the
   Director can see whether `SM-C` would import the `M3-01` problem into M1;
6. whether the multi-script subpopulation is concentrated in particular cells, which bears on
   `ID-03`.

**Not required and not to be produced**: any relationship between either term and `Y_A` or `Y_B`.
That would make this an outcome-driven selection, which SSOT §21 and `CR-FAST-G5-REALIZED-MODEL-01`
§6 both forbid.

---

## 2. `M3-01` — chunk-scale versus pair-length reparameterization

### 2.1 What was measured (G5, already persisted)

```
M3   condition number (standardized)  134.57   ≥ 100  → REPARAMETERIZATION_REVIEW
     max VIF                        1252.61   ≥  20  → STRONG_REDUNDANCY_REVIEW
     rank                             45/45   full   → no estimability problem

top VIF   pair_log_size        1252.61
          en_chunk_count_log     854.04
          ko_chunk_count_log     791.04
          log_code_point_ratio    60.41
          en_mean_chunk_bytes     51.53
          ko_mean_chunk_bytes     47.99

M2 (same model without the D-05 block)   condition 20.98 · max VIF 17.47 · no trigger
```

The pressure appears only when the D-05 block is added, and it lands on the **length terms**, not on
the categorical coding (`GVIF^(1/2df)` stays 1.10–1.34 across all five models).

### 2.2 Construct derivation

A regex chunk is a maximal span matched by the frozen `o200k_base` `pat_str`. The number of chunks
in a text is, mechanically, close to proportional to its length: longer text yields more chunks.
`ko_chunk_count_log` and `en_chunk_count_log` therefore re-express, in a second basis, information
that `pair_log_size` and `log_code_point_ratio` already carry.

This is a **basis** problem, not a defect: rank is full, so the block is estimable; the terms are
simply not separated in a way that lets an individual coefficient be read.

What M3 is for (SSOT §19.3) is tracking *which surface and morphological patterns connect to chunk
fragmentation*. The construct that answers that is **fragmentation intensity per unit of text**, not
the raw chunk count — the count is length, restated.

### 2.3 Decision alternatives

| id | option | construct | relation to existing SSOT idiom |
|---|---|---|---|
| `M3-A` | keep as frozen; interpret the D-05 block only at block level (RQ5 = `M3 − M2`) | unchanged | SSOT §19.2/§19.3 already designate block-level as primary for M3 |
| `M3-B` | replace the two chunk counts with **chunk density** per side, `chunk_count / codepoint_count` (or its log) | "how finely the regex partitions a unit of text" — fragmentation intensity | directly parallel to §13.3 `BytesPerCodePoint`, §13.4 `WhitespaceDensity`, §13.6 `MorphemeDensity`; density is the specification's standard way to remove length |
| `M3-C` | re-base to size + ratio, mirroring M0/M1: `chunk_log_size = 0.5(ln k_KO + ln k_EN)` and `log_chunk_ratio = ln(k_KO/k_EN)` | separates joint chunk scale from KO/EN chunk asymmetry | mirrors `CR-FAST-G5-REALIZED-MODEL-01` §4.4's `pair_log_size` + `logCodePointRatio` split |
| `M3-D` | drop the chunk counts, retain only chunk-byte distribution and chunk-type shares | avoids the overlap entirely | loses the fragmentation-count mechanism, which is the core of RQ5 |
| `M3-E` | residualize the chunk counts on `pair_log_size` | orthogonal by construction | introduces an estimated quantity into the design matrix and complicates provenance |

Construct commentary:

- `M3-C` only partially helps: `log_chunk_ratio` is close to orthogonal to `pair_log_size`, but
  `chunk_log_size` remains a length restatement. Expect the trigger to persist in attenuated form.
- `M3-B` removes the duplication **by construction**, and the resulting term is the one SSOT §19.3
  actually asks about. It is the preparer's recommendation on construct grounds. Note it is a
  transform of existing physical columns, not a new measurement — no D-05 regeneration is implied,
  and `RD-SSOT-CANONICAL-RETURN-01` §3 authorizes none.
- `M3-D` should be rejected unless the Director decides RQ5 is out of scope for this release.
- `M3-A` is legitimate and cheapest, and is sufficient if RQ5 is reported strictly as a block
  comparison with no per-term claims.

`M3-A` and `M3-B` are not exclusive: adopting `M3-B` and *still* restricting RQ5 to block-level is
the most conservative combination.

**Ordering note.** `M3-B` and `SM-C` interact: both concern whether a count term is length-normalized.
If the Director adopts `M3-B`'s density reasoning, consistency argues for applying the same reasoning
to `script_switch_count` — which is `SM-D` with a normalized second term, or an argument against
`SM-C`. This should be decided once, not twice.

### 2.4 Evidence NB07 must supply to resolve `M3-01`

1. the distribution of chunks per code point, per side, overall and by length stratum — the direct
   descriptive form of the `M3-B` construct;
2. the empirical relationship between `chunk_count` and `codepoint_count` per side, reported
   descriptively (SSOT §16 canonical distributions), so the Director can see how close to
   proportional it actually is;
3. the chunk-byte distribution family (`mean`, `p50`, `p90`, `max`) summarized per side, with the
   G5 within-family correlations (KO 0.8307, EN 0.7861) restated in descriptive form — these did
   **not** trigger and no representative rule is currently required for them;
4. the KO/EN chunk-count asymmetry distribution, which is the `M3-C` construct;
5. the three-boundary distinction made concrete (SSOT §5.1, `RD-SSOT-CANONICAL-RETURN-01` §9):
   linguistic morpheme counts, regex chunk counts and final subword token counts side by side, so
   the mechanism layer is not read as a second tokenizer outcome.

**Not required**: any regression of chunk terms on either outcome, and any partial or incremental R².

---

## 3. `ID-03` — `source_domain_cell` is an observed-stratum control only

### 3.1 Standing structural fact

```
sources 2 · domains 4 · realized cells 5
025 × {dialogue, general, other}      026 × {other, technology}
only `other` occurs under both sources
```

Independent main effects of source and domain are **not separately identifiable**. This is
structural (SSOT §32 T-04, §20.2 Gate G-ID) and **NB07 cannot resolve it.** No descriptive evidence
can separate two factors that the sampling design confounds.

What NB07 *can* do is bound the interpretation and tell the Director whether the composite control
is doing meaningful work.

### 3.2 Decision alternatives

| id | option | consequence |
|---|---|---|
| `ID3-A` | keep `source_domain_cell`, forbid pure-source and pure-domain language in all RQ3–RQ5 reporting | the approved design; interpretation restriction only |
| `ID3-B` | additionally report the `025-other` vs `026-other` contrast as the **only** window where source varies with domain held fixed | one named, bounded descriptive contrast; must be labelled as a single-domain comparison, never as "the source effect" |
| `ID3-C` | fit the `domain + source_id` additive sensitivity permitted by `CR-FAST-G5-REALIZED-MODEL-01` §4.3 | permitted **only if** that additive design is full rank and numerically acceptable; that is a G5-class check, not an NB07 output, and it has **not** been run |

`ID3-A` is already binding. `ID3-B` is a reporting addition, not a design change, and is the
preparer's recommendation because it makes the confound legible instead of only prohibited.
`ID3-C` requires a separate identifiability check before it may be attempted; it is listed for
completeness and is **not** proposed for this release.

### 3.3 Evidence NB07 must supply

1. outcome distributions (`logTP`, and the exact decomposition components) **by cell**, all five
   cells, as descriptive summaries;
2. the `025-other` vs `026-other` descriptive comparison, explicitly labelled as domain-held-fixed;
3. cell sizes and length-stratum composition per cell, so heterogeneity attributable to length
   composition is visible before any model is fitted;
4. an explicit statement in the NB07 text that no cell contrast may be read as a source effect or a
   domain effect.

---

## 4. `ID-04` — direction identified from within-025 variation only

### 4.1 Standing structural fact

```
                    KO_TO_EN    EN_TO_KO    UNKNOWN
025-dialogue         247,947     254,955     13,260
025-general          354,654     449,606         31
025-other            559,527     568,728     37,255
026-other            990,119           0          1
026-technology       359,905           0         0
```

Three of fifteen combinations are empty and two more are near-singletons (31 and 1). The 026 family
contains **no** `EN_TO_KO` observation. Under main-effects-only coding the direction contrast is
estimable — M0 is full rank — but it is identified entirely from within-025 variation, and a
`cell × direction` interaction is not estimable and is not introduced.

The `UNKNOWN` level (50,547 total) is also extremely unevenly distributed: 37,255 in `025-other`,
13,260 in `025-dialogue`, 31 in `025-general`, 1 in `026-other`, 0 in `026-technology`.

### 4.2 Decision alternatives

| id | option | consequence |
|---|---|---|
| `ID4-A` | retain all three direction levels including `UNKNOWN`, per `CR-FAST-G5-REALIZED-MODEL-01` §5 and §7 | approved design; `UNKNOWN` is a level, not a missing value |
| `ID4-B` | retain as `ID4-A`, and additionally state in every direction interpretation that identification comes from source 025 only | interpretation restriction only |
| `ID4-C` | report the known-direction subset as a **named sensitivity**, consistent with the RQ1 precedent (`KNOWN_DIRECTION_ONLY`, N = 3,785,441) | already listed as an approved sensitivity candidate in `CR-FAST-G5-REALIZED-MODEL-01` §7; belongs to NB11, not NB09 |
| `ID4-D` | collapse or drop `UNKNOWN` | **not proposed** — `RD-FAST-G5-01` §7 explicitly forbids introducing a primary exclusion for `translation_direction = UNKNOWN` |

`ID4-B` is the preparer's recommendation. `ID4-C` is a scheduling item for NB11, not a decision for
NB09.

### 4.3 Evidence NB07 must supply

1. outcome distributions by direction **within each 025 cell**, which is the actual identification
   window;
2. a descriptive characterization of the `UNKNOWN` pairs — length, cell, and how they differ
   descriptively from known-direction pairs — so the Director can judge whether treating `UNKNOWN`
   as a substantive level is defensible;
3. explicit confirmation, restated from the artifacts, that 026 contains no `EN_TO_KO`;
4. the direction composition of each length stratum, since direction and length may be jointly
   distributed (SSOT §32 T-03 translationese).

---

## 5. `SPEC-01` and `SPEC-02` — carry-forward notes

These are not reviews. They are recorded scope decisions that NB09 must state, and NB07 can supply
the evidence that shows whether either mattered.

### 5.1 `SPEC-01` — held-out D-02 variables

Held out of every primary matrix at G5 because SSOT §18.1's explicit form does not carry them and
`RD-SSOT-CANONICAL-RETURN-01` §11 forbids open-ended feature expansion at G5:

```
ko/en_url_flag · ko/en_email_flag · ko/en_emoji_flag · ko/en_code_like_flag
ko/en_space_run_count
ko/en_grapheme_count · pair_grapheme_ratio · ko/en_bytes_per_grapheme
```

**NB07 evidence**: prevalence of each flag per side and per cell, and the distribution of
`space_run_count` and the grapheme-scale terms. If the flags are near-degenerate, the exclusion is
costless and the note closes. If any flag is substantially prevalent, the Director may reopen it as
an NB11 sensitivity — **never** as a mid-analysis addition to a primary matrix.

### 5.2 `SPEC-02` — Outcome B's M1 conditions on both representation ratios

SSOT §18.2's *illustrative* form for `Y_B = log CompressionPenalty` omits `logCodePointRatio` and
`logByteDensityRatio`; the Director-approved common ladder includes them. G5 verified that neither
outcome is reconstructible from its own right-hand side, so this is a specification choice, not a
leakage question.

**Required of NB09 reporting**: state that Outcome B's M1 conditions on both representation ratios,
and that `IR-02`'s reading — the B model explains tokenizer compression asymmetry once byte
representation volume is separated — is delivered here by *conditioning* on those components rather
than by omitting them.

**NB07 evidence**: the descriptive distribution of `logCP` alongside `logCR` and `logBDR`, and the
exact-decomposition accounting (SSOT §8, already verified at 8.9e-16 in G5), so the relationship
between the two outcomes is visible before either model is fitted.

---

## 6. Consolidated NB07 evidence request

One list, so NB07 can be scoped without re-reading the sections above. All items are descriptive and
computed from canonical D-02/D-03/D-04/D-05. **None involves fitting a model.**

| # | evidence | closes |
|---|---|---|
| 1 | `script_type_count × script_switch_count` joint contingency, per side | `SM-01` |
| 2 | `P(script_type_count ≥ 2)` per side and per cell | `SM-01`, `ID-03` |
| 3 | conditional Spearman between the two script-mixing terms, restricted to `type_count ≥ 2` | `SM-01` |
| 4 | count and composition of sides with `script_type_count = 0` | `SM-01` (incidental) |
| 5 | `script_switch_count` distribution across length strata | `SM-01`, `M3-01` |
| 6 | chunks per code point, per side, overall and by length stratum | `M3-01` |
| 7 | descriptive `chunk_count` versus `codepoint_count` relationship, per side | `M3-01` |
| 8 | chunk-byte family (`mean`/`p50`/`p90`/`max`) summaries per side | `M3-01` |
| 9 | KO/EN chunk-count asymmetry distribution | `M3-01` |
| 10 | morpheme / regex-chunk / subword-token counts side by side (three-boundary table) | `M3-01`, SSOT §5.1 |
| 11 | outcome and decomposition distributions by cell, all five cells | `ID-03` |
| 12 | `025-other` versus `026-other`, labelled domain-held-fixed | `ID-03` |
| 13 | cell sizes and per-cell length-stratum composition | `ID-03`, `ID-04` |
| 14 | outcome by direction **within each 025 cell** | `ID-04` |
| 15 | descriptive characterization of `UNKNOWN`-direction pairs | `ID-04` |
| 16 | direction composition per length stratum | `ID-04`, T-03 |
| 17 | prevalence of the held-out D-02 flags and surface terms | `SPEC-01` |
| 18 | `logCP` distribution alongside `logCR` and `logBDR`; decomposition accounting | `SPEC-02` |

**Explicitly excluded from NB07 for these purposes**: any association between a candidate predictor
and either outcome that could be used to rank the options in §1.3 or §2.3. NB07 legitimately reports
outcome distributions *by stratum* (items 11, 14) — those are descriptive heterogeneity, which SSOT
§16 requires — but they must not be used as a feature-selection criterion, and this document does
not propose them as one.

---

## 7. Director decision template

To be returned marked. Nothing proceeds to NB09 until items `R0`–`R4` carry a decision.

```
### R0 — INTERPRETATION SCOPE FOR BLOCK-LEVEL QUESTIONS       (settle first; may close R1 and R2)

  [ ] R0-1  RQ3/RQ4/RQ5 are reported as block-level nested comparisons; individual
            coefficients inside a triggered block are NOT reported as findings
  [ ] R0-2  individual coefficients ARE to be reported, so both triggers must be
            resolved by changing the matrix
  [ ] other: ______________________________________________

  If R0-1: M3-01 and SM-01 may both close as interpretation restrictions
           (options M3-A and SM-A) with no column change.


### R1 — SM-01  script-mixing representative feature

  [ ] SM-A  keep both, block-level interpretation only
  [ ] SM-B  keep script_type_count only            (variety)
  [ ] SM-C  keep script_switch_count only          (intensity; note: not length-normalized)
  [ ] SM-D  reparameterize as 1{type >= 2} + switch_count     ← preparer's construct recommendation
  [ ] defer until NB07 items 1-5 are available
  [ ] other: ______________________________________________

  applies to: M1, M2, M2A, M3        blocks RQ4? NO


### R2 — M3-01  chunk-scale reparameterization

  [ ] M3-A  keep as frozen; RQ5 reported at block level only
  [ ] M3-B  chunk density per side                 ← preparer's construct recommendation
  [ ] M3-C  chunk size + chunk ratio basis
  [ ] M3-D  drop chunk counts                      (not recommended; loses RQ5's core)
  [ ] M3-E  residualize on pair_log_size           (not recommended; estimated quantity in design)
  [ ] M3-A + M3-B combined                         (most conservative)
  [ ] defer until NB07 items 6-10 are available
  [ ] other: ______________________________________________

  applies to: M3 only                blocks RQ3/RQ4? NO

  consistency check with R1: if M3-B is adopted, does the same length-normalization
  reasoning apply to script_switch_count?     [ ] yes  [ ] no  [ ] n/a under chosen R1


### R3 — ID-03  source / domain

  [ ] ID3-A  composite cell control; pure-source and pure-domain language forbidden
  [ ] ID3-B  ID3-A plus a named, bounded 025-other vs 026-other descriptive contrast
             ← preparer's recommendation
  [ ] ID3-C  attempt the domain + source_id additive sensitivity
             (requires a separate identifiability check first; NOT run)
  [ ] other: ______________________________________________

  NOT resolvable by NB07 — structural. Decision is about reporting, not identification.


### R4 — ID-04  translation direction

  [ ] ID4-A  retain all three levels including UNKNOWN
  [ ] ID4-B  ID4-A plus explicit "identified from 025 only" statement on every
             direction interpretation                       ← preparer's recommendation
  [ ] ID4-C  schedule KNOWN_DIRECTION_ONLY as an NB11 sensitivity
  [ ] ID4-D  collapse or drop UNKNOWN     — NOT AVAILABLE, forbidden by RD-FAST-G5-01 §7
  [ ] other: ______________________________________________


### R5 — carry-forward notes (acknowledge; no choice required)

  [ ] SPEC-01 acknowledged — held-out D-02 variables stay out of primary matrices;
              reopening is an NB11 sensitivity decision, never a mid-analysis addition
  [ ] SPEC-02 acknowledged — Outcome B's M1 conditions on logCR and logBDR; NB09 must
              say so when reporting IR-02


### R6 — sequencing

  [ ] NB07 executes first; R1 and R2 revisited with NB07 items in hand
  [ ] R0 alone is sufficient to unblock NB09; NB07 proceeds in parallel
  [ ] other: ______________________________________________
```

---

## 8. Standing prohibitions until the template is returned

```
NB09 is NOT started
M0 / M1 / M2 / M2A / M3 are NOT fitted
no coefficient, p-value, partial R2 or delta R2 is produced
no feature is chosen on the basis of any association with Y_A or Y_B
no D-02/D-03/D-04/D-05 regeneration is proposed or performed
the frozen G5 matrices are NOT edited — any adopted option becomes a
  documented protocol amendment with its own pre-result commit, not a silent change
```

Any option adopted from §7 changes `G5_DIAGNOSTIC_PROTOCOL_v001`. The amendment must be persisted
and pushed **before** NB09 executes, on the same pre-result discipline used for the G5 freeze, and
the affected rank / condition-number / VIF diagnostics must be re-measured on the amended matrix.
An option cannot be adopted and fitted in one step.

---

**Prepared**: 2026-08-18 KST, Claude-B. Not frozen. Not a decision. No canonical science state
was modified.
