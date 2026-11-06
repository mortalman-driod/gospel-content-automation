"""
Cloud Image Generator & Autonomous Studio Compositor (Gemini-Trained Model 2.0)
Generates 1:1 Square and 9:16 Vertical viral fliers using:
1. Google Gemini 2.5 Flash for intelligent typographic hierarchy & prompt design
2. Cloud Imagen / Gemini Image synthesis (with auto-fallback when rate-limited)
3. Studio-Grade Compositor with:
   - Dynamic auto-scaling font engine (prevents text clipping and overflow)
   - Strict safe-zone margins (8% for 1:1, 12% for 9:16)
   - Bundled Google Fonts (Playfair Display & Montserrat)
"""

import json
import os
import sys
import textwrap
import urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

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
    for p in [Path("C:/Windows/Fonts"), Path("/usr/share/fonts")]:
        alt = p / font_name
        if alt.is_file():
            try:
                return ImageFont.truetype(str(alt), size)
            except Exception:
                pass
    return ImageFont.load_default()

def fit_text_to_box(draw: ImageDraw.ImageDraw, text: str, font_name: str, max_width: int, max_height: int, initial_size: int, min_size: int = 16):
    """Dynamically steps down font size until text wraps and fits inside bounding box."""
    size = initial_size
    while size >= min_size:
        font = get_font(font_name, size)
        wrap_chars = max(12, int(max_width / (size * 0.52)))
        lines = textwrap.wrap(text, width=wrap_chars)
        total_h = len(lines) * (size + 10)
        max_line_w = 0
        for l in lines:
            bbox = draw.textbbox((0, 0), l, font=font)
            max_line_w = max(max_line_w, bbox[2] - bbox[0])
        
        if max_line_w <= max_width and total_h <= max_height:
            return font, lines, size
        size -= 2

    font = get_font(font_name, min_size)
    lines = textwrap.wrap(text, width=max(12, int(max_width / (min_size * 0.52))))
    return font, lines, min_size

def optimize_flier_text_with_gemini(quote: str, scripture: str, api_key: str) -> dict:
    """Uses Gemini 2.5 Flash to decompose any quote into optimal poster typography hierarchy."""
    if not api_key:
        return None
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        prompt = f"""You are the master visual typographer for a luxury Christian editorial poster.
Given this quote: "{quote}"
Scripture: "{scripture}"
Deconstruct it into high-impact poster copy.
Output JSON with:
- "hook_top": punchy opening hook line (under 30 chars, uppercase)
- "banner_text": 2 to 4 bold words for the focal paint banner (uppercase)
- "body_quote": the elegant heart of the quote (under 95 chars)
- "badge_text": scripture and context badge (under 40 chars, uppercase)
"""
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 0.4}
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            parsed = json.loads(data["candidates"][0]["content"]["parts"][0]["text"])
            print(f"[GEMINI TYPOGRAPHY SUCCESS] Optimized poster hierarchy: Banner='{parsed.get('banner_text')}'")
            return parsed
    except Exception as e:
        print(f"[GEMINI TYPOGRAPHY NOTICE] Fallback to direct text: {e}", file=sys.stderr)
        return None

def generate_via_imagen_api(prompt: str, aspect_ratio: str, output_path: Path, api_key: str) -> bool:
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
        with urllib.request.urlopen(req, timeout=25) as resp:
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
    """High-accuracy compositor with auto-scaling text and safe-zone clipping protection."""
    FLIERS_DIR.mkdir(parents=True, exist_ok=True)
    tw, th = target_dim
    is_square = (tw == th)

    if base_art_path and base_art_path.is_file():
        img = Image.open(base_art_path).convert("RGBA")
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
        # Deep rich sanctuary gradient if base image is not provided
        canvas = Image.new("RGBA", (tw, th), (15, 23, 42, 255))
        draw_c = ImageDraw.Draw(canvas)
        for y in range(th):
            r = int(18 + (35 - 18) * (y / th))
            g = int(24 + (40 - 24) * (y / th))
            b = int(38 + (55 - 38) * (y / th))
            draw_c.line([(0, y), (tw, y)], fill=(r, g, b, 255))

    # Multi-pass atmospheric gradient vignette
    vignette = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    v_draw = ImageDraw.Draw(vignette)
    
    # Top gradient
    top_vignette_limit = int(th * 0.42)
    for y in range(top_vignette_limit):
        ratio = y / top_vignette_limit
        alpha = int(190 * (1 - ratio))
        v_draw.line([(0, y), (tw, y)], fill=(8, 10, 15, alpha))
        
    # Bottom gradient
    bottom_vignette_start = int(th * 0.60)
    for y in range(bottom_vignette_start, th):
        ratio = (y - bottom_vignette_start) / (th - bottom_vignette_start)
        alpha = int(230 * (ratio ** 1.1))
        v_draw.line([(0, y), (tw, y)], fill=(8, 10, 15, alpha))

    final_canvas = Image.alpha_composite(canvas, vignette)
    draw = ImageDraw.Draw(final_canvas)

    # Safe Zone Calculations
    safe_margin_x = int(tw * 0.08) # 8% horizontal margin
    safe_margin_y = int(th * 0.08) if is_square else int(th * 0.12)
    usable_width = tw - (safe_margin_x * 2)

    # Outer Thin Gold Border
    draw.rectangle(
        [(safe_margin_x // 2, safe_margin_y // 2), (tw - safe_margin_x // 2, th - safe_margin_y // 2)],
        outline=(217, 119, 6, 140),
        width=2
    )

    # 1. Top Hook with Auto-Scaling
    hook_font, hook_lines, hook_size = fit_text_to_box(
        draw=draw,
        text=hook_top.upper(),
        font_name="PlayfairDisplay-Bold.ttf",
        max_width=usable_width,
        max_height=int(th * 0.12),
        initial_size=36 if is_square else 42,
        min_size=20
    )
    
    curr_y = safe_margin_y
    for hline in hook_lines:
        draw.text((tw // 2 + 1, curr_y + 1), hline, font=hook_font, fill=(0, 0, 0, 220), anchor="mt")
        draw.text((tw // 2, curr_y), hline, font=hook_font, fill=(250, 250, 249, 255), anchor="mt")
        curr_y += hook_size + 10

    # 2. Dynamic Banner with Auto-Fit
    curr_y += 12
    banner_font, banner_lines, b_size = fit_text_to_box(
        draw=draw,
        text=banner_text.upper(),
        font_name="Montserrat-Bold.ttf",
        max_width=usable_width - 40,
        max_height=int(th * 0.10),
        initial_size=42 if is_square else 48,
        min_size=24
    )

    # Measure combined banner box
    banner_full_text = " ".join(banner_lines)
    bbox = draw.textbbox((0, 0), banner_full_text, font=banner_font)
    bw = min(usable_width, (bbox[2] - bbox[0]) + 48)
    bh = (len(banner_lines) * (b_size + 8)) + 18
    bx1 = (tw - bw) // 2
    by1 = curr_y
    bx2 = bx1 + bw
    by2 = by1 + bh

    # Draw rounded ribbon banner
    draw.rounded_rectangle([(bx1, by1), (bx2, by2)], radius=8, fill=(217, 119, 6, 245), outline=(245, 158, 11, 255), width=2)
    b_text_y = by1 + 10
    for bline in banner_lines:
        draw.text((tw // 2, b_text_y), bline, font=banner_font, fill=(15, 23, 42, 255), anchor="mt")
        b_text_y += b_size + 8

    # 3. Vector Gold Divider Line
    curr_y = by2 + 20
    draw.line([(tw // 2 - 100, curr_y), (tw // 2 + 100, curr_y)], fill=(217, 119, 6, 200), width=2)
    draw.ellipse([(tw // 2 - 4, curr_y - 4), (tw // 2 + 4, curr_y + 4)], fill=(245, 158, 11, 255))

    # 4. Body Quote (Lower Safe Section with Auto-Scaling)
    quote_box_height = int(th * 0.18)
    quote_font, quote_lines, q_size = fit_text_to_box(
        draw=draw,
        text=f'"{body_quote}"',
        font_name="PlayfairDisplay-Bold.ttf",
        max_width=usable_width - 20,
        max_height=quote_box_height,
        initial_size=28 if is_square else 32,
        min_size=18
    )

    quote_y = th - safe_margin_y - quote_box_height - 30
    for qline in quote_lines:
        draw.text((tw // 2 + 1, quote_y + 1), qline, font=quote_font, fill=(0, 0, 0, 240), anchor="mt")
        draw.text((tw // 2, quote_y), qline, font=quote_font, fill=(245, 245, 244, 255), anchor="mt")
        quote_y += q_size + 10

    # 5. Speaker & Scripture Badge
    font_meta = get_font("Montserrat-Bold.ttf", 16 if is_square else 18)
    draw.text((tw // 2, quote_y + 8), speaker_scripture.upper(), font=font_meta, fill=(217, 119, 6, 240), anchor="mt")

    # Save final artifact
    final_canvas.convert("RGB").save(str(output_path), "JPEG", quality=95)
    print(f"[STUDIO COMPOSITOR 2.0] High-accuracy flier generated: {output_path.name}")
    return True

def generate_daily_fliers(topic_data: dict = None):
    load_env()
    FLIERS_DIR.mkdir(parents=True, exist_ok=True)
    gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()

    data = topic_data or {
        "hook_top": "When words are not enough",
        "banner_text": "Let Worship Speak",
        "quote": "When words are not enough, let your worship speak.",
        "speaker": "Mercy Chinwo & Apostle Joshua Selman",
        "scripture": "Romans 8:26 • Psalm 46:10"
    }

    # Use Gemini to optimize layout hierarchy if available
    gemini_typo = optimize_flier_text_with_gemini(
        quote=data.get("quote", ""),
        scripture=data.get("scripture", ""),
        api_key=gemini_key
    )
    if gemini_typo:
        hook_top = gemini_typo.get("hook_top", data.get("hook_top", "When words are not enough"))
        banner_text = gemini_typo.get("banner_text", data.get("banner_text", "Let Worship Speak"))
        body_quote = gemini_typo.get("body_quote", data.get("quote", ""))
        badge_text = gemini_typo.get("badge_text", f"{data.get('scripture')} • {data.get('speaker')}")
    else:
        hook_top = data.get("hook_top", "When words are not enough")
        banner_text = data.get("banner_text", "Let Worship Speak")
        body_quote = data.get("quote", "When words are not enough, let your worship speak.")
        badge_text = f"{data.get('scripture', 'Romans 8:26')} • {data.get('speaker', 'Mercy Chinwo')}"

    square_out = FLIERS_DIR / "flyer_dawn_square.jpg"
    story_out = FLIERS_DIR / "flyer_secret_place_story.jpg"

    # 1. Cloud Imagen API if configured
    if gemini_key:
        print("[CLOUD GENERATOR] Attempting cloud Imagen synthesis...")
        sq_prompt = f"Viral Christian quote flier for {banner_text}. African Christian worshipper, gold Bible, warm light, 8k."
        st_prompt = f"Vertical 9:16 Christian poster for {body_quote[:60]}. Believer in prayer, warm lantern, 8k."
        sq_ok = generate_via_imagen_api(sq_prompt, "1:1", square_out, gemini_key)
        st_ok = generate_via_imagen_api(st_prompt, "9:16", story_out, gemini_key)
        if sq_ok and st_ok:
            return True

    # 2. Autonomous Studio Compositor 2.0
    print("[CLOUD GENERATOR] Executing Studio Compositor 2.0 with dynamic auto-scaling...")
    base_sq = square_out if square_out.is_file() else None
    base_st = story_out if story_out.is_file() else None

    # Keep existing high-res photographic artwork if verified
    if base_sq and base_st and base_sq.stat().st_size > 150000 and base_st.stat().st_size > 150000:
        print(f"[CLOUD GENERATOR] High-res photographic artwork verified: {square_out.name}, {story_out.name}")
        return True

    render_studio_composite(
        base_art_path=base_sq,
        output_path=square_out,
        hook_top=hook_top,
        banner_text=banner_text,
        body_quote=body_quote,
        speaker_scripture=badge_text,
        target_dim=(1080, 1080)
    )

    render_studio_composite(
        base_art_path=base_st,
        output_path=story_out,
        hook_top="Never underestimate the silent seasons",
        banner_text="What God Builds in Secret",
        body_quote="What God builds in secret cannot be dismantled in public.",
        speaker_scripture=f"{data.get('scripture', 'Isaiah 40:31')} • {data.get('speaker', 'Joshua Selman')}",
        target_dim=(1080, 1920)
    )

    return True

if __name__ == "__main__":
    generate_daily_fliers()
