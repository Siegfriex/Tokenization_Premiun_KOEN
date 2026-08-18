# PRE-NB10 — Leakage Grouping Contract v001 (DESIGN)

> Artifact ID: `PRE_NB10_GROUPING_CONTRACT_v001`
>
> Status: `DESIGN` · `NOT_FROZEN` · `NOT_A_DECISION` · `NO_SPLIT_PRODUCED` · `NO_MODEL_FITTED`
>
> Author: Claude-A (Engineering / Reproducibility)
> Prepared: 2026-08-18 17:35 KST
>
> Branch: `impl/pre-nb10-readiness-20260818`
> Base: `1b212986527a273301c5fefdf87a41e7fb33dd37`
>
> Authority: `KOEN-TP-RS-001` §23.2 · `LR-01` · `CR-FAST-G5-SPLIT-RELOCATION-01`
> (split manifest and near-duplicate grouping relocated from G5 to PRE-NB10, `LR-01` not weakened)
>
> This is an `A-*` engineering design. It is not an `RD-*` decision and does not become one.

```
PREDICTIVE_MODEL_FITTED = NO
TEST_SET_RESULT         = NO
SPLIT_ASSIGNED          = NO
HEAVY_GROUPING_JOB_RUN  = NO      (B holds the heavy WSL slot)
```

---

## 1. Inventory before invention

Every candidate grouping key already present in D-01 was measured on the **analysis cohort**
(`N = 3,835,988`, the D-04 pair-id spine) before any new mechanism was considered.

### 1.1 Existing keys are all singleton on the cohort

| key | nulls | distinct | singleton | non-singleton | rows in NS | max group |
|---|---:|---:|---:|---:|---:|---:|
| `duplicate_group_id` | 0 | 3,835,988 | 3,835,988 | **0** | 0 | 1 |
| `representative_pair_id` | 0 | 3,835,988 | 3,835,988 | **0** | 0 | 1 |
| `analysis_representative_pair_id` | 0 | 3,835,988 | 3,835,988 | **0** | 0 | 1 |
| `source_record_id` | 0 | 3,835,988 | 3,835,988 | **0** | 0 | 1 |
| `raw_locator` | 0 | 3,835,988 | 3,835,988 | **0** | 0 | 1 |
| `source_native_id` | **3,835,988** | 0 | — | — | — | — |
| `source_native_sid` | **3,835,988** | 0 | — | — | — | — |
| `raw_file_sha256` | 0 | 6 | 0 | 6 | 3,835,988 | 1,200,025 |

`duplicate_disposition` is `REPRESENTATIVE` for all 3,835,988 cohort rows and
`analysis_eligible_exact_dedup` is `true` for all of them.

```
CURRENT_DUPLICATE_GROUP_NON_SINGLETON_SHARE = 0.00%
```

**`duplicate_group_id` does not implement `LR-01`.** It implements exact-pair de-duplication, and
that de-duplication has already been applied — so on the cohort it is, by construction, a column of
unique values. `raw_file_sha256` has six levels and is a file identifier, not a leakage unit.

### 1.2 Why that is not a failure of D-01

Measured on the **full** D-01 population (5,652,925 rows), the pre-dedup grouping is real and
non-trivial:

```
distinct duplicate_group_id      5,436,099
non-singleton groups                96,377   covering 313,203 rows, max group 5,508
duplicate_disposition            REPRESENTATIVE 5,436,099 · NON_REPRESENTATIVE_DUPLICATE 216,826
```

And the collapse is complete:

```
pre-dedup non-singleton groups represented in the cohort : 93,876
maximum cohort rows contributed by any one such group    : 1
such groups contributing MORE THAN ONE cohort row        : 0
```

Exact duplicates therefore **cannot** cross a split boundary — not because a grouping key prevents
it, but because only one member of each exact-duplicate group survives into the cohort. That is a
structural guarantee, and it is the one part of `LR-01` that is already satisfied.

### 1.3 What is *not* satisfied

De-duplication was performed on the **pair**. It does not touch families where one side repeats and
the other varies. Measured on the cohort with MD5 of the analysis text:

| grouping | distinct | singleton | non-singleton | rows in NS | share | max |
|---|---:|---:|---:|---:|---:|---:|
| KO+EN pair hash | 3,835,988 | 3,835,988 | 0 | 0 | 0.00% | 1 |
| KO-side hash | 3,784,963 | 3,755,874 | 29,089 | 80,114 | **2.09%** | 285 |
| EN-side hash | 3,705,241 | 3,612,374 | 92,867 | 223,614 | **5.83%** | 136 |

Every one of the 29,089 repeated-KO groups has more than one distinct EN, and every one of the
92,867 repeated-EN groups has more than one distinct KO. These are one-to-many translation
families — the same source sentence carrying several accepted counterparts. A model trained on one
member and evaluated on another has seen the input side verbatim.

```
EXISTING_GROUP_KEYS_SUFFICIENT = NO
```

---

## 2. Proposed grouping contract

### 2.1 Definition

Two cohort pairs belong to the same leakage group if they share a normalised KO text or a normalised
EN text, transitively.

```
node        pair_id
edge        pair_i ~ pair_j  iff  norm_ko(i) = norm_ko(j)  or  norm_en(i) = norm_en(j)
group_id    connected component of that relation
```

The grouping is a **connected-component closure**, not a single-key equality, because the relation
chains: A shares its KO with B, B shares its EN with C, so A and C are in one family and must not be
separated.

### 2.2 Two normalisation tiers, both model-free

```
TIER-1  exact        norm(t) = t                                   (the analysis text as stored)
TIER-2  normalised   norm(t) = md5(regexp_replace(lower(t), '[^0-9a-z가-힣]', '', 'g'))
```

Tier-2 casefolds and removes every non-alphanumeric character, so it absorbs case, punctuation and
whitespace variants. It introduces **no model, no tokenizer and no embedding** — it is deterministic
string normalisation plus MD5, auditable line by line and reproducible anywhere.

Measured coverage on the cohort:

| tier | linked rows | share |
|---|---:|---:|
| Tier-1 exact | 276,100 | 7.20% |
| Tier-2 normalised | 371,184 | **9.68%** |
| found only by Tier-2 | +95,084 | +2.48% |

Tier-2 additionally reveals **23,988 groups covering 59,060 rows that are identical *pairs* up to
case, punctuation and whitespace** — genuine near-duplicates that exact de-duplication kept as
distinct rows. Those are exactly the objects `LR-01` exists to control, and they are reachable
without any new semantic method.

**Recommendation: adopt Tier-2 as the binding grouping.** Tier-1 is retained as a reported
sub-measurement so the increment attributable to normalisation is visible rather than buried.

### 2.3 Realised group structure (Tier-1 measured; Tier-2 to be measured in the heavy pass)

```
non-singleton groups           100,441
rows in non-singleton groups   276,100   (7.20%)
singleton groups             3,559,888
TOTAL groups                 3,660,329
group size  p50 2 · p90 3 · p99 8 · max 37,849
```

Corroboration of `LR-01`: **17,187 groups straddle the upstream TRAIN/VALIDATION boundary**,
consistent in order of magnitude with the 25,247 upstream shared pairs `LR-01` recorded. **12,648
groups span more than one `source_domain_cell`**, which constrains stratified assignment — see §3.3.

### 2.4 The giant component — disclosed, not hidden

One component holds **37,849 rows** (0.99% of the cohort; **5.19% of a 19% holdout**), against a
median group size of 2. It is chained through short strings:

```
giant component   19,257 distinct KO hashes · 12,920 distinct EN hashes
KO length  min 1 · p50 7 · p90 13 · max 43       (all linked rows: KO p50 20)
EN length  min 1 · p50 13 · p90 29 · max 122     (all linked rows: EN p50 40)
```

High-multiplicity hubs are short: the KO hubs with multiplicity ≥ 100 have median length 14, and the
≥ 20 bucket median 8. Excluding short texts from *linking* would shrink coverage from 7.20% to 4.95%
at a 20-character floor.

**No length threshold is proposed.** Excluding short strings would *reduce* leakage protection to
make the split tidier, which is the wrong trade at a leakage gate, and any threshold would be an
unfounded free parameter. The giant component is therefore kept whole and assigned as one unit; the
resulting holdout imbalance is a **reported quantity in the split manifest**, not a silently
absorbed one. If the Director prefers a threshold, it is a decision, not an engineering default.

### 2.5 What this contract does not cover

Tier-2 catches pairs identical up to surface normalisation. It does **not** catch paraphrases that
differ lexically on both sides — reordered clauses, synonym substitution, genuine retranslation with
no exact or normalised match on either side. That residual is **unmeasured**, and measuring it would
require a new mechanism (shingle MinHash / LSH, or an embedding model).

```
NEW_SEMANTIC_METHOD_REQUIRED = NO   for the Tier-1 + Tier-2 contract proposed here
                               OPEN for a further near-duplicate tier — see §5
```

---

## 3. Split policy

### 3.1 Primary holdout

```
final holdout target   19%          (SSOT §23.2 permits 15–20%; see §3.1.1 — NOT the band edge)
unit of assignment     group_id     never pair_id
training share         81%
tuning / CV            inside the training partition only
CV balancing bins      derived from the TRAINING target distribution only, never the full cohort
```

#### 3.1.1 Why the target is 19% and not 20%

Caught by the contract's own test suite rather than by inspection. Realised holdout share fluctuates
about the target, and on this cohort the fluctuation is **not** hash noise — it is dominated by the
37,849-row giant component (§2.4), which is assigned as one unit and moves the share by roughly
+0.8pp when it lands in holdout.

```
target 0.20  ->  realised 0.1980 (giant in train) .. 0.2079 (giant in holdout)   VIOLATES the band
target 0.19  ->  realised 0.1881                  .. 0.1980                      inside the band
target 0.18  ->  realised 0.1782                  .. 0.1881                      inside the band

remaining ~3.66M groups contribute sd ≈ 0.0002, an order of magnitude smaller
```

Targeting the band edge would breach SSOT §23.2 roughly whenever the giant component lands in
holdout. **19% is chosen so that both outcomes of that single coin flip stay inside the band**, with
the realised share recorded in the manifest either way. The alternative — re-salting until the share
fits — is rejected: it is outcome-blind but it is still selection on a realised statistic, and it
would make the split depend on a rejection loop rather than on one frozen salt.

### 3.2 Assignment rule — deterministic, outcome-blind

```
h(group_id) = first 8 bytes of sha256(SPLIT_SALT || group_id)  interpreted as uint64
assign to HOLDOUT iff  h(group_id) / 2^64  <  0.19
SPLIT_SALT frozen in the split manifest before any assignment is computed
```

The hash consumes **only the frozen `group_id`**. No outcome value, no `Y_A`, no `Y_B`, no feature
and no model output participates in holdout membership. Assignment is reproducible from the salt
alone and requires no stored index.

### 3.3 Stratification, and an honest limit

Stratifying within `source_domain_cell` is desirable so both partitions retain support in all five
realised cells. But **12,648 groups span more than one cell**, so a group has no unique stratum.

Proposed resolution, stated rather than assumed: assign each group by the hash above using its
**modal cell** (ties broken by the lexicographically smallest cell) purely to *choose the salt
stream*, while the group itself moves whole. Cell support in each partition is then a **measured and
reported** outcome, not an enforced quota. Enforcing exact per-cell quotas would require splitting
groups, which is precisely what `LR-01` forbids.

```
GROUP_INTEGRITY  >  STRATUM_QUOTA        (non-negotiable ordering)
```

### 3.4 Secondary OOD

```
SOURCE_HELD_OUT = SECONDARY_OOD_ONLY
```

There are two realised sources and `other` is the only domain occurring under both, so a
source-held-out split confounds source with domain almost completely — G5 recorded
`SOURCE_DOMAIN_IDENTIFIABILITY = COMPOSITE_CELL_CONTROL_ONLY`. A source-held-out test is therefore
reportable as a **secondary out-of-distribution probe** and **never replaces** the primary
group-aware pair holdout. Feasibility is assessed separately and its result does not gate the
primary split.

---

## 4. `LR-01` test plan — fail-closed

Every check is a HARD FAIL. All are computed on identifiers and hashes; none reads or persists raw
text.

| # | test | requirement |
|---|---|---|
| `LR01-1` | no `group_id` appears in both train and holdout | count = 0 |
| `LR01-2` | no exact normalised KO hash crosses the boundary | count = 0 |
| `LR01-3` | no exact normalised EN hash crosses the boundary | count = 0 |
| `LR01-4` | no Tier-1 exact KO or EN hash crosses the boundary | count = 0 |
| `LR01-5` | no pre-dedup `duplicate_group_id` crosses the boundary | count = 0 |
| `LR01-6` | no `analysis_representative_pair_id` family crosses the boundary | count = 0 |
| `LR01-7` | every cohort row receives exactly one assignment | count = N, no duplicates, no nulls |
| `LR01-8` | holdout share within the SSOT §23.2 band | 0.15 ≤ share ≤ 0.20 |
| `LR01-9` | assignment reproduces bit-for-bit from the frozen salt | re-derived == persisted |
| `LR01-10` | no outcome column participates in the assignment code path | static check |

`LR01-1` through `LR01-6` are the enforced group keys of §7 of the assignment brief. Any crossing is
`HARD FAIL` and no split manifest is frozen.

---

## 5. `METHOD_DECISION_REQUIRED` — bounded, one question

The Tier-1 + Tier-2 contract needs no new method and is recommended for adoption as-is. A further
tier does need one, and that is a scope decision rather than an engineering default.

```
QUESTION   Is surface-normalised exact matching sufficient LR-01 coverage for NB10,
           or must a lexical near-duplicate tier be added?

OPTION A   Tier-1 + Tier-2 only.
           Model-free, deterministic, fully auditable, 9.68% of the cohort grouped.
           Residual risk: lexically divergent paraphrases remain ungrouped, size unmeasured.
           Cost: none beyond the single grouping pass already planned.

OPTION B   Add a character-shingle MinHash / LSH tier over the normalised text.
           Still model-free and deterministic; introduces two free parameters
           (shingle size, Jaccard threshold) that must be frozen before measurement.
           Cost: one additional full-population pass; grows the giant component further.

OPTION C   Add an embedding-based semantic tier.
           Introduces a new model dependency and a new frozen artifact into a project whose
           tokenizer identity is deliberately pinned. NOT recommended by this lane —
           it enlarges the reproducibility surface to solve a residual of unknown size.
```

Recommendation: **Option A now**, with the residual disclosed as a stated NB10 limitation, and
Option B revisited only if NB10 predictive performance looks implausibly high — which would itself
be evidence of remaining leakage. Option C is not proposed.

Measuring the residual to size Option B is itself an additional full-population pass and is **not**
started while B holds the heavy slot.

---

## 6. Execution status

```
branch                          impl/pre-nb10-readiness-20260818
base                            1b212986527a273301c5fefdf87a41e7fb33dd37
inventory queries run           aggregation and union-find over identifiers/hashes only
heavy full-population grouping  NOT STARTED — B holds the heavy WSL slot
split assignment                NOT COMPUTED
split manifest                  SCHEMA ONLY (02_SPLIT_MANIFEST_SCHEMA_v001.json)
raw text persisted              NO
```

Next, on Director confirmation of §5 and release of the heavy slot: freeze `SPLIT_SALT`, run the
single grouping pass under `ENG-OBS-001`, emit the split manifest, and run the `LR-01` suite. No
predictive model is fitted at any point in this lane.
