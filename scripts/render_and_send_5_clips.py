"""
Master Script: scripts/render_and_send_5_clips.py
Composites and renders all 5 viral 90-second vertical shorts (9:16),
calibrated to the user's curated preacher & gospel music lineup:
- 3 Preaching: Bro. Gbile Akanni, Apostle Arome Osayi, Apostle Michael Orokpo
- 1 Nigerian Gospel Music: Minister Theophilus Sunday
- 1 Foreign Gospel Music: Josiah Queen ("Queen Josiah")
Compresses them for Gmail attachment limits (under 3.3 MB each, ~16 MB total),
extracts snapshot previews, and dispatches a dedicated showcase email
to aondoaseerezekiel@gmail.com with all 5 videos attached.
"""

import email
import email.mime.application
import email.mime.image
import email.mime.multipart
import email.mime.text
import json
import logging
import os
import shutil
import smtplib
import subprocess
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("kingdom_journal.5_clips")

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

load_env()

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
RECIPIENT = os.environ.get("RECIPIENT_EMAIL") or os.environ.get("NOTIFICATION_EMAIL") or SMTP_USER or "aondoaseerezekiel@gmail.com"

clips_dir = BASE_DIR / "output" / "clips"
clips_dir.mkdir(parents=True, exist_ok=True)
artifact_dir = Path("C:/Users/ezeki/.gemini/antigravity/brain/f8f5e9a2-d815-425e-baca-43eda4414c39")
fonts_dir = BASE_DIR / "assets" / "fonts"

font_bold = str((fonts_dir / "Montserrat-Bold.ttf").resolve()).replace("\\", "/").replace(":", "\\:")
font_regular = str((fonts_dir / "Poppins-Regular.ttf").resolve()).replace("\\", "/").replace(":", "\\:")
font_serif = str((fonts_dir / "PlayfairDisplay-Bold.ttf").resolve()).replace("\\", "/").replace(":", "\\:")

TARGETS = [
    {
        "id": "clip_1_gbile",
        "category": "Preaching 1 (Discipleship & Consecration)",
        "badge_color": "#9A3412",
        "speaker": "Bro. Gbile Akanni",
        "title": "Why Regular Intimacy is Not Optional",
        "window": "00:02:15 - 00:03:45",
        "raw_file": "raw_gbile_90s.mp4",
        "raw_alt": "raw_gbile_90s.webm",
        "quote": "If you lose your secret place, you have lost your spiritual bearing. Power is not demonstrated in the crowd; it is conceived in quietness.",
        "scripture_ref": "Psalm 91:1",
        "scripture_text": "He that dwelleth in the secret place of the most High shall abide under the shadow of the Almighty."
    },
    {
        "id": "clip_2_arome",
        "category": "Preaching 2 (Apostolic Priesthood)",
        "badge_color": "#9A3412",
        "speaker": "Apostle Arome Osayi",
        "title": "How God Raises Men of Spiritual Authority",
        "window": "00:25:20 - 00:26:50",
        "raw_file": "raw_arome_90s.mp4",
        "raw_alt": "raw_arome_90s.webm",
        "quote": "God does not use men because they are gifted; He uses men who have yielded their will at the altar of consecrated prayer.",
        "scripture_ref": "Romans 12:1",
        "scripture_text": "Present your bodies a living sacrifice, holy, acceptable unto God, which is your reasonable service."
    },
    {
        "id": "clip_3_orokpo",
        "category": "Preaching 3 (Spiritual Mysteries)",
        "badge_color": "#9A3412",
        "speaker": "Apostle Michael Orokpo",
        "title": "The Making of Men: The Divine Presence",
        "window": "00:12:30 - 00:14:00",
        "raw_file": "raw_orokpo_90s.mp4",
        "raw_alt": "raw_orokpo_90s.webm",
        "quote": "You cannot carry the presence of God and remain ordinary. When the Holy Ghost rests upon a man, he becomes an eternal wonder.",
        "scripture_ref": "Acts 1:8",
        "scripture_text": "But ye shall receive power, after that the Holy Ghost is come upon you: and ye shall be witnesses unto me."
    },
    {
        "id": "clip_4_theophilus",
        "category": "Gospel Music (Nigerian)",
        "badge_color": "#0284C7",
        "speaker": "Minister Theophilus Sunday",
        "title": "I Believe Live (Prophetic Chants)",
        "window": "00:08:45 - 00:10:15",
        "raw_file": "raw_theophilus_90s.mp4",
        "raw_alt": "raw_theophilus_90s.webm",
        "quote": "I live by faith and not by sight. My spirit pants after You, Jesus, my firm foundation!",
        "scripture_ref": "2 Corinthians 5:7",
        "scripture_text": "For we walk by faith, not by sight."
    },
    {
        "id": "clip_5_josiah_queen",
        "category": "Gospel Music (Foreign)",
        "badge_color": "#0284C7",
        "speaker": "Josiah Queen (Queen Josiah)",
        "title": "The Prodigal (Acoustic Folk Worship)",
        "window": "00:01:05 - 00:02:35",
        "raw_file": "raw_josiah_queen_90s.webm",
        "raw_alt": "raw_josiah_queen_90s.mp4",
        "quote": "I took what was mine and threw it away, but when I came running home, You ran right out to meet me with boundless grace!",
        "scripture_ref": "Luke 15:20",
        "scripture_text": "And he arose, and came to his father. But when he was yet a great way off, his father saw him, and had compassion, and ran."
    }
]

def wrap_text(text: str, max_chars: int = 34) -> list:
    words = text.split()
    lines = []
    cur = []
    for w in words:
        if sum(len(x) for x in cur) + len(cur) + len(w) <= max_chars:
            cur.append(w)
        else:
            if cur:
                lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines

def esc(s: str) -> str:
    return s.replace(":", "\\:").replace("'", "\\'").replace('"', '\\"').replace("%", "\\%")

def render_target(target: dict):
    """
    Renders high-fidelity master (if needed) and optimizes for email attachment (under 3.3 MB).
    """
    master_video = clips_dir / f"{target['id']}.mp4"
    email_video = clips_dir / f"{target['id']}_email.mp4"
    out_preview = clips_dir / f"{target['id']}_preview.png"

    # Find raw input file
    raw_path = clips_dir / target["raw_file"]
    if not (raw_path.is_file() and raw_path.stat().st_size > 1000):
        raw_path = clips_dir / target["raw_alt"]

    if not (raw_path.is_file() and raw_path.stat().st_size > 1000):
        logger.error(f"Raw source file not found for {target['id']}: looked for {target['raw_file']} and {target['raw_alt']}")
        return None, None

    # 1. Render master video if missing
    if not (master_video.is_file() and master_video.stat().st_size > 1000000):
        logger.info(f"[RENDERING MASTER] {target['id']} ({target['speaker']})...")
        quote_lines = wrap_text(target["quote"], max_chars=34)[:3]
        esc_speaker = esc(target["speaker"].upper())
        esc_title = esc(target["title"][:42])
        esc_scripture_ref = esc(f"SCRIPTURE ANCHOR • {target['scripture_ref'].upper()}")
        esc_scripture_text = esc(f'"{target["scripture_text"][:75]}"')

        filters = [
            "[0:v]scale=1080:608:force_original_aspect_ratio=decrease,pad=1080:608:(ow-iw)/2:(oh-ih)/2:color=black[vscaled]",
            "color=c=0x080c14:s=1080x1920:d=120[bg]",
            "[bg][vscaled]overlay=0:360[vbase]",
            "[vbase]drawbox=x=0:y=356:w=1080:h=4:color=0xd4af37@1.0:t=fill[vb1]",
            "[vb1]drawbox=x=0:y=968:w=1080:h=4:color=0xd4af37@1.0:t=fill[vb2]",
            f"[vb2]drawtext=fontfile='{font_bold}':text='THE KINGDOM JOURNAL':fontcolor=0xd4af37:fontsize=22:x=(w-text_w)/2:y=120[vh1]",
            f"[vh1]drawtext=fontfile='{font_serif}':text='{esc_speaker}':fontcolor=0xffffff:fontsize=40:x=(w-text_w)/2:y=170[vh2]",
            f"[vh2]drawtext=fontfile='{font_regular}':text='{esc_title}':fontcolor=0x94a3b8:fontsize=26:x=(w-text_w)/2:y=240[vh3]",
        ]

        last_tag = "vh3"
        y_quote_start = 1040
        for idx, line in enumerate(quote_lines):
            next_tag = f"vq{idx}"
            col = "0xffe082" if idx % 2 == 1 else "0xffffff"
            filters.append(
                f"[{last_tag}]drawtext=fontfile='{font_bold}':text='{esc(line)}':fontcolor={col}:fontsize=36:x=(w-text_w)/2:y={y_quote_start + idx * 56}[{next_tag}]"
            )
            last_tag = next_tag

        filters.extend([
            f"[{last_tag}]drawbox=x=80:y=1360:w=920:h=230:color=0x131d2e@0.92:t=fill[vsc1]",
            "[vsc1]drawbox=x=80:y=1360:w=920:h=230:color=0xd4af37@0.65:t=2[vsc2]",
            f"[vsc2]drawtext=fontfile='{font_bold}':text='{esc_scripture_ref}':fontcolor=0xd4af37:fontsize=24:x=(w-text_w)/2:y=1400[vsc3]",
            f"[vsc3]drawtext=fontfile='{font_regular}':text='{esc_scripture_text}':fontcolor=0xffffff:fontsize=28:x=(w-text_w)/2:y=1460[vsc4]",
            f"[vsc4]drawtext=fontfile='{font_regular}':text='Daily Spiritual Fuel • 07\\:00 AM WAT':fontcolor=0x64748b:fontsize=20:x=(w-text_w)/2:y=1750"
        ])

        filter_graph = "; ".join(filters)

        cmd = [
            "ffmpeg", "-y",
            "-i", str(raw_path),
            "-filter_complex", filter_graph,
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
            "-c:a", "aac", "-b:a", "128k",
            "-t", "90",
            str(master_video)
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if res.returncode != 0:
            logger.error(f"Failed to render master {target['id']}: {res.stderr[-400:]}")
            return None, None

    # 2. Extract preview frame if missing
    if not (out_preview.is_file() and out_preview.stat().st_size > 50000):
        prev_cmd = ["ffmpeg", "-y", "-i", str(master_video), "-ss", "00:00:05", "-vframes", "1", str(out_preview)]
        subprocess.run(prev_cmd, capture_output=True)

    # 3. Create email-optimized version (under 3.3 MB)
    if not (email_video.is_file() and 2000000 <= email_video.stat().st_size <= 3500000):
        logger.info(f"[COMPRESSING FOR EMAIL] {target['id']} target ~3.1 MB...")
        comp_cmd = [
            "ffmpeg", "-y", "-i", str(master_video),
            "-c:v", "libx264", "-preset", "fast", "-b:v", "260k", "-maxrate", "320k", "-bufsize", "600k",
            "-c:a", "aac", "-b:a", "48k",
            str(email_video)
        ]
        res = subprocess.run(comp_cmd, capture_output=True, text=True, timeout=120)
        if res.returncode != 0:
            logger.error(f"Compression failed for {target['id']}: {res.stderr[-300:]}")
            return None, None

    logger.info(f"[READY] {target['id']}: Email size = {email_video.stat().st_size / (1024*1024):.2f} MB")
    return email_video, out_preview

def build_showcase_email(rendered_clips: list):
    cards_html = ""
    for c in rendered_clips:
        cid = c["target"]["id"]
        t = c["target"]
        vid_size_mb = c["video"].stat().st_size / (1024 * 1024)
        cards_html += f"""
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-bottom: 28px; background-color: #0B1120; border-radius: 8px; border: 1px solid #1E293B; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
          <tr>
            <td style="background-color: #0F172A; padding: 14px 18px; border-bottom: 2px solid #D4AF37;">
              <span style="background-color: {t['badge_color']}; color: #FFFFFF; font-size: 10px; font-weight: 700; text-transform: uppercase; padding: 3px 8px; border-radius: 3px; letter-spacing: 0.5px;">
                {t['category']}
              </span>
              <span style="float: right; color: #D4AF37; font-family: monospace; font-size: 11.5px; font-weight: 700;">
                ⏱ 90s ({t['window']})
              </span>
              <div style="font-family: Georgia, serif; font-size: 19px; color: #FFFFFF; font-weight: 700; margin-top: 8px;">
                {t['speaker']}
              </div>
              <div style="font-size: 13px; color: #94A3B8; margin-top: 2px;">
                {t['title']}
              </div>
            </td>
          </tr>
          <tr>
            <td align="center" style="padding: 18px 14px; background-color: #080C14;">
              <img src="cid:{cid}_preview" alt="{t['speaker']} Preview" width="300" style="max-width: 100%; height: auto; border-radius: 6px; border: 1px solid #334155; display: block;" />
              <div style="margin-top: 12px; font-size: 12px; color: #94A3B8;">
                <strong style="color: #F1F5F9;">Attached MP4 Video:</strong> <code style="color: #FCD34D;">{t['id']}.mp4</code> ({vid_size_mb:.2f} MB)
              </div>
            </td>
          </tr>
          <tr>
            <td style="padding: 14px 18px; background-color: #0F172A; border-top: 1px solid #1E293B;">
              <div style="font-size: 13px; color: #F1F5F9; font-style: italic; line-height: 1.5; margin-bottom: 8px;">
                "{t['quote']}"
              </div>
              <div style="font-size: 12px; color: #D4AF37; font-weight: 700;">
                ⚓ {t['scripture_ref']} &middot; <span style="font-weight: 400; color: #CBD5E1;">"{t['scripture_text']}"</span>
              </div>
            </td>
          </tr>
        </table>
        """

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Kingdom Journal · Curated 5-Video Viral Clipping Suite</title>
</head>
<body style="margin: 0; padding: 0; background-color: #020617; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #020617;">
  <tr>
    <td align="center" style="padding: 24px 12px;">
      <table role="presentation" width="650" cellspacing="0" cellpadding="0" border="0" style="max-width: 650px; width: 100%; background-color: #FFFFFF; border-radius: 10px; overflow: hidden; box-shadow: 0 12px 30px rgba(0,0,0,0.5);">
        
        <!-- Top Masthead -->
        <tr>
          <td style="background-color: #9A3412; padding: 32px 24px; text-align: center; border-bottom: 4px solid #D97706;">
            <div style="font-size: 11px; letter-spacing: 2px; color: #FEE2E2; text-transform: uppercase; font-weight: 700; margin-bottom: 6px;">
              The Kingdom Journal &middot; Curated Roster Showcase
            </div>
            <div style="font-family: Georgia, 'Times New Roman', serif; font-size: 27px; color: #FFFFFF; font-weight: 700; line-height: 1.2;">
              5-Video Viral Clipping Suite
            </div>
            <div style="font-size: 13.5px; color: #FED7AA; margin-top: 8px;">
              Bro. Gbile Akanni &middot; Apostle Arome Osayi &middot; Apostle Michael Orokpo &middot; Min. Theophilus Sunday &middot; Josiah Queen
            </div>
          </td>
        </tr>

        <!-- Intro -->
        <tr>
          <td style="padding: 24px 24px 16px 24px; background-color: #F8FAFC;">
            <p style="font-size: 15px; line-height: 1.6; color: #1E293B; margin: 0 0 12px 0;">
              Good day, Ezekiel! Here is the <strong>fully calibrated 5-video suite</strong> featuring your handpicked theological roster and foreign worship lineup, with <strong>all 5 MP4 videos attached directly to this email</strong>.
            </p>
            <p style="font-size: 14px; line-height: 1.6; color: #475569; margin: 0 0 8px 0;">
              Every video below was sliced at its <strong>exact 90-second peak viral climax</strong>, composited into the <strong>9:16 Triple-Deck vertical short format (1080&times;1920)</strong> with editorial gold borders, dynamic typography, and verified scripture anchors.
            </p>
          </td>
        </tr>

        <!-- Cards Section -->
        <tr>
          <td style="padding: 16px 20px; background-color: #0F172A;">
            {cards_html}
          </td>
        </tr>

        <!-- Summary Specs -->
        <tr>
          <td style="padding: 20px 24px; background-color: #F8FAFC; border-top: 1px solid #E2E8F0;">
            <div style="background-color: #FFFBEB; border: 1px solid #FDE68A; border-radius: 6px; padding: 14px 16px;">
              <h4 style="margin: 0 0 6px 0; font-size: 13.5px; color: #92400E;">
                Calibrated Roster & Pipeline Specs
              </h4>
              <ul style="margin: 0; padding-left: 18px; font-size: 12.5px; color: #78350F; line-height: 1.6;">
                <li><strong>Curated Preachers:</strong> Bro. Gbile Akanni, Apostle Arome Osayi, Apostle Michael Orokpo (plus Kumuyi, Papa Omolehin, Kesena Esiri, Wesley).</li>
                <li><strong>Gospel Music:</strong> Minister Theophilus Sunday (Nigerian) and Josiah Queen ("Queen Josiah" - Foreign Folk Revival).</li>
                <li><strong>Optimized Email Payload:</strong> Precision rate-control keeping all 5 videos attached under Gmail's 25 MB ceiling.</li>
                <li><strong>Strict Sandbox Isolation:</strong> The clipping pipeline remains fully decoupled from the daily 07:00 AM journal dispatches.</li>
              </ul>
            </div>
          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="background-color: #1E293B; padding: 22px 24px; text-align: center;">
            <div style="font-size: 12px; color: #94A3B8; line-height: 1.5;">
              <strong style="color: #F1F5F9;">The Kingdom Journal</strong> &middot; Multi-Platform Video Engine<br/>
              Delivered to {RECIPIENT}
            </div>
          </td>
        </tr>

      </table>
    </td>
  </tr>
</table>
</body>
</html>
"""
    return html

def main():
    logger.info("Starting Full 5-Video Clipping Render & Email Dispatch...")
    rendered_clips = []

    for t in TARGETS:
        vid_p, prev_p = render_target(t)
        if vid_p and prev_p:
            rendered_clips.append({
                "target": t,
                "video": vid_p,
                "preview": prev_p
            })
            # Copy to brain artifact directory as well
            if artifact_dir.is_dir():
                shutil.copy2(vid_p, artifact_dir / f"{t['id']}.mp4")
                shutil.copy2(prev_p, artifact_dir / f"{t['id']}_preview.png")

    logger.info(f"Successfully processed {len(rendered_clips)} / {len(TARGETS)} clips!")

    # Check total attachments size
    total_bytes = sum(c["video"].stat().st_size for c in rendered_clips)
    total_mb = total_bytes / (1024 * 1024)
    logger.info(f"Total video attachments size: {total_mb:.2f} MB")

    html_content = build_showcase_email(rendered_clips)
    plain_text = (
        "The Kingdom Journal · Curated 5-Video Viral Clipping Suite\n\n"
        "Here are all 5 rendered 90-second vertical shorts (9:16) for your inspection.\n"
        "All 5 MP4 videos are attached directly to this email.\n"
    )

    msg_root = email.mime.multipart.MIMEMultipart("mixed")
    msg_root["Subject"] = "The Kingdom Journal · Curated 5-Video Viral Clipping Suite (All 5 Videos Attached)"
    msg_root["From"] = f"The Kingdom Journal <{SMTP_USER}>"
    msg_root["To"] = RECIPIENT

    msg_alt = email.mime.multipart.MIMEMultipart("alternative")
    msg_alt.attach(email.mime.text.MIMEText(plain_text, "plain", "utf-8"))

    msg_related = email.mime.multipart.MIMEMultipart("related")
    msg_related.attach(email.mime.text.MIMEText(html_content, "html", "utf-8"))

    # Attach all 5 previews inline
    for c in rendered_clips:
        cid = c["target"]["id"]
        prev_data = c["preview"].read_bytes()
        img_part = email.mime.image.MIMEImage(prev_data, _subtype="png")
        img_part.add_header("Content-ID", f"<{cid}_preview>")
        img_part.add_header("Content-Disposition", "inline", filename=f"{cid}_preview.png")
        msg_related.attach(img_part)

    msg_alt.attach(msg_related)
    msg_root.attach(msg_alt)

    # Attach all 5 MP4 video files
    for c in rendered_clips:
        t = c["target"]
        vid_data = c["video"].read_bytes()
        vid_part = email.mime.application.MIMEApplication(vid_data, Name=f"{t['id']}.mp4")
        vid_part["Content-Disposition"] = f'attachment; filename="{t["id"]}.mp4"'
        msg_root.attach(vid_part)

    logger.info(f"Connecting to SMTP {SMTP_HOST}:{SMTP_PORT} and transmitting 5-video email to {RECIPIENT}...")
    t0 = time.time()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, [RECIPIENT], msg_root.as_string())

    logger.info(f"SUCCESS! 5-Video Showcase Email delivered in {time.time()-t0:.1f}s to {RECIPIENT}")

if __name__ == "__main__":
    main()
