"""
Milestone 5: Institutional Delivery Engine (src/deliver.py)
Constructs responsive, audited HTML email briefings with:
1. Hidden preheader & plain text alternative.
2. Progressive JPEG optimized inline 4:5 primary flyer (< 180 KB payload).
3. Outlook MSO-compliant hybrid tables (banning unsupported Flexbox in email body).
4. WCAG AAA/AA verified Editorial Print Broadsheet palette on warm archival paper.
5. Transparent editorial provenance & understated speaker citations.
6. Genuine working share intents (X, Threads, WhatsApp) with zero fake buttons or emojis.
"""

import email
import email.mime.application
import email.mime.image
import email.mime.multipart
import email.mime.text
import io
import json
import logging
import os
import re
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

def optimize_email_asset(pil_img: Image.Image, max_kb: int = 180) -> bytes:
    """
    Compresses poster render to a progressive JPEG under max_kb for rapid email loading.
    Eliminates multi-megabyte payloads that cause Gmail message clipping.
    """
    rgb_img = pil_img.convert("RGB")
    quality = 85
    buf = io.BytesIO()
    rgb_img.save(buf, format="JPEG", quality=quality, optimize=True, progressive=True)
    
    while len(buf.getvalue()) > (max_kb * 1024) and quality > 40:
        quality -= 5
        buf = io.BytesIO()
        rgb_img.save(buf, format="JPEG", quality=quality, optimize=True, progressive=True)
        
    return buf.getvalue()

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
        """
        Constructs a classic Light Editorial Print Magazine email briefing
        (Monocle / Kinfolk / New Yorker aesthetic): warm archival cream canvas,
        crisp alabaster reading sheet, deep ink typography, hairline rules,
        zero SaaS card boxes, zero developer prompts, and zero decorative emojis.
        """
        theme = package.get("theme", "The Kingdom Journal")
        hook = package.get("hook", "Daily Kingdom Dispatch")
        scripture = package.get("scripture", {})
        reflection = package.get("reflection", "")

        fb_post = package.get("facebook_post", "")
        ig_caption = package.get("instagram_caption", "")
        x_post = package.get("x_post", "")
        threads_post = package.get("threads_post", "")
        whatsapp_status = package.get("whatsapp_status", "")
        story_text = package.get("story_text", "")
        altar_invite = package.get("altar_invite", "")

        today_str = datetime.now().strftime("%B %d, %Y").upper()

        # Format editorial essay into balanced magazine paragraphs with classic small-caps lead-in
        def format_essay_html(text: str) -> str:
            paragraphs = [p.strip() for p in text.strip().split("\n\n") if p.strip()]
            if len(paragraphs) == 1:
                # Split dense single-block essay into breathable editorial paragraphs on sentence boundaries
                sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+|(?<=[.!?]["\u201d\'])\s+', paragraphs[0]) if s.strip()]
                if len(sentences) >= 5:
                    mid = len(sentences) // 2
                    p1 = " ".join(sentences[:mid])
                    p2 = " ".join(sentences[mid:])
                    paragraphs = [p1, p2]
                elif len(sentences) == 4:
                    paragraphs = [" ".join(sentences[:2]), " ".join(sentences[2:])]

            out = []
            for idx, p in enumerate(paragraphs):
                if idx == 0:
                    words = p.split(" ", 3)
                    if len(words) >= 4:
                        lead = " ".join(words[:3])
                        rest = words[3]
                        formatted_p = (
                            f'<span style="font-variant: small-caps; font-weight: 700; '
                            f'letter-spacing: 0.6px; color: #1C1917;">{lead}</span> {rest}'
                        )
                    else:
                        formatted_p = p
                else:
                    formatted_p = p
                margin_bot = "18px" if idx < len(paragraphs) - 1 else "0"
                out.append(f'<p style="margin: 0 0 {margin_bot} 0; line-height: 1.82; color: #292524;">{formatted_p.replace(chr(10), "<br>")}</p>')
            return "".join(out)

        # Format clean paragraphs for social ledger items
        def to_ledger_paragraphs(text: str) -> str:
            paragraphs = [p.strip() for p in text.strip().split("\n\n") if p.strip()]
            if not paragraphs:
                return f'<p style="margin: 0; line-height: 1.65;">{text.replace(chr(10), "<br>")}</p>'
            out = []
            for idx, p in enumerate(paragraphs):
                margin_bot = "12px" if idx < len(paragraphs) - 1 else "0"
                out.append(f'<p style="margin: 0 0 {margin_bot} 0; line-height: 1.65;">{p.replace(chr(10), "<br>")}</p>')
            return "".join(out)

        essay_html = format_essay_html(reflection)
        fb_html = to_ledger_paragraphs(fb_post)
        ig_html = to_ledger_paragraphs(ig_caption)
        wa_html = to_ledger_paragraphs(whatsapp_status)

        # URL encoded share intents
        x_text = x_post[:280] if len(x_post) > 280 else x_post
        threads_text = threads_post[:490] if len(threads_post) > 490 else threads_post
        x_intent = f"https://twitter.com/intent/tweet?text={urllib.parse.quote(x_text)}"
        threads_intent = f"https://threads.com/intent/post?text={urllib.parse.quote(threads_text)}"
        wa_intent = f"https://api.whatsapp.com/send?text={urllib.parse.quote(whatsapp_status)}"

        # Clean Editorial Provenance Citation
        if verified_meta and verified_meta.get("speaker"):
            provenance_html = f"""
            <div style="margin-top: 16px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 13px; color: #57534E; line-height: 1.6;">
                Inspired by <strong>{verified_meta.get('speaker')}</strong> &middot;
                <a href="{verified_meta.get('url')}" target="_blank" style="color: #855A18; text-decoration: underline;">Watch ministration excerpt&nbsp;&nearr;</a>
            </div>
            """
        else:
            provenance_html = """
            <div style="margin-top: 16px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 13px; color: #57534E; font-style: italic;">
                Original editorial meditation &middot; Prepared for private ministry circulation.
            </div>
            """

        # Curated Ministrations Index (Clean Newspaper Reading List, zero telemetry metrics)
        radar_section_html = ""
        if radar_videos:
            radar_items = []
            for idx, v in enumerate(radar_videos[:5], 1):
                radar_items.append(f"""
                <tr>
                    <td valign="top" style="padding: 12px 0; border-bottom: 1px solid #EBE6DC; width: 32px; font-family: Georgia, 'Times New Roman', serif; font-size: 14px; color: #855A18; font-style: italic;">
                        0{idx}.
                    </td>
                    <td valign="top" style="padding: 12px 0; border-bottom: 1px solid #EBE6DC;">
                        <a href="{v.get('url', '#')}" target="_blank" style="font-family: Georgia, 'Times New Roman', serif; font-size: 15px; color: #1C1917; text-decoration: underline; line-height: 1.4; display: inline-block; word-break: break-word;">
                            {v.get('title', '')}
                        </a>
                        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 12px; color: #57534E; margin-top: 3px;">
                            {v.get('channel', '')}
                        </div>
                    </td>
                </tr>
                """)
            radar_section_html = f"""
            <!-- Section IV: Editorial Reading & Listening Index -->
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-top: 40px;">
                <tr>
                    <td colspan="2" style="padding-bottom: 14px; border-bottom: 2px solid #1C1917;">
                        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 10px; letter-spacing: 2.5px; color: #855A18; font-weight: 700; text-transform: uppercase;">
                            IV &middot; NOTABLE MINISTRATIONS
                        </div>
                        <div style="font-family: Georgia, 'Times New Roman', serif; font-size: 19px; color: #1C1917; font-weight: 700; margin-top: 4px;">
                            Sermon &amp; Worship Index
                        </div>
                    </td>
                </tr>
                {''.join(radar_items)}
            </table>
            """

        html = f"""<!DOCTYPE html>
<html lang="en" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<title>The Kingdom Journal &middot; Issue {issue_number}</title>
<!--[if mso]>
<xml>
  <o:OfficeDocumentSettings>
    <o:AllowPNG/>
    <o:PixelsPerInch>96</o:PixelsPerInch>
  </o:OfficeDocumentSettings>
</xml>
<![endif]-->
<style>
  body {{ margin: 0; padding: 0; background-color: #F4F1EA; font-family: Georgia, 'Times New Roman', Times, serif; color: #1C1917; -webkit-font-smoothing: antialiased; width: 100% !important; }}
  table {{ border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt; }}
  img {{ -ms-interpolation-mode: bicubic; display: block; border: 0; outline: none; max-width: 100%; height: auto; }}
  a {{ color: #855A18; }}
  @media only screen and (max-width: 620px) {{
    .outer-pad {{ padding: 14px 8px !important; }}
    .paper-pad {{ padding: 26px 20px !important; }}
    .dateline-text {{ font-size: 9px !important; letter-spacing: 1px !important; }}
    .stack-col {{ display: block !important; width: 100% !important; padding-left: 0 !important; padding-right: 0 !important; border-right: none !important; box-sizing: border-box !important; }}
    .stack-col-divider {{ border-bottom: 1px solid #EBE6DC !important; padding-bottom: 20px !important; margin-bottom: 20px !important; }}
    .masthead-title {{ font-size: 27px !important; }}
    .plate-wrap {{ padding: 12px !important; }}
  }}
</style>
</head>
<body style="margin: 0; padding: 0; background-color: #F4F1EA; color: #1C1917;">

<!-- Hidden Preheader -->
<div style="display: none; max-height: 0px; overflow: hidden; font-size: 1px; line-height: 1px; color: #F4F1EA;">
    Issue {issue_number}: {hook}. Morning meditation, featured artwork plate, and channel dispatches.
</div>

<!-- Outer Archival Desk Wrapper -->
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #F4F1EA; table-layout: fixed;">
  <tr>
    <td class="outer-pad" align="center" style="padding: 32px 12px;">
      <!--[if mso]>
      <table role="presentation" width="640" align="center" cellspacing="0" cellpadding="0" border="0">
      <tr>
      <td>
      <![endif]-->
      <!-- Crisp Print Paper Sheet -->
      <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width: 640px; width: 100%; background-color: #FFFFFF; border: 1px solid #E5E0D5; table-layout: fixed;">
        <tr>
          <td class="paper-pad" style="padding: 44px 42px; word-wrap: break-word; overflow-wrap: break-word;">

            <!-- Dateline Folio Bar (Responsive 2-Cell Broadsheet Header) -->
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="border-top: 1px solid #1C1917; border-bottom: 1px solid #D6D0C4;">
              <tr>
                <td class="dateline-text" align="left" style="padding: 8px 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 10px; font-weight: 700; letter-spacing: 1.8px; color: #57534E; text-transform: uppercase;">
                  ISSUE NO. {issue_number} &middot; {today_str}
                </td>
                <td class="dateline-text" align="right" style="padding: 8px 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 10px; font-weight: 700; letter-spacing: 1.8px; color: #855A18; text-transform: uppercase;">
                  MORNING EDITION
                </td>
              </tr>
            </table>

            <!-- Broadsheet Masthead -->
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="border-bottom: 2px solid #1C1917;">
              <tr>
                <td align="center" style="padding: 30px 0 28px 0;">
                  <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 11px; letter-spacing: 4.5px; color: #855A18; font-weight: 700; text-transform: uppercase;">
                    THE KINGDOM JOURNAL
                  </div>
                  <h1 class="masthead-title" style="margin: 14px 0 10px 0; font-family: Georgia, 'Times New Roman', serif; font-size: 34px; line-height: 1.18; font-weight: 700; color: #1C1917; letter-spacing: -0.5px;">
                    {theme}
                  </h1>
                  <div style="font-family: Georgia, 'Times New Roman', serif; font-size: 16px; line-height: 1.45; color: #57534E; font-style: italic;">
                    {hook}
                  </div>
                </td>
              </tr>
            </table>

            <!-- Section I: Morning Meditation (Unboxed Editorial Essay) -->
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
              <tr>
                <td style="padding: 34px 0 28px 0; border-bottom: 1px solid #E5E0D5;">
                  <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 10px; letter-spacing: 2.5px; color: #855A18; font-weight: 700; text-transform: uppercase; margin-bottom: 18px;">
                    I &middot; MORNING MEDITATION
                  </div>
                  <div style="font-family: Georgia, 'Times New Roman', serif; font-size: 17px; color: #292524;">
                    {essay_html}
                  </div>

                  <!-- Scripture Anchor (Architectural Left-Rule Pull Quote) -->
                  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-top: 26px;">
                    <tr>
                      <td style="border-left: 2px solid #855A18; padding: 4px 0 4px 20px;">
                        <div style="font-family: Georgia, 'Times New Roman', serif; font-size: 16px; line-height: 1.65; color: #1C1917; font-style: italic;">
                          "{scripture.get('text', '')}"
                        </div>
                        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 11px; letter-spacing: 1.5px; color: #57534E; font-weight: 700; text-transform: uppercase; margin-top: 8px;">
                          {scripture.get('ref', '')} &middot; {scripture.get('translation', 'WEB')}
                        </div>
                      </td>
                    </tr>
                  </table>

                  {provenance_html}
                </td>
              </tr>
            </table>

            <!-- Section II: Featured Plate / Print Gallery -->
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
              <tr>
                <td style="padding: 34px 0; border-bottom: 2px solid #1C1917;">
                  <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 10px; letter-spacing: 2.5px; color: #855A18; font-weight: 700; text-transform: uppercase; margin-bottom: 18px;">
                    II &middot; FEATURED ARTWORK PLATE
                  </div>
                  <div class="plate-wrap" align="center" style="background-color: #FAF8F5; padding: 20px; border: 1px solid #EBE6DC;">
                    <img src="cid:flyer_primary_4_5" alt="{theme} Print Plate" style="width: 100%; max-width: 480px; height: auto; display: block; margin: 0 auto;">
                  </div>
                  <div align="center" style="font-family: Georgia, 'Times New Roman', serif; font-size: 13px; color: #57534E; font-style: italic; margin-top: 14px; line-height: 1.5;">
                    Plate {issue_number}.1 &mdash; Full-resolution editions attached: 4:5 Feed, 1:1 Square, and 9:16 Story.
                  </div>
                </td>
              </tr>
            </table>

            <!-- Section III: Copy-Paste Channel Ledger (Box-Free, Emoji-Free) -->
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-top: 34px; table-layout: fixed;">
              <tr>
                <td style="padding-bottom: 16px; border-bottom: 1px solid #D6D0C4;">
                  <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 10px; letter-spacing: 2.5px; color: #855A18; font-weight: 700; text-transform: uppercase;">
                    III &middot; CHANNEL DISPATCHES
                  </div>
                  <div style="font-family: Georgia, 'Times New Roman', serif; font-size: 20px; color: #1C1917; font-weight: 700; margin-top: 4px;">
                    Editorial Copy Ready for Release
                  </div>
                  <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 12px; color: #57534E; font-style: italic; margin-top: 2px;">
                    Tap any passage below to select and copy.
                  </div>
                </td>
              </tr>

              <!-- Facebook Row -->
              <tr>
                <td style="padding: 22px 0; border-bottom: 1px solid #EBE6DC;">
                  <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 11px; letter-spacing: 2px; color: #1C1917; font-weight: 700; text-transform: uppercase; margin-bottom: 10px;">
                    FACEBOOK &middot; LONG-FORM DISPATCH
                  </div>
                  <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 14px; color: #292524; user-select: all; word-wrap: break-word;">
                    {fb_html}
                  </div>
                </td>
              </tr>

              <!-- Instagram Row -->
              <tr>
                <td style="padding: 22px 0; border-bottom: 1px solid #EBE6DC;">
                  <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 11px; letter-spacing: 2px; color: #1C1917; font-weight: 700; text-transform: uppercase; margin-bottom: 10px;">
                    INSTAGRAM &middot; FEED CAPTION
                  </div>
                  <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 14px; color: #292524; user-select: all; word-wrap: break-word;">
                    {ig_html}
                  </div>
                </td>
              </tr>

              <!-- WhatsApp Row -->
              <tr>
                <td style="padding: 22px 0; border-bottom: 1px solid #EBE6DC;">
                  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-bottom: 10px;">
                    <tr>
                      <td align="left" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 11px; letter-spacing: 2px; color: #1C1917; font-weight: 700; text-transform: uppercase;">
                        WHATSAPP &middot; STATUS
                      </td>
                      <td align="right">
                        <a href="{wa_intent}" target="_blank" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 12px; font-weight: 600; color: #855A18; text-decoration: underline;">
                          Open WhatsApp &rarr;
                        </a>
                      </td>
                    </tr>
                  </table>
                  <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 14px; color: #292524; user-select: all; word-wrap: break-word;">
                    {wa_html}
                  </div>
                </td>
              </tr>

              <!-- Two-Column Print Row: X & Threads -->
              <tr>
                <td style="padding: 22px 0; border-bottom: 1px solid #EBE6DC;">
                  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="table-layout: fixed;">
                    <tr>
                      <td class="stack-col stack-col-divider" width="50%" valign="top" style="padding-right: 18px; border-right: 1px solid #EBE6DC;">
                        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-bottom: 8px;">
                          <tr>
                            <td align="left" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 11px; letter-spacing: 2px; color: #1C1917; font-weight: 700;">
                              X &middot; BRIEF
                            </td>
                            <td align="right">
                              <a href="{x_intent}" target="_blank" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 11px; font-weight: 600; color: #855A18; text-decoration: underline;">
                                Post &rarr;
                              </a>
                            </td>
                          </tr>
                        </table>
                        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 13px; line-height: 1.6; color: #292524; user-select: all; word-wrap: break-word;">
                          {x_post}
                        </div>
                      </td>
                      <td class="stack-col" width="50%" valign="top" style="padding-left: 18px;">
                        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-bottom: 8px;">
                          <tr>
                            <td align="left" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 11px; letter-spacing: 2px; color: #1C1917; font-weight: 700;">
                              THREADS &middot; NOTE
                            </td>
                            <td align="right">
                              <a href="{threads_intent}" target="_blank" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 11px; font-weight: 600; color: #855A18; text-decoration: underline;">
                                Share &rarr;
                              </a>
                            </td>
                          </tr>
                        </table>
                        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 13px; line-height: 1.6; color: #292524; user-select: all; word-wrap: break-word;">
                          {threads_post}
                        </div>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>

              <!-- Story Overlay & Altar Invitation -->
              <tr>
                <td style="padding: 20px 0 8px 0;">
                  <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 13px; color: #292524; line-height: 1.6; margin-bottom: 10px;">
                    <span style="font-size: 11px; letter-spacing: 1.5px; color: #57534E; font-weight: 700; text-transform: uppercase;">STORY OVERLAY &mdash;</span>
                    <span style="font-family: Georgia, 'Times New Roman', serif; font-style: italic; color: #1C1917; user-select: all;">"{story_text}"</span>
                  </div>
                  <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 13px; color: #292524; line-height: 1.6;">
                    <span style="font-size: 11px; letter-spacing: 1.5px; color: #57534E; font-weight: 700; text-transform: uppercase;">ALTAR INVITATION &mdash;</span>
                    <span style="font-family: Georgia, 'Times New Roman', serif; font-style: italic; color: #1C1917; user-select: all;">"{altar_invite}"</span>
                  </div>
                </td>
              </tr>
            </table>

            {radar_section_html}

            <!-- Print Publisher Colophon -->
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-top: 42px; border-top: 2px solid #1C1917;">
              <tr>
                <td align="center" style="padding-top: 24px; font-family: Georgia, 'Times New Roman', serif; font-size: 12px; line-height: 1.7; color: #57534E;">
                  <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-weight: 700; color: #1C1917; letter-spacing: 3px; text-transform: uppercase; font-size: 10px; margin-bottom: 6px;">
                    THE KINGDOM JOURNAL &middot; DAILY EDITORIAL DISPATCH
                  </div>
                  Curated from verified ministrations for pastors, leaders, and Christian thinkers.<br>
                  <em>Published in Lagos &amp; London &middot; Private Editorial Circulation</em>
                </td>
              </tr>
            </table>

          </td>
        </tr>
      </table>
      <!--[if mso]>
      </td>
      </tr>
      </table>
      <![endif]-->
    </td>
  </tr>
</table>
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
        Dispatches the complete issue briefing email via SMTP with progressive JPEG inline flyer and attached PNGs.
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
            f"THE KINGDOM JOURNAL · ISSUE {issue_number}\n"
            f"{package.get('theme')}: {package.get('hook')}\n\n"
            f"REFLECTION:\n{package.get('reflection')}\n\n"
            f"FACEBOOK POST:\n{package.get('facebook_post')}\n\n"
            f"WHATSAPP STATUS:\n{package.get('whatsapp_status')}\n\n"
            f"X POST:\n{package.get('x_post')}\n"
        )

        # Save Local Issue Assets Archive
        out_dir = BASE_DIR / "out" / f"issue-{issue_number}"
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "email.html").write_text(html_content, encoding="utf-8")
        (out_dir / "briefing.txt").write_text(plain_text, encoding="utf-8")
        (out_dir / "package.json").write_text(json.dumps(package, indent=2, ensure_ascii=False), encoding="utf-8")

        # Save flyer images
        for key, img in flyer_images.items():
            img.save(out_dir / f"{key}.png", format="PNG")

        logger.info(f"Successfully archived Issue {issue_number} assets to {out_dir}")

        # Handle Dry-Run Output
        if dry_run:
            logger.info(f"[DRY-RUN] Execution completed successfully. Live email dispatch skipped.")
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

        # Attach optimized progressive JPEG inline flyer (< 180 KB)
        if "flyer_primary_4_5" in flyer_images:
            jpeg_bytes = optimize_email_asset(flyer_images["flyer_primary_4_5"], max_kb=180)
            img_part = email.mime.image.MIMEImage(jpeg_bytes, _subtype="jpeg")
            img_part.add_header("Content-ID", "<flyer_primary_4_5>")
            img_part.add_header("Content-Disposition", "inline", filename="flyer_primary_4_5.jpg")
            msg_related.attach(img_part)

        msg_alt.attach(msg_related)
        msg_root.attach(msg_alt)

        # Attach all flyer PNGs as standalone downloads
        for fname, img in flyer_images.items():
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
