"""한글 font 탐색과 PNG/SVG rendering smoke test를 제공한다."""

from __future__ import annotations  # Python 3.12 지연 annotation 평가를 사용한다.

import warnings  # missing glyph 및 font fallback warning을 포착한다.
from pathlib import Path  # font 및 figure artifact 경로를 처리한다.
from typing import Any  # figure validation mapping 타입을 표현한다.

import matplotlib  # headless backend와 rcParams를 명시적으로 설정한다.

matplotlib.use("Agg")  # display server 없이 fresh-kernel figure를 렌더링한다.

import matplotlib.pyplot as plt  # publication figure API를 사용한다.
from matplotlib import font_manager  # 설치된 font 파일을 탐색한다.
from matplotlib.ft2font import FT2Font  # 실제 font cmap에서 한글 glyph를 확인한다.
from PIL import Image  # 저장된 PNG를 다시 열어 artifact integrity를 검사한다.

from tokenization_premium.hashing import sha256_file  # 저장된 figure의 SHA-256을 기록한다.

KOREAN_SAMPLE = "한글 토큰화 재현성 - 마이너스"  # 한글 glyph와 ASCII minus fallback을 함께 검사할 고정 문자열이다.


def find_korean_font() -> dict[str, str]:
    """
    /**
     * @purpose 실제 설치 font의 cmap을 검사해 한글 sample 전체를 지원하는 font를 선택한다.
     * @spec_ref Notebook Constitution §7
     * @return family와 실제 font file path mapping
     * @raises RuntimeError 우선순위 font 중 한글 glyph를 모두 제공하는 파일이 없는 경우
     * @validation sample codepoint가 모두 FT2Font charmap에 존재하는지 검사한다.
     * @artifact ENVIRONMENT_REPRO_v001.json
     */
    """
    priorities = ("Noto Sans CJK KR", "Noto Sans KR", "NanumGothic")  # Research Director가 정한 font 우선순위를 사용한다.
    candidates: list[tuple[int, str, Path]] = []  # 우선순위와 실제 font metadata를 누적한다.
    for font_path_text in font_manager.findSystemFonts():  # 시스템에서 실제 발견된 font 파일만 검사한다.
        font_path = Path(font_path_text)  # 문자열 경로를 안전한 Path 객체로 변환한다.
        try:  # 손상되었거나 지원되지 않는 font 파일을 개별적으로 격리한다.
            font = FT2Font(font_path)  # FreeType을 통해 실제 font metadata와 cmap을 읽는다.
            family = font.family_name  # hard-code가 아닌 파일 내부 family 이름을 사용한다.
            cmap = font.get_charmap()  # font가 제공하는 Unicode codepoint 집합을 읽는다.
        except (RuntimeError, OSError):  # 읽을 수 없는 font는 fallback 없이 제외한다.
            continue  # 다른 실제 설치 font 후보를 계속 검사한다.
        korean_characters = [character for character in KOREAN_SAMPLE if "가" <= character <= "힣"]  # font cmap의 핵심 검사 대상을 완성형 한글로 제한한다.
        if family in priorities and all(ord(character) in cmap for character in korean_characters):  # 한글 glyph를 모두 제공하는지 검사한다.
            candidates.append((priorities.index(family), family, font_path))  # 우선순위와 함께 검증된 후보를 저장한다.
    if not candidates:  # 실제 glyph를 보장하는 font가 없으면 figure 생성을 금지한다.
        raise RuntimeError("한글 glyph를 모두 제공하는 font를 찾지 못했습니다.")  # silent fallback 대신 명시적으로 실패한다.
    _, family, selected_path = sorted(candidates, key=lambda item: (item[0], item[2].as_posix()))[0]  # 우선순위와 경로로 결정론적으로 선택한다.
    return {"family": family, "path": selected_path.as_posix()}  # 실제 사용 family와 file path를 반환한다.


def render_korean_smoke(font_info: dict[str, str], png_path: Path, svg_path: Path) -> dict[str, Any]:
    """
    /**
     * @purpose 한글 title/axis/legend와 Unicode minus를 PNG·SVG로 저장하고 재검증한다.
     * @spec_ref Notebook Constitution §7
     * @param font_info find_korean_font가 반환한 실제 font metadata
     * @param png_path PNG artifact 경로
     * @param svg_path SVG artifact 경로
     * @return 파일 크기, image shape, SHA-256, warning 목록
     * @raises AssertionError missing glyph warning, 빈 PNG, 한글 없는 SVG가 발견된 경우
     * @validation 저장 파일을 Pillow/XML text로 다시 읽고 glyph warning을 검사한다.
     * @artifact outputs/figures/F00_KOREAN_FONT_SMOKE_v001.png/.svg
     */
    """
    png_path.parent.mkdir(parents=True, exist_ok=True)  # 승인된 figure output 경로를 생성한다.
    svg_path.parent.mkdir(parents=True, exist_ok=True)  # PNG와 독립적으로 SVG 상위 경로를 보장한다.
    font_properties = font_manager.FontProperties(fname=font_info["path"])  # 검증된 실제 font 파일을 figure에 직접 연결한다.
    matplotlib.rcParams["axes.unicode_minus"] = False  # Matplotlib minus glyph fallback 문제를 통제한다.
    matplotlib.rcParams["svg.fonttype"] = "none"  # SVG에 한글 text를 보존해 재검증 가능하게 한다.
    matplotlib.rcParams["svg.hashsalt"] = "koen-tokenization-premium-v1"  # SVG element ID를 실행마다 동일하게 만든다.
    with warnings.catch_warnings(record=True) as captured:  # rendering 중 발생하는 glyph warning을 수집한다.
        warnings.simplefilter("always")  # 이미 발생한 warning도 숨기지 않고 모두 기록한다.
        figure, axis = plt.subplots(figsize=(7.2, 4.2), dpi=120)  # 고정 크기와 DPI로 deterministic smoke figure를 만든다.
        axis.plot([-2, -1, 0, 1, 2], [4, 1, 0, 1, 4], marker="o", label="토큰 수 예시")  # Unicode minus가 필요한 음수 tick과 한글 legend를 만든다.
        axis.set_title(KOREAN_SAMPLE, fontproperties=font_properties)  # 한글 title을 실제 선택 font로 렌더링한다.
        axis.set_xlabel("문장 위치", fontproperties=font_properties)  # 한글 x축 label을 검증한다.
        axis.set_ylabel("상대 토큰 수", fontproperties=font_properties)  # 한글 y축 label을 검증한다.
        axis.legend(prop=font_properties)  # 한글 legend에도 동일 font 파일을 강제한다.
        figure.tight_layout()  # label clipping 없이 고정 layout을 만든다.
        figure.savefig(png_path, format="png", metadata={"Software": "Tokenization Premium Phase 0"})  # 고정 metadata로 PNG를 저장한다.
        figure.savefig(svg_path, format="svg", metadata={"Date": "2026-08-16", "Creator": "Tokenization Premium Phase 0"})  # 고정 metadata로 SVG를 저장한다.
        plt.close(figure)  # hidden notebook state와 figure 누수를 제거한다.
    warning_messages = [str(item.message) for item in captured]  # warning 객체를 JSON 직렬화 가능한 문자열로 변환한다.
    missing_glyph_warnings = [message for message in warning_messages if "Glyph" in message and "missing" in message]  # 한글 깨짐과 직접 관련된 warning만 분리한다.
    if missing_glyph_warnings:  # silent font fallback을 허용하지 않는다.
        raise AssertionError(missing_glyph_warnings)  # 저장된 figure를 PASS로 승격하지 않고 중단한다.
    with Image.open(png_path) as image:  # 저장된 PNG를 다시 열어 decoder 수준 무결성을 검사한다.
        image_shape = [image.height, image.width, len(image.getbands())]  # height, width, channel 의미가 명시된 shape를 기록한다.
        extrema = image.convert("L").getextrema()  # 빈 단색 이미지 여부를 검사할 밝기 범위를 읽는다.
    svg_text = svg_path.read_text(encoding="utf-8")  # SVG를 UTF-8 text artifact로 다시 읽는다.
    if extrema[0] == extrema[1] or "한글" not in svg_text:  # 이미지 내용 또는 SVG 한글 text가 없으면 실패한다.
        raise AssertionError("저장된 한글 figure artifact 검증에 실패했습니다.")  # 깨진 artifact가 manifest에 들어가지 않게 중단한다.
    return {"font": font_info, "png_sha256": sha256_file(png_path), "svg_sha256": sha256_file(svg_path), "png_size_bytes": png_path.stat().st_size, "svg_size_bytes": svg_path.stat().st_size, "image_shape_hwc": image_shape, "warnings": warning_messages}  # 검증된 figure metadata를 반환한다.
