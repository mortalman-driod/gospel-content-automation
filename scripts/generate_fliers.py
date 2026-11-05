"""
Gospel Social Media Flier Generator
Generates high-resolution viral graphic fliers with professional typography,
custom gradients, quote blocks, and platform-optimized aspect ratios.
"""

import argparse
import math
import os
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def get_font(font_name="segoeuib.ttf", size=32):
    fonts_dir = Path("C:/Windows/Fonts")
    font_path = fonts_dir / font_name
    if not font_path.is_file():
        font_path = fonts_dir / "arialbd.ttf"
    if font_path.is_file():
        return ImageFont.truetype(str(font_path), size)
    return ImageFont.load_default()

def draw_gradient_background(width, height, top_color, bottom_color, glow_center=None, glow_radius=400):
    img = Image.new("RGBA", (width, height), top_color)
    draw = ImageDraw.Draw(img)
    
    # Linear vertical gradient
    r1, g1, b1 = top_color
    r2, g2, b2 = bottom_color
    for y in range(height):
        ratio = y / height
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))
        
    # Subtle radial glow
    if glow_center:
        glow_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_layer)
        cx, cy = glow_center
        for rad in range(glow_radius, 0, -10):
            alpha = int(45 * (1 - (rad / glow_radius)))
            glow_draw.ellipse(
                [(cx - rad, cy - rad), (cx + rad, cy + rad)],
                fill=(245, 158, 11, alpha)  # Warm golden amber glow
            )
        img = Image.alpha_composite(img, glow_layer)
        
    return img

def create_flier(
    output_path: Path,
    topic: str,
    quote: str,
    speaker: str,
    scripture: str,
    aspect: str = "square", # 'square' (1080x1080), 'story' (1080x1920), 'twitter' (1200x675)
    platform_label: str = "INSTAGRAM & FACEBOOK"
):
    if aspect == "story":
        w, h = 1080, 1920
        title_font_size = 54
        quote_font_size = 56
        wrap_width = 24
        glow_center = (w // 2, h // 3)
    elif aspect == "twitter":
        w, h = 1200, 675
        title_font_size = 36
        quote_font_size = 40
        wrap_width = 38
        glow_center = (w // 2, h // 2)
    else: # square
        w, h = 1080, 1080
        title_font_size = 44
        quote_font_size = 48
        wrap_width = 26
        glow_center = (w // 2, h // 2 - 50)

    # Midnight indigo to deep obsidian blue
    top_color = (12, 17, 34)
    bottom_color = (30, 27, 75)
    base = draw_gradient_background(w, h, top_color, bottom_color, glow_center)
    draw = ImageDraw.Draw(base)

    # Outer decorative border
    margin = 35
    draw.rectangle(
        [(margin, margin), (w - margin, h - margin)],
        outline=(217, 119, 6, 90), # Subtle gold border
        width=2
    )

    # Top Tag / Category pill
    tag_font = get_font("segoeui.ttf", 22)
    pill_text = f"✨  {topic.upper()}  ✨"
    bbox = draw.textbbox((0, 0), pill_text, font=tag_font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    top_y = 75 if aspect != "story" else 140
    pill_x1 = (w - tw) // 2 - 20
    pill_y1 = top_y
    pill_x2 = pill_x1 + tw + 40
    pill_y2 = pill_y1 + th + 16
    
    draw.rounded_rectangle([(pill_x1, pill_y1), (pill_x2, pill_y2)], radius=18, fill=(245, 158, 11, 40), outline=(245, 158, 11, 180), width=1)
    draw.text((pill_x1 + 20, pill_y1 + 8), pill_text, fill=(251, 191, 36, 255), font=tag_font)

    # Large Quotation Mark
    quote_mark_font = get_font("georgiab.ttf", 90 if aspect != "twitter" else 65)
    qmark_y = pill_y2 + (30 if aspect != "twitter" else 15)
    draw.text(((w - 40) // 2, qmark_y), "“", fill=(217, 119, 6, 200), font=quote_mark_font)

    # Main Quote Text wrapped
    quote_font = get_font("segoeuib.ttf", quote_font_size)
    wrapped_lines = textwrap.wrap(quote, width=wrap_width)
    line_height = quote_font_size + 16
    total_text_h = len(wrapped_lines) * line_height
    
    # Calculate starting Y to keep quote nicely centered
    start_y = qmark_y + (80 if aspect != "twitter" else 60)
    for i, line in enumerate(wrapped_lines):
        line_bbox = draw.textbbox((0, 0), line, font=quote_font)
        lw = line_bbox[2] - line_bbox[0]
        lx = (w - lw) // 2
        ly = start_y + (i * line_height)
        
        # Drop shadow for readability
        draw.text((lx + 2, ly + 2), line, fill=(5, 5, 10, 200), font=quote_font)
        draw.text((lx, ly), line, fill=(255, 255, 255, 255), font=quote_font)

    # Divider line
    div_y = start_y + total_text_h + (35 if aspect != "twitter" else 20)
    div_w = 160
    draw.line([((w - div_w) // 2, div_y), ((w + div_w) // 2, div_y)], fill=(245, 158, 11, 230), width=3)

    # Speaker / Attribution
    speaker_font = get_font("segoeuib.ttf", 28 if aspect != "twitter" else 24)
    sp_text = f"— {speaker.upper()} —"
    s_bbox = draw.textbbox((0, 0), sp_text, font=speaker_font)
    sw = s_bbox[2] - s_bbox[0]
    draw.text(((w - sw) // 2, div_y + 20), sp_text, fill=(253, 230, 138, 255), font=speaker_font)

    # Scripture / Anchor note
    if scripture:
        scrip_font = get_font("segoeui.ttf", 22 if aspect != "twitter" else 18)
        scrip_text = scripture
        sc_bbox = draw.textbbox((0, 0), scrip_text, font=scrip_font)
        scw = sc_bbox[2] - sc_bbox[0]
        draw.text(((w - scw) // 2, div_y + (60 if aspect != "twitter" else 52)), scrip_text, fill=(209, 213, 219, 220), font=scrip_font)

    # Footer Branding & Platform standard badge
    footer_font = get_font("segoeui.ttf", 18)
    footer_text = f"DAILY GOSPEL DIGEST  •  FORMATTED FOR {platform_label.upper()}"
    f_bbox = draw.textbbox((0, 0), footer_text, font=footer_font)
    fw = f_bbox[2] - f_bbox[0]
    footer_y = h - (65 if aspect != "story" else 120)
    draw.text(((w - fw) // 2, footer_y), footer_text, fill=(156, 163, 175, 180), font=footer_font)

    # Convert to RGB and save
    final_img = base.convert("RGB")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    final_img.save(str(output_path), quality=95)
    print(f"[GENERATED] {output_path.name} ({w}x{h} for {platform_label})")
    return output_path

def generate_daily_flier_suite(output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    
    fliers_metadata = [
        {
            "filename": "flier_instagram_facebook_square.jpg",
            "topic": "Spiritual Resilience & Alignment",
            "quote": "What is birthed in the secret place cannot be extinguished by public storms.",
            "speaker": "Dunsin Oyekan & Theophilus Sunday",
            "scripture": "Matthew 6:6  •  Psalm 91:1-2",
            "aspect": "square",
            "platform_label": "Instagram & Facebook Feed"
        },
        {
            "filename": "flier_whatsapp_status_story.jpg",
            "topic": "Praise as a Weapon",
            "quote": "Praise is not an emotional reaction to good news. It is your strategic weapon to enforce victory.",
            "speaker": "Moses Bliss (The Mercy Experience)",
            "scripture": "Acts 16:25-26  •  2 Chronicles 20:22",
            "aspect": "story",
            "platform_label": "WhatsApp Status & Stories"
        },
        {
            "filename": "flier_twitter_landscape.jpg",
            "topic": "Kingdom Authority & Surrender",
            "quote": "God does not entrust spiritual authority to unyielded vessels. Your alignment always matters more than your ambition.",
            "speaker": "Apostle Joshua Selman (Koinonia)",
            "scripture": "James 4:7  •  Proverbs 3:5-6",
            "aspect": "twitter",
            "platform_label": "Twitter / X Feed"
        },
        {
            "filename": "flier_threads_square.jpg",
            "topic": "Faith & Inner Rest",
            "quote": "You cannot pour from a cup that has run dry. True strength begins when you rest in His finished work.",
            "speaker": "Elevation Worship (Tiffany Hudson)",
            "scripture": "Isaiah 40:31  •  Hebrews 4:9-11",
            "aspect": "square",
            "platform_label": "Threads & Reels"
        }
    ]

    generated_paths = []
    for meta in fliers_metadata:
        path = output_dir / meta["filename"]
        create_flier(
            output_path=path,
            topic=meta["topic"],
            quote=meta["quote"],
            speaker=meta["speaker"],
            scripture=meta["scripture"],
            aspect=meta["aspect"],
            platform_label=meta["platform_label"]
        )
        generated_paths.append(path)
        
    return generated_paths

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate gospel social fliers.")
    parser.add_argument("--outdir", default="C:/Users/ezeki/.gemini/antigravity/scratch/gospel-content-automation/reports/fliers")
    args = parser.parse_args()
    
    suite = generate_daily_flier_suite(Path(args.outdir))
    print(f"Total fliers generated: {len(suite)}")
