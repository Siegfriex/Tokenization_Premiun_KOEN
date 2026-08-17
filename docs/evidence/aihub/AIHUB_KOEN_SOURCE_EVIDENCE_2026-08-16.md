# AI Hub KO-EN Source Evidence Audit — G1 Port

- Port date: 2026-08-16 KST
- Base: `main@f1b2a901b3bc9a9d759af0698bd0c308ec6e468b`
- Prior evidence source: `evidence/g0-perplexity@c5b704f4b534f4a5d4da5d3c3af78516f6814f6b`
- Scope: official AI Hub dataset pages and use-policy materials.
- Boundary: `WEB/OFFICIAL` is not local archive inspection. Local findings are used only when Git-persisted with exact branch/SHA.

## Candidate baseline

| Candidate | Official identity | WEB/OFFICIAL evidence | Baseline status |
|---|---|---|---|
| D71265 | `일상생활 및 구어체 한-영 번역 병렬 말뭉치 데이터`, AI Hub dataset `71265` | Official page identifies a Korean-text KO-EN everyday/spoken translation corpus; build year 2021 and update 2022-07 are displayed. | Director-approved role remains `025 Tier A candidate`; provenance closure pending. |
| D71266 | `기술과학 분야 한-영 번역 병렬 말뭉치 데이터`, AI Hub dataset `71266` | Official page states KO-EN 1.5m sentences, technical-science domains, and JSON labeling. | Director-approved role remains `026 Tier A candidate`; provenance closure pending. |
| D87 | `한국어-영어 번역(병렬) 말뭉치`, AI Hub catalogue `87` | Official catalogue describes 1.6m KO-EN translation sentences across news, government websites, ordinances, Korean culture, spoken language, and dialogue. | Director-approved role remains `Legacy unassigned`; see provenance-closure memo. |

## Hard-gate boundary

Official corpus descriptions establish candidate relevance, not automatic final pairability, human-final field provenance, record-level direction, release identity, or redistribution right. Any Tier A/B/C decision remains Director-owned.

## Official sources

1. AI Hub. `일상생활 및 구어체 한-영 번역 병렬 말뭉치 데이터`. https://aihub.or.kr/aihubdata/data/view.do?dataSetSn=71265. Accessed 2026-08-16.
2. AI Hub. `기술과학 분야 한-영 번역 병렬 말뭉치 데이터`. https://aihub.or.kr/aihubdata/data/view.do?dataSetSn=71266. Accessed 2026-08-16.
3. AI Hub. `한국어-영어 번역(병렬) 말뭉치`. https://www.aihub.or.kr/aidata/87. Accessed 2026-08-16.
4. AI Hub. `데이터 이용정책`. https://aihub.or.kr/intrcn/guid/usagepolicy.do. Accessed 2026-08-16.
5. AI Hub. `논문 작성시 주의해야 할 이용정책과 명시 사항` FAQ. https://aihub.or.kr/aihubnews/faq/list.do. Accessed 2026-08-16.

## Do not overclaim

- `AI Hub KO-EN` is not a single corpus identifier.
- Local directory names do not by themselves prove official dataset ID, version, or schema.
- Official corpus pages do not define every local raw field.
- Download approval does not imply permission to publicly redistribute raw or reprocessed corpus files.
