# Phase 2 QC — Open Decision Queue v1.1 (collapsed)

이전 버전(v1)의 Q0-Q8 9개 항목 중 대부분은 Director/Vice-Director의 2026-08-16 최소 QC 개정 지시로 **해소되었다** — 재판단이 필요한 것이 아니라 명시적으로 결정이 내려졌으므로, 여기 다시 나열하지 않는다:

- **Q0(accepted 게이팅 방식)** → RESOLVED: population rule-based, 500쌍은 calibration 전용. `docs/contracts/P2_NORMALIZE_QC_PRECONTRACT_v1.md` §3c/§7.
- **Q1-Q5, Q6(threshold류)** → RESOLVED as ENGINEERING_PARAMETER: review-only smoke flag의 threshold는 estimand-level 결정이 아니며 이 문서(precontract §3b/§5)가 직접 확정한다. Director 승인 대상에서 제외.
- **LID 방법 선택** → CLOSED: NO MODEL. Deterministic script-based review-only smoke check만 사용(§5). 재논의하지 않는다.
- **Q5(named_entity_heavy_flag 정의)** → DEFERRED, 게이팅 없음(§6). Director 결정 대상에서 제외, Phase 3/4 이후 별도 CR.

남는 항목은 진짜로 사람의 판단이 필요한 연구적 결정 1건과, 이 P2 설계 자체를 막지 않는 별도 문서 정리 1건뿐이다.

## R1 — Manual audit 로지스틱스 (유일하게 남는 실질적 미해결 사안)

**질문**: 500쌍 semantic-QC manual audit을
(a) 프로젝트 전체 1회 표본으로 배정할지, 아니면
(b) stratum(`domain × sentence_type × translation_direction × source_id × length_stratum`)별 최소 표본을 배정할지, 그리고
(c) 실제 채점자가 누구인지(Research Director 본인 또는 지정 rater).

**왜 아직 열려 있는가**: 이것은 사람의 의미 판단을 요구하는 SSOT §10.3 요구사항이며, 어떤 agent도 이 판단을 대신하거나 결과를 발명할 수 없다.

**필요 결정**: Research Director의 로지스틱스 지시(표본 배정 방식 + 채점자 지정).

## R2 — CR-003 (별도 문서 정리 사안, P2 QC 설계의 blocker 아님)

`research/g1-gate-claude@566f30b`의 CR-003(G1 게이트 §31/§37 번호 대응 명확화 제안)은 여전히 미승인 상태이나, 이번 지시(§8)에 따라 이는 **P2 QC 설계와 분리된 별도 문서 정리 사안**으로 취급한다 — P2 precontract v1.1의 실행 여부를 막지 않는다. Vice Director/Research Director가 별도 트랙에서 처리한다.

---

**이관 원칙(유지)**: R1/R2 어느 것도 이 세션에서 코드/설정 파일에 임의 기본값을 기록하지 않았다. Smoke-flag threshold 등 ENGINEERING_PARAMETER로 재분류된 항목은 precontract v1.1 본문에 직접 확정되어 있으며(Director 결정 대상 아님), 별도 대기 상태가 아니다.
