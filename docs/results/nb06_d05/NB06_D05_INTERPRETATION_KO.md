# NB06 / D-05 해설 — regex chunk 측정을 어떻게 읽을 것인가

이 문서는 [README.md](README.md)보다 깊은 한국어 해설입니다.
기술 용어는 첫 등장 시 `한국어 설명(Original English Term)`으로 병기하고,
코드 변수명과 schema field는 번역하지 않습니다.

---

## 1. 왜 tokenizer 처리를 단계로 분해하는가

"한국어 문장이 영어 번역보다 token을 더 많이 쓴다"는 사실만으로는 아무것도 설명되지
않습니다. 그것은 **결과**이고, 결과를 다시 말하는 것은 설명이 아닙니다.

`o200k_base` 같은 BPE 계열 tokenizer는 텍스트를 한 번에 token으로 바꾸지 않습니다.
적어도 두 단계를 거칩니다.

1. **1차 분할** — 하나의 정규식(`pat_str`)으로 텍스트를 조각(chunk)으로 자른다.
2. **2차 병합** — 각 조각 **안에서** mergeable ranks(BPE)를 적용해 최종 token을 만든다.

두 단계는 서로 독립적으로 결과에 기여합니다. 조각이 많아져도 각 조각이 token 하나면
token은 조각 수만큼만 나옵니다. 반대로 조각이 적어도 각 조각이 다섯 개로 갈라지면
token은 많아집니다. **두 축을 분리하지 않으면 어느 쪽이 작동하는지 알 수 없습니다.**

D-05는 정확히 이 분리를 위해 존재합니다.

---

## 2. regex chunk란 정확히 무엇인가

정규식 chunk(regex chunk)는 tokenizer가 BPE를 적용하기 **전에** 텍스트를 나눈 조각입니다.
SSOT §5 표기로는 `x → b=UTF8(x) → P_v(b) → T_v(P_v(b)) → N`에서 `P_v`의 출력입니다.

성질:

- **완전 분할** — 조각을 순서대로 이어붙이면 원문이 정확히 복원됩니다.
  손실되는 문자도, 중복되는 문자도 없습니다.
- **빈 조각 없음** — 길이 0인 조각은 만들어지지 않습니다.
- **결정적** — 같은 입력에 대해 항상 같은 조각열이 나옵니다.
- **문법을 모름** — 품사도, 단어 사전도 참조하지 않습니다.

D-05는 이 세 성질을 가정하지 않고 **매 행에서 검사**합니다. 위반이 있으면 조용히
넘어가지 않고 실패합니다(fail-closed).

---

## 3. o200k_base pat_str의 역할

`pat_str`은 `o200k_base` encoding에 내장된 하나의 긴 정규식입니다. 대략 다음과 같은
분기를 우선순위대로 적용합니다.

- 축약형(`'s`, `'re` 등)
- 선행 공백을 포함한 문자(letter) 덩어리
- 숫자(number) 덩어리 (자릿수 제한 있음)
- 구두점·기호 덩어리
- 개행·공백 덩어리

D-05는 이 정규식을 문헌에서 옮겨 적지 않습니다. 살아 있는 encoder 객체에서 직접 읽어
D-04가 동결한 sha256과 대조하고, 다르면 `ChunkConfigMismatch`로 즉시 멈춥니다.
"같은 tokenizer를 썼다"가 주장이 아니라 검사여야 하기 때문입니다.

chunk 유형(`chunk_type_share_*`)의 네 범주 — letter / number / punctuation / whitespace —
는 이 분기 구조를 그대로 반영한 우선순위 분류이며, 새 범주를 발명하지 않았습니다.

---

## 4. regex chunk와 morpheme의 차이

언어학적 형태론(linguistic morphology)은 문법 단위를 찾습니다.
정규식 청킹은 표면 문자 패턴만 봅니다.

`"학교에서"`를 예로 들면:

| 관점 | 분할 |
|---|---|
| morpheme (D-03, Kiwi) | `학교/NNG` + `에서/JKB` — 명사와 부사격 조사 |
| regex chunk (D-05) | `학교에서` 한 덩어리 — 공백 사이의 문자 덩어리일 뿐 |
| final token (D-04) | 이 덩어리가 BPE에서 다시 여러 조각으로 갈라짐 |

정규식은 조사 `에서`가 형태소라는 사실을 모릅니다. 한국어에서 어절은 어근에 조사·어미가
붙어 길어지므로, regex chunk는 **영어 단어보다 길고 정보 밀도가 높은 단위**가 됩니다.

이것이 §5에서 볼 관찰의 배경입니다 — 하지만 배경이지 **원인 증명은 아닙니다**.

---

## 5. regex chunk와 token의 차이

regex chunk는 BPE의 **입력**이고, token은 **출력**입니다.

영어에서는 흔한 단어 하나가 vocabulary에 통째로 들어 있어 chunk 하나 → token 하나가
자주 성립합니다(측정값 1.04). 한국어에서는 어절 형태가 워낙 다양해 통째로 등재되기
어렵고, 하나의 chunk가 여러 subword로 갈라집니다(측정값 2.02).

`ko_chunk_token_total`이 D-04에 저장된 실제 token 수와 일치하는지가 D-05의 핵심
검사이며, 이것이 성립하기 때문에 "이 chunk가 저 token들을 만들었다"고 말할 수 있습니다.

---

## 6. D-05 schema의 feature group

| group | field | 무엇을 말하는가 |
|---|---|---|
| **분할 규모** | `chunk_count` | 텍스트가 몇 조각으로 잘렸는가 |
| **조각 크기** | `mean_chunk_bytes`, `p50_chunk_bytes`, `p90_chunk_bytes`, `max_chunk_bytes` | 조각이 얼마나 긴가. p90/max는 긴 꼬리를 본다 |
| **확장 정도** | `tokens_per_chunk`, `max_tokens_per_chunk` | 조각 하나가 몇 개 token으로 갈라지는가 |
| **총량** | `chunk_token_total`, `chunk_byte_total` | D-04 및 원문 UTF-8 길이와의 정합성 검사에 쓰인다 |
| **구성** | `chunk_type_share_letter/number/punctuation/whitespace` | 어떤 종류의 조각으로 이루어져 있는가 |
| **pair 수준** | `pair_chunk_ratio` | `ko_chunk_count / en_chunk_count` |

백분위수는 nearest-rank로 계산합니다. 조각 수가 적은 짧은 문장에서 실제로 존재하지 않은
보간값이 나오지 않도록 하기 위해서입니다.

---

## 7. KO의 chunk 수가 EN보다 작다는 것의 의미

평균 13.56 대 19.50, 중앙값 11 대 15, pair 단위 비 `pair_chunk_ratio` 평균 0.711.
한국어 측은 영어 측의 약 71% 개수의 조각으로 같은 의미를 담습니다.

읽는 법:

- 한국어 어절은 조사·어미를 흡수해 공백 사이 덩어리가 길어집니다
  (`mean_chunk_bytes` 8.12 대 4.94, `p90` 13.96 대 8.81).
- 따라서 정규식이 자를 지점 자체가 적습니다.
- 즉 **1차 분할 단계에서는 한국어가 "더 잘게 쪼개지고 있지 않습니다."**

이 관찰은 "한국어는 애초에 더 많이 쪼개진다"는 직관을 **부정**합니다.
적어도 regex 단계에서는 그렇지 않습니다.

---

## 8. KO의 tokens_per_chunk가 크다는 것의 의미

평균 2.02 대 1.04, 중앙값 2 대 1.

읽는 법:

- 영어는 조각 하나가 대체로 token 하나입니다 — vocabulary가 그 형태를 이미 담고 있습니다.
- 한국어는 조각 하나가 평균 두 조각 이상으로 갈라집니다.
- 차이는 **1차 분할이 아니라 2차 병합 단계**에서 생깁니다.

주의: 이것은 vocabulary 구성에 대한 **관찰과 정합적인 서술**이지, vocabulary 구성이
원인이라는 **증명이 아닙니다**. D-05는 `o200k_base` 하나의 고정 설정에서 무엇이
관찰되는지만 말합니다.

---

## 9. 두 축이 반대 방향으로 움직인다는 것의 의미

```
ln(N_ko / N_en) = ln(C_ko / C_en) + ln( (N_ko/C_ko) / (N_en/C_en) )
    +0.2852     =     −0.3672     +           +0.6523
```

이 등식은 정의상 항상 성립합니다(측정된 최대 잔차 `4.7e-16`). 새로운 주장이 아니라
**분해 도구**입니다. 여기서 읽을 수 있는 것:

1. 두 항의 **부호가 반대**입니다. chunk 수 축은 한국어 token 수를 **줄이는** 방향으로,
   chunk당 token 축은 **늘리는** 방향으로 작용합니다.
2. 늘리는 쪽의 크기가 줄이는 쪽보다 커서 순효과가 양수(+0.2852)로 남습니다.
3. 따라서 **두 축을 합쳐서 하나의 "분할 정도"로 요약하면 상쇄가 숨겨집니다.**
   최종 token 수 차이를 이해하려면 반드시 분리해서 봐야 합니다.

이것이 D-05가 제공하는 분석적 기여입니다 — 답이 아니라, 답을 찾을 때 쓸 좌표계입니다.

---

## 10. 기존 RQ1과의 연결

세 질문을 혼동하지 않습니다.

| | 질문 | 담당 |
|---|---|---|
| **RQ1** | 토큰화 프리미엄(Tokenization Premium)이 존재하는가? | D-04 / NB05·NB08 |
| **NB06 / D-05** | tokenizer 내부의 regex-chunk 수준에서 어떤 구조 차이가 관찰되는가? | 이 문서 |
| **NB09 / M3** | 그 measured chunk block이 M2 이후에도 conditional explanatory information을 추가하는가? | 대기 |

RQ1은 **결과의 존재**를 묻습니다. D-05는 **내부 구조를 기술**합니다.
M3는 **그 구조가 설명력을 추가하는지**를 검정합니다. 셋은 서로 대체하지 않습니다.

D-05는 RQ1의 답을 바꾸지 않으며, 바꿀 수 있는 위치에 있지도 않습니다 —
token 수의 authority는 D-04 하나입니다.

---

## 11. 왜 이것만으로 원인이라고 말할 수 없는가

측정된 것은 **하나의 tokenizer, 하나의 설정, 하나의 cohort**에서의 연관 구조입니다.

말할 수 없는 이유:

- **대조군이 없다.** 다른 tokenizer, 다른 vocabulary 크기, 다른 정규식에서 같은 패턴이
  나오는지 측정하지 않았습니다. `o200k_base` 하나의 관찰로 tokenizer 일반을 말할 수 없습니다.
- **교란 요인이 통제되지 않았다.** 도메인, 문장 길이, 번역 방향, 문체가 chunk profile과
  token 수 양쪽에 동시에 영향을 줄 수 있습니다. 그 통제는 M2/M3의 일입니다.
- **분해는 항등식이지 인과가 아니다.** `ln(C_ko/C_en) + ln(density)`가 합쳐진다는 것은
  산술이 성립한다는 뜻이지, chunk 구조가 token 수를 **만들어냈다**는 뜻이 아닙니다.
- **morphology와의 관계는 측정하지 않았다.** D-03과 D-05는 같은 cohort의 서로 다른
  경로 측정이며, 이 문서는 둘 사이의 인과를 주장하지 않습니다.

그래서 허용되는 최대 강도의 서술은 다음과 같습니다:

> The Korean side formed fewer regex chunks but exhibited substantially greater
> final-token expansion per chunk.
>
> This is a descriptive tokenizer-mechanism measurement; its conditional explanatory
> contribution is evaluated later in M3.

---

## 12. NB09 M3에서 무엇을 검정하게 되는가

M3는 D-05의 chunk block이 **M2 이후에도 추가 설명력을 갖는가**를 묻습니다.

구조적으로:

- M2까지의 모형이 이미 통제한 변수들(표현 수준 feature, 길이, 도메인 등)을 넣은 뒤
- D-05의 mechanism block(`chunk_count`, `tokens_per_chunk`, chunk type 구성 등)을 추가했을 때
- 조건부로 설명력이 유의하게 증가하는지

증가한다면 "regex-chunk 구조는 다른 요인으로 환원되지 않는 정보를 담는다"고 말할 수
있습니다. 증가하지 않는다면 "관찰된 chunk 차이는 이미 통제된 요인들로 흡수된다"는
결론이 됩니다. **어느 쪽이든 M3 이전에 미리 말할 수 없습니다.**

M3가 끝나기 전까지 D-05의 지위는 `DESCRIPTIVE MECHANISM MEASUREMENT`이며,
`NOT CAUSAL`입니다.
