"""UTF-8 JSON 및 text artifact를 원자적으로 저장하는 최소 Phase 0 I/O 계층이다."""

from __future__ import annotations  # Python 3.12 지연 annotation 평가를 사용한다.

import os  # 같은 filesystem 안에서 atomic replace를 수행한다.
from pathlib import Path  # artifact 경로를 운영체제 독립적으로 처리한다.
from typing import Any  # JSON payload의 범용 타입을 표현한다.

from tokenization_premium.hashing import canonical_json_bytes  # JSON 저장 규칙을 hashing 규칙과 일치시킨다.


def write_json(path: Path, payload: Any) -> None:
    """
    /**
     * @purpose canonical UTF-8 JSON을 임시파일 후 atomic replace 방식으로 저장한다.
     * @spec_ref §30.2, §38
     * @param path 최종 JSON artifact 경로
     * @param payload JSON 직렬화 가능한 객체
     * @return None
     * @raises OSError 디렉터리 생성·쓰기·교체가 실패한 경우
     * @validation 저장 후 read_json 결과와 입력 payload의 exact equality를 검사한다.
     * @artifact outputs/manifests/*.json
     */
    """
    path.parent.mkdir(parents=True, exist_ok=True)  # 승인된 project output 경로만 idempotent하게 만든다.
    temporary = path.with_suffix(path.suffix + ".tmp")  # 불완전한 JSON이 최종 경로에 남지 않게 임시 경로를 정한다.
    temporary.write_bytes(canonical_json_bytes(payload))  # canonical bytes를 한 번에 기록한다.
    os.replace(temporary, path)  # 같은 filesystem에서 원자적으로 최종 파일로 교체한다.


def read_json(path: Path) -> Any:
    """
    /**
     * @purpose UTF-8 JSON artifact를 읽어 Python 객체로 복원한다.
     * @spec_ref §30.2
     * @param path 읽을 JSON artifact 경로
     * @return 복원된 JSON 객체
     * @raises FileNotFoundError 파일이 없는 경우
     * @raises json.JSONDecodeError JSON이 손상된 경우
     * @validation write_json roundtrip exact equality로 검사한다.
     * @artifact outputs/manifests/*.json
     */
    """
    import json  # JSON parser 의존성을 함수 실행 시점에 명시적으로 로드한다.

    return json.loads(path.read_text(encoding="utf-8"))  # 한글을 UTF-8로 복원해 객체를 반환한다.
