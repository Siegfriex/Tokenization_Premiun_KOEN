# AIHUB LOCAL RECON COMPLETE

## Scope
- Allowed roots inspected: 3
- Other raw datasets inspected: 0
- Raw files modified: 0
- Raw text exported: 0

## Existing Notebook Handoff
- Existing notebook count: 4
- AI Hub relevant notebook paths: notebooks/exploratory/raw/EDA_RAW_AIHUB_025_G1_SANITIZED.ipynb | notebooks/exploratory/raw/EDA_RAW_AIHUB_026_G1_SANITIZED.ipynb | notebooks/exploratory/raw/EDA_RAW_LEGACY_KO_EN_XLSX_G1_SANITIZED.ipynb
- New notebook path: notebooks/exploratory/evidence/AIHUB_LOCAL_RECON_EVIDENCE_EXPORT_20260816.ipynb
- Reused notebook logic: streaming aggregate patterns only; all results re-run from raw
- Existing notebook files to provide Perplexity: notebooks/exploratory/raw/EDA_RAW_AIHUB_025_G1_SANITIZED.ipynb | notebooks/exploratory/raw/EDA_RAW_AIHUB_026_G1_SANITIZED.ipynb | notebooks/exploratory/raw/EDA_RAW_LEGACY_KO_EN_XLSX_G1_SANITIZED.ipynb

## Candidate Dataset Summary
### LOCAL_DIR_025
- official ID/title/version: NOT VERIFIED
- parseable file count: 9
- apparent record grain: segment/row; AMBIGUOUS field-name inference
- strongest candidate KO/EN field pair: ko + en
- candidate pair-ID status: mean availability 1.000000
- candidate direction status: DIRECTLY_OBSERVED
- pairability verdict: PASS_CANDIDATE
- major metadata fields observed: file_name|source | domain|subdomain | style | license
- major preprocessing indicators: aggregate rates in aihub_quality_flags.csv
- major soft-flag rates: {"duplicate_candidate_pair": 0.06610177, "high_punctuation_ratio_KO": 0.03277925, "many_to_one_indicator": 0.01291537}
- top unresolved questions for Perplexity: official identity, split/grain, translation workflow, license
### LOCAL_DIR_026
- official ID/title/version: NOT VERIFIED
- parseable file count: 4
- apparent record grain: segment/row; AMBIGUOUS field-name inference
- strongest candidate KO/EN field pair: ko + en
- candidate pair-ID status: mean availability 1.000000
- candidate direction status: DIRECTLY_OBSERVED
- pairability verdict: PASS_CANDIDATE
- major metadata fields observed: file_name|source | domain|subdomain | style | license
- major preprocessing indicators: aggregate rates in aihub_quality_flags.csv
- major soft-flag rates: {"high_digit_ratio_KO": 0.00281175, "high_punctuation_ratio_KO": 0.0002733, "language_mismatch": 0.00066575}
- top unresolved questions for Perplexity: official identity, split/grain, translation workflow, license
### LOCAL_LEGACY_KO_EN_XLSX
- official ID/title/version: NOT VERIFIED
- parseable file count: 10
- apparent record grain: segment/row; AMBIGUOUS field-name inference
- strongest candidate KO/EN field pair: 원문 + 번역문
- candidate pair-ID status: mean availability 0.900000
- candidate direction status: INDIRECTLY_SUGGESTED
- pairability verdict: CONDITIONAL
- major metadata fields observed: NOT OBSERVED | 언론사 | NOT OBSERVED | 대분류|소분류 | 자동분류1|자동분류2|자동분류3 | 지자체 | 키워드 | NOT OBSERVED | 상황 | NOT OBSERVED
- major preprocessing indicators: aggregate rates in aihub_quality_flags.csv
- major soft-flag rates: {"high_digit_ratio_KO": 0.00361926, "language_mismatch": 0.00030633, "unobserved_direction": 1.0}
- top unresolved questions for Perplexity: official identity, split/grain, translation workflow, license

## Reconciliation Package
- Markdown report: outputs/aihub_recon_g1/aihub_local_recon_summary.md
- CSV inventory: outputs/aihub_recon_g1/aihub_dataset_inventory.csv | outputs/aihub_recon_g1/aihub_file_manifest.csv
- CSV schema: outputs/aihub_recon_g1/aihub_schema_inventory.csv
- CSV pairability: outputs/aihub_recon_g1/aihub_pairability_audit.csv
- JSON reconciliation packet: outputs/aihub_recon_g1/aihub_reconciliation_packet.json
- Figures directory: outputs/aihub_recon_g1/figures/

## Interpretation Boundary
- LOCAL_OBSERVED evidence is not official documentation.
- No final source rank or Tier A/B/C decision was made.
- Perplexity must reconcile local evidence against official AI Hub documentation.
