"""
Milestone 3: Auto-Scaling Multi-Font Typography & Vector Primitives (src/design/text_layout.py)
Provides 100% bundled multi-hierarchy font resolution, mixed-font inline emphasis layout,
baseline alignment across display/serif/script faces, 2x supersampled painterly brush strips,
and organic curved underlines with zero OS font dependencies.
"""

import math
import random
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFilter, ImageFont

logger = logging.getLogger("kingdom_journal.design.text_layout")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FONTS_DIR = BASE_DIR / "assets" / "fonts"

# Legacy bundled TrueType mappings (preserved for API compatibility)
BUNDLED_FONTS = {
    ("sans", "bold"): FONTS_DIR / "Poppins-Bold.ttf",
    ("sans", "extrabold"): FONTS_DIR / "Montserrat-ExtraBold.ttf",
    ("sans", "black"): FONTS_DIR / "Montserrat-Black.ttf",
    ("sans", "regular"): FONTS_DIR / "Poppins-Regular.ttf",
    ("serif", "bold"): FONTS_DIR / "PlayfairDisplay-Bold.ttf",
    ("serif", "regular"): FONTS_DIR / "DMSerifDisplay-Regular.ttf",
}

# Full Art-Director Multi-Hierarchy Font Registry
FONT_REGISTRY: Dict[str, Path] = {
    # Expressive Brush & Calligraphy Scripts
    "display_brush": FONTS_DIR / "KaushanScript-Regular.ttf",
    "display_calligraphy": FONTS_DIR / "Allura-Regular.ttf",
    # Heavy Condensed & Display Sans
    "display_condensed": FONTS_DIR / "BarlowCondensed-Bold.ttf",
    "display_condensed_italic": FONTS_DIR / "BarlowCondensed-BoldItalic.ttf",
    "sans_condensed_ref": FONTS_DIR / "BarlowCondensed-SemiBold.ttf",
    "display_bebas": FONTS_DIR / "BebasNeue-Regular.ttf",
    "display_black": FONTS_DIR / "Montserrat-Black.ttf",
    "display_extrabold": FONTS_DIR / "Montserrat-ExtraBold.ttf",
    # Dramatic & Editorial Serifs
    "serif_bold": FONTS_DIR / "PlayfairDisplay-Bold.ttf",
    "serif_editorial": FONTS_DIR / "DMSerifDisplay-Regular.ttf",
    "serif_italic": FONTS_DIR / "DMSerifDisplay-Italic.ttf",
    # Clean Modern Geometric Sans (Full Weight Ladder)
    "sans_bold": FONTS_DIR / "Poppins-Bold.ttf",
    "sans_bold_italic": FONTS_DIR / "Poppins-BoldItalic.ttf",
    "sans_semibold": FONTS_DIR / "Poppins-SemiBold.ttf",
    "sans_semibold_italic": FONTS_DIR / "Poppins-SemiBoldItalic.ttf",
    "sans_medium": FONTS_DIR / "Poppins-Medium.ttf",
    "sans_regular": FONTS_DIR / "Poppins-Regular.ttf",
    # Montserrat Bold preserved for explicit legacy tests
    "montserrat_bold": FONTS_DIR / "Montserrat-Bold.ttf",
}

# Cross-platform system fallbacks (Linux, Windows, macOS)
SYSTEM_FALLBACKS = [
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    Path("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
    Path(r"C:\Windows\Fonts\segoeuib.ttf"),
    Path(r"C:\Windows\Fonts\arialbd.ttf"),
    Path("/System/Library/Fonts/Helvetica.ttc"),
]


def resolve_bundled_font(font_family: str, weight: str = "bold") -> Path:
    """
    Deterministically resolves font path from assets/fonts/ with zero OS dependencies.
    Preserves compatibility with existing Montserrat/Playfair tests while supporting new styles.
    """
    key_lower = font_family.lower().strip()
    if key_lower in FONT_REGISTRY and FONT_REGISTRY[key_lower].is_file():
        return FONT_REGISTRY[key_lower]

    family = "serif" if "serif" in key_lower else "sans"
    weight_clean = weight.lower()
    if "black" in weight_clean:
        w_key = "black"
    elif "extra" in weight_clean:
        w_key = "extrabold"
    elif "bold" in weight_clean or "heavy" in weight_clean:
        w_key = "bold"
    else:
        w_key = "regular"

    # Keep Montserrat resolution intact for generic sans+bold queries
    if family == "sans" and w_key == "bold":
        m_bold = FONTS_DIR / "Montserrat-Bold.ttf"
        if m_bold.is_file():
            return m_bold

    target = BUNDLED_FONTS.get((family, w_key))
    if target and target.is_file():
        return target

    bold_target = FONTS_DIR / ("PlayfairDisplay-Bold.ttf" if family == "serif" else "Montserrat-Bold.ttf")
    if bold_target.is_file():
        return bold_target

    for sys_font in SYSTEM_FALLBACKS:
        if sys_font.is_file():
            return sys_font

    return None


def load_art_font(style_key: str, size: int) -> ImageFont.FreeTypeFont:
    """Loads a specific art-directed font role by registry key from assets/fonts/."""
    font_path = FONT_REGISTRY.get(style_key)
    if font_path and font_path.is_file():
        try:
            return ImageFont.truetype(str(font_path), max(8, int(size)))
        except Exception as e:
            logger.warning(f"Failed loading art font {style_key} ({font_path}): {e}")
    return load_font("sans", max(8, int(size)), weight="bold")


def load_font(font_family: str, size: int, weight: str = "bold") -> ImageFont.FreeTypeFont:
    """
    Loads appropriate typography prioritizing bundled repository fonts first.
    Supports both role keys (e.g. 'display_brush', 'serif_italic') and legacy family+weight pairs.
    """
    if font_family in FONT_REGISTRY and FONT_REGISTRY[font_family].is_file():
        try:
            return ImageFont.truetype(str(FONT_REGISTRY[font_family]), max(8, int(size)))
        except Exception as e:
            logger.warning(f"Error loading registry font {font_family}: {e}")

    font_path = resolve_bundled_font(font_family, weight=weight)
    if font_path and font_path.is_file():
        try:
            return ImageFont.truetype(str(font_path), max(8, int(size)))
        except Exception as e:
            logger.warning(f"Error loading bundled font {font_path}: {e}")

    for sys_font in SYSTEM_FALLBACKS:
        if sys_font.is_file():
            try:
                return ImageFont.truetype(str(sys_font), max(8, int(size)))
            except Exception:
                continue

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
    if draw is None:
        dummy_img = Image.new("RGB", (100, 100))
        draw = ImageDraw.Draw(dummy_img)

    current_size = initial_size
    clean_text = headline_text.strip()

    while current_size >= min_size:
        font = load_font(font_family, current_size)
        lines = wrap_text_to_width(clean_text, font, max_width, draw)

        if len(lines) <= max_lines:
            line_heights = []
            max_line_w = 0
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                lw = bbox[2] - bbox[0]
                lh = bbox[3] - bbox[1]
                if lw > max_line_w:
                    max_line_w = lw
                line_heights.append(lh)

            line_spacing = int(current_size * 0.30)
            total_h = sum(line_heights) + line_spacing * max(0, len(lines) - 1)

            if total_h <= max_height:
                return lines, font, max_line_w, total_h

        current_size -= 4

    font = load_font(font_family, min_size)
    lines = wrap_text_to_width(clean_text, font, max_width, draw)
    return lines[:max_lines], font, max_width, max_height


def draw_brush_underline(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    width: int,
    color=(250, 204, 21, 255),
    thickness: int = 8
):
    """
    Draws an organic curved brush underline stroke with dynamic tapering.
    """
    steps = 36
    pts = []
    for i in range(steps + 1):
        t = i / steps
        px = x + (width * t)
        # Gentle expressive upward arc with slight brush flare
        curve = -math.sin(t * math.pi) * 6.5 + (t * 1.5)
        py = y + curve
        pts.append((px, py))

    for i in range(len(pts) - 1):
        t = i / steps
        taper = 0.55 + 0.45 * math.sin(t * math.pi)
        current_w = max(3, int(thickness * taper))
        draw.line([pts[i], pts[i + 1]], fill=color, width=current_w)


def draw_supersampled_brush_arc(
    base_img: Image.Image,
    x: int,
    y: int,
    width: int,
    color: Tuple[int, int, int, int] = (250, 204, 21, 255),
    thickness: int = 10,
    arch_height: float = 8.0
) -> Image.Image:
    """
    Renders a silky anti-aliased tapered curved brush stroke on a 2x supersampled RGBA overlay
    and composites cleanly onto base_img.
    """
    w_canvas, h_canvas = base_img.size
    scale = 2
    overlay = Image.new("RGBA", (w_canvas * scale, h_canvas * scale), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)

    sx = x * scale
    sy = y * scale
    sw = max(20, width * scale)
    steps = 48
    pts = []
    for i in range(steps + 1):
        t = i / steps
        px = sx + (sw * t)
        # Slightly arched upward curve like hand-drawn calligraphy swoosh
        py = sy - math.sin(t * math.pi) * (arch_height * scale) + (t * 2.0 * scale)
        pts.append((px, py))

    for i in range(len(pts) - 1):
        t = i / steps
        taper = 0.45 + 0.55 * math.sin(t * math.pi)
        cw = max(4, int(thickness * scale * taper))
        odraw.line([pts[i], pts[i + 1]], fill=color, width=cw)
        r = cw // 2
        cx, cy = pts[i]
        odraw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)

    downsampled = overlay.resize((w_canvas, h_canvas), Image.Resampling.LANCZOS)
    return Image.alpha_composite(base_img.convert("RGBA"), downsampled)


def draw_painterly_strip(
    base_img: Image.Image,
    box: Tuple[int, int, int, int],
    fill_color: Tuple[int, int, int, int],
    seed: int = 42
) -> Image.Image:
    """
    Draws an organic, hand-painted brush highlight strip behind emphasized text or scripture badges
    using 2x supersampling for crisp edges with natural dry-brush end bristles.
    """
    x1, y1, x2, y2 = [int(v) for v in box]
    w_canvas, h_canvas = base_img.size
    scale = 2
    overlay = Image.new("RGBA", (w_canvas * scale, h_canvas * scale), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)

    rng = random.Random(seed)
    sx1, sy1, sx2, sy2 = x1 * scale, y1 * scale, x2 * scale, y2 * scale
    strip_h = max(12, sy2 - sy1)

    # Organic tilted brush polygon body with slightly imperfect edges
    pts = []
    # Top edge left to right
    steps = 12
    for i in range(steps + 1):
        t = i / steps
        px = sx1 + (sx2 - sx1) * t
        py = sy1 + rng.uniform(-2.5, 2.5) * scale - (t * 1.5 * scale)
        pts.append((px, py))

    # Right ragged bristle end
    for i in range(5):
        frac = (i + 0.5) / 5.0
        px = sx2 + rng.uniform(-6, 10) * scale
        py = sy1 + strip_h * frac
        pts.append((px, py))

    # Bottom edge right to left
    for i in range(steps, -1, -1):
        t = i / steps
        px = sx1 + (sx2 - sx1) * t
        py = sy2 + rng.uniform(-2.5, 2.5) * scale - (t * 1.5 * scale)
        pts.append((px, py))

    # Left ragged bristle end
    for i in range(4, -1, -1):
        frac = (i + 0.5) / 5.0
        px = sx1 + rng.uniform(-10, 6) * scale
        py = sy1 + strip_h * frac
        pts.append((px, py))

    odraw.polygon(pts, fill=fill_color)

    # Subtle extra paint bristle streaks at ends for texture
    for _ in range(4):
        by_top = rng.uniform(sy1 + 2, sy2 - 6)
        odraw.line(
            [(sx1 - rng.uniform(4, 14) * scale, by_top), (sx1 + 18 * scale, by_top)],
            fill=fill_color,
            width=max(2, int(2 * scale))
        )
        odraw.line(
            [(sx2 - 18 * scale, by_top), (sx2 + rng.uniform(4, 14) * scale, by_top)],
            fill=fill_color,
            width=max(2, int(2 * scale))
        )

    downsampled = overlay.resize((w_canvas, h_canvas), Image.Resampling.LANCZOS)
    return Image.alpha_composite(base_img.convert("RGBA"), downsampled)


def draw_optical_text(
    img: Image.Image,
    pos: Tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill_color: Tuple[int, int, int, int],
    soft_backing: bool = False,
    backing_is_dark: bool = True
) -> Image.Image:
    """
    Renders razor-sharp typography without harsh 2px pixel drop shadows.
    Optional soft optical ambient feather only when over textured mid-tone areas.
    """
    if soft_backing:
        glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glow)
        glow_col = (0, 0, 0, 75) if backing_is_dark else (255, 255, 255, 95)
        gdraw.text(pos, text, font=font, fill=glow_col)
        glow = glow.filter(ImageFilter.GaussianBlur(radius=7))
        img = Image.alpha_composite(img.convert("RGBA"), glow)

    draw = ImageDraw.Draw(img)
    draw.text(pos, text, font=font, fill=fill_color)
    return img


def draw_pill_badge(
    base_img: Image.Image,
    cx_or_x: int,
    y: int,
    text: str,
    font: ImageFont.FreeTypeFont,
    bg_color: Tuple[int, int, int, int],
    text_color: Tuple[int, int, int, int],
    align: str = "center",
    style: str = "pill",
    pad_x: int = 28,
    pad_y: int = 12
) -> Tuple[Image.Image, int]:
    """
    Renders a crisp, optically centered Scripture badge or painterly brush ribbon.
    style: 'pill' (clean rounded capsule), 'brush' (painted ribbon), or 'underline' (minimalist editorial rule).
    Returns: (updated_img, badge_bottom_y)
    """
    draw = ImageDraw.Draw(base_img)
    tb = draw.textbbox((0, 0), text, font=font)
    tw = tb[2] - tb[0]
    th = tb[3] - tb[1]

    bw = tw + (pad_x * 2)
    bh = th + (pad_y * 2)

    if align == "center":
        bx = cx_or_x - (bw // 2)
    elif align == "right":
        bx = cx_or_x - bw
    else:
        bx = cx_or_x

    if style == "brush":
        base_img = draw_painterly_strip(
            base_img,
            (bx - 6, y, bx + bw + 6, y + bh),
            bg_color,
            seed=sum(ord(c) for c in text)
        )
    elif style == "underline":
        draw = ImageDraw.Draw(base_img)
        draw.line([(bx, y + bh), (bx + bw, y + bh)], fill=bg_color, width=3)
    else:
        draw = ImageDraw.Draw(base_img)
        draw.rounded_rectangle([bx, y, bx + bw, y + bh], radius=min(12, bh // 3), fill=bg_color)

    # Exact optical centering compensating for font bbox offset (tb[0], tb[1])
    tx = bx + ((bw - tw) // 2) - tb[0]
    ty = y + ((bh - th) // 2) - tb[1]

    draw = ImageDraw.Draw(base_img)
    draw.text((tx, ty), text, font=font, fill=text_color)
    return base_img, y + bh


def tokenize_with_emphasis(
    headline: str,
    emphasized_phrases: List[str]
) -> List[Tuple[str, bool]]:
    """
    Splits headline into word tokens cleanly flagging words belonging to emphasized_phrases (1-4 key words).
    Ensures exact verbatim spelling preservation without duplicating or mangling punctuation.
    """
    words = headline.strip().split()
    if not words:
        return []

    clean_phrases = [p.strip().lower() for p in (emphasized_phrases or []) if p and p.strip()]
    if not clean_phrases:
        return [(w, False) for w in words]

    flags = [False] * len(words)
    stripped_words = [re.sub(r'^[^\w]+|[^\w]+$', '', w.lower()) for w in words]

    for phrase in clean_phrases:
        p_tokens = [re.sub(r'^[^\w]+|[^\w]+$', '', pt.lower()) for pt in phrase.split() if pt.strip()]
        if not p_tokens:
            continue
        plen = len(p_tokens)
        for i in range(len(stripped_words) - plen + 1):
            if stripped_words[i:i + plen] == p_tokens:
                for k in range(i, i + plen):
                    flags[k] = True

    return list(zip(words, flags))


def wrap_mixed_tokens(
    tokens: List[Tuple[str, bool]],
    font_base: ImageFont.FreeTypeFont,
    font_accent: ImageFont.FreeTypeFont,
    max_width: int,
    draw: ImageDraw.ImageDraw
) -> List[List[Tuple[str, bool]]]:
    """
    Wraps [(word, is_accent), ...] into lines where each word is measured in its own typeface.
    """
    if not tokens:
        return []

    space_w_base = draw.textbbox((0, 0), " ", font=font_base)[2]
    lines: List[List[Tuple[str, bool]]] = []
    cur_line: List[Tuple[str, bool]] = []
    cur_w = 0

    for word, is_acc in tokens:
        f = font_accent if is_acc else font_base
        wb = draw.textbbox((0, 0), word, font=f)
        ww = wb[2] - wb[0]
        gap = max(space_w_base, int(f.size * 0.24)) if cur_line else 0

        if cur_w + gap + ww <= max_width or not cur_line:
            cur_line.append((word, is_acc))
            cur_w += gap + ww
        else:
            lines.append(cur_line)
            cur_line = [(word, is_acc)]
            cur_w = ww

    if cur_line:
        lines.append(cur_line)

    return lines


def fit_mixed_headline(
    headline: str,
    emphasized_phrases: List[str],
    max_width: int,
    max_height: int,
    base_font_key: str,
    accent_font_key: str,
    initial_size: int = 72,
    min_size: int = 38,
    accent_scale: float = 1.12,
    max_lines: int = 5,
    line_leading: float = 1.24,
    draw: Optional[ImageDraw.ImageDraw] = None
) -> Tuple[List[List[Tuple[str, bool]]], ImageFont.FreeTypeFont, ImageFont.FreeTypeFont, int]:
    """
    Auto-scales mixed-font headline until wrapped lines fit comfortably inside max_width and max_height.
    Returns: (wrapped_token_lines, font_base, font_accent, total_block_height)
    """
    if draw is None:
        dummy = Image.new("RGB", (100, 100))
        draw = ImageDraw.Draw(dummy)

    tokens = tokenize_with_emphasis(headline, emphasized_phrases)
    cur_size = initial_size

    while cur_size >= min_size:
        f_base = load_art_font(base_font_key, cur_size)
        f_acc = load_art_font(accent_font_key, int(cur_size * accent_scale))
        lines = wrap_mixed_tokens(tokens, f_base, f_acc, max_width, draw)

        if len(lines) <= max_lines:
            step_h = int(max(cur_size, int(cur_size * accent_scale)) * line_leading)
            total_h = len(lines) * step_h
            if total_h <= max_height:
                return lines, f_base, f_acc, total_h

        cur_size -= 4

    f_base = load_art_font(base_font_key, min_size)
    f_acc = load_art_font(accent_font_key, int(min_size * accent_scale))
    lines = wrap_mixed_tokens(tokens, f_base, f_acc, max_width, draw)
    step_h = int(max(min_size, int(min_size * accent_scale)) * line_leading)
    return lines[:max_lines], f_base, f_acc, min(max_height, len(lines[:max_lines]) * step_h)


def draw_mixed_headline(
    base_img: Image.Image,
    lines: List[List[Tuple[str, bool]]],
    anchor_x: int,
    start_y: int,
    max_width: int,
    align: str,
    font_base: ImageFont.FreeTypeFont,
    font_accent: ImageFont.FreeTypeFont,
    color_base: Tuple[int, int, int, int],
    color_accent: Tuple[int, int, int, int],
    line_leading: float = 1.24,
    treatment: str = "inline_color",
    strip_bg_color: Optional[Tuple[int, int, int, int]] = None,
    strip_text_color: Optional[Tuple[int, int, int, int]] = None,
    soft_backing: bool = False,
    backing_is_dark: bool = True
) -> Tuple[Image.Image, int, Optional[Tuple[int, int, int]]]:
    """
    Renders wrapped mixed-font headline lines with precise baseline alignment across fonts
    and optional painterly highlight strips or brush underlines.
    Returns: (updated_img, final_y, last_accent_span=(x, y_bottom, width))
    """
    draw = ImageDraw.Draw(base_img)
    base_ascent, _ = font_base.getmetrics()
    acc_ascent, _ = font_accent.getmetrics()
    max_ascent = max(base_ascent, acc_ascent)
    step_h = int(max(font_base.size, font_accent.size) * line_leading)

    last_accent_span = None
    cur_y = start_y

    for line_tokens in lines:
        # Measure segments width to compute alignment offset
        token_widths = []
        gaps = []
        for idx, (word, is_acc) in enumerate(line_tokens):
            f = font_accent if is_acc else font_base
            wb = draw.textbbox((0, 0), word, font=f)
            ww = wb[2] - wb[0]
            token_widths.append((ww, wb[0]))
            if idx < len(line_tokens) - 1:
                next_acc = line_tokens[idx + 1][1]
                base_gap = max(8, int(f.size * 0.25))
                if treatment == "paint_strip_highlight" and (is_acc != next_acc):
                    base_gap += 10
                gaps.append(base_gap)

        total_line_w = sum(tw for tw, _ in token_widths) + sum(gaps)
        if align == "center":
            lx = anchor_x + (max_width - total_line_w) // 2
        elif align == "right":
            lx = anchor_x + (max_width - total_line_w)
        else:
            lx = anchor_x

        # Group contiguous accented words if using strip highlight
        if treatment == "paint_strip_highlight" and strip_bg_color:
            # Find contiguous accent spans in this line
            cx_scan = lx
            i = 0
            while i < len(line_tokens):
                _, is_acc = line_tokens[i]
                ww, _ = token_widths[i]
                gap_after = gaps[i] if i < len(gaps) else 0
                if is_acc:
                    span_start_x = cx_scan
                    span_w = ww
                    j = i + 1
                    while j < len(line_tokens) and line_tokens[j][1]:
                        span_w += gaps[j - 1] + token_widths[j][0]
                        j += 1
                    pad_strip_x = 10
                    pad_strip_top = int(max_ascent * 0.06)
                    strip_box = (
                        span_start_x - pad_strip_x,
                        cur_y + (max_ascent - acc_ascent) - pad_strip_top,
                        span_start_x + span_w + pad_strip_x,
                        cur_y + max_ascent + int(font_accent.size * 0.25)
                    )
                    base_img = draw_painterly_strip(base_img, strip_box, strip_bg_color, seed=cur_y + i)
                    # Advance scan
                    for k in range(i, j):
                        cx_scan += token_widths[k][0] + (gaps[k] if k < len(gaps) else 0)
                    i = j
                else:
                    cx_scan += ww + gap_after
                    i += 1

        # Render each word token aligned on the shared typographic baseline
        cx = lx
        for idx, (word, is_acc) in enumerate(line_tokens):
            f = font_accent if is_acc else font_base
            ascent = acc_ascent if is_acc else base_ascent
            ww, x_bearing = token_widths[idx]
            ty = cur_y + (max_ascent - ascent)

            if is_acc:
                col = strip_text_color if (treatment == "paint_strip_highlight" and strip_text_color) else color_accent
                use_soft = soft_backing and (treatment != "paint_strip_highlight")
                base_img = draw_optical_text(
                    base_img, (cx - x_bearing, ty), word, f, col,
                    soft_backing=use_soft, backing_is_dark=backing_is_dark
                )
                last_accent_span = (cx, cur_y + max_ascent + int(f.size * 0.16), ww)
            else:
                base_img = draw_optical_text(
                    base_img, (cx - x_bearing, ty), word, f, color_base,
                    soft_backing=soft_backing, backing_is_dark=backing_is_dark
                )

            cx += ww + (gaps[idx] if idx < len(gaps) else 0)

        cur_y += step_h

    return base_img, cur_y, last_accent_span
