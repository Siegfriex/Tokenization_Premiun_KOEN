# G0 Ambiguities & Decisions Required — SSOT v1.0

SSOT(KOEN-TP-RS-001 v1.0)를 `docs/contracts/RESEARCH_CONTRACT_v1.md`로 옮기는 과정에서, 스펙이 **원칙은 명시하지만 정확한 숫자/파라미터는 지정하지 않았던** 항목들. D-RD-01(2026-08-16)로 아래 대부분이 RESOLVED되어 `configs/research_v1.yaml`에 반영되었다. AMB-05/AMB-12는 여전히 OPEN.

| ID | 항목 | SSOT 근거 | 상태 | 값 |
|---|---|---|---|---|
| AMB-01 | G2 exact-decomposition identity 허용오차 ε | §31 G2 | **RESOLVED (D-RD-01)** | 1e-10 |
| AMB-02 | Bootstrap resample 횟수(B) | §17.2 | **RESOLVED (D-RD-01)** | 5,000 |
| AMB-03 | FDR alpha 수준 | §24, §29 | **RESOLVED (D-RD-01)** | 0.05 |
| AMB-04 | length_stratum 분위수 개수/기준 | §9.2 | **RESOLVED (D-RD-01)** | EN codepoint count 기준 quintile |
| AMB-05 | 표본 규모 목표치 (실제 목표 N) | §9.1 | **OPEN** | data-recon(AIHub) 공식 보고 전까지 미확정 — local raw-record 관측치(~8.1M)를 valid pair로 간주하지 않음 |
| AMB-06 | 수동 semantic QC audit 표본 수 | §9.1, §10.3 | **RESOLVED (D-RD-01)** | 500 pairs |
| AMB-07 | Hold-out 비율 | §23.2 | **RESOLVED (D-RD-01)** | 20% |
| AMB-08 | high_digit_ratio_flag / high_punctuation_ratio_flag 임계값 | §10.2 | **RESOLVED (D-RD-01)** | 둘 다 > 0.20 |
| AMB-09 | Random vs Fixed effects 판단 기준 | §20.1 | **RESOLVED (D-RD-01)** | primary = fixed effects; random-intercept은 alternative/sensitivity로만, 조건: n_source≥10 + 식별가능 + convergence + non-singular |
| AMB-10 | VIF/GVIF 임계값 | §20.2, §21 | **RESOLVED (D-RD-01)** | warning≥5, severe≥10, VIF 단독 자동 삭제는 여전히 금지 |
| AMB-11 | Quantile regression 분석 분위수 | §22 | **RESOLVED (D-RD-01)** | reference=0.50, primary upper-tail=0.90, sensitivity=0.95 |
| AMB-12 | Source tier ↔ 실제 corpus 매핑 | §9.3 | **OPEN** | AIHub 등 raw 데이터가 canonical ingest 공식 보고 전까지 의도적으로 미확정 |
| AMB-13 | `src/koen_tp/visualization.py` 소재 | Notebook Constitution vs SSOT §36 IA | **RESOLVED_NON_BLOCKING_IMPLEMENTATION_EXTENSION** (2026-08-16, read-only 확인) | `origin/impl/g0-codex`의 `src/tokenization_premium/visualization.py`를 읽기전용 확인함: 한글 font 탐색(`find_korean_font`, Noto Sans CJK KR→Noto Sans KR→NanumGothic 우선순위) + PNG/SVG rendering smoke test — Notebook Constitution §7(한글 시각화 계약)의 engineering support 구현일 뿐 RQ/estimand/연구범위 변경 없음. SSOT §36의 11개 모듈 목록을 "추가 모듈 금지 목록"으로 해석하지 않음. CHANGE_REQUEST 불필요. |
| AMB-14 | 패키지 네임스페이스 | CR-001 | **CLOSED** | `src/tokenization_premium/` — 재논의하지 않음 |

**Seed freeze (D-RD-01, §30.3 대응)**: master_seed=20260816, split=1456095166, bootstrap=4263151703, model_tuning=3618347261, serving=2218276919, auxiliary=2995913794. `configs/research_v1.yaml`의 `seed_policy` 참조.

**Track B (D-RD-03 / CR-002)**: RQ7/Track B는 `DEFERRED_NOT_EXECUTED`. 상세는 `docs/CHANGELOG.md`의 CR-002 및 `configs/research_v1.yaml`의 `track_b_status` 참조. `[[project-hardware-track-b-constraint]]` 메모리(RTX 5070 12GB VRAM으로는 gpt-oss-20b/120b 로컬 서빙 불가)가 이 결정의 배경 증거 중 하나다.

AMB-05, AMB-12는 data-recon 트랙의 공식 보고 전까지 계속 OPEN으로 유지한다.
