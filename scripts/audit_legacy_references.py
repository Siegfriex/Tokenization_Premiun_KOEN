"""Pre-G5 legacy reference census — READ ONLY.

Phase A: 저장소 전체에서 과거 pipeline 상태(old cohort N / old artifact / old API /
old hash / old status / old schema)를 전수 식별하고 severity matrix를 만든다.
어떤 파일도 수정하지 않는다.

ipynb는 grep이 아니라 cell 단위로 parse해서 legacy reference가
SOURCE_CODE / MARKDOWN / EXECUTED_OUTPUT / NOTEBOOK_METADATA
중 어디에 있는지 분리한다.
"""

from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass
from pathlib import Path

from tokenization_premium.paths import PROJECT_ROOT

EXCLUDE_DIRS = {".git", ".venv", ".runtime", "node_modules", "__pycache__",
                ".pytest_cache", ".ruff_cache", ".mypy_cache", ".agent_worktrees"}
# data/는 불변 raw corpus와 파생 artifact다. 저장소 "로직"이 아니므로 census 대상이 아니며,
# 실제로 원문에 "scaffolding" 같은 단어가 들어 있어 순수 오탐만 만든다.
EXCLUDE_TOP = {"data"}
# census 자신의 산출물과 도구는 설계상 모든 legacy 문자열을 담고 있으므로 자기참조 제외한다.
SELF_EXCLUDE = {"outputs/reports/LEGACY_REFERENCE_AUDIT_PRE_G5_v001.json",
                "outputs/reports/LEGACY_REFERENCE_AUDIT_PRE_G5_v001.md",
                "scripts/audit_legacy_references.py"}
TEXT_SUFFIXES = {".py", ".md", ".json", ".yaml", ".yml", ".toml", ".cfg", ".txt", ".csv", ".sh"}

# 위치별 기본 심각도 (§4)
LOC_SOURCE, LOC_MD, LOC_OUT, LOC_META = "SOURCE_CODE", "MARKDOWN", "EXECUTED_OUTPUT", "NOTEBOOK_METADATA"
LOC_COMMENT = "COMMENT_OR_DOCSTRING"
# outputs/ 아래 JSON/CSV는 실행 기록(provenance)이지 실행 코드가 아니다. SSOT §24에 따라
# 과거값을 보존해야 하므로 기본 등급을 HISTORICAL로 둔다.
LOC_RECORD = "EXECUTION_RECORD"
# 실행되는 코드만 P0 후보다. 주석/docstring/markdown은 서술이므로 등급을 낮춘다.
LOC_BASE = {LOC_SOURCE: "P0", LOC_OUT: "P1", LOC_MD: "P2", LOC_META: "P2",
            LOC_COMMENT: "P2", LOC_RECORD: "P3"}

# 과거임을 명시하는 문맥이면 P3로 내린다 (§24 provenance 보존)
HISTORICAL_MARKERS = re.compile(
    r"SUPERSEDED|HISTORICAL|NOT_CURRENT|superseded|historical|과거|폐기|이전 |구 |legacy|"
    r"changelog|Conformance decision|conformance finding|M[1-6] |negative test|회귀|regression",
    re.I)


@dataclass
class Pattern:
    pid: str
    regex: str
    canonical: str
    category: str
    severity_override: str | None = None
    note: str = ""


PATTERNS: list[Pattern] = [
    # --- old cohort ---------------------------------------------------------
    Pattern("OLD_COHORT_N", r"3[_,]?836[_,]?013", "3,835,988 (derive from input artifact)", "OLD_COHORT"),
    # --- old representation -------------------------------------------------
    Pattern("REP_V001_PATH", r"REP_FEATURES_v001", "REP_FEATURES_v002", "OLD_ARTIFACT"),
    Pattern("REP_47_COLS", r"\b47\b[^\n]{0,40}(column|col|feature)|(column|col|feature)[^\n]{0,40}\b47\b",
            "49 columns (v002)", "OLD_SCHEMA"),
    Pattern("EXPECTED_COLS_47", r"EXPECTED_COLS\s*=\s*47", "49", "OLD_SCHEMA"),
    # --- old morph pilot ----------------------------------------------------
    Pattern("MORPH_PILOT_V001", r"MORPH_FEATURES_PILOT_(v001|MANIFEST_v001)",
            "MORPH_FEATURES_KIWI_v001 (full)", "OLD_ARTIFACT"),
    Pattern("NB04_PILOT_DIR", r"nb04-pilot(?!-v002)", ".runtime/morph-full/<run_id>", "OLD_ARTIFACT"),
    Pattern("SANITY_85", r"85[- ]row|MORPHOLOGY_SANITY_AUDIT_SAMPLE",
            "Director N=100 audit", "OLD_EVIDENCE"),
    Pattern("PILOT_ONLY", r"PILOT_ONLY|FULL_RUN_DEFERRED|pilot only|full population deferred",
            "FULL_POPULATION executed", "OLD_STATUS"),
    # --- old morph config / API --------------------------------------------
    Pattern("OLD_MORPH_CONFIG_SHA", r"c056dd7a[0-9a-f]*", "6f48802a… (morph_v002)", "OLD_HASH"),
    Pattern("CODEPOINT_DENOM", r"codepoint_count\s*=|ko_codepoint_count[^\n]{0,40}denominator|"
                               r"morpheme_density_denominator[^\n]{0,30}codepoint",
            "eojeol_count (SSOT §13.6)", "OLD_API"),
    Pattern("EXACT_AFFIX_MAP", r'tag\s+in\s+\{?["\']XSN["\']|_DERIV_AFFIX_TAGS\s*=\s*frozenset',
            "base_tag = tag.partition('-')[0]", "OLD_API"),
    # --- old ETA ------------------------------------------------------------
    Pattern("OLD_ETA", r"151\.2|151 min|projected_full_population_3836013",
            "2.7 min projected / 187.9 s actual", "OLD_RUNTIME"),
    # --- old tokenizer ------------------------------------------------------
    Pattern("SYNTHETIC_ONLY", r"[Ss]ynthetic[- ][Oo]nly|SYNTHETIC_ONLY|synthetic only",
            "FULL_POPULATION executed", "OLD_STATUS"),
    Pattern("OLD_TOKEN_ARTIFACT", r"TOKEN_MEASUREMENTS_O200K",
            "TOKEN_O200K_BASE_v001 (SSOT §38)", "OLD_ARTIFACT"),
    Pattern("TOK_SCAFFOLD", r"scaffold|light scaffold", "full population engine", "OLD_STATUS"),
    # --- old gate status ----------------------------------------------------
    Pattern("GATE_NOT_PASS", r"G[234][^\n]{0,30}(NOT[_ ]CLAIMED|NOT PASS|BLOCKED|NOT_ENTERED)",
            "B G2/G3/G4 verdict", "OLD_STATUS"),
    Pattern("AWAITING_ADJUDICATION", r"EVIDENCE_COMPLETE_AWAITING_ADJUDICATION|AWAITING_ADJUDICATION",
            "B verdict", "OLD_STATUS"),
    # --- dangerous fallbacks (§11) -----------------------------------------
    Pattern("FALLBACK_IF_EXISTS", r"if\s+\w*(REP_FEATURES|MORPH|TOKEN|PILOT)\w*\.exists\(\)",
            "fail-closed identity assertion", "FALLBACK", "P0"),
    Pattern("FALLBACK_GLOB", r"glob\([^)]*\.parquet[^)]*\)\s*\[\s*0\s*\]|sorted\([^)]*\)\s*\[\s*-1\s*\]",
            "explicit artifact id/path/hash", "FALLBACK", "P0"),
    Pattern("FALLBACK_LATEST", r"latest_manifest|fallback_to_pilot|_latest\b",
            "explicit artifact id", "FALLBACK", "P0"),
    # --- row-count hardcode (§12) ------------------------------------------
    Pattern("COHORT_N_HARDCODE", r"3[_,]?835[_,]?988", "derive from input artifact", "N_HARDCODE"),
]

# script 분류 (§8)
SCRIPT_CLASS = {
    "build_rep_features_v002.py": ("CANONICAL_LOGIC_HIDDEN_IN_SCRIPT",
                                   "D-02 v002 생성 로직이 notebook 밖에 있다 (SSOT §36 IA에 scripts 없음)"),
    "run_morphology_pilot_v002.py": ("ONE_OFF_MIGRATION", "corrected pilot 재현 + 폐기 pilot 대조"),
    "build_morphology_audit_100.py": ("ONE_OFF_MIGRATION", "Director 감사 표본 생성"),
    "run_full_measurement.py": ("CANONICAL_LOGIC_HIDDEN_IN_SCRIPT",
                                "현재 canonical D-03/D-04 artifact를 실제로 생성한 실행 경로"),
    "validate_full_measurement.py": ("CANONICAL_LOGIC_HIDDEN_IN_SCRIPT",
                                     "G2/G3 증거 검증 로직이 notebook 밖에 있다"),
    "build_token_audit_sample.py": ("CANONICAL_LOGIC_HIDDEN_IN_SCRIPT", "G3 audit sample 생성"),
    "bench_kiwi_morphology.py": ("ENGINEERING_BENCHMARK", "연구 산출물 아님"),
    "bench_o200k_concurrency.py": ("ENGINEERING_BENCHMARK", "연구 산출물 아님"),
    "audit_legacy_references.py": ("ENGINEERING_BENCHMARK", "본 census 도구"),
}


@dataclass
class Finding:
    finding_id: str
    path: str
    locator: str
    location: str
    pattern: str
    category: str
    excerpt: str
    canonical: str
    severity: str
    historical_marked: bool = False


findings: list[Finding] = []
_counter = {"n": 0}


def add(path: Path, locator: str, location: str, p: Pattern, excerpt: str, context: str) -> None:
    historical = bool(HISTORICAL_MARKERS.search(context))
    severity = p.severity_override or LOC_BASE[location]
    if historical and severity != "P0":
        severity = "P3"
    _counter["n"] += 1
    findings.append(Finding(
        finding_id=f"L{_counter['n']:03d}",
        path=str(path.relative_to(PROJECT_ROOT)),
        locator=locator, location=location, pattern=p.pid, category=p.category,
        excerpt=excerpt.strip()[:150], canonical=p.canonical, severity=severity,
        historical_marked=historical))


def docstring_lines(text: str) -> set[int]:
    """.py에서 docstring이 차지하는 line 번호 집합을 구한다."""
    out: set[int] = set()
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return out
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            doc = ast.get_docstring(node, clean=False)
            if doc and node.body and isinstance(node.body[0], ast.Expr):
                expr = node.body[0]
                out.update(range(expr.lineno, (expr.end_lineno or expr.lineno) + 1))
    return out


def scan_text(path: Path, text: str, location: str, locator_prefix: str = "line") -> None:
    lines = text.split("\n")
    docs = docstring_lines(text) if path.suffix == ".py" else set()
    for pat in PATTERNS:
        rx = re.compile(pat.regex)
        for i, line in enumerate(lines, 1):
            if rx.search(line):
                loc = location
                if path.suffix == ".py" and (i in docs or line.lstrip().startswith("#")):
                    loc = LOC_COMMENT
                lo = max(0, i - 3)
                context = "\n".join(lines[lo:i + 2])
                add(path, f"{locator_prefix} {i}", loc, pat, line, context)


def scan_notebook(path: Path) -> None:
    nb = json.loads(path.read_text(encoding="utf-8"))
    for idx, cell in enumerate(nb.get("cells", [])):
        src = "".join(cell.get("source", []))
        loc = LOC_SOURCE if cell["cell_type"] == "code" else LOC_MD
        if src:
            scan_text_block(path, src, loc, f"cell {idx}")
        for o_i, out in enumerate(cell.get("outputs", [])):
            chunks = []
            if out.get("output_type") == "stream":
                chunks.append("".join(out.get("text", [])))
            for key, val in out.get("data", {}).items():
                if key.startswith("text/"):
                    chunks.append("".join(val) if isinstance(val, list) else str(val))
            if out.get("output_type") == "error":
                chunks.append("\n".join(out.get("traceback", [])))
            for chunk in chunks:
                scan_text_block(path, chunk, LOC_OUT, f"cell {idx} out {o_i}")
    meta = json.dumps(nb.get("metadata", {}), ensure_ascii=False)
    scan_text_block(path, meta, LOC_META, "metadata")


def scan_text_block(path: Path, text: str, location: str, locator: str) -> None:
    lines = text.split("\n")
    for pat in PATTERNS:
        rx = re.compile(pat.regex)
        for i, line in enumerate(lines, 1):
            if rx.search(line):
                loc = location
                if location == LOC_SOURCE and line.lstrip().startswith("#"):
                    loc = LOC_COMMENT
                lo = max(0, i - 3)
                add(path, f"{locator} L{i}", loc, pat, line, "\n".join(lines[lo:i + 2]))


def iter_files() -> list[Path]:
    out = []
    for p in PROJECT_ROOT.rglob("*"):
        if not p.is_file():
            continue
        if any(part in EXCLUDE_DIRS for part in p.parts):
            continue
        rel = p.relative_to(PROJECT_ROOT)
        if rel.parts and rel.parts[0] in EXCLUDE_TOP:
            continue
        if p.suffix in {".parquet", ".xlsx"}:
            continue
        if str(rel) in SELF_EXCLUDE:
            continue
        if p.suffix == ".ipynb" or p.suffix in TEXT_SUFFIXES or p.name == ".gitignore":
            out.append(p)
    return sorted(out)


def import_graph() -> dict:
    """canonical notebook -> src function / artifact path 그래프 (§7)."""
    graph: dict[str, dict] = {}
    for nb_path in sorted((PROJECT_ROOT / "notebooks").glob("*.ipynb")):
        nb = json.loads(nb_path.read_text(encoding="utf-8"))
        code = "\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code")
        imports, artifacts = set(), set()
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module and "tokenization_premium" in node.module:
                    for alias in node.names:
                        imports.add(f"{node.module}.{alias.name}")
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if "tokenization_premium" in alias.name:
                            imports.add(alias.name)
        except SyntaxError:
            imports.add("<unparseable>")
        for m in re.finditer(r"[\w/\.\-]*(?:PAIR_REGISTRY|REP_FEATURES|MORPH_FEATURES|TOKEN_O200K|"
                             r"TOKEN_MEASUREMENTS)[\w/\.\-]*", code):
            artifacts.add(m.group(0))
        graph[nb_path.name] = {"src_imports": sorted(imports), "artifact_refs": sorted(artifacts)}
    return graph


def resolve_src_symbols() -> dict:
    """notebook이 import하는 심볼이 현재 src에 실제로 존재하는지 확인 (§7 dead/superseded)."""
    import importlib
    result = {}
    for nb, info in import_graph().items():
        missing = []
        for sym in info["src_imports"]:
            if sym == "<unparseable>":
                continue
            module, _, name = sym.rpartition(".")
            try:
                mod = importlib.import_module(module)
                if not hasattr(mod, name):
                    missing.append(sym)
            except Exception:  # noqa: BLE001
                missing.append(sym)
        result[nb] = missing
    return result


if __name__ == "__main__":
    files = iter_files()
    for path in files:
        if path.suffix == ".ipynb":
            scan_notebook(path)
        else:
            rel = str(path.relative_to(PROJECT_ROOT))
            if path.suffix in {".md", ".txt"}:
                location = LOC_MD
            elif rel.startswith("outputs/") and path.suffix in {".json", ".csv"}:
                location = LOC_RECORD
            else:
                location = LOC_SOURCE
            scan_text(path, path.read_text(encoding="utf-8", errors="replace"), location)

    graph = import_graph()
    missing_symbols = resolve_src_symbols()

    by_sev: dict[str, int] = {}
    for f in findings:
        by_sev[f.severity] = by_sev.get(f.severity, 0) + 1

    payload = {
        "artifact_id": "LEGACY_REFERENCE_AUDIT_PRE_G5_v001",
        "phase": "A_READ_ONLY_CENSUS",
        "files_scanned": len(files),
        "total_findings": len(findings),
        "severity_counts": by_sev,
        "findings": [f.__dict__ for f in findings],
        "notebook_import_graph": graph,
        "unresolved_notebook_imports": {k: v for k, v in missing_symbols.items() if v},
        "script_classification": {k: {"class": v[0], "note": v[1]} for k, v in SCRIPT_CLASS.items()},
    }
    out = PROJECT_ROOT / "outputs/reports/LEGACY_REFERENCE_AUDIT_PRE_G5_v001.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    print(f"files scanned : {len(files)}")
    print(f"findings      : {len(findings)}")
    print(f"severity      : {dict(sorted(by_sev.items()))}")
    print("\n--- P0 ---")
    for f in findings:
        if f.severity == "P0":
            print(f"  {f.finding_id} {f.path}:{f.locator} [{f.location}] {f.pattern}")
            print(f"       {f.excerpt[:110]}")
    print("\n--- unresolved notebook imports (dead/superseded API) ---")
    for nb, miss in missing_symbols.items():
        if miss:
            print(f"  {nb}: {miss}")
    print(f"\nwrote {out.relative_to(PROJECT_ROOT)}")
