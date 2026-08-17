from __future__ import annotations

import importlib.metadata as metadata
import importlib.util
import platform
import sys

PYTHON_DISTS = {
    "numpy": "numpy",
    "pandas": "pandas",
    "scipy": "scipy",
    "scikit-learn": "sklearn",
    "statsmodels": "statsmodels",
    "matplotlib": "matplotlib",
    "seaborn": "seaborn",
    "plotly": "plotly",
    "openpyxl": "openpyxl",
    "tiktoken": "tiktoken",
    "transformers": "transformers",
    "tokenizers": "tokenizers",
    "sentencepiece": "sentencepiece",
    "sentence-transformers": "sentence_transformers",
    "torch": "torch",
    "anthropic": "anthropic",
    "openai": "openai",
    "httpx": "httpx",
    "pydantic": "pydantic",
    "tqdm": "tqdm",
    "jupyterlab": "jupyterlab",
    "notebook": "notebook",
    "ipykernel": "ipykernel",
    "ruff": "ruff",
    "pytest": "pytest",
}


def dist_version(dist_name: str) -> str:
    try:
        return metadata.version(dist_name)
    except metadata.PackageNotFoundError:
        return "missing"


def module_status(module_name: str) -> str:
    return "ok" if importlib.util.find_spec(module_name) else "missing"


def main() -> int:
    print(f"python_executable\t{sys.executable}")
    print(f"python_version\t{sys.version.replace(chr(10), ' ')}")
    print(f"platform\t{platform.platform()}")
    print()
    print("python_package\tdistribution_version\tmodule_status")
    for dist_name, module_name in PYTHON_DISTS.items():
        print(f"{dist_name}\t{dist_version(dist_name)}\t{module_status(module_name)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
