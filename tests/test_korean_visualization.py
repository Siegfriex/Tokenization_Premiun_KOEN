"""실제 설치 한글 font와 PNG/SVG 저장 계약을 검사한다."""

from tokenization_premium.paths import PROJECT_ROOT  # test figure를 project root 내부에 제한한다.
from tokenization_premium.visualization import find_korean_font, render_korean_smoke  # 한글 figure 검증 API를 검사한다.


def test_korean_png_svg_rendering() -> None:
    """
    /**
     * @purpose 실제 한글 glyph를 사용한 PNG와 SVG가 저장·재개방되는지 검사한다.
     * @spec_ref Notebook Constitution §7
     * @return None
     * @raises RuntimeError 한글 font가 없는 경우
     * @raises AssertionError missing glyph 또는 저장 artifact 검증이 실패한 경우
     * @validation PNG shape, SVG 한글 text, SHA-256 길이를 검사한다.
     * @artifact .runtime/test_outputs/F00_KOREAN_FONT_SMOKE_TEST.*
     */
    """
    output_dir = PROJECT_ROOT / ".runtime" / "test_outputs"  # 외부 temporary directory를 사용하지 않는 ignored 경로를 선택한다.
    font_info = find_korean_font()  # 실제 cmap으로 검증된 한글 font를 선택한다.
    result = render_korean_smoke(font_info, output_dir / "F00_KOREAN_FONT_SMOKE_TEST.png", output_dir / "F00_KOREAN_FONT_SMOKE_TEST.svg")  # 두 format을 저장하고 재검증한다.
    assert result["image_shape_hwc"][0] > 0 and result["image_shape_hwc"][1] > 0  # 저장된 PNG height와 width가 양수인지 확인한다.
    assert len(result["png_sha256"]) == 64 and len(result["svg_sha256"]) == 64  # 두 artifact의 SHA-256 형식을 확인한다.
