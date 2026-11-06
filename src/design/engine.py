"""
Milestone 3: Master Flyer Compositor & Typography Rendering Engine (src/design/engine.py)
Composites high-end editorial gospel flyers with code-rendered typography over text-free backgrounds.
Supports 3 standard formats: 4:5 (1080x1350), 1:1 (1080x1080), 9:16 (1080x1920)
and 6 rotating institutional templates with WCAG AA contrast verification.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import yaml
from PIL import Image, ImageDraw

from .contrast import (
    apply_adaptive_scrim,
    calculate_contrast_ratio,
    sample_region_average_color
)
from .text_layout import fit_headline, load_font, wrap_text_to_width
from .backgrounds import (
    generate_procedural_background,
    generate_text_free_image_prompt
)

logger = logging.getLogger("kingdom_journal.design")
BASE_DIR = Path(__file__).resolve().parent.parent.parent

SIZES = {
    "4:5": (1080, 1350),   # Mobile Feed Primary
    "1:1": (1080, 1080),   # Feed Square
    "9:16": (1080, 1920)   # WhatsApp Status & IG Story
}

def hex_to_rgb(h: str) -> Tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

class FlyerEngine:
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or (BASE_DIR / "config" / "brand.yml")
        self.brand_config = self._load_brand_config()
        self.palettes = self.brand_config.get("palettes", [])
        self.templates = self.brand_config.get("templates", [
            "bold_statement", "contrast_split", "scripture_card",
            "question_hook", "quiet_light", "numbered_list"
        ])

    def _load_brand_config(self) -> Dict:
        if self.config_path.is_file():
            try:
                return yaml.safe_load(self.config_path.read_text(encoding="utf-8")) or {}
            except Exception as e:
                logger.warning(f"Error loading brand config: {e}")
        return {}

    def get_palette(self, palette_id: Optional[str] = None) -> Dict:
        if palette_id:
            for p in self.palettes:
                if p.get("id") == palette_id:
                    return p
        return self.palettes[0] if self.palettes else {
            "id": "navy_gold",
            "bg_primary": "#0A1128",
            "accent": "#D4AF37",
            "text_primary": "#F8F9FA",
            "text_secondary": "#CBD5E1",
            "scrim_tint": [10, 17, 40]
        }

    def render_flyer(
        self,
        template_name: str,
        size_key: str,
        content: Dict,
        palette_id: Optional[str] = None,
        background_image: Optional[Image.Image] = None
    ) -> Tuple[Image.Image, Dict]:
        """
        Renders a flyer for a given template and aspect ratio.
        content dict:
            headline: str
            subline: Optional[str]
            credit: Optional[str]
            scripture_badge: Optional[str]
            points: Optional[List[str]] (for numbered_list)
        Returns: (rendered_image, metadata)
        """
        width, height = SIZES.get(size_key, (1080, 1350))
        palette = self.get_palette(palette_id)

        # 1. Base Background
        if background_image is not None:
            # Resize and crop to fill
            bg = background_image.copy().convert("RGB")
            bg = self._crop_to_aspect(bg, width, height)
        else:
            bg = generate_procedural_background(width, height, palette)

        # Safe Margins
        if size_key == "9:16":
            # 9:16 safe zone (avoid Instagram UI overlay)
            safe_top = 260
            safe_bottom = height - 360
        else:
            safe_top = int(height * 0.08)
            safe_bottom = int(height * 0.92)

        safe_left = int(width * 0.08)
        safe_right = int(width * 0.92)
        content_width = safe_right - safe_left
        content_height = safe_bottom - safe_top

        # Prepare colors
        c_primary = hex_to_rgb(palette.get("text_primary", "#F8F9FA"))
        c_secondary = hex_to_rgb(palette.get("text_secondary", "#CBD5E1"))
        c_accent = hex_to_rgb(palette.get("accent", "#D4AF37"))
        tint_rgb = tuple(palette.get("scrim_tint", [10, 17, 40]))

        # Render specific template layout
        renderer_map = {
            "bold_statement": self._render_bold_statement,
            "contrast_split": self._render_contrast_split,
            "scripture_card": self._render_scripture_card,
            "question_hook": self._render_question_hook,
            "quiet_light": self._render_quiet_light,
            "numbered_list": self._render_numbered_list
        }
        renderer = renderer_map.get(template_name, self._render_bold_statement)

        rendered, text_box = renderer(
            bg=bg,
            width=width,
            height=height,
            safe_box=(safe_left, safe_top, safe_right, safe_bottom),
            content=content,
            colors={"primary": c_primary, "secondary": c_secondary, "accent": c_accent, "tint": tint_rgb}
        )

        # Measure final contrast
        avg_bg = sample_region_average_color(rendered, text_box)
        contrast = calculate_contrast_ratio(c_primary, avg_bg)

        # 3-Second Legibility Check (Thumbnail rendering)
        thumb = rendered.copy()
        thumb.thumbnail((300, int(300 * (height / width))))

        metadata = {
            "template": template_name,
            "size": size_key,
            "dimensions": f"{width}x{height}",
            "palette": palette.get("id"),
            "contrast_ratio": round(contrast, 2),
            "wcag_aa_compliant": contrast >= 4.5,
            "legibility_pass": contrast >= 4.5 and len(content.get("headline", "").split()) <= 20
        }

        return rendered, metadata

    def _crop_to_aspect(self, img: Image.Image, target_w: int, target_h: int) -> Image.Image:
        """Center-crops and resizes an image to exactly fill target dimensions."""
        img_w, img_h = img.size
        target_ratio = target_w / target_h
        img_ratio = img_w / img_h

        if img_ratio > target_ratio:
            new_w = int(img_h * target_ratio)
            left = (img_w - new_w) // 2
            img = img.crop((left, 0, left + new_w, img_h))
        else:
            new_h = int(img_w / target_ratio)
            top = (img_h - new_h) // 2
            img = img.crop((0, top, img_w, top + new_h))

        return img.resize((target_w, target_h), Image.Resampling.LANCZOS)

    def _draw_brand_masthead(self, draw: ImageDraw.ImageDraw, left: int, top: int, right: int, colors: Dict):
        """Renders the institutional Journal masthead header."""
        font_brand = load_font("sans", 24)
        brand_text = "THE KINGDOM JOURNAL"
        bbox = draw.textbbox((0, 0), brand_text, font=font_brand)
        bw = bbox[2] - bbox[0]
        # Centered masthead
        cx = (left + right) // 2
        draw.text((cx - bw // 2, top), brand_text, font=font_brand, fill=colors["accent"])

        # Thin rule under masthead
        rule_y = top + 36
        draw.line([(cx - 70, rule_y), (cx + 70, rule_y)], fill=colors["accent"], width=2)

    def _draw_watermark(self, draw: ImageDraw.ImageDraw, left: int, bottom: int, right: int, colors: Dict):
        """Renders subtle footer watermark."""
        font_wm = load_font("sans", 20)
        wm_text = "THE KINGDOM JOURNAL  •  DAILY EDITORIAL"
        bbox = draw.textbbox((0, 0), wm_text, font=font_wm)
        bw = bbox[2] - bbox[0]
        cx = (left + right) // 2
        draw.text((cx - bw // 2, bottom - 25), wm_text, font=font_wm, fill=colors["secondary"])

    # 1. BOLD STATEMENT TEMPLATE
    def _render_bold_statement(self, bg, width, height, safe_box, content, colors):
        s_left, s_top, s_right, s_bottom = safe_box
        draw = ImageDraw.Draw(bg)
        self._draw_brand_masthead(draw, s_left, s_top, s_right, colors)

        headline = content.get("headline", "")
        credit = content.get("credit", "The Kingdom Journal")

        # Fit headline
        max_w = s_right - s_left
        max_h = int(height * 0.45)
        lines, font, _, text_h = fit_headline(headline, max_w, max_h, font_family="serif", initial_size=74, min_size=48)

        text_y = s_top + int((s_bottom - s_top - text_h) * 0.44)
        text_bbox = (s_left, text_y, s_right, text_y + text_h)

        # Apply adaptive scrim
        bg = apply_adaptive_scrim(bg, text_bbox, colors["primary"], colors["tint"], min_contrast=4.5)
        draw = ImageDraw.Draw(bg)

        # Accent vertical bar on the left
        draw.line([(s_left, text_y), (s_left, text_y + text_h)], fill=colors["accent"], width=5)

        # Draw lines
        cur_y = text_y
        line_spacing = int(font.size * 0.30)
        for line in lines:
            draw.text((s_left + 24, cur_y), line, font=font, fill=colors["primary"])
            bbox = draw.textbbox((0, 0), line, font=font)
            cur_y += (bbox[3] - bbox[1]) + line_spacing

        # Credit line
        font_credit = load_font("sans", 28)
        draw.text((s_left + 24, cur_y + 20), f"— {credit}", font=font_credit, fill=colors["accent"])

        self._draw_watermark(draw, s_left, s_bottom, s_right, colors)
        return bg, text_bbox

    # 2. CONTRAST SPLIT TEMPLATE
    def _render_contrast_split(self, bg, width, height, safe_box, content, colors):
        s_left, s_top, s_right, s_bottom = safe_box
        draw = ImageDraw.Draw(bg)
        self._draw_brand_masthead(draw, s_left, s_top, s_right, colors)

        headline = content.get("headline", "")
        # Split by punctuation or comma or slash if present
        parts = [p.strip() for p in headline.replace("/", ".").split(".") if p.strip()]
        line1 = parts[0] if parts else headline
        line2 = parts[1] if len(parts) > 1 else content.get("subline", "God looks on the secret place.")
        credit = content.get("credit", "The Kingdom Journal")

        max_w = s_right - s_left
        font1 = load_font("sans", 46)
        lines1 = wrap_text_to_width(line1, font1, max_w, draw)

        lines2, font2, _, h2 = fit_headline(line2, max_w, int(height * 0.35), font_family="serif", initial_size=68, min_size=46)

        total_h = len(lines1) * 55 + 50 + h2
        start_y = s_top + int((s_bottom - s_top - total_h) * 0.42)
        text_bbox = (s_left, start_y, s_right, start_y + total_h)

        bg = apply_adaptive_scrim(bg, text_bbox, colors["primary"], colors["tint"], min_contrast=4.5)
        draw = ImageDraw.Draw(bg)

        # Draw Line 1 (Muted / Contrast header)
        y = start_y
        for l in lines1:
            draw.text((s_left, y), l, font=font1, fill=colors["secondary"])
            y += 55

        # Thin accent separator
        y += 10
        draw.line([(s_left, y), (s_left + 120, y)], fill=colors["accent"], width=3)
        y += 25

        # Draw Line 2 (Radiant Gold Punchline)
        for l in lines2:
            draw.text((s_left, y), l, font=font2, fill=colors["accent"])
            bbox = draw.textbbox((0, 0), l, font=font2)
            y += (bbox[3] - bbox[1]) + int(font2.size * 0.28)

        # Credit line
        font_credit = load_font("sans", 26)
        draw.text((s_left, y + 25), f"— {credit}", font=font_credit, fill=colors["primary"])

        self._draw_watermark(draw, s_left, s_bottom, s_right, colors)
        return bg, text_bbox

    # 3. SCRIPTURE CARD TEMPLATE
    def _render_scripture_card(self, bg, width, height, safe_box, content, colors):
        s_left, s_top, s_right, s_bottom = safe_box
        draw = ImageDraw.Draw(bg)
        self._draw_brand_masthead(draw, s_left, s_top, s_right, colors)

        scripture_text = content.get("headline", "")
        badge = content.get("scripture_badge") or content.get("credit", "HOLY SCRIPTURE")

        max_w = int((s_right - s_left) * 0.90)
        lines, font, _, text_h = fit_headline(f'"{scripture_text}"', max_w, int(height * 0.45), font_family="serif", initial_size=64, min_size=42)

        start_y = s_top + int((s_bottom - s_top - text_h) * 0.42)
        text_bbox = (s_left, start_y, s_right, start_y + text_h + 90)

        bg = apply_adaptive_scrim(bg, text_bbox, colors["primary"], colors["tint"], min_contrast=4.5)
        draw = ImageDraw.Draw(bg)

        # Ornamental Cross / Diamond top icon
        cx = width // 2
        draw.text((cx - 10, start_y - 45), "✦", font=load_font("serif", 32), fill=colors["accent"])

        cur_y = start_y
        for l in lines:
            bbox = draw.textbbox((0, 0), l, font=font)
            lw = bbox[2] - bbox[0]
            draw.text((cx - lw // 2, cur_y), l, font=font, fill=colors["primary"])
            cur_y += (bbox[3] - bbox[1]) + int(font.size * 0.32)

        # Pill badge for Reference
        font_badge = load_font("sans", 24)
        b_bbox = draw.textbbox((0, 0), badge, font=font_badge)
        bw = b_bbox[2] - b_bbox[0]
        bh = b_bbox[3] - b_bbox[1]

        badge_x = cx - (bw + 40) // 2
        badge_y = cur_y + 25
        draw.rounded_rectangle([badge_x, badge_y, badge_x + bw + 40, badge_y + bh + 16], radius=6, outline=colors["accent"], width=2)
        draw.text((badge_x + 20, badge_y + 8), badge, font=font_badge, fill=colors["accent"])

        self._draw_watermark(draw, s_left, s_bottom, s_right, colors)
        return bg, text_bbox

    # 4. QUESTION HOOK TEMPLATE
    def _render_question_hook(self, bg, width, height, safe_box, content, colors):
        s_left, s_top, s_right, s_bottom = safe_box
        draw = ImageDraw.Draw(bg)
        self._draw_brand_masthead(draw, s_left, s_top, s_right, colors)

        question = content.get("headline", "")
        if not question.endswith("?"):
            question += "?"
        subline = content.get("subline", "When human striving stops, divine intervention takes over.")
        credit = content.get("credit", "The Kingdom Journal")

        max_w = s_right - s_left
        lines_q, font_q, _, h_q = fit_headline(question, max_w, int(height * 0.35), font_family="serif", initial_size=68, min_size=46)

        font_sub = load_font("sans", 34)
        lines_sub = wrap_text_to_width(subline, font_sub, max_w, draw)

        total_h = h_q + 50 + len(lines_sub) * 45
        start_y = s_top + int((s_bottom - s_top - total_h) * 0.44)
        text_bbox = (s_left, start_y, s_right, start_y + total_h)

        bg = apply_adaptive_scrim(bg, text_bbox, colors["primary"], colors["tint"], min_contrast=4.5)
        draw = ImageDraw.Draw(bg)

        # Question in Gold
        y = start_y
        for l in lines_q:
            draw.text((s_left, y), l, font=font_q, fill=colors["accent"])
            bbox = draw.textbbox((0, 0), l, font=font_q)
            y += (bbox[3] - bbox[1]) + int(font_q.size * 0.28)

        y += 20
        # Answer/Reflection in Warm White
        for l in lines_sub:
            draw.text((s_left, y), l, font=font_sub, fill=colors["primary"])
            y += 45

        # Credit
        font_c = load_font("sans", 24)
        draw.text((s_left, y + 20), f"— {credit}", font=font_c, fill=colors["secondary"])

        self._draw_watermark(draw, s_left, s_bottom, s_right, colors)
        return bg, text_bbox

    # 5. QUIET LIGHT TEMPLATE
    def _render_quiet_light(self, bg, width, height, safe_box, content, colors):
        s_left, s_top, s_right, s_bottom = safe_box
        draw = ImageDraw.Draw(bg)
        self._draw_brand_masthead(draw, s_left, s_top, s_right, colors)

        headline = content.get("headline", "")
        credit = content.get("credit", "The Kingdom Journal")

        max_w = int((s_right - s_left) * 0.88)
        lines, font, _, text_h = fit_headline(headline, max_w, int(height * 0.40), font_family="serif", initial_size=62, min_size=42)

        cx = width // 2
        start_y = s_top + int((s_bottom - s_top - text_h) * 0.46)
        text_bbox = (s_left, start_y - 60, s_right, start_y + text_h + 60)

        bg = apply_adaptive_scrim(bg, text_bbox, colors["primary"], colors["tint"], min_contrast=4.5)
        draw = ImageDraw.Draw(bg)

        # Soft quotation mark glyph
        font_quote_glyph = load_font("serif", 72)
        draw.text((cx - 20, start_y - 75), "“", font=font_quote_glyph, fill=colors["accent"])

        cur_y = start_y
        for l in lines:
            bbox = draw.textbbox((0, 0), l, font=font)
            lw = bbox[2] - bbox[0]
            draw.text((cx - lw // 2, cur_y), l, font=font, fill=colors["primary"])
            cur_y += (bbox[3] - bbox[1]) + int(font.size * 0.34)

        font_credit = load_font("sans", 24)
        c_bbox = draw.textbbox((0, 0), f"— {credit} —", font=font_credit)
        cw = c_bbox[2] - c_bbox[0]
        draw.text((cx - cw // 2, cur_y + 30), f"— {credit} —", font=font_credit, fill=colors["accent"])

        self._draw_watermark(draw, s_left, s_bottom, s_right, colors)
        return bg, text_bbox

    # 6. NUMBERED LIST TEMPLATE
    def _render_numbered_list(self, bg, width, height, safe_box, content, colors):
        s_left, s_top, s_right, s_bottom = safe_box
        draw = ImageDraw.Draw(bg)
        self._draw_brand_masthead(draw, s_left, s_top, s_right, colors)

        title = content.get("headline", "3 SPIRITUAL LAWS OF WORSHIP")
        points = content.get("points") or [
            "Surrender precedes authority",
            "Midnight praise dismantles spiritual friction",
            "Silence in the secret place opens public heavens"
        ]

        font_title = load_font("serif", 46)
        max_w = s_right - s_left
        lines_title = wrap_text_to_width(title.upper(), font_title, max_w, draw)

        total_h = len(lines_title) * 54 + len(points) * 90 + 40
        start_y = s_top + int((s_bottom - s_top - total_h) * 0.42)
        text_bbox = (s_left, start_y, s_right, start_y + total_h)

        bg = apply_adaptive_scrim(bg, text_bbox, colors["primary"], colors["tint"], min_contrast=4.5)
        draw = ImageDraw.Draw(bg)

        # Title
        y = start_y
        for l in lines_title:
            draw.text((s_left, y), l, font=font_title, fill=colors["accent"])
            y += 54

        y += 15
        draw.line([(s_left, y), (s_left + 80, y)], fill=colors["accent"], width=3)
        y += 35

        # Render numbered points
        font_num = load_font("sans", 32)
        font_p = load_font("sans", 32)

        for idx, pt in enumerate(points[:3], 1):
            num_str = f"0{idx}"
            draw.text((s_left, y), num_str, font=font_num, fill=colors["accent"])
            draw.text((s_left + 65, y), pt, font=font_p, fill=colors["primary"])
            y += 85

        self._draw_watermark(draw, s_left, s_bottom, s_right, colors)
        return bg, text_bbox
