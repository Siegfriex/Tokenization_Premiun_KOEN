"""Phase-4 D-04 o200k_base tokenizer measurement (NB05) 엔지니어링 구현.

SSOT 범위: 고정된 tiktoken o200k_base 구현으로 pair-level token count와
Tokenization Premium(TP)의 정확한 가법적 분해(logTP = logCR + logBDR + logCP)만
측정한다. 형태소(NB04), regex chunk mechanism(NB06), 통계적 추론, 모델링은
이 모듈의 범위 밖이다.

이 모듈은 light scaffold다: full population execution은 여기서 하지 않는다.
"""

from __future__ import annotations

import math
from typing import Any

import tiktoken

TOKENIZER_MEASUREMENT_RULE_VERSION = "tok_meas_v001"  # 이 측정 규칙의 고정 버전 문자열이다.
EXACT_DECOMPOSITION_EPSILON = 1e-10  # logTP = logCR + logBDR + logCP identity의 허용 오차다.


def _token_count_and_roundtrip(text: str, encoding: tiktoken.Encoding) -> tuple[int, bool]:
    """text를 encode/decode해 token count와 roundtrip 성공 여부를 함께 계산한다."""
    tokens = encoding.encode(text)
    roundtrip_ok = encoding.decode(tokens) == text
    return len(tokens), roundtrip_ok


def pair_token_measurement(ko_text: str, en_text: str, *, encoding: tiktoken.Encoding) -> dict[str, Any]:
    """
    /**
     * @purpose 의미 대응 KO/EN pair에서 T_KO/T_EN, TP, 그리고 CodePointRatio/ByteDensityRatio/
     *          CompressionPenalty로의 정확한 log 가법적 분해를 계산한다.
     * @spec_ref SSOT §(logTP = logCodePointRatio + logByteDensityRatio + logCompressionPenalty); Directive Task 11
     * @param ko_text ko_text_analysis 문자열 (accepted cohort는 empty 불가)
     * @param en_text en_text_analysis 문자열 (accepted cohort는 empty 불가)
     * @param encoding 검증된 o200k_base tiktoken.Encoding (load_o200k_base_offline 결과)
     * @return T_KO/T_EN/TP/logTP/CodePointRatio/ByteDensityRatio/CompressionPenalty/roundtrip_ok/identity_abs_error
     * @raises ValueError 빈 문자열이 전달된 경우
     * @validation abs(logTP - (logCR+logBDR+logCP)) < 1e-10 을 단위 테스트로 검사한다.
     * @artifact 향후 TOKEN_MEASUREMENTS_O200K_v001.parquet (full population은 이 스캐폴드의 범위 밖)
     */
    """
    if ko_text == "" or en_text == "":
        raise ValueError("accepted cohort의 텍스트는 empty일 수 없다: pair_token_measurement는 빈 문자열을 거부한다")

    ko_codepoints, en_codepoints = len(ko_text), len(en_text)
    ko_bytes, en_bytes = len(ko_text.encode("utf-8")), len(en_text.encode("utf-8"))
    t_ko, ko_roundtrip_ok = _token_count_and_roundtrip(ko_text, encoding)
    t_en, en_roundtrip_ok = _token_count_and_roundtrip(en_text, encoding)

    tp = t_ko / t_en
    code_point_ratio = ko_codepoints / en_codepoints
    byte_density_ratio = (ko_bytes / ko_codepoints) / (en_bytes / en_codepoints)
    compression_penalty = (t_ko / ko_bytes) / (t_en / en_bytes)

    log_tp = math.log(tp)
    log_cr = math.log(code_point_ratio)
    log_bdr = math.log(byte_density_ratio)
    log_cp = math.log(compression_penalty)
    identity_abs_error = abs(log_tp - (log_cr + log_bdr + log_cp))

    return {
        "T_KO": t_ko,
        "T_EN": t_en,
        "token_difference": t_ko - t_en,
        "TP": tp,
        "logTP": log_tp,
        "CodePointRatio": code_point_ratio,
        "ByteDensityRatio": byte_density_ratio,
        "CompressionPenalty": compression_penalty,
        "logCodePointRatio": log_cr,
        "logByteDensityRatio": log_bdr,
        "logCompressionPenalty": log_cp,
        "identity_abs_error": identity_abs_error,
        "roundtrip_ok": ko_roundtrip_ok and en_roundtrip_ok,
    }


__all__ = [
    "EXACT_DECOMPOSITION_EPSILON",
    "TOKENIZER_MEASUREMENT_RULE_VERSION",
    "pair_token_measurement",
]
