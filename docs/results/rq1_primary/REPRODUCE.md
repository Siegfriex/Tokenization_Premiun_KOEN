# Reproducing the RQ1 result

Three levels, in increasing order of what they require from you.

| Level | What it reproduces | Needs D-04? | Needs raw text? |
|---|---|---|---|
| [A](#level-a--figures-only) | every figure in this package | no | no |
| [B](#level-b--full-statistical-re-execution) | the RQ1 statistics themselves | **yes** | no |
| [C](#level-c--full-pipeline-provenance) | D-04 itself, from source | — | **yes** |

> **Honest statement up front.** The canonical D-04 artifact is **not** in this Git repository. It is
> excluded by `.gitignore:27` (`data/registry/**`). A `git clone` alone therefore reproduces Level A
> only. Levels B and C require artifacts or source data you must obtain separately. This document
> does not pretend otherwise.

---

## Level A — figures only

Rebuilds all five figures from `data/RQ1_VISUAL_DATA_v001.json`, a committed file containing
**aggregate values only** — histogram bin counts, the most frequent exact outcome values, quantiles,
and the frozen test/bootstrap results copied from the analysis artifacts. It contains no Korean or
English text, no `pair_id`, and no morpheme surfaces.

```bash
cd docs/results/rq1_primary
./reproduce.sh figures
```

This runs `build_rq1_figures.py --mode figures` and then re-hashes every output against
`NB08_RQ1_VISUAL_MANIFEST_v001.json`.

**Requirements**: Python 3.12 with `matplotlib`, and a Korean font that actually carries Hangul
glyphs. The builder searches `Noto Sans CJK KR` → `Noto Sans KR` → `NanumGothic` in that order and
**fails loudly** if none is installed rather than silently rendering boxes.

```bash
# Debian/Ubuntu
sudo apt-get install fonts-nanum        # or fonts-noto-cjk
```

**Expected**: `FIGURE_REPRODUCTION_PASS`, and 15 files (5 figures × SVG/PNG/PDF) whose SHA-256 values
match the manifest.

> The builder suppresses creation-date metadata in SVG and PDF, so repeated runs in the same
> environment are **byte-identical** (verified: 15/15 files). Across different matplotlib versions or
> a different font file the bytes may still differ; if the hashes differ but the figures render
> correctly, treat it as an environment difference, not a data difference — the numeric content is
> checked separately by `./reproduce.sh verify`.

> **Interpreter**: the script searches `$KOEN_PYTHON` → `$REPO/.venv/bin/python` → the active
> virtualenv → `python3`, picking the first that can import matplotlib, and exits with a clear
> prerequisite message if none can. If you are running from a Git worktree whose root has no
> `.venv`, point it at one:
>
> ```bash
> KOEN_PYTHON=/path/to/Tokenization_KOEN/.venv/bin/python ./reproduce.sh figures
> KOEN_REPO=/path/to/Tokenization_KOEN ./reproduce.sh inference
> ```

### Regenerating the visual data itself

Only needed if you want to re-derive the aggregates from D-04 rather than trust the committed file.
This requires Level B's prerequisites.

```bash
python build_rq1_figures.py --mode extract --repo /path/to/Tokenization_KOEN
```

The extractor verifies the D-04 SHA-256 before reading anything and refuses to run on a mismatch.

---

## Level B — full statistical re-execution

Re-runs the canonical RQ1 inference notebook and compares every result against the frozen values.

### Prerequisite: the D-04 artifact

```
path      data/registry/TOKEN_O200K_BASE_v001.parquet
SHA-256   1c30e3276222dd94885ae4f79fc6ab5c45e4e26226de0afd91fc6b1f7d2c16e7
rows      3,835,988
columns   28
```

Also required: `data/registry/PAIR_REGISTRY_v002.parquet`
(SHA-256 `95f523d11b0e8fcfd761dee949f082e9b4590b919801441fbcfa3426010bec52`), which supplies the
translation-direction and source-stratum columns used by the sensitivity analyses.

**Neither file is in Git.** Obtain them by one of:

1. copying the artifacts from a machine that already holds the canonical registry; or
2. rebuilding them through Level C.

There is no synthetic fallback. `reproduce.sh inference` exits non-zero with a prerequisite message
if D-04 is absent or its hash does not match.

### Environment

The repository's actual environment authority is `pyproject.toml` + `uv.lock` + `.python-version`,
driven by `scripts/setup_environment.sh`. From the repository root:

```bash
npm run setup          # → bash scripts/setup_environment.sh   (requires uv, Python 3.12)
npm run check:env      # → bash scripts/run_env_check.sh
```

`00_environment_repro.ipynb` is the canonical record of the frozen environment, including the
tokenizer artifact hashes and the Korean-font resolution.

### Run

```bash
cd docs/results/rq1_primary
./reproduce.sh inference
```

which executes the canonical notebook headless — the same command the analysis itself used:

```bash
.venv/bin/jupyter nbconvert --to notebook --execute --inplace \
  --ExecutePreprocessor.timeout=2700 --ExecutePreprocessor.kernel_name=python3 \
  notebooks/08_primary_inference.ipynb
```

Runtime is roughly 6–8 minutes: about 2 minutes for the primary protocol and about 100 s for the
source-stratified bootstrap. The notebook's own `POST-PROTOCOL SSOT CLOSEOUT` section opens with a
hard-stop guard that halts if any of 15 frozen primary values fails to reproduce.

### Machine comparison

`reproduce.sh inference` compares the regenerated results against the frozen artifacts on:

```
N · median logTP · pair bootstrap CI · Wilcoxon W · positive/negative/tie counts
tie-aware robustness · known-direction result · source-stratified result
bootstrap seeds · D-04 SHA-256
```

**Expected**: `STATISTICAL_REEXECUTION_PASS`. Only wall-clock fields (timestamps, runtimes) may
differ; an independent re-execution has already been recorded as bit-identical on every statistic in
`ssot_nb01/08_NB08_RQ1_REPRODUCTION_CHECK.md`.

---

## Level C — full pipeline provenance

What it takes to build D-04 from source, stated accurately rather than assumed.

### The chain

```
notebooks/00_environment_repro.ipynb      environment + tokenizer/analyzer artifact freeze
        ▼
notebooks/01_build_pair_registry.ipynb    raw sources → PAIR_REGISTRY_v001
        ▼
notebooks/02_normalize_and_qc.ipynb       normalization + QC → PAIR_REGISTRY_v002
        ▼
notebooks/03_representation_features.ipynb  D-02 REP_FEATURES_v002
        ▼
notebooks/05_o200k_measurement.ipynb      D-04 TOKEN_O200K_BASE_v001      ← the RQ1 input
        ▼
notebooks/08_primary_inference.ipynb      RQ1 inference
```

**`04_morphology_features.ipynb` (D-03) is not an input to RQ1.** It was verified separately under
gate G4 and feeds RQ4, not RQ1. Confirmed by inspection: the RQ1 notebook references
`TOKEN_O200K_BASE_v001` and `PAIR_REGISTRY_v002` and never references `MORPH_FEATURES`.
`REP_FEATURES` is likewise not referenced by NB08 directly.

### Raw source data

The corpus is AI Hub licensed material and is a **local prerequisite**, not a repository asset:

- 일상생활 및 구어체 한-영 번역 병렬 말뭉치 데이터 (dataSetSn=71265)
- 기술과학 분야 한-영 번역 병렬 말뭉치 데이터 (dataSetSn=71266)
- 한국어-영어 번역(병렬) 말뭉치 (aidata/87)

See `docs/evidence/aihub/AIHUB_KOEN_SOURCE_EVIDENCE_2026-08-16.md` for the full provenance record.
Access is subject to AI Hub's terms; this repository does not redistribute the corpus.

### What this means for reproducibility claims

- **Reproducible from Git alone**: figures (Level A) and artifact-consistency verification.
- **Reproducible with the canonical registry artifacts**: the full RQ1 statistics (Level B).
- **Reproducible from source**: requires separately obtaining the licensed corpus (Level C).

Claiming more than this would be false.

---

## Verification without re-running anything

```bash
cd docs/results/rq1_primary
./reproduce.sh verify
```

Checks that the committed RQ1 artifacts are internally consistent: the values in `README.md`, the
figures' source data, and the manifest all agree with
`ssot_nb01/04_NB08_RQ1_RESULTS_v001.json` and `ssot_nb01/06_NB08_RQ1_SSOT_CLOSEOUT_v001.json`.
Requires no large artifacts.

**Expected**: `RESULT_VERIFICATION_PASS`.
