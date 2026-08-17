from __future__ import annotations  # Python 3.12 지연 annotation 평가를 사용한다.

import sys  # 실행 interpreter의 major/minor version을 검사한다.

import numpy as np  # sparse matrix의 dense 변환 타입을 검사한다.
import pandas as pd  # tabular package import와 기본 DataFrame shape를 검사한다.
from sklearn.feature_extraction.text import TfidfVectorizer  # scikit-learn text feature smoke를 수행한다.

from tokenization_premium import __version__  # canonical package namespace와 version export를 검사한다.


def test_python_and_package_contract() -> None:
    """
    /**
     * @purpose Python 3.12와 canonical package import 계약을 검사한다.
     * @spec_ref §30.1, §36
     * @return None
     * @raises AssertionError interpreter 또는 package version 계약이 깨진 경우
     * @validation sys.version_info와 package export를 직접 비교한다.
     * @artifact pytest result
     */
    """
    assert sys.version_info[:2] == (3, 12)  # project가 고정한 Python major/minor를 확인한다.
    assert __version__  # package metadata가 비어 있지 않은지 확인한다.


def test_tabular_and_tokenization_smoke() -> None:
    """
    /**
     * @purpose pandas와 scikit-learn의 최소 tabular/text dependency 호환성을 검사한다.
     * @spec_ref §30.1
     * @return None
     * @raises AssertionError DataFrame 또는 sparse feature shape가 예상과 다른 경우
     * @validation 고정 2행 corpus의 exact shape를 비교한다.
     * @artifact pytest result
     */
    """
    frame = pd.DataFrame({"text": ["token premium", "premium research"]})  # 고정 2행 dependency smoke 입력을 만든다.
    matrix = TfidfVectorizer().fit_transform(frame["text"])  # 연구 측정과 분리된 최소 TF-IDF 연산을 실행한다.
    assert frame.shape == (2, 1)  # DataFrame grain과 column 수를 확인한다.
    assert isinstance(matrix.toarray(), np.ndarray)  # SciPy sparse 결과가 NumPy로 변환되는지 확인한다.
    assert matrix.shape == (2, 3)  # 고정 vocabulary에서 예상 feature shape를 확인한다.
