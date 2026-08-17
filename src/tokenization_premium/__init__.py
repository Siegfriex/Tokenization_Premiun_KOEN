"""Tokenization Premium 연구 재현성 유틸리티를 공개한다."""

from importlib.metadata import PackageNotFoundError, version  # 설치된 배포판 버전을 안전하게 조회한다.

try:  # editable install 여부와 무관하게 실제 배포판 버전을 우선 사용한다.
    __version__ = version("tokenization-premium")  # 환경 manifest에 기록할 패키지 버전을 읽는다.
except PackageNotFoundError:  # src 경로만 직접 사용하는 환경도 import 가능하게 유지한다.
    __version__ = "0.1.0"  # 설치 전 bootstrap 상태의 명시적인 fallback 버전을 사용한다.

__all__ = ["__version__"]  # 외부에 노출하는 최소 공개 API를 고정한다.
