# NB06 / D-05 재현 절차

재현 가능성은 **하나의 상태가 아니라 세 단계**입니다. 각 단계마다 필요한 것이 다르고,
Git checkout만으로 도달할 수 있는 지점은 LEVEL A까지입니다.

> **과장하지 않기 위한 명시** — 이 결과는 **"Git checkout만으로 완전히 재현되지 않습니다."**
> canonical parquet artifact는 `.gitignore`(`data/registry/**`)로 저장소에서 제외되어
> 있습니다. `PAIR_REGISTRY_v002.parquet`(2.8 GB)와 `TOKEN_O200K_BASE_v001.parquet`(776 MB)는
> 로컬 환경에만 존재합니다.

| 수준 | 필요한 것 | 검증하는 것 | 소요 |
|---|---|---|---|
| **A** 문서/figure 재현 | Git checkout + Python 환경 | figure 파일 hash 동일 | 수 초 |
| **B** D-05 검증 재현 | A + 로컬 `CHUNK_O200K_BASE_v001.parquet` + D-04 | 17/17 검증 PASS | 수 분 |
| **C** 전집단 재실행 | B + pair registry + tiktoken 오프라인 캐시 | artifact SHA256 동일 | 약 6분 + 검증 |

---

## 공통 환경

| | |
|---|---|
| Python | 3.12.3 |
| tiktoken | 0.13.0 |
| duckdb | 1.5.5 |
| pyarrow | 24.0.0 |
| regex | 2026.7.19 |
| matplotlib | 3.11.1 |

한국어 label 렌더링에는 `NanumGothic`(또는 `Noto Sans CJK KR`)이 필요합니다.
없으면 figure builder는 기본 라틴 폰트로 떨어지며, 이 경우 한국어 label이 깨져
**figure hash가 달라집니다.** `build_nb06_figures.py`가 사용한 폰트 family를 출력하므로
비교 시 확인하세요.

모든 명령은 저장소 루트에서 실행하며 `PYTHONPATH`에 `src`를 넣습니다.

```bash
export PYTHONPATH="$PWD/src"
```

---

## LEVEL A — 문서 / figure 재현

**필요한 것**: Git checkout만.

입력은 커밋된 집계 JSON 하나뿐입니다. canonical parquet을 읽지 않습니다.

```bash
python docs/results/nb06_d05/build_nb06_figures.py
```

기대 결과 — `docs/results/nb06_d05/figures/`의 SVG/PNG 8개가 커밋된 파일과
**byte 단위로 동일**해야 합니다.

```bash
git status --short docs/results/nb06_d05/figures/    # 출력이 비어 있으면 PASS
```

또는 패키지 검증기가 hash를 직접 대조합니다:

```bash
python docs/results/nb06_d05/verify_nb06_d05.py
```

이 스크립트는 실행할 때마다 `NB06_D05_REPRO_MANIFEST_v001.json`을 갱신합니다 —
패키지 각 파일의 sha256과 재현 수준별 상태(`LEVEL_A` / `LEVEL_B` / `LEVEL_C`)가 들어갑니다.
커밋된 manifest와 diff가 없으면 패키지가 커밋 시점과 동일하다는 뜻입니다.

> figure 재현성을 위해 `svg.hashsalt`를 고정하고 SVG/PNG metadata에서 실행 시각을
> 제거했습니다. 이 두 가지가 없으면 같은 데이터로도 파일 hash가 매번 달라집니다.

---

## LEVEL B — D-05 검증 재현

**추가로 필요한 것**:

| 파일 | 크기 | 비고 |
|---|---|---|
| `data/registry/CHUNK_O200K_BASE_v001.parquet` | 491 MB | 검증 대상 |
| `data/registry/TOKEN_O200K_BASE_v001.parquet` | 776 MB | anti-join 상대 |

### B-1. artifact 신원 확인

```bash
sha256sum data/registry/CHUNK_O200K_BASE_v001.parquet
# 기대: bfa98bd6cf7ee8b7254c469aed3e259ce43cc8f0529153347ca4c2c3fc1944ab

sha256sum data/registry/TOKEN_O200K_BASE_v001.parquet
# 기대: 1c30e3276222dd94885ae4f79fc6ab5c45e4e26226de0afd91fc6b1f7d2c16e7
```

해시가 다르면 **여기서 멈춥니다.** 다른 파일을 검증하는 것은 의미가 없습니다.

### B-2. canonical validator 실행

문서용으로 검증 로직을 다시 구현하지 않습니다. 측정 시 사용한 것과 **같은** 스크립트를
재사용합니다.

```bash
python scripts/validate_d05.py
```

PASS 조건:

- 17/17 checks PASS
- `row_count = 3,835,988`
- `pair_set_md5 = d9660d654ee449e4d0c23a0070225274`
- `chunking_config_sha256 = b8f26abf3e64a1d7d91284e7ccdda0a27a1d615052d86c304c9f7196e7f7dbf5`
- `artifact_sha256` = 위 기대값

출력은 `outputs/manifests/CHUNK_O200K_BASE_VALIDATION_v001.json`에 기록됩니다.

### B-3. (선택) 집계값 재산출

figure 입력 JSON을 physical artifact에서 다시 만들어 커밋본과 대조할 수 있습니다.

```bash
python docs/results/nb06_d05/extract_visual_data.py
git diff --stat docs/results/nb06_d05/data/   # 차이가 없어야 한다
```

---

## LEVEL C — 전집단 재실행

**추가로 필요한 것**:

| 항목 | 비고 |
|---|---|
| `data/registry/PAIR_REGISTRY_v002.parquet` (2.8 GB) | `ko_text_analysis` / `en_text_analysis` 원문 |
| `data/registry/TOKEN_O200K_BASE_v001.parquet` (776 MB) | 저장된 token ID 배열 |
| tiktoken 오프라인 캐시 | `o200k_base` encoding 파일. 네트워크 접근은 하지 않음 |
| 여유 RAM | MemAvailable ≥ 5 GiB (guard RED 임계). 실측 최소 6.19 GiB |
| 디스크 | 결과 491 MB + DuckDB spill 여유 |

> **재실행은 Git만으로 불가능합니다.** 위 두 parquet은 저장소에 없습니다.
> 두 파일은 Phase 2–3 파이프라인(`scripts/run_full_measurement.py` 등)의 산출물이며,
> 그 단계까지 거슬러 재생성하려면 원본 코퍼스가 필요합니다. 이 문서의 범위를 넘습니다.

### C-1. tiktoken 캐시 준비

```bash
export TIKTOKEN_CACHE_DIR="$PWD/.runtime/tiktoken-cache"
ls "$TIKTOKEN_CACHE_DIR"    # o200k_base encoding 파일이 있어야 한다
```

없으면 `load_o200k_base_offline()`이 실패합니다 — 실행 중 네트워크로 내려받지 않는
것이 의도된 동작입니다.

### C-2. pilot (전집단 게이트)

```bash
python scripts/run_d05_pilot.py
```

`full_run_authorized = true`가 나와야 합니다.
`TOTAL MISMATCH > 0`이면 전집단 실행이 금지됩니다.

### C-3. 전집단 실행

```bash
# 기존 산출물이 있으면 FileExistsError로 멈춘다. 의도적으로 자동 재시작하지 않는다.
rm -f data/registry/CHUNK_O200K_BASE_v001.parquet

python scripts/run_d05_full.py
```

실행 파라미터는 코드에 고정되어 있습니다 — `batch_rows=2500`,
DuckDB `memory_limit=3GB`, `threads=8`.

기대 결과:

```
rows   = 3,835,988
sha256 = bfa98bd6cf7ee8b7254c469aed3e259ce43cc8f0529153347ca4c2c3fc1944ab
```

**SHA256이 다르면 재현 실패입니다.** 세 번의 독립 실행이 동일 값을 냈으므로,
불일치는 입력 artifact 또는 tokenizer 설정이 다르다는 신호입니다.

### C-4. 검증

```bash
python scripts/validate_d05.py     # 17/17 PASS
```

### C-5. 노트북 재실행 (선택)

```bash
jupyter nbconvert --to notebook --execute --inplace \
  --ExecutePreprocessor.kernel_name=tokenization_premium \
  notebooks/06_regex_chunk_audit.ipynb
```

노트북은 pilot과 다른 salt로 3,000 pair를 새로 뽑아 여섯 불변식을 다시 계산합니다.
표본은 결정적이므로 같은 artifact에서는 같은 표본이 나옵니다.

---

## 한 번에 실행

LEVEL A와 (파일이 있으면) LEVEL B를 순서대로 수행합니다.

```bash
bash docs/results/nb06_d05/reproduce.sh
```

LEVEL C는 **포함하지 않습니다.** 전집단 재실행은 기존 canonical artifact를 지워야 하므로
자동화 스크립트에 넣지 않고, 위 C-3 절차를 직접 수행하도록 남겨 두었습니다.

---

## 재현 실패 시 확인 순서

| 증상 | 확인 |
|---|---|
| figure hash 불일치 | 폰트 family가 `NanumGothic`인지, matplotlib 버전이 3.11.1인지 |
| `ChunkConfigMismatch` | tiktoken 버전과 캐시 파일. `pat_str` 해시가 D-04 동결값과 다름 |
| `CanonicalArtifactIdentityMismatch` | 상류 parquet의 sha256이 pinned 값과 다름 |
| `MemoryGuardAbort` (시작 시점) | MemAvailable < 5 GiB. 다른 프로세스를 정리하고 재시도 |
| `FileExistsError` | 기존 artifact 또는 `.partial`이 남아 있음. 자동 삭제하지 않는다 |
| 검증 FAIL `pair_set_md5` | 해시 정의를 직접 다시 쓰지 말 것. `lineage.pair_set_md5()` 사용 |
