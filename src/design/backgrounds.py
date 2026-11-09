"""
Milestone 3: Text-Free Background Generator & AI Prompt Engine (src/design/backgrounds.py)
Generates high-resolution atmospheric procedural backgrounds (vignette, grain, ray light)
and formats strict text-free AI image prompts following institutional design rules.
"""

import math
import random
from typing import Dict, Tuple
from PIL import Image, ImageDraw

SYMBOLIC_SUBJECTS = [
    "solitary bronze oil lamp burning on a rustic wooden table in a dimly lit sacred chamber",
    "golden dawn light streaming through a weathered tall cathedral arched doorway onto stone floor",
    "serene morning mist rising over distant mountain ridges at sunrise with deep atmospheric depth",
    "empty wooden chair situated near a morning window bathed in gentle sacred dawn rays",
    "ancient quiet courtyard path illuminated by warm amber lantern glow at night",
    "silhouetted figure standing in quiet contemplative prayer on a high rocky overlook at twilight",
    "shaft of golden celestial light breaking through dramatic parted storm clouds over still waters"
]

def generate_text_free_image_prompt(theme: str, palette_name: str = "navy_gold") -> str:
    """
    Constructs a model-ready image prompt following Master Prompt constraints:
    - Text-free guarantee
    - Clear negative space
    - No faces, no close-up hands, no letters, no watermarks
    """
    subject = random.choice(SYMBOLIC_SUBJECTS)
    prompt = (
        f"{subject}, reverent contemplative mood, atmospheric volumetric light beams, "
        f"{palette_name.replace('_', ' ')} color grading, vertical composition with vast calm negative space "
        f"in the center for typography, cinematic 35mm film photography, shallow depth of field, 8k resolution, "
        f"no text, no letters, no words, no signs, no typography, no logos, no watermark, "
        f"no recognizable real faces, no close-up hands, no depiction of Jesus face."
    )
    return prompt

def generate_procedural_background(
    width: int,
    height: int,
    palette: Dict
) -> Image.Image:
    """
    Generates a procedural, textured atmospheric background with
    subtle radial glow, gradient, and fine film grain texture.
    """
    # 1. Base gradient canvas
    bg_hex = palette.get("bg_primary", "#0A1128")
    accent_hex = palette.get("accent", "#D4AF37")
    tint_rgb = palette.get("scrim_tint", [10, 17, 40])

    def hex_to_rgb(h):
        h = h.lstrip("#")
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    c_dark = hex_to_rgb(bg_hex)
    c_accent = hex_to_rgb(accent_hex)

    img = Image.new("RGBA", (width, height), (c_dark[0], c_dark[1], c_dark[2], 255))
    draw = ImageDraw.Draw(img)

    # 2. Vertical ambient tone gradient
    for y in range(height):
        ratio = y / float(height)
        # Deepening downwards
        r = int(c_dark[0] * (1.1 - 0.3 * ratio))
        g = int(c_dark[1] * (1.1 - 0.3 * ratio))
        b = int(c_dark[2] * (1.1 - 0.3 * ratio))
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    # 3. Soft radial heavenly glow in upper-middle zone
    glow_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)

    glow_cx = int(width * 0.5)
    glow_cy = int(height * 0.32)
    max_radius = int(width * 0.65)

    # Concentric soft rings
    for r in range(max_radius, 0, -12):
        frac = 1.0 - (r / max_radius)
        alpha = int(32 * (frac ** 1.8))
        ring_color = (c_accent[0], c_accent[1], c_accent[2], alpha)
        glow_draw.ellipse(
            [(glow_cx - r, glow_cy - r), (glow_cx + r, glow_cy + r)],
            fill=ring_color
        )

    # Composite glow
    img = Image.alpha_composite(img, glow_layer)

    # 4. Subtle procedural film grain
    grain_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    grain_draw = ImageDraw.Draw(grain_layer)
    # Stippled procedural grain (sample grid for performance)
    random.seed(42 + width + height)
    for _ in range(int(width * height * 0.008)):
        gx = random.randint(0, width - 1)
        gy = random.randint(0, height - 1)
        g_val = random.randint(200, 255)
        g_alpha = random.randint(6, 14)
        grain_draw.point((gx, gy), fill=(g_val, g_val, g_val, g_alpha))

    img = Image.alpha_composite(img, grain_layer)
    return img.convert("RGB")

def load_atmospheric_background(
    width: int,
    height: int,
    palette: Dict,
    preferred_subject: str = None
) -> Image.Image:
    """
    Loads a high-resolution text-free photographic background from assets/backgrounds/,
    center-crops to target dimensions, and falls back smoothly to procedural gradient
    if no files exist or loading fails.
    """
    from pathlib import Path
    base_dir = Path(__file__).resolve().parent.parent.parent
    bg_dir = base_dir / "assets" / "backgrounds"
    bg_dir.mkdir(parents=True, exist_ok=True)

    valid_exts = {".jpg", ".jpeg", ".png", ".webp"}
    available_files = [p for p in bg_dir.iterdir() if p.suffix.lower() in valid_exts]

    if available_files:
        selected_file = None
        if preferred_subject:
            keywords = preferred_subject.lower().split()
            for f in available_files:
                if any(k in f.stem.lower() for k in keywords):
                    selected_file = f
                    break
        if not selected_file:
            selected_file = random.choice(available_files)

        try:
            with Image.open(selected_file) as raw_img:
                img = raw_img.convert("RGB")
                img_w, img_h = img.size
                target_ratio = width / height
                img_ratio = img_w / img_h
                if img_ratio > target_ratio:
                    new_w = int(img_h * target_ratio)
                    left = (img_w - new_w) // 2
                    img = img.crop((left, 0, left + new_w, img_h))
                else:
                    new_h = int(img_w / target_ratio)
                    top = (img_h - new_h) // 2
                    img = img.crop((0, top, img_w, top + new_h))

                return img.resize((width, height), Image.Resampling.LANCZOS)
        except Exception:
            pass

    return generate_procedural_background(width, height, palette)
