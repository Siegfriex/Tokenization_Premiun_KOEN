"""Canonical notebook의 lineage 위생을 source scan으로 강제한다.

의도: legacy 참조가 다시 기어들어오는 것을 CI 단계에서 막는다. artifact를 읽지 않으므로
데이터가 없는 환경에서도 돌아간다.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from tokenization_premium.lineage import CANONICAL_ARTIFACTS, HISTORICAL_ARTIFACTS
from tokenization_premium.paths import PROJECT_ROOT

CANONICAL_NOTEBOOKS = [
    "03_representation_features.ipynb",
    "04_morphology_features.ipynb",
    "05_o200k_measurement.ipynb",
    "06_regex_chunk_audit.ipynb",
]

# D-05는 Claude-B의 독립 재계산 대상에 아직 포함되지 않았으므로 CANONICAL_ARTIFACTS에 hash를
# 고정하지 않는다. 대신 실행 산출물이 자기 manifest가 기록한 sha256을 담고 있는지 확인한다.
MANIFEST_BACKED_ARTIFACTS = {
    "06_regex_chunk_audit.ipynb": "outputs/manifests/CHUNK_O200K_BASE_MANIFEST_v001.json",
}


def load(name: str) -> dict:
    return json.loads((PROJECT_ROOT / "notebooks" / name).read_text(encoding="utf-8"))


def code_of(nb: dict) -> str:
    """code cell을 이어붙인다.

    IPython magic(%..., !...)은 Python 문법이 아니므로 ast.parse가 실패한다. 줄 번호를
    유지하려고 삭제 대신 빈 줄로 바꾼다 — 검사 대상은 Python 의미론이지 magic이 아니다.
    """
    joined = "\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code")
    return "\n".join("" if line.lstrip().startswith(("%", "!")) else line
                     for line in joined.split("\n"))


def executable_lines(nb: dict) -> list[str]:
    """주석을 제외한 실행 코드 줄만 돌려준다."""
    return [ln for ln in code_of(nb).split("\n") if ln.strip() and not ln.lstrip().startswith("#")]


@pytest.fixture(params=CANONICAL_NOTEBOOKS)
def notebook(request) -> tuple[str, dict]:
    return request.param, load(request.param)


# --- 1. obsolete artifact path -------------------------------------------------------


def test_no_obsolete_artifact_path_in_executable_code(notebook) -> None:
    """폐기 artifact를 '경로로' 참조하면 실패한다.

    registry API(describe_historical)를 통한 이름 참조는 SSOT §24가 요구하는 provenance
    기록이므로 허용한다 — 그 경로는 읽히지 않는다.
    """
    name, nb = notebook
    forbidden_paths = ["REP_FEATURES_v001.parquet", "MORPH_FEATURES_PILOT_v001.parquet",
                       "MORPH_FEATURES_PILOT_MANIFEST_v001.json", ".runtime/nb04-pilot",
                       "TOKEN_MEASUREMENTS_O200K", "MORPH_FEATURES_v002.parquet"]
    for line in executable_lines(nb):
        for token in forbidden_paths:
            assert token not in line, f"{name}: obsolete artifact path in executable code: {line!r}"
        if "MORPH_FEATURES_PILOT_v001" in line or "REP_FEATURES_v001" in line:
            provenance_context = ("describe_historical" in line
                                  or '"superseded"' in line or '"historical"' in line)
            assert provenance_context, (
                f"{name}: superseded artifact referenced outside the historical registry: {line!r}")


def test_canonical_artifacts_are_reached_only_through_the_registry(notebook) -> None:
    name, nb = notebook
    code = code_of(nb)
    assert "assert_canonical_artifact" in code, f"{name}: canonical artifact must be asserted"
    # canonical parquet 경로를 문자열로 직접 조립하지 않는다 (registry를 우회하지 않도록).
    for line in executable_lines(nb):
        assert "data/registry/" not in line, f"{name}: raw registry path in executable code: {line!r}"


# --- 2. old cohort literals ----------------------------------------------------------


def test_no_old_cohort_literal_in_executable_code(notebook) -> None:
    name, nb = notebook
    tree = ast.parse(code_of(nb))
    literals = [n.value for n in ast.walk(tree)
                if isinstance(n, ast.Constant) and isinstance(n.value, int)
                and not isinstance(n.value, bool)]
    assert 3_836_013 not in literals, f"{name}: superseded cohort constant present"
    assert 3_835_988 not in literals, f"{name}: cohort N must be derived from the artifact"


def test_no_superseded_runtime_projection(notebook) -> None:
    name, nb = notebook
    code = code_of(nb)
    for token in ("projected_full_population_3836013", "151.2"):
        assert token not in code, f"{name}: superseded runtime projection {token!r}"


# --- 3. superseded morphology API ----------------------------------------------------


def test_no_codepoint_count_morphology_api(notebook) -> None:
    name, nb = notebook
    for line in executable_lines(nb):
        assert "codepoint_count=" not in line, f"{name}: pre-M1 morphology API: {line!r}"
        assert "input_path=" not in line, f"{name}: pre-conformance run signature: {line!r}"


def test_notebook_calls_match_current_src_signatures(notebook) -> None:
    """import는 성공해도 호출 계약이 깨질 수 있으므로 시그니처까지 검사한다."""
    import importlib
    import inspect

    name, nb = notebook
    code = code_of(nb)
    tree = ast.parse(code)
    symbols: dict[str, tuple[str, str]] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and "tokenization_premium" in node.module:
            for alias in node.names:
                symbols[alias.asname or alias.name] = (node.module, alias.name)

    problems: list[str] = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)):
            continue
        if node.func.id not in symbols:
            continue
        module, attr = symbols[node.func.id]
        target = getattr(importlib.import_module(module), attr)
        if not callable(target):
            continue
        try:
            signature = inspect.signature(target)
        except (TypeError, ValueError):
            continue
        supplied = [kw.arg for kw in node.keywords if kw.arg]
        accepts_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD
                             for p in signature.parameters.values())
        unknown = [k for k in supplied if k not in signature.parameters and not accepts_kwargs]
        required = [p.name for p in signature.parameters.values()
                    if p.kind == inspect.Parameter.KEYWORD_ONLY
                    and p.default is inspect.Parameter.empty]
        missing = [r for r in required if r not in supplied]
        if unknown or missing:
            problems.append(f"{node.func.id}() line {node.lineno}: unknown={unknown} missing={missing}")
    assert not problems, f"{name}: superseded call signatures -> {problems}"


# --- 4. fail-closed, no fallback -----------------------------------------------------


def test_no_fallback_to_pilot_or_earlier_version(notebook) -> None:
    """artifact를 암묵적으로 '고르는' 구문을 금지한다.

    정렬 자체는 무해하다 (예: 파싱한 pair_id 정렬). 위험한 것은 정렬/탐색 결과에서
    하나를 집어 artifact로 삼는 형태와 존재 여부에 따른 분기다.
    """
    name, nb = notebook
    forbidden = [".exists()", "glob(", "latest_manifest", "fallback_to_", "_latest"]
    for line in executable_lines(nb):
        for token in forbidden:
            assert token not in line, f"{name}: fallback-shaped construct: {line!r}"
        if "sorted(" in line:
            assert "[-1]" not in line and "[0]" not in line, (
                f"{name}: implicit newest/first artifact selection: {line!r}")


def test_rebuild_gate_defaults_to_false(notebook) -> None:
    name, nb = notebook
    code = code_of(nb)
    assert "REBUILD_CANONICAL_ARTIFACT = False" in code, f"{name}: rebuild gate missing or enabled"
    assert "if REBUILD_CANONICAL_ARTIFACT:" in code, f"{name}: rebuild gate not enforced"


# --- 5. status strings must reflect the executed reality -----------------------------


def test_no_synthetic_only_or_deferred_state_in_nb05() -> None:
    nb = load("05_o200k_measurement.ipynb")
    code = code_of(nb)
    assert "SYNTHETIC_ONLY" not in code
    assert "FULL_RUN_DEFERRED" not in code
    outputs = "\n".join(
        "".join(o.get("text", [])) for c in nb["cells"] if c["cell_type"] == "code"
        for o in c.get("outputs", []) if o.get("output_type") == "stream")
    assert "ROUNDTRIP_100_PERCENT = PASS" in outputs
    assert "EXACT_DECOMPOSITION = PASS" in outputs


def test_no_pilot_only_status_in_nb04_outputs() -> None:
    nb = load("04_morphology_features.ipynb")
    outputs = "\n".join(
        "".join(o.get("text", [])) for c in nb["cells"] if c["cell_type"] == "code"
        for o in c.get("outputs", []) if o.get("output_type") == "stream")
    assert "PILOT_ONLY_FULL_RUN_DEFERRED" not in outputs
    assert "c056dd7a" not in outputs, "superseded morphology config hash in stored output"
    assert "D03_INDEPENDENT_RECOMPUTATION = PASS" in outputs


# --- 6. current artifact identity is recorded ----------------------------------------


def test_current_artifact_sha_recorded_in_outputs(notebook) -> None:
    name, nb = notebook
    outputs = "\n".join(
        "".join(o.get("text", [])) for c in nb["cells"] if c["cell_type"] == "code"
        for o in c.get("outputs", []) if o.get("output_type") == "stream")
    if name in MANIFEST_BACKED_ARTIFACTS:
        manifest = json.loads(
            (PROJECT_ROOT / MANIFEST_BACKED_ARTIFACTS[name]).read_text(encoding="utf-8"))
        expected_sha = manifest["output"]["sha256"]
    else:
        expected = {"03_representation_features.ipynb": "REP_FEATURES_v002",
                    "04_morphology_features.ipynb": "MORPH_FEATURES_KIWI_v001",
                    "05_o200k_measurement.ipynb": "TOKEN_O200K_BASE_v001"}[name]
        expected_sha = CANONICAL_ARTIFACTS[expected].sha256
    assert expected_sha in outputs, (
        f"{name}: canonical artifact sha256 not recorded in the executed output")
    assert "CANONICAL_ARTIFACT_IDENTITY_VERIFIED" in outputs


def test_every_canonical_notebook_executed_without_error(notebook) -> None:
    name, nb = notebook
    code_cells = [c for c in nb["cells"] if c["cell_type"] == "code"]
    errors = [o for c in code_cells for o in c.get("outputs", [])
              if o.get("output_type") == "error"]
    assert not errors, f"{name}: stored error output {[e.get('ename') for e in errors]}"
    assert all(c.get("execution_count") for c in code_cells), f"{name}: unexecuted code cell"


# --- 7. historical provenance is preserved, not deleted ------------------------------


def test_superseded_artifacts_remain_documented_but_unreachable() -> None:
    assert set(HISTORICAL_ARTIFACTS) == {"REP_FEATURES_v001", "MORPH_FEATURES_PILOT_v001"}
    for name in HISTORICAL_ARTIFACTS:
        assert name not in CANONICAL_ARTIFACTS


def test_scripts_do_not_leak_into_notebook_imports(notebook) -> None:
    name, nb = notebook
    code = code_of(nb)
    assert "scripts." not in code and "sys.path" not in code, (
        f"{name}: notebooks must import canonical implementation from src only")


def test_audit_report_exists_for_pre_g5_traceability() -> None:
    report = PROJECT_ROOT / "outputs/reports/LEGACY_REFERENCE_AUDIT_PRE_G5_v001.md"
    assert report.exists()
    assert Path(report).read_text(encoding="utf-8").count("REPORT_TYPO_ONLY") >= 1
