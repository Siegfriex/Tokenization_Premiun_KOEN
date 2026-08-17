# KOEN Preliminary Results Axis — V1

```
Status:     PRELIMINARY_RESULTS_DISCOVERY_V1
Authority:  NON_CANONICAL / SUBORDINATE_TO KOEN-TP-RS-001
run_id:     VIZ_CASEBOOK_20260817T151317
Base SHA:   2d99c906c7c94a9ce2ee2e0ff9dc01cf61998c3a
```

V1 is permitted to assert **five axes and no more**. Every number below is transcribed
from the frozen notebook; nothing was recomputed for this document.

Evidence classes are defined in [`KOEN_EDA_V1_TRACEABILITY.md`](KOEN_EDA_V1_TRACEABILITY.md).

---

## AXIS 1 — REPRESENTATION REVERSAL

**Evidence:** `[R-FULL]` — `REP_FEATURES_v002.parquet`, N = 3,835,988.

Korean is **shorter than English in code points**, yet **heavier in UTF-8 bytes**. The
two length measures point in opposite directions.

| Quantity | p01 | p05 | p25 | median | p75 | p95 | p99 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `pair_codepoint_ratio` $(C_{KO}/C_{EN})$ | 0.2781 | 0.3333 | 0.4085 | **0.4675** | 0.5385 | 0.6792 | 0.8333 |
| `pair_byte_ratio` $(B_{KO}/B_{EN})$ | 0.6562 | 0.8037 | 0.9848 | **1.1268** | 1.3000 | 1.6333 | 1.9697 |
| `ko_bytes_per_codepoint` | 1.9091 | 2.1333 | 2.3548 | 2.4500 | 2.5000 | 2.5714 | 2.6250 |
| `en_bytes_per_codepoint` | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

Reading:

- Code-point ratio stays below 1.0 through **p99 (0.8333)** — the direction is near-universal.
- Byte ratio crosses 1.0 **between p25 (0.9848) and the median (1.1268)** — so the
  reversal holds for the **majority of the cohort, not for all of it**. Roughly the
  lower quarter of pairs remains below 1.0 in bytes as well.
- The mechanism is visible directly: `ko_bytes_per_codepoint` sits near 2.45 while
  `en_bytes_per_codepoint` is exactly 1.0 through p99.
- `pair_codepoint_diff` median **−39** code points (p01 −188, p99 −3, max +102).

### Prohibited extension

This axis is a statement about **string representation only**. It must **not** be
extended into:

- token premium,
- tokenizer inefficiency,
- any claim about $T_{KO}$ vs $T_{EN}$.

Whether the byte reversal survives tokenization is precisely what AXIS 2 probes and what
V2 must settle.

---

## AXIS 2 — DECOMPOSITION CANDIDATE

**Evidence:** `[R-FULL]` + `[T-SAMPLE40]` (n = 40, 10 per domain).

**Status: PRELIMINARY SIGNAL.**

SSOT §8 identity, verified numerically in V1:

$$\log TP_i = \log \mathrm{CodePointRatio}_i + \log \mathrm{ByteDensityRatio}_i + \log \mathrm{CompressionPenalty}_i$$

Identity error over the 40 pairs: **max 2.78 × 10⁻¹⁶** (against $\varepsilon = 10^{-10}$).
Roundtrip failures: **0 / 40**.

Sample medians of the three components:

| Component | Sample median (n = 40) |
|---|---:|
| $\log \mathrm{CodePointRatio}$ | **−0.8113** |
| $\log \mathrm{ByteDensityRatio}$ | **+0.9004** |
| $\log \mathrm{CompressionPenalty}$ | **+0.1360** |
| $\log TP$ | +0.2007 |

Directional reading — the only reading V1 permits:

- The first two components carry **opposite signs** and largely offset one another;
  their medians sum to **+0.089**.
- The median of $\log CP$ (**+0.1360**) is **larger than that offset sum**, i.e. in this
  probe the byte-normalised tokenizer asymmetry is not a residual detail.
- Medians are **not additive**, so the above is a statement about relative magnitude and
  sign, not an exact accounting of the median $\log TP$.

Per-domain component medians (n = 10 each) — descriptive only:

| domain | $\log TP$ | $\log CR$ | $\log BDR$ | $\log CP$ |
|---|---:|---:|---:|---:|
| dialogue | 0.0589 | −0.8511 | 0.9051 | **−0.0518** |
| general | 0.1987 | −0.9154 | 0.8785 | 0.1574 |
| other | 0.2636 | −0.7704 | 0.9145 | 0.1473 |
| technology | 0.3972 | −0.6362 | 0.8800 | 0.2729 |

Note that `dialogue` shows a **negative** $\log CP$ median in this probe. Direction is
not uniform across strata even at n = 10.

### Prohibited at V1

- population TP estimate
- population $P(TP > 1)$
- any primary inference (§17.1 signed-rank + bootstrap belongs to NB08)
- any statement about SSOT §33 Case A vs Case B as a **conclusion**

The 40-pair observation that $\log CP$ is positive and non-trivial is a **hypothesis
generator** pointing at §33 Case B. Confirming or refuting it requires the
full-population $\log CP$ distribution.

---

## AXIS 3 — MORPHOLOGY

**Evidence:** `[M-SAMPLE40]` — 40-pair recompute, Kiwi 0.23.2 / model 0.23.0, no custom
dictionary; density denominator `eojeol_count` per SSOT §13.6.

Sample medians (n = 40): `eojeol_count` 8.0, `morpheme_density` 2.275,
`particle_ratio` 0.1371, `ending_ratio` 0.2034, `deriv_affix_ratio` 0.0742.
Analyzer warnings: **0 / 40**.

Raw (unconditional) Spearman concordance against the premium quantities:

| | $\log CR$ | $\log BDR$ | morpheme density | particle ratio | ending ratio | deriv-affix ratio |
|---|---:|---:|---:|---:|---:|---:|
| $\log TP$ | +0.647 | −0.007 | +0.054 | +0.098 | **−0.192** | +0.135 |
| $\log CP$ | −0.301 | +0.013 | +0.099 | +0.020 | +0.022 | +0.104 |

Reading:

- Every morphology association is **weak**: $\lvert\rho_s\rvert \le 0.192$.
- $\rho_s(\log TP, \log CR) = +0.647$ is a **deterministic consequence of the §8
  identity**, not a finding (§32 T-06).
- No pair reaches $\lvert\rho_s\rvert \ge 0.8$.

Domain-level morphology composition distance (Jensen–Shannon, base 2, sample means):
minimum **0.00201** (dialogue ↔ general), maximum **0.01710** (general ↔ technology) —
all small.

### Explicit scope statement

**This is not the SSOT RQ4 test.** RQ4 asks whether the morphology block retains
**incremental explanatory value after conditioning** on length, byte, whitespace,
script, domain, direction and source. V1 computes an **unconditional rank
concordance** with no controls whatsoever, and computes **no p-values** (§17.3).

The required comparison is §19.1–19.2:

```
M1 : Y ~ M0 + byte/whitespace/script/surface features
M2 : Y ~ M1 + morphology block
```

evaluated by block-level incremental fit, in V2 / full modelling (NB09). A weak
unconditional $\rho_s$ at n = 40 neither supports nor refutes RQ4.

---

## AXIS 4 — HETEROGENEITY / IDENTIFIABILITY

**Evidence:** `[DESIGN-FULL]` (full-cohort cross-tabulations) + `[T-SAMPLE40]`.

Three strata axes are kept distinct: `domain`, `logical_corpus`, `translation_direction`.

Full-cohort `domain × logical_corpus` (N = 3,835,988):

| domain | 025 | 026 |
|---|---:|---:|
| dialogue | 516,162 | 0 |
| general | 804,291 | 0 |
| other | 1,165,510 | 990,120 |
| technology | 0 | 359,905 |

Full-cohort `domain × translation_direction`:

| domain | EN_TO_KO | KO_TO_EN | UNKNOWN |
|---|---:|---:|---:|
| dialogue | 254,955 | 247,947 | 13,260 |
| general | 449,606 | 354,654 | 31 |
| other | 568,728 | 1,549,646 | 37,256 |
| technology | **0** | 359,905 | 0 |

Additional structural observation: `sentence_type` takes **exactly one level** across all
3,835,988 rows, so it carries zero variance and cannot function as a control variable.

Consequences V1 is allowed to state:

- Three of four domains are confined to a single `logical_corpus`.
- `technology` is additionally confined to a single translation direction.
- Therefore the per-domain $\log TP$ ordering in AXIS 2 (dialogue 0.059 < general 0.199 <
  other 0.264 < technology 0.397) **cannot be read as a domain effect**; corpus and
  direction move with it.

### Critical scope limit — `logical_corpus` ≠ `source_id`

V1 cross-tabulated `domain × logical_corpus`. `logical_corpus` is an operational
grouping; it is **not** the SSOT `source_id` stratification variable (§9.2).

**V1 must not be described as having identified source confounding.** V1 identified a
*corpus*-level structural overlap and a direction-level degeneracy. Whether `source_id`
is confounded with `domain` — the actual Gate G-ID question of §20.2 — was **not tested**
by V1. See `[NOT-ESTABLISHED]` N5 and caveat **C3**.

V2 / Gate G-ID must re-verify:

```
domain × source_id
domain × translation_direction
source_id × translation_direction
+ condition number, VIF / generalized VIF, zero-variance screen
```

---

## AXIS 5 — BOUNDARY REGIONS

**Evidence:** `[R-FULL]`.

V1 proposes the following regions as **candidate targets** for full tokenization, the
NB06 regex-chunk audit, and the canonical NB07 extreme audit. These are proposals, not
findings.

| Region | Full-population evidence |
|---|---|
| **Ultra-short pairs** | `ko_codepoint_count` min 1, p01 6, p05 11; `ko_eojeol_count` min 1, p01 1, p05 3 |
| **Mixed script** | `ko_hangul_share` min 0.0 (KO side with no Hangul exists); `en_bytes_per_codepoint` max 2.5088 (EN side carrying non-ASCII) |
| **High script switching** | `ko_script_switch_count` median 0, p95 2, p99 6, **max 34**; `en_script_switch_count` max 42 — a rare, heavy tail |
| **Grapheme / code-point disagreement** | `ko_grapheme_count` and `ko_codepoint_count` are identical at every reported quantile (1, 6, 11, 23, 36, 66, 103, 122, max 684); disagreement is therefore rare and needs targeted search rather than quantile screening |
| **Extreme ratio tails** | `pair_codepoint_ratio` max 60.0; `pair_byte_ratio` min 0.0539, max 144.0; `pair_codepoint_diff` max **+102** (the rare direction where KO is longer in code points) |
| **High punctuation / symbol** | `ko_punctuation_share` p99 0.2222, max 0.8000; `ko_symbol_other_share` p99 0.1429, max 0.7500 |

Per SSOT §16.3, extreme values are **not deleted**. V1 removed nothing: its own
40-pair rubric returned 38 `EXPECTED`, 2 `PLAUSIBLE_EXTREME`, and zero
`MEASUREMENT_WARNING` / `SUSPICIOUS` / `HARD_INVALID`.

---

## Axis-to-Gate map

| Axis | Feeds | Settles |
|---|---|---|
| 1 | §8 decomposition framing, §16.1 | nothing |
| 2 | RQ2, §33 Case selection, NB07/NB08 | nothing |
| 3 | RQ4 design (M1 vs M2), NB09 | nothing |
| 4 | §20.2 Gate G-ID agenda, §32 T-04 | nothing |
| 5 | §16.3 extreme audit, NB06 | nothing |

V1 closes no Gate and settles no research question. It sets the agenda that V2 must
answer from full-population D-03 and D-04 artifacts.
