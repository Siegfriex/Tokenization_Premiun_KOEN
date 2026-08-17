# PAIR_DUPLICATE_RECON_v001 — SHA-256 Collision-Resistant Duplicate/Identity Recon

이 문서는 `PAIR_DUPLICATE_RECON_v001_20260816T143558+0900.{json,csv}`의 요약이다. **G1 PASS, QC acceptance, 또는 row/pair exclusion 결정이 아니다.** Reconnaissance evidence이며, 최종 canonical dedup 구현 계약은 Codex 소관이다.

## A. SHA-256 exact identity definition

- Pair identity: `SHA256( u64be(len(ko_utf8)) || ko_utf8 || u64be(len(en_utf8)) || en_utf8 )`
- `sn` identity: `SHA256( u64be(len(sn_utf8)) || sn_utf8 )`
- 기존 raw-profile baseline(`profile_aihub_raw.py`/`profile_aihub_duplicate_overlap.py`)이 사용한 BLAKE2b-64(64-bit) 후보 해시와 동일한 length-prefixed byte framing을 그대로 사용하되, digest를 SHA-256(256-bit)로 대체했다. Normalization은 하지 않았다(raw byte 그대로). 이는 여전히 candidate identity이며, normalization/whitespace 정의 문제까지 해결하지는 않는다.
- 원문(ko/en/sn) 텍스트는 이 감사 어디에도 저장하지 않았다 — digest, count, file/direction/split label만 유지한다.

## B. 025 duplicate count 재현 (BLAKE2b-64 → SHA-256)

| Dataset | Metric | Baseline (BLAKE2b-64) | SHA-256 recheck | 일치 |
|---|---|---:|---:|---|
| 025 | duplicate_pair_rows_after_first_occurrence | 214,252 | 214,252 | 일치 |
| 025 | distinct_pair_hashes(=digests)_with_duplicates | 93,823 | 93,823 | 일치 |
| 026 | duplicate_pair_rows_after_first_occurrence | 44 | 44 | 일치 |
| 026 | distinct_pair_hashes(=digests)_with_duplicates | 44 | 44 | 일치 |

이 데이터 규모에서 BLAKE2b-64 후보 집계는 collision으로 인한 오탐(false positive)이 없었음을 SHA-256으로 확인했다.

## C. direction×direction — cross-direction 중복

025 내부에서 `EN_TO_KO`(영한)와 `KO_TO_EN`(한영)로 명목상 다른 방향인 두 파일 집합이 공유하는 distinct pair digest 수: **50,511건**.

방향 판정 규칙: `relative_path`에 `영한` 포함 시 `EN_TO_KO`, `한영` 포함 시 `KO_TO_EN`, 그 외(Legacy XLSX 등 direction 필드 없음) `UNKNOWN`.

## D. split×split — train/validation distinct overlap

프로젝트 전체(025+026, Legacy는 split UNKNOWN이라 제외 범주로 별도 집계) 기준 `TRAIN` ↔ `VALIDATION`이 공유하는 distinct pair digest 수: **25,247건**.

## E. sn identity — dataset-wide collision

| Dataset | Nonempty sn rows | Distinct sn digest | Within-file collision | Cross-sub-file collision |
|---|---:|---:|---:|---:|
| 025 | 2,700,345 | 2,700,345 | 0 | 0 |
| 026 | 1,350,162 | 1,350,162 | 0 | 0 |

각 dataset 내부에서 file 경계(방향×split)를 넘어서도 `sn` collision은 0건이다.

## F. Cross-corpus raw exact-pair overlap (count only)

| Pair | Shared distinct pair digest count |
|---|---:|
| 025 ↔ 026 | 0 |
| 025 ↔ Legacy | 35 |
| 026 ↔ Legacy | 1 |

원문은 export하지 않았다 — count만 기록한다.

## G. 이례적 발견 — Legacy News(2) ↔ Culture

Legacy XLSX 내부 file×file 매트릭스에서, `3_문어체_뉴스(2).xlsx`와 `4_문어체_한국문화.xlsx`가 공유하는 distinct exact pair 수가 **2,469건**으로 다른 파일쌍 대비 두드러지게 높다(다른 Legacy 파일쌍은 대부분 0~7건). 두 워크북의 도메인 라벨(뉴스 vs 문화)이 서로 다른 점을 고려하면 예상 밖의 수치이며, data-recon/Codex 트랙의 추가 확인이 필요한 항목으로 기록한다. 원인(동일 원본 재수록, 워크북 간 콘텐츠 재사용 등)은 이 감사에서 판정하지 않는다.

## H. Explicit non-claims

1. 이 문서는 G1 PASS를 주장하지 않는다.
2. 이 문서는 어떠한 row/pair exclusion 결정도 주장하지 않는다.
3. 이 문서는 canonical duplicate registry를 정의하지 않는다.
4. Canonical dedup 구현 계약은 여전히 Codex 소관이다.
5. SHA-256 identity는 collision 위험을 사실상 제거하지만, normalization/whitespace 등 identity 정의 자체의 모호성은 해소하지 않는다.

## I. Source artifacts

- `outputs/reports/data_recon/profile_pair_duplicate_recon_sha256.py`
- `outputs/manifests/data_recon/PAIR_DUPLICATE_RECON_v001_20260816T143558+0900.json`
- `outputs/manifests/data_recon/PAIR_DUPLICATE_RECON_v001_20260816T143558+0900.csv`
- Baseline 재확인 근거: `outputs/manifests/data_recon/aihub_raw_profile_20260816T132650+0900.json`, `outputs/manifests/data_recon/aihub_duplicate_overlap_20260816T132650+0900.json` (수정하지 않음)
