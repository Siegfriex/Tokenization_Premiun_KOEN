"""NB08 RQ1 publication figure builder.

두 모드로 동작한다.

  extract   canonical D-04 parquet에서 **집계값만** 뽑아 data/RQ1_VISUAL_DATA_v001.json 을 만든다.
            원문(KO/EN)·pair_id·형태소 표면형은 일절 읽지 않는다. D-04가 필요하다.
  figures   위 JSON만 읽어 figure를 렌더링한다. D-04도 원문도 필요 없다. (기본 모드)

새 통계를 만들지 않는다. 검정·bootstrap 수치는 전부 아래 authority에서 복사한다.
  1. ssot_nb01/04_NB08_RQ1_RESULTS_v001.json      (primary evidence-of-record)
  2. ssot_nb01/06_NB08_RQ1_SSOT_CLOSEOUT_v001.json (closeout)
D-04에서는 §1이 허용한 descriptive count(outcome frequency / histogram bin /
exact TP ratio frequency)만 산출한다.

Figure ID는 NB08-RQ1-V01..V04, S01. SSOT canonical F01-F09는 NB07 소유이며 쓰지 않는다.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from zoneinfo import ZoneInfo

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ft2font import FT2Font
from matplotlib.patches import Patch

KST = ZoneInfo("Asia/Seoul")
HERE = Path(__file__).resolve().parent
DATA = HERE / "data" / "RQ1_VISUAL_DATA_v001.json"
FIGDIR = HERE / "figures"

BASE_MAIN_SHA = "07d132e924fbd1127897b2e73fb25a22b6f719b3"
RQ1_CLOSEOUT_SHA = "3f4e8210739205389cfb0c7853f5384015020382"
PRIMARY_RESULT_SHA = "502bc128f6b5855f1648802cc990b715808f26f3"
D04_SHA256 = "1c30e3276222dd94885ae4f79fc6ab5c45e4e26226de0afd91fc6b1f7d2c16e7"
PAIR_SET_HASH = "d9660d654ee449e4d0c23a0070225274"

FIG_STAMP = "RQ1 RESULT VISUALIZATION · NOT SSOT F01-F09 · CANONICAL STATISTICS / NON-CANONICAL FIGURE ID"
BIN = 0.05

# dataviz validator(light/print)를 통과한 값
ACCENT, SECOND, COUNTER = "#2a78d6", "#eb6834", "#e34948"
NEUTRAL = MUTED = "#898781"
INK, INK2, RULE, SURFACE = "#0b0b0b", "#52514e", "#e1e0d9", "#fcfcfb"

CAPTIONS = {
    "NB08-RQ1-V01": ("고정된 o200k_base raw-text Track A와 final paired KO-EN cohort에서의 primary "
                     "outcome 분포. outcome은 이산 lattice이므로 KDE 평활을 쓰지 않았다."),
    "NB08-RQ1-V02": ("Descriptive pair polarity. This is not itself the sign-test statistic. "
                     "부호 구성의 기술통계이며 검정통계량이 아니다."),
    "NB08-RQ1-V03": ("The degenerate bootstrap interval reflects a large discrete point mass at the "
                     "median, not infinite measurement precision."),
    "NB08-RQ1-V04": ("effect magnitude와 robustness를 보고한다. p-value 크기는 시각화하지 않는다. "
                     "CI 두 끝점이 같으므로 가짜 error bar를 그리지 않고 퇴화로 표기한다."),
    "NB08-RQ1-S01": ("DESCRIPTIVE SOURCE STRATA — NOT SOURCE EFFECT. source와 domain은 이 cohort에서 "
                     "분리 식별되지 않는다 (SSOT §20.2)."),
}


# ── extract ──────────────────────────────────────────────────────────────────
def extract(repo: Path) -> None:
    """D-04에서 집계값만 추출한다. 원문·pair_id는 읽지 않는다."""
    import duckdb

    d04 = repo / "data/registry/TOKEN_O200K_BASE_v001.parquet"
    if not d04.exists():
        raise SystemExit(f"D-04 artifact가 없다: {d04}")
    actual = hashlib.sha256()
    with d04.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b""):
            actual.update(chunk)
    if actual.hexdigest() != D04_SHA256:
        raise SystemExit(f"D-04 SHA 불일치: {actual.hexdigest()}")

    R = json.loads((repo / "ssot_nb01/04_NB08_RQ1_RESULTS_v001.json").read_text())
    C = json.loads((repo / "ssot_nb01/06_NB08_RQ1_SSOT_CLOSEOUT_v001.json").read_text())

    con = duckdb.connect()
    con.execute("SET memory_limit='5GB'"); con.execute("SET threads=8")
    rel = f"read_parquet('{d04.as_posix()}')"
    hist = con.execute(
        f"SELECT floor(log_token_premium/{BIN})*{BIN} b, count(*) n FROM {rel} GROUP BY 1 ORDER BY 1"
    ).fetchall()
    topv = con.execute(
        f"SELECT log_token_premium lg, any_value(token_premium) tp, count(*) k "
        f"FROM {rel} GROUP BY 1 ORDER BY k DESC LIMIT 12"
    ).fetchall()
    qs = [0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]
    quant = con.execute(f"SELECT quantile_cont(log_token_premium, {qs}) FROM {rel}").fetchone()[0]
    con.close()

    payload = {
        "schema": "RQ1_VISUAL_DATA_v001",
        "provenance": {
            "base_main_sha": BASE_MAIN_SHA,
            "rq1_closeout_sha": RQ1_CLOSEOUT_SHA,
            "primary_result_sha": PRIMARY_RESULT_SHA,
            "d04_sha256": D04_SHA256,
            "pair_set_hash": PAIR_SET_HASH,
            "note": "집계값만 포함한다. 원문 KO/EN, pair_id, 형태소 표면형은 포함하지 않는다.",
        },
        "authority": {  # 검정·bootstrap 수치는 재계산하지 않고 그대로 복사한다
            "N": R["primary"]["n"],
            "median_logTP": R["primary"]["median_logTP"],
            "median_TP_scale": R["primary"]["exp_median_logTP"],
            "bootstrap_ci95": R["primary"]["bootstrap_ci95"],
            "share_TP_gt_1": R["primary"]["share_TP_gt_1"],
            "sign_positive": R["primary"]["sign_test"]["positive"],
            "sign_negative": R["primary"]["sign_test"]["negative"],
            "sign_ties": R["primary"]["sign_test"]["ties"],
            "known": {
                "N": R["sensitivity_known_direction"]["n"],
                "median_logTP": R["sensitivity_known_direction"]["median_logTP"],
                "median_TP_scale": R["sensitivity_known_direction"]["exp_median_logTP"],
                "share_TP_gt_1": R["sensitivity_known_direction"]["share_TP_gt_1"],
            },
            "tie_aware": {
                "primary": C["TIE_AWARE_MEDIAN_SIGN_ROBUSTNESS"]["PRIMARY_FINAL_COHORT"]["point_estimate"],
                "known": C["TIE_AWARE_MEDIAN_SIGN_ROBUSTNESS"]["KNOWN_DIRECTION_ONLY"]["point_estimate"],
            },
            "point_mass_at_median": C["CI_DEGENERACY"]["point_mass_at_median"],
            "point_mass_rank_span": C["CI_DEGENERACY"]["point_mass_rank_span"],
            "order_stat_rank_low": C["CI_DEGENERACY"]["order_statistic_interval"]["rank_low"],
            "order_stat_rank_high": C["CI_DEGENERACY"]["order_statistic_interval"]["rank_high"],
            "order_stat_ci95": C["CI_DEGENERACY"]["order_statistic_interval"]["ci95"],
            "stratified_ci95": C["SOURCE_STRATIFIED_BOOTSTRAP_SENSITIVITY"]["ci95"],
            "per_source": C["INTERPRETATION"]["per_source"],
        },
        "descriptive_from_d04": {
            "bin_width": BIN,
            "histogram": [[round(b, 10), int(n)] for b, n in hist],
            "top_lattice": [[lg, tp, int(k)] for lg, tp, k in topv],
            "quantile_levels": qs,
            "quantile_values": list(quant),
        },
        "extracted_at_kst": dt.datetime.now(KST).isoformat(timespec="seconds"),
    }
    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(f"추출 완료: {DATA.relative_to(HERE)}  ({DATA.stat().st_size:,} bytes)")


# ── figures ──────────────────────────────────────────────────────────────────
def korean_font() -> font_manager.FontProperties:
    sample = "한글 토큰 재현"
    priorities = ("Noto Sans CJK KR", "Noto Sans KR", "NanumGothic")
    cands = []
    for p in font_manager.findSystemFonts():
        try:
            f = FT2Font(Path(p)); fam, cmap = f.family_name, f.get_charmap()
        except (RuntimeError, OSError):
            continue
        if fam in priorities and all(ord(c) in cmap for c in sample if "가" <= c <= "힣"):
            cands.append((priorities.index(fam), fam, p))
    if not cands:
        raise SystemExit("한글 glyph를 제공하는 font를 찾지 못했다")
    _, fam, path = sorted(cands, key=lambda t: (t[0], t[2]))[0]
    print(f"  font: {fam}")
    return font_manager.FontProperties(fname=path)


def rname(tp: float) -> str:
    from fractions import Fraction
    f = Fraction(tp).limit_denominator(40)
    return f"{f.numerator}/{f.denominator}"


def build_figures() -> dict:
    if not DATA.exists():
        raise SystemExit(f"visual data가 없다. 먼저 --mode extract 를 실행하라: {DATA}")
    D = json.loads(DATA.read_text())
    A = D["authority"]
    X = D["descriptive_from_d04"]

    FP = korean_font()
    matplotlib.rcParams.update({
        "axes.unicode_minus": False, "svg.fonttype": "none",
        "svg.hashsalt": "koen-tokenization-premium-v1", "pdf.fonttype": 42,
        "font.family": FP.get_name(),
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "axes.edgecolor": "#c3c2b7", "axes.linewidth": 0.8,
        "xtick.color": MUTED, "ytick.color": MUTED,
        "xtick.labelsize": 8, "ytick.labelsize": 8,
        "axes.labelcolor": INK2, "text.color": INK,
        "axes.labelsize": 9, "axes.titlesize": 10,
        "legend.frameon": False, "legend.fontsize": 8, "figure.dpi": 300,
    })

    N = A["N"]; MED = A["median_logTP"]; MED_TP = A["median_TP_scale"]
    POS, NEG, TIE = A["sign_positive"], A["sign_negative"], A["sign_ties"]
    HIST = [(b, n) for b, n in X["histogram"]]

    def save(fig, stem):
        FIGDIR.mkdir(parents=True, exist_ok=True)
        out = {}
        # 생성시각을 명시적으로 제거해야 SVG/PDF가 byte-reproducible해진다.
        # matplotlib은 Date/CreationDate가 None이면 해당 metadata를 생략한다.
        META = {
            "svg": {"Creator": "KOEN NB08 RQ1 figure builder", "Date": None},
            "pdf": {"Creator": "KOEN NB08 RQ1 figure builder", "CreationDate": None},
            "png": {"Software": "KOEN NB08 RQ1 figure builder"},
        }
        for ext, kw in (("svg", {}), ("png", {"dpi": 300}), ("pdf", {})):
            p = FIGDIR / f"{stem}.{ext}"
            fig.savefig(p, format=ext, bbox_inches="tight", metadata=META[ext], **kw)
            out[ext] = {"path": f"figures/{p.name}",
                        "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
        plt.close(fig)
        return out

    def stamp(fig, fid, gap=0.0):
        h = fig.get_size_inches()[1]
        step = 0.16 / h
        y0 = -0.035 - gap
        fig.text(0.0, y0, CAPTIONS[fid], ha="left", va="top", fontsize=7.0,
                 color=INK2, fontproperties=FP, wrap=True)
        fig.text(0.0, y0 - step, f"{fid} · {FIG_STAMP}", ha="left", va="top",
                 fontsize=6, color=MUTED, fontproperties=FP)

    made = {}

    # ── V01 ──────────────────────────────────────────────────────────────────
    lo, hi = -1.0, 1.3
    bins = [(b, n) for b, n in HIST if lo <= b < hi]
    below = sum(n for b, n in HIST if b < lo); above = sum(n for b, n in HIST if b >= hi)
    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(7.0, 5.0),
                                  gridspec_kw={"height_ratios": [2.6, 1.0], "hspace": 0.38})
    xs = [b + BIN / 2 for b, _ in bins]; ys = [n for _, n in bins]
    ax.bar(xs, ys, width=BIN * 0.86, color=ACCENT, edgecolor="none", zorder=3)
    ax.axvline(0.0, color=INK2, lw=1.0, ls=(0, (5, 3)), zorder=4)
    ax.axvline(MED, color=INK, lw=1.4, zorder=5)
    ax.plot([MED], [max(ys) * 1.045], marker="v", ms=6, color=INK, zorder=6, clip_on=False)
    ax.annotate("parity\nlogTP = 0", xy=(0.0, max(ys) * 0.30), xytext=(-0.60, max(ys) * 0.38),
                fontsize=7.5, color=INK2, fontproperties=FP,
                arrowprops=dict(arrowstyle="-", color=INK2, lw=0.7))
    ax.annotate(f"Median(logTP) = {MED:.4f} = ln(4/3)\nMedian TP scale = {MED_TP:.4f}",
                xy=(MED, max(ys) * 0.60), xytext=(MED + 0.20, max(ys) * 0.66),
                fontsize=7.5, color=INK, fontproperties=FP,
                arrowprops=dict(arrowstyle="-", color=INK, lw=0.7))
    ax.text(0.015, 0.96, f"N = {N:,}", transform=ax.transAxes, ha="left", va="top",
            fontsize=8.5, color=INK, fontproperties=FP)
    ax.text(0.015, 0.885, f"표시 구간 밖 합산: 좌 {below:,} · 우 {above:,}", transform=ax.transAxes,
            ha="left", va="top", fontsize=7, color=MUTED, fontproperties=FP)
    ax.set_xlim(lo, hi); ax.set_ylim(0, max(ys) * 1.12)
    ax.set_xlabel("log_token_premium  (bin 폭 0.05, discrete lattice)", fontproperties=FP)
    ax.set_ylabel("pair 수", fontproperties=FP)
    ax.set_title("NB08-RQ1-V01 · Primary Token Premium 분포", fontproperties=FP, loc="left", color=INK)
    ax.yaxis.set_major_formatter(lambda v, _: f"{v/1000:.0f}k" if v else "0")
    ax.grid(axis="y", color=RULE, lw=0.7, zorder=0)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax2.step(X["quantile_values"], X["quantile_levels"], where="post", color=ACCENT, lw=1.6)
    ax2.plot(X["quantile_values"], X["quantile_levels"], "o", ms=3.4, color=ACCENT, mec=SURFACE, mew=0.9)
    ax2.axvline(0.0, color=INK2, lw=1.0, ls=(0, (5, 3)))
    ax2.axvline(MED, color=INK, lw=1.2)
    ax2.set_xlim(lo, hi); ax2.set_ylim(0, 1.02)
    ax2.set_xlabel("log_token_premium", fontproperties=FP)
    ax2.set_ylabel("누적 비율", fontproperties=FP)
    ax2.set_title("누적 분포 (quantile 9점, 보간 없음)", fontproperties=FP, loc="left",
                  fontsize=8.5, color=INK2)
    ax2.grid(axis="y", color=RULE, lw=0.7)
    for s in ("top", "right"): ax2.spines[s].set_visible(False)
    stamp(fig, "NB08-RQ1-V01")
    made["NB08-RQ1-V01"] = save(fig, "NB08_RQ1_V01_distribution")

    # ── V02 ──────────────────────────────────────────────────────────────────
    cats = [("TP > 1", POS, ACCENT, ""), ("TP = 1", TIE, NEUTRAL, "///"), ("TP < 1", NEG, COUNTER, "xxx")]
    fig, ax = plt.subplots(figsize=(7.0, 2.05))
    left = 0.0
    for label, cnt, col, hatch in cats:
        w = 100.0 * cnt / N
        ax.barh(0, w, left=left, height=0.40, color=col, edgecolor=SURFACE,
                linewidth=1.6, hatch=hatch, zorder=3)
        if w > 12:
            ax.text(left + w / 2, 0, f"{w:.4f}%", ha="center", va="center",
                    fontsize=9.5, color="#ffffff", fontproperties=FP, zorder=4)
        left += w
    ax.set_xlim(0, 100); ax.set_ylim(-0.34, 0.52); ax.set_yticks([]); ax.set_xlabel("")
    ax.set_title("NB08-RQ1-V02 · pair polarity 구성", fontproperties=FP, loc="left", color=INK)
    for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
    handles = [Patch(facecolor=c, hatch=h, edgecolor=SURFACE, linewidth=1.2,
                     label=f"{l}\n{n:,}  ({100*n/N:.4f}%)") for l, n, c, h in cats]
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(0, -0.30), ncol=3,
              prop=FP, handlelength=1.5, columnspacing=2.4, handletextpad=0.7)
    ax.text(1.0, 1.02, f"N = {N:,}", transform=ax.transAxes, ha="right", va="bottom",
            fontsize=8.5, color=INK2, fontproperties=FP)
    stamp(fig, "NB08-RQ1-V02", gap=0.40)
    made["NB08-RQ1-V02"] = save(fig, "NB08_RQ1_V02_polarity")

    # ── V03 ──────────────────────────────────────────────────────────────────
    want = [1.0, 1.25, 4/3, 1.4, 1.5, 5/3, 2.0]
    top8 = sorted(X["top_lattice"], key=lambda r: -r[2])[:8]
    have = {round(r[1], 6) for r in top8}
    missing = [w for w in want if round(w, 6) not in have]
    if missing:
        raise SystemExit(f"필수 TP 값이 상위 빈도에 없다: {missing}")
    rows = sorted(top8, key=lambda r: r[0])
    kmax = max(r[2] for r in rows)
    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(7.0, 5.2),
                                  gridspec_kw={"height_ratios": [2.5, 1.0], "hspace": 0.55})
    for i, (lg, tp, k) in enumerate(rows):
        is_med = abs(lg - MED) < 1e-12
        col = ACCENT if is_med else NEUTRAL
        ax.vlines(lg, 0, k, color=col, lw=2.4 if is_med else 1.6, zorder=3)
        ax.plot([lg], [k], "o" if is_med else "s", ms=8 if is_med else 5.5,
                color=col, mec=SURFACE, mew=1.4, zorder=4)
        if is_med:
            continue
        off = kmax * (0.045 if i % 2 == 0 else 0.135)
        ax.plot([lg, lg], [k + kmax * 0.012, k + off - kmax * 0.012], color=RULE, lw=0.7, zorder=2)
        ax.text(lg, k + off, f"TP={rname(tp)}", ha="center", va="bottom",
                fontsize=7.2, color=MUTED, fontproperties=FP)
    ax.axvline(MED, color=INK, lw=0.9, ls=(0, (4, 3)), zorder=1)
    mass = A["point_mass_at_median"]
    ax.annotate(f"median lattice point  TP = 4/3\n{mass:,} observations  ({mass/N:.4%})",
                xy=(MED, mass), xytext=(MED - 0.30, kmax * 0.80),
                fontsize=8.2, color=INK, fontproperties=FP, ha="left",
                arrowprops=dict(arrowstyle="->", color=INK, lw=0.9,
                                connectionstyle="arc3,rad=-0.12"))
    ax.set_xlabel("log_token_premium (exact lattice point)", fontproperties=FP)
    ax.set_ylabel("pair 수", fontproperties=FP)
    ax.set_title("NB08-RQ1-V03 · median CI가 퇴화하는 이유 — outcome은 이산 격자다",
                 fontproperties=FP, loc="left", color=INK)
    ax.yaxis.set_major_formatter(lambda v, _: f"{v/1000:.0f}k" if v else "0")
    ax.grid(axis="y", color=RULE, lw=0.7, zorder=0)
    ax.set_ylim(0, kmax * 1.34)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    lo_r, hi_r = A["point_mass_rank_span"]
    ci_lo, ci_hi = A["order_stat_rank_low"], A["order_stat_rank_high"]
    pad = (hi_r - lo_r) * 0.42; x0, x1 = lo_r - pad, hi_r + pad
    ax2.axhspan(-0.30, 0.30, xmin=(lo_r - x0) / (x1 - x0), xmax=(hi_r - x0) / (x1 - x0),
                color=ACCENT, alpha=0.16, zorder=1)
    ax2.hlines(0, x0, x1, color="#c3c2b7", lw=1.0, zorder=2)
    ax2.vlines([lo_r, hi_r], -0.30, 0.30, color=ACCENT, lw=1.4, zorder=3)
    ax2.vlines([ci_lo, ci_hi], -0.20, 0.20, color=INK, lw=1.8, zorder=4)
    ax2.plot([N // 2], [0], "o", ms=6, color=INK, mec=SURFACE, mew=1.2, zorder=5)
    ax2.text((lo_r + hi_r) / 2, 0.46, f"TP = 4/3 point mass · 순위 {lo_r:,} – {hi_r:,}",
             ha="center", fontsize=8, color=INK, fontproperties=FP)
    ax2.text((ci_lo + ci_hi) / 2, -0.62,
             f"order-statistic 95% CI 순위 {ci_lo:,} – {ci_hi:,}\n두 끝점이 모두 point mass 내부 → CI 퇴화",
             ha="center", va="top", fontsize=7.8, color=INK2, fontproperties=FP)
    ax2.set_xlim(x0, x1); ax2.set_ylim(-1.15, 0.78); ax2.set_yticks([])
    ax2.set_xlabel("정렬된 표본의 순위", fontproperties=FP)
    ax2.xaxis.set_major_formatter(lambda v, _: f"{v/1e6:.2f}M")
    for s in ("top", "right", "left"): ax2.spines[s].set_visible(False)
    stamp(fig, "NB08-RQ1-V03")
    made["NB08-RQ1-V03"] = save(fig, "NB08_RQ1_V03_lattice_ci")

    # ── V04 ──────────────────────────────────────────────────────────────────
    K = A["known"]
    rows4 = [("PRIMARY FINAL COHORT", N, MED, MED_TP, A["share_TP_gt_1"],
              A["tie_aware"]["primary"], ACCENT, "o"),
             ("KNOWN DIRECTION ONLY", K["N"], K["median_logTP"], K["median_TP_scale"],
              K["share_TP_gt_1"], A["tie_aware"]["known"], SECOND, "s")]
    fig = plt.figure(figsize=(7.0, 3.5))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.0, 1.5], hspace=0.05)
    ax, axt = fig.add_subplot(gs[0]), fig.add_subplot(gs[1])
    for i, (lab, n, med, tp, p1, ptie, col, mk) in enumerate(rows4):
        ax.plot([med], [1 - i], mk, ms=11, color=col, mec=SURFACE, mew=1.8, zorder=4)
        ax.text(med + 0.00055, 1 - i, f"  {lab}", ha="left", va="center", fontsize=8.4,
                color=INK, fontproperties=FP)
    ax.axvline(MED, color=INK, lw=0.8, ls=(0, (4, 3)), zorder=1)
    ax.set_xlim(MED - 0.0022, MED + 0.0050); ax.set_ylim(-0.95, 1.55); ax.set_yticks([])
    ax.set_xticks([MED]); ax.set_xticklabels([f"ln(4/3) = {MED:.7f}"], fontproperties=FP, fontsize=8)
    ax.text(MED - 0.0019, 1.44, "DEGENERATE AT LATTICE POINT — CI 폭 0", ha="left", va="top",
            fontsize=7.6, color=INK2, fontproperties=FP)
    ax.text(MED - 0.0019, -0.72,
            "pair-level bootstrap CI · source-stratified bootstrap CI 모두 동일 지점에서 퇴화",
            ha="left", va="center", fontsize=7.2, color=MUTED, fontproperties=FP)
    ax.set_title("NB08-RQ1-V04 · robustness / sensitivity 요약", fontproperties=FP, loc="left", color=INK)
    for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
    axt.axis("off")
    hdr = ["cohort", "N", "Median(logTP)", "TP scale", "P(TP>1)", "tie-aware\nP(Y>0)"]
    cells = [[lab, f"{n:,}", f"{med:.7f}", f"{tp:.6f}", f"{p1:.4%}", f"{ptie:.6f}"]
             for lab, n, med, tp, p1, ptie, _, _ in rows4]
    t = axt.table(cellText=cells, colLabels=hdr,
                  colWidths=[0.27, 0.145, 0.165, 0.145, 0.14, 0.135], cellLoc="right", loc="center")
    t.auto_set_font_size(False); t.set_fontsize(8); t.scale(1, 1.9)
    for (r, c), cell in t.get_celld().items():
        cell.set_edgecolor(RULE); cell.set_linewidth(0.6); cell.PAD = 0.07
        cell.get_text().set_fontproperties(FP)
        if r == 0:
            cell.get_text().set_color(MUTED); cell.set_facecolor(SURFACE)
            cell.get_text().set_fontsize(7.4)
        if c == 0:
            cell.get_text().set_ha("left"); cell.PAD = 0.035
            if r > 0:
                cell.get_text().set_color(rows4[r - 1][6]); cell.get_text().set_fontsize(7.6)
    axt.text(0.5, 0.02, "Wilcoxon signed-rank: p < 1e-300 (두 cohort 모두)   ·   "
                        "tie-aware robustness는 tie를 denominator에 유지한 보수적 검정",
             transform=axt.transAxes, ha="center", va="bottom", fontsize=7.4,
             color=INK2, fontproperties=FP)
    stamp(fig, "NB08-RQ1-V04")
    made["NB08-RQ1-V04"] = save(fig, "NB08_RQ1_V04_robustness")

    # ── S01 ──────────────────────────────────────────────────────────────────
    ps_ = A["per_source"]; ks = sorted(ps_)
    meds = [ps_[k]["median_logTP"] for k in ks]
    prs = [ps_[k]["P_TP_gt_1"] for k in ks]
    ns = [ps_[k]["n"] for k in ks]
    cols, hats = [ACCENT, SECOND], ["", "///"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.0, 2.9), gridspec_kw={"wspace": 0.34})
    for ax_, vals, ttl, fmt, lim in (
        (a1, meds, "Median(logTP)", lambda v: f"{v:.5f}", (0, max(meds) * 1.30)),
        (a2, prs, "P(TP > 1)", lambda v: f"{v:.2%}", (0, 1.12)),
    ):
        for i, v in enumerate(vals):
            ax_.bar(i, v, width=0.52, color=cols[i], hatch=hats[i],
                    edgecolor=SURFACE, linewidth=1.4, zorder=3)
            ax_.text(i, v * 1.02, fmt(v), ha="center", va="bottom", fontsize=8.4,
                     color=INK, fontproperties=FP)
        ax_.set_xticks(range(len(ks)))
        ax_.set_xticklabels([f"{k}-family\nn={n:,}" for k, n in zip(ks, ns)],
                            fontproperties=FP, fontsize=8)
        ax_.set_ylim(*lim); ax_.set_title(ttl, fontproperties=FP, loc="left", fontsize=9, color=INK2)
        ax_.grid(axis="y", color=RULE, lw=0.7, zorder=0)
        for s in ("top", "right"): ax_.spines[s].set_visible(False)
    a2.yaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
    fig.suptitle("NB08-RQ1-S01 · DESCRIPTIVE SOURCE STRATA — NOT SOURCE EFFECT",
                 fontproperties=FP, x=0.02, ha="left", fontsize=10, color=INK, y=1.045)
    stamp(fig, "NB08-RQ1-S01", gap=0.06)
    made["NB08-RQ1-S01"] = save(fig, "NB08_RQ1_S01_source_strata")

    return made


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="NB08 RQ1 figure builder")
    ap.add_argument("--mode", choices=("extract", "figures"), default="figures")
    ap.add_argument("--repo", default="/home/sieg/projects-wsl/Tokenization_KOEN",
                    help="canonical tree (extract 모드에서 D-04 위치)")
    a = ap.parse_args()
    if a.mode == "extract":
        extract(Path(a.repo))
    else:
        m = build_figures()
        (HERE / "_figures.json").write_text(
            json.dumps(m, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
        for k in m:
            print(f"  {k} done")
        print(f"\n생성 완료: figures/  ({len(m)} figures × 3 formats)")
