"""
Cloud Image Generator & Autonomous Studio Compositor
Runs inside GitHub Actions daily at 6:45 AM before email dispatch.
Generates 1:1 Square and 9:16 Vertical viral fliers using either:
1. Google Imagen 3 / Gemini 2.0 API (when GEMINI_API_KEY is configured in GitHub Secrets)
2. Studio-Grade Autonomous Compositor (using bundled Google Fonts & high-res backgrounds)
"""

import json
import os
import sys
import textwrap
import urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"
FLIERS_DIR = BASE_DIR / "reports" / "fliers"

def load_env():
    env_file = BASE_DIR / ".env"
    if env_file.is_file():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k and k not in os.environ:
                    os.environ[k] = v

def get_font(font_name: str, size: int):
    fpath = FONTS_DIR / font_name
    if fpath.is_file():
        try:
            return ImageFont.truetype(str(fpath), size)
        except Exception:
            pass
    # Fallback search in Windows or Linux system paths
    for p in [Path("C:/Windows/Fonts"), Path("/usr/share/fonts")]:
        alt = p / font_name
        if alt.is_file():
            try:
                return ImageFont.truetype(str(alt), size)
            except Exception:
                pass
    return ImageFont.load_default()

def generate_via_imagen_api(prompt: str, aspect_ratio: str, output_path: Path, api_key: str) -> bool:
    """Calls Google Imagen 3 API to generate an authentic image."""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={api_key}"
        payload = {
            "instances": [{"prompt": prompt}],
            "parameters": {
                "sampleCount": 1,
                "aspectRatio": "1:1" if aspect_ratio == "1:1" else "9:16",
                "outputMimeType": "image/jpeg"
            }
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            predictions = result.get("predictions", [])
            if predictions and "bytesBase64Encoded" in predictions[0]:
                import base64
                img_data = base64.b64decode(predictions[0]["bytesBase64Encoded"])
                output_path.write_bytes(img_data)
                print(f"[IMAGEN API SUCCESS] Generated {output_path.name}")
                return True
    except Exception as e:
        print(f"[IMAGEN API NOTICE] Cloud generation fallback to compositor: {e}", file=sys.stderr)
    return False

def render_studio_composite(
    base_art_path: Path,
    output_path: Path,
    hook_top: str,
    banner_text: str,
    body_quote: str,
    speaker_scripture: str,
    target_dim: tuple = (1080, 1080),
    accent_color: tuple = (217, 119, 6) # Amber/Gold
):
    """Studio-grade compositor using bundled Google Fonts and crisp anti-aliased rendering."""
    FLIERS_DIR.mkdir(parents=True, exist_ok=True)
    tw, th = target_dim

    if base_art_path and base_art_path.is_file():
        img = Image.open(base_art_path).convert("RGBA")
        # Smart crop & center
        sw, sh = img.size
        aspect_src = sw / sh
        aspect_tgt = tw / th
        if aspect_src > aspect_tgt:
            nw = int(sh * aspect_tgt)
            ox = (sw - nw) // 2
            cropped = img.crop((ox, 0, ox + nw, sh))
        else:
            nh = int(sw / aspect_tgt)
            oy = (sh - nh) // 2
            cropped = img.crop((0, oy, sw, oy + nh))
        canvas = cropped.resize((tw, th), Image.Resampling.LANCZOS)
    else:
        # Generate rich deep sanctuary gradient if no base image provided
        canvas = Image.new("RGBA", (tw, th), (15, 23, 42, 255))
        draw_c = ImageDraw.Draw(canvas)
        for y in range(th):
            r = int(18 + (35 - 18) * (y / th))
            g = int(24 + (40 - 24) * (y / th))
            b = int(38 + (55 - 38) * (y / th))
            draw_c.line([(0, y), (tw, y)], fill=(r, g, b, 255))

    # Add dark vignette for high contrast readability
    vignette = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    v_draw = ImageDraw.Draw(vignette)
    
    # Top and bottom dark gradient
    for y in range(int(th * 0.45)):
        ratio = y / (th * 0.45)
        alpha = int(180 * (1 - ratio))
        v_draw.line([(0, y), (tw, y)], fill=(8, 10, 15, alpha))
        
    for y in range(int(th * 0.65), th):
        ratio = (y - int(th * 0.65)) / (th * 0.35)
        alpha = int(220 * (ratio ** 1.2))
        v_draw.line([(0, y), (tw, y)], fill=(8, 10, 15, alpha))

    final_canvas = Image.alpha_composite(canvas, vignette)
    draw = ImageDraw.Draw(final_canvas)

    # Outer Thin Gold Border
    border_margin = 28
    draw.rectangle(
        [(border_margin, border_margin), (tw - border_margin, th - border_margin)],
        outline=(217, 119, 6, 140),
        width=2
    )

    # Load Google Fonts
    font_serif = get_font("PlayfairDisplay-Bold.ttf", 36 if tw == 1080 and th == 1080 else 42)
    font_banner = get_font("Montserrat-Bold.ttf", 44 if tw == 1080 and th == 1080 else 52)
    font_quote = get_font("PlayfairDisplay-Bold.ttf", 28 if tw == 1080 and th == 1080 else 32)
    font_meta = get_font("Montserrat-Bold.ttf", 18 if tw == 1080 and th == 1080 else 22)

    # 1. Top Hook
    start_y = int(th * 0.08)
    hook_lines = textwrap.wrap(hook_top.upper(), width=28)
    curr_y = start_y
    for hline in hook_lines:
        # Subtle drop shadow
        draw.text((tw // 2 + 1, curr_y + 1), hline, font=font_serif, fill=(0, 0, 0, 220), anchor="mt")
        draw.text((tw // 2, curr_y), hline, font=font_serif, fill=(250, 250, 249, 255), anchor="mt")
        curr_y += 48

    # 2. Textured Banner
    curr_y += 12
    bbox = draw.textbbox((0, 0), banner_text.upper(), font=font_banner)
    bw = bbox[2] - bbox[0] + 48
    bh = bbox[3] - bbox[1] + 24
    bx1 = (tw - bw) // 2
    by1 = curr_y
    bx2 = bx1 + bw
    by2 = by1 + bh

    # Draw rounded banner
    draw.rounded_rectangle([(bx1, by1), (bx2, by2)], radius=8, fill=(217, 119, 6, 240), outline=(245, 158, 11, 255), width=2)
    draw.text((tw // 2, by1 + 10), banner_text.upper(), font=font_banner, fill=(15, 23, 42, 255), anchor="mt")

    # 3. Vector Gold Divider Line
    curr_y = by2 + 24
    draw.line([(tw // 2 - 120, curr_y), (tw // 2 + 120, curr_y)], fill=(217, 119, 6, 200), width=2)
    draw.ellipse([(tw // 2 - 4, curr_y - 4), (tw // 2 + 4, curr_y + 4)], fill=(245, 158, 11, 255))

    # 4. Body Quote (Lower Section for optimal reading)
    quote_y = int(th * 0.76) if th > 1080 else int(th * 0.72)
    quote_lines = textwrap.wrap(f'"{body_quote}"', width=32 if tw == 1080 and th == 1080 else 28)
    for qline in quote_lines:
        draw.text((tw // 2 + 1, quote_y + 1), qline, font=font_quote, fill=(0, 0, 0, 240), anchor="mt")
        draw.text((tw // 2, quote_y), qline, font=font_quote, fill=(245, 245, 244, 255), anchor="mt")
        quote_y += 38

    # 5. Speaker & Scripture Badge
    quote_y += 14
    draw.text((tw // 2, quote_y), speaker_scripture.upper(), font=font_meta, fill=(217, 119, 6, 240), anchor="mt")

    # Convert to RGB and save
    final_canvas.convert("RGB").save(str(output_path), "JPEG", quality=95)
    print(f"[STUDIO COMPOSITOR] Rendered high-res flier at {output_path.name}")
    return True

def generate_daily_fliers():
    load_env()
    FLIERS_DIR.mkdir(parents=True, exist_ok=True)
    gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()

    square_out = FLIERS_DIR / "flyer_dawn_square.jpg"
    story_out = FLIERS_DIR / "flyer_secret_place_story.jpg"

    # Prompts for today's topic
    sq_prompt = (
        "A high-impact viral Christian gospel quote flyer for today: Divine Help at Break of Day. "
        "A handsome young Black male worshipper with eyes closed in serene prayer holding a gold-gilded Holy Bible, "
        "golden sunrise dawn light streaming through an airy sanctuary window. Crisp typography reading: "
        "'WHEN HUMAN CAPACITY REACHES ITS END, DIVINE HELP BEGINS AT DAWN. Psalm 46:5', 8k resolution, cinematic."
    )
    story_prompt = (
        "A vertical 9:16 mobile wallpaper and status graphic poster. A graceful young Black female believer seated "
        "in peaceful morning prayer over an open gold-edged Holy Bible beside an amber lantern glow. "
        "Typography: 'NEVER UNDERESTIMATE THE SILENT SEASONS • WHAT GOD BUILDS IN SECRET cannot be dismantled in public • Isaiah 40:31', 8k."
    )

    # 1. Try Imagen API if key is present
    if gemini_key:
        print("[CLOUD GENERATOR] GEMINI_API_KEY detected. Attempting cloud Imagen synthesis...")
        sq_ok = generate_via_imagen_api(sq_prompt, "1:1", square_out, gemini_key)
        st_ok = generate_via_imagen_api(story_prompt, "9:16", story_out, gemini_key)
        if sq_ok and st_ok:
            return True

    # 2. Studio Compositor fallback
    print("[CLOUD GENERATOR] Utilizing Studio Compositor with Google Fonts...")
    # Use existing high-res photographic bases if available
    base_sq = square_out if square_out.is_file() else None
    base_st = story_out if story_out.is_file() else None

    # If already exists and valid, we keep the existing photorealistic assets
    if base_sq and base_st and base_sq.stat().st_size > 100000 and base_st.stat().st_size > 100000:
        print(f"[CLOUD GENERATOR] High-res studio assets verified: {square_out.name} ({base_sq.stat().st_size} bytes), {story_out.name} ({base_st.stat().st_size} bytes)")
        return True

    # Otherwise synthesize fresh
    render_studio_composite(
        base_art_path=base_sq,
        output_path=square_out,
        hook_top="When human capacity reaches its end",
        banner_text="Divine Help Begins at Dawn",
        body_quote="You do not have to panic over battles God has already scheduled for your deliverance.",
        speaker_scripture="Psalm 46:5 • Victoria Orenze & Apostle Joshua Selman",
        target_dim=(1080, 1080)
    )

    render_studio_composite(
        base_art_path=base_st,
        output_path=story_out,
        hook_top="Never underestimate the silent seasons",
        banner_text="What God Builds in Secret",
        body_quote="What God builds in secret cannot be dismantled in public.",
        speaker_scripture="Isaiah 40:31 • Apostle Joshua Selman",
        target_dim=(1080, 1920)
    )

    return True

if __name__ == "__main__":
    generate_daily_fliers()
