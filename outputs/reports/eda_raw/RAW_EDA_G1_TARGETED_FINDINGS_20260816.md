# Raw EDA G1 Targeted Findings — 2026-08-16

All findings below are recomputed aggregate-only `LOCAL_OBSERVED` evidence. They are not causal findings, exclusion decisions, QC acceptance, official corpus claims, or Tier decisions.

## AIHub 025

- Full population: 2,700,345 local records.
- SBS occurs in 449,805 rows; observed rows outside `KO_TO_EN`: 0; observed rows outside raw domain `일상생활`: 0. This is a local categorical scope observation only.
- Raw source strings `크라우드 소싱` and `크라우드소싱` occur in different observed direction/domain cells. EDA can establish that the strings and their cross-tabs differ; it cannot establish whether they are only spelling variants or distinct provenance.
- Exact-pair duplicate rows after the first member: 214,252 across 2,486,093 distinct exact-pair groups.
- Direction-mirror matchable rows: 50,529 across 50,511 groups, explaining 23.5839% of duplicate rows under the stated matchable-row decomposition. This is a structural candidate mechanism, not semantic equivalence evidence.
- Cross-split matchable rows: 36,089 across 25,238 groups.
- Proposed mapping preview only: `일상생활 -> general` 899,757; `해외고객과의채팅 -> dialogue` 540,221; `해외영업 -> other` 1,260,367. No canonical data was written.

## AIHub 026

- Raw source `특허정보원`: 359,910 rows; raw domain `기술과학`: 359,910 rows; joint rows: 359,910.
- `특허정보원` outside `기술과학`: 0; `기술과학` outside `특허정보원`: 0. This is an exact row-level local categorical biconditional, not an official provenance claim.
- Proposed mapping preview only: `기술과학 -> technology` 359,910; all remaining observed raw domains -> `other` 990,252. No canonical data was written.

## Legacy News(2) and Culture

- Exact KO/EN overlap groups: 2,469; one-to-one matchable groups: 2,469.
- News(2): 2,469 / 200,541 rows, 1.2312%.
- Culture: 2,469 / 100,646 rows, 2.4532%.
- Multiplicity is 1 News(2) row plus 1 Culture row for each observed group, combined size 2.
- Available news metadata and culture keyword distributions are exported only as aggregate category counts and concentration summaries.
- Classification: `POTENTIAL_CORPUS_COMPOSITION_OVERLAP`; no error or exclusion interpretation is made.
