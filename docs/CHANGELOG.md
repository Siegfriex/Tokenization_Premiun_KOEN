# Decision / Change Log

SSOT(KOEN-TP-RS-001 v1.0) Appendix A 결정 로그 형식을 계승한다. 본문을 덮어쓰지 않고 여기에 사유·영향을 기록한다.

## Research Director Decisions — 2026-08-16

**D-RD-01 — G0 parameter bundle = APPROVED**
`docs/research/AMBIGUITIES_g0.md`의 AMB-01, 02, 03, 04, 06, 07, 08, 09, 10, 11을 아래 값으로 확정하고 `configs/research_v1.yaml`에 반영함:
- exact decomposition epsilon(G2) = 1e-10
- bootstrap resamples = 5,000
- BH-FDR alpha = 0.05
- length_stratum = EN codepoint count 기준 quintile
- manual semantic QC audit N = 500 pairs
- predictive holdout = 20%
- high_digit_ratio_flag / high_punctuation_ratio_flag threshold = > 0.20 (둘 다)
- source specification: primary = fixed effects; random-intercept = alternative/sensitivity only (조건: n_source≥10 + 식별가능 구조 + optimizer convergence + non-singular fit)
- VIF: warning≥5, severe warning≥10, VIF 단독 기준 자동 feature 삭제는 계속 금지
- quantile regression: reference=0.50, primary upper-tail=0.90, sensitivity=0.95
- seed freeze: master=20260816, split=1456095166, bootstrap=4263151703, model_tuning=3618347261, serving=2218276919, auxiliary=2995913794

AMB-05(최종 분석 N)와 AMB-12(source tier↔corpus 매핑)는 AIHub reconnaissance 공식 보고 전까지 OPEN 유지.

**D-RD-02 — Merge policy = APPROVED**
`agent branch → integration/g0 → cross-agent validation → canonical-root rerun → main`. 각 agent worktree(`research/g0-claude`, `impl/g0-codex`, `data/g0-aihub-recon`, `evidence/g0-perplexity`)는 `integration/g0`로 병합되고, cross-agent contract audit(config key 충돌/research-vs-implementation 불일치/seed 동일성/tokenizer 동일성/Track B 우발 실행 경로/패키지 네임스페이스 유지 여부)을 통과한 뒤 canonical root에서 `00_environment_repro.ipynb` fresh-kernel Run All로 재검증하고 `main`으로 승격한다.

**D-RD-03 — Track B = DEFERRED**
Track B(RQ7, `12_gpt_oss_serving.ipynb`) 실행을 연기한다. **삭제가 아니다** — 상태는 `DEFERRED_NOT_EXECUTED`. 현재 phase에서 gpt-oss model download, local serving, HF API 호출, serving benchmark, notebook 12 실행을 모두 금지한다. 재개 시 배포 baseline은 Hugging Face hosted API를 전제로 하되, 실제 재개 시점에 provider/model ID/revision/API semantics/reasoning telemetry/request-final token accounting/latency observability/cost를 다시 evidence-grounded로 freeze한다 — 지금 세부값을 추측해 넣지 않는다.

## CR-002 — TRACK_B_EXECUTION_DEFERRED

- **Evidence**: 로컬 개발 박스는 RTX 5070(~12GB VRAM) + 16GB RAM — gpt-oss-20b(native MXFP4 최소 ~16GB) 및 gpt-oss-120b(단일GPU 클래스 최소 ~80GB) 둘 다 이 하드웨어로 서빙 불가 (구조적 한계, "더 기다리면 되는" 문제 아님). SSOT §31 게이트 텍스트 확인 결과 어떤 G0-G6 게이트의 PASS 조건도 Track B 완료를 요구하지 않음.
- **Research impact**: Track A(RQ1-RQ6, notebooks 00-11, tiktoken+Kiwi 기반 전량 CPU-bound)는 이 제약의 영향을 받지 않음. RQ7은 SSOT에서 제거하지 않으며, 상태만 `DEFERRED_NOT_EXECUTED`로 기록.
- **Alternative considered**: (A) hosted inference API 경유 실행 — pyproject에 openai/anthropic SDK가 이미 있어 이 경로를 염두에 둔 것으로 보임; (B) gpt-oss-20b만 로컬로, 표본을 §9.1 하한(~1,000쌍)까지 축소, B1(request-only)만 우선 — 20b도 VRAM 여유가 사실상 없어 CPU offload 필요, decode throughput이 B2/B3에 부적합; (C) 전체 연기, exploratory로 한정 — **채택됨**.
- **Decision**: Track B는 현재 Track A/G1-G5 진행을 차단하지 않는다. 향후 실행 시 Hugging Face hosted API를 기본 deployment 경로로 한다.
- **Impact**: notebook 12 실행 연기 / T07·F09 serving artifact 연기 / Track A RQ1-RQ6 영향 없음 / RQ7 삭제 아님.

## Carried forward from SSOT Appendix A

D-01 ~ D-07은 SSOT 본문(§ 각 항목 참조)에 이미 기록되어 있으며 여기서 재기록하지 않는다. CR-001(패키지 네임스페이스 `src/tokenization_premium/` 확정)은 재논의하지 않는다.
