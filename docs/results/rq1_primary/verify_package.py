"""RQ1 publication package 검증기.

세 검사를 제공한다.
  figures    figure 파일 존재 · SVG parse · PNG 판독 · manifest hash 대조
  all        위 + README / paper text / visual data 의 수치가 canonical authority와 일치하는지
  inference  재실행된 NB08 결과가 frozen expected value와 일치하는지

새 통계를 만들지 않는다. 값을 비교만 한다.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data" / "RQ1_VISUAL_DATA_v001.json"
MANIFEST = HERE / "NB08_RQ1_VISUAL_MANIFEST_v001.json"

FIGS = ["NB08_RQ1_V01_distribution", "NB08_RQ1_V02_polarity", "NB08_RQ1_V03_lattice_ci",
        "NB08_RQ1_V04_robustness", "NB08_RQ1_S01_source_strata"]

FROZEN = {  # evidence-of-record 502bc128 / closeout 3f4e821
    "N": 3835988,
    "median_logTP": 0.28768207245178085,
    "median_TP_scale": 1.3333333333333333,
    "sign_positive": 3375095, "sign_negative": 264175, "sign_ties": 196718,
    "known_N": 3785441,
    "tie_aware_primary": 0.8798502497922308,
    "tie_aware_known": 0.8798285325029828,
    "point_mass": 123040,
    "d04_sha256": "1c30e3276222dd94885ae4f79fc6ab5c45e4e26226de0afd91fc6b1f7d2c16e7",
    "pair_set_hash": "d9660d654ee449e4d0c23a0070225274",
}

ok, fail = [], []


def chk(name: str, cond: bool, detail: str = "") -> None:
    (ok if cond else fail).append(name)
    print(f"  {'OK  ' if cond else 'FAIL'} {name}{('  ' + detail) if detail else ''}")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def check_figures() -> None:
    print("[figures]")
    man = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else None
    for stem in FIGS:
        for ext in ("svg", "png", "pdf"):
            p = HERE / "figures" / f"{stem}.{ext}"
            chk(f"exists {stem}.{ext}", p.exists() and p.stat().st_size > 0)
            if not p.exists():
                continue
            if ext == "svg":
                try:
                    ET.parse(p); parsed = True
                except ET.ParseError:
                    parsed = False
                chk(f"svg parse {stem}", parsed)
            if ext == "png":
                chk(f"png header {stem}", p.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n")
    if man:
        for fid, entry in man["figures"].items():
            for ext in ("svg", "png"):
                p = HERE / entry[f"path_{ext}"]
                chk(f"manifest hash {fid} {ext}",
                    p.exists() and sha(p) == entry[f"sha256_{ext}"])
    else:
        print("  (manifest 없음 — hash 대조 생략)")


def check_numbers(repo: Path) -> None:
    print("[numeric authority]")
    r4 = repo / "ssot_nb01/04_NB08_RQ1_RESULTS_v001.json"
    r6 = repo / "ssot_nb01/06_NB08_RQ1_SSOT_CLOSEOUT_v001.json"
    if r4.exists() and r6.exists():
        R, C = json.loads(r4.read_text()), json.loads(r6.read_text())
        P = R["primary"]
        chk("04 N", P["n"] == FROZEN["N"])
        chk("04 median", P["median_logTP"] == FROZEN["median_logTP"])
        chk("04 TP scale", P["exp_median_logTP"] == FROZEN["median_TP_scale"])
        chk("04 sign counts", (P["sign_test"]["positive"], P["sign_test"]["negative"],
                               P["sign_test"]["ties"]) ==
            (FROZEN["sign_positive"], FROZEN["sign_negative"], FROZEN["sign_ties"]))
        chk("04 CI degenerate", P["bootstrap_ci95"][0] == P["bootstrap_ci95"][1] == FROZEN["median_logTP"])
        T = C["TIE_AWARE_MEDIAN_SIGN_ROBUSTNESS"]
        chk("06 tie-aware primary", T["PRIMARY_FINAL_COHORT"]["point_estimate"] == FROZEN["tie_aware_primary"])
        chk("06 point mass", C["CI_DEGENERACY"]["point_mass_at_median"] == FROZEN["point_mass"])
        chk("06 stratified CI degenerate",
            C["SOURCE_STRATIFIED_BOOTSTRAP_SENSITIVITY"]["ci95"][0] ==
            C["SOURCE_STRATIFIED_BOOTSTRAP_SENSITIVITY"]["ci95"][1])
    else:
        print("  (canonical artifact 없음 — frozen 상수만으로 대조)")

    print("[visual data]")
    D = json.loads(DATA.read_text())
    A = D["authority"]
    chk("data N", A["N"] == FROZEN["N"])
    chk("data median", A["median_logTP"] == FROZEN["median_logTP"])
    chk("data TP scale", A["median_TP_scale"] == FROZEN["median_TP_scale"])
    chk("data sign counts", (A["sign_positive"], A["sign_negative"], A["sign_ties"]) ==
        (FROZEN["sign_positive"], FROZEN["sign_negative"], FROZEN["sign_ties"]))
    chk("data point mass", A["point_mass_at_median"] == FROZEN["point_mass"])
    chk("data d04 sha", D["provenance"]["d04_sha256"] == FROZEN["d04_sha256"])
    chk("data pair-set hash", D["provenance"]["pair_set_hash"] == FROZEN["pair_set_hash"])
    hist_total = sum(n for _, n in D["descriptive_from_d04"]["histogram"])
    chk("histogram sums to N", hist_total == FROZEN["N"], f"{hist_total:,}")

    print("[documents]")
    for doc, needles in (
        ("README.md", ["3,835,988", "0.28768207245178085", "1.3333333333333333",
                       "87.9850", "3,375,095", "196,718", "264,175", "123,040", "3,725"]),
        ("RQ1_PAPER_TEXT_EN.md", ["3,835,988", "0.28768207245178085", "1.3333333333333333",
                                  "87.99", "3,375,095", "196,718", "264,175", "123,040"]),
        ("RQ1_INTERPRETATION_KO.md", ["3,835,988", "0.28768207245178085", "0.879850",
                                      "123,040", "3,725", "196,718"]),
    ):
        text = (HERE / doc).read_text()
        miss = [n for n in needles if n not in text]
        chk(f"{doc} 수치 일치", not miss, f"missing={miss}" if miss else "")

    print("[privacy]")
    bad_patterns = [
        (r"ko_text_analysis\"?\s*:\s*\"[^\"]{20,}", "raw KO text field"),
        (r"en_text_analysis\"?\s*:\s*\"[^\"]{20,}", "raw EN text field"),
        (r"morpheme_sequence\"?\s*:\s*\[\s*\{", "raw morpheme sequence"),
        (r"pair_[0-9a-f]{64}", "pair_id"),
    ]
    hits = []
    for p in sorted(HERE.rglob("*")):
        if p.is_dir() or p.suffix in (".png", ".pdf"):
            continue
        try:
            t = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for pat, label in bad_patterns:
            if re.search(pat, t):
                hits.append(f"{p.relative_to(HERE)}:{label}")
    chk("raw text / pair_id 노출 없음", not hits, f"{hits[:3]}" if hits else "")
    # 한글 장문(원문 문장) 탐지: 문서 서술은 허용, data/figures 에는 금지
    long_ko = []
    for p in list((HERE / "data").rglob("*")) + list((HERE / "figures").glob("*.svg")):
        if p.is_dir():
            continue
        try:
            t = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if re.search(r"[가-힣]{15,}", t):
            long_ko.append(str(p.relative_to(HERE)))
    chk("data/figures 내 한글 장문 없음", not long_ko, f"{long_ko}" if long_ko else "")


def check_inference(repo: Path) -> None:
    print("[re-executed inference vs frozen]")
    R = json.loads((repo / "ssot_nb01/04_NB08_RQ1_RESULTS_v001.json").read_text())
    C = json.loads((repo / "ssot_nb01/06_NB08_RQ1_SSOT_CLOSEOUT_v001.json").read_text())
    P = R["primary"]; K = R["sensitivity_known_direction"]
    T = C["TIE_AWARE_MEDIAN_SIGN_ROBUSTNESS"]; S = C["SOURCE_STRATIFIED_BOOTSTRAP_SENSITIVITY"]
    chk("N", P["n"] == FROZEN["N"])
    chk("median logTP", P["median_logTP"] == FROZEN["median_logTP"])
    chk("pair bootstrap CI", P["bootstrap_ci95"] == [FROZEN["median_logTP"]] * 2)
    chk("Wilcoxon W", P["wilcoxon"]["statistic"] == 6405551963244.0)
    chk("sign counts", (P["sign_test"]["positive"], P["sign_test"]["negative"],
                        P["sign_test"]["ties"]) ==
        (FROZEN["sign_positive"], FROZEN["sign_negative"], FROZEN["sign_ties"]))
    chk("tie-aware primary", T["PRIMARY_FINAL_COHORT"]["point_estimate"] == FROZEN["tie_aware_primary"])
    chk("known-direction N", K["n"] == FROZEN["known_N"])
    chk("known-direction median", K["median_logTP"] == FROZEN["median_logTP"])
    chk("source-stratified CI", S["ci95"] == [FROZEN["median_logTP"]] * 2)
    chk("bootstrap seed", R["bootstrap"]["seed"] == 969634713)
    chk("stratified seed", S["seed"] == 2856958648)
    chk("D-04 sha256", R["source"]["artifact_sha256"] == FROZEN["d04_sha256"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", choices=("figures", "all", "inference"), default="all")
    ap.add_argument("--repo", default=str(HERE.parents[2]))
    a = ap.parse_args()
    repo = Path(a.repo)

    if a.check == "figures":
        check_figures()
        tag = "FIGURE_REPRODUCTION"
    elif a.check == "inference":
        check_inference(repo)
        tag = "STATISTICAL_REEXECUTION"
    else:
        check_figures(); check_numbers(repo)
        tag = "RESULT_VERIFICATION"

    print(f"\n  passed {len(ok)} · failed {len(fail)}")
    print(f"\n{tag}_{'PASS' if not fail else 'FAIL'}")
    sys.exit(0 if not fail else 1)
