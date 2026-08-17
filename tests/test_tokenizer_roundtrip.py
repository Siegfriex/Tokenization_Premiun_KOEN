"""o200k_base offline artifact와 raw-text roundtrip 계약을 검사한다."""

from tokenization_premium.paths import PROJECT_ROOT  # repository-local tokenizer cache를 찾는다.
from tokenization_premium.tokenization import load_o200k_base_offline, tokenizer_manifest, validate_roundtrip  # G3 Phase 0 API를 검사한다.


def test_o200k_base_offline_roundtrip() -> None:
    """
    /**
     * @purpose 고정 o200k_base artifact에서 KO/EN raw text roundtrip 100%를 검사한다.
     * @spec_ref §14.2, §25.4, G3
     * @return None
     * @raises FileNotFoundError 승인 artifact가 provision되지 않은 경우
     * @raises AssertionError roundtrip 또는 hash 계약이 깨진 경우
     * @validation 모든 fixed sample의 roundtrip_ok와 manifest hash를 검사한다.
     * @artifact pytest result
     */
    """
    cache_dir = PROJECT_ROOT / ".runtime" / "tiktoken-cache"  # network fallback이 금지된 project-local cache를 선택한다.
    encoding = load_o200k_base_offline(cache_dir)  # 존재·raw SHA 검증 후 o200k_base를 로드한다.
    samples = ["한국어 토큰화", "English tokenization", "공백  두 개\n줄바꿈", "emoji 😀 123"]  # corpus와 무관한 고정 smoke 문자열을 정의한다.
    rows = validate_roundtrip(encoding, samples)  # raw text encode/decode와 token bytes를 함께 검사한다.
    manifest = tokenizer_manifest(encoding, cache_dir)  # ranks, regex, special-token hash를 계산한다.
    assert len(rows) == len(samples)  # 모든 입력 sample이 검증되었는지 확인한다.
    assert all(row["roundtrip_ok"] for row in rows)  # roundtrip pass rate가 100%인지 확인한다.
    assert manifest["encoding_file_sha256"] == "446a9538cb6c348e3516120d7c08b09f57c36495e2acfffe59a5bf8b0cfb1a2d"  # SSOT와 구현이 고정한 raw artifact를 확인한다.
