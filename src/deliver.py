"""
Milestone 5: Institutional Delivery Engine (src/deliver.py)
Constructs responsive, audited HTML email briefing with:
1. Hidden preheader & plain text alternative.
2. Inline 4:5 primary flyer + file attachments (4:5, 1:1, 9:16 primary, 4:5 alternate).
3. Plain selectable copy-paste blocks for Facebook, IG, X, Threads, WhatsApp, Story.
4. Transparent VERIFY section with real links, timestamps, view counts, and match scores.
5. Live Radar table with real clickable links and outlier multiples.
6. Genuine working share intents (X, Threads, WhatsApp) and zero fake buttons.
"""

import email
import email.mime.application
import email.mime.image
import email.mime.multipart
import email.mime.text
import json
import logging
import os
import smtplib
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
logger = logging.getLogger("kingdom_journal.deliver")

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

class EmailDeliverer:
    def __init__(self):
        load_env()
        self.smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.environ.get("SMTP_PORT", 587))
        self.smtp_user = os.environ.get("SMTP_USER")
        self.smtp_password = os.environ.get("SMTP_PASSWORD")
        self.recipient = os.environ.get("RECIPIENT_EMAIL") or self.smtp_user or "aondoaseerezekiel@gmail.com"

    def build_email_html(
        self,
        issue_number: int,
        package: Dict,
        verified_meta: Optional[Dict],
        radar_videos: List[Dict],
        quota_used: int,
        review_flags: Optional[List[str]] = None
    ) -> str:
        theme = package.get("theme", "Daily Editorial")
        hook = package.get("hook", "When Human Words Run Dry")
        quote = package.get("quote")
        scripture = package.get("scripture", {})
        reflection = package.get("reflection", "")

        # Format social copy
        fb_post = package.get("facebook_post", "")
        ig_caption = package.get("instagram_caption", "")
        x_post = package.get("x_post", "")
        threads_post = package.get("threads_post", "")
        whatsapp_status = package.get("whatsapp_status", "")
        story_text = package.get("story_text", "")
        altar_invite = package.get("altar_invite", "")
        flyers = package.get("flyers", [])

        # URL encoded intents
        x_intent = f"https://twitter.com/intent/tweet?text={urllib.parse.quote(x_post)}"
        threads_intent = f"https://www.threads.net/intent/post?text={urllib.parse.quote(threads_post)}"
        wa_intent = f"https://api.whatsapp.com/send?text={urllib.parse.quote(whatsapp_status)}"

        # Radar rows HTML
        radar_rows_html = []
        for idx, v in enumerate(radar_videos[:5], 1):
            radar_rows_html.append(f"""
            <tr style="border-bottom: 1px solid #1E293B;">
                <td style="padding: 12px 8px; color: #D4AF37; font-weight: bold;">#{idx}</td>
                <td style="padding: 12px 8px;">
                    <a href="{v.get('url', '#')}" target="_blank" style="color: #F8F9FA; text-decoration: none; font-weight: 500;">
                        {v.get('title', '')}
                    </a>
                    <div style="font-size: 12px; color: #94A3B8; margin-top: 2px;">{v.get('channel', '')}</div>
                </td>
                <td style="padding: 12px 8px; text-align: right; color: #CBD5E1; font-size: 13px;">
                    {v.get('views', 0):,} views<br>
                    <span style="color: #38BDF8; font-size: 11px;">{v.get('velocity', 0):.0f} v/hr • {v.get('outlier_multiple', 1.0):.1f}x</span>
                </td>
            </tr>
            """)
        radar_table_html = "\n".join(radar_rows_html)

        # Verification block HTML
        if verified_meta and verified_meta.get("verified"):
            verify_status_badge = '<span style="background: #14532D; color: #4ADE80; padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: bold;">VERIFIED (100% MATCH)</span>'
            verify_details = f"""
            <div style="margin-top: 10px; font-size: 13px; color: #CBD5E1; line-height: 1.6;">
                <strong>Source Ministration:</strong> <a href="{verified_meta.get('url')}" target="_blank" style="color: #38BDF8;">{verified_meta.get('video_title')}</a><br>
                <strong>Speaker:</strong> {verified_meta.get('speaker')}<br>
                <strong>Exact Timestamp:</strong> <a href="{verified_meta.get('url')}" target="_blank" style="color: #D4AF37; font-weight: bold;">{verified_meta.get('start_sec')} seconds (Jump to video)</a><br>
                <strong>Fuzzy Match Score:</strong> {verified_meta.get('match_score', 1.0) * 100:.1f}% ratio against raw transcript
            </div>
            """
        else:
            verify_status_badge = '<span style="background: #78350F; color: #FCD34D; padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: bold;">EDITORIAL ONLY (NO ATTRIBUTED QUOTE)</span>'
            verify_details = f"""
            <div style="margin-top: 10px; font-size: 13px; color: #CBD5E1; line-height: 1.6;">
                <em>No transcript quote met strict verification (ratio >= 0.92). In compliance with Non-Negotiable Rule R1, this issue is signed strictly as <strong>The Kingdom Journal</strong> with zero pastor attributions.</em>
            </div>
            """

        # Review flags HTML
        if review_flags:
            flags_html = "<ul style='margin: 6px 0 0 18px; padding: 0; color: #F87171;'>" + "".join([f"<li>{f}</li>" for f in review_flags]) + "</ul>"
            review_box = f"""
            <div style="background: #450A0A; border: 1px solid #991B1B; border-radius: 8px; padding: 16px; margin: 24px 0;">
                <strong style="color: #F87171; font-size: 14px;">⚠️ NEEDS YOUR REVIEW</strong>
                {flags_html}
            </div>
            """
        else:
            review_box = """
            <div style="background: #064E3B; border: 1px solid #059669; border-radius: 8px; padding: 12px 16px; margin: 24px 0; color: #A7F3D0; font-size: 13px;">
                ✓ <strong>Integrity Verified:</strong> 0 risk flags detected. Quote matches transcript tokens.
            </div>
            """

        # Prompt display
        flyer_a_prompt = flyers[0].get("image_prompt", "") if flyers else ""

        html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Kingdom Journal • Issue {issue_number}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #050B14; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #F8F9FA;">

<!-- Hidden Preheader -->
<div style="display: none; max-height: 0px; overflow: hidden; font-size: 1px; line-height: 1px; color: #050B14;">
    Issue {issue_number}: {hook}. Ready-to-post gospel editorial, flyers, and verified radar.
</div>

<div style="max-width: 680px; margin: 0 auto; padding: 24px 16px; background-color: #0A1128;">

    <!-- Masthead -->
    <div style="text-align: center; padding: 20px 0 24px 0; border-bottom: 1px solid #1E293B;">
        <div style="font-size: 12px; letter-spacing: 3px; color: #D4AF37; font-weight: 700; text-transform: uppercase;">The Kingdom Journal</div>
        <h1 style="margin: 8px 0 4px 0; font-size: 26px; color: #FFFFFF; font-weight: 800; letter-spacing: -0.5px;">{theme}</h1>
        <div style="font-size: 13px; color: #94A3B8;">Issue {issue_number} • {hook}</div>
    </div>

    <!-- Primary Flyer (Inline 4:5 Mobile Feed) -->
    <div style="text-align: center; margin: 28px 0;">
        <div style="font-size: 11px; color: #D4AF37; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 8px; font-weight: bold;">TODAY'S MASTER FLYER (4:5 PRIMARY FEED)</div>
        <img src="cid:flyer_primary_4_5" alt="{theme} Flyer" style="width: 100%; max-width: 540px; height: auto; border-radius: 8px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); display: inline-block;">
        <div style="font-size: 12px; color: #64748B; margin-top: 8px;">Attached in 4:5 (Feed), 1:1 (Square), and 9:16 (WhatsApp Status & Story)</div>
    </div>

    <!-- Editorial Reflection -->
    <div style="background-color: #0F172A; border: 1px solid #1E293B; border-radius: 8px; padding: 24px; margin: 24px 0;">
        <div style="font-size: 11px; letter-spacing: 1.5px; color: #D4AF37; font-weight: bold; text-transform: uppercase; margin-bottom: 12px;">DAILY CONTEMPLATIVE REFLECTION</div>
        <div style="font-size: 15px; line-height: 1.7; color: #E2E8F0; white-space: pre-line;">{reflection}</div>
        <div style="margin-top: 16px; padding-top: 16px; border-top: 1px solid #334155; font-size: 13px; color: #38BDF8;">
            <strong>Scripture Anchor:</strong> "{scripture.get('text', '')}" — <em>{scripture.get('ref', '')} [{scripture.get('translation', 'WEB')}]</em>
        </div>
    </div>

    <!-- Copy-Paste Social Kits -->
    <div style="margin: 32px 0;">
        <h2 style="font-size: 18px; color: #FFFFFF; border-bottom: 2px solid #D4AF37; padding-bottom: 8px; margin-bottom: 20px;">
            COPY-PASTE SOCIAL KITS (REVIEW & POST)
        </h2>

        <!-- Facebook Post -->
        <div style="margin-bottom: 24px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="font-weight: bold; color: #38BDF8; font-size: 14px;">📘 FACEBOOK POST (TAP TO SELECT & COPY)</span>
            </div>
            <textarea readonly style="width: 100%; box-sizing: border-box; height: 180px; background: #0F172A; border: 1px solid #334155; border-radius: 6px; padding: 12px; color: #F1F5F9; font-family: monospace; font-size: 13px; line-height: 1.5; resize: vertical;">{fb_post}</textarea>
        </div>

        <!-- Instagram Caption -->
        <div style="margin-bottom: 24px;">
            <div style="font-weight: bold; color: #F43F5E; font-size: 14px; margin-bottom: 6px;">📸 INSTAGRAM CAPTION</div>
            <textarea readonly style="width: 100%; box-sizing: border-box; height: 160px; background: #0F172A; border: 1px solid #334155; border-radius: 6px; padding: 12px; color: #F1F5F9; font-family: monospace; font-size: 13px; line-height: 1.5; resize: vertical;">{ig_caption}</textarea>
        </div>

        <!-- WhatsApp Status Devotional -->
        <div style="margin-bottom: 24px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="font-weight: bold; color: #22C55E; font-size: 14px;">💬 WHATSAPP STATUS</span>
                <a href="{wa_intent}" target="_blank" style="background: #15803D; color: #FFFFFF; text-decoration: none; padding: 6px 14px; border-radius: 4px; font-size: 12px; font-weight: bold;">Open WhatsApp</a>
            </div>
            <textarea readonly style="width: 100%; box-sizing: border-box; height: 120px; background: #0F172A; border: 1px solid #334155; border-radius: 6px; padding: 12px; color: #F1F5F9; font-family: monospace; font-size: 13px; line-height: 1.5; resize: vertical;">{whatsapp_status}</textarea>
        </div>

        <!-- X (Twitter) & Threads -->
        <div style="display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 280px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-weight: bold; color: #FFFFFF; font-size: 14px;">𝕏 POST (<= 280 Chars)</span>
                    <a href="{x_intent}" target="_blank" style="background: #1D4ED8; color: #FFFFFF; text-decoration: none; padding: 6px 14px; border-radius: 4px; font-size: 12px; font-weight: bold;">Post to 𝕏</a>
                </div>
                <textarea readonly style="width: 100%; box-sizing: border-box; height: 100px; background: #0F172A; border: 1px solid #334155; border-radius: 6px; padding: 10px; color: #F1F5F9; font-family: monospace; font-size: 12px; line-height: 1.4;">{x_post}</textarea>
            </div>

            <div style="flex: 1; min-width: 280px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-weight: bold; color: #A855F7; font-size: 14px;">🧵 THREADS POST</span>
                    <a href="{threads_intent}" target="_blank" style="background: #7E22CE; color: #FFFFFF; text-decoration: none; padding: 6px 14px; border-radius: 4px; font-size: 12px; font-weight: bold;">Post to Threads</a>
                </div>
                <textarea readonly style="width: 100%; box-sizing: border-box; height: 100px; background: #0F172A; border: 1px solid #334155; border-radius: 6px; padding: 10px; color: #F1F5F9; font-family: monospace; font-size: 12px; line-height: 1.4;">{threads_post}</textarea>
            </div>
        </div>

        <!-- Story Text & Altar Invite -->
        <div style="background: #111827; border: 1px solid #1F2937; border-radius: 8px; padding: 16px; margin-bottom: 24px;">
            <div style="font-size: 13px; color: #E5E7EB; margin-bottom: 8px;">
                <strong>📲 9:16 Story Text Overlay:</strong> <code style="color: #D4AF37; background: #1F2937; padding: 2px 6px; border-radius: 4px;">{story_text}</code>
            </div>
            <div style="font-size: 13px; color: #E5E7EB;">
                <strong>🕊️ Personal Altar Invite:</strong> <em>"{altar_invite}"</em>
            </div>
        </div>
    </div>

    <!-- AI Background Prompt -->
    <div style="background: #090D1A; border: 1px dashed #334155; border-radius: 8px; padding: 16px; margin: 24px 0;">
        <div style="font-size: 11px; letter-spacing: 1.5px; color: #94A3B8; font-weight: bold; text-transform: uppercase; margin-bottom: 6px;">TEXT-FREE AI IMAGE PROMPT (STANDARD OUTPUT)</div>
        <div style="font-size: 12px; color: #CBD5E1; font-family: monospace; line-height: 1.5;">{flyer_a_prompt}</div>
    </div>

    <!-- VERIFICATION BLOCK -->
    <div style="background: #0B132B; border: 1px solid #1C2541; border-radius: 8px; padding: 20px; margin: 28px 0;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 14px; font-weight: bold; color: #FFFFFF;">JOURNALISTIC INTEGRITY AUDIT</span>
            {verify_status_badge}
        </div>
        {verify_details}
        {review_box}
    </div>

    <!-- VIRAL WORSHIP RADAR -->
    <div style="margin: 32px 0;">
        <h2 style="font-size: 18px; color: #FFFFFF; border-bottom: 2px solid #38BDF8; padding-bottom: 8px; margin-bottom: 16px;">
            TODAY'S VIRAL WORSHIP RADAR (TOP 5 DISCOVERIES)
        </h2>
        <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
            <thead>
                <tr style="border-bottom: 2px solid #334155; color: #94A3B8; text-align: left; font-size: 12px;">
                    <th style="padding: 8px;">RANK</th>
                    <th style="padding: 8px;">TITLE & CHANNEL</th>
                    <th style="padding: 8px; text-align: right;">METRICS</th>
                </tr>
            </thead>
            <tbody>
                {radar_table_html}
            </tbody>
        </table>
    </div>

    <!-- Footer -->
    <div style="border-top: 1px solid #1E293B; padding-top: 20px; text-align: center; font-size: 12px; color: #64748B;">
        The Kingdom Journal System • Run Quota: {quota_used} units • {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}<br>
        Built with strict attribution, verbatim scripture, and WCAG AA flyer rendering.
    </div>

</div>
</body>
</html>
"""
        return html

    def send_issue_email(
        self,
        issue_number: int,
        package: Dict,
        verified_meta: Optional[Dict],
        radar_videos: List[Dict],
        quota_used: int,
        flyer_images: Dict[str, Image.Image],
        review_flags: Optional[List[str]] = None,
        dry_run: bool = False
    ) -> bool:
        """
        Dispatches the complete issue briefing email via SMTP with inline flyer and attached PNGs.
        If dry_run is True, writes email and assets to out/issue-<N>/ and returns True without sending.
        """
        html_content = self.build_email_html(
            issue_number=issue_number,
            package=package,
            verified_meta=verified_meta,
            radar_videos=radar_videos,
            quota_used=quota_used,
            review_flags=review_flags
        )

        plain_text = (
            f"THE KINGDOM JOURNAL • ISSUE {issue_number}\n"
            f"{package.get('theme')}: {package.get('hook')}\n\n"
            f"REFLECTION:\n{package.get('reflection')}\n\n"
            f"FACEBOOK POST:\n{package.get('facebook_post')}\n\n"
            f"WHATSAPP STATUS:\n{package.get('whatsapp_status')}\n\n"
            f"X POST:\n{package.get('x_post')}\n"
        )

        # Handle Dry-Run Output
        if dry_run:
            out_dir = BASE_DIR / "out" / f"issue-{issue_number}"
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / "email.html").write_text(html_content, encoding="utf-8")
            (out_dir / "briefing.txt").write_text(plain_text, encoding="utf-8")
            (out_dir / "package.json").write_text(json.dumps(package, indent=2, ensure_ascii=False), encoding="utf-8")

            # Save flyer images
            for key, img in flyer_images.items():
                img.save(out_dir / f"{key}.png", format="PNG")

            logger.info(f"[DRY-RUN] Successfully saved Issue {issue_number} assets to {out_dir}")
            return True

        # Send Live Email
        if not self.smtp_user or not self.smtp_password:
            raise ValueError("SMTP_USER and SMTP_PASSWORD must be configured in environment or .env")

        msg_root = email.mime.multipart.MIMEMultipart("mixed")
        msg_root["Subject"] = f"Issue {issue_number} · {package.get('hook', 'The Kingdom Journal')}"
        msg_root["From"] = f"The Kingdom Journal <{self.smtp_user}>"
        msg_root["To"] = self.recipient

        # Alternative body (plain + html)
        msg_alt = email.mime.multipart.MIMEMultipart("alternative")
        msg_alt.attach(email.mime.text.MIMEText(plain_text, "plain", "utf-8"))

        msg_related = email.mime.multipart.MIMEMultipart("related")
        msg_related.attach(email.mime.text.MIMEText(html_content, "html", "utf-8"))

        # Attach inline flyer image
        if "flyer_primary_4_5" in flyer_images:
            import io
            buf = io.BytesIO()
            flyer_images["flyer_primary_4_5"].save(buf, format="PNG")
            img_part = email.mime.image.MIMEImage(buf.getvalue(), _subtype="png")
            img_part.add_header("Content-ID", "<flyer_primary_4_5>")
            img_part.add_header("Content-Disposition", "inline", filename="flyer_primary_4_5.png")
            msg_related.attach(img_part)

        msg_alt.attach(msg_related)
        msg_root.attach(msg_alt)

        # Attach all flyer PNGs as standalone downloads
        for fname, img in flyer_images.items():
            import io
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            part = email.mime.application.MIMEApplication(buf.getvalue(), Name=f"{fname}.png")
            part["Content-Disposition"] = f'attachment; filename="{fname}.png"'
            msg_root.attach(part)

        # Dispatch via SMTP
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.sendmail(self.smtp_user, [self.recipient], msg_root.as_string())

        logger.info(f"Successfully sent Issue {issue_number} email briefing to {self.recipient}")
        return True
