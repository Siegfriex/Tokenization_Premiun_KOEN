# G1_INGEST_EXPECTATIONS_v001 — Canonical Ingest Expectations for Codex

이 문서는 `G1_INGEST_EXPECTATIONS_v001.{json,csv}`의 요약이다. **G1 PASS 주장이 아니다.** Reconnaissance 증거로부터 도출한 canonical ingest 기대치 계약이며, 실제 ingest 구현은 Codex 소관이다. normalization, QC exclusion, source-tier 확정, tokenization, morphology 어느 것도 수행하지 않았다.

## 0. Provenance

- `raw_root`: `/home/sieg/projects-wsl/Tokenization_Premium/data/raw/aigub`
- `raw_manifest_sha`: `9a546bc91225e5331d0e8e48a1e06685cb5304ed7098aff5cbf40c74022c1f0c`
- 근거: `aihub_raw_profile_20260816T132650+0900.json`, `aihub_duplicate_overlap_20260816T132650+0900.json`, `PAIR_DUPLICATE_RECON_v001_20260816T143558+0900.json` (모두 이 브랜치에 이미 커밋됨, cherry-pick 출처는 `data/g0-aihub-recon`)
- 생성 스크립트: `build_g1_ingest_expectations.py` — 아래 모든 수치는 위 세 매니페스트에서 프로그램적으로 추출했으며 수기로 옮겨 적지 않았다.

## 1. Physical file allowlist (23 physical → 16 canonical)

| logical_corpus | physical files | canonical (unique-content) files | alias 종류 |
|---|---:|---:|---|
| 025 | 9 | 4 | 4× BYTE_IDENTICAL_ALIAS (TS1/TS2/VS-영한/VS-한영) + 1× ARCHIVE_CONTAINER_ALIAS (VS1.zip, 2 member 모두 VL1 json과 byte-identical) |
| 026 | 4 | 2 | 2× BYTE_IDENTICAL_ALIAS (TS1, VS1) |
| Legacy | 10 | 10 | 없음 (전부 canonical) |
| **Total** | **23** | **16** | |

전체 목록·SHA-256·역할은 `G1_INGEST_EXPECTATIONS_v001.csv` 및 json의 `physical_file_allowlist`에 있다.

## 2. Expected logical record counts (canonical 파일만 합산)

| Corpus | Expected count |
|---|---:|
| 025 | 2,700,345 |
| 026 | 1,350,162 |
| Legacy | 1,602,418 |
| **Total** | **5,652,925** |

## 3. Double-ingest 방지 계약

Codex ingester는 `data/raw/aigub`를 재귀 rglob 하지 않고, `double_ingest_prevention_contract.ingest_allowlist`(16개 canonical relative_path)만 읽어야 한다. `alias_status != CANONICAL`인 항목(byte-identical 라벨/원천 사본, VS1.zip)은 전부 skip 대상이다. 이를 어기고 순수 재귀 ingest를 하면 025는 5,400,690건, 026은 2,700,324건으로 정확히 2배 부풀려지고, 025 validation은 VS1.zip 재추출로 추가 중복된다.

## 4. Source record ID 기대치

- **025 / 026**: `sn` 필드. 각 dataset 전체(양방향 × train/valid 4개 또는 2개 sub-file)에서 within-file, cross-sub-file 모두 **collision 0건** 검증됨(`PAIR_DUPLICATE_RECON_v001` section 3).
- **Legacy**: bare `ID`/`SID` 전역 key 금지. `workbook/file namespace + sheet + 결정론적 physical row locator(헤더 이후 1-base 행 번호)`를 사용하고, 원본 `ID`/`SID`는 raw auxiliary metadata로 보존한다. 근거: workbook 네임스페이스 없이 풀면 127,824건 중복 후보, 대화체는 단일 unique ID 자체가 없음(Set Nr.+발화자도 8건 중복).

## 5. Expected pairability

- 025/026: `ko`/`en`이 같은 JSON object에 공존 (DIRECT).
- Legacy: `원문`/`번역문`이 같은 행에 공존 (DIRECT), 단 전역 안전 bare ID는 없음.

## 6. Duplicate baseline oracle (Codex 검증용 독립 기대값)

| Metric | Expected value |
|---|---:|
| 025 duplicate-after-first | 214,252 |
| 025 distinct duplicate groups | 93,823 |
| 026 duplicate-after-first / distinct groups | 44 / 44 |
| Cross-direction (025 EN_TO_KO↔KO_TO_EN) distinct shared | 50,511 |
| TRAIN↔VALIDATION distinct shared (project-wide) | 25,247 |
| Cross-corpus 025↔026 / 025↔Legacy / 026↔Legacy | 0 / 35 / 1 |
| Legacy News(2)↔Culture distinct shared | 2,469 |
| sn collision (025, 026; within-file / cross-subfile) | 0 / 0 |

Identity method: `SHA256(u64be(len(ko_utf8))‖ko_utf8‖u64be(len(en_utf8))‖en_utf8)`. 이 값들은 Codex의 canonical registry/dedup 구현이 스스로 재도출해야 할 목표가 아니라, 구현 결과를 대조 검증하기 위한 **독립적** 기대값이다.

## 7. Non-claims

1. Normalization을 수행하지 않았다.
2. QC exclusion 결정을 내리지 않았다.
3. Source-tier(§9.3 Tier A/B/C) 확정을 내리지 않았다.
4. Tokenization을 수행하지 않았다.
5. Morphology 분석을 수행하지 않았다.
6. G1 PASS를 주장하지 않는다. G1 PASS 조건(pair ID 유일성, null/duplicate 점검, LID/QC pass rate, source/license metadata 완성)은 실제 canonical ingest + QC 구현 이후 별도로 평가되어야 한다.

## 8. Source artifacts

- `outputs/reports/data_recon/build_g1_ingest_expectations.py`
- `outputs/manifests/data_recon/G1_INGEST_EXPECTATIONS_v001.json`
- `outputs/manifests/data_recon/G1_INGEST_EXPECTATIONS_v001.csv`
