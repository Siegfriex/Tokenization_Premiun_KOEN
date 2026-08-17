# Claude-B Session Freeze — RQ1 Publication Package

> **Date**: 2026-08-17 KST
> **Role**: Research / Statistics / Result Communication
> **Mode**: `RQ1_PACKAGE_CLOSEOUT_ONLY` — no new inference, no new RQ1 numbers, no main merge.

---

## 1. Git state

```
canonical science main   a31a4c27417b93567bb6e261b6225813aaa5f66e
RQ1 closeout             3f4e8210739205389cfb0c7853f5384015020382
primary result           502bc128f6b5855f1648802cc990b715808f26f3
decision / cohort / protocol
                         e72274086a7e9c611c9014e6b5612df0e69dae30
                         9b695307c0551be84d4d6c374646bfe001b7b3a9
                         86521fdf04839d2e3e8e5db8e15a08ea067871e3

package branch           results/rq1-publication-visuals-20260817
starting remote SHA      6dc8c7175ef49fcba18e344d3a762f202b993c12
```

The local branch was one commit behind at session start and was fast-forwarded to `6dc8c71`. No
history was rewritten, nothing was reverted.

## 2. What was completed

Across this working line, on frozen artifacts and under a protocol committed before any result was
observed:

- RQ1 **decision, cohort and protocol** frozen as three separate pre-result commits
- **Primary Wilcoxon signed-rank** inference (`alternative = greater`, `zero_method = wilcox`)
- **Pair-level percentile bootstrap** (B = 2,000, seed 969634713 derived from the plan identifier)
- **Lattice CI diagnostic** — the degenerate interval explained and cross-checked with an exact
  order-statistic interval
- **`CONDITIONAL_NONZERO_SIGN_TEST`** reclassification — the ties-excluded test names a conditional
  parameter, not a distribution-free statement about a median with ties
- **`TIE_AWARE_MEDIAN_SIGN_ROBUSTNESS`** — full `N` denominator, ties counted against the alternative
- **Source-stratified bootstrap sensitivity** (SSOT §17.2; B = 2,000, seed 2856958648)
- **Known-direction sensitivity** (N = 3,785,441)
- **Independent re-execution checks** — a second headless run reproduced every statistic bit-for-bit
- **Publication figures** `NB08-RQ1-V01…V04` + `S01`, each in SVG / PNG 300 dpi / PDF
- **Korean interpretation** document, 14 sections
- **Manuscript-ready English** — Results and Methods paragraphs, table-ready values, figure captions,
  limitation sentence
- **Level A / B / C reproducibility documentation** with honest prerequisites
- **Visual manifest** with per-file hashes
- **Package verifier** (`verify_package.py`) and orchestration wrapper (`reproduce.sh`)

## 3. Primary result

```
N                 3,835,988
median logTP      0.28768207245178085      = ln(4/3)
TP scale          1.3333333333333333       = 4/3

positive TP > 1   3,375,095      87.9850 %
tie      TP = 1     196,718       5.1282 %
negative TP < 1     264,175       6.8868 %
```

Verified against the frozen artifacts at freeze time: **0 mismatches**.

## 4. Statistical interpretation

Read in this order — the p-value is last, and least informative at this sample size.

1. **Effect magnitude.** The median pair needs 4 Korean tokens per 3 English ones. The value sits
   exactly on a small integer ratio because the outcome is a ratio of integer counts.
2. **Prevalence.** 87.99 % of pairs point the same way, so the result describes the distribution
   rather than a tail dragging an average.
3. **Robustness.** The direction holds with all 196,718 ties counted against it, on the
   known-direction subset, and under source-stratified resampling.
4. **CI.** Degenerate at `ln(4/3)` because 123,040 pairs (3.21 %) sit exactly at the median and the
   median rank falls inside that point mass. An exact order-statistic interval agrees. This is
   discreteness, **not** precision.
5. **p-value.** `p < 1e-300`. At N ≈ 3.8 M, significance carries little information.

## 5. Claim boundary

**Allowed**: under the fixed `o200k_base` raw-text Track A configuration and the defined final paired
KO–EN cohort, the pair-level median log tokenization premium is positive and the median TP scale is
4/3, with 87.99 % of pairs positive, surviving the stated robustness checks.

**Forbidden**: causal claims of any kind · generalization to other tokenizers · morphology as the
cause · UTF-8 as a direct cause of a 33 % premium · reasoning-quality claims · universal API pricing
claims · source or domain as the cause · "every pair has TP = 1.333" · reporting the degenerate CI as
precision · presenting the median pair-level premium as an aggregate corpus token ratio.

## 6. Reproducibility

| level | scope | status |
|---|---|---|
| **A** | figures from committed aggregate data; no D-04, no raw text | `FIGURE_REPRODUCTION_PASS` (35/35) |
| **B** | full statistical re-execution; requires canonical D-04 | available — D-04 present locally at the expected hash; **not re-run tonight** (closeout mode forbids new inference) |
| **C** | D-04 from source; requires the AI Hub licensed corpus | documented, not attempted |

Package consistency check at freeze: `RESULT_VERIFICATION_PASS` (56/56).

D-04 is **not** in Git (`.gitignore:27 data/registry/**`), so a plain clone reproduces Level A only.
This is stated in `REPRODUCE.md` rather than glossed over.

## 7. Files produced

```
docs/results/rq1_primary/
├── README.md                              authoritative package landing page
├── RQ1_INTERPRETATION_KO.md               Korean statistical interpretation
├── RQ1_PAPER_TEXT_EN.md                   manuscript-ready English
├── REPRODUCE.md                           Level A / B / C
├── build_rq1_figures.py                   extract / figures modes
├── verify_package.py                      package verifier
├── reproduce.sh                           orchestration wrapper
├── NB08_RQ1_VISUAL_MANIFEST_v001.json     hashes + provenance
├── data/RQ1_VISUAL_DATA_v001.json         aggregates only, no raw text
└── figures/                               5 figures × SVG / PNG / PDF

docs/handoff/
└── 2026-08-17_2233_CLAUDE_B_RQ1_PACKAGE_SESSION_FREEZE.md   (this file)
```

Science-of-record artifacts, produced earlier and unchanged tonight, live in `ssot_nb01/` on
canonical `main`.

## 8. Unresolved package-level review

```
ROOT_README_MODIFIED_ON_RESULT_BRANCH = YES
ROOT_README_MERGED_TO_MAIN            = NO
ROOT_README_SCOPE_REVIEW_REQUIRED     = YES
```

Commit `6dc8c71 "Update README.md"` on this branch rewrites the **repository-root** `README.md`
(+332 / −58) toward an RQ1 landing page. It is not part of the package work and was not authored in
this working line. It was left exactly as found tonight — not modified, not reverted, not merged.

Whether the canonical repository README should become an RQ1 landing page is a Research Director
decision. The authoritative package README remains `docs/results/rq1_primary/README.md`.

## 9. Repo-level known loose ends

**`RD-SSOT-CANONICAL-RETURN-01`**

```
branch   docs/ssot-canonical-return-20260817
SHA      e92701289edec339fc2f6eb7b7a8c1292190815e
```

Not observed on canonical `main` at freeze time. Integration review required next session.

**Canonical working tree is behind.** `/home/sieg/projects-wsl/Tokenization_KOEN` has local `main` at
`07d132e` while `origin/main` is `a31a4c2`. Because the venv resolves `tokenization_premium` from
that tree via an editable install, the modules NB06 added (`chunking`, `telemetry`) are not importable
there and the test suite cannot be collected cleanly. This is an environment condition, not a code
defect — the modules exist at `a31a4c2`. Fast-forward that tree before the next canonical run.

**D-05 location.** `CHUNK_O200K_BASE_v001.parquet` exists only in the `KOEN_nb06_d05` worktree, at the
expected hash. `data/registry/**` is git-ignored, so each worktree holds its own copy. It must be
placed in the canonical tree before NB09 executes from there.

**Uncommitted G5 exploration.** A G5 readiness working line exists in the `KOEN_g5` worktree on
branch `research/g5-analysis-readiness-20260817`. It was **stopped mid-session** when tonight's
closeout instruction arrived and is **not committed, not pushed, and carries no adjudication**. It
must not be treated as a G5 result. Either discard it or re-derive it from the post-integration
canonical `main` next session.

## 10. Next canonical handoff

1. `git fetch origin --prune`
2. Review and integrate `RD-SSOT-CANONICAL-RETURN-01` (`e927012…`)
3. Keep the RQ1 result branch **frozen** — do not resume work on it
4. Do **not** merge the root README automatically; it needs a Director scope decision
5. Fast-forward the canonical working tree and place D-05 there
6. Create a **fresh** `research/g5-analysis-readiness-*` branch from the resulting canonical `main`
7. Begin formal G5 only after Director confirmation

---

**Frozen**: 2026-08-17 KST, Claude-B.
