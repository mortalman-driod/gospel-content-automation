"""
Milestone 3: Auto-Scaling Typography & Word Wrapping Engine (src/design/text_layout.py)
Dynamically calculates optimal font size, wraps text into balanced lines,
and prevents visual overflow across all aspect ratios.
"""

from pathlib import Path
from typing import List, Optional, Tuple
from PIL import ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FONTS_DIR = BASE_DIR / "assets" / "fonts"

SERIF_PATH = FONTS_DIR / "PlayfairDisplay-Bold.ttf"
SANS_PATH = FONTS_DIR / "Montserrat-Bold.ttf"

SYSTEM_FONTS = {
    "sans_bold": [Path(r"C:\Windows\Fonts\segoeuib.ttf"), Path(r"C:\Windows\Fonts\arialbd.ttf")],
    "sans": [Path(r"C:\Windows\Fonts\segoeui.ttf"), Path(r"C:\Windows\Fonts\arial.ttf")],
    "serif_bold": [Path(r"C:\Windows\Fonts\georgiab.ttf"), SERIF_PATH],
    "serif": [Path(r"C:\Windows\Fonts\georgia.ttf"), SERIF_PATH]
}

def load_font(font_family: str, size: int) -> ImageFont.FreeTypeFont:
    """Loads appropriate typography with robust system fallbacks."""
    # Normalize family name
    family_key = "sans_bold" if font_family in ("sans", "sans_bold") else "serif_bold"
    if font_family in ("sans_regular", "sans_light"):
        family_key = "sans"
    elif font_family in ("serif_regular", "serif_light"):
        family_key = "serif"

    candidates = SYSTEM_FONTS.get(family_key, SYSTEM_FONTS["sans_bold"])
    for p in candidates:
        if p and p.is_file():
            try:
                return ImageFont.truetype(str(p), size)
            except Exception:
                continue

    # Fallback to default
    try:
        return ImageFont.load_default()
    except Exception:
        return None

def wrap_text_to_width(
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
    draw: ImageDraw.ImageDraw
) -> List[str]:
    """Wraps text into lines that do not exceed max_width."""
    words = text.split()
    if not words:
        return []

    lines = []
    current_line = []

    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        line_w = bbox[2] - bbox[0]

        if line_w <= max_width or not current_line:
            current_line.append(word)
        else:
            lines.append(" ".join(current_line))
            current_line = [word]

    if current_line:
        lines.append(" ".join(current_line))

    return lines

def fit_headline(
    headline_text: str,
    max_width: int,
    max_height: int,
    font_family: str = "serif",
    initial_size: int = 76,
    min_size: int = 42,
    max_lines: int = 5,
    draw: Optional[ImageDraw.ImageDraw] = None
) -> Tuple[List[str], ImageFont.FreeTypeFont, int, int]:
    """
    Auto-scales font size down until headline fits within max_width, max_height, and max_lines.
    Returns: (lines, font, total_text_width, total_text_height)
    """
    from PIL import Image
    if draw is None:
        dummy_img = Image.new("RGB", (100, 100))
        draw = ImageDraw.Draw(dummy_img)

    current_size = initial_size
    clean_text = headline_text.strip()

    while current_size >= min_size:
        font = load_font(font_family, current_size)
        lines = wrap_text_to_width(clean_text, font, max_width, draw)

        if len(lines) <= max_lines:
            # Measure total height
            line_heights = []
            max_line_w = 0
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                lw = bbox[2] - bbox[0]
                lh = bbox[3] - bbox[1]
                if lw > max_line_w:
                    max_line_w = lw
                line_heights.append(lh)

            line_spacing = int(current_size * 0.32)
            total_h = sum(line_heights) + line_spacing * max(0, len(lines) - 1)

            if total_h <= max_height:
                return lines, font, max_line_w, total_h

        current_size -= 4

    # Minimum size fallback
    font = load_font(font_family, min_size)
    lines = wrap_text_to_width(clean_text, font, max_width, draw)
    return lines[:max_lines], font, max_width, max_height
