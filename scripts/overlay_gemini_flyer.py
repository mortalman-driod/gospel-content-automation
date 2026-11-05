"""
Overlay typography on top of Gemini AI-generated artwork
to produce viral, high-conversion social media flyers.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import textwrap

def get_font(font_name="segoeuib.ttf", size=32):
    fonts_dir = Path("C:/Windows/Fonts")
    font_path = fonts_dir / font_name
    if not font_path.is_file():
        font_path = fonts_dir / "arialbd.ttf"
    if font_path.is_file():
        return ImageFont.truetype(str(font_path), size)
    return ImageFont.load_default()

def create_gemini_viral_flyer(
    src_img_path: Path,
    out_img_path: Path,
    headline: str,
    quote: str,
    speaker: str,
    scripture: str,
    target_size=(1080, 1080), # (w, h)
    platform_name="Instagram & Facebook"
):
    base_img = Image.open(src_img_path).convert("RGBA")
    w, h = target_size
    
    # Crop / fit background to target size
    src_w, src_h = base_img.size
    aspect_src = src_w / src_h
    aspect_target = w / h
    
    if aspect_src > aspect_target:
        new_w = int(src_h * aspect_target)
        offset_x = (src_w - new_w) // 2
        cropped = base_img.crop((offset_x, 0, offset_x + new_w, src_h))
    else:
        new_h = int(src_w / aspect_target)
        offset_y = (src_h - new_h) // 2
        cropped = base_img.crop((0, offset_y, src_w, offset_y + new_h))
        
    resized = cropped.resize((w, h), Image.Resampling.LANCZOS)
    
    # Create dark gradient overlay for text readability at the bottom and top
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)
    
    # Top subtle dark gradient
    for y in range(int(h * 0.22)):
        alpha = int(140 * (1 - (y / (h * 0.22))))
        draw_ov.line([(0, y), (w, y)], fill=(10, 15, 30, alpha))
        
    # Bottom heavy dark gradient for typography
    bottom_start = int(h * 0.45)
    for y in range(bottom_start, h):
        progress = (y - bottom_start) / (h - bottom_start)
        alpha = int(240 * progress)
        draw_ov.line([(0, y), (w, y)], fill=(8, 12, 24, alpha))
        
    final_canvas = Image.alpha_composite(resized, overlay)
    draw = ImageDraw.Draw(final_canvas)
    
    # Golden outer border
    margin = 30
    draw.rectangle(
        [(margin, margin), (w - margin, h - margin)],
        outline=(245, 158, 11, 140),
        width=2
    )
    
    # Top Tag
    tag_font = get_font("segoeuib.ttf", 22)
    tag_text = f"✨  {headline.upper()}  ✨"
    tbbox = draw.textbbox((0, 0), tag_text, font=tag_font)
    tw = tbbox[2] - tbbox[0]
    
    tag_y = 65 if h <= 1200 else 120
    px1 = (w - tw) // 2 - 20
    py1 = tag_y
    px2 = px1 + tw + 40
    py2 = py1 + 36
    draw.rounded_rectangle([(px1, py1), (px2, py2)], radius=18, fill=(15, 23, 42, 200), outline=(245, 158, 11, 220), width=1)
    draw.text((px1 + 20, py1 + 6), tag_text, fill=(251, 191, 36, 255), font=tag_font)
    
    # Quote Text
    quote_font_size = 46 if h >= 1080 else 36
    quote_font = get_font("georgiab.ttf", quote_font_size)
    wrap_chars = 24 if w <= 1080 else 30
    lines = textwrap.wrap(quote, width=wrap_chars)
    line_h = quote_font_size + 16
    
    start_y = int(h * 0.58) if h >= 1080 else int(h * 0.50)
    for i, line in enumerate(lines):
        lbbox = draw.textbbox((0, 0), line, font=quote_font)
        lw = lbbox[2] - lbbox[0]
        lx = (w - lw) // 2
        ly = start_y + (i * line_h)
        # Glow / drop shadow
        draw.text((lx + 2, ly + 2), line, fill=(0, 0, 0, 240), font=quote_font)
        draw.text((lx, ly), line, fill=(255, 255, 255, 255), font=quote_font)
        
    # Gold separator
    sep_y = start_y + (len(lines) * line_h) + 20
    draw.line([((w - 140) // 2, sep_y), ((w + 140) // 2, sep_y)], fill=(245, 158, 11, 240), width=3)
    
    # Speaker
    spk_font = get_font("segoeuib.ttf", 26 if h >= 1080 else 22)
    spk_text = f"— {speaker.upper()} —"
    sbbox = draw.textbbox((0, 0), spk_text, font=spk_font)
    draw.text(((w - (sbbox[2] - sbbox[0])) // 2, sep_y + 18), spk_text, fill=(253, 230, 138, 255), font=spk_font)
    
    # Scripture
    if scripture:
        scr_font = get_font("segoeui.ttf", 20 if h >= 1080 else 18)
        sc_bbox = draw.textbbox((0, 0), scripture, font=scr_font)
        draw.text(((w - (sc_bbox[2] - sc_bbox[0])) // 2, sep_y + 54), scripture, fill=(203, 213, 225, 240), font=scr_font)
        
    # Footer
    ftr_font = get_font("segoeui.ttf", 16)
    ftr_text = f"GOOGLE GEMINI AI VISUAL  •  {platform_name.upper()} EDITION"
    fbbox = draw.textbbox((0, 0), ftr_text, font=ftr_font)
    draw.text(((w - (fbbox[2] - fbbox[0])) // 2, h - 55), ftr_text, fill=(148, 163, 184, 200), font=ftr_font)
    
    final_canvas.convert("RGB").save(str(out_img_path), quality=95)
    print(f"[CREATED] {out_img_path.name} ({w}x{h})")

if __name__ == "__main__":
    src = Path("C:/Users/ezeki/.gemini/antigravity/scratch/gospel-content-automation/reports/fliers/gemini_gospel_flyer.jpg")
    out_dir = Path("C:/Users/ezeki/.gemini/antigravity/scratch/gospel-content-automation/reports/fliers")
    
    # 1. Instagram / Facebook Square (1080x1080)
    create_gemini_viral_flyer(
        src_img_path=src,
        out_img_path=out_dir / "gemini_flyer_square.jpg",
        headline="Daily Gospel Inspiration",
        quote="What is birthed in the secret place cannot be extinguished by public storms.",
        speaker="Apostle Joshua Selman • Dunsin Oyekan",
        scripture="Psalm 91:1  •  Matthew 6:6",
        target_size=(1080, 1080),
        platform_name="Instagram & Facebook Feed"
    )
    
    # 2. WhatsApp Status & Stories (1080x1920)
    create_gemini_viral_flyer(
        src_img_path=src,
        out_img_path=out_dir / "gemini_flyer_story.jpg",
        headline="Morning Revival Word",
        quote="What is birthed in the secret place cannot be extinguished by public storms.",
        speaker="Apostle Joshua Selman • Dunsin Oyekan",
        scripture="Psalm 91:1  •  Matthew 6:6",
        target_size=(1080, 1920),
        platform_name="WhatsApp Status & Stories"
    )
    
    # 3. Twitter / X Landscape (1200x675)
    create_gemini_viral_flyer(
        src_img_path=src,
        out_img_path=out_dir / "gemini_flyer_twitter.jpg",
        headline="Spiritual Alignment",
        quote="What is birthed in the secret place cannot be extinguished by public storms.",
        speaker="Apostle Joshua Selman • Dunsin Oyekan",
        scripture="Psalm 91:1",
        target_size=(1200, 675),
        platform_name="Twitter / X Feed"
    )
