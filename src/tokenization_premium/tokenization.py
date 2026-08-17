"""o200k_base를 network fallback 없이 검증하는 Phase 0 tokenizer interface다."""

from __future__ import annotations  # Python 3.12 지연 annotation 평가를 사용한다.

import base64  # token bytes를 canonical text representation으로 변환한다.
import hashlib  # ranks와 regex의 SHA-256을 incremental하게 계산한다.
import os  # tiktoken cache 경로를 process 환경에 고정한다.
from pathlib import Path  # repository-local cache artifact를 처리한다.
from typing import Any  # tokenizer manifest mapping 타입을 표현한다.

import tiktoken  # SSOT의 primary Track A tokenizer 구현을 사용한다.

from tokenization_premium.hashing import canonical_json_bytes, sha256_file  # artifact와 mapping hash 규칙을 공유한다.

O200K_BASE_URL = "https://openaipublic.blob.core.windows.net/encodings/o200k_base.tiktoken"  # 승인된 공개 encoding artifact URL을 고정한다.
O200K_BASE_CACHE_KEY = "fb374d419588a4632f3f557e76b4b70aebbca790"  # tiktoken이 URL에서 계산하는 SHA-1 cache key를 고정한다.
O200K_BASE_SHA256 = "446a9538cb6c348e3516120d7c08b09f57c36495e2acfffe59a5bf8b0cfb1a2d"  # 구현이 선언한 raw artifact SHA-256을 고정한다.


def load_o200k_base_offline(cache_dir: Path) -> tiktoken.Encoding:
    """
    /**
     * @purpose 사전 provision된 o200k_base artifact만 사용해 encoding을 로드한다.
     * @spec_ref §14.1, §14.2, G3
     * @param cache_dir repository-local tiktoken cache 디렉터리
     * @return 검증된 o200k_base Encoding
     * @raises FileNotFoundError 승인된 raw artifact가 없는 경우
     * @raises ValueError raw artifact SHA가 고정값과 다른 경우
     * @validation 호출 전에 artifact 존재·hash를 검사하고 encoding name을 확인한다.
     * @artifact TOKENIZER_O200K_BASE_ARTIFACT_v001.json
     */
    """
    artifact = cache_dir / O200K_BASE_CACHE_KEY  # URL과 연결된 정확한 cache artifact 경로를 계산한다.
    if not artifact.is_file():  # tiktoken을 호출하기 전에 누락 여부를 fail-fast로 검사한다.
        raise FileNotFoundError(f"승인된 o200k_base artifact가 없습니다: {artifact}")  # 자동 network fallback 없이 실행을 중단한다.
    actual_sha256 = sha256_file(artifact)  # raw bytes의 실제 SHA-256을 계산한다.
    if actual_sha256 != O200K_BASE_SHA256:  # 손상되거나 교체된 artifact를 거부한다.
        raise ValueError(f"o200k_base SHA-256 불일치: {actual_sha256}")  # 기대 hash와 다른 encoding 사용을 중단한다.
    os.environ["TIKTOKEN_CACHE_DIR"] = str(cache_dir)  # 검증된 repository-local cache만 tiktoken에 노출한다.
    encoding = tiktoken.get_encoding("o200k_base")  # 검증 완료 후 local cache에서 primary encoding을 구성한다.
    if encoding.name != "o200k_base":  # registry 오염이나 잘못된 encoding 반환을 방지한다.
        raise ValueError(f"예상하지 못한 encoding: {encoding.name}")  # 잘못된 tokenizer로 측정이 이어지지 않게 한다.
    return encoding  # 검증된 encoding 객체를 반환한다.


def mergeable_ranks_sha256(encoding: tiktoken.Encoding) -> str:
    """
    /**
     * @purpose mergeable rank mapping을 rank·token bytes 순서의 binary 규약으로 hash한다.
     * @spec_ref §12.4, §14.2, G3
     * @param encoding 검증된 o200k_base Encoding
     * @return canonical mergeable ranks SHA-256
     * @raises AttributeError tiktoken 구현이 audit mapping을 제공하지 않는 경우
     * @validation rank 수와 unique rank/token 조건을 별도 assertion한다.
     * @artifact TOKENIZER_O200K_BASE_ARTIFACT_v001.json
     */
    """
    ranks: dict[bytes, int] = encoding._mergeable_ranks  # 공개 구현의 audit 대상 mapping을 명시적으로 읽는다.
    digest = hashlib.sha256()  # canonical binary stream의 SHA-256 상태를 초기화한다.
    for token, rank in sorted(ranks.items(), key=lambda item: (item[1], item[0])):  # filesystem이나 dict 삽입 순서를 제거한다.
        digest.update(rank.to_bytes(8, "big", signed=False))  # rank를 고정 폭 unsigned big-endian으로 기록한다.
        digest.update(len(token).to_bytes(4, "big", signed=False))  # token 경계를 보존하기 위해 byte 길이를 기록한다.
        digest.update(token)  # 원본 mergeable token bytes를 그대로 반영한다.
    return digest.hexdigest()  # canonical mapping digest를 반환한다.


def tokenizer_manifest(encoding: tiktoken.Encoding, cache_dir: Path) -> dict[str, Any]:
    """
    /**
     * @purpose raw encoding, ranks, pat_str, special token mapping의 provenance를 생성한다.
     * @spec_ref §12.4, §14.2, §30.1, G3
     * @param encoding 검증된 o200k_base Encoding
     * @param cache_dir repository-local cache 디렉터리
     * @return tokenizer artifact metadata mapping
     * @raises AttributeError 필요한 공개 구현 audit attribute가 없는 경우
     * @validation 각 hash가 64자리이고 rank/special-token 수가 기대 범위인지 검사한다.
     * @artifact TOKENIZER_O200K_BASE_ARTIFACT_v001.json
     */
    """
    artifact = cache_dir / O200K_BASE_CACHE_KEY  # manifest에 기록할 raw artifact를 선택한다.
    special_tokens: dict[str, int] = encoding._special_tokens  # special-token mapping을 별도 hash하기 위해 읽는다.
    audit_sample = [{"rank": rank, "token_base64": base64.b64encode(token).decode("ascii")} for token, rank in sorted(encoding._mergeable_ranks.items(), key=lambda item: item[1])[:5]]  # 최소 rank sample을 사람이 검토 가능한 형태로 만든다.
    return {  # SSOT D-04에서 요구한 tokenizer provenance를 구조화한다.
        "schema_version": "tokenizer-artifact-v1",  # manifest schema evolution을 추적한다.
        "tokenizer_id": encoding.name,  # Track A primary tokenizer ID를 기록한다.
        "tiktoken_version": tiktoken.__version__,  # 실제 실행 package version을 기록한다.
        "encoding_source_url": O200K_BASE_URL,  # raw artifact 출처를 기록한다.
        "encoding_cache_key_sha1": O200K_BASE_CACHE_KEY,  # URL과 local artifact의 연결 키를 기록한다.
        "encoding_file_size_bytes": artifact.stat().st_size,  # raw artifact byte size를 기록한다.
        "encoding_file_sha256": sha256_file(artifact),  # raw artifact SHA-256을 기록한다.
        "mergeable_ranks_count": len(encoding._mergeable_ranks),  # canonical mapping row count를 기록한다.
        "mergeable_ranks_hash": mergeable_ranks_sha256(encoding),  # canonical rank mapping SHA-256을 기록한다.
        "pat_str_sha256": hashlib.sha256(encoding._pat_str.encode("utf-8")).hexdigest(),  # regex pattern bytes의 SHA-256을 기록한다.
        "special_tokens_count": len(special_tokens),  # special-token mapping row count를 기록한다.
        "special_tokens_hash": hashlib.sha256(canonical_json_bytes(special_tokens)).hexdigest(),  # canonical JSON mapping SHA-256을 기록한다.
        "audit_sample": audit_sample,  # 공개 가능한 최소 token byte sample을 기록한다.
        "network_fallback_allowed": False,  # notebook 실행 중 network 접근을 금지한 사실을 기록한다.
    }  # tokenizer provenance mapping을 반환한다.


def validate_roundtrip(encoding: tiktoken.Encoding, samples: list[str]) -> list[dict[str, Any]]:
    """
    /**
     * @purpose 고정 KO/EN/Unicode sample의 encode-decode exact roundtrip을 검증한다.
     * @spec_ref §14.2, §25.4, G3
     * @param encoding 검증된 o200k_base Encoding
     * @param samples 원문 보존을 검사할 고정 문자열 목록
     * @return sample별 token count와 roundtrip 상태 행 목록
     * @raises AssertionError 하나라도 roundtrip이 실패하거나 token count가 0인 경우
     * @validation 모든 row의 roundtrip_ok가 True인지 집계한다.
     * @artifact TOKENIZER_O200K_BASE_ARTIFACT_v001.json
     */
    """
    rows: list[dict[str, Any]] = []  # sample 한 개당 한 행인 검증 결과를 누적한다.
    for sample_id, text in enumerate(samples):  # 입력 순서를 고정 sample ID로 보존한다.
        token_ids = encoding.encode(text)  # special token 없는 raw analysis text를 encode한다.
        decoded = encoding.decode(token_ids)  # 같은 encoding으로 token ID를 문자열로 복원한다.
        token_bytes = b"".join(encoding.decode_single_token_bytes(token_id) for token_id in token_ids)  # token byte 경계를 합쳐 UTF-8 원문 bytes와 비교한다.
        roundtrip_ok = decoded == text and token_bytes == text.encode("utf-8")  # 문자열과 byte 두 경로가 모두 정확한지 검사한다.
        if not token_ids or not roundtrip_ok:  # zero-token 또는 원문 손실을 fail-fast로 거부한다.
            raise AssertionError(f"Tokenizer roundtrip 실패: sample_id={sample_id}")  # G3 위반 sample을 명확히 표시한다.
        rows.append({"sample_id": sample_id, "text": text, "token_count": len(token_ids), "roundtrip_ok": roundtrip_ok})  # sample 결과를 manifest에 추가한다.
    return rows  # 100% PASS가 확인된 sample 결과를 반환한다.
