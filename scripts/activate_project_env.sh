#!/usr/bin/env bash

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  echo "이 스크립트는 source로 실행하세요: source scripts/activate_project_env.sh" >&2
  exit 2
fi

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

prepend_path_value() {
  local variable_name="$1"
  local new_value="$2"
  local current_value="${!variable_name:-}"
  case ":$current_value:" in
    *":$new_value:"*) ;;
    *) export "$variable_name=$new_value${current_value:+:$current_value}" ;;
  esac
}

if [[ ! -x "$project_root/.venv/bin/python" ]]; then
  echo "가상환경이 없습니다. 먼저 bash scripts/setup_environment.sh 를 실행하세요." >&2
  return 1
fi

export TOKENIZATION_PREMIUM_ROOT="$project_root"
export VIRTUAL_ENV="$project_root/.venv"
prepend_path_value PATH "$project_root/node_modules/.bin"
prepend_path_value PATH "$VIRTUAL_ENV/bin"
prepend_path_value PYTHONPATH "$project_root/src"
export MPLCONFIGDIR="$project_root/.runtime/matplotlib"
export JUPYTER_CONFIG_DIR="$project_root/.runtime/jupyter/config"
export JUPYTER_DATA_DIR="$project_root/.runtime/jupyter/data"
export JUPYTER_RUNTIME_DIR="$project_root/.runtime/jupyter/runtime"
export XDG_CACHE_HOME="$project_root/.runtime/cache"
export HF_HOME="$project_root/.runtime/huggingface"
export HF_DATASETS_CACHE="$HF_HOME/datasets"
export TORCH_HOME="$project_root/.runtime/torch"
export KERAS_HOME="$project_root/.runtime/keras"
export TOKENIZERS_PARALLELISM="${TOKENIZERS_PARALLELISM:-false}"
export TF_CPP_MIN_LOG_LEVEL="${TF_CPP_MIN_LOG_LEVEL:-2}"
export CUDA_DEVICE_ORDER="${CUDA_DEVICE_ORDER:-PCI_BUS_ID}"

mkdir -p \
  "$MPLCONFIGDIR" "$JUPYTER_CONFIG_DIR" "$JUPYTER_DATA_DIR" "$JUPYTER_RUNTIME_DIR" \
  "$XDG_CACHE_HOME" "$HF_HOME" "$HF_DATASETS_CACHE" "$TORCH_HOME" "$KERAS_HOME"

tf_dir="$($VIRTUAL_ENV/bin/python - <<'PY' 2>/dev/null || true
import importlib.util
from pathlib import Path

spec = importlib.util.find_spec("tensorflow")
print(Path(spec.origin).parent if spec and spec.origin else "")
PY
)"

if [[ -n "$tf_dir" ]]; then
  prepend_path_value LD_LIBRARY_PATH "$tf_dir"
  prepend_path_value LD_LIBRARY_PATH "/usr/lib/wsl/lib"
else
  prepend_path_value LD_LIBRARY_PATH "/usr/lib/wsl/lib"
fi

unset project_root tf_dir
unset -f prepend_path_value
