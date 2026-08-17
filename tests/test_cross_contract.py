"""G0 연구·구현 교차 계약과 Track B 실행 차단 상태를 검사한다."""

from __future__ import annotations  # Python 3.12 지연 annotation 평가를 사용한다.

import pytest  # integration 전 Claude-owned config 부재를 명시적 skip으로 표현한다.

from tokenization_premium.contracts import ContractValidationError, load_yaml_mapping, validate_cross_contract_files, validate_cross_contracts, validate_engineering_contracts, validate_package_namespace  # 공개 cross-contract API를 검사한다.
from tokenization_premium.paths import PROJECT_ROOT  # 실제 worktree의 config와 pyproject 경로를 선택한다.


def _valid_contract_mappings() -> tuple[dict[str, object], dict[str, object], dict[str, object], dict[str, object]]:
    """
    /**
     * @purpose 연구 수치를 재정의하지 않고 cross-contract 구조 단위 테스트용 mapping을 제공한다.
     * @spec_ref D-RD-01, D-RD-03
     * @return research, morphology, tokenizer, serving 최소 mapping tuple
     * @raises None
     * @validation validate_cross_contracts의 PASS와 mutation FAIL test가 함께 사용한다.
     * @artifact pytest result
     */
    """
    research: dict[str, object] = {"seed_policy": {"master_seed": 1, "split": 2, "bootstrap": 3, "model_tuning": 4, "serving": 5, "auxiliary": 6}, "track_b_status": {"status": "DEFERRED_NOT_EXECUTED"}}  # key/type 계약만 검증하는 비연구 synthetic seed를 만든다.
    morphology: dict[str, object] = {"analyzer": {"primary_name": "Kiwi", "primary_package": "kiwipiepy", "design_freeze_version": "0.23.2"}}  # SSOT analyzer identity/version fixture를 만든다.
    tokenizer: dict[str, object] = {"track": "A", "tokenizer_id": "o200k_base", "implementation": "tiktoken", "package_version": "0.13.0", "network_fallback_allowed": False}  # Track A exact implementation fixture를 만든다.
    serving: dict[str, object] = {  # concrete endpoint/model을 만들지 않은 deferred fixture를 구성한다.
        "track": "B",  # Track A와 분리된 serving track을 지정한다.
        "execution_status": "deferred",  # 현재 비실행 상태를 지정한다.
        "enabled_in_phase_0": False,  # Phase 0 실행 비활성 상태를 지정한다.
        "execution_permissions": {"model_download_allowed": False, "local_inference_allowed": False, "hosted_api_call_allowed": False, "serving_benchmark_allowed": False, "gpu_serving_setup_allowed": False},  # 모든 금지 동작을 false로 지정한다.
        "deployment": {"baseline_if_reactivated": "hugging_face_hosted_api"},  # 재개 시 hosted API baseline만 지정한다.
        "research_contract": {"track_b_status_path": "track_b_status.status", "serving_seed_path": "seed_policy.serving"},  # Claude-owned status/seed key reference를 지정한다.
    }  # Track B deferred fixture mapping을 닫는다.
    return research, morphology, tokenizer, serving  # 독립 mutation을 위해 새 mapping tuple을 반환한다.


def test_owned_engineering_contracts() -> None:
    """
    /**
     * @purpose 실제 Codex 소유 tokenizer/serving config가 Track 분리와 비실행 계약을 지키는지 검사한다.
     * @spec_ref §14, §26, D-RD-03
     * @return None
     * @raises AssertionError 실제 config가 PASS가 아닌 경우
     * @validation repository config를 직접 읽고 validator 결과를 비교한다.
     * @artifact pytest result
     */
    """
    tokenizer = load_yaml_mapping(PROJECT_ROOT / "configs" / "tokenizer_v1.yaml")  # 실제 Track A config를 UTF-8로 읽는다.
    serving = load_yaml_mapping(PROJECT_ROOT / "configs" / "serving_v1.yaml")  # 실제 Track B config를 UTF-8로 읽는다.
    result = validate_engineering_contracts(tokenizer, serving)  # owned config의 exact 계약을 검증한다.
    assert result["status"] == "PASS"  # machine-readable 최종 상태를 확인한다.
    assert all(value is False for value in result["execution_permissions"].values())  # 모든 Track B 실행 경로가 닫혔는지 확인한다.


def test_cross_contract_structure_and_namespace() -> None:
    """
    /**
     * @purpose seed key, tokenizer, Kiwi, Track 상태와 canonical namespace 구조를 검사한다.
     * @spec_ref D-RD-01, D-RD-03, §36
     * @return None
     * @raises AssertionError validator 결과가 PASS가 아닌 경우
     * @validation synthetic mapping과 실제 pyproject를 함께 검사한다.
     * @artifact pytest result
     */
    """
    research, morphology, tokenizer, serving = _valid_contract_mappings()  # numeric semantics와 분리된 최소 구조 fixture를 만든다.
    result = validate_cross_contracts(research, morphology, tokenizer, serving)  # 네 mapping의 상호계약을 검사한다.
    namespace = validate_package_namespace(PROJECT_ROOT / "pyproject.toml")  # 실제 build namespace를 검사한다.
    assert result["status"] == "PASS"  # cross-contract 구조가 완전한지 확인한다.
    assert namespace == {"status": "PASS", "namespace": "tokenization_premium"}  # koen_tp alias 없는 단일 namespace를 확인한다.


def test_track_b_permission_cannot_be_enabled() -> None:
    """
    /**
     * @purpose deferred 상태에서 accidental HF API 또는 serving 실행 permission을 fail-fast 차단한다.
     * @spec_ref D-RD-03
     * @return None
     * @raises AssertionError validator가 열린 permission을 허용한 경우
     * @validation hosted_api_call_allowed만 true로 mutation해 오류를 확인한다.
     * @artifact pytest result
     */
    """
    _, _, tokenizer, serving = _valid_contract_mappings()  # valid engineering fixture를 준비한다.
    permissions = serving["execution_permissions"]  # mutation할 nested permission mapping을 선택한다.
    assert isinstance(permissions, dict)  # fixture 구조 오류와 validator 오류를 구분한다.
    permissions["hosted_api_call_allowed"] = True  # D-RD-03이 금지한 API 실행 경로를 의도적으로 연다.
    with pytest.raises(ContractValidationError, match="permission"):  # validator가 위반을 명시적으로 거부하는지 검사한다.
        validate_engineering_contracts(tokenizer, serving)  # 손상된 serving config를 검증한다.


def test_integrated_claude_contract_when_present() -> None:
    """
    /**
     * @purpose Claude-owned config가 merge된 integration branch에서 실제 파일 교차 검사를 자동 실행한다.
     * @spec_ref D-RD-02, G0 cross-agent validation
     * @return None
     * @raises AssertionError 통합 config가 상호계약을 위반한 경우
     * @validation impl branch에서는 명시적 skip, integration branch에서는 strict PASS를 요구한다.
     * @artifact pytest result
     */
    """
    claude_paths = [PROJECT_ROOT / "configs" / "research_v1.yaml", PROJECT_ROOT / "configs" / "morphology_v1.yaml"]  # Claude-owned integration dependency를 열거한다.
    if not all(path.is_file() for path in claude_paths):  # agent branch에 연구 config가 아직 없으면 통합 검사를 실행할 수 없다.
        pytest.skip("Claude-owned research/morphology config가 아직 impl branch에 통합되지 않았습니다.")  # 미통합 상태를 PASS로 가장하지 않고 skip한다.
    result = validate_cross_contract_files(PROJECT_ROOT)  # 실제 네 config와 pyproject를 strict 검증한다.
    assert result["status"] == "PASS"  # 통합 branch의 cross-contract gate를 확인한다.
