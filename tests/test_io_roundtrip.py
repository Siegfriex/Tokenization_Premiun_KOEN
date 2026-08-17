"""한국어 UTF-8 JSON과 Parquet roundtrip 계약을 검사한다."""

import pandas as pd  # 한글 tabular Parquet roundtrip을 수행한다.

from tokenization_premium.io import read_json, write_json  # canonical JSON I/O를 검사한다.
from tokenization_premium.paths import PROJECT_ROOT  # test artifact를 project root 내부에 제한한다.


def test_korean_json_roundtrip() -> None:
    """
    /**
     * @purpose 한글 JSON을 ASCII escape 없이 저장하고 exact roundtrip하는지 검사한다.
     * @spec_ref §30.2, Notebook Constitution §6
     * @return None
     * @raises AssertionError payload 또는 저장 text가 기대와 다른 경우
     * @validation 입력과 read_json 결과의 exact equality를 비교한다.
     * @artifact .runtime/test_outputs/korean_roundtrip.json
     */
    """
    path = PROJECT_ROOT / ".runtime" / "test_outputs" / "korean_roundtrip.json"  # project 내부 ignored JSON 경로를 선택한다.
    payload = {"언어": "한국어", "검증": True, "행수": 2}  # 한글과 scalar dtype을 포함한 고정 payload를 만든다.
    write_json(path, payload)  # canonical UTF-8 JSON으로 저장한다.
    assert read_json(path) == payload  # 저장 전후 객체가 정확히 같은지 확인한다.
    assert "한국어" in path.read_text(encoding="utf-8")  # 한글이 ASCII escape로 변환되지 않았는지 확인한다.


def test_korean_parquet_roundtrip() -> None:
    """
    /**
     * @purpose 한글 DataFrame의 value, dtype, shape를 Parquet에서 보존하는지 검사한다.
     * @spec_ref §30.2, Notebook Constitution §4, §6
     * @return None
     * @raises AssertionError Parquet roundtrip 결과가 원본과 다른 경우
     * @validation pandas testing exact frame equality를 사용한다.
     * @artifact .runtime/test_outputs/korean_roundtrip.parquet
     */
    """
    path = PROJECT_ROOT / ".runtime" / "test_outputs" / "korean_roundtrip.parquet"  # project 내부 ignored Parquet 경로를 선택한다.
    frame = pd.DataFrame({"sample_id": [1, 2], "text": ["한국어", "English"], "valid": [True, False]})  # grain=sample, PK=sample_id인 고정 2행 표를 만든다.
    frame.to_parquet(path, index=False)  # index를 artifact schema에 섞지 않고 Parquet으로 저장한다.
    restored = pd.read_parquet(path)  # 같은 engine으로 저장 artifact를 다시 읽는다.
    pd.testing.assert_frame_equal(restored, frame)  # value, column order, dtype, shape를 정확히 비교한다.
