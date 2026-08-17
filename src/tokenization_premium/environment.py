"""Phase 0 notebook에서 사용할 host, package, Git metadata 수집기를 제공한다."""

from __future__ import annotations  # Python 3.12 지연 annotation 평가를 사용한다.

import locale  # 실행 locale과 preferred encoding을 기록한다.
import os  # WSL과 process 환경 정보를 읽는다.
import platform  # OS, kernel, architecture를 표준 API로 읽는다.
import subprocess  # Git, uv, NVIDIA CLI를 shell 없이 실행한다.
import sys  # 실제 Python executable과 version을 기록한다.
import unicodedata  # Python이 사용하는 Unicode database version을 기록한다.
from importlib import metadata  # 설치된 distribution version을 조회한다.
from pathlib import Path  # canonical root와 파일 경로를 처리한다.
from typing import Any  # JSON manifest row 타입을 표현한다.

import psutil  # CPU와 RAM 정보를 portable API로 수집한다.


def command_result(arguments: list[str], cwd: Path) -> dict[str, Any]:
    """
    /**
     * @purpose shell expansion 없이 read-only 진단 명령을 실행하고 결과를 구조화한다.
     * @spec_ref §30.1, §30.2
     * @param arguments 실행 파일과 인수 목록
     * @param cwd 명령의 working directory
     * @return command, returncode, stdout, stderr mapping
     * @raises OSError 실행 파일 자체를 시작할 수 없는 경우
     * @validation known command의 returncode와 stdout을 단위 테스트한다.
     * @artifact ENVIRONMENT_REPRO_v001.json
     */
    """
    completed = subprocess.run(arguments, cwd=cwd, check=False, capture_output=True, text=True)  # shell을 사용하지 않아 의도치 않은 확장을 막는다.
    return {"command": arguments, "returncode": completed.returncode, "stdout": completed.stdout.strip(), "stderr": completed.stderr.strip()}  # 감사 가능한 원시 결과를 반환한다.


def collect_host_metadata(project_root: Path) -> dict[str, Any]:
    """
    /**
     * @purpose Python, OS/WSL, CPU, RAM, locale, GPU visibility metadata를 수집한다.
     * @spec_ref §30.1, §37 Phase 0
     * @param project_root read-only command의 working directory
     * @return host environment metadata mapping
     * @raises OSError 필수 OS metadata를 읽을 수 없는 경우
     * @validation Python/UTF-8/CPU/RAM 필드의 존재성과 dtype을 검사한다.
     * @artifact ENVIRONMENT_REPRO_v001.json
     */
    """
    memory = psutil.virtual_memory()  # 실행 시점 RAM 총량과 가용량을 읽는다.
    nvidia = command_result(["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"], project_root)  # GPU와 driver를 read-only로 조회한다.
    return {  # host를 재현·비교하는 데 필요한 최소 metadata를 한 mapping으로 묶는다.
        "python_executable": sys.executable,  # 실제 notebook kernel interpreter를 기록한다.
        "python_version": platform.python_version(),  # Python semantic version을 기록한다.
        "python_build": list(platform.python_build()),  # JSON roundtrip에서 dtype이 유지되도록 build tuple을 list로 고정한다.
        "platform": platform.platform(),  # OS와 kernel 요약을 기록한다.
        "kernel": platform.release(),  # WSL kernel version을 분리 기록한다.
        "machine": platform.machine(),  # wheel 선택에 영향을 주는 architecture를 기록한다.
        "wsl_interop": bool(os.environ.get("WSL_INTEROP")),  # WSL process 여부를 환경변수로 확인한다.
        "cpu_model": platform.processor(),  # Python이 관측한 CPU model 문자열을 기록한다.
        "cpu_logical": psutil.cpu_count(logical=True),  # 병렬 실행 용량을 logical CPU 단위로 기록한다.
        "memory_total_bytes": memory.total,  # RAM 총량을 byte 단위로 기록한다.
        "memory_available_bytes": memory.available,  # 실행 시점 가용 RAM을 byte 단위로 기록한다.
        "locale": locale.setlocale(locale.LC_ALL, None),  # process locale의 실제 설정을 기록한다.
        "preferred_encoding": locale.getpreferredencoding(False),  # text I/O 기본 encoding을 기록한다.
        "unicode_version": unicodedata.unidata_version,  # codepoint 동작에 영향을 주는 Unicode DB version을 기록한다.
        "nvidia_smi": nvidia,  # GPU가 없을 때도 returncode를 포함해 상태를 보존한다.
        "dev_dxg_present": Path("/dev/dxg").exists(),  # WSL GPU bridge device 존재를 기록한다.
    }  # JSON 직렬화 가능한 metadata를 반환한다.


def collect_package_versions(names: list[str]) -> list[dict[str, str]]:
    """
    /**
     * @purpose 연구 필수 distribution의 installed/not-installed 상태와 version을 기록한다.
     * @spec_ref §14.1, §15.1, §30.1
     * @param names 조회할 distribution 이름 목록
     * @return package 이름 기준 정렬된 version 행 목록
     * @raises None 누락 package는 NOT_INSTALLED 상태로 반환
     * @validation tiktoken과 kiwipiepy exact version assertion을 수행한다.
     * @artifact PACKAGE_INVENTORY_v001.parquet
     */
    """
    rows: list[dict[str, str]] = []  # package 한 개당 한 행을 누적한다.
    for name in sorted(set(names), key=str.lower):  # 중복과 입력 순서가 manifest에 영향을 주지 않게 정렬한다.
        try:  # 설치된 distribution의 실제 version 조회를 시도한다.
            installed = metadata.version(name)  # import 성공 여부가 아닌 distribution metadata를 읽는다.
            status = "INSTALLED"  # version 조회 성공을 명시적으로 표시한다.
        except metadata.PackageNotFoundError:  # 추측하지 않고 누락을 구조화한다.
            installed = ""  # 누락 package에는 거짓 version을 만들지 않는다.
            status = "NOT_INSTALLED"  # downstream assertion이 사용할 상태를 기록한다.
        rows.append({"package": name, "version": installed, "status": status})  # package grain row를 추가한다.
    return rows  # package 이름 기준의 결정론적 inventory를 반환한다.


def collect_git_metadata(project_root: Path) -> dict[str, Any]:
    """
    /**
     * @purpose 현재 worktree의 branch, HEAD, upstream, dirty 상태를 기록한다.
     * @spec_ref §30.2, §38
     * @param project_root Git worktree root
     * @return Git provenance mapping
     * @raises RuntimeError Git repository 또는 HEAD가 유효하지 않은 경우
     * @validation HEAD가 40자리 hex이고 branch가 detached가 아닌지 검사한다.
     * @artifact ENVIRONMENT_REPRO_v001.json
     */
    """
    head = command_result(["git", "rev-parse", "HEAD"], project_root)  # 현재 code commit을 읽는다.
    branch = command_result(["git", "branch", "--show-current"], project_root)  # 현재 branch 이름을 읽는다.
    upstream = command_result(["git", "rev-parse", "--abbrev-ref", "@{upstream}"], project_root)  # remote tracking branch를 읽는다.
    status = command_result(["git", "status", "--porcelain=v1", "--untracked-files=all"], project_root)  # artifact 생성 전 dirty 상태를 읽는다.
    if head["returncode"] != 0 or len(head["stdout"]) != 40:  # release manifest에 쓸 수 없는 Git 상태를 거부한다.
        raise RuntimeError("유효한 Git HEAD를 확인할 수 없습니다.")  # code provenance 없는 실행을 중단한다.
    return {"head_sha": head["stdout"], "branch": branch["stdout"], "upstream": upstream["stdout"], "dirty": bool(status["stdout"]), "status_porcelain": status["stdout"]}  # Git 상태를 추측 없이 반환한다.
