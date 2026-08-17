# KOEN EDA V1 — Retrospective Caveats

```
Status:    KNOWN_LATER_CAVEAT register
Applies to: notebooks/exploratory/EDA_representation_kiwi_o200k_casebook_v1.ipynb
run_id:     VIZ_CASEBOOK_20260817T151317
Base SHA:   2d99c906c7c94a9ce2ee2e0ff9dc01cf61998c3a
```

## Purpose and rule of use

This document records knowledge acquired **after** the V1 execution. Its function is to
tell a later reader **how to read V1**, not to correct V1.

**The notebook is not modified.** No caveat below has been, or may be, back-inserted into
the frozen artifact. If a V1 statement is wrong or incomplete in light of later work,
that wrongness is itself part of the historical record and is preserved.

Everything in this file is external commentary. Nothing here changes a V1 number.

---

## C1 — The o200k layer is an n = 40 probe, not population inference

V1's tokenizer layer is a **40-pair equal-domain probe** (10 per populated domain),
recorded in the notebook as `T_tokenizer = SAMPLE_RECOMPUTED_FOR_VISUALIZATION`.

Therefore:

- V1's `median TP`, `median logTP`, and the count `TP > 1 in 33/40` are **sample
  descriptives**. They are **not** estimates of population TP or of $P(TP>1)$.
- The equal-domain allocation is deliberately **not** proportional to the cohort
  (`other` alone is 2,155,630 of 3,835,988 rows). Any average taken across the 40 pairs
  is therefore weighted unlike the population.
- SSOT §17.1 primary inference — one-sample signed-rank on $\log TP$ with bootstrap CI —
  was **not performed** and could not have been.

**Read V1's tokenizer numbers as direction and order of magnitude only.**

## C2 — The morphology layer is not the full D-03 artifact

At V1 execution there was **no** `MORPH_FEATURES_v001/v002.parquet` full-population
artifact. V1 recomputed morphology for its 40 pairs through the canonical
`morphology_features()` function.

Two consequences:

1. V1 deliberately **withheld the phrase "population percentile"** from the morphology
   and tokenizer layers, applying it only to Representation. That restraint should be
   preserved when quoting V1.
2. The pilot file `.runtime/nb04-pilot/MORPH_FEATURES_PILOT_v001.parquet` was **detected
   in the artifact census but never read**. V1 contains no pilot-derived value. Do not
   describe V1 as "based on the N=1,000 pilot".

Full-population D-03 was executed **after** the V1 base commit. Because V1 pinned its
40 `pair_id`s and their set hash
(`5b4393fb541c3a6dc347fa2422ed25fbfb384eed45a4b98b652ed3f85c8e0ac1`), a direct
join-and-compare against the full artifact is possible and is the intended check.

## C3 — Domain patterns may be confounded, and V1 did not test `source_id`

V1 established, on the **full cohort**, that three of four domains occur in only one
`logical_corpus` and that `technology` carries only one translation direction.

However:

> **`logical_corpus` is not `source_id`.**

V1 cross-tabulated `domain × logical_corpus` and `domain × translation_direction`. It did
**not** cross-tabulate `domain × source_id`, `source_id × translation_direction`, nor
compute condition number / VIF.

Therefore **V1 must not be cited as having identified source confounding.** It surfaced a
corpus-level overlap and a direction-level degeneracy — a strong prompt for Gate G-ID
(§20.2), not a discharge of it.

Any per-domain ordering reported by V1 (including the monotone $\log TP$ ordering
dialogue < general < other < technology) is confounded with corpus, direction and length
and must not be read as a domain effect.

## C4 — `sentence_type` is degenerate in the realized cohort

V1 observed that `sentence_type` takes **exactly one level** (`other`) across all
3,835,988 rows of the final cohort. This is a consequence of the D-01 field contract
(source value if available, else `other` + provenance status), not a data defect.

Implication for later work: `sentence_type` carries **zero variance** and cannot serve as
a stratification or control variable in any model, despite appearing in SSOT §9.2's
stratification list and in the §18 model specifications. This needs an explicit design
decision before M0–M3 are fitted.

## C5 — Do not read extreme morphology values as linguistic complexity

Morphology features on **Q1 ultra-short fragments** are unstable: with very few
morphemes, ratios move in large discrete jumps, and analyzer ambiguity on fragments,
neologisms and proper nouns is a known threat (§32 T-05).

V1's own 40-pair probe returned **zero** analyzer warnings, which should **not** be read
as evidence that the analyzer is reliable in the short-length tail — n = 40 with only a
handful of Q1 items has no power to detect it.

Later morphology audit work may observe analyzer ambiguity concentrated in exactly this
region. Accordingly:

> An extreme morphology value must **not** be automatically interpreted as linguistic
> complexity. Measurement instability is at least as likely an explanation until a
> length-stratified audit says otherwise.

## C6 — Whether V1's patterns survive is an open question for V2

Every V1 axis is a **hypothesis about the full population**, not a result on it. In
particular the following require re-verification against full-population D-03 / D-04:

| V1 pattern | Must be re-checked as |
|---|---|
| $\log CP$ median positive and larger than the $\log CR + \log BDR$ offset (n = 40) | full-population $\log CP$ distribution |
| `dialogue` showing a **negative** $\log CP$ median | stratum-level distribution at full N |
| morphology associations uniformly weak ($\lvert\rho_s\rvert \le 0.192$) | M2 vs M1 incremental fit (§19), not raw $\rho_s$ |
| SSOT §33 leaning toward Case B | Case selection from full-population evidence |

If V2 contradicts a V1 pattern, **V1 is not amended.** The divergence is the finding, and
it is recorded in V2.

## C7 — V1 figure identifiers are local and collide with canonical SSOT IDs

The notebook uses internal identifiers `F05`, `F06A/B`, `F06C/D`, `F07`, `F08`, `F09A`,
`F09B`, `F10`, `F11`, `F12A`, `F12B`.

These are **numbered by notebook section, not by the SSOT figure register.** They do
**not** correspond to canonical figures F01–F09 defined in §16.2 / §35. The strings
overlap while the contents differ — for example V1's `F05` is a sample-percentile
placement panel, whereas SSOT `F05` is "UTF-8 load vs tokenizer compression penalty".

Canonical figure IDs are frozen only at release (§39 checklist, "Figure/table IDs
freeze"), which has not occurred. When citing a V1 figure, always qualify it as
**"V1 internal F-xx"**.

---

## Caveats that do **not** apply

For completeness, two things V1 did correctly and which need no retrospective warning:

- **Exact-decomposition identity.** V1 verified $\lvert \log TP - (\log CR + \log BDR +
  \log CP)\rvert \le 2.78 \times 10^{-16}$ on its 40 pairs, well inside
  $\varepsilon = 10^{-10}$. The arithmetic is sound; only its coverage is limited.
- **Boundary discipline.** V1 issued no Gate verdict, created no QC rule or exclusion,
  removed no extreme case, rendered no raw KO/EN sentence text, and performed no Git
  operation. Its `authority_boundary` record documents this and it holds on inspection.
