#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv가 없습니다. README의 시스템 준비 명령을 먼저 실행하세요." >&2
  exit 1
fi

if [[ "$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')" != "3.12" ]]; then
  echo "Python 3.12가 필요합니다." >&2
  exit 1
fi

mkdir -p .runtime/{cache,huggingface,jupyter/runtime,keras,matplotlib,torch}

echo "[1/5] Python 3.12 프로젝트 환경 동기화"
UV_CACHE_DIR="$project_root/.runtime/uv-cache" uv sync --all-groups

echo "[2/5] TensorFlow WSL GPU 라이브러리 연결"
bash scripts/configure_tensorflow_gpu.sh

echo "[3/5] Jupyter 커널 등록"
.venv/bin/python -m ipykernel install --user --name tokenization_premium \
  --display-name "Python (Tokenization Premium .venv)"

echo "[4/5] Node 개발 도구 설치"
npm install

echo "[5/5] 환경 스모크 검사"
bash scripts/run_env_check.sh

echo
echo "설정 완료: source scripts/activate_project_env.sh"

