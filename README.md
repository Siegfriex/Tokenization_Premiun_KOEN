# Tokenization Premium

토큰화·표현학습 연구를 위한 독립 실행 환경입니다. 다른 DSJA/SBS 저장소의 가상환경을
공유하거나 심볼릭 링크하지 않으며, 이 저장소의 `pyproject.toml`과 `uv.lock`을 의존성
SSOT로 사용합니다.

## 환경 기준

- Python 3.12 + 프로젝트 전용 `.venv`
- `uv` lock/sync 기반 재현성
- NumPy, pandas, SciPy, scikit-learn, Jupyter, 시각화·통계·Parquet 도구
- PyTorch CUDA 13.0 wheel + TensorFlow `and-cuda` (WSL/Linux)
- Transformers, tokenizers, tiktoken, datasets, sentence-transformers, 한국어 토크나이저 도구
- OpenAI·Anthropic SDK와 HTTPX (키는 저장소에 넣지 않고 환경변수로만 주입)
- Node.js 20 + npm 10 연구 보조 도구
- 로컬 캐시는 `.runtime/`, 원천/중간/가공 데이터는 `data/` 아래에서 관리

이 머신에서 확인한 호스트 기준은 NVIDIA RTX 5070 Laptop GPU, 드라이버 595.71,
드라이버 지원 CUDA 13.2입니다. PyTorch는 호스트 드라이버보다 낮은 CUDA 13.0 wheel을
사용합니다. `nvcc`가 없는 상태에서도 사전 빌드 wheel의 GPU 실행은 가능하지만,
사용자 정의 CUDA 확장 컴파일에는 별도 CUDA Toolkit이 필요합니다.

## 최초 설정

```bash
cd /home/sieg/projects-wsl/Tokenization_Premium
bash scripts/setup_environment.sh
source scripts/activate_project_env.sh
```

설정 스크립트는 Python 환경 동기화, TensorFlow 라이브러리 연결, Jupyter 커널 등록,
Node 의존성 설치, 기본 검사를 순서대로 수행합니다. Jupyter에서는
`Python (Tokenization Premium .venv)` 커널을 선택합니다.

## 일상 명령

```bash
source scripts/activate_project_env.sh
npm run check:env
npm run check:gpu
npm test
npm run lint
npm run jupyter
```

GPU 검사는 TensorFlow와 PyTorch를 서로 다른 Python 하위 프로세스에서 실행합니다.
두 프레임워크의 CUDA 런타임을 한 프로세스에서 동시에 초기화해 생기는 충돌을 피하기
위한 구성입니다.

## 디렉터리 계약

- `src/tokenization_premium/`: 재사용 가능한 연구 코드
- `notebooks/`: 탐색·실험 노트북
- `data/raw/`: 변경하지 않는 원천 데이터
- `data/interim/`: 중간 산출물
- `data/processed/`: 분석 입력용 가공 데이터
- `models/`: 체크포인트와 모델 산출물
- `reports/figures/`: 검토 가능한 표·그림
- `.runtime/`: Hugging Face, Torch, Jupyter, Matplotlib 등 로컬 캐시

대용량 데이터와 모델은 기본적으로 Git에서 제외됩니다. 공개·버전 관리가 필요한
산출물은 별도 manifest와 checksum을 둔 뒤 선택적으로 추적하세요.

## 시스템 패키지

현재 필수 항목인 `build-essential`, `python3-dev`, `python3.12-venv`, `pkg-config`,
`libgomp1`, `fonts-nanum`, `fonts-noto-cjk`, Java 21, Node 20은 이미 준비되어 있어
필수 `sudo apt` 작업은 없습니다.

향후 사용자 정의 CUDA 확장, 그래프 렌더링, 영상/음성 데이터, Git LFS를 실제로 사용할
때만 아래 선택 패키지를 설치하면 됩니다.

```bash
sudo apt update
sudo apt install -y cmake ninja-build graphviz ffmpeg git-lfs shellcheck
```

CUDA Toolkit은 WSL의 Windows NVIDIA 드라이버와 별개의 큰 시스템 변경입니다. `nvcc`가
필요한 연구가 확정되기 전에는 설치하지 않습니다.
