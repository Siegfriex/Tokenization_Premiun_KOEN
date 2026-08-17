from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class PackageStatus:
    import_name: str
    version: str | None
    ok: bool
    detail: str = ""


PACKAGES = (
    "numpy",
    "pandas",
    "scipy",
    "sklearn",
    "matplotlib",
    "seaborn",
    "plotly",
    "pyarrow",
    "polars",
    "duckdb",
    "statsmodels",
    "jupyterlab",
    "ipykernel",
    "torch",
    "torchvision",
    "torchaudio",
    "tensorflow",
    "keras",
    "transformers",
    "tokenizers",
    "datasets",
    "sentence_transformers",
    "tiktoken",
    "kiwipiepy",
    "konlpy",
    "openai",
    "anthropic",
)


def inspect_package(name: str) -> PackageStatus:
    code = (
        "import importlib, json; "
        f"m=importlib.import_module({name!r}); "
        "print(json.dumps({'version': getattr(m, '__version__', 'unknown')}))"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        check=False,
        capture_output=True,
        text=True,
        timeout=180,
        env={**os.environ, "TF_CPP_MIN_LOG_LEVEL": "2"},
    )
    if result.returncode == 0:
        try:
            payload = json.loads(result.stdout.strip().splitlines()[-1])
            return PackageStatus(name, str(payload["version"]), True)
        except (IndexError, KeyError, json.JSONDecodeError) as exc:
            return PackageStatus(name, None, False, f"unreadable output: {exc}")
    detail = " | ".join(result.stderr.strip().splitlines()[-3:])
    return PackageStatus(name, None, False, detail or f"exit={result.returncode}")


def numerical_smoke() -> dict[str, object]:
    import numpy as np
    import pandas as pd
    from sklearn.feature_extraction.text import TfidfVectorizer

    frame = pd.DataFrame({"text": ["token premium", "premium research"]})
    matrix = TfidfVectorizer().fit_transform(frame["text"])
    return {
        "dataframe_shape": list(frame.shape),
        "tfidf_shape": list(matrix.shape),
        "finite": bool(np.isfinite(matrix.toarray()).all()),
    }


def main() -> int:
    statuses = [inspect_package(name) for name in PACKAGES]
    report = {
        "python": sys.version.split()[0],
        "executable": sys.executable,
        "platform": platform.platform(),
        "packages": [asdict(status) for status in statuses],
        "smoke": numerical_smoke(),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if any(not status.ok for status in statuses) else 0


if __name__ == "__main__":
    raise SystemExit(main())
