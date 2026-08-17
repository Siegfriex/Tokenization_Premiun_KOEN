"""Claude 연구 계약과 Codex 구현 계약을 읽기 전용으로 교차 검증한다."""

from __future__ import annotations  # Python 3.12 지연 annotation 평가를 사용한다.

import tomllib  # pyproject의 canonical package namespace를 표준 라이브러리로 읽는다.
from collections.abc import Mapping  # YAML mapping의 읽기 전용 구조 타입을 표현한다.
from pathlib import Path  # repository-relative 계약 파일 경로를 안전하게 처리한다.
from typing import Any  # 구조화된 검사 결과의 heterogeneous value 타입을 표현한다.

import yaml  # Claude/Codex 소유 YAML 계약을 변경 없이 파싱한다.

from tokenization_premium.hashing import sha256_file  # 입력 계약 파일의 exact bytes provenance를 기록한다.


class ContractValidationError(ValueError):
    """
    /**
     * @purpose 교차 계약의 누락·충돌을 일반 입력 오류와 구분해 fail-fast 보고한다.
     * @spec_ref D-RD-01, D-RD-03, Cross-contract validation
     * @return None
     * @raises None 이 class 자체는 validation 함수에서 발생시킨다.
     * @validation 의도적으로 손상된 mapping을 사용하는 단위 테스트로 검사한다.
     * @artifact pytest result, ENVIRONMENT_REPRO_v001.json
     */
    """


def load_yaml_mapping(path: Path) -> dict[str, Any]:
    """
    /**
     * @purpose 소유권이 다른 YAML 계약을 수정 없이 UTF-8 mapping으로 읽는다.
     * @spec_ref §30.2, D-RD-01
     * @param path 읽을 YAML 파일의 project 내부 경로
     * @return YAML root mapping
     * @raises FileNotFoundError 계약 파일이 아직 branch에 통합되지 않은 경우
     * @raises ContractValidationError YAML root가 mapping이 아니거나 문법이 잘못된 경우
     * @validation 실제 config와 비정상 fixture를 모두 검사한다.
     * @artifact ENVIRONMENT_REPRO_v001.json
     */
    """
    try:  # YAML parser 오류를 계약 전용 오류로 변환하기 위해 경계를 둔다.
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))  # source bytes를 변경하지 않고 UTF-8로 파싱한다.
    except yaml.YAMLError as error:  # 문법 오류를 file path와 함께 보고한다.
        raise ContractValidationError(f"YAML parse 실패: {path}: {error}") from error  # 후속 분석이 진행되지 않도록 즉시 중단한다.
    if not isinstance(payload, dict):  # top-level mapping이 아니면 key-path 계약을 검증할 수 없다.
        raise ContractValidationError(f"YAML root는 mapping이어야 합니다: {path}")  # 모호한 scalar/list config를 거부한다.
    return payload  # 원본 mapping을 수정하지 않고 반환한다.


def _required_path(mapping: Mapping[str, Any], dotted_path: str) -> Any:
    """
    /**
     * @purpose 중첩 계약 key를 점 표기법으로 조회하고 누락을 fail-fast 처리한다.
     * @spec_ref D-RD-01, Cross-contract validation
     * @param mapping 읽기 전용 계약 mapping
     * @param dotted_path 예: seed_policy.serving
     * @return 지정 key의 값
     * @raises ContractValidationError 중간 또는 최종 key가 누락된 경우
     * @validation required seed key 누락 fixture로 검사한다.
     * @artifact pytest result
     */
    """
    current: Any = mapping  # root mapping에서 탐색을 시작한다.
    for key in dotted_path.split("."):  # 점으로 구분된 각 계층을 순서대로 방문한다.
        if not isinstance(current, Mapping) or key not in current:  # 현재 계층이 mapping이 아니거나 key가 없으면 계약 위반이다.
            raise ContractValidationError(f"required config key 누락: {dotted_path}")  # 누락된 전체 경로를 보고하고 중단한다.
        current = current[key]  # 다음 계층 또는 최종 값으로 이동한다.
    return current  # 조회한 값을 변경 없이 반환한다.


def validate_package_namespace(pyproject_path: Path) -> dict[str, str]:
    """
    /**
     * @purpose build target이 tokenization_premium 단일 namespace만 배포하는지 검증한다.
     * @spec_ref Research Director namespace decision, §36
     * @param pyproject_path pyproject.toml 경로
     * @return PASS 상태와 canonical namespace mapping
     * @raises ContractValidationError koen_tp alias 또는 다른 package target이 설정된 경우
     * @validation 실제 pyproject build package 목록을 exact 비교한다.
     * @artifact ENVIRONMENT_REPRO_v001.json
     */
    """
    pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))  # pyproject를 표준 TOML parser로 읽는다.
    packages = _required_path(pyproject, "tool.hatch.build.targets.wheel.packages")  # 실제 wheel package source 목록을 조회한다.
    if packages != ["src/tokenization_premium"]:  # dual package나 SSOT 표기의 잘못된 구현 적용을 거부한다.
        raise ContractValidationError(f"canonical package namespace 위반: {packages!r}")  # 관측한 package 목록을 오류에 포함한다.
    return {"status": "PASS", "namespace": "tokenization_premium"}  # machine-readable namespace 결과를 반환한다.


def validate_engineering_contracts(tokenizer: Mapping[str, Any], serving: Mapping[str, Any]) -> dict[str, Any]:
    """
    /**
     * @purpose Codex 소유 Track A tokenizer와 Track B deferred 설정을 독립 검증한다.
     * @spec_ref §14, §26, D-RD-03
     * @param tokenizer configs/tokenizer_v1.yaml mapping
     * @param serving configs/serving_v1.yaml mapping
     * @return PASS 상태와 Track 분리·차단 검사 결과
     * @raises ContractValidationError tokenizer/version/Track B 차단 계약이 다른 경우
     * @validation 실제 config와 손상된 permission fixture로 검사한다.
     * @artifact ENVIRONMENT_REPRO_v001.json
     */
    """
    expected_values = {  # Phase 0 engineering이 반드시 고정할 SSOT/Director 계약을 선언한다.
        "tokenizer.track": (tokenizer, "track", "A"),  # raw-text primary measurement가 Track A인지 확인한다.
        "tokenizer.tokenizer_id": (tokenizer, "tokenizer_id", "o200k_base"),  # primary encoding identity를 확인한다.
        "tokenizer.implementation": (tokenizer, "implementation", "tiktoken"),  # 구현 package를 확인한다.
        "tokenizer.package_version": (tokenizer, "package_version", "0.13.0"),  # design-freeze version을 확인한다.
        "serving.track": (serving, "track", "B"),  # serving config가 별도 Track B인지 확인한다.
        "serving.execution_status": (serving, "execution_status", "deferred"),  # D-RD-03의 machine-readable 상태를 확인한다.
        "serving.enabled_in_phase_0": (serving, "enabled_in_phase_0", False),  # Phase 0 실행이 비활성인지 확인한다.
        "serving.deployment.baseline_if_reactivated": (serving, "deployment.baseline_if_reactivated", "hugging_face_hosted_api"),  # 재개 시 hosted API baseline만 기록했는지 확인한다.
        "serving.research_contract.serving_seed_path": (serving, "research_contract.serving_seed_path", "seed_policy.serving"),  # numeric seed 복제 없이 Claude config를 참조하는지 확인한다.
    }  # exact equality 검사 목록을 닫는다.
    for label, (mapping, dotted_path, expected) in expected_values.items():  # 각 고정 계약을 동일한 방식으로 검사한다.
        actual = _required_path(mapping, dotted_path)  # 해당 mapping에서 실제 값을 읽는다.
        if actual != expected:  # 문자열·boolean을 exact 비교해 silent coercion을 막는다.
            raise ContractValidationError(f"{label} 불일치: expected={expected!r}, actual={actual!r}")  # expected/actual을 함께 보고한다.
    permission_keys = ["model_download_allowed", "local_inference_allowed", "hosted_api_call_allowed", "serving_benchmark_allowed", "gpu_serving_setup_allowed"]  # 현재 금지된 모든 Track B 동작을 열거한다.
    permission_states = {key: _required_path(serving, f"execution_permissions.{key}") for key in permission_keys}  # 각 permission의 실제 boolean을 수집한다.
    if any(value is not False for value in permission_states.values()):  # 하나라도 false가 아니면 accidental execution 경로가 열린 것이다.
        raise ContractValidationError(f"Track B 실행 permission은 모두 false여야 합니다: {permission_states!r}")  # 열린 permission을 포함해 즉시 중단한다.
    if _required_path(tokenizer, "network_fallback_allowed") is not False:  # Track A notebook의 network fallback도 금지한다.
        raise ContractValidationError("Track A tokenizer network fallback은 false여야 합니다.")  # offline artifact 계약 위반을 중단한다.
    return {"status": "PASS", "track_a": "o200k_base/tiktoken==0.13.0", "track_b": "deferred", "track_separation": "PASS", "execution_permissions": permission_states}  # 감사 가능한 engineering 결과를 반환한다.


def validate_cross_contracts(research: Mapping[str, Any], morphology: Mapping[str, Any], tokenizer: Mapping[str, Any], serving: Mapping[str, Any]) -> dict[str, Any]:
    """
    /**
     * @purpose Claude가 freeze한 연구 config와 Codex 구현 config의 key·version·상태를 교차 검증한다.
     * @spec_ref D-RD-01, D-RD-03, G0 cross-contract validation
     * @param research Claude 소유 configs/research_v1.yaml mapping
     * @param morphology Claude 소유 configs/morphology_v1.yaml mapping
     * @param tokenizer Codex 소유 configs/tokenizer_v1.yaml mapping
     * @param serving Codex 소유 configs/serving_v1.yaml mapping
     * @return PASS 상태, seed key 목록, analyzer/Track 결과
     * @raises ContractValidationError 필수 seed, analyzer version, Track 상태가 누락·충돌한 경우
     * @validation synthetic 구조 fixture와 integration config에서 검사한다.
     * @artifact ENVIRONMENT_REPRO_v001.json
     */
    """
    engineering = validate_engineering_contracts(tokenizer, serving)  # Codex 소유 계약부터 fail-fast 검증한다.
    seed_keys = ["master_seed", "split", "bootstrap", "model_tuning", "serving", "auxiliary"]  # D-RD-01이 요구한 Claude-owned seed key 집합을 고정한다.
    seed_values = {key: _required_path(research, f"seed_policy.{key}") for key in seed_keys}  # numeric 값을 복제하지 않고 research config에서만 읽는다.
    if any(type(value) is not int or not 0 <= value <= 4_294_967_295 for value in seed_values.values()):  # bool을 제외한 uint32 범위 정수인지 확인한다.
        raise ContractValidationError(f"seed_policy 값은 uint32 정수여야 합니다: {seed_values!r}")  # 잘못된 seed mapping을 보고하고 중단한다.
    if len(set(seed_values.values())) != len(seed_values):  # 서로 다른 stochastic stream이 같은 seed를 공유하지 않는지 확인한다.
        raise ContractValidationError("seed_policy 값은 stream별로 유일해야 합니다.")  # 의도치 않은 stream 결합을 거부한다.
    analyzer_name = _required_path(morphology, "analyzer.primary_name")  # 연구 계약의 analyzer identity를 읽는다.
    analyzer_package = _required_path(morphology, "analyzer.primary_package")  # analyzer distribution 이름을 읽는다.
    analyzer_version = _required_path(morphology, "analyzer.design_freeze_version")  # analyzer design-freeze version을 읽는다.
    if (analyzer_name, analyzer_package, analyzer_version) != ("Kiwi", "kiwipiepy", "0.23.2"):  # SSOT와 Phase 0 설치 계약을 exact 비교한다.
        raise ContractValidationError(f"morphology analyzer 계약 불일치: {(analyzer_name, analyzer_package, analyzer_version)!r}")  # 관측 tuple을 포함해 중단한다.
    research_track_b = _required_path(research, "track_b_status.status")  # Claude가 기록한 연구 측 Track B 상태를 읽는다.
    if research_track_b != "DEFERRED_NOT_EXECUTED":  # D-RD-03의 연구 상태가 아니면 실행 차단 계약과 충돌한다.
        raise ContractValidationError(f"research Track B 상태 불일치: {research_track_b!r}")  # 충돌 값을 보고하고 중단한다.
    if _required_path(serving, "research_contract.track_b_status_path") != "track_b_status.status":  # serving config가 같은 연구 key를 참조하는지 확인한다.
        raise ContractValidationError("serving Track B research key reference가 일치하지 않습니다.")  # 잘못된 key 연결을 거부한다.
    return {  # numeric seed를 재정의하지 않는 cross-contract 결과를 구성한다.
        "status": "PASS",  # 모든 교차 검사가 통과했음을 표시한다.
        "research_config_parseable": "PASS",  # research YAML mapping parse 성공을 기록한다.
        "required_seed_keys": seed_keys,  # 발견한 필수 seed key 이름만 기록한다.
        "seed_values_source": "configs/research_v1.yaml",  # numeric seed의 단일 권위 source를 기록한다.
        "primary_tokenizer": engineering["track_a"],  # Track A tokenizer/version 계약을 기록한다.
        "analyzer": f"{analyzer_name}/{analyzer_package}=={analyzer_version}",  # Kiwi package/version 계약을 기록한다.
        "track_a_b_separation": engineering["track_separation"],  # measurement와 serving 분리 상태를 기록한다.
        "track_b_research_status": research_track_b,  # 연구 측 deferred 상태를 기록한다.
        "track_b_engineering_status": engineering["track_b"],  # 구현 측 deferred 상태를 기록한다.
    }  # 감사 가능한 cross-contract 결과를 반환한다.


def validate_cross_contract_files(project_root: Path) -> dict[str, Any]:
    """
    /**
     * @purpose project의 실제 네 config와 pyproject를 읽어 integration-ready 계약을 검증한다.
     * @spec_ref G0 cross-agent validation, D-RD-02
     * @param project_root canonical root 또는 agent worktree root
     * @return config SHA-256과 모든 교차 검증 결과
     * @raises FileNotFoundError Claude-owned config가 아직 branch에 통합되지 않은 경우
     * @raises ContractValidationError parse 또는 계약 검사가 실패한 경우
     * @validation integration test와 00 notebook에서 실행한다.
     * @artifact ENVIRONMENT_REPRO_v001.json
     */
    """
    config_paths = {  # ownership별 실제 config 경로를 명시한다.
        "research": project_root / "configs" / "research_v1.yaml",  # Claude-owned G0 parameter source를 선택한다.
        "morphology": project_root / "configs" / "morphology_v1.yaml",  # Claude-owned analyzer contract를 선택한다.
        "tokenizer": project_root / "configs" / "tokenizer_v1.yaml",  # Codex-owned Track A contract를 선택한다.
        "serving": project_root / "configs" / "serving_v1.yaml",  # Codex-owned Track B contract를 선택한다.
    }  # 네 입력 계약 경로 mapping을 닫는다.
    configs = {name: load_yaml_mapping(path) for name, path in config_paths.items()}  # 네 YAML을 읽기 전용으로 파싱한다.
    cross_contract = validate_cross_contracts(configs["research"], configs["morphology"], configs["tokenizer"], configs["serving"])  # mapping 간 상호계약을 검증한다.
    namespace = validate_package_namespace(project_root / "pyproject.toml")  # package namespace를 YAML과 독립적으로 검증한다.
    return {"status": "PASS", "cross_contract": cross_contract, "namespace": namespace, "config_sha256": {name: sha256_file(path) for name, path in config_paths.items()}}  # 입력 bytes hash와 PASS 결과를 함께 반환한다.
