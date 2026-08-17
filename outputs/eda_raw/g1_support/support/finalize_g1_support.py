from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
REPORT_DIR = ROOT / "outputs/reports/eda_raw"
MANIFEST_DIR = ROOT / "outputs/manifests/eda_raw"

NOTEBOOKS = [
    ROOT / "notebooks/exploratory/raw/EDA_RAW_AIHUB_025_G1_SANITIZED.ipynb",
    ROOT / "notebooks/exploratory/raw/EDA_RAW_AIHUB_026_G1_SANITIZED.ipynb",
    ROOT / "notebooks/exploratory/raw/EDA_RAW_LEGACY_KO_EN_XLSX_G1_SANITIZED.ipynb",
    ROOT / "notebooks/exploratory/evidence/AIHUB_LOCAL_RECON_EVIDENCE_EXPORT_20260816.ipynb",
]

TEXT_ROOTS = [
    ROOT / "outputs/eda_raw/g1_support",
    ROOT / "outputs/aihub_recon_g1",
    ROOT / "outputs/reports/eda_raw",
]

ARTIFACT_ROOTS = [
    ROOT / "notebooks/exploratory/raw",
    ROOT / "notebooks/exploratory/evidence",
    ROOT / "outputs/eda_raw/g1_support",
    ROOT / "outputs/figures/eda_raw/g1_support",
    ROOT / "outputs/aihub_recon_g1",
    ROOT / "outputs/reports/eda_raw",
]

FORBIDDEN_RAW_HEADERS = {
    "ko", "en", "ko_preview", "en_preview", "원문", "번역문", "raw_text",
    "raw_ko", "raw_en", "sentence", "sentence_text", "text_hash", "pair_hash",
}
URL_RE = re.compile(r"(?i)\b(?:https?|ftp)://|www\.")
EMAIL_RE = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?82[- .]?)?(?:0\d{1,2}[- .]?)?\d{3,4}[- .]\d{4}(?!\d)")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def notebook_state(path: Path) -> dict[str, int | str]:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    code = [cell for cell in notebook["cells"] if cell.get("cell_type") == "code"]
    return {
        "relative_path": rel(path),
        "code_cells": len(code),
        "executed_code_cells": sum(cell.get("execution_count") is not None for cell in code),
        "error_outputs": sum(
            output.get("output_type") == "error"
            for cell in code
            for output in cell.get("outputs", [])
        ),
    }


def inspect_csv(path: Path) -> list[dict[str, str | int]]:
    violations: list[dict[str, str | int]] = []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = set(reader.fieldnames or [])
        forbidden = sorted(headers & FORBIDDEN_RAW_HEADERS)
        if forbidden:
            violations.append({
                "relative_path": rel(path),
                "check": "forbidden_raw_header",
                "count": len(forbidden),
                "classification": "FAIL",
            })
        pattern_counts = {"url_like": 0, "email_like": 0, "phone_like": 0, "long_nonpath_value": 0}
        for row in reader:
            for field, value in row.items():
                value = value or ""
                pattern_counts["url_like"] += bool(URL_RE.search(value))
                pattern_counts["email_like"] += bool(EMAIL_RE.search(value))
                pattern_counts["phone_like"] += bool(PHONE_RE.search(value))
                if len(value) > 200 and "path" not in field.lower():
                    pattern_counts["long_nonpath_value"] += 1
        for check, count in pattern_counts.items():
            if count:
                violations.append({
                    "relative_path": rel(path),
                    "check": check,
                    "count": count,
                    "classification": "FAIL",
                })
    return violations


def inspect_json_strings(value, field_path: str = "root") -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            found.extend(inspect_json_strings(child, f"{field_path}.{key}"))
    elif isinstance(value, list):
        for child in value:
            found.extend(inspect_json_strings(child, f"{field_path}[]"))
    elif isinstance(value, str):
        found.append((field_path, value))
    return found


def validate() -> tuple[list[dict[str, str | int]], list[dict[str, str | int]]]:
    violations: list[dict[str, str | int]] = []
    notebook_states = [notebook_state(path) for path in NOTEBOOKS]
    for state in notebook_states:
        if state["executed_code_cells"] != state["code_cells"] or state["error_outputs"]:
            violations.append({
                "relative_path": state["relative_path"],
                "check": "fresh_kernel_execution",
                "count": 1,
                "classification": "FAIL",
            })

    for base in TEXT_ROOTS:
        for path in base.rglob("*"):
            if not path.is_file() or "support" in path.parts:
                continue
            if path.suffix.lower() == ".csv":
                violations.extend(inspect_csv(path))
            elif path.suffix.lower() == ".json" and path.name != "fontlist-v3.11.0.json":
                data = json.loads(path.read_text(encoding="utf-8-sig"))
                counts = {"url_like": 0, "email_like": 0, "phone_like": 0, "long_nonpath_value": 0}
                for field, value in inspect_json_strings(data):
                    counts["url_like"] += bool(URL_RE.search(value))
                    counts["email_like"] += bool(EMAIL_RE.search(value))
                    counts["phone_like"] += bool(PHONE_RE.search(value))
                    if len(value) > 200 and "path" not in field.lower():
                        counts["long_nonpath_value"] += 1
                for check, count in counts.items():
                    if count:
                        violations.append({
                            "relative_path": rel(path),
                            "check": check,
                            "count": count,
                            "classification": "FAIL",
                        })

    return notebook_states, violations


def write_reports(notebook_states: list[dict[str, str | int]], violations: list[dict[str, str | int]]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)

    validation_path = MANIFEST_DIR / "G1_SANITIZATION_VALIDATION_20260816.csv"
    rows = violations or [{
        "relative_path": "ALL_ALLOWLISTED_DERIVED_ARTIFACTS",
        "check": "raw_text_url_pii_text_hash_and_notebook_execution",
        "count": 0,
        "classification": "PASS",
    }]
    with validation_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["relative_path", "check", "count", "classification"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)

    targeted = REPORT_DIR / "RAW_EDA_G1_TARGETED_FINDINGS_20260816.md"
    targeted.write_text(
        """# Raw EDA G1 Targeted Findings — 2026-08-16

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
""",
        encoding="utf-8",
    )

    execution_lines = "\n".join(
        f"- `{state['relative_path']}`: {state['executed_code_cells']}/{state['code_cells']} code cells executed; {state['error_outputs']} error outputs"
        for state in notebook_states
    )
    report = REPORT_DIR / "EDA_G1_SANITIZED_SUPPORT_REPORT_20260816.md"
    report.write_text(
        f"""# EDA G1 Sanitized Support Report — 2026-08-16

## A. Old-branch exposure audit

- Read-only audit: `outputs/reports/eda_raw/EDA_REPOSITORY_EXPOSURE_AUDIT_20260816.md`.
- Audited target: `eda/g0-raw-notebooks@4e56fdbc70c0571e9eeb912c61816885ad5477a7`, including reachable committed versions.
- Old branch was not merged, cherry-picked, rewritten, deleted, or force-pushed.

## B. Sanitized file allowlist

- `notebooks/exploratory/raw/*_G1_SANITIZED.ipynb`
- `notebooks/exploratory/evidence/AIHUB_LOCAL_RECON_EVIDENCE_EXPORT_20260816.ipynb`
- `outputs/eda_raw/g1_support/**` excluding caches and font caches
- `outputs/figures/eda_raw/g1_support/**`
- `outputs/aihub_recon_g1/**` excluding font caches
- `outputs/reports/eda_raw/**`
- `outputs/manifests/eda_raw/**`

All dataset artifacts were recomputed from immutable local raw roots. No contaminated Git blob was used as a data source.

## C. Omitted unsafe files

- Every `*_samples.csv` and every raw KO/EN preview export was omitted.
- The three old executed notebooks with sentence previews were not ported.
- Old raw-preview producer/generator scripts were not ported.
- No text hash value, pair hash value, raw URL, PII-like value, raw sentence, or recoverable sentence excerpt is allowlisted.

## D. Notebook execution

{execution_lines}

Validation result: `{('PASS' if not violations else 'FAIL')}`. Details: `outputs/manifests/eda_raw/G1_SANITIZATION_VALIDATION_20260816.csv`.

## E. Output hashes

Artifact hashes are recorded in `outputs/manifests/eda_raw/G1_SUPPORT_ARTIFACT_HASHES_20260816.csv`. The manifest excludes itself to avoid self-reference.

## F. New branch SHA

- Branch: `eda/g1-support`
- Released base: `f1b2a901b3bc9a9d759af0698bd0c308ec6e468b`
- Commit SHA and remote ref are authoritative in the final push evidence because a commit cannot embed its own SHA without changing that SHA.

## G. Remaining public-history remediation requirement

The old branch and its raw-text blobs remain reachable. No deletion, history rewrite, or force-push was performed. Public-history remediation remains `AWAIT_OPS_DR_01` and requires Research Director authorization.
""",
        encoding="utf-8",
    )


def write_hash_manifest() -> None:
    manifest = MANIFEST_DIR / "G1_SUPPORT_ARTIFACT_HASHES_20260816.csv"
    paths: set[Path] = set()
    for base in ARTIFACT_ROOTS:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            if path == manifest or "__pycache__" in path.parts or ".mplconfig" in path.parts:
                continue
            paths.add(path)
    with manifest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["relative_path", "bytes", "sha256"],
            lineterminator="\n",
        )
        writer.writeheader()
        for path in sorted(paths):
            writer.writerow({"relative_path": rel(path), "bytes": path.stat().st_size, "sha256": sha256(path)})


if __name__ == "__main__":
    states, findings = validate()
    write_reports(states, findings)
    write_hash_manifest()
    print(json.dumps({
        "notebooks": states,
        "sanitization_violations": len(findings),
        "result": "PASS" if not findings else "FAIL",
    }, ensure_ascii=False, indent=2))
    if findings:
        raise SystemExit(1)
