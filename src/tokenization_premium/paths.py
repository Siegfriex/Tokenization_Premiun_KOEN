"""Notebook과 지원 모듈이 공유하는 canonical project 경로를 정의한다."""

from pathlib import Path  # 운영체제와 독립적인 경로 연산을 수행한다.

PROJECT_ROOT = Path(__file__).resolve().parents[2]  # 현재 worktree의 pyproject가 있는 root를 계산한다.
DATA_DIR = PROJECT_ROOT / "data"  # 모든 연구 데이터 계층의 공통 상위 경로를 고정한다.
RAW_DATA_DIR = DATA_DIR / "raw"  # 변경하지 않는 원천 데이터 경로를 정의한다.
INTERIM_DATA_DIR = DATA_DIR / "interim"  # 재생성 가능한 중간 데이터 경로를 정의한다.
PROCESSED_DATA_DIR = DATA_DIR / "processed"  # 분석 입력용 가공 데이터 경로를 정의한다.
OUTPUTS_DIR = PROJECT_ROOT / "outputs"  # 재현성 산출물의 공통 상위 경로를 정의한다.
MANIFESTS_DIR = OUTPUTS_DIR / "manifests"  # JSON·Parquet manifest 저장 경로를 정의한다.
FIGURES_DIR = OUTPUTS_DIR / "figures"  # PNG·SVG figure 저장 경로를 정의한다.
MODELS_DIR = OUTPUTS_DIR / "models"  # 향후 모델 산출물 경로를 SSOT IA에 맞춘다.
REPORTS_DIR = OUTPUTS_DIR / "reports"  # 검증 보고서 저장 경로를 SSOT IA에 맞춘다.


def ensure_runtime_directories() -> None:
    """
    /**
     * @purpose Phase 0 실행에 필요한 출력 디렉터리를 idempotent하게 생성한다.
     * @spec_ref §30, §36, §37 Phase 0
     * @return None
     * @raises OSError 경로 생성 권한이 없거나 파일 충돌이 있는 경우
     * @validation 생성 후 각 경로의 디렉터리 여부를 검사한다.
     * @artifact outputs/manifests, outputs/figures, outputs/reports
     */
    """
    for path in (MANIFESTS_DIR, FIGURES_DIR, MODELS_DIR, REPORTS_DIR):  # Phase 0 출력 경로만 순회한다.
        path.mkdir(parents=True, exist_ok=True)  # 기존 디렉터리를 보존하며 누락된 경로를 만든다.
        if not path.is_dir():  # 생성 결과가 실제 디렉터리인지 fail-fast로 확인한다.
            raise NotADirectoryError(path)  # 파일 충돌 등 잘못된 상태에서 실행을 중단한다.
