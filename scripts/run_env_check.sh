#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"

required_commands=(python3 uv node npm java git)
missing=()

echo "system"
for command_name in "${required_commands[@]}"; do
  if command -v "$command_name" >/dev/null 2>&1; then
    printf '%-12s %s\n' "$command_name" "$(command -v "$command_name")"
  else
    printf '%-12s missing\n' "$command_name"
    missing+=("$command_name")
  fi
done

printf '%-12s %s\n' "python" "$(python3 --version 2>&1)"
printf '%-12s %s\n' "uv" "$(uv --version 2>&1)"
printf '%-12s %s\n' "node" "$(node --version 2>&1)"
printf '%-12s %s\n' "npm" "$(npm --version 2>&1)"

if [[ ! -x .venv/bin/python ]]; then
  echo "project venv missing: $project_root/.venv" >&2
  exit 1
fi

source scripts/activate_project_env.sh

echo
echo "python_packages"
.venv/bin/python scripts/check_environment.py

echo
echo "dependency_integrity"
uv pip check
npm ls --depth=0

echo
echo "fonts"
fc-match 'NanumGothic' | head -1
fc-match 'Noto Sans CJK KR' | head -1

if ((${#missing[@]} > 0)); then
  echo "missing required commands: ${missing[*]}" >&2
  exit 1
fi

