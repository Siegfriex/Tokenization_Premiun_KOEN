"""Recreate the privacy-safe local recon evidence notebook in the G1 worktree."""

from __future__ import annotations

import re
from pathlib import Path

import nbformat


WORKTREE_ROOT = Path(__file__).resolve().parents[4]
SOURCE_ROOT = Path("/home/sieg/projects-wsl/Tokenization_Premium")
DEFAULT_RAW_ROOT = SOURCE_ROOT / "data/raw/aigub"
SOURCE = SOURCE_ROOT / "notebooks/01_aihub_local_recon_evidence_export.ipynb"
TARGET = WORKTREE_ROOT / "notebooks/exploratory/evidence/AIHUB_LOCAL_RECON_EVIDENCE_EXPORT_20260816.ipynb"

if not SOURCE.is_file():
    raise FileNotFoundError(SOURCE)

notebook = nbformat.read(SOURCE, as_version=4)
for cell in notebook.cells:
    if cell.cell_type == "code":
        for output in cell.get("outputs", []):
            rendered = str(output)
            if "ko_preview" in rendered or "en_preview" in rendered:
                raise AssertionError("source evidence notebook contains raw preview output")
        cell.outputs = []
        cell.execution_count = None

inventory_rows = [
    {
        "relative_path": "notebooks/00_environment_repro.ipynb",
        "filename": "00_environment_repro.ipynb",
        "extension": ".ipynb",
        "bytes": (WORKTREE_ROOT / "notebooks/00_environment_repro.ipynb").stat().st_size,
        "modified_time": "BASELINE_FILE",
        "git_status_if_available": "TRACKED",
        "first_markdown_heading_or_blank": "00 — Environment / Repository Reproducibility",
        "inferred_role": "environment reproducibility",
        "ai_hub_recon_relevant_boolean": False,
        "notes": "released main baseline",
    },
]
for filename, title in [
    ("EDA_RAW_AIHUB_025_G1_SANITIZED.ipynb", "AIHub 025 sanitized raw EDA"),
    ("EDA_RAW_AIHUB_026_G1_SANITIZED.ipynb", "AIHub 026 sanitized raw EDA"),
    ("EDA_RAW_LEGACY_KO_EN_XLSX_G1_SANITIZED.ipynb", "Legacy KO-EN XLSX sanitized raw EDA"),
]:
    path = WORKTREE_ROOT / "notebooks/exploratory/raw" / filename
    inventory_rows.append({
        "relative_path": path.relative_to(WORKTREE_ROOT).as_posix(),
        "filename": filename,
        "extension": ".ipynb",
        "bytes": path.stat().st_size,
        "modified_time": "G1_REBUILD",
        "git_status_if_available": "NEW_G1_SUPPORT",
        "first_markdown_heading_or_blank": title,
        "inferred_role": "sanitized raw dataset exploratory EDA",
        "ai_hub_recon_relevant_boolean": True,
        "notes": "aggregate-only; no old-branch blob reused",
    })

old_notebook_rel = "notebooks/01_aihub_local_recon_evidence_export.ipynb"
new_notebook_rel = "notebooks/exploratory/evidence/AIHUB_LOCAL_RECON_EVIDENCE_EXPORT_20260816.ipynb"
for cell in notebook.cells:
    source = cell.source
    source = source.replace(old_notebook_rel, new_notebook_rel)
    source = source.replace("outputs/aihub_recon/", "outputs/aihub_recon_g1/")
    if cell.cell_type == "code":
        source = source.replace(
            "PROJECT_ROOT = Path('/home/sieg/projects-wsl/Tokenization_Premium')",
            f'''def discover_project_root(start=Path.cwd()):
    for candidate in (start.resolve(), *start.resolve().parents):
        if (candidate / 'pyproject.toml').is_file() and (candidate / 'src/tokenization_premium').is_dir():
            return candidate
    raise RuntimeError(f'Tokenization_Premium checkout not found from {{start}}')

DISCOVERED_PROJECT_ROOT = discover_project_root()
sys.path.insert(0, str(DISCOVERED_PROJECT_ROOT / 'src'))
from tokenization_premium.paths import PROJECT_ROOT
assert PROJECT_ROOT.resolve() == DISCOVERED_PROJECT_ROOT.resolve()
RAW_ROOT = Path(os.environ.get('TOKENIZATION_PREMIUM_RAW_ROOT', {str(DEFAULT_RAW_ROOT)!r})).expanduser().resolve()''',
        )
        source = source.replace(
            "OUTPUT_ROOT = PROJECT_ROOT / 'outputs/aihub_recon'",
            "OUTPUT_ROOT = PROJECT_ROOT / 'outputs/aihub_recon_g1'",
        )
        source = re.sub(r"PROJECT_ROOT/'data/raw/aigub/([^']+)'", r"RAW_ROOT/'\1'", source)
        source = source.replace(
            "path=PROJECT_ROOT/entry.relative_file_path; suffix=path.suffix.lower()",
            "path=RAW_ROOT/Path(entry.relative_file_path).relative_to('data/raw/aigub'); suffix=path.suffix.lower()",
        )
        source = source.replace(
            "'allowed_raw_roots': [root.relative_to(PROJECT_ROOT).as_posix() for root in ALLOWED_ROOTS]",
            "'allowed_raw_roots': [(Path('data/raw/aigub')/root.relative_to(RAW_ROOT)).as_posix() for root in ALLOWED_ROOTS]",
        )
        source = source.replace("'project_root': str(PROJECT_ROOT)", "'project_root': 'CURRENT_CHECKOUT'")
        source = re.sub(
            r"PREEXISTING_NOTEBOOK_ROWS = .*\nRUN_TIMESTAMP_KST =",
            f"PREEXISTING_NOTEBOOK_ROWS = {inventory_rows!r}\nRUN_TIMESTAMP_KST =",
            source,
            count=1,
        )
        source = source.replace(
            "def safe_rel(path):\n    return path.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()",
            "def safe_rel(path):\n    resolved=path.resolve()\n    project=PROJECT_ROOT.resolve()\n    raw=RAW_ROOT.resolve()\n    if resolved == project or project in resolved.parents:\n        return resolved.relative_to(project).as_posix()\n    if resolved == raw or raw in resolved.parents:\n        suffix=resolved.relative_to(raw)\n        return (Path('data/raw/aigub')/suffix).as_posix()\n    raise ValueError(f'path is outside project and raw roots: {path.name}')",
        )
    cell.source = source

notebook.cells[0].source = notebook.cells[0].source.replace(
    "# KOEN-TP-RS-001 — AIHub Local Recon Evidence Export",
    "# KOEN-TP-RS-001 — AIHub Local Recon Evidence Export — G1 Sanitized Support",
)
notebook.cells[0].source += "\n\n- Rebuilt from released main without reusing any `eda/g0-raw-notebooks` blob."
notebook.metadata["g1_sanitized_support"] = {
    "old_branch_blob_reused": False,
    "raw_text_exported": False,
    "root_level_01_collision": False,
}

TARGET.parent.mkdir(parents=True, exist_ok=True)
nbformat.validate(notebook)
nbformat.write(notebook, TARGET)
print(TARGET)
