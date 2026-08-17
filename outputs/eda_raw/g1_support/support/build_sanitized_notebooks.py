"""Build G1 sanitized exploratory notebooks without importing old-branch files."""

from __future__ import annotations

from pathlib import Path

import nbformat


ROOT = Path(__file__).resolve().parents[4]
NOTEBOOK_DIR = ROOT / "notebooks/exploratory/raw"
DEFAULT_RAW_ROOT = Path("/home/sieg/projects-wsl/Tokenization_Premium/data/raw/aigub")


def md(source: str, cell_id: str):
    cell = nbformat.v4.new_markdown_cell(source)
    cell["id"] = cell_id
    return cell


def code(source: str, cell_id: str):
    cell = nbformat.v4.new_code_cell(source)
    cell["id"] = cell_id
    return cell


def build(config: dict, target_call: str, target_explanation: str, filename: str) -> None:
    setup = f'''from pathlib import Path
import json, os, sys
import pandas as pd
from IPython.display import Markdown, display

def discover_project_root(start=Path.cwd()):
    for candidate in (start.resolve(), *start.resolve().parents):
        if (candidate / "pyproject.toml").is_file() and (candidate / "src/tokenization_premium").is_dir():
            return candidate
    raise RuntimeError(f"Tokenization_Premium checkout not found from {{start}}")

DISCOVERED_PROJECT_ROOT = discover_project_root()
sys.path.insert(0, str(DISCOVERED_PROJECT_ROOT / "src"))
from tokenization_premium.paths import PROJECT_ROOT
assert PROJECT_ROOT.resolve() == DISCOVERED_PROJECT_ROOT.resolve()

RAW_ROOT = Path(os.environ.get("TOKENIZATION_PREMIUM_RAW_ROOT", {str(DEFAULT_RAW_ROOT)!r})).expanduser().resolve()
SUPPORT_DIR = PROJECT_ROOT / "outputs/eda_raw/g1_support/support"
sys.path.insert(0, str(SUPPORT_DIR))

from sanitized_raw_eda import profile_dataset, save_profile, plot_profile, {target_call.split('(')[0]}

CONFIG = {config!r}
CONFIG["raw_root"] = str(RAW_ROOT / CONFIG.pop("raw_relative_dir"))
OUTPUT_DIR = PROJECT_ROOT / "outputs/eda_raw/g1_support" / CONFIG["artifact_prefix"]
FIGURE_DIR = PROJECT_ROOT / "outputs/figures/eda_raw/g1_support" / CONFIG["artifact_prefix"]
TARGET_OUTPUT_DIR = OUTPUT_DIR / "targeted"
TARGET_FIGURE_DIR = FIGURE_DIR / "targeted"

print("project root: CURRENT_CHECKOUT")
print("raw root:", RAW_ROOT)
print("dataset:", CONFIG["dataset_local_id"])
print("population: FULL_POPULATION_AGGREGATES")
print("raw text export: 0")
'''
    profile = '''result = profile_dataset(CONFIG)
profile_paths = save_profile(result, OUTPUT_DIR)
figure_paths = plot_profile(result, FIGURE_DIR)
display(pd.DataFrame([result["summary"]]))
display(result["record_counts"])
'''
    inspect = '''display(Markdown("### Schema: keys/types/missingness only"))
display(result["schema"].sort_values(["group", "missing_or_empty_rate"], ascending=[True, False]))
display(Markdown("### Length summaries: aggregate only"))
display(result["length_summary"])
display(Markdown("### Non-sensitive category distributions"))
display(result["categories"].sort_values(["dimension", "record_count"], ascending=[True, False]).groupby("dimension").head(20))
display(Markdown("### Soft noise and duplicate candidates"))
display(result["noise"].sort_values("rate", ascending=False).head(40))
display(result["duplicates"])
'''
    target = f'''targeted = {target_call}
for name, frame in targeted.items():
    display(Markdown(f"### {{name}}"))
    display(frame)
'''
    validate = '''required = profile_paths + figure_paths
for path in required:
    assert path.exists(), path
for frame_name in ["inventory", "record_counts", "schema", "length_summary", "noise", "categories", "duplicates"]:
    frame = result[frame_name]
    assert not {"ko", "en", "ko_preview", "en_preview", "원문", "번역문", "URL"}.intersection(frame.columns)
assert result["summary"]["raw_text_exported"] is False
assert result["summary"]["text_hash_exported"] is False
print("SANITIZED NOTEBOOK PASS")
print("raw text rows exported: 0")
print("text hashes exported: 0")
'''
    cells = [
        md(f'''# {config["dataset_local_id"]} — G1 Sanitized Raw EDA

Status: **G1 SANITIZED SUPPORT / PRE-INGESTION EDA / NOT QC ACCEPTANCE**

이 notebook은 old EDA branch의 notebook/blob을 복사하지 않고 local raw에서 aggregate를 새로 계산한다.
원문 문장, preview, URL, pair ID, text hash를 출력하거나 저장하지 않는다.''', f'{config["artifact_prefix"]}-title'),
        md('''## 1. Safety and execution contract

- Full-population aggregate profiling
- Raw roots are read-only
- No tokenization, morphology, model fitting, inferential claim, or automatic exclusion
- No raw sentence/example output''', f'{config["artifact_prefix"]}-contract'),
        code(setup, f'{config["artifact_prefix"]}-setup'),
        md('## 2. Full-population sanitized profile', f'{config["artifact_prefix"]}-profile-md'),
        code(profile, f'{config["artifact_prefix"]}-profile'),
        md('''## 3. Aggregate structure, length, category, and soft flags

모든 표는 keys, counts, rates, lengths, categories만 포함한다.''', f'{config["artifact_prefix"]}-inspect-md'),
        code(inspect, f'{config["artifact_prefix"]}-inspect'),
        md(f'''## 4. Targeted decision evidence

{target_explanation}

모든 결과는 structural/local observation이며 causal, exclusion, Tier, QC acceptance 판단이 아니다.''', f'{config["artifact_prefix"]}-target-md'),
        code(target, f'{config["artifact_prefix"]}-target'),
        md('''## 5. Interpretation scaffold

관찰:

원인 후보:

제한: local raw aggregate이며 official identity/provenance를 확정하지 않는다.

결론: Research Director reconciliation 전에는 source rank, exclusion, Tier를 결정하지 않는다.''', f'{config["artifact_prefix"]}-interpret'),
        md('## 6. Export validation', f'{config["artifact_prefix"]}-validate-md'),
        code(validate, f'{config["artifact_prefix"]}-validate'),
    ]
    notebook = nbformat.v4.new_notebook(cells=cells)
    notebook.metadata = {
        "kernelspec": {"display_name": "Tokenization Premium", "language": "python", "name": "tokenization_premium"},
        "language_info": {"name": "python", "version": "3.12"},
        "g1_sanitized_support": {"raw_text_exported": False, "old_branch_blob_reused": False},
    }
    NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
    nbformat.write(notebook, NOTEBOOK_DIR / filename)


build(
    {
        "dataset_local_id": "AIHUB_025_LOCAL_G1_SANITIZED",
        "artifact_prefix": "aihub_025_g1",
        "kind": "json",
        "raw_relative_dir": "025.일상생활 및 구어체 한-영 번역 병렬 말뭉치 데이터",
    },
    "targeted_025(Path(CONFIG['raw_root']), TARGET_OUTPUT_DIR, TARGET_FIGURE_DIR)",
    "direction×split×domain, direction×source×domain, exact-pair duplicate mechanisms, SBS scope, crowd-source string variants, and domain-mapping preview.",
    "EDA_RAW_AIHUB_025_G1_SANITIZED.ipynb",
)

build(
    {
        "dataset_local_id": "AIHUB_026_LOCAL_G1_SANITIZED",
        "artifact_prefix": "aihub_026_g1",
        "kind": "json",
        "raw_relative_dir": "026.기술과학 분야 한-영 번역 병렬 말뭉치 데이터",
    },
    "targeted_026(Path(CONFIG['raw_root']), TARGET_OUTPUT_DIR, TARGET_FIGURE_DIR)",
    "source×domain crosstab, patent-source/technology-domain row-level biconditional, and domain-mapping preview.",
    "EDA_RAW_AIHUB_026_G1_SANITIZED.ipynb",
)

build(
    {
        "dataset_local_id": "LOCAL_KO_EN_XLSX_G1_SANITIZED",
        "artifact_prefix": "legacy_ko_en_g1",
        "kind": "xlsx",
        "raw_relative_dir": "한국어-영어 번역(병렬) 말뭉치",
    },
    "targeted_legacy(Path(CONFIG['raw_root']), TARGET_OUTPUT_DIR, TARGET_FIGURE_DIR)",
    "News2↔Culture exact-pair overlap, multiplicity, and aggregate metadata concentration under POTENTIAL_CORPUS_COMPOSITION_OVERLAP.",
    "EDA_RAW_LEGACY_KO_EN_XLSX_G1_SANITIZED.ipynb",
)

print("sanitized notebooks built")
