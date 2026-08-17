"""NB06 / D-05 결과 figure 생성기.

입력은 커밋된 data/NB06_D05_VISUAL_DATA_v001.json 하나뿐이다. canonical parquet을
읽지 않으므로 Git checkout만으로 동일한 figure를 재생성할 수 있다 (REPRODUCE.md LEVEL A).

figure 이름은 NB06_D05_Vxx이며, SSOT §16.2의 canonical F01-F09 이름은 쓰지 않는다.
이 figure들은 measurement-result visualization 전용이다.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

# SVG 내부 요소 id는 기본적으로 실행마다 달라진다. salt를 고정해야 파일 hash가 재현된다.
matplotlib.rcParams["svg.hashsalt"] = "NB06_D05_v001"
# NanumGothic에는 bold weight가 없어 600으로 대체된다. 결과에 영향이 없는 경고라 낮춘다.
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

HERE = Path(__file__).resolve().parent
DATA = HERE / "data/NB06_D05_VISUAL_DATA_v001.json"
FIGURES = HERE / "figures"

KO_COLOR = "#c0392b"
EN_COLOR = "#2980b9"
NEUTRAL = "#5d6d7e"
OK_COLOR = "#1e8449"
INK = "#1c2833"

PLAIN = FuncFormatter(lambda v, _: f"{v:g}")


def setup_font() -> str:
    """한국어 label을 쓰기 위해 설치된 폰트를 찾는다. 없으면 영어 label로 떨어진다."""
    from matplotlib import font_manager

    for family in ("NanumGothic", "Noto Sans CJK KR", "Malgun Gothic", "AppleGothic"):
        try:
            font_manager.findfont(family, fallback_to_default=False)
        except Exception:  # noqa: BLE001 - 폰트 조회 실패 사유는 구분할 필요가 없다
            continue
        plt.rcParams["font.family"] = family
        plt.rcParams["axes.unicode_minus"] = False
        return family
    plt.rcParams["axes.unicode_minus"] = False
    return "DEFAULT_LATIN_ONLY"


def save(fig: plt.Figure, stem: str) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    for suffix in ("svg", "png"):
        # metadata를 비워야 실행 시각이 파일에 섞이지 않아 hash가 재현된다.
        meta = {"Date": None} if suffix == "svg" else {"Software": None}
        fig.savefig(FIGURES / f"{stem}.{suffix}", dpi=160, bbox_inches="tight", metadata=meta)
    plt.close(fig)
    print(f"  wrote figures/{stem}.svg, figures/{stem}.png")


# --------------------------------------------------------------------------- V01
def figure_v01_pipeline_boundary(d: dict) -> None:
    """세 경계가 서로 다르다는 것을 그림으로 못박는다."""
    fig, ax = plt.subplots(figsize=(12.5, 6.2))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 62)
    ax.axis("off")

    def box(x, y, w, h, label, sub, color, fc="white"):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.6",
                                    linewidth=1.6, edgecolor=color, facecolor=fc))
        ax.text(x + w / 2, y + h * 0.62, label, ha="center", va="center",
                fontsize=10.5, color=INK, fontweight="bold")
        ax.text(x + w / 2, y + h * 0.26, sub, ha="center", va="center",
                fontsize=8.4, color=NEUTRAL)

    def arrow(x1, y1, x2, y2, color=NEUTRAL):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                     mutation_scale=13, linewidth=1.3, color=color))

    ax.text(50, 59, "측정 대상 경계 (measurement boundaries)", ha="center",
            fontsize=13, fontweight="bold", color=INK)

    # --- tokenizer 경로 (측정 대상) -----------------------------------------
    ax.text(2, 49.5, "tokenizer 내부 경로", fontsize=9.5, color=INK, fontweight="bold")
    box(2, 36, 19, 11, "raw analysis text", "ko_text_analysis / en_text_analysis", NEUTRAL)
    arrow(21, 41.5, 26, 41.5)
    box(26, 36, 19, 11, "regex chunks", "o200k_base pat_str · P_v", KO_COLOR, "#fdf2f0")
    arrow(45, 41.5, 50, 41.5)
    box(50, 36, 20, 11, "final subword tokens", "mergeable ranks / BPE", EN_COLOR, "#eef5fb")
    arrow(70, 41.5, 75, 41.5)
    box(75, 36, 23, 11, "D-04 Token Measurement", "token counts · Tokenization Premium", INK)

    ax.annotate("D-05 Regex Chunk Measurement\n(여기를 측정한다)",
                xy=(35.5, 36), xytext=(35.5, 27),
                ha="center", fontsize=9.4, color=KO_COLOR, fontweight="bold",
                arrowprops={"arrowstyle": "-|>", "color": KO_COLOR, "linewidth": 1.3})
    ax.annotate("D-04가 token 수 / TP의 유일한 authority",
                xy=(86.5, 36), xytext=(86.5, 29),
                ha="center", fontsize=8.8, color=INK,
                arrowprops={"arrowstyle": "-|>", "color": INK, "linewidth": 1.1})

    # --- morphology 경로 (별개) ----------------------------------------------
    ax.text(2, 18.5, "언어학적 분석 경로 (별개 경로)", fontsize=9.5, color=INK,
            fontweight="bold")
    box(2, 5, 19, 11, "raw analysis text", "동일한 입력 텍스트", NEUTRAL)
    arrow(21, 10.5, 26, 10.5, OK_COLOR)
    box(26, 19.5, 0.001, 0.001, "", "", "white", "white")   # 레이아웃 여백
    box(26, 5, 24, 11, "linguistic morphology", "Kiwi morpheme / POS · D-03", OK_COLOR,
        "#eef7f1")

    ax.plot([23.5, 23.5], [4, 48], linestyle=(0, (4, 4)), color="#95a5a6", linewidth=1.0)
    ax.text(56, 10.5,
            "morpheme 경계는 regex chunk 경계와\n일치할 필요가 없고, 둘 다\n"
            "final subword token 경계와도 다르다.",
            fontsize=9.2, color=INK, va="center")

    ax.text(50, 0.5,
            "linguistic morphology  ≠  tokenizer regex chunking  ≠  final subword tokenization",
            ha="center", fontsize=10.2, color=INK, fontweight="bold")

    save(fig, "NB06_D05_V01_pipeline_boundary")


# --------------------------------------------------------------------------- V02
def figure_v02_chunk_vs_token_expansion(d: dict) -> None:
    """가장 중요한 figure: 두 축이 반대 방향으로 움직인다."""
    ko, en = d["side_profile"]["ko"], d["side_profile"]["en"]
    dec = d["decomposition"]
    n = d["population"]["n_pairs"]

    fig = plt.figure(figsize=(14.5, 5.6))
    grid = fig.add_gridspec(1, 3, width_ratios=[1, 1, 1.35], wspace=0.32)

    # (1) chunk 수
    ax1 = fig.add_subplot(grid[0, 0])
    bars = ax1.bar(["KO", "EN"], [ko["mean_chunk_count"], en["mean_chunk_count"]],
                   color=[KO_COLOR, EN_COLOR], width=0.55)
    ax1.set_title("regex chunk 수 (ko/en_chunk_count)", fontsize=11)
    ax1.set_ylabel("pair-side 평균")
    ax1.set_ylim(0, max(ko["mean_chunk_count"], en["mean_chunk_count"]) * 1.28)
    for bar, value in zip(bars, [ko["mean_chunk_count"], en["mean_chunk_count"]], strict=True):
        ax1.text(bar.get_x() + bar.get_width() / 2, value, f"{value:.2f}",
                 ha="center", va="bottom", fontsize=11, fontweight="bold")
    ax1.text(0.5, 0.93, "KO가 더 적다", transform=ax1.transAxes, ha="center",
             fontsize=9.6, color=KO_COLOR, fontweight="bold")

    # (2) chunk당 token 수
    ax2 = fig.add_subplot(grid[0, 1])
    bars = ax2.bar(["KO", "EN"], [ko["mean_tokens_per_chunk"], en["mean_tokens_per_chunk"]],
                   color=[KO_COLOR, EN_COLOR], width=0.55)
    ax2.set_title("chunk당 token 수 (tokens_per_chunk)", fontsize=11)
    ax2.set_ylabel("pair-side 평균")
    ax2.set_ylim(0, max(ko["mean_tokens_per_chunk"], en["mean_tokens_per_chunk"]) * 1.28)
    for bar, value in zip(bars,
                          [ko["mean_tokens_per_chunk"], en["mean_tokens_per_chunk"]],
                          strict=True):
        ax2.text(bar.get_x() + bar.get_width() / 2, value, f"{value:.2f}",
                 ha="center", va="bottom", fontsize=11, fontweight="bold")
    ax2.text(0.5, 0.93, "KO가 훨씬 크다", transform=ax2.transAxes, ha="center",
             fontsize=9.6, color=KO_COLOR, fontweight="bold")

    # (3) 로그 분해: 두 항이 반대 부호
    ax3 = fig.add_subplot(grid[0, 2])
    chunk_term = dec["mean_log_chunk_count_term"]
    density_term = dec["mean_log_tokens_per_chunk_term"]
    total = dec["mean_log_token_ratio"]
    labels = ["chunk 수 축\nln(C_ko/C_en)", "chunk당 token 축\nln(density ratio)",
              "합계\nln(N_ko/N_en)"]
    values = [chunk_term, density_term, total]
    colors = [KO_COLOR if v < 0 else EN_COLOR for v in values[:2]] + [INK]
    bars = ax3.barh(labels, values, color=colors, height=0.55)
    ax3.axvline(0, color=INK, linewidth=1.0)
    ax3.set_title("두 축은 반대 방향으로 움직인다 (log 분해)", fontsize=11)
    ax3.set_xlabel("평균 로그 비")
    span = max(abs(v) for v in values)
    ax3.set_xlim(-span * 1.45, span * 1.45)
    for bar, value in zip(bars, values, strict=True):
        offset = span * 0.05 * (1 if value >= 0 else -1)
        ax3.text(value + offset, bar.get_y() + bar.get_height() / 2, f"{value:+.4f}",
                 va="center", ha="left" if value >= 0 else "right",
                 fontsize=10, fontweight="bold")
    ax3.invert_yaxis()
    ax3.xaxis.set_major_formatter(PLAIN)

    for ax in (ax1, ax2):
        ax.yaxis.set_major_formatter(PLAIN)
        ax.spines[["top", "right"]].set_visible(False)
    ax3.spines[["top", "right"]].set_visible(False)

    fig.suptitle(
        f"한국어는 regex chunk가 더 적지만, chunk 하나가 더 많은 token으로 확장된다   "
        f"(N = {n:,} pairs · o200k_base · Track A)",
        fontsize=12.5, y=1.03)
    save(fig, "NB06_D05_V02_chunk_vs_token_expansion")


# --------------------------------------------------------------------------- V03
def figure_v03_validation(d: dict) -> None:
    """audit dashboard 형태. 화려한 chart보다 통과/실패가 한눈에 보이는 편이 낫다."""
    pilot, validation = d["pilot"], d["validation"]

    fig, (ax_left, ax_right) = plt.subplots(
        1, 2, figsize=(14.5, 6.6), gridspec_kw={"width_ratios": [1, 1.12]})
    for ax in (ax_left, ax_right):
        ax.axis("off")

    inv_labels = {
        "1_concat_reconstruction_failures": "concat 재구성 실패",
        "1b_empty_chunks": "빈 chunk",
        "2_lost_or_duplicated_span": "손실/중복 span",
        "3_chunk_order_nondeterministic": "chunk 순서 비결정성",
        "4_ko_token_id_mismatch": "KO token ID 불일치",
        "4_en_token_id_mismatch": "EN token ID 불일치",
        "5_token_count_mismatch": "token 수 불일치",
        "6_unclassified_chunk_type": "미분류 chunk type",
        "6b_type_share_not_one": "type share 합 != 1",
        "warning_rows": "warning 행",
    }
    ax_left.text(0, 1.0, "Pilot 불변식 (§5)", fontsize=13, fontweight="bold",
                 transform=ax_left.transAxes, color=INK)
    ax_left.text(0, 0.955,
                 f"{pilot['pilot_n']:,} pairs · {pilot['total_chunks_inspected']:,} chunks "
                 f"· salt {pilot['sampling_salt']}",
                 fontsize=9.4, transform=ax_left.transAxes, color=NEUTRAL)
    y = 0.885
    for key, label in inv_labels.items():
        value = pilot["invariants"].get(key, 0)
        mark, color = ("0", OK_COLOR) if value == 0 else (str(value), KO_COLOR)
        ax_left.text(0.02, y, label, fontsize=10.2, transform=ax_left.transAxes, color=INK)
        ax_left.text(0.92, y, mark, fontsize=10.6, transform=ax_left.transAxes,
                     color=color, fontweight="bold", ha="right")
        y -= 0.075
    ax_left.text(0.02, y - 0.02, f"TOTAL MISMATCH  {pilot['total_mismatch']}",
                 fontsize=11.4, transform=ax_left.transAxes,
                 color=OK_COLOR if pilot["total_mismatch"] == 0 else KO_COLOR,
                 fontweight="bold")

    check_labels = {
        "row_count_equals_canonical_cohort": "행 수 = canonical cohort",
        "pair_id_unique": "pair_id 유일",
        "chunk_measurement_id_unique": "chunk_measurement_id 유일",
        "tokenizer_fk_unique": "D-04 외래키 유일",
        "no_missing_vs_d04": "D-04 대비 누락 없음",
        "no_extra_vs_d04": "D-04 대비 잉여 없음",
        "no_orphan_tokenizer_fk": "고아 외래키 없음",
        "pair_set_md5_matches_canonical": "pair-set md5 일치",
        "single_chunking_config": "chunking config 단일",
        "single_pat_str_in_artifact": "pat_str 단일",
        "manifest_schema_version_matches": "schema version 일치",
        "physical_columns_match_schema": "물리 열 = 선언 schema",
        "zero_token_equivalence_failures": "token 등가성 실패 0",
        "zero_reconstruction_failures": "재구성 실패 0",
        "manifest_sha256_matches_artifact": "manifest sha256 일치",
        "manifest_row_count_matches": "manifest 행 수 일치",
        "r1_periodic_telemetry": "R1 주기 telemetry",
    }
    passed = sum(1 for v in validation["checks"].values() if v)
    total = len(validation["checks"])
    ax_right.text(0, 1.0, "전집단 검증", fontsize=13, fontweight="bold",
                  transform=ax_right.transAxes, color=INK)
    ax_right.text(0, 0.955, f"N = {d['population']['n_pairs']:,} · {passed}/{total} PASS",
                  fontsize=9.4, transform=ax_right.transAxes, color=NEUTRAL)
    y = 0.895
    for key, label in check_labels.items():
        ok = bool(validation["checks"].get(key))
        ax_right.text(0.02, y, label, fontsize=9.7, transform=ax_right.transAxes, color=INK)
        ax_right.text(0.95, y, "PASS" if ok else "FAIL", fontsize=9.7,
                      transform=ax_right.transAxes, ha="right",
                      color=OK_COLOR if ok else KO_COLOR, fontweight="bold")
        y -= 0.05

    fig.suptitle("D-05 검증 근거 — chunk 통계가 그럴듯한지가 아니라, "
                 "chunk가 D-04 token을 정확히 재현하는지를 본다",
                 fontsize=12.2, y=1.0)
    save(fig, "NB06_D05_V03_validation")


# --------------------------------------------------------------------------- V04
def figure_v04_runtime(d: dict) -> None:
    """R1이 실행 전 구간을 실제로 관측했음을 보인다."""
    runtime = d["runtime"]
    samples = runtime["samples"]
    t = [s["elapsed_sec"] for s in samples]
    rows = [s["rows_processed"] for s in samples]
    rss = [s["rss_gib"] for s in samples]
    mem = [s["mem_available_gib"] for s in samples]

    fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.6))

    axes[0].plot(t, [r / 1e6 for r in rows], color=INK, linewidth=1.6)
    axes[0].scatter(t, [r / 1e6 for r in rows], s=13, color=INK, zorder=3)
    axes[0].set_title(f"진행 (표본 {runtime['sample_count']}개 · "
                      f"{runtime['interval_sec']:.0f}초 주기)", fontsize=11)
    axes[0].set_ylabel("처리 행 수 (백만)")

    axes[1].plot(t, rss, color=KO_COLOR, linewidth=1.6, label="process RSS")
    axes[1].scatter(t, rss, s=13, color=KO_COLOR, zorder=3)
    axes[1].axhline(6.0, color=KO_COLOR, linestyle="--", linewidth=1.0,
                    label="RED 임계 6.0 GiB")
    axes[1].set_title("프로세스 RSS", fontsize=11)
    axes[1].set_ylabel("GiB")
    axes[1].set_ylim(0, 6.8)
    axes[1].legend(fontsize=8.4, loc="upper left")

    axes[2].plot(t, mem, color=EN_COLOR, linewidth=1.6, label="MemAvailable")
    axes[2].scatter(t, mem, s=13, color=EN_COLOR, zorder=3)
    axes[2].axhline(8.0, color="#b7950b", linestyle=":", linewidth=1.0,
                    label="GREEN 하한 8.0 GiB")
    axes[2].axhline(5.0, color=KO_COLOR, linestyle="--", linewidth=1.0,
                    label="RED 임계 5.0 GiB")
    axes[2].set_title(f"MemAvailable (최소 {runtime['min_mem_available_gib']:.2f} GiB)",
                      fontsize=11)
    axes[2].set_ylabel("GiB")
    axes[2].set_ylim(0, max(mem) * 1.18)
    axes[2].legend(fontsize=8.4, loc="lower left")

    for ax in axes:
        ax.set_xlabel("경과 시간 (초)")
        ax.xaxis.set_major_formatter(PLAIN)
        ax.yaxis.set_major_formatter(PLAIN)
        ax.spines[["top", "right"]].set_visible(False)

    fig.suptitle(
        f"R1 runtime telemetry — 전집단 실행 {runtime['telemetry_elapsed_sec']:.1f}초, "
        f"평균 {runtime['telemetry_mean_rows_per_second']:,.0f} rows/sec, "
        f"RED 이상 표본 {runtime['red_or_worse_sample_count']}개, "
        f"최종 {runtime['final_status']}",
        fontsize=12, y=1.04)
    fig.tight_layout()
    save(fig, "NB06_D05_V04_runtime")


def main() -> None:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    font = setup_font()
    print(f"font family: {font}")
    figure_v01_pipeline_boundary(data)
    figure_v02_chunk_vs_token_expansion(data)
    figure_v03_validation(data)
    figure_v04_runtime(data)


if __name__ == "__main__":
    main()
