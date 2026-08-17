# KO-EN Tokenization Premium — Printed SSOT Manual Redline & G1 Parallel-Branch Traffic Control

> Snapshot: 2026-08-16 17:01 KST  
> Authority: KOEN-TP-RS-001 / Korean_English_Tokenization_Premium_Research_Spec_v1.0  
> Purpose: printed-PDF manual redline + current Git reconciliation + next execution order  
> Page notation: `PDF p.X / printed footer p.Y`

## Legend

- **[INK]**: already approved/factual; safe to write permanently on the printed SSOT.
- **[MARGIN]**: evidence/status annotation; do not strike the original design wording.
- **[PENCIL]**: proposed change requiring formal Research Director approval / CHANGE_REQUEST closure.

---

## 1. PDF p.6 / printed p.5 — §0.1 변경 로그

**Before**
`v1.0 | 2026-08-16 | ...`

**After — [INK], append one row; do not strike v1.0**
`Operational Addendum OA-20260816 | 2026-08-16 | CR-001 namespace; CR-002 Track B execution deferral; D-RD-05~08 source/direction/domain/cohort operationalization; G0 release closed; D-01 Pair Registry v001 executed and validated.`

Margin:
`SSOT core RQ/estimand/decomposition unchanged.`

---

## 2. PDF p.12 / printed p.11 — §9.1 권장 표본 규모

**Before**
`권장 본 분석 | 100,000+ | 도메인/길이 strata 및 이질성 분석`

**After — [INK]**
`권장 본 분석 | 100,000+ (권장 최소 규모; fixed cap 아님) | 최종 primary N은 primary-eligible source에서 QC를 통과한 realized N으로 결정`

Margin:
`D-RD-08: fixed_n_cap = null.`

Do not write `N=5,652,925` here; that is the raw D-01 registry size, not the analysis cohort.

---

## 3. PDF p.12 / printed p.11 — §9.2 translation_direction

**Original taxonomy stays unchanged.**

**[MARGIN] current source application**
- `025: KO_TO_EN / EN_TO_KO`
- `026: KO_TO_EN`
- `Legacy: UNKNOWN`
- `Do not infer HUMAN_PARALLEL_UNKNOWN for Legacy.`

---

## 4. PDF p.12 / printed p.11 — §9.3 데이터 source 계층

**Before**
`Tier A — curated/official parallel corpus ...`
`Tier B — benchmark parallel corpus ...`
`Tier C — web-mined parallel corpus ...`

**After — [INK] keep definitions; append current application**
`D-RD-05 current portfolio: 025 = Tier-A candidate / PRIMARY_BACKBONE; 026 = Tier-A candidate / PRIMARY_DOMAIN_SUPPLEMENT; Legacy = UNASSIGNED / SENSITIVITY_ONLY.`

**[INK] add separate axis**
`provenance_closure_status is orthogonal to source_tier.`

Current:
- `025/026: PENDING_OFFICIAL_SCHEMA_AND_RELEASE_LINK`
- `Legacy: PARTIAL_OFFICIAL_CONSTRUCTION_CONFIRMED_FIELD_AND_RELEASE_LINK_PENDING`

Do not change Tier B into a provenance-shortfall fallback.

---

## 5. PDF p.14 / printed p.13 — §12.1 D-01 Pair Registry: source_tier

**Before**
`source_tier | A/B/C`

**After — [INK]**
`source_tier | A/B/C/null(UNASSIGNED); source tier와 provenance closure는 별도 관리`

---

## 6. PDF p.14 / printed p.13 — §12.1 D-01 normalization/QC fields

### `ko_text_nfc, en_text_nfc`

**Before**
`NFC`

**After — [INK]**
`NFC; Phase 1에서는 null + normalization_status=NOT_GENERATED_PHASE1, Phase 2에서 새 registry version에 생성`

### `ko_text_analysis, en_text_analysis`

**Before**
`primary analysis text`

**After — [INK]**
`primary analysis text; Phase 1 null, Phase 2 authoritative`

### `pair_quality_status`

**Before**
`accepted/review/rejected`

**After — [INK]**
`accepted/review/rejected; Phase 1 structurally ingestible row는 review + qc_stage_status=PENDING_PHASE2`

### `pair_quality_score`

**Before**
`optional alignment score`

**After — [INK]**
`optional alignment score; Phase 1=null, semantic/alignment QC 이후 생성`

### `pair_version`

**Before**
`pair registry 버전`

**After — [INK]**
`pair registry 버전; initial canonical Phase-1 registry = v001`

---

## 7. PDF p.14 / printed p.13 — §12.1 D-01 auxiliary lineage fields

**[INK] append below the table**

`Operational D-01 auxiliary fields (approved G1 contract):`

- `source_record_id`
- `raw_locator`
- `duplicate_group_id`
- `representative_pair_id`
- `domain_raw`
- `subdomain_raw`
- `source_provenance_raw`
- `is_validation_upstream`
- `translation_direction_raw`
- `translation_direction_review_flag`
- `mt_field_present`
- `sentence_type_raw`
- `sentence_type_provenance_status`
- `normalization_status`
- `qc_stage_status`
- `direction_conflict_flag`
- `domain_conflict_flag`
- `source_id_conflict_flag`
- `source_provenance_raw_conflict_flag`
- `logical_corpus`
- `canonical_ingest_role`
- `raw_file_relative_path`
- `raw_file_sha256`
- `raw_sheet_name`
- `raw_physical_row_number`
- `source_native_id`
- `source_native_sid`
- `raw_metadata_json`

Core identity note:
`pair_id = provenance identity; duplicate_group_id = raw KO+EN content identity.`

Representative note:
`representative_pair_id is provenance pointer only; it does not supply semantic covariates.`

---

## 8. PDF p.22 / printed p.21 — §20.2 Identifiability Gate

**Original wording remains.**

**[MARGIN] empirical activation**
`Observed in 026: source_provenance_raw=특허정보원 ↔ domain_raw=기술과학, N=359,910, exception=0.`

`Therefore the two axes are not separately identifiable within 026 without redesign/composite/restriction.`

---

## 9. PDF p.23 / printed p.22 — §23 Leakage Rule LR-01

**Original wording remains.**

**[MARGIN] observed evidence**
`Upstream TRAIN↔VALID exact shared pairs = 25,247 distinct pairs.`

`AIHub upstream split is provenance only; project predictive split must be rebuilt under LR-01.`

---

## 10. PDF p.24 / printed p.23 — §26 Track B

Immediately after `26. Track B — gpt-oss Serving Experiment` add:

**[INK]**
`Execution status: DEFERRED_NOT_EXECUTED (CR-002 / D-RD-03). RQ7 remains in scope; Track A is unaffected.`

Do not strike model/protocol definitions.

---

## 11. PDF p.27 / printed p.26 — §30.2 데이터 lineage

**Before**
`• Git commit SHA`

**After — [INK operational clarification]**
`• execution_code_commit`
`• artifact_record_commit`
`  (single SHA 허용 시 동일값; 실행 코드와 산출물 기록 commit이 다르면 둘 다 보존)`

D-01 observed example:
`execution_code_commit=0b401d1...`
`artifact_record_commit=66c8ef0...`

---

## 12. PDF p.28 / printed p.27 — §31 G1 Data Integrity

**Before**
- `pair IDs unique`
- `null/duplicate checks`
- `LID/QC pass rate 보고`
- `source/license metadata 완성`

**[PENCIL — CR-003 pending] proposed clarification below the bullets**
`Phase-1 D-01 engineering completion alone does not constitute G1 PASS. Formal G1 PASS requires the stated LID/QC diagnostic evidence. Phase 2 remains authoritative for normalization and accepted/review/rejected QC disposition.`

Do not strike `LID/QC pass rate 보고` until CR-003 is formally approved.

Current factual status in margin:
- `pair ID uniqueness: PASS`
- `null/duplicate integrity: PASS`
- `source registry: PASS`
- `official provenance closure: OPEN`
- `LID/QC pass-rate: NOT CLOSED`
- `G1: OPEN`

---

## 13. PDF p.29 / printed p.28 — §32 T-03 Translationese

**Original threat wording remains.**

**[MARGIN]**
`025 cross-direction shared exact-pair groups = 50,511.`

This confirms the threat is empirically relevant, but does not explain all duplicates.

---

## 14. PDF p.29 / printed p.28 — §32 T-04 Domain-source confounding

**Original threat wording remains.**

**[MARGIN]**
`026 특허정보원 ↔ 기술과학 biconditional, N=359,910, exception=0.`

---

## 15. PDF p.30 / printed p.29 — §34 Traceability Matrix, RQ1

**Before**
`RQ1 | D-01 + D-04 | median logTP | ...`

**After — [MARGIN progress only]**
`D-01 = L4 COMPLETE`
`D-04 = NOT STARTED`

Do not change the matrix itself.

---

## 16. PDF p.31 / printed p.30 — §36 Repository IA

**Before**
`src/`
`└── koen_tp/`

**After — [INK, CR-001 approved]**
`src/`
`└── tokenization_premium/`

Strike `koen_tp` physically.

No alias/dual package.

---

## 17. PDF p.32 / printed p.31 — §37 Phase 1 Data Contract

**Before**
- `source ingest`
- `stable pair ID`
- `metadata schema`
- `raw hash`

**After — [INK, append; do not delete original bullets]**
- `alias-safe canonical ingest allowlist`
- `source registry`
- `source_record_id + raw_locator`
- `pair_id + duplicate_group_id`
- `raw-file SHA linkage`
- `Phase-1 pending-normalization/QC state`

Current status:
`01_build_pair_registry.ipynb = D-01 engineering L4 COMPLETE.`

---

## 18. PDF p.32 / printed p.31 — §37 Phase 2 Normalization & QC

**Before**
- `NFC/analysis text`
- `anomaly flags`
- `duplicate/LID/parallel quality`
- `QC flow table`

**After — [INK margin clarification]**
`Phase 2 is authoritative for normalized analysis text and accepted/review/rejected QC disposition.`

No Phase-2 execution has formally started yet.

---

## 19. PDF p.34 / printed p.33 — §38 file naming / release manifest

**Before**
`모든 release manifest에는 SHA-256, row count, schema version, code commit을 포함한다.`

**After — [INK operational clarification]**
`모든 release manifest에는 SHA-256, row count, schema version, execution_code_commit을 포함하고, 산출물을 후속 commit에서 기록하는 경우 artifact_record_commit도 별도 보존한다.`

---

## 20. PDF p.34 / printed p.33 — §39 분석 전 체크리스트

Manual marks now:

- `☑ Research questions와 estimand freeze`
- `☑ Primary tokenizer와 implementation freeze`
- `☑ Morphology analyzer/POS mapping freeze`
- `△ Source registry와 license note 완료`
  - source registry: done
  - official provenance/license closure: open
- `☑ Pair QC rubric freeze`
- `□ Unicode normalization tests PASS` — Phase 2
- `△ Tokenizer roundtrip tests PASS` — environment-level PASS; accepted-cohort execution later
- `□ Exact decomposition identity tests PASS` — full cohort later
- `□ Morphology sample audit PASS`
- `□ Source-domain identifiability audit PASS` — warning already found in 026
- `□ Analysis cohort hash freeze`
- `□ Train/hold-out manifest freeze`
- `□ Figure/table IDs freeze`

**[INK append new completed line]**
`☑ D-01 Pair Registry v001 engineering + independent oracle audit (N=5,652,925 raw registry rows)`

---

## 21. PDF p.35 / printed p.34 — Appendix A 결정 로그

Keep existing D-01~D-07 untouched.

Append a separate block titled:

`Operational / Research Director Decisions after Design Freeze`

**[INK]**
- `CR-001 | canonical Python namespace = src/tokenization_premium/ | implementation namespace alignment`
- `CR-002 / D-RD-03 | Track B execution = DEFERRED_NOT_EXECUTED; RQ7 retained | sequence/cost control`
- `D-RD-04 | Raw EDA auxiliary track authorized; non-canonical | pre-ingestion diagnostics`
- `D-RD-05 | 025=A candidate backbone; 026=A candidate supplement; Legacy=UNASSIGNED sensitivity-only | source portfolio`
- `D-RD-06 | 025 directions from raw provenance; 026=KO_TO_EN; Legacy=UNKNOWN | avoid unsupported direction/human-parallel inference`
- `D-RD-07 | actual raw top-level domain labels mapped to SSOT taxonomy; raw labels preserved | operational domain contract`
- `D-RD-08 | primary cohort fixed cap=null; final N is QC-realized | avoid arbitrary pre-analysis sampling`

Optional operational note:
`INC-001 | memory pressure / Cursor remote connection incident; no D-01 data loss; D-01 byte integrity PASS.`

---

## 22. PDF p.36 / printed p.35 — Appendix B raw-data release wording

**Before**
`이 중 raw data는 license와 배포 조건에 따라 release bundle에서 제외할 수 있으며, 대신 source hash와 acquisition metadata를 남긴다.`

**[PENCIL — CR-004 candidate; recommended] After**
`공식 재배포 권한이 명시적으로 확인되지 않은 raw data 및 recoverable raw-text export는 release bundle과 public Git history에서 제외한다. 대신 source hash, acquisition metadata, aggregate QC/reconciliation evidence를 남긴다.`

Reason:
The old public EDA branch exposed raw-text previews; sanitized G1 support corrected the forward path, but historical remediation is still pending.

---

# Current Git traffic snapshot

Direct remote state at 17:01 KST:

- `main = f1b2a901...`
- `integration/g1 = de9124f...`
  - already contains `research/g1-claude@f7dd12d`
  - already contains `data/g1-recon@617f6fd`
  - already contains `evidence/g1-perplexity@cc535b3`
- `data/g1-recon = ebae51c...`
  - one new audit commit after the integration snapshot
- `impl/g1-codex = 66c8ef0...`
  - D-01 engineering/artifact commit; not integrated
- `eda/g1-support = 2e11112...`
  - remote unchanged; local portability work is still in progress
- `research/g1-claude = f7dd12d...`
  - no persisted CR-003 proposal yet

## Report mismatch fixed

The authoritative D-01 schema contains **44 columns**.
A parallel Claude report stated **41 columns**; treat that count as stale/miscounted.

---

# Immediate integration order

## Merge now

1. `impl/g1-codex@66c8ef0`
2. `data/g1-recon@ebae51c`

Reason:
- D-01 implementation is complete and post-incident integrity passed.
- The independent audit commit logically follows the implementation.
- The audit branch contributes only two safe aggregate evidence files.
- EDA is auxiliary and need not block canonical Phase-1 integration.

## Hold

- `eda/g1-support` until portability fix is committed/pushed and revalidated.
- no `main` merge.
- no Phase 2 start.
- no G1 PASS.

---

# Untracked-local-file protection

Canonical root currently has local-only governance/evidence files.

Protect immediately:

- keep the three SSOT decision logs
- do not stage the old `notebooks/01_aihub_local_recon_evidence_export.ipynb`
- after sanitized EDA evidence is complete, move the old local notebook outside the repository or delete only after SHA/archive confirmation
- persist governance logs via a dedicated `ops/g1-governance` branch from current `integration/g1`, not through `integration/g0`

---

# Next branches after integration

1. `research/g1-gate-claude` from the updated `integration/g1`
   - real D-01 semantic conformance audit
   - CR-003 proposal
   - no config mutation before Director approval

2. `impl/g1-runtime-safety-codex` from updated `integration/g1`
   - externalize DuckDB memory limit
   - default 8GB, environment override
   - spill required
   - no research semantics change
   - needed before final canonical heavy rerun

3. EDA finishes independently, then merge only after remote SHA + portability/sanitization validation.

4. Canonical integration Run All occurs only after runtime-safety fix and G1 gate-sequencing decision.

