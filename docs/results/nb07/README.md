# NB07 — 정준 기술 통계 분석(Canonical Descriptive EDA) 및 정확 분해

```
NOTEBOOK_ID      = notebooks/07_eda_and_decomposition.ipynb
EXECUTION_BASE   = origin/audit/g5-analysis-readiness-20260818 @ 9d99e13026b89dcf7d8846d0c105a811f64274bc
BRANCH           = research/nb07-canonical-eda-20260818
G5_STATUS        = G5_ANALYSIS_READINESS_PASS_WITH_NOTES
HEADLESS_STATUS  = PASS (jupyter nbconvert --execute, 0 error outputs, 25.5s)
```

이 패키지는 **기술 통계 전용**이다. 모형 적합·계수 산출·RQ 재검정을 하지 않는다. RQ1은
NB08의 frozen 결과를 주석(annotate)만 한다.

## 1. RQ map

| RQ | 이 notebook의 역할 | 조건부/증분/메커니즘 판단 |
|---|---|---|
| RQ1 | NB08 frozen 결과 주석 (bit-identical 재확인) | NB08 (이미 CLOSED) |
| RQ2 | 정확 분해 `logTP=logCR+logBDR+logCP` — **이 notebook이 canonical** | 해당 없음 |
| RQ3 | surface-form 기술 구조만 | NB09 M1 vs M0 |
| RQ4 | 형태론 분포 기술만 | NB09 M2 vs M1 |
| RQ5 | D-05 정규식 청킹 기술만 | NB09 M3 vs M2 |
| RQ6 | source/domain/direction/length 이질성 기술만 | NB09 이후 모형 기반 |

## 2. SSOT map

`KOEN-TP-RS-001` §8(분해) · §12.2-12.5(D02-D05) · §13(형태론) · §16.2(F01-F09, 이번 세션
PDF 원문 재검증 없이 기존 인용 section 번호를 계승) · §20.1/§20.2/§32(식별가능성) · §21(구성
reference coding) · §31(G5) — `RD-FAST-G5-01` · `RD-SSOT-CANONICAL-RETURN-01` §14(NB07 role) ·
`RD-G5-ENTRY-GOVERNANCE-CLOSEOUT-01` · `ssot_g5/02_G5_DIAGNOSTIC_PROTOCOL_v001.md`.

## 3. Artifact identity

| artifact | SHA-256 | 결과 |
|---|---|---|
| D-01 PAIR_REGISTRY_v002 | `95f523d1…10bec52` | MATCH |
| D-02 REP_FEATURES_v002 | `dfae8e01…50d309` | MATCH |
| D-03 MORPH_FEATURES_KIWI_v001 | `0fe5bd74…3e50f7d` | MATCH |
| D-04 TOKEN_O200K_BASE_v001 | `1c30e327…2c16e7` | MATCH |
| D-05 CHUNK_O200K_BASE_v001 | `bfa98bd6…1944ab` | MATCH |

`N = 3,835,988`, pair-set md5 `d9660d654ee449e4d0c23a0070225274`, 모든 join이 N을 보존.

## 4. Figure map

| id | 설명 | 의존성 | 상태 |
|---|---|---|---|
| F01 | KO/EN 토큰 수 관계 | D-04 | GENERATED |
| F02 | TP/logTP 분포·ECDF | D-04 | GENERATED |
| F03 | source×domain 기술 TP | D-04+D-01 | GENERATED |
| F04 | 정확 분해 (logCR×logBDR) | D-02/D-04 | GENERATED |
| F05 | byte-density vs compression | D-02/D-04 | GENERATED |
| F06 | 형태론 partial effect | NB09 M2 vs M1 | **DEFERRED_BY_DEPENDENCY** |
| F07 | 정제된 극단값 감사 | local audit | GENERATED |
| F08 | source/domain 설명 forest | NB09 | **DEFERRED_BY_DEPENDENCY** |
| F09 | Track B | NB12 | **DEFERRED_BY_DEPENDENCY** |

추가로 G5 review/identifiability를 위한 참고용 figure 4종:
`EDA_REF_M3_01_chunk_scale_vs_length`, `EDA_REF_SM_01_script_mixing_redundancy`,
`EDA_REF_ID_03_source_domain_support`, `EDA_REF_ID_04_cell_direction_support`
(모두 canonical `Fxx`가 아니라 `EDA-REF-*` 명명을 유지).

`NB08-RQ1-Vxx`, `NB06_D05_Vxx`는 참고용 result-communication figure이며 여기서 canonical
`Fxx`로 재명명하지 않았다.

## 5. G5 review 참조

| id | 내용 | 이 notebook의 처리 |
|---|---|---|
| `M3-01` | M3 collinearity trigger(조건수 134.57, `pair_log_size` VIF 1,252.61) | EDA-REF-M3-01: chunk 규모가 절대 길이와 강하게 연관됨을 시각화(r=0.94-0.97). 변수를 드롭하지 않음. |
| `SM-01` | `script_type_count~script_switch_count` ρ≥0.95 | EDA-REF-SM-01: KO ρ=0.9910, EN ρ=0.9994를 독립 재계산(교차검증). `PRE_NB09_REPRESENTATIVE_FEATURE_REVIEW_REQUIRED` — 대표 feature 미선정. |
| `ID-03` | source×domain 비분리 식별 | source×domain support heatmap(5개 관측 셀만 존재). |
| `ID-04` | 026에 EN_TO_KO 관측 없음 | cell×direction heatmap(빈 칸 3개, 근-단일 2개 노출). |

## 6. Anomaly 참조

| id | status | 요지 |
|---|---|---|
| `EDA-REF-EOJEOL1-01` | EXPECTED_BOUNDARY | `eojeol_count=1` 42,096건(1.10%) — analyzer artifact, 언어적 복잡도 아님(R3). |
| `EDA-REF-TPEXT-01` | REVIEW_REQUIRED | TP≥10 또는 ≤0.1 극단 14건 — 원문 비공개, 로컬 감사 필요. |
| `EDA-REF-DISC-01` | REVIEW_REQUIRED | representation reversal 재계산치(99.66%)가 비canonical V2 checkpoint(71.05%)와 불일치 — Director/Claude-B 대조 검토 권고. |

## 7. Claim boundary

허용: 위 §1의 "이 notebook의 역할" 열. 금지: causal 언어, RQ1 재검정, RQ3-RQ6의 조건부/증분/
메커니즘 설명력 주장, G5 review trigger를 근거로 한 변수 제거/대표 feature 선정, source/domain
순수 효과·`cell×direction` 상호작용 추정, D-02~D-05 재생성.

## 8. Reproduction

```bash
cd <this-worktree>
export PYTHONPATH="$PWD/src"
.venv/bin/python -m jupyter nbconvert --to notebook --execute --inplace \
  --ExecutePreprocessor.timeout=1800 \
  --ExecutePreprocessor.kernel_name=<a kernel pointing at this repo's .venv> \
  notebooks/07_eda_and_decomposition.ipynb
```

D-02/D-03/D-04는 canonical `data/registry/`에 대한 symlink, D-05는 검증된 소스에서의 실제
복사본(하드링크 아님)이어야 한다. 재실행은 SHA-256 5/5, N=3,835,988, pair-set md5
`d9660d654ee449e4d0c23a0070225274`를 fail-closed로 재확인한다.

## 9. 산출물

```
notebooks/07_eda_and_decomposition.ipynb
outputs/reports/NB07_CANONICAL_DESCRIPTIVE_SUMMARY_v001.json
outputs/reports/NB07_ANOMALY_REGISTER_v001.json
outputs/manifests/NB07_FIGURE_MANIFEST_v001.json
outputs/figures/nb07/  (F01-F05,F07 + EDA-REF-M3-01/SM-01/ID-03/ID-04 + 한글 폰트 smoke)
```

원문 KO/EN 문장, 복구 가능한 pair 전체, token/chunk ID 배열은 어디에도 커밋되지 않았다.

```
NB07_CANONICAL_DESCRIPTIVE_EDA_COMPLETE
READY_FOR_CLAUDE_B_NB07_AUDIT
DO_NOT_MERGE_MAIN
```
