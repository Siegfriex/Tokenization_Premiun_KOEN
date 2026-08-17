# Phase 2 — `02_normalize_and_qc.ipynb` Precontract v1.1 (minimal QC revision)

**Status: CONTRACT DESIGN ONLY.** `CR-003`(`research/g1-gate-claude@566f30b`)는 아직 승인되지 않았다. 이 문서는 **계약 설계까지만** 수행하며, Phase 2의 공식 실행 권한을 전제하지 않는다. Notebook 구현 없음, 565만 행 전체 실행 없음. (CR-003은 이번 개정에서 별도의 문서 정리 사안으로 취급되며 — §8 참조 — 더 이상 이 계약 자체의 QC 설계를 막는 blocker로 다루지 않는다.)

**Branch:** `research/p2-qc-claude` (동일 브랜치, 신규 브랜치 생성 없음)
**Base (P2-FIX-01로 정정):** `origin/integration/g1@691a378d2047eb4e4d18c2c5060cd6c2498f77fe` (Wave 3C 최종 HEAD — D-01 독립감사 + DuckDB runtime-safety + ENG-OBS-001 progress heartbeat + sanitized EDA support 전부 통합됨). v1의 `@526a14c` 표기는 오류였다 — 그 시점 이후 origin이 3개 커밋(progress-observability, EDA sanitized support) 더 전진했고, 실제 브랜치 히스토리는 이미 `691a378`에서 분기했다.
**Author:** Claude, Research/Data/Statistics Orchestrator

## Revision history

- **v1 (이전)**: 초기 설계 — LID를 통계/신경망 모델 후보까지 포함해 비교, semantic QC gating 방식을 미해결로 남김, tokenizer round-trip을 QC 게이트에 직접 구현, `duplicate_group_id`를 LR-01 근거로 과잉 주장, `EXACT_UNIQUE_CONTENT_DENOMINATOR`를 산술 근사로 정의, D-01 `representative_pair_id`를 분석 생존자로 오용.
- **v1.1 (이번, Director/Vice-Director 지시 반영)**: 025/026이 이미 구조화된 curated AIHub parallel corpus(명시적 train/validation, pair 필드, record identity, raw locator/hash lineage 보유)이며 Phase 2가 open-web pair-mining 문제가 **아님**을 근거로 QC를 방어 가능한 최소 스택으로 축소. 아래 §1-§8이 정확한 변경 내역이다.

---

## 0. Purpose and scope boundary

Canonical notebook: `02_normalize_and_qc.ipynb`.

```
D-01 raw registry (PAIR_REGISTRY_v001.parquet, 5,652,925 rows, 44 cols)
  → deterministic normalization (raw → nfc → analysis)
  → minimal structural QC flags (전부 독립 계산, §3)
  → exact-dedup disposition (representative vs non-representative, no deletion, §4)
  → language-side sanity smoke review (REVIEW ONLY, never hard-reject, §5)
  → population-level rule-based accepted/review/rejected disposition (§3c, §7 — Q0 RESOLVED)
  → decode-integrity check (Unicode-level only; NOT tokenizer roundtrip, §8 재정의)
  → aggregate QC-flow / pass-rate reporting (4개 분모, §6)
  → G1 closure evidence (partial — §10)
```

**Explicitly out of scope for this notebook** (belongs to later Phase per §37):
- Token-premium computation, `TP_i`/`logTP_i`, exact decomposition (D-04, Phase 4/5)
- **`o200k_base` encode→decode tokenizer roundtrip 측정 — 이제 명시적으로 G3/`05_o200k_measurement.ipynb`의 몫 (§8 재정의, 이전 버전에서의 중복 제거)**
- Morphology measurement (D-03, Phase 4, Kiwi)
- Any explanatory/predictive model (M0-M3, Phase 5)
- Regex chunk measurement (D-05)
- **어떤 형태의 통계적/신경망 언어감지 모델(Lingua, fastText, transformer LID 등) — CLOSED, 도입하지 않음 (§5)**
- **개체명 인식(NER) 휴리스틱/모델 — DEFERRED, 이번 Phase에서 발명하지 않음 (§6)**

## 1. SSOT-first audit — classification (개정)

| Rule | SSOT ref | Classification |
|---|---|---|
| `*_text_raw` immutable | §11 | SSOT_EXPLICIT |
| `*_text_nfc` = NFC only | §11.1 | SSOT_EXPLICIT |
| `*_text_analysis` = NFC + **edge-only** BOM 제거 + 외곽 whitespace trim, 내부 whitespace/BOM/zero-width 보존 | §11.1 (P2-FIX-05로 명시화) | SSOT_EXPLICIT |
| Forbidden silent ops | §11.2 | SSOT_EXPLICIT |
| 구조적 hard-exclusion (empty/exact-dup/markup/control-char/decode-integrity) | §10.1 | SSOT_EXPLICIT existence; threshold = **ENGINEERING_PARAMETER**(신규 분류, 아래 참조) |
| **LID 방법 자체("언어 식별이 명백히 잘못된 pair"의 구현 방식)** | §10.1 | **CLOSED — NO MODEL.** Director/Vice-Director 지시로 결정 완료: deterministic script-based review-only smoke check만 사용(§5). 더 이상 IMPLEMENTATION_CHOICE_REQUIRED 아님 |
| Smoke-flag(review-only) threshold(BOM/control-char 비율, script-mix 비율, short/long text 등) | §10.1/§10.2 flag 존재, 숫자 미지정 | **ENGINEERING_PARAMETER** — "review 전용 flag의 threshold는 estimand-level 결정이 아니다"(directive §8). Decision Queue에 올리지 않고 이 문서가 직접 확정 |
| `high_digit_ratio_flag`/`high_punctuation_ratio_flag` threshold = `>0.20` | D-RD-01 | DIRECTOR_APPROVED_EXTENSION — 재논의 안 함 |
| Semantic QC 3-step | §10.3 | SSOT_EXPLICIT |
| Manual audit N=500 | D-RD-01/AMB-06 | DIRECTOR_APPROVED_EXTENSION — 재논의 안 함 |
| Audit rubric 2/1/0 | §10.3 | SSOT_EXPLICIT, 그대로 유지 |
| 자동 유사도 score가 주 결과변수를 gate하지 않음(T-01) | §10.3, T-01 | SSOT_EXPLICIT — **강화됨**: 이번 개정은 자동 유사도 계산 자체를 population 실행에서 제거(§3), 그러므로 이 게이팅 금지 규칙이 사실상 자동 충족 |
| **`accepted` 판정이 개별 row manual-audit-gated인지, population rule-based인지** | §10.3 | **RESOLVED (Q0 CLOSED, 이번 개정)** — population rule-based, 500쌍은 calibration/validation 전용. §3c/§7 참조 |
| D-01 `representative_pair_id` = provenance pointer, **분석 생존자 아님** | D-01 precontract §7 | SSOT_EXPLICIT (P2-FIX-02로 이번 문서가 명시적으로 분리) |
| `duplicate_group_id` = **exact raw pair identity만**, LR-01 near-duplicate/paraphrase grouping을 만족시키지 않음 | D-01 registry.py, §23 | SSOT_EXPLICIT (P2-FIX-03 — v1의 과잉 주장 정정) |
| domain/source_id/source_provenance_raw group-conflict 값 resolution | D-01 precontract §7 | 여전히 **UNRESOLVED**, Phase 2도 답하지 않음 (변경 없음) |
| `EXACT_UNIQUE_CONTENT_DENOMINATOR` 산출 방식 | 엔지니어링 | `COUNT(DISTINCT duplicate_group_id)` 직접 계산만 인정, 산술 근사 금지 (P2-FIX-04) |
| P2 decode-integrity check vs G3 tokenizer roundtrip 분리 | §10.1, §25.4 | SSOT_EXPLICIT existence(둘 다), **scope 분리는 이번 개정에서 확정**(§8) |
| `named_entity_heavy_flag` | §10.2 flag 존재, 방법 미지정 | DEFERRED(이번 개정) — nullable, `named_entity_evaluation_status=DEFERRED`. Director 결정 대상에서 제외, Phase 3/4로 이월 |
| Reproducibility fields (`normalization_rule_version`, `normalization_ops`) | §11.1 | SSOT_EXPLICIT, v002 신규 컬럼 |
| ENG-OBS-001 heartbeat | 2026-08-16 17:32 로그 | DIRECTOR_APPROVED_EXTENSION — 지금은 `src/tokenization_premium/progress.py`로 이미 구현되어 `integration/g1`에 병합되어 있음(§9 확인) |

## 2. Normalization contract (변경 없음, P2-FIX-05로 invariant 명시화만 추가)

```python
import unicodedata

def to_nfc(raw: str) -> str:
    return unicodedata.normalize("NFC", raw)

_BOM = "﻿"

def to_analysis(raw: str) -> str:
    step1 = unicodedata.normalize("NFC", raw)   # 1. NFC
    step2 = step1.strip(_BOM)                   # 2. BOM 제거 — Python str.strip(chars) 의미상 EDGE(선두/말미)만, 내부는 미변경
    step3 = step2.strip()                        # 3. 외곽 whitespace trim, 내부 whitespace는 미변경
    return step3
```

**P2-FIX-05 (명시화, 동작 변경 없음)**: `step2 = step1.strip(_BOM)`은 Python 언어 자체의 정의상 이미 edge-only이다 — `str.strip(chars)`는 문자열의 **앞뒤에서만** `chars` 집합에 속한 문자를 제거하며 내부는 절대 건드리지 않는다. 그러나 v1 문서의 "BOM 제거"라는 표현이 "모든 위치의 BOM 제거"로 오독될 수 있었으므로, 이 조항으로 **내부(internal) U+FEFF와 zero-width 문자는 `to_analysis` 이후에도 관측 가능해야 한다**는 invariant를 명시적으로 못 박는다. 이것이 바로 `unicode_anomaly_flag`가 `ko_text_raw`/`en_text_raw` 원문(정규화 이전) 기준으로 정의되어야 하는 이유다 — 정규화가 증거를 지워버리면 이상 탐지 자체가 불가능해진다.

**금지 (§11.2, 변경 없음)**: 내부 whitespace collapse, punctuation ASCII 치환, lowercasing, full-width/half-width 통합, NFKC, 숫자 치환, emoji 제거, 조사/어미 분리.

### Tests (변경/추가)

- (v1의 6개 테스트 유지)
- **신규** `test_analysis_preserves_internal_bom_and_zerowidth` — `to_analysis("텍스﻿트")`의 결과에 내부 `﻿`가 그대로 남아 있는지 확인(edge 제거만, 내부 무손실).

## 3. QC flags — minimal structural stack (대폭 축소)

**설계 원칙 변경**: 025/026은 이미 구조화된 curated corpus다 — record identity, raw locator, hash lineage가 D-01에서 이미 확보되어 있으므로, Phase 2 QC는 **오픈웹 pair-mining 수준의 방어**가 아니라 **D-01 handoff 검증 + 결정적 구조 이상 탐지**에 집중한다. 모델 스택을 추가하지 않는다.

### 3a. 구조적 hard-exclusion 후보 (5개, 전부 결정적, 전부 독립 계산)

| Flag | 정의 | Threshold(ENGINEERING_PARAMETER, 이 문서가 직접 확정) |
|---|---|---|
| `empty_text_flag` | `ko_text_analysis`/`en_text_analysis` 정규화 후 빈 문자열 | 없음(존재/부재 자체가 기준) |
| `exact_duplicate_flag` | `pair_id != analysis_representative_pair_id`(§4, D-01의 `representative_pair_id`가 아님 — P2-FIX-02) | 없음 |
| `markup_dominant_flag` | HTML 태그/URL/코드 패턴 매치 문자 수 ÷ 전체 문자 수 | `> 0.5` |
| `control_char_excess_flag` | 제어문자(`Cc`, tab/newline 제외)+비정상 zero-width 문자 수 ÷ 전체 codepoint 수 | `> 0.05` |
| `decode_integrity_flag` | §8 참조 — Unicode 레벨 decode 무결성만(토크나이저 아님) | U+FFFD 존재 또는 unpaired surrogate 존재 |

**제거됨(v1 대비)**: `lid_failure_flag`(→ §5로 대체, review-only로 강등), `semantic_qc_fail_flag`(→ population 자동 계산 제거, §7의 500쌍 manual audit 전용 정보로 이동), `roundtrip_failure_flag`(→ `decode_integrity_flag`로 축소, tokenizer 부분은 G3로 이관).

### 3b. Review-only / advisory flags (게이팅 없음, 순수 descriptive metadata)

| Flag | 정의 | Threshold |
|---|---|---|
| `lang_side_anomaly_review_flag` + `lang_side_anomaly_reason` | §5 참조 | §5 |
| `short_text_flag`/`long_text_flag` | `length_stratum`(EN codepoint quintile, D-RD-01) 최하/최상위 분위 | 분위 기준 재사용(신규 절대 threshold 발명 안 함) |
| `high_digit_ratio_flag`/`high_punctuation_ratio_flag` | 숫자/구두점 codepoint 비율 | `> 0.20`(D-RD-01, 고정) |
| `script_mix_flag` | Hangul과 Latin이 각각 전체 alnum codepoint의 일정 비율 이상 동시 존재 | `>= 0.10` 양쪽 모두 |
| `unicode_anomaly_flag` | §2 정의(raw 텍스트 기준, 정규화 이후 텍스트 아님) | §2 |
| `translation_quality_review_flag` | §7의 500쌍 manual audit에서 `language_side_status != NO_APPARENT_SIDE_SWAP` 이거나 rubric score `<= 1`인 경우에만 값 존재(그 외 audit 미대상 row는 null) — D-01의 `translation_direction_review_flag`(방향 애매성)와 다른 필드, 혼동 금지 | audit 결과 직접 사용, 별도 threshold 없음 |
| `named_entity_heavy_flag` | **nullable, 항상 null** | 해당 없음 — `named_entity_evaluation_status = "DEFERRED"`(§6) |

이 표의 threshold는 전부 **ENGINEERING_PARAMETER**로 분류되어 이 문서가 직접 확정한다 — review-only 표시에만 영향을 주고 어떤 row의 `pair_quality_status`도 바꾸지 않으므로 estimand-level Director 결정이 아니다(directive §8).

### 3c. Disposition (Q0 RESOLVED — population rule-based)

```
primary_rejection_reason (deterministic priority, REPORTING ONLY):
  1. empty_text_flag
  2. decode_integrity_flag
  3. markup_dominant_flag
  4. control_char_excess_flag
  5. exact_duplicate_flag   (마지막 — 중복은 구조적 오류보다 후순위 보고)

secondary_rejection_flags = 위 5개 중 primary로 선택되지 않은 나머지 true flag 전체

pair_quality_status:
  rejected  ⟺ 위 5개 구조적 flag 중 하나 이상 true
  accepted  ⟺ 위 5개 전부 false
```

**더 이상 `review`를 population-level 영구 상태로 남기지 않는다.** §7의 500쌍은 이 rule-based 판정이 방향적으로 타당한지 검증하는 별도 calibration statistic이며, 감사 대상이 아닌 나머지 row는 감사받지 않았다는 이유만으로 강등되지 않는다(directive §3, "Unaudited rows are not downgraded merely because they were not manually inspected"). `lang_side_anomaly_review_flag`/`translation_quality_review_flag`가 true인 row도 **자동으로 rejected가 되지 않는다** — 이들은 review-only(advisory) metadata다.

## 4. Exact duplicate disposition (P2-FIX-02/03 반영)

- D-01 상속(변경 없음): `duplicate_group_id`(exact raw KO+EN content identity), D-01 `representative_pair_id`(provenance pointer, 유지), 4종 conflict flag.
- **P2-FIX-02 — 신규 분리**: D-01의 `representative_pair_id`는 **provenance pointer일 뿐 분석 생존자가 아니다.** Phase 2는 별도 필드 `analysis_representative_pair_id`를 정의한다:

```
group의 candidates = 해당 duplicate_group_id를 공유하는 모든 pair_id
eligible = candidates 중 logical_corpus ∈ {025, 026} (= primary_analysis_eligible=true, source_portfolio 025/026과 동치)
analysis_representative_pair_id =
    min(eligible)         if eligible is non-empty
    else min(candidates)  # group 전체가 Legacy-only인 경우의 결정적 fallback
```

- `duplicate_disposition` ∈ `{REPRESENTATIVE, NON_REPRESENTATIVE_DUPLICATE}` = `pair_id == analysis_representative_pair_id` 여부(D-01의 `representative_pair_id`가 아니라 위 신규 필드 기준).
- `analysis_eligible_exact_dedup` (bool) = `duplicate_disposition == REPRESENTATIVE`. row는 삭제하지 않는다 — v002도 v001과 동일하게 5,652,925 rows.
- Mixed-direction/domain/source conflict: D-01 값 그대로 상속, 값으로 resolve하지 않음(변경 없음, D-01 precontract §7의 미해결 유지).
- **P2-FIX-03 — 정정**: v1은 "`duplicate_group_id`가 LR-01의 near-duplicate cluster group key 역할을 한다"고 서술했으나 이는 **과잉 주장이었다.** `duplicate_group_id`는 **exact byte-identical raw KO+EN pair identity만** 포착한다 — paraphrase나 fuzzy near-duplicate는 어떤 컴포넌트도 아직 클러스터링하지 않았다. §23 LR-01이 요구하는 "near-duplicate cluster" group key는 이것과 **다른, 아직 설계되지 않은** future Phase-5 문제로 남는다. 이 문서는 그 설계를 수행하지 않으며, `duplicate_group_id`를 그 대체물로 제시하지 않는다.

## 5. Language-side sanity smoke check (LID 전면 재설계)

**개념 전환**: "언어 식별(LID)"이 아니라 **언어 방향(side) 데이터 배선(wiring) sanity check**다. 025/026/Legacy는 이미 ko_text/en_text 컬럼이 스키마 레벨에서 확정된 curated bilingual parallel corpus이며, 이는 open-set 언어 감지 문제가 아니다.

**제거(CLOSED, 재도입하지 않음)**: Lingua 추론, fastText, 통계/신경망 LID, confidence score, LID threshold 최적화, LID 기반 자동 hard-exclusion.

### Perplexity 근거 메모의 위치

Vice Director가 전달한 외부 Perplexity 근거 메모(현재 `evidence/g1-perplexity` 브랜치에는 아직 별도 파일로 커밋되어 있지 않음을 확인함 — 이 세션은 그 메모의 결론을 지시문 본문을 통해 전달받아 인용함)의 결론:
- Deterministic Unicode script 근거가 이 좁은 과업(닫힌 집합 스키마 정합성 검증)에 비례적으로 적합.
- Lingua(KO/EN 제한)는 기술적으로 사용 가능하나 primary pipeline에 불필요.
- fastText `lid.176`은 model/license lineage 부담을 추가하나 primary 대비 명확한 이득이 없음.

이 메모는 **두 의존성을 도입하지 않는 근거**로만 사용한다. 향후 정식 written artifact가 `evidence/g1-perplexity`에 committed되면 이 인용을 그 커밋 SHA로 교체해야 한다(이 문서 자체가 그 산출을 대신 발명하지 않는다).

### New field

```
lang_side_anomaly_review_flag: bool
lang_side_anomaly_reason: enum, nullable
  - KO_NO_HANGUL_LATIN_DOMINANT
  - EN_NO_LATIN_HANGUL_DOMINANT
  - INSUFFICIENT_LINGUISTIC_EVIDENCE
  - NONE
```

**규칙(deliberately conservative, review-only)**:

```python
def ko_side_flag(ko_text: str) -> str:
    hangul = count_hangul(ko_text)          # U+AC00–U+D7A3
    latin = count_latin(ko_text)             # A-Za-z
    alphabetic_evidence = hangul + latin      # 숫자/구두점/공백 제외
    if alphabetic_evidence < MIN_EVIDENCE:    # 엔지니어링 threshold, 예: 5 codepoints
        return "INSUFFICIENT_LINGUISTIC_EVIDENCE"
    if hangul == 0 and latin >= SUBSTANTIAL:  # 엔지니어링 threshold, 예: latin >= 5
        return "KO_NO_HANGUL_LATIN_DOMINANT"
    return "NONE"

# en_side_flag는 대칭 — Latin==0 and Hangul substantial → "EN_NO_LATIN_HANGUL_DOMINANT"

lang_side_anomaly_review_flag = (ko_side_flag != "NONE") or (en_side_flag != "NONE")
lang_side_anomaly_reason = 위 두 reason 중 NONE이 아닌 것(둘 다 해당되면 KO 우선 — reporting 편의, 정보 손실은 secondary로 별도 기록 가능)
```

- **REVIEW ONLY. 자동 hard-reject 금지.** `lang_side_anomaly_review_flag`는 `pair_quality_status`를 gate하지 않는다(§3c).
- 한국어 텍스트 속 영어 기술 용어, 영어 텍스트 속 한국어 고유명사는 **정상**이며 anomaly가 아니다 — 그래서 조건이 "Hangul/Latin 혼재"가 아니라 "target script가 **전무(==0)**하고 반대쪽 script가 상당량(substantial) 존재"로 의도적으로 보수적이다.
- 짧은 텍스트/비언어적 값(숫자만, 기호만 등)은 `INSUFFICIENT_LINGUISTIC_EVIDENCE`로 분류되며 실패가 아니다.
- 정확한 `MIN_EVIDENCE`/`SUBSTANTIAL` 숫자는 ENGINEERING_PARAMETER(§1) — review-only 표시에만 영향을 주므로 Decision Queue로 올리지 않는다.

의존성 영향: 0 (stdlib `unicodedata`/정규식만, 신규 패키지 없음).

## 6. Named entity flag — DEFERRED, no heuristic invented

```
named_entity_heavy_flag: bool, nullable, 이번 Phase 2 v1.1에서는 항상 null
named_entity_evaluation_status: string, 항상 "DEFERRED"
```

휴리스틱 NER(대문자 시작 단어 비율 등)을 발명하지 않는다 — v1이 제안했던 proxy heuristic은 폐기한다. 정식 feature 근거가 있는 Phase 3/4(Representation/Morphology) 이후 별도 CR로 정의한다. 게이팅 없음.

## 7. Semantic QC (Q0 RESOLVED)

- Audit N = **500**(고정, 재논의 안 함).
- Strata: `domain × sentence_type × translation_direction × source_id × length_stratum`(변경 없음).
- Rubric: 2/1/0(변경 없음, §10.3 그대로).
- **신규 audit item** `language_side_status` (500쌍 manual audit에만 존재, population 컬럼 아님):

```
language_side_status: enum
  - NO_APPARENT_SIDE_SWAP
  - POSSIBLE_ANOMALY
  - CLEAR_SIDE_SWAP
  - INSUFFICIENT_SHORT_NONLINGUISTIC
```

- **자동 multilingual similarity score는 population 실행에서 제거한다(mandatory 아님).** `pair_quality_score`는 Phase 2 population 레벨에서 계속 null이며, 오직 500쌍 manual audit 대상 row에 한해 audit rubric 점수(2/1/0)를 별도 audit 아티팩트(§9)에 기록한다 — population 스키마(`PAIR_REGISTRY_v002`)를 대부분-null 컬럼으로 오염시키지 않는다.
- 자동 유사도가 **나중에** sensitivity로 재도입될 수 있는 유일한 조건: manual audit이 실질적인 semantic-alignment 문제(예: `language_side_status=CLEAR_SIDE_SWAP` 비율이 유의미하게 높거나 rubric score=0이 다수)를 드러낼 경우에 한함(directive §3). 이 조건이 실제로 충족되었는지는 이 문서가 판단하지 않는다 — 500쌍 audit 실행 이후에만 평가 가능.
- **Q0 RESOLVED**: population `pair_quality_status`는 개별 row manual-audit-gated가 **아니다.** §3c의 5개 구조적 flag만으로 rule-based accepted/rejected를 population 전체에 부여한다. 500쌍은 이 규칙의 population-level calibration/validation 통계로만 기능하며, 감사받지 않은 row를 그 사실만으로 강등하지 않는다.
- Manual audit 로지스틱스(누가/어떻게 500쌍을 배정하는지)는 여전히 사람의 판단이 필요한 실제 미해결 사안이다 — §8 Decision Queue 참조(collapse 이후에도 유일하게 남는 연구적 결정).

## 8. Roundtrip scope — clarified, no duplication

- **Phase 2 (`02_normalize_and_qc.ipynb`)**: source/text decoding + Unicode 무결성만.

```python
def decode_integrity_ok(text: str) -> bool:
    if "�" in text:          # 이전 손실 디코드의 증거(replacement character)
        return False
    if has_unpaired_surrogate(text):  # 정의: lone high/low surrogate codepoint
        return False
    return True

decode_integrity_flag = not (decode_integrity_ok(ko_text_analysis) and decode_integrity_ok(en_text_analysis))
```

- **G3 / `05_o200k_measurement.ipynb`**: `o200k_base` 전체 encode→decode round-trip, token IDs, token count, `TP_i`/`logTP_i`, compression penalty — 이 전부가 D-04 스키마(§12.4)이며 Phase 2는 이를 **생성하지 않는다.**
- **의존성 변화**: v1은 Phase 2 QC 게이트에 `tiktoken`을 직접 사용했으나(§8, v1), v1.1은 이를 완전히 제거한다 — Phase 2는 순수 stdlib `unicodedata`/정규식만으로 동작하며 tokenizer 의존성이 없다. `tiktoken`은 G3에서만 로드된다.
- SSOT §25.4의 "encode/decode roundtrip 100% PASS" 요구는 그대로 유효하나, 그 authoritative full-population 증거는 **G3의 소관**이며 Phase 2가 미리 만들지 않는다(중복 제거).

## 9. Output contract (갱신)

```
data/registry/PAIR_REGISTRY_v002.parquet         # untracked, raw-text 보유(변경 없음)
outputs/reports/QC_FLOW_v001.csv                  # flag/disposition aggregate, raw text 없음
outputs/reports/LID_QC_PASS_RATE_v001.csv         # §6(pass-rate denominators)의 4개 분모
outputs/reports/SEMANTIC_QC_MANUAL_AUDIT_v001.csv # 신규 — 500쌍 audit 결과만(pair_id, rubric score, language_side_status), population 스키마와 분리
outputs/manifests/QC_MANIFEST_v001.json           # SHA-256, row count, schema version,
                                                   #   execution_code_commit + artifact_record_commit,
                                                   #   contract hashes(이 문서 v1.1 포함)
```

### v002 신규 컬럼 (v1.1 최종, v001의 44개 컬럼에 추가만, 삭제 없음)

| 컬럼 | 타입 | 비고 |
|---|---|---|
| `normalization_rule_version`, `normalization_ops` | string | §2, 변경 없음 |
| `unicode_anomaly_flag` | bool | §2, raw 기준 |
| `empty_text_flag`, `markup_dominant_flag`, `control_char_excess_flag`, `decode_integrity_flag` | bool ×4 | §3a — **`lid_failure_flag`/`semantic_qc_fail_flag`/`roundtrip_failure_flag`는 v1.1에서 제거됨** |
| `short_text_flag`, `long_text_flag`, `high_digit_ratio_flag`, `high_punctuation_ratio_flag`, `script_mix_flag`, `translation_quality_review_flag` | bool ×6 | §3b |
| `lang_side_anomaly_review_flag` | bool | §5, 신규 |
| `lang_side_anomaly_reason` | string enum, nullable | §5, 신규 |
| `named_entity_heavy_flag` | bool, nullable, 항상 null(Phase 2) | §6 |
| `named_entity_evaluation_status` | string, 항상 `"DEFERRED"` | §6, 신규 |
| `primary_rejection_reason` | string, nullable | §3c |
| `secondary_rejection_flags` | string(canonical JSON array) | §3c |
| `analysis_representative_pair_id` | string | §4, 신규 — D-01의 `representative_pair_id`(유지)와 별개 |
| `duplicate_disposition` | string enum | §4 — `analysis_representative_pair_id` 기준으로 재정의 |
| `analysis_eligible_exact_dedup` | bool | §4 |
| `qc_stage_status`(값 갱신: `PENDING_PHASE2`→`PHASE2_COMPLETE`) | string | 기존 컬럼 |
| `pair_quality_status`(rule-based, population 전체) | string | §3c — **더 이상 대부분 `review`로 남지 않음** |
| `pair_quality_score`(population은 null, audit 대상만 별도 아티팩트에 기록) | float, 대부분 null | §7 |
| `ko_text_nfc`/`en_text_nfc`/`ko_text_analysis`/`en_text_analysis` | string | §2, 실값 채움 |

**제거된 v1 컬럼**: `lid_failure_flag`, `semantic_qc_fail_flag`, `roundtrip_failure_flag`, `tokenizer_roundtrip_ok`(→ `decode_integrity_flag`로 대체, tiktoken 의존성 제거).

## 10. G1 closure matrix (변경 없음, 그대로 재확인)

| 항목 | CURRENT | PHASE2 REQUIRED EVIDENCE | PASS RULE | OWNER ARTIFACT |
|---|---|---|---|---|
| pair ID uniqueness | PASS | 없음 | `pair_id` distinct==total, null==0 | `PAIR_REGISTRY_RECONCILIATION_v001.csv` |
| null/duplicate integrity | PASS | 없음 | 구조적 null/dup 가시화 완료 | 위와 동일 |
| source/license metadata | **PASS**(Vice Director adjudication) | 없음. `provenance_closure_status`는 **OPEN NON-BLOCKING RISK** | self-asserted 기록 + non-verification 명시 완료 | `SOURCE_REGISTRY_v001.parquet` |
| LID/QC pass rate | NOT CLOSED | `QC_FLOW_v001.csv`+`LID_QC_PASS_RATE_v001.csv` 생성, §6의 4개 분모 보고 — **disposition 규칙은 이제 확정됨(Q0 RESOLVED), 실행만 남음** | 4개 분모 산출 + rule 문서화·실행 가능 | `outputs/reports/LID_QC_PASS_RATE_v001.csv`, `QC_MANIFEST_v001.json` |

`D-RD-05`는 재논의하지 않는다(변경 없음).

## 11. QC pass-rate denominators (P2-FIX-04 반영)

```
RAW_RECORD_DENOMINATOR
  = 5,652,925

EXACT_UNIQUE_CONTENT_DENOMINATOR
  = COUNT(DISTINCT duplicate_group_id)     -- P2-FIX-04: 직접 COUNT(DISTINCT ...)만 인정
  -- v1의 산술 근사("RAW − Σafter-first ≈ 5,436,135")는 폐기한다.
  -- 참고: 두 계산이 이론상 같은 값이어야 하지만, 실제 인정되는 정의는
  --       COUNT(DISTINCT duplicate_group_id)이며 Phase 2 실행 시 이 SQL로만 산출한다.

PRIMARY_ELIGIBLE_DENOMINATOR
  = source_tier=='A' (025+026) = 2,700,345 + 1,350,162 = 4,050,507
  (`primary_cohort_policy.mode: all_qc_accepted_tier_a`와 명명 일관)

FINAL_ANALYSIS_DENOMINATOR
  = PRIMARY_ELIGIBLE_DENOMINATOR ∩ analysis_eligible_exact_dedup=true ∩ pair_quality_status='accepted'
  (규칙은 확정됨 — §3c/§7, Q0 RESOLVED. 실측값은 Phase 2 실행 시에만 산출)
```

## 12. ENG-OBS-001 적용 (갱신 — tiktoken 단계 제거, decode-integrity로 대체)

| Stage | total 알려짐? | progress unit | checkpoint | memory class | restartability |
|---|---|---|---|---|---|
| v001 registry read | Yes | rows read | batch당 | 낮음 | 무상태 재실행 |
| Normalization pass | Yes | rows processed | batch당 | 낮음 | idempotent |
| 구조적 QC flag 계산(§3a/§3b) | Yes | rows scanned | batch당 | 낮음 | idempotent |
| Language-side smoke check(§5) | Yes | rows scanned | batch당 | 낮음(stdlib만) | idempotent |
| Duplicate disposition join(`analysis_representative_pair_id`) | Yes(group 수 사전 계산 가능) | groups resolved | DuckDB query 단위 | 중간(8GB 캡, runtime-safety 계약) | 전체 재실행(atomic COPY) |
| Decode-integrity check(§8) | Yes | pairs checked | batch당 | 낮음(stdlib만, tiktoken 없음) | idempotent |
| Manual audit(500쌍) | Yes(고정 500) | audited pairs | 개별 단위 | 해당 없음 | 해당 없음 |
| Manifest/report 저장 | Yes | 파일 수 | 파일 단위 | 낮음 | atomic replace |

실제 구현은 이미 `integration/g1@691a378`에 병합된 `src/tokenization_premium/progress.py`(`ProgressHeartbeat`)를 그대로 재사용한다(신규 구현 불필요, API 확인 완료).

---

**요약(v1.1)**: LID는 모델 없는 review-only smoke check로 폐쇄, semantic QC gating(Q0)은 population rule-based로 해결, tokenizer roundtrip은 G3로 완전히 이관, duplicate representative 개념은 provenance-pointer/analysis-survivor로 분리, `EXACT_UNIQUE_CONTENT_DENOMINATOR`는 정확한 COUNT(DISTINCT)로 교정, named-entity는 명시적으로 DEFERRED. 남은 미해결 사안은 `docs/research/P2_QC_DECISION_QUEUE_v1.md`(collapsed)를 참조 — Director 승인 대기 항목은 이제 manual-audit 로지스틱스 1건과 CR-003 문서 정리뿐이다.
