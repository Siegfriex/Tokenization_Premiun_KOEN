"""Canonical JSON과 파일 SHA-256 규약을 검사한다."""


from tokenization_premium.hashing import canonical_json_bytes, sha256_file  # release hash API를 검사한다.
from tokenization_premium.paths import PROJECT_ROOT  # 모든 test artifact를 project root 안에 제한한다.


def test_canonical_json_is_key_order_independent() -> None:
    """
    /**
     * @purpose mapping 입력 순서가 canonical JSON bytes에 영향을 주지 않는지 검사한다.
     * @spec_ref §30.2, §38
     * @return None
     * @raises AssertionError canonical 직렬화 규칙이 깨진 경우
     * @validation 서로 다른 key 입력 순서의 exact byte equality를 비교한다.
     * @artifact pytest result
     */
    """
    first = canonical_json_bytes({"한글": 1, "english": 2})  # 첫 번째 key 순서의 UTF-8 payload를 직렬화한다.
    second = canonical_json_bytes({"english": 2, "한글": 1})  # 반대 key 순서의 동일 payload를 직렬화한다.
    assert first == second  # key 입력 순서가 digest에 영향을 주지 않는지 확인한다.
    assert first.endswith(b"\n")  # canonical JSON이 단일 LF로 끝나는지 확인한다.


def test_file_hash_uses_exact_bytes() -> None:
    """
    /**
     * @purpose sha256_file이 UTF-8 파일의 원본 bytes를 정확히 hash하는지 검사한다.
     * @spec_ref §30.2, §38
     * @return None
     * @raises AssertionError known digest와 다른 경우
     * @validation hashlib known digest를 고정값으로 비교한다.
     * @artifact .runtime/test_outputs/hash_input.txt
     */
    """
    path = PROJECT_ROOT / ".runtime" / "test_outputs" / "hash_input.txt"  # project 내부 ignored test 경로를 선택한다.
    path.parent.mkdir(parents=True, exist_ok=True)  # 외부 temporary directory 없이 test 경로를 만든다.
    path.write_text("한글\n", encoding="utf-8")  # 고정 UTF-8 bytes를 저장한다.
    assert sha256_file(path) == "712f4b5a23ccde2c6cacfa46258849855f00be71873bb8e377132b8436030684"  # known SHA-256과 비교한다.
