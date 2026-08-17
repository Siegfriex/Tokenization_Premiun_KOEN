# KO-EN Tokenization Premium — Vice Director Decision & Execution Coordination Log

> **Snapshot:** 2026-08-16 13:56 KST  
> **Document role:** Research Director 의사결정, Agent 실행기록, 분업·병렬작업, Git lineage, Gate 상태를 한 시점에서 추적하는 운영 로그  
> **Project:** Korean–English Tokenization Premium  
> **Authority SSOT:** `KOEN-TP-RS-001` — `Korean_English_Tokenization_Premium_Research_Spec_v1.0`  
> **Research status:** `FINAL DESIGN / PRE-ANALYSIS`  
> **Canonical project root:** `/home/sieg/projects-wsl/Tokenization_Premium`  
> **Canonical Python package:** `src/tokenization_premium/`  
> **Remote:** `Siegfriex/Tokenization_Premium`  
> **Vice Director status:** ACTIVE — evidence reconciliation / Gate adjudication / decision routing

---

## 0. 문서 목적과 권위

이 문서는 연구 SSOT 자체를 대체하지 않는다.

목적은 다음 네 계층을 분리하여 현재 연구의 실제 상태를 추적하는 것이다.

1. **Research Director Decision** — 사용자가 승인한 연구·운영 결정
2. **Agent Execution** — Claude, Codex, AIHub Recon, Raw EDA, Perplexity가 실제 수행한 범위
3. **Evidence State** — 제안, 실행, 검증, persisted artifact/hash를 구분
4. **Integration / Gate State** — 어떤 branch가 어디에서 합쳐지며 현재 어떤 Gate를 통과했는지 판정

SSOT와 코드 또는 Agent 제안이 충돌하면 SSOT가 우선한다. 단, Research Director가 승인한 구현 편차 또는 실행 유보는 별도 결정/CHANGELOG로 기록한다.

---

# 1. Executive Snapshot

## 1.1 현재 판정

| 항목 | 현재 상태 | Vice Director 판정 |
|---|---|---|
| G0 — Design Freeze | RQ/estimand/outcome/QC/analyzer/main-sensitivity + 추가 parameter bundle 고정 | **PASS** |
| Phase 0 — Environment/Repro | Codex branch에서 구현·fresh-kernel 실행·hash persistence 완료 | **BRANCH PASS** |
| Phase 0 — Canonical Integration | `integration/g0`에 Claude/Codex 최신 상태 미통합 | **PENDING** |
| G1 — Data Integrity | canonical D-01 Pair Registry 미구축 | **NOT ENTERED** |
| AIHub Raw Recon | 실제 raw profiling artifact/remote commit 관측 | **PRE-G1 EVIDENCE AVAILABLE** |
| Raw EDA notebooks | Research Director가 신규 auxiliary track 승인 | **AUTHORIZED / NOT YET OBSERVED REMOTELY** |
| Perplexity AIHub evidence | 공식 AIHub source audit remote artifact 관측 | **WEB EVIDENCE AVAILABLE** |
| Track B / RQ7 | 현 릴리스 본선에서 실행 유보 | **DEFERRED_NOT_EXECUTED** |
| Track B future baseline | 재개 시 Hugging Face hosted API | **DIRECTOR DECISION** |
| Track A / RQ1–RQ6 | 영향 없음 | **ACTIVE SCOPE** |

## 1.2 지금의 실질 목표

```text
Claude G0 final contract
        +
Codex Phase-0 engineering
        ↓
integration/g0
        ↓
cross-agent contract validation
        ↓
canonical root fresh-kernel 00 Run All
        ↓
canonical artifact/hash regeneration
        ↓
main
```

데이터 source 선정은 별도 병렬 evidence lane에서 진행한다.

```text
AIHub Recon
    +
Raw EDA Notebooks
    +
Perplexity Web Evidence
        ↓
Vice Director reconciliation
        ↓
Research Director source/cohort decision
        ↓
01_build_pair_registry
        ↓
G1 Data Integrity
```

---

# 2. Current Git / Branch Snapshot

아래 SHA는 **2026-08-16 13:56 KST 전후 Vice Director가 GitHub remote에서 직접 재확인한 값**이다.

| Branch | Remote HEAD | 역할 | 현재 판정 |
|---|---|---|---|
| `main` | `5bf770eacbdd341d9539bd392614657f6cf0777a` | integration/release | bootstrap PR #1 merge 상태 |
| `integration/g0` | `b37f73326e3b1de12232853952b10134062bdf27` | G0 integration | Claude/Codex 최신 commit 아직 미통합 |
| `impl/g0-codex` | `6a81a51c348f3671493bf87b2051c1a9cdcaa52f` | Engineering / Reproducibility | Phase-0 execution artifacts persisted |
| `research/g0-claude` | `51147e31f42cdcd4748bcbb31609f46b27243cc6` | Research contract / methodology | G0 parameter bundle + Track B defer 반영 완료 |
| `data/g0-aihub-recon` | `15b9129e7dd2ab2ba7afeaa37ed890b15ff8f5a9` | Local raw reconnaissance | profiling + Git evidence persisted |
| `evidence/g0-perplexity` | `c5b704f4b534f4a5d4da5d3c3af78516f6814f6b` | Official web evidence | AIHub source audit persisted |
| `eda/g0-raw-notebooks` | **remote branch 미관측** | Dataset-by-dataset raw EDA | directive only / execution pending |

### 2.1 Snapshot timing rule

각 Agent 보고는 동일 시점이 아니다.

따라서 앞으로도:

- 보고서에 적힌 SHA
- 현재 remote branch SHA
- 해당 artifact가 생성된 시점의 base SHA

를 별도로 관리한다.

이 문서의 원칙:

```text
Agent report ≠ automatically current repository state
```

항상 timestamp + branch + HEAD + base를 함께 본다.

---

# 3. Research Director Decision Register

## CR-001 — Canonical Python Namespace

**Status:** APPROVED

| 항목 | 결정 |
|---|---|
| SSOT IA 표기 | `src/koen_tp/` |
| 실제 canonical codebase | `src/tokenization_premium/` |
| Director decision | 기존 실제 codebase 유지 |
| 금지 | `koen_tp` rename, dual package, alias package |
| 연구 영향 | RQ/estimand/data schema에는 영향 없음 |
| 분류 | approved implementation deviation |

---

## D-RD-01 — G0 Parameter Bundle

**Status:** APPROVED / Claude commit에 반영됨

| Parameter | Freeze |
|---|---:|
| exact decomposition epsilon | `1e-10` |
| bootstrap resamples | `5,000` |
| BH-FDR alpha | `0.05` |
| length strata | EN codepoint 기준 quintile |
| manual semantic QC audit | `N=500` |
| predictive holdout | `20%` |
| high digit ratio soft flag | `> 0.20` |
| high punctuation ratio soft flag | `> 0.20` |
| source effect primary | fixed effects |
| random-intercept | alternative/sensitivity only |
| VIF warning | `>=5` |
| VIF severe warning | `>=10` |
| VIF 자동삭제 | 금지 |
| quantile reference | `.50` |
| quantile primary upper tail | `.90` |
| quantile sensitivity | `.95` |
| master seed | `20260816` |
| split seed | `1456095166` |
| bootstrap seed | `4263151703` |
| model tuning seed | `3618347261` |
| serving seed | `2218276919` |
| auxiliary seed | `2995913794` |

Random-intercept candidate 조건:

- `n_source >= 10`
- source/domain 구조 식별 가능
- optimizer convergence
- singular/boundary fit 아님

### 계속 OPEN

- `AMB-05` — final analysis cohort N
- `AMB-12` — actual corpus ↔ source Tier A/B/C mapping

두 항목은 AIHub Recon + Raw EDA + Perplexity reconciliation 이전에 확정하지 않는다.

---

## D-RD-02 — Merge Policy

**Status:** APPROVED

현재 G0에 대해:

```text
agent-owned branch
    ↓
remote staging commit
    ↓
integration/g0
    ↓
cross-agent validation
    ↓
canonical root rerun
    ↓
main
```

Agent는 `main`에 직접 merge하지 않는다.

금지:

- 동일 working tree에서 병렬 agent 동시 수정
- `git add .`
- `git add -A`
- `git commit -am`
- 다른 agent-owned path stage
- 다른 agent worktree 변경
- project artifact를 canonical root 밖에 생성

---

## D-RD-03 / CR-002 — Track B Execution Deferral

**Status:** APPROVED / Claude commit에 반영됨

```text
RQ7 / Track B
= DEFERRED_NOT_EXECUTED
```

의미:

- RQ7 삭제 아님
- SSOT 삭제/수정 아님
- 현재 Track A 진행을 차단하지 않음
- 현재 `12_gpt_oss_serving.ipynb` 실행 금지
- 현재 gpt-oss local serving 금지
- 현재 HF API 호출 금지
- 현재 serving benchmark 금지

향후 Track B를 재개할 경우:

```text
deployment baseline = Hugging Face hosted API
```

재개 시점에 다시 freeze할 것:

- exact HF endpoint/provider
- model ID / revision
- API semantics
- Harmony behavior
- reasoning telemetry
- request/final token accounting
- TTFT/stream observability
- pricing
- rate limit
- seed/determinism support

현재 시점의 provider 세부값을 미래 contract로 선제 고정하지 않는다.

---

## D-RD-04 — Raw Dataset EDA Notebook Track

**Status:** AUTHORIZED / execution pending

목적:

현재 소싱된 각 logical raw dataset별로 **독립 exploratory IPYNB**를 생성하여 데이터 구조·분포·결측·범주·길이·이상치·노이즈·시각적 특성을 파악한다.

원칙:

- One logical dataset = one EDA notebook
- canonical `00`–`13` notebook과 분리
- raw file immutable
- token premium / morphology / inference 금지
- 사용 가능한 EDA/IPYNB skill을 Agent가 우선 활용
- visualization-centric exploratory artifact
- G1 PASS evidence로 승격 금지

예정 branch:

`eda/g0-raw-notebooks`

예정 notebook root:

`notebooks/exploratory/raw/`

**2026-08-16 13:56 KST remote에서 해당 branch는 아직 관측되지 않음.**

---

# 4. Agent Responsibility Matrix

## 4.1 Claude Orchestrator

**Authority domain**

- research logic
- RQ / estimand
- source/data contract
- pair QC
- normalization semantics
- morphology definition
- statistical model
- sensitivity / inference
- interpretation boundary

**Branch**

`research/g0-claude`

**Write ownership**

- `configs/research_v1.yaml`
- `configs/normalization_v1.yaml`
- `configs/morphology_v1.yaml`
- `docs/contracts/**`
- `docs/research/**`
- research decision/change logs

**Not owned**

- `src/**`
- `tests/**`
- `pyproject.toml`
- `uv.lock`
- `00_environment_repro.ipynb`
- tokenizer/serving engineering config
- raw data

**Current execution**

Latest remote HEAD:

`51147e31f42cdcd4748bcbb31609f46b27243cc6`

Observed commit purpose:

- D-RD-01 parameter bundle freeze
- AMB-01/02/03/04/06/07/08/09/10/11 resolution
- full seed policy
- D-RD-03 / CR-002 Track B deferral
- `RQ7.status = DEFERRED_NOT_EXECUTED`
- `docs/CHANGELOG.md` creation
- AMB-05, AMB-12 remain OPEN

**Evidence level**

`LEVEL 4 — artifact persisted + Git commit`

단, 이는 **research-contract artifact evidence**이며 statistical evidence가 아니다.

---

## 4.2 Codex Orchestrator

**Authority domain**

- Git / environment
- reproducibility
- package / schema enforcement
- library implementation
- automated tests
- Unicode/tokenizer implementation
- exact decomposition test infrastructure
- artifact manifests / hashes
- serving implementation when activated

**Branch**

`impl/g0-codex`

**Worktree**

`.agent_worktrees/codex`

**Current execution**

Latest remote HEAD:

`6a81a51c348f3671493bf87b2051c1a9cdcaa52f`

Phase-0 report에서 확인된 사항:

- safe Git bootstrap
- `00_environment_repro.ipynb`
- tiktoken `0.13.0`
- kiwipiepy `0.23.2`
- raw o200k artifact SHA
- mergeable-ranks / pat_str / special-token hashes
- roundtrip 100%
- JSON/Parquet roundtrip
- Korean font PNG/SVG smoke
- environment/package manifests
- `pytest 8 passed`
- ruff PASS
- mypy PASS
- fresh-kernel code cells `12/12`
- execution artifacts committed and pushed

**Evidence level**

`LEVEL 4 — executed + validated + artifact persisted/hash`

**Current outstanding**

Research Director의 Track B 유보 결정 이후 Codex branch의 추가 remote commit은 이 snapshot에서 아직 관측되지 않았다.

따라서:

- `configs/serving_v1.yaml`의 deferred machine-readable 반영
- Claude 최신 research config와의 cross-contract validation

은 **Codex 다음 보고에서 재확인 필요**.

---

## 4.3 AIHub Raw Recon Agent

**Authority domain**

- local raw file reality
- inventory/hash
- schema
- pairability
- missingness
- duplicate/overlap
- raw length/noise
- source/domain metadata
- deterministic ingest feasibility

**Branch**

`data/g0-aihub-recon`

**Latest remote HEAD**

`15b9129e7dd2ab2ba7afeaa37ed890b15ff8f5a9`

**Observed persisted artifacts**

- `outputs/manifests/data_recon/**`
- `outputs/reports/data_recon/**`
- raw profile
- duplicate overlap profile
- artifact SHA manifest
- Git push evidence

**Raw root actually audited**

`/home/sieg/projects-wsl/Tokenization_Premium/data/raw/aigub`

주의: 초기 지시의 `data/raw/aihub`가 아니라 실제 사용자가 둔 경로 `data/raw/aigub`가 존재하여 그 경로를 감사함.

### 현재 직접 관측된 raw snapshot

- physical files: `23`
- bytes: `8,474,355,522`
- all 23 files stable during audit
- partial/download-in-progress: `0`
- raw manifest SHA:
  `9a546bc91225e5331d0e8e48a1e06685cb5304ed7098aff5cbf40c74022c1f0c`

### Unique-content record count

| Local corpus | Unique-content records |
|---|---:|
| 025 일상생활 및 구어체 | `2,700,345` |
| 026 기술과학 | `1,350,162` |
| Legacy 한국어-영어 번역(병렬) | `1,602,418` |
| **Total** | **`5,652,925`** |

따라서 이전 별도 capacity report의 “약 8.1M rows”는 현재 canonical raw-recon 집계와 동일한 숫자로 사용하면 안 된다.

```text
5,652,925 unique-content raw records
≠ accepted analysis pairs
≠ final analysis cohort
```

### Pairability observation

- JSON 025/026: same object에 `ko`/`en` 공존 → direct pair candidate
- JSON `sn`: file-local unique candidate
- Legacy XLSX: 같은 row에 `원문`/`번역문`
- 대화체: 단일 stable ID 부재 → physical row fallback 필요
- cross-workbook ID namespace collision 존재

### Duplicate/overlap warning

Recon report는 특히 025에서 상당한 raw pair duplicate 및 train/validation overlap candidate를 관측했다.

이는 G1에서 반드시 별도 dedup/lineage rule을 필요로 한다.

**Evidence level**

`LEVEL 4 — raw reconnaissance artifact persisted + hashes`

그러나:

- G1 PASS 아님
- D-01 registry 아님
- final QC acceptance 아님

---

## 4.4 Raw EDA Notebook Agent

**Authority domain**

raw distribution의 exploratory visual understanding

**Status**

`AUTHORIZED / NOT YET OBSERVED REMOTELY`

**Planned branch**

`eda/g0-raw-notebooks`

**Expected outputs**

- dataset-specific EDA `.ipynb`
- `outputs/eda_raw/**`
- `outputs/figures/eda_raw/**`
- EDA-specific manifest/report

**Boundary**

다음은 금지:

- o200k TP
- logTP
- compression penalty inference
- morphology explanation
- signed-rank/bootstrap inference
- M0–M3
- G1 accepted cohort 생성

**Evidence level**

현재 `LEVEL 0 — directive / proposal`.

---

## 4.5 Perplexity Research Aide

**Authority domain**

- AIHub official dataset identification
- official schema/provenance
- license/acquisition
- translation process
- source/domain documentation
- external evidence audit

**Branch**

`evidence/g0-perplexity`

**Latest remote HEAD**

`c5b704f4b534f4a5d4da5d3c3af78516f6814f6b`

**Persisted evidence document**

`docs/evidence/aihub/AIHUB_KOEN_SOURCE_EVIDENCE_2026-08-16.md`

### Official candidate mapping observed

| Internal evidence ID | Official candidate |
|---|---|
| D71265 | 일상생활 및 구어체 한-영 번역 병렬 말뭉치 데이터 |
| D71266 | 기술과학 분야 한-영 번역 병렬 말뭉치 데이터 |
| D87 | 한국어-영어 번역(병렬) 말뭉치 |
| D71693 | 국제 학술대회용 전문분야 한영/영한 통번역 데이터 |

Perplexity artifact는 web-only임을 명시하고 local schema claim으로 확대하지 않았다.

Current provisional web score:

- D71265: `77/100`
- D71266: `78/100`
- D87 / D71693: hard-gate unresolved로 final score 보류

**Evidence level**

`LEVEL 4 — external evidence document persisted in Git`

단, 사실 수준은 각 항목별 `WEB_CONFIRMED / LOCAL_INSPECTION_REQUIRED` 경계를 유지한다.

---

# 5. Parallel Work Design

## 5.1 두 핵심 Orchestrator의 관계

Claude와 Codex는 동일 작업을 반씩 나누는 구조가 아니다.

```text
                      Research Director
                            │
                       Vice Director
                            │
             ┌──────────────┴──────────────┐
             │                             │
           Claude                         Codex
   Research / Method Contract    Engineering / Reproducibility
             │                             │
 RQ / estimand / QC                 environment / Git
 source contract                    schemas / tests
 normalization semantics            tokenizer implementation
 morphology semantics               hashes / manifests
 statistical decisions              notebook execution
 interpretation                     reproducibility
             │                             │
             └──────────────┬──────────────┘
                            │
                      integration/g0
                            │
                  contract compatibility
                            │
                  canonical fresh Run All
                            │
                           main
```

Claude가 연구 의미를 정의하고, Codex가 그 의미를 실행 가능한 contract/test/artifact로 보장한다.

---

## 5.2 Data Evidence Lane

```text
AIHub Raw Recon
       │
       ├── raw schema / pairability / duplicates
       │
Raw EDA Notebook Agent
       │
       ├── visual distribution / metadata / anomaly
       │
Perplexity
       │
       └── official provenance / license / dataset ID
               │
               ↓
        Vice Director Reconciliation
               │
               ↓
        Research Director Decision
        AMB-05 / AMB-12
               │
               ↓
          Claude Data Contract
               │
               ↓
         Codex Schema Review
               │
               ↓
      01_build_pair_registry
```

세 데이터 에이전트의 출력은 서로 대체하지 않는다.

| Agent | 대답하는 질문 |
|---|---|
| Recon | “로컬에 실제로 무엇이 있는가?” |
| Raw EDA | “그 raw distribution은 실제로 어떻게 생겼는가?” |
| Perplexity | “공식 문서는 이 데이터가 무엇이라고 말하는가?” |

---

# 6. Integration Policy

## 6.1 G0 integration 대상

현재 G0/Phase-0 canonical integration의 핵심 대상은:

1. `impl/g0-codex`
2. `research/g0-claude`

이다.

Data Recon / Raw EDA / Perplexity artifact는 source decision evidence이며, **G0 engineering/research contract와 동일하게 무조건 merge하지 않는다.**

Vice Director가 artifact quality와 source relevance를 검토한 뒤 integration 시점을 결정한다.

---

## 6.2 Current recommended merge sequence

현재 권고:

```text
[1]
Codex가 D-RD-03 Track-B defer를 engineering config에 반영
+ latest remote push

[2]
Claude latest = 51147e3... 유지/검증

[3]
impl/g0-codex
→ integration/g0

[4]
research/g0-claude
→ integration/g0

[5]
Cross-agent validation
- config parse
- namespace
- tokenizer/analyzer
- G0 params
- seed policy
- Track B deferred status
- path containment
- no ownership contamination

[6]
canonical root에서
00_environment_repro.ipynb
fresh-kernel Run All

[7]
canonical artifacts/hash regeneration

[8]
Vice Director Phase-0 final adjudication

[9]
integration/g0 → main
```

---

# 7. Gate & Evidence Matrix

| Area | Artifact / Evidence | Level | Status |
|---|---|---:|---|
| SSOT | KOEN-TP-RS-001 | Authority | FINAL DESIGN |
| G0 research contract | Claude configs/docs | 4 | PASS |
| G0 parameter bundle | Claude `51147e3...` | 4 | PASS |
| Phase-0 code | Codex branch | 4 | PASS ON BRANCH |
| Phase-0 canonical rerun | canonical root | — | PENDING |
| AIHub local raw reality | Recon artifacts | 4 | AVAILABLE |
| AIHub official web evidence | Perplexity doc | 4 | AVAILABLE |
| Raw visual EDA | planned notebooks | 0 | PENDING |
| D-01 pair registry | none | 0 | NOT STARTED |
| G1 | none | — | NOT ENTERED |
| RQ1–RQ6 statistical evidence | none | — | NOT STARTED |
| Track B serving | deferred | — | DEFERRED |

### Evidence hierarchy

```text
LEVEL 0 — Proposal
LEVEL 1 — Code exists
LEVEL 2 — Code executed
LEVEL 3 — Validation passed
LEVEL 4 — Artifact persisted + hash
LEVEL 5 — Statistical / robustness evidence
LEVEL 6 — Release evidence
```

주의:

`LEVEL 4`는 해당 artifact의 persistence/reproducibility를 뜻한다.  
그 artifact의 연구 주장이 자동으로 `LEVEL 5`가 되는 것은 아니다.

---

# 8. Current Open Issues

## O-01 — Canonical Phase-0 Integration

**Status:** OPEN

Codex/Claude 최신 remote branch는 존재하지만 `integration/g0`에는 아직 들어오지 않았다.

필요:

- Codex latest directive 반영
- merge
- canonical root rerun
- artifact hash regeneration

---

## O-02 — AMB-05 Final Analysis N

**Status:** DEFER

현재 raw record 규모만 보고 final N을 결정하지 않는다.

판단 순서:

```text
raw records
→ deterministic candidate pairs
→ duplicate/overlap handling
→ QC-eligible pairs
→ source/domain/direction composition
→ capacity benchmark
→ final cohort strategy
```

---

## O-03 — AMB-12 Corpus → Tier Mapping

**Status:** DEFER

현재 evidence:

- local raw recon 존재
- Perplexity official evidence 존재
- Raw EDA 미실행

세 evidence를 reconcile한 뒤 Tier를 결정한다.

AIHub라는 이유만으로 자동 Tier A를 부여하지 않는다.

---

## O-04 — 025 Duplicate / Train-Validation Overlap

**Status:** NEW DATA-INTEGRITY ISSUE

AIHub Recon에서 025 corpus에 상당한 pair-hash duplicate 및 train/validation overlap candidate가 관측되었다.

이는 아직 hard exclusion 결과가 아니다.

G1 설계에서 최소한 다음을 분리해야 한다.

- exact duplicate
- repeated translation
- same text pair across train/valid
- source-level intentional repetition
- hash-collision-safe canonical duplicate key

Claude: QC semantics  
Codex: deterministic duplicate implementation/test  
Vice Director: exclusion vs flag vs provenance-only 처리 adjudication

---

## O-05 — Legacy XLSX Global ID Collision

**Status:** NEW DATA-INTEGRITY ISSUE

workbook 간 동일 `ID/SID` 값이 반복될 수 있으므로 raw ID를 전역 pair ID로 사용할 수 없다.

D-01에서 source-qualified stable pair key가 필요하다.

---

## O-06 — Raw EDA Track Startup

**Status:** PENDING

`eda/g0-raw-notebooks` remote branch가 아직 관측되지 않았다.

이 track이 시작되면 dataset별 EDA notebook 생성 및 push evidence를 별도로 추적한다.

---

## O-07 — Track B

**Status:** CLOSED FOR CURRENT PHASE

추가 의사결정 없음.

`DEFERRED_NOT_EXECUTED`.

재개 시 HF hosted API 기준으로 별도 Gate를 연다.

---

# 9. Decision / Action Ownership

| 현안 | Claude | Codex | Recon | Raw EDA | Perplexity | Vice Director | Research Director |
|---|---|---|---|---|---|---|---|
| G0 parameters | contract | consume/test | — | — | — | reconcile | **APPROVED** |
| Track B defer | research log | machine status | — | — | future evidence only | enforce | **APPROVED** |
| Phase-0 canonical PASS | review | execute | — | — | — | adjudicate | final acceptance |
| source identity | contract mapping | ingest schema later | local facts | distribution | official evidence | reconcile | decide if contested |
| duplicate policy | define semantic rule | implement/test | detect | visualize | — | adjudicate | if major design change |
| final N | model/QC implication | capacity evidence | eligible counts | distributions | corpus scope | recommend | **OPEN** |
| Tier assignment | methodology | schema support | local provenance | support | official provenance | recommend | **OPEN** |
| D-01 registry | design/narrative | schema/repro review | evidence input | evidence input | evidence input | Gate review | approve major deviations |

---

# 10. Immediate Next Sequence

```text
NOW
│
├─ Claude: current G0 decision commit already observed (51147e3...)
│
├─ Codex: Track-B deferred engineering state 반영 후 latest report
│
├─ AIHub Recon: artifact exists — Vice Director detailed reconciliation 대상
│
├─ Perplexity: artifact exists — local↔web reconciliation 대상
│
└─ Raw EDA: branch/worktree 생성 및 dataset별 EDA 시작
```

이후:

```text
G0 Engineering/Research Integration
        ↓
Canonical 00 PASS
        ↓
main
        ↓
Data evidence reconciliation
        ↓
AMB-05 / AMB-12 Director decision
        ↓
01_build_pair_registry
        ↓
G1 Data Integrity
```

---

# 11. Research Claim Boundary at This Snapshot

현재 허용되는 말:

- Phase-0 environment/repro branch는 실행·검증·persist되었다.
- AIHub local raw에는 deterministic KO/EN candidate pair 구조가 존재하는 corpus들이 관측되었다.
- 025에는 duplicate/overlap 위험이 실질적으로 존재한다.
- 공식 AIHub 문서상 D71265/D71266 등이 현재 local corpus와 대응할 강한 후보로 확인되고 있다.
- Track B는 Research Director 결정으로 유보되었다.

현재 금지되는 말:

- “5.65M pair가 최종 연구표본이다.”
- “AIHub corpus는 모두 Tier A다.”
- “025 중복은 전부 오류이므로 삭제한다.”
- “현재 raw corpus에서 Tokenization Premium이 확인됐다.”
- “형태소가 Tokenization Premium의 원인이다.”
- “Track B를 수행하지 않아도 아무 limitation이 없다.”

---

# 12. Vice Director Current Judgment

현재 프로젝트는 **설계 부재 단계가 아니다.**

G0 연구계약은 이미 사실상 닫혔고 Phase-0 engineering도 branch 수준에서 PASS evidence가 존재한다.

지금의 핵심은 더 많은 코드를 동시에 만드는 것이 아니라:

```text
1. Claude/Codex 최신 contract를 canonical integration
2. 00_environment_repro canonical PASS
3. AIHub local/web/EDA evidence reconciliation
4. duplicate / ID / source-tier / final-N decision
5. 그 뒤 01_build_pair_registry 시작
```

의 순서를 지키는 것이다.

특히 데이터가 대규모로 확보되었다는 사실은 G1을 생략할 이유가 아니라, 오히려 **pair lineage와 duplicate policy를 더 엄격하게 고정해야 할 이유**다.

---

# 13. Traceability References

## SSOT

- `ssot/Korean_English_Tokenization_Premium_Research_Spec_v1.0-2.pdf`
- Document ID: `KOEN-TP-RS-001`

## Current remote evidence heads

- `main@5bf770eacbdd341d9539bd392614657f6cf0777a`
- `integration/g0@b37f73326e3b1de12232853952b10134062bdf27`
- `impl/g0-codex@6a81a51c348f3671493bf87b2051c1a9cdcaa52f`
- `research/g0-claude@51147e31f42cdcd4748bcbb31609f46b27243cc6`
- `data/g0-aihub-recon@15b9129e7dd2ab2ba7afeaa37ed890b15ff8f5a9`
- `evidence/g0-perplexity@c5b704f4b534f4a5d4da5d3c3af78516f6814f6b`

## Current key persisted artifacts

- Claude: `configs/research_v1.yaml`
- Claude: `configs/normalization_v1.yaml`
- Claude: `configs/morphology_v1.yaml`
- Claude: `docs/contracts/RESEARCH_CONTRACT_v1.md`
- Claude: `docs/CHANGELOG.md`
- Codex: `notebooks/00_environment_repro.ipynb`
- Codex: `outputs/manifests/ENVIRONMENT_*`
- Codex: `outputs/manifests/TOKENIZER_O200K_BASE_ARTIFACT_v001.json`
- Recon: `outputs/reports/data_recon/AIHUB_RAW_RECON_20260816T132650+0900.md`
- Recon: `outputs/manifests/data_recon/**`
- Perplexity: `docs/evidence/aihub/AIHUB_KOEN_SOURCE_EVIDENCE_2026-08-16.md`

---

# 14. Update Policy

본 문서는 point-in-time snapshot이다.

다음 중 하나가 발생하면 새 시점 문서를 생성하거나 본 문서 후속 revision을 만든다.

- Gate 판정 변화
- Research Director 결정 추가
- canonical integration 완료
- source/Tier/final-N 결정
- 01 notebook 착수
- major data-quality issue 발견
- Track B 재활성화
- SSOT CHANGE_REQUEST 승인

과거 snapshot의 사실을 현재 상태로 덮어쓰지 않는다.

---

**Snapshot closed:** `2026-08-16 13:56 KST`  
**Prepared by:** Vice Director / Senior Research Architect  
**Authority:** Research Director final decision
