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
from PIL import Image, ImageDraw, ImageFilter

from .contrast import (
    apply_adaptive_scrim,
    calculate_contrast_ratio,
    sample_region_average_color
)
from .text_layout import fit_headline, load_font, wrap_text_to_width
from .backgrounds import (
    generate_procedural_background,
    load_atmospheric_background,
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
            subject_hint = content.get("subject_hint") or content.get("headline", "")
            bg = load_atmospheric_background(width, height, palette, preferred_subject=subject_hint)

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
            "numbered_list": self._render_numbered_list,
            "modern_quote_card": self._render_modern_quote_card,
            "hero_vista": self._render_hero_vista,
            "lifestyle_study": self._render_lifestyle_study
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
        if template_name == "modern_quote_card":
            contrast = calculate_contrast_ratio((15, 23, 42), (255, 255, 255))
        else:
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
        font_wm = load_font("sans", 22)
        wm_text = "THE KINGDOM JOURNAL  •  DAILY EDITORIAL"
        bbox = draw.textbbox((0, 0), wm_text, font=font_wm)
        bw = bbox[2] - bbox[0]
        cx = (left + right) // 2
        draw.text((cx - bw // 2, bottom - 25), wm_text, font=font_wm, fill=colors.get("accent", colors["primary"]))

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
        text_bbox = (s_left, text_y, s_right, text_y + text_h + 110)

        # Apply adaptive scrim
        bg = apply_adaptive_scrim(bg, text_bbox, colors["primary"], colors["tint"], min_contrast=5.5)
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

        # Credit line with auto-wrapping
        font_credit = load_font("sans", 24)
        credit_lines = wrap_text_to_width(f"— {credit}", font_credit, max_w - 48, draw)
        c_y = cur_y + 20
        for cl in credit_lines[:2]:
            # Subtle drop shadow for crisp readability over textured photos
            draw.text((s_left + 25, c_y + 1), cl, font=font_credit, fill=(0, 0, 0))
            draw.text((s_left + 24, c_y), cl, font=font_credit, fill=colors["primary"])
            bbox_c = draw.textbbox((0, 0), cl, font=font_credit)
            c_y += (bbox_c[3] - bbox_c[1]) + 8

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
        text_bbox = (s_left, start_y, s_right, start_y + total_h + 60)

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

        # Credit line with auto-wrapping
        font_credit = load_font("sans", 24)
        credit_lines = wrap_text_to_width(f"— {credit}", font_credit, max_w, draw)
        c_y = y + 25
        for cl in credit_lines[:2]:
            draw.text((s_left, c_y), cl, font=font_credit, fill=colors["primary"])
            bbox_c = draw.textbbox((0, 0), cl, font=font_credit)
            c_y += (bbox_c[3] - bbox_c[1]) + 8

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

    # 7. MODERN QUOTE CARD TEMPLATE (Canva EAGyXr Inspired)
    def _render_modern_quote_card(self, bg, width, height, safe_box, content, colors):
        """Renders clean floating white card over vibrant background with oversized quotation badge."""
        headline = content.get("headline", "")
        credit = content.get("credit", "The Kingdom Journal")
        scripture = content.get("scripture_badge", "Romans 8:26 (WEB)")

        # Prepare base image
        img = bg.convert("RGBA")
        draw = ImageDraw.Draw(img)

        # Diagonal architectural shadow
        draw.polygon([(0, int(height * 0.72)), (width, height), (0, height)], fill=(0, 20, 60, 75))

        # Card dimensions
        card_margin_x = int(width * 0.075)
        card_w = width - (card_margin_x * 2)
        card_h = int(height * 0.72)
        card_x = card_margin_x
        card_y = int((height - card_h) / 2) + 20

        # Multi-layer soft drop shadow
        shadow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(shadow)
        s_draw.rounded_rectangle(
            [card_x + 8, card_y + 14, card_x + card_w + 8, card_y + card_h + 14],
            radius=36,
            fill=(0, 20, 50, 90)
        )
        shadow = shadow.filter(ImageFilter.GaussianBlur(28))
        img = Image.alpha_composite(img, shadow)
        draw = ImageDraw.Draw(img)

        # Solid White Card
        draw.rounded_rectangle(
            [card_x, card_y, card_x + card_w, card_y + card_h],
            radius=36,
            fill=(255, 255, 255, 255)
        )

        # Oversized Quotation Mark Badge at Top Left
        badge_w, badge_h = 135, 115
        badge_x = card_x + 35
        badge_y = card_y - 48
        draw.rounded_rectangle(
            [badge_x, badge_y, badge_x + badge_w, badge_y + badge_h],
            radius=24,
            fill=colors.get("accent", (255, 184, 0))
        )

        # Draw vector quotation marks inside badge
        for offset_x in [0, 38]:
            cx = badge_x + 36 + offset_x
            cy = badge_y + 32
            r = 17
            draw.ellipse([cx, cy, cx + (r * 2), cy + (r * 2)], fill=(255, 255, 255, 255))
            tail = [
                (cx + (r * 2) - 2, cy + r),
                (cx + r, cy + (r * 2) + 18),
                (cx - 4, cy + (r * 2) + 14),
                (cx + 2, cy + r)
            ]
            draw.polygon(tail, fill=(255, 255, 255, 255))

        # Header Section
        font_cat = load_font("sans", 22)
        draw.text((badge_x + badge_w + 35, card_y + 40), "THE KINGDOM JOURNAL", font=font_cat, fill=(30, 41, 59, 255))
        draw.line([(badge_x + badge_w + 35, card_y + 75), (card_x + card_w - 55, card_y + 75)], fill=(226, 232, 240, 255), width=2)

        # Headline
        font_quote = load_font("serif", 56)
        lines = wrap_text_to_width(headline, font_quote, card_w - 130, draw)
        content_area_top = card_y + 140
        content_area_bottom = card_y + card_h - 170
        content_h = len(lines) * 80
        text_start_y = content_area_top + max(0, int((content_area_bottom - content_area_top - content_h) / 2))

        for line in lines:
            draw.text((card_x + 65, text_start_y), line, font=font_quote, fill=(15, 23, 42, 255))
            text_start_y += 80

        # Author Profile Box at Base
        author_card_y = card_y + card_h - 145
        draw.rounded_rectangle(
            [card_x + 50, author_card_y, card_x + card_w - 50, author_card_y + 105],
            radius=20,
            fill=(248, 250, 252, 255)
        )

        avatar_r = 34
        avatar_cx = card_x + 105
        avatar_cy = author_card_y + 52
        draw.ellipse(
            [avatar_cx - avatar_r, avatar_cy - avatar_r, avatar_cx + avatar_r, avatar_cy + avatar_r],
            fill=colors.get("primary", (13, 71, 161))
        )
        initials = "".join([p[0] for p in credit.replace("Line from ", "").split() if p and p[0].isupper()][:2]) or "KJ"
        font_init = load_font("sans", 24)
        i_bbox = draw.textbbox((0, 0), initials, font=font_init)
        draw.text((avatar_cx - (i_bbox[2] - i_bbox[0]) // 2, avatar_cy - (i_bbox[3] - i_bbox[1]) // 2), initials, font=font_init, fill=(255, 255, 255, 255))

        # Name
        font_name = load_font("sans", 26)
        name_x = avatar_cx + avatar_r + 25
        name_y = author_card_y + 26
        speaker_name = credit.replace("Line from ", "").split(",")[0]
        draw.text((name_x, name_y), speaker_name, font=font_name, fill=(15, 23, 42, 255))

        # Verified Checkmark Badge
        n_bbox = draw.textbbox((name_x, name_y), speaker_name, font=font_name)
        check_cx = n_bbox[2] + 24
        check_cy = name_y + 16
        draw.ellipse([check_cx - 12, check_cy - 12, check_cx + 12, check_cy + 12], fill=(37, 99, 235, 255))
        # Check vector
        draw.line([(check_cx - 5, check_cy), (check_cx - 1, check_cy + 5)], fill=(255, 255, 255, 255), width=3)
        draw.line([(check_cx - 1, check_cy + 5), (check_cx + 6, check_cy - 4)], fill=(255, 255, 255, 255), width=3)

        # Handle & Scripture Subline
        font_sub = load_font("sans_regular", 22)
        draw.text((name_x, author_card_y + 64), f"@thekingdomjournal  •  {scripture}", font=font_sub, fill=(100, 116, 139, 255))

        # Masthead
        font_top = load_font("sans", 20)
        top_str = "DAILY KINGDOM EDITORIAL"
        t_bbox = draw.textbbox((0, 0), top_str, font=font_top)
        draw.text(((width - (t_bbox[2] - t_bbox[0])) // 2, card_y - 80), top_str, font=font_top, fill=(255, 255, 255, 230))

        text_bbox = (card_x, card_y, card_x + card_w, card_y + card_h)
        return img.convert("RGB"), text_bbox

    # 8. HERO VISTA TEMPLATE (Canva EAGPQV Inspired)
    def _render_hero_vista(self, bg, width, height, safe_box, content, colors):
        """Renders bold clean uppercase modern typography floating in open scenery sky."""
        s_left, s_top, s_right, s_bottom = safe_box
        headline = content.get("headline", "")
        credit = content.get("credit", "The Kingdom Journal")
        scripture = content.get("scripture_badge", "Romans 8:26 (WEB)")

        img = bg.convert("RGBA")
        draw = ImageDraw.Draw(img)

        # Header
        font_hdr = load_font("sans", 22)
        hdr_text = "THE KINGDOM JOURNAL  •  DAILY EDITORIAL"
        h_bbox = draw.textbbox((0, 0), hdr_text, font=font_hdr)
        hx = (width - (h_bbox[2] - h_bbox[0])) // 2
        hy = s_top + 40
        draw.text((hx + 2, hy + 2), hdr_text, font=font_hdr, fill=(0, 0, 0, 160))
        draw.text((hx, hy), hdr_text, font=font_hdr, fill=(255, 255, 255, 240))

        # Headline
        font_quote = load_font("sans", 50)
        lines = wrap_text_to_width(headline.upper(), font_quote, int(width * 0.85), draw)

        y_pos = hy + 110
        for idx, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font_quote)
            lx = (width - (bbox[2] - bbox[0])) // 2
            draw.text((lx + 3, y_pos + 3), line, font=font_quote, fill=(0, 0, 0, 160))
            # Accent final line in radiant gold
            color = colors.get("accent", (255, 215, 64)) if idx == len(lines) - 1 else (255, 255, 255)
            draw.text((lx, y_pos), line, font=font_quote, fill=color)
            y_pos += 76

        # Credit & Scripture
        y_pos += 45
        font_credit = load_font("sans", 24)
        credit_text = f"— {credit.replace('Line from ', '')}"
        c_bbox = draw.textbbox((0, 0), credit_text, font=font_credit)
        cx = (width - (c_bbox[2] - c_bbox[0])) // 2
        draw.text((cx + 2, y_pos + 2), credit_text, font=font_credit, fill=(0, 0, 0, 160))
        draw.text((cx, y_pos), credit_text, font=font_credit, fill=(255, 255, 255, 240))

        y_pos += 44
        font_scrip = load_font("sans", 20)
        s_bbox = draw.textbbox((0, 0), scripture, font=font_scrip)
        sx = (width - (s_bbox[2] - s_bbox[0])) // 2
        draw.text((sx + 2, y_pos + 2), scripture, font=font_scrip, fill=(0, 0, 0, 160))
        draw.text((sx, y_pos), scripture, font=font_scrip, fill=colors.get("accent", (255, 215, 64)))

        text_bbox = (int(width * 0.08), hy, int(width * 0.92), y_pos + 40)
        return img.convert("RGB"), text_bbox

    # 9. LIFESTYLE STUDY TEMPLATE (Canva EAE48l Inspired)
    def _render_lifestyle_study(self, bg, width, height, safe_box, content, colors):
        """Renders magazine-style left-aligned quote over warm contemplative workspace photograph."""
        headline = content.get("headline", "")
        credit = content.get("credit", "The Kingdom Journal")
        scripture = content.get("scripture_badge", "Romans 8:26 (WEB)")

        img = bg.convert("RGBA")
        draw = ImageDraw.Draw(img)

        # Subtle left-side scrim
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        o_draw = ImageDraw.Draw(overlay)
        for x in range(int(width * 0.75)):
            alpha = int(95 * (1 - (x / (width * 0.75))))
            o_draw.line([(x, 0), (x, height)], fill=(15, 18, 24, alpha))
        img = Image.alpha_composite(img, overlay)
        draw = ImageDraw.Draw(img)

        start_x = int(width * 0.09)
        y_pos = int(height * 0.14)

        font_cat = load_font("sans", 22)
        draw.text((start_x + 2, y_pos + 2), "THE KINGDOM JOURNAL  •  DAILY REVELATION", font=font_cat, fill=(0, 0, 0, 150))
        draw.text((start_x, y_pos), "THE KINGDOM JOURNAL  •  DAILY REVELATION", font=font_cat, fill=(255, 255, 255, 230))

        y_pos += 75
        font_quote = load_font("sans", 52)
        lines = wrap_text_to_width(headline.upper(), font_quote, int(width * 0.65), draw)

        for idx, line in enumerate(lines):
            draw.text((start_x + 3, y_pos + 3), line, font=font_quote, fill=(0, 0, 0, 160))
            # Highlight key phrase
            color = colors.get("accent", (255, 215, 64)) if idx in (1, 2) else (255, 255, 255)
            draw.text((start_x, y_pos), line, font=font_quote, fill=color)
            y_pos += 72

        y_pos += 50
        font_spk = load_font("sans", 26)
        spk_str = f"— {credit.replace('Line from ', '')}"
        draw.text((start_x + 2, y_pos + 2), spk_str, font=font_spk, fill=(0, 0, 0, 160))
        draw.text((start_x, y_pos), spk_str, font=font_spk, fill=(255, 255, 255, 240))

        y_pos += 42
        font_handle = load_font("sans", 22)
        h_str = f"@thekingdomjournal  •  {scripture}"
        draw.text((start_x + 2, y_pos + 2), h_str, font=font_handle, fill=(0, 0, 0, 160))
        draw.text((start_x, y_pos), h_str, font=font_handle, fill=(226, 232, 240, 240))

        text_bbox = (start_x, int(height * 0.14), int(width * 0.75), y_pos + 40)
        return img.convert("RGB"), text_bbox
