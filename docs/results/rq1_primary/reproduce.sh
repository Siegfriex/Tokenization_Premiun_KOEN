#!/usr/bin/env bash
# RQ1 publication package — reproduction orchestration wrapper.
# 분석 logic을 재구현하지 않는다. 기존 canonical 절차를 호출하고 결과를 대조만 한다.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="${KOEN_REPO:-$(cd "$HERE/../../.." && pwd)}"

# 인터프리터 탐색: 명시 지정 > repo venv > 활성 venv > system python3.
# figures 모드는 matplotlib만 있으면 되므로 아무 3.12 환경이나 무방하다.
pick_python() {
  local c
  for c in "${KOEN_PYTHON:-}" "$REPO/.venv/bin/python" "${VIRTUAL_ENV:-}/bin/python"            "$(command -v python3 || true)"; do
    [ -n "$c" ] && [ -x "$c" ] || continue
    if "$c" -c "import matplotlib" >/dev/null 2>&1; then echo "$c"; return 0; fi
  done
  # matplotlib을 가진 후보가 없으면 마지막 실행 가능한 것을 돌려주고 호출부에서 실패시킨다
  for c in "${KOEN_PYTHON:-}" "$REPO/.venv/bin/python" "$(command -v python3 || true)"; do
    [ -n "$c" ] && [ -x "$c" ] && { echo "$c"; return 0; }
  done
  return 1
}
PY="$(pick_python)" || { echo "PYTHON_NOT_FOUND" >&2; exit 2; }

require_matplotlib() {
  "$PY" -c "import matplotlib" >/dev/null 2>&1 && return 0
  cat >&2 <<EOF
PREREQUISITE_MISSING: matplotlib을 가진 Python을 찾지 못했다.

  시도한 인터프리터: $PY

해결 방법 중 하나를 쓰라.
  1) KOEN_PYTHON=/path/to/python ./reproduce.sh figures
  2) repository root에서 'npm run setup' 으로 .venv 구성 후 재시도
  3) pip install matplotlib
EOF
  exit 2
}

D04="$REPO/data/registry/TOKEN_O200K_BASE_v001.parquet"
D04_SHA="1c30e3276222dd94885ae4f79fc6ab5c45e4e26226de0afd91fc6b1f7d2c16e7"
NB="$REPO/notebooks/08_primary_inference.ipynb"

usage() {
  cat <<'EOF'
usage: ./reproduce.sh <mode>

  figures     committed aggregate data에서 figure를 재생성하고 hash를 검증한다.
              D-04도 원문도 필요 없다.

  verify      committed RQ1 artifact들의 값 일관성을 검증한다. 큰 artifact가 필요 없다.

  inference   D-04 존재/hash를 확인하고 canonical NB08을 headless 실행한 뒤
              frozen expected value와 machine-compare 한다. D-04가 필요하다.
EOF
}

need_d04() {
  if [ ! -f "$D04" ]; then
    cat >&2 <<EOF
PREREQUISITE_MISSING: canonical D-04 artifact가 없다.

  expected path : $D04
  expected sha256: $D04_SHA

이 파일은 Git에 포함되어 있지 않다 (.gitignore:27 data/registry/**).
REPRODUCE.md 의 Level B / Level C 를 참조하라. synthetic fallback은 제공하지 않는다.
EOF
    exit 2
  fi
  local actual
  actual="$(sha256sum "$D04" | cut -d' ' -f1)"
  if [ "$actual" != "$D04_SHA" ]; then
    echo "D04_SHA_MISMATCH: expected $D04_SHA, got $actual" >&2
    exit 2
  fi
  echo "  D-04 sha256 OK"
}

case "${1:-}" in
  figures)
    echo "== FIGURES =="
    require_matplotlib
    "$PY" "$HERE/build_rq1_figures.py" --mode figures
    "$PY" "$HERE/verify_package.py" --check figures
    ;;
  verify)
    echo "== VERIFY =="
    echo "  python: $PY"
    "$PY" "$HERE/verify_package.py" --check all --repo "$REPO"
    ;;
  inference)
    echo "== INFERENCE =="
    need_d04
    [ -f "$NB" ] || { echo "NOTEBOOK_MISSING: $NB" >&2; exit 2; }
    echo "  canonical NB08 headless 실행 (6-8분)"
    "$REPO/.venv/bin/jupyter" nbconvert --to notebook --execute --inplace \
      --ExecutePreprocessor.timeout=2700 --ExecutePreprocessor.kernel_name=python3 "$NB"
    "$PY" "$HERE/verify_package.py" --check inference --repo "$REPO"
    ;;
  *)
    usage; exit 1 ;;
esac
