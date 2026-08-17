#!/usr/bin/env bash
# NB06 / D-05 재현 실행기 — LEVEL A, 그리고 canonical artifact가 있으면 LEVEL B까지.
#
# LEVEL C(전집단 재실행)는 기존 canonical artifact를 지워야 하므로 여기에 넣지 않는다.
# 절차는 REPRODUCE.md의 C-1 ~ C-5를 직접 따른다.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../../.." && pwd)"
cd "$REPO"

export PYTHONPATH="${PYTHONPATH:+$PYTHONPATH:}$REPO/src"
PYTHON="${PYTHON:-python}"

D05="data/registry/CHUNK_O200K_BASE_v001.parquet"
D05_EXPECTED_SHA256="bfa98bd6cf7ee8b7254c469aed3e259ce43cc8f0529153347ca4c2c3fc1944ab"

echo "=============================================================="
echo " NB06 / D-05  reproduction"
echo " repo   : $REPO"
echo " python : $($PYTHON --version 2>&1)"
echo "=============================================================="

echo
echo "--- LEVEL A : figures from committed aggregate JSON ------------"
"$PYTHON" "$HERE/build_nb06_figures.py"

echo
echo "--- package verification --------------------------------------"
"$PYTHON" "$HERE/verify_nb06_d05.py"

echo
echo "--- LEVEL B : D-05 artifact validation -------------------------"
if [[ ! -f "$D05" ]]; then
  echo "  SKIPPED — $D05 이 없다 (저장소에 포함되지 않는 파일이다)."
  echo "  LEVEL_B=NOT_RUN"
  exit 0
fi

ACTUAL_SHA="$(sha256sum "$D05" | cut -d' ' -f1)"
echo "  artifact sha256 : $ACTUAL_SHA"
echo "  expected        : $D05_EXPECTED_SHA256"
if [[ "$ACTUAL_SHA" != "$D05_EXPECTED_SHA256" ]]; then
  echo "  MISMATCH — 다른 파일을 검증하는 것은 의미가 없다. 중단한다."
  echo "  LEVEL_B=FAIL"
  exit 1
fi

# 검증 로직을 문서용으로 다시 구현하지 않고 canonical validator를 재사용한다.
"$PYTHON" scripts/validate_d05.py
echo "  LEVEL_B=PASS"
