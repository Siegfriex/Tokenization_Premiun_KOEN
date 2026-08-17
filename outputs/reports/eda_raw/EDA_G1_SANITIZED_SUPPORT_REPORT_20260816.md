# EDA G1 Sanitized Support Report — 2026-08-16

## A. Old-branch exposure audit

- Read-only audit: `outputs/reports/eda_raw/EDA_REPOSITORY_EXPOSURE_AUDIT_20260816.md`.
- Audited target: `eda/g0-raw-notebooks@4e56fdbc70c0571e9eeb912c61816885ad5477a7`, including reachable committed versions.
- Old branch was not merged, cherry-picked, rewritten, deleted, or force-pushed.

## B. Sanitized file allowlist

- `notebooks/exploratory/raw/*_G1_SANITIZED.ipynb`
- `notebooks/exploratory/evidence/AIHUB_LOCAL_RECON_EVIDENCE_EXPORT_20260816.ipynb`
- `outputs/eda_raw/g1_support/**` excluding caches and font caches
- `outputs/figures/eda_raw/g1_support/**`
- `outputs/aihub_recon_g1/**` excluding font caches
- `outputs/reports/eda_raw/**`
- `outputs/manifests/eda_raw/**`

All dataset artifacts were recomputed from immutable local raw roots. No contaminated Git blob was used as a data source.

## C. Omitted unsafe files

- Every `*_samples.csv` and every raw KO/EN preview export was omitted.
- The three old executed notebooks with sentence previews were not ported.
- Old raw-preview producer/generator scripts were not ported.
- No text hash value, pair hash value, raw URL, PII-like value, raw sentence, or recoverable sentence excerpt is allowlisted.

## D. Notebook execution

- `notebooks/exploratory/raw/EDA_RAW_AIHUB_025_G1_SANITIZED.ipynb`: 5/5 code cells executed; 0 error outputs
- `notebooks/exploratory/raw/EDA_RAW_AIHUB_026_G1_SANITIZED.ipynb`: 5/5 code cells executed; 0 error outputs
- `notebooks/exploratory/raw/EDA_RAW_LEGACY_KO_EN_XLSX_G1_SANITIZED.ipynb`: 5/5 code cells executed; 0 error outputs
- `notebooks/exploratory/evidence/AIHUB_LOCAL_RECON_EVIDENCE_EXPORT_20260816.ipynb`: 17/17 code cells executed; 0 error outputs

Validation result: `PASS`. Details: `outputs/manifests/eda_raw/G1_SANITIZATION_VALIDATION_20260816.csv`.

## E. Output hashes

Artifact hashes are recorded in `outputs/manifests/eda_raw/G1_SUPPORT_ARTIFACT_HASHES_20260816.csv`. The manifest excludes itself to avoid self-reference.

## F. New branch SHA

- Branch: `eda/g1-support`
- Released base: `f1b2a901b3bc9a9d759af0698bd0c308ec6e468b`
- Commit SHA and remote ref are authoritative in the final push evidence because a commit cannot embed its own SHA without changing that SHA.

## G. Remaining public-history remediation requirement

The old branch and its raw-text blobs remain reachable. No deletion, history rewrite, or force-push was performed. Public-history remediation remains `AWAIT_OPS_DR_01` and requires Research Director authorization.
