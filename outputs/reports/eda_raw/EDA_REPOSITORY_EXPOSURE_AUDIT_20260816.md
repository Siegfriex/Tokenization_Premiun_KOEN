# EDA Repository Exposure Audit — 2026-08-16

| path | artifact type | row count / approximate exposure count | classification |
|---|---|---:|---|
| `outputs/eda_raw/aihub_025/aihub_025_samples.csv` | CSV | 27,115 raw preview rows; 5 email-like and 9 phone-like pattern rows | `CRITICAL_RAW_KO_EN_TEXT_EXPORT / PII_LIKE_PATTERN_PRESENT` |
| `outputs/eda_raw/aihub_026/aihub_026_samples.csv` | CSV | 13,632 raw preview rows; 12 phone-like pattern rows | `CRITICAL_RAW_KO_EN_TEXT_EXPORT / PII_LIKE_PATTERN_PRESENT` |
| `outputs/eda_raw/legacy_ko_en_xlsx/legacy_ko_en_xlsx_samples.csv` | CSV | 15,966 raw preview rows; 1 URL-like, 1 email-like, and 21 phone-like pattern rows | `CRITICAL_RAW_KO_EN_TEXT_EXPORT / URL_AND_PII_LIKE_PATTERN_PRESENT` |
| `notebooks/exploratory/raw/EDA_RAW_AIHUB_025_daily_conversation_parallel.ipynb` | executed notebook | approximately 12 displayed raw preview rows per committed version; 2 risky blob versions | `HIGH_RAW_SENTENCE_NOTEBOOK_OUTPUT` |
| `notebooks/exploratory/raw/EDA_RAW_AIHUB_026_tech_science_parallel.ipynb` | executed notebook | approximately 12 displayed raw preview rows per committed version; 2 risky blob versions | `HIGH_RAW_SENTENCE_NOTEBOOK_OUTPUT` |
| `notebooks/exploratory/raw/EDA_RAW_LOCAL_KO_EN_PARALLEL_XLSX_V1_legacy_ko_en_parallel_xlsx.ipynb` | executed notebook | approximately 12 displayed raw preview rows per committed version; 2 risky blob versions | `HIGH_RAW_SENTENCE_NOTEBOOK_OUTPUT` |
| `outputs/eda_raw/support/raw_eda_framework.py` | Python producer code | deterministic sample path can emit `ko_preview` / `en_preview` rows | `UNSAFE_RAW_PREVIEW_PRODUCER / DO_NOT_PORT` |
| `outputs/eda_raw/support/create_raw_eda_notebooks.py` | Python notebook generator | generated notebooks display raw preview columns | `UNSAFE_RAW_PREVIEW_PRODUCER / DO_NOT_PORT` |
| `outputs/eda_raw/aihub_025/aihub_025_duplicates.csv` | CSV | 1 aggregate row; count only, no hash value | `SAFE_AGGREGATE_DUPLICATE_COUNT / RECOMPUTE_ONLY` |
| `outputs/eda_raw/aihub_026/aihub_026_duplicates.csv` | CSV | 1 aggregate row; count only, no hash value | `SAFE_AGGREGATE_DUPLICATE_COUNT / RECOMPUTE_ONLY` |
| `outputs/eda_raw/legacy_ko_en_xlsx/legacy_ko_en_xlsx_duplicates.csv` | CSV | 1 aggregate row; count only, no hash value | `SAFE_AGGREGATE_DUPLICATE_COUNT / RECOMPUTE_ONLY` |
| `outputs/eda_raw/**/{inventory,record_counts,schema,length_summary,noise,categories}.csv` | aggregate CSV family | aggregate rows only | `SAFE_MATERIAL_CLASS / RECOMPUTE_FROM_LOCAL_RAW` |
| `outputs/eda_raw/targeted_decision_audit/**` | aggregate CSV family | 15 aggregate tables | `SAFE_TARGETED_RESULT_CLASS / RECOMPUTE_FROM_LOCAL_RAW` |
| `outputs/figures/eda_raw/**` | PNG figure family | aggregate or numeric-length visuals; no raw sentence labels detected | `SAFE_AGGREGATE_FIGURE_CLASS / REBUILD` |
| `outputs/reports/eda_raw/**` | Markdown report family | aggregate findings only | `SAFE_REPORT_CLASS / REWRITE_FROM_RECOMPUTED_EVIDENCE` |
| `outputs/eda_raw/support/append_targeted_decision_audit.py` | Python aggregate producer code | no persisted raw text or text-hash values detected | `SAFE_LOGIC_CLASS / INDEPENDENT_REIMPLEMENTATION_REQUIRED` |
| `eda/g0-raw-notebooks@4e56fdbc70c0571e9eeb912c61816885ad5477a7` | Git branch history | 3 raw-text CSV blobs and 6 risky notebook blob versions remain reachable | `PUBLIC_HISTORY_REMEDIATION_REQUIRED / AWAIT_OPS_DR_01` |
