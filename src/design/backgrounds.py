"""
Milestone 3: Text-Free Background Generator & AI Prompt Engine (src/design/backgrounds.py)
Generates high-resolution atmospheric procedural backgrounds (vignette, grain, ray light)
and formats strict text-free AI image prompts following institutional design rules.
"""

import math
import random
from typing import Dict, Tuple
from PIL import Image, ImageDraw

THEMED_SUBJECT_MAP = {
    "light": [
        "wide-angle 35mm film photograph of a majestic mountain summit overlooking golden dawn clouds with clean open sky in upper 60%",
        "golden dawn rays breaking through morning mist over distant mountain ridges with vast calm negative space in the sky",
        "shaft of radiant celestial morning sunlight breaking through dramatic parted clouds over still waters"
    ],
    "prayer": [
        "authentic warm minimalist wooden study desk with an open Bible journal, fountain pen, and a brass desk lamp casting gentle bokeh",
        "peaceful sunlit morning reading table with an open notebook, ceramic mug, and soft golden window light casting gentle shadows",
        "solitary silhouette standing on a rugged rocky overlook at dusk looking out at an expansive calm pastel sunset sky"
    ],
    "worship": [
        "breathtaking panoramic ocean horizon with calm waves catching gentle morning sunlight and expansive calm sky",
        "vast tranquil mountain valley at dawn bathed in warm amber and peach morning glow with vast open sky",
        "gentle morning light illuminating a quiet wooden sanctuary bench beside tall sunlit windows"
    ],
    "default": [
        "wide-angle 35mm film photograph of rugged rocky mountain ridges during golden hour with clear gradient sky occupying the upper 60%",
        "aesthetic warm lifestyle study workspace with open journal, laptop, potted plant, and glowing ambient lamp bokeh",
        "peaceful misty sunrise horizon over still reflective waters with vast calm open negative space in the sky"
    ]
}

def generate_text_free_image_prompt(theme: str, palette_name: str = "royal_blue_gold") -> str:
    t_lower = (theme or "").lower()
    if any(k in t_lower for k in ["light", "understanding", "glory", "mind", "sight", "illumination"]):
        category = "light"
    elif any(k in t_lower for k in ["prayer", "secret", "devotion", "groan", "altar", "closet", "night"]):
        category = "prayer"
    elif any(k in t_lower for k in ["worship", "praise", "hallelujah", "sound", "adoration", "song"]):
        category = "worship"
    else:
        category = "default"

    import random
    subject = random.choice(THEMED_SUBJECT_MAP[category])
    palette_desc = palette_name.replace("_", " ")

    prompt = (
        f"{subject}, reverent contemplative mood, natural atmospheric light, "
        f"{palette_desc} color grading, vertical composition with vast calm negative space "
        f"for typography, cinematic 35mm film photography, shallow depth of field, 8k resolution, "
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
