"""Release-critical 파일과 canonical 객체의 SHA-256을 계산한다."""

from __future__ import annotations  # Python 3.12의 지연 annotation 평가를 사용한다.

import hashlib  # 재현성 manifest에 사용할 SHA-256 digest를 계산한다.
import json  # mapping을 결정론적인 UTF-8 JSON으로 직렬화한다.
from pathlib import Path  # 파일 경로를 운영체제 독립적으로 처리한다.
from typing import Any  # JSON 직렬화 가능한 payload의 타입을 표현한다.


def canonical_json_bytes(payload: Any) -> bytes:
    """
    /**
     * @purpose JSON payload를 key 정렬·UTF-8·LF 규칙으로 canonical 직렬화한다.
     * @spec_ref §30.2, §38
     * @param payload JSON 직렬화 가능한 객체
     * @return canonical UTF-8 JSON bytes
     * @raises TypeError JSON 직렬화가 불가능한 값이 포함된 경우
     * @validation 같은 의미의 key 순서가 다른 mapping이 동일 bytes를 생성하는지 검사한다.
     * @artifact 모든 JSON manifest
     */
    """
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"  # 표현 차이를 제거한 JSON 문자열을 만든다.
    return text.encode("utf-8")  # 한글을 손실 없이 저장할 UTF-8 bytes를 반환한다.


def sha256_bytes(data: bytes) -> str:
    """
    /**
     * @purpose 주어진 bytes의 SHA-256 hex digest를 계산한다.
     * @spec_ref §30.2, §38
     * @param data 해시할 원본 bytes
     * @return 64자리 소문자 SHA-256 hex digest
     * @raises TypeError bytes가 아닌 값이 전달된 경우
     * @validation hashlib 기준 digest와 일치하는지 단위 테스트한다.
     * @artifact artifact hash fields
     */
    """
    return hashlib.sha256(data).hexdigest()  # 원본 bytes를 변경하지 않고 SHA-256을 반환한다.


def sha256_file(path: Path) -> str:
    """
    /**
     * @purpose 파일 전체 bytes의 SHA-256을 streaming 방식으로 계산한다.
     * @spec_ref §14.2, §15.1, §30.2, §38
     * @param path 해시할 파일 경로
     * @return 64자리 소문자 SHA-256 hex digest
     * @raises FileNotFoundError 대상 파일이 없는 경우
     * @validation sha256sum CLI 결과와 교차 확인한다.
     * @artifact tokenizer/model/environment manifest
     */
    """
    digest = hashlib.sha256()  # 파일 전체 내용을 누적할 SHA-256 상태를 초기화한다.
    with path.open("rb") as stream:  # newline 변환 없이 원본 bytes를 읽는다.
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):  # 큰 파일도 메모리를 과도하게 사용하지 않도록 1 MiB씩 읽는다.
            digest.update(chunk)  # 읽은 순서대로 digest 상태에 bytes를 반영한다.
    return digest.hexdigest()  # 최종 64자리 digest를 반환한다.


def file_inventory(paths: list[Path], base: Path) -> list[dict[str, Any]]:
    """
    /**
     * @purpose 파일 목록을 relative path, size, SHA-256 manifest로 변환한다.
     * @spec_ref §15.1, §30.2, §38
     * @param paths inventory 대상 파일 경로 목록
     * @param base relative path의 기준 디렉터리
     * @return path 기준 정렬된 파일 metadata 행 목록
     * @raises ValueError 파일이 base 바깥에 있으면 발생
     * @validation row count와 실제 파일 수, 각 개별 SHA-256을 검사한다.
     * @artifact model/package file inventory
     */
    """
    rows: list[dict[str, Any]] = []  # 파일 한 개당 한 행인 manifest를 누적한다.
    for path in sorted(paths):  # 파일시스템 열거 순서에 의존하지 않도록 경로를 정렬한다.
        relative = path.relative_to(base).as_posix()  # machine-specific absolute path를 제거한다.
        rows.append({"path": relative, "size_bytes": path.stat().st_size, "sha256": sha256_file(path)})  # 재현 검증에 필요한 최소 metadata를 기록한다.
    return rows  # 결정론적으로 정렬된 inventory를 반환한다.
