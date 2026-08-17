"""NB06 / D-05 결과 패키지 자체 검증.

검사 대상:
  1. 패키지 파일이 모두 존재하는가
  2. 문서의 내부 링크가 실제 파일을 가리키는가
  3. 문서에 쓰인 수치가 집계 JSON / manifest와 일치하는가 (§16 numeric audit)
  4. 원문·chunk 문자열·token ID 배열이 노출되지 않았는가 (§17 hygiene)
  5. figure를 다시 만들었을 때 hash가 같은가 (LEVEL A)
  6. (파일이 있으면) canonical D-05 artifact의 sha256이 기대값과 같은가

이 스크립트는 canonical artifact를 수정하지 않는다. 읽기 전용이다.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
DATA = HERE / "data/NB06_D05_VISUAL_DATA_v001.json"
FIGURES = HERE / "figures"

EXPECTED_D05_SHA256 = "bfa98bd6cf7ee8b7254c469aed3e259ce43cc8f0529153347ca4c2c3fc1944ab"
EXPECTED_PAIR_SET_MD5 = "d9660d654ee449e4d0c23a0070225274"
EXPECTED_ROWS = 3_835_988
EXPECTED_COLUMNS = 39

DOCS = ["README.md", "RESULT_CARD.md", "NB06_D05_INTERPRETATION_KO.md",
        "NB06_D05_METHOD_AND_VALIDATION_KO.md", "REPRODUCE.md"]
FIGURE_STEMS = ["NB06_D05_V01_pipeline_boundary", "NB06_D05_V02_chunk_vs_token_expansion",
                "NB06_D05_V03_validation", "NB06_D05_V04_runtime"]
SCRIPTS = ["build_nb06_figures.py", "extract_visual_data.py", "verify_nb06_d05.py",
           "reproduce.sh"]

# SSOT §16.2 canonical figure 이름은 이 패키지에서 쓰지 않는다.
CANONICAL_FIGURE_IDS = tuple(f"F0{i}" for i in range(1, 10))

# §4.5 / §11에서 금지한 인과 서술. 문서에 나타나면 안 된다.
FORBIDDEN_CLAIMS = [
    "regex chunking이 TP를 유발",
    "morphology 때문에 chunk",
    "차별한다",
    "causes the premium",
    "causes all TP",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


class Report:
    def __init__(self) -> None:
        self.results: list[tuple[str, bool, str]] = []

    def check(self, name: str, ok: bool, detail: str = "") -> None:
        self.results.append((name, bool(ok), detail))

    def render(self) -> bool:
        width = max(len(n) for n, _, _ in self.results)
        for name, ok, detail in self.results:
            suffix = f"   {detail}" if detail else ""
            print(f"  {name:<{width}}  {'PASS' if ok else 'FAIL'}{suffix}")
        return all(ok for _, ok, _ in self.results)


def check_files(report: Report) -> None:
    for name in DOCS + SCRIPTS:
        report.check(f"exists {name}", (HERE / name).is_file())
    report.check("exists data/NB06_D05_VISUAL_DATA_v001.json", DATA.is_file())
    for stem in FIGURE_STEMS:
        for suffix in ("svg", "png"):
            report.check(f"exists figures/{stem}.{suffix}",
                         (FIGURES / f"{stem}.{suffix}").is_file())


def check_links(report: Report) -> None:
    pattern = re.compile(r"\[[^\]]*\]\(([^)#]+)\)")
    broken: list[str] = []
    for name in DOCS:
        text = (HERE / name).read_text(encoding="utf-8")
        for target in pattern.findall(text):
            if target.startswith(("http://", "https://")):
                continue
            if not (HERE / target).exists():
                broken.append(f"{name} -> {target}")
    report.check("internal links resolve", not broken, "; ".join(broken))


def check_figure_naming(report: Report) -> None:
    leaked: list[str] = []
    for path in FIGURES.iterdir():
        if any(fid in path.name for fid in CANONICAL_FIGURE_IDS):
            leaked.append(path.name)
    report.check("no canonical F01-F09 figure ids", not leaked, "; ".join(leaked))


def check_numbers(report: Report, data: dict) -> None:
    """§16: 문서의 수치를 집계 JSON과 기계 대조한다."""
    ko, en = data["side_profile"]["ko"], data["side_profile"]["en"]
    dec = data["decomposition"]
    runtime, validation, pilot = data["runtime"], data["validation"], data["pilot"]

    expected_strings = {
        "population N": f"{data['population']['n_pairs']:,}",
        "KO chunk_count": f"{ko['mean_chunk_count']:.2f}",
        "EN chunk_count": f"{en['mean_chunk_count']:.2f}",
        "KO tokens_per_chunk": f"{ko['mean_tokens_per_chunk']:.2f}",
        "EN tokens_per_chunk": f"{en['mean_tokens_per_chunk']:.2f}",
        "chunk term": f"{dec['mean_log_chunk_count_term']:.4f}",
        "density term": f"+{dec['mean_log_tokens_per_chunk_term']:.4f}",
        "log token ratio": f"+{dec['mean_log_token_ratio']:.4f}",
        "d05 sha256": data["provenance"]["d05_artifact"]["sha256"],
        "pair set md5": data["provenance"]["d05_artifact"]["pair_set_md5"],
        "telemetry elapsed": f"{runtime['telemetry_elapsed_sec']}",
        "mean rows/sec": f"{runtime['telemetry_mean_rows_per_second']:,}",
        "min MemAvailable": f"{runtime['min_mem_available_gib']}",
        "pilot chunks": f"{pilot['total_chunks_inspected']:,}",
    }
    # 문서는 조판용 U+2212(−)를 쓸 수 있다. 숫자 비교 전에 ASCII 하이픈으로 정규화한다.
    def normalise(text: str) -> str:
        return text.replace("\u2212", "-").replace("\u2013", "-")

    blob = normalise("\n".join((HERE / name).read_text(encoding="utf-8") for name in DOCS))
    missing = [label for label, value in expected_strings.items()
               if normalise(value) not in blob]
    report.check("document numbers match aggregates", not missing, "; ".join(missing))

    # 집계 JSON 자체가 manifest 및 기대 신원과 어긋나지 않는지도 확인한다.
    report.check("aggregate row count", data["population"]["n_pairs"] == EXPECTED_ROWS)
    report.check("aggregate column count",
                 data["provenance"]["d05_artifact"]["column_count"] == EXPECTED_COLUMNS)
    report.check("aggregate d05 sha256",
                 data["provenance"]["d05_artifact"]["sha256"] == EXPECTED_D05_SHA256)
    report.check("aggregate pair-set md5",
                 data["provenance"]["d05_artifact"]["pair_set_md5"] == EXPECTED_PAIR_SET_MD5)
    report.check("validation 17/17 PASS",
                 validation["validation_status"] == "PASS"
                 and all(validation["checks"].values()),
                 f"{sum(validation['checks'].values())}/{len(validation['checks'])}")
    report.check("pilot total mismatch 0", pilot["total_mismatch"] == 0)
    report.check("zero token equivalence failures",
                 validation["token_equivalence_failures"] == 0)
    report.check("R1 periodic telemetry", runtime["r1_periodic_sampling"] is True)
    report.check("no RED-or-worse telemetry sample",
                 runtime["red_or_worse_sample_count"] == 0)

    # 분해 항등식이 문서가 주장하는 대로 닫히는지 확인한다.
    residual = abs(dec["mean_log_chunk_count_term"] + dec["mean_log_tokens_per_chunk_term"]
                   - dec["mean_log_token_ratio"])
    report.check("decomposition identity closes", residual < 1e-6, f"residual {residual:.2e}")


def check_hygiene(report: Report, data: dict) -> None:
    """§17: 원문·chunk 문자열·token ID 배열이 패키지에 들어가지 않았는지 확인한다."""
    text_files = [HERE / name for name in DOCS + SCRIPTS] + [DATA]

    # 집계 JSON에는 한글이 전혀 없어야 한다 (원문 흔적).
    json_blob = DATA.read_text(encoding="utf-8")
    hangul = re.findall(r"[가-힣]+", json_blob)
    report.check("visual data has no Korean text", not hangul, "".join(hangul[:5]))

    # 문서에 4자 이상 한글이 있는 것은 정상(설명문). 긴 인용문 형태의 원문만 걸러낸다.
    long_quotes: list[str] = []
    for path in [HERE / name for name in DOCS]:
        for match in re.finditer(r"[\"'“”][^\"'“”\n]{40,}[\"'“”]", path.read_text(encoding="utf-8")):
            if len(re.findall(r"[가-힣]", match.group())) >= 25:
                long_quotes.append(f"{path.name}: {match.group()[:40]}…")
    report.check("no long Korean quotations", not long_quotes, "; ".join(long_quotes))

    # token ID 배열 형태 (숫자 4개 이상이 쉼표로 이어진 리스트). 집계 JSON은 히스토그램
    # bin count처럼 정당한 숫자 배열을 담으므로 문자열 검사 대신 아래에서 구조로 확인한다.
    id_array = re.compile(r"\[\s*\d{2,6}\s*(,\s*\d{2,6}\s*){3,}\]")
    offenders = [p.name for p in text_files if p != DATA
                 and id_array.search(p.read_text(encoding="utf-8"))]
    report.check("no token id arrays in docs/scripts", not offenders, "; ".join(offenders))

    # 집계 JSON에서 숫자 리스트가 허용된 위치(히스토그램 bin) 밖에 있으면 실패시킨다.
    allowed_list_paths = {".histograms.*.counts", ".histograms.*.bin_edges_lo"}
    stray: list[str] = []

    def scan_lists(node: object, path: str = "") -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                child = f"{path}.{key}"
                scan_lists(value, "" if key == "histograms" else child)
                if key == "histograms":
                    for hist in value.values():
                        for field in hist:
                            if f".histograms.*.{field}" not in allowed_list_paths \
                                    and isinstance(hist[field], list):
                                stray.append(f".histograms.*.{field}")
        elif isinstance(node, list) and len(node) > 3 \
                and all(isinstance(item, (int, float)) for item in node):
            stray.append(path or "<root>")

    scan_lists({k: v for k, v in data.items() if k != "histograms"})
    report.check("numeric arrays only in histogram bins", not stray, "; ".join(sorted(set(stray))))

    # parquet이 패키지에 들어가지 않았는지
    parquet = [p.name for p in HERE.rglob("*.parquet")]
    report.check("no parquet in package", not parquet, "; ".join(parquet))

    # 집계 JSON에 chunk 문자열 필드가 없는지
    forbidden_keys = {"chunks", "chunk_strings", "token_ids", "ko_text", "en_text",
                      "ko_token_ids", "en_token_ids"}
    found: list[str] = []

    def walk(node: object, path: str = "") -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key in forbidden_keys:
                    found.append(f"{path}.{key}")
                walk(value, f"{path}.{key}")
        elif isinstance(node, list):
            for item in node[:3]:
                walk(item, path)

    walk(data)
    report.check("no raw-content keys in visual data", not found, "; ".join(found))


def check_claim_boundary(report: Report) -> None:
    negations = ("않습니다", "않는다", "아님", "금지", "부정", "쓰지 않")
    offenders: list[str] = []
    for name in DOCS:
        text = (HERE / name).read_text(encoding="utf-8")
        # 단락 단위로 본다. 금지 문구를 '이렇게 쓰지 않는다'며 인용하는 단락에서는
        # 문구가 다음 줄에 오므로 줄 단위 예외로는 잡히지 않는다.
        for paragraph in re.split(r"\n\s*\n", text):
            if any(marker in paragraph for marker in negations):
                continue
            for claim in FORBIDDEN_CLAIMS:
                if claim in paragraph:
                    offenders.append(f"{name}: {claim}")
    report.check("no causal claims", not offenders, "; ".join(offenders))

    required = {"README.md": ["확립하지"],
                "RESULT_CARD.md": ["NOT CAUSAL"],
                "NB06_D05_INTERPRETATION_KO.md": ["NOT CAUSAL"]}
    for name, needles in required.items():
        text = (HERE / name).read_text(encoding="utf-8")
        report.check(f"claim boundary stated in {name}",
                     all(needle in text for needle in needles))

    # 세 경계 구분 문장이 원문 term 그대로 병기되어 있는지
    readme = (HERE / "README.md").read_text(encoding="utf-8")
    report.check(
        "three-way distinction stated verbatim",
        "linguistic morphology" in readme
        and "tokenizer regex chunking" in readme
        and "final subword tokenization" in readme)


def check_figure_reproduction(report: Report) -> None:
    """figure를 임시 디렉터리에 다시 만들어 hash를 대조한다 (LEVEL A)."""
    committed = {stem: {suffix: sha256_file(FIGURES / f"{stem}.{suffix}")
                        for suffix in ("svg", "png")} for stem in FIGURE_STEMS}
    backup = Path(tempfile.mkdtemp(prefix="nb06_figures_"))
    for stem in FIGURE_STEMS:
        for suffix in ("svg", "png"):
            shutil.copy2(FIGURES / f"{stem}.{suffix}", backup / f"{stem}.{suffix}")

    result = subprocess.run(  # noqa: S603 - 같은 인터프리터로 패키지 내 스크립트만 실행한다
        [sys.executable, str(HERE / "build_nb06_figures.py")],
        capture_output=True, text=True, check=False)
    if result.returncode != 0:
        report.check("figure builder runs", False, result.stderr.strip()[:160])
        return
    report.check("figure builder runs", True)

    mismatched = [f"{stem}.{suffix}"
                  for stem in FIGURE_STEMS for suffix in ("svg", "png")
                  if sha256_file(FIGURES / f"{stem}.{suffix}") != committed[stem][suffix]]
    if mismatched:
        # 재현 실패 시 커밋된 파일을 되돌려 작업 트리를 더럽히지 않는다.
        for stem in FIGURE_STEMS:
            for suffix in ("svg", "png"):
                shutil.copy2(backup / f"{stem}.{suffix}", FIGURES / f"{stem}.{suffix}")
    shutil.rmtree(backup, ignore_errors=True)
    report.check("figure hashes reproduce", not mismatched, "; ".join(mismatched))


def check_local_artifact(report: Report) -> None:
    """로컬에 canonical D-05가 있으면 신원을 확인한다. 없으면 건너뛴다 (LEVEL B)."""
    path = REPO / "data/registry/CHUNK_O200K_BASE_v001.parquet"
    if not path.exists():
        print("  (LEVEL B skipped) local CHUNK_O200K_BASE_v001.parquet not present")
        return
    actual = sha256_file(path)
    report.check("local D-05 sha256 matches expected", actual == EXPECTED_D05_SHA256,
                 actual[:16] + "…")


REPRO_MANIFEST = HERE / "NB06_D05_REPRO_MANIFEST_v001.json"


def write_repro_manifest(report: Report, data: dict) -> None:
    """패키지 구성 파일의 해시와 재현 수준별 상태를 기록한다.

    manifest 자신은 대상에서 제외한다 (자기 해시를 담을 수 없다).
    """
    files = {}
    for path in sorted(HERE.rglob("*")):
        if not path.is_file() or path == REPRO_MANIFEST:
            continue
        if "__pycache__" in path.parts:
            continue
        files[str(path.relative_to(HERE))] = sha256_file(path)

    checks = {name: ok for name, ok, _ in report.results}
    local = REPO / "data/registry/CHUNK_O200K_BASE_v001.parquet"
    payload = {
        "artifact_id": "NB06_D05_REPRO_MANIFEST_v001",
        "package_root": "docs/results/nb06_d05",
        "canonical_main": "a31a4c27417b93567bb6e261b6225813aaa5f66e",
        "nb06_result_commit": "c9aa4796f8157b9025deee33ef6504f5921aaf59",
        "expected": {
            "d05_sha256": EXPECTED_D05_SHA256,
            "d05_row_count": EXPECTED_ROWS,
            "d05_column_count": EXPECTED_COLUMNS,
            "pair_set_md5": EXPECTED_PAIR_SET_MD5,
            "d04_sha256": data["provenance"]["d04_authority"]["sha256"],
        },
        "reproduction_levels": {
            "LEVEL_A_documentation_and_figures": {
                "requires": "git checkout only",
                "status": "PASS" if checks.get("figure hashes reproduce") else "FAIL",
            },
            "LEVEL_B_d05_validation": {
                "requires": "local CHUNK_O200K_BASE_v001.parquet + TOKEN_O200K_BASE_v001.parquet",
                "status": ("PASS" if checks.get("local D-05 sha256 matches expected")
                           else "NOT_RUN"),
                "artifact_present": local.exists(),
                "validator": "scripts/validate_d05.py",
            },
            "LEVEL_C_full_re_execution": {
                "requires": ("local PAIR_REGISTRY_v002.parquet (2.8 GB), "
                             "TOKEN_O200K_BASE_v001.parquet (776 MB), "
                             "offline tiktoken o200k_base cache, MemAvailable >= 5 GiB"),
                "status": "NOT_RUN",
                "reason": ("canonical parquet artifacts are excluded from the repository "
                           "by .gitignore (data/registry/**); a git checkout alone cannot "
                           "regenerate them"),
                "runner": "scripts/run_d05_full.py",
            },
        },
        "package_verify": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "files": files,
    }
    REPRO_MANIFEST.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")


def main() -> int:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    report = Report()

    check_files(report)
    check_links(report)
    check_figure_naming(report)
    check_numbers(report, data)
    check_hygiene(report, data)
    check_claim_boundary(report)
    check_figure_reproduction(report)
    check_local_artifact(report)

    ok = report.render()
    write_repro_manifest(report, data)
    print(f"\n  wrote {REPRO_MANIFEST.relative_to(REPO)}")
    print(f"  sha256 {sha256_file(REPRO_MANIFEST)}")
    print(f"  PACKAGE_VERIFY = {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
