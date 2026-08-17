# NB06 / D-05 Result Card

**o200k_base Regex Chunk Measurement** · Track A · KOEN Tokenization Premium

---

### Population

**3,835,988** KO–EN pairs (canonical final cohort, 전수)

### Tokenizer

`o200k_base` · tiktoken 0.13.0 · Track A (raw text, no chat template, no special tokens)
`pat_str` sha256 `2d1b8dc11e89af71…` — D-04 동결값과 일치

---

### 관찰값

| | **KO** | **EN** |
|---|---|---|
| regex chunk 수 / pair-side (`chunk_count`) | **13.56** | **19.50** |
| chunk당 최종 token 수 (`tokens_per_chunk`) | **2.02** | **1.04** |
| chunk 평균 byte (`mean_chunk_bytes`) | 8.12 | 4.94 |

### 핵심 패턴

> 한국어는 regex chunk가 **더 적지만**, chunk 하나가 **훨씬 더 많은**
> subword token으로 확장된다.
>
> Fewer Korean regex chunks, but substantially greater subword expansion per chunk.

로그 분해 (두 항의 부호가 반대):

```
ln(N_ko/N_en) = ln(C_ko/C_en) + ln(density ratio)
   +0.2852    =    −0.3672    +    +0.6523          잔차 max 4.7e-16
```

---

### 검증

| | |
|---|---|
| 재구성 실패 (reconstruction failures) | **0** |
| token ID 등가성 실패 (token-ID equivalence failures) | **0** |
| warning 행 | **0** |
| 전집단 검증 체크 | **17 / 17 PASS** |
| Pilot (20,000 pairs · 665,765 chunks) | 전 항목 **0** |
| 노트북 독립 재검사 (3,000 pairs · 98,222 chunks, 다른 salt) | **0** |
| D-04 대비 anti-join (양방향) | **0 / 0** |

### Artifact

```
data/registry/CHUNK_O200K_BASE_v001.parquet
SHA256   bfa98bd6cf7ee8b7254c469aed3e259ce43cc8f0529153347ca4c2c3fc1944ab
rows     3,835,988      columns 39
pair-set d9660d654ee449e4d0c23a0070225274
```

독립 전집단 실행 3회 — 모두 동일 SHA256.

### Runtime (R1)

347.21초 · 평균 11,045.8 rows/sec · telemetry 표본 36개(10초 주기) ·
최소 MemAvailable 6.188 GiB · RED 이상 표본 0 · COMPLETED

---

### Interpretation status

```
DESCRIPTIVE MECHANISM MEASUREMENT
NOT CAUSAL
M3 / NB09 PENDING
```

D-05는 최종 token 수와 TP의 authority가 아닙니다 — **D-04**가 authority입니다.
D-05 schema에는 token ID 배열도, `token_premium`도, §8 분해항도 존재하지 않으며
이는 회귀 테스트로 강제됩니다.
