#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
venv_dir="${VENV_DIR:-$project_root/.venv}"
python_bin="$venv_dir/bin/python"

if [[ ! -x "$python_bin" ]]; then
  echo "가상환경이 없습니다: $venv_dir" >&2
  exit 1
fi

tf_dir="$($python_bin - <<'PY'
import importlib.util
from pathlib import Path

spec = importlib.util.find_spec("tensorflow")
if spec is None or spec.origin is None:
    raise SystemExit("tensorflow is not installed")
print(Path(spec.origin).parent)
PY
)"

site_packages="$($python_bin - <<'PY'
import sysconfig

print(sysconfig.get_paths()["purelib"])
PY
)"

linked=0
while IFS= read -r -d '' library; do
  ln -sf "$library" "$tf_dir/$(basename "$library")"
  linked=$((linked + 1))
done < <(find "$site_packages/nvidia" -mindepth 3 -maxdepth 3 -path '*/lib/*.so*' -type f -print0 2>/dev/null)

ptxas_path="$(find "$site_packages/nvidia" -path '*/bin/ptxas' -type f -print -quit 2>/dev/null || true)"
if [[ -n "$ptxas_path" ]]; then
  ln -sf "$ptxas_path" "$venv_dir/bin/ptxas"
fi

echo "TensorFlow GPU 연결 완료: libraries=$linked, tensorflow=$tf_dir"

