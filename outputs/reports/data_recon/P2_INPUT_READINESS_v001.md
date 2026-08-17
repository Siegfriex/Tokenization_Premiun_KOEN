# P2 Input Readiness v001

`02_normalize_and_qc` 설계용 기존 증거 handoff다. 새 분석·원천 재스캔·새 LID 실행·QC 합격 판정은 수행하지 않았다. 원문 문장, sample/preview 행, 원시 URL·이메일·전화번호 값, text/pair hash 값은 포함하지 않는다.

## 증거 등급

| 등급 | 의미 |
|---|---|
| `D01_VALIDATED` | D-01 canonical manifest 수치가 independent post-execution audit에서 재현되거나 명시적으로 일치함 |
| `RECON_VALIDATED` | 기존 data recon의 SHA-256/ingest-oracle 결과이며 D-01 독립 검증으로 자동 승격하지 않음 |
| `EDA_OBSERVED` | sanitized full-population 집계 관찰이며 QC acceptance가 아님 |
| `PRELIMINARY_HEURISTIC` | 기존 임계치·문자 스크립트 기반 후보 신호이며 Phase 2 재계산/판정이 필요함 |

JSON에서 상위 metric 객체의 `evidence_level`은 자식이 더 좁은 등급을 명시하지 않는 한 그 객체의 모든 값과 배열 항목에 적용된다.

## A. 사용한 원천 증거

- `outputs/manifests/PAIR_REGISTRY_MANIFEST_v001.json` — D-01 manifest (`D01_VALIDATED`)
- `outputs/manifests/data_recon/D01_INDEPENDENT_POST_EXECUTION_AUDIT_v001_20260816T164500+0900.json` — D-01 독립 감사 (`D01_VALIDATED`)
- `outputs/manifests/data_recon/G1_INGEST_EXPECTATIONS_v001.json` — canonical ingest 방향·분할·allowlist (`RECON_VALIDATED`)
- `outputs/manifests/data_recon/PAIR_DUPLICATE_RECON_v001_20260816T143558+0900.json` — SHA-256 raw exact-pair 중복/겹침 (`RECON_VALIDATED`)
- `outputs/aihub_recon_g1/{aihub_quality_flags.csv,aihub_pairability_audit.csv}` — 기존 후보율 (`EDA_OBSERVED` 또는 `PRELIMINARY_HEURISTIC`)
- `outputs/eda_raw/g1_support/**` — sanitized aggregate domain/source/Unicode/중복 구조 (`EDA_OBSERVED`)

각 입력 SHA-256은 machine-readable packet의 `source_evidence`에 기록했다.

## B. 코퍼스 요약

| corpus | 행 수 | 번역 방향/분할 | raw domain 또는 안전한 proxy | raw source |
|---|---:|---|---|---|
| 025 | 2,700,345 `D01_VALIDATED` | EN→KO train 1,200,307; valid 150,038 / KO→EN train 1,200,000; valid 150,000 `RECON_VALIDATED` | 해외영업 1,260,367; 일상생활 899,757; 해외고객과의채팅 540,221 `EDA_OBSERVED` | 크라우드 소싱 1,350,345; 크라우드소싱 900,195; SBS 449,805 `EDA_OBSERVED` |
| 026 | 1,350,162 `D01_VALIDATED` | KO→EN train 1,200,144; valid 150,018 `RECON_VALIDATED` | 세계 449,941; 기술과학 359,910; 경제 270,144; 정치 180,239; 기후 89,928 `EDA_OBSERVED` | 한국연구재단 990,252; 특허정보원 359,910 `EDA_OBSERVED` |
| Legacy | 1,602,418 `D01_VALIDATED` | direction/split 모두 `UNKNOWN` 1,602,418 `RECON_VALIDATED` | 통일 raw domain 필드 없음. 파일군 proxy: 구어체 400,000; 대화체 100,000; 문어체뉴스 801,387; 한국문화 100,646; 조례 100,298; 지자체웹 100,087 `EDA_OBSERVED` | `언론사` 필드 801,387행(50.0111%)만 부분 관찰. 전체 11개 값은 JSON에 수록 `EDA_OBSERVED` |

Legacy 파일군은 정확한 집계지만 canonical domain으로 확정하지 않는다. 025의 두 crowd-source 표기는 raw category 그대로 분리한다.

## C. 기존 QC 관련 신호

모든 비율은 `count / corpus row count`다.

| corpus | missing/empty KO·EN | zero-width KO / EN | control KO / EN | language mismatch 후보 | high digit KO / EN | high punctuation KO / EN |
|---|---|---|---|---|---|---|
| 025 | 모두 0 `EDA_OBSERVED` | 5 / 86 `EDA_OBSERVED` | 0 / 0 `EDA_OBSERVED` | 8,184 (0.303072%) `PRELIMINARY_HEURISTIC` | 14,922 (0.552596%) / 4,295 (0.159054%) `PRELIMINARY_HEURISTIC` | 89,910 (3.329575%) / 26,674 (0.987800%) `PRELIMINARY_HEURISTIC` |
| 026 | 모두 0 `EDA_OBSERVED` | 5 / 7,528 `EDA_OBSERVED` | 0 / 0 `EDA_OBSERVED` | 884 (0.065474%) `PRELIMINARY_HEURISTIC` | 3,634 (0.269153%) / 38 (0.002814%) `PRELIMINARY_HEURISTIC` | 369 (0.027330%) / 3 (0.000222%) `PRELIMINARY_HEURISTIC` |
| Legacy | 모두 0 `EDA_OBSERVED` | 21 / 192 `EDA_OBSERVED` | 0 / 1 `EDA_OBSERVED` | 593 (0.037007%) `PRELIMINARY_HEURISTIC` | 5,583 (0.348411%) / 241 (0.015040%) `PRELIMINARY_HEURISTIC` | 417 (0.026023%) / 27 (0.001685%) `PRELIMINARY_HEURISTIC` |

전역 D-01 감사에서는 `raw_pair_structural_missing=0`, `pair_id null=0`, `pair_id distinct=5,652,925/5,652,925`가 `D01_VALIDATED`다. 언어 불일치는 새 LID 결과가 아니라 “KO Hangul 또는 EN Latin dominance < 0.5” 후보 규칙이다.

## D. 알려진 중복 구조

- 025 raw exact pair: after-first 214,252행, 93,823그룹 `D01_VALIDATED`.
  - multiplicity 2~5,508; size-2 그룹 80,834, size>2 그룹 12,989 `EDA_OBSERVED`.
  - EN→KO와 KO→EN 사이 distinct shared pair 50,511 `D01_VALIDATED`; matchable row 50,529 `EDA_OBSERVED`.
  - train-valid cross-split group 25,238, matchable row 36,089 `EDA_OBSERVED`.
- 026 raw exact pair: after-first 44행, 44그룹(따라서 모두 size 2) `D01_VALIDATED`; train-valid distinct shared pair 9 `RECON_VALIDATED`.
- Legacy raw exact pair: after-first 2,494행, 2,494그룹 `EDA_OBSERVED`.
- cross-corpus exact overlap: 025↔026 0, 025↔Legacy 35, 026↔Legacy 1 `D01_VALIDATED`.
- project-wide train↔validation distinct shared pair digest 25,247 `RECON_VALIDATED`. raw length-prefixed UTF-8 SHA-256 identity이며 normalization 이전 수치다.

## E. 알려진 이상

- Legacy News(2)↔Culture: exact pair 2,469그룹, 양쪽 각 1행인 one-to-one 구조. 그룹 수는 `D01_VALIDATED`, News(2) 1.231170%·Culture 2.453153% 비율과 multiplicity는 `EDA_OBSERVED`다.
- 분류는 `POTENTIAL_CORPUS_COMPOSITION_OVERLAP`; 오류·누출·제외로 확정하지 않는다.
- 026 EN zero-width 7,528건은 기존 관찰상 가장 두드러진 Unicode 입력 신호지만 자동 제거 근거가 아니다.
- 025 crowd-source 표기 두 종류는 provenance가 확인되기 전 병합하지 않는다.

## F. Phase 2에서 아직 계산할 필드

- `ko_text_nfc`, `en_text_nfc`, `ko_text_analysis`, `en_text_analysis`: 현재 전부 null이며 `normalization_status=NOT_GENERATED_PHASE1` `D01_VALIDATED`.
- LID model/version/score와 mismatch reason: 이번 packet에서 새 LID를 실행하지 않았고 기존 값은 `PRELIMINARY_HEURISTIC`.
- Unicode normalization action과 before/after zero-width/control flag.
- `qc_rule_version`, reason codes, `pair_quality_score`, 최종 `pair_quality_status`, `qc_stage_status`.
- normalization 후 duplicate group/representative/disposition 및 split-overlap disposition.
- Legacy direction/split, canonical domain/source 결정. 파일명·필드 순서만으로 확정하지 않는다.

이 packet은 QC acceptance, G1 PASS, 행 제외, source-tier/license closure, semantic duplicate equivalence를 주장하거나 승인하지 않는다.
