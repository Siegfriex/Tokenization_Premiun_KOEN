#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"

if [[ ! -x .venv/bin/python ]]; then
  echo "가상환경이 없습니다. bash scripts/setup_environment.sh 를 먼저 실행하세요." >&2
  exit 1
fi

source scripts/activate_project_env.sh
exec .venv/bin/python scripts/check_gpu.py

