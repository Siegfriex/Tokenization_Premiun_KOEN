# AI Hub KO-EN Provenance Closure — D87 Priority Audit

- Audit date: 2026-08-16 KST
- Evidence standard: official-source evidence only for provenance conclusions.
- Base: `main@f1b2a901b3bc9a9d759af0698bd0c308ec6e468b`.
- Local-data boundary: this audit did not inspect a local filesystem or raw files.

## A. Source list

1. AI Hub, *Q&A로 풀어본 AI 학습용 데이터 상세 매뉴얼* (2019), section `한국어-영어 번역 말뭉치 AI 데이터`. https://www.aihub.or.kr/web-nas/aihub21/files/sample/intro/Q%26A%20%EC%82%AC%EB%A1%80%EC%A7%91%20%EC%B5%9C%EC%A2%85-%EB%82%B1%EC%9E%A5.pdf. Accessed 2026-08-16.
2. AI Hub, *일상생활 및 구어체 한-영 번역 병렬 말뭉치 데이터*, dataset `71265`. https://aihub.or.kr/aihubdata/data/view.do?dataSetSn=71265. Accessed 2026-08-16.
3. AI Hub, *기술과학 분야 한-영 번역 병렬 말뭉치 데이터*, dataset `71266`. https://aihub.or.kr/aihubdata/data/view.do?dataSetSn=71266. Accessed 2026-08-16.
4. AI Hub, *한국어-영어 번역(병렬) 말뭉치*, catalogue `87`. https://www.aihub.or.kr/aidata/87. Accessed 2026-08-16.
5. AI Hub, *데이터 이용정책*. https://aihub.or.kr/intrcn/guid/usagepolicy.do. Accessed 2026-08-16.
6. AI Hub, *논문 작성시 주의해야 할 이용정책과 명시 사항* FAQ. https://aihub.or.kr/aihubnews/faq/list.do. Accessed 2026-08-16.

## B. Dataset identity status

| Local label | Official candidate | WEB/OFFICIAL | Release-link status | Director role — do not override |
|---|---|---|---|---|
| 025 | D71265 | Official dataset page identifies the candidate title and KO-EN everyday/spoken translation corpus. | UNVERIFIED_LINK: local archive/version not inspected here. | `025 Tier A candidate` |
| 026 | D71266 | Official dataset page identifies the candidate title, KO-EN 1.5m sentences, technical-science domains, JSON labeling. | UNVERIFIED_LINK: local archive/version not inspected here. | `026 Tier A candidate` |
| Legacy | D87 | Official catalogue identifies a 1.6m KO-EN translation corpus; 2019 official manual supplies construction evidence. | UNVERIFIED_LINK: local 1,602,418-record count is not treated as an official current-release count. | `Legacy unassigned` |

## C. D87 construction and quality evidence

### WEB/OFFICIAL

The 2019 AI Hub manual states that a high-quality Korean-English translation corpus of 1.6m sentences was constructed for neural machine translation. It describes the composition as news 800k, local-government websites 100k, ordinances 100k, Korean culture 100k, spoken language 400k, and dialogue 100k. It names Saltlux Partners, Evertran, and Flitto as construction organizations.

The documented process is collection -> cleaning -> translation -> inspection -> distribution. The manual states that paired sentences were intended for training; sentence numbers were attached to all sentences. It describes metadata including news URL/date and dialogue-set/speaker distinctions. Distribution is described as XLSX. The manual describes externally performed quality inspection by Kwangwoon University AI Translation Industry Research Center and follow-up full inspection by construction organizations for output associated with workers with low quality indices. It describes accuracy/fluency assessment and error categories including mistranslation, omission, addition/source-text error, grammar, and awkwardness.

### What this supports

- D87 was intentionally built as a KO-EN translation-learning corpus, not merely described as generic web text.
- It has documented construction workflow, sentence-pair intent, sentence numbering, selected source metadata, and external quality-inspection process.

### What this does not support

- Exact semantics of current local fields.
- A record-level guarantee that final `ko`/`en` fields are human-final translations.
- A MT-draft plus human-post-edit workflow.
- Record-level original/source and target direction.
- Equality of local 1,602,418 rows with a current official release.
- Permission to redistribute raw or derived corpus files.

## D. Field-semantics matrix

Field names are not semantic evidence.

| Local raw field | Official-source definition found | Classification | Permitted statement |
|---|---|---|---|
| `mt` | No official D71265/D71266/D87 schema/guide definition located | UNKNOWN | Do not infer machine-translation draft status. |
| `ko_original` | No official definition located | UNKNOWN | Do not infer original-language or source-side status. |
| `en_original` | No official definition located | UNKNOWN | Do not infer original-language or source-side status. |
| `ko` | No official definition located | UNKNOWN | Do not infer human-final Korean status. |
| `en` | No official definition located | UNKNOWN | Do not infer human-final English status. |
| `source_language` | No official definition located | UNKNOWN | Do not infer record-level translation direction. |
| `target_language` | No official definition located | UNKNOWN | Do not infer record-level translation direction. |
| `source` | D87 manual documents some source metadata, but not the exact local field schema | PARTIAL | It may be metadata; exact field meaning is unverified. |
| `license` | AI Hub policy/FAQ establish access and redistribution restrictions, not the local field-value dictionary | PARTIAL | `license="open"` field semantics are unverified. |

## E. Release-link status

### LOCAL_REPORTED_GIT_EVIDENCE

Git-persisted reconnaissance branch `data/g1-recon@617f6fdaf994f9496d97e15621a6921d49451015` reports logical record counts `025=2,700,345`, `026=1,350,162`, and `Legacy=1,602,418`, plus a canonical-file allowlist and identity/duplicate checks. This is local reconnaissance evidence, not an official release statement.

### UNVERIFIED_LINK

No official manifest, official archive hash, official version identifier, or official schema has been established here to prove that the reported Legacy 1,602,418 records equal the D87 current official release. Therefore: `LOCAL_REPORTED_GIT_EVIDENCE != WEB/OFFICIAL release identity`.

## F. License and acquisition

AI Hub policy says data download requires a separate procedure. The official FAQ states that original downloaded files such as JSON/JPG may not be externally leaked and that redistribution of reprocessed data is in principle disallowed absent prior consultation; it also describes attribution requirements.

Accordingly, local observed value `license="open"` does **not** establish permission to redistribute AI Hub raw data, derived text, or a public corpus mirror. Its exact schema meaning remains UNKNOWN until an official field dictionary or dataset-specific terms define it.

## G. Provenance closure status

| Candidate | Construction/QC | Exact field semantics | Release identity | License closure | Provenance closure status |
|---|---|---|---|---|---|
| D71265 | Official corpus-page level only | UNKNOWN | UNVERIFIED_LINK | incomplete | OPEN |
| D71266 | Official corpus-page level only | UNKNOWN | UNVERIFIED_LINK | incomplete | OPEN |
| D87 | PARTIAL: 2019 official construction/QC manual | UNKNOWN/PARTIAL | UNVERIFIED_LINK | incomplete | OPEN |

This memo does not revise D-RD-05 roles. No official evidence found here materially contradicts `025 Tier A candidate`, `026 Tier A candidate`, or `Legacy unassigned`.

D87 translation-direction label: `UNKNOWN`, not `HUMAN_PARALLEL_UNKNOWN`. The official manual documents corpus-level translation and inspection but does not define local final-field provenance or record-level direction.

## H. Conflicts and reconciliation

No direct official contradiction was found. The following are unresolved and must not be silently resolved by filename or field-name inference:

- local label `025` -> official D71265 exact archive/version/schema
- local label `026` -> official D71266 exact archive/version/schema
- Legacy 1,602,418 records -> D87 current official release
- `mt`, `ko_original`, `en_original`, `ko`, `en`, `source_language`, `target_language` semantics
- `license="open"` -> legal redistribution permission

If a future official schema/manual contradicts Git-persisted local evidence, create `CONFLICT_FOR_RECONCILIATION` with the official URL/access date and exact Git branch/SHA; do not change Director roles silently.
