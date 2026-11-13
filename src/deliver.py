import io
import json
import logging
import os
import re
import smtplib
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import email
import email.mime.application
import email.mime.image
import email.mime.multipart
import email.mime.text
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
    """Compresses poster render to a progressive JPEG under max_kb for rapid email loading."""
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
    """Dispatches complete issue briefings formatted in the Warm Terracotta & Burnt Amber edition."""

    def __init__(self):
        load_env()
        self.smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        self.smtp_user = os.environ.get("SMTP_USER")
        self.smtp_password = os.environ.get("SMTP_PASSWORD")
        self.recipient = os.environ.get("NOTIFICATION_EMAIL", "aondoaseerezekiel@gmail.com")

    def build_email_html(
        self,
        issue_number: int,
        package: Dict,
        verified_meta: Optional[Dict],
        radar_videos: List[Dict],
        quota_used: int = 0,
        review_flags: Optional[List[str]] = None
    ) -> str:
        """
        Constructs an unmistakable Warm Terracotta & Burnt Amber email briefing:
        - Rich Terracotta (#9A3412) Masthead Banner with Burnt Amber (#D97706) detail
        - Distinct spiritual theme badge
        - Warm linen studio backdrop (#F6F2ED) & crisp white reading sheet (#FFFFFF)
        - Terracotta pill action buttons for one-click social publishing
        - Burnt amber framed scripture pull quote on warm parchment
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

        today_str = datetime.now().strftime("%B %d, %Y")

        def format_essay_html(text: str) -> str:
            paragraphs = [p.strip() for p in text.strip().split("\n\n") if p.strip()]
            if len(paragraphs) == 1:
                sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+|(?<=[.!?]["\u201d\'])\s+', paragraphs[0]) if s.strip()]
                if len(sentences) >= 5:
                    mid = len(sentences) // 2
                    paragraphs = [" ".join(sentences[:mid]), " ".join(sentences[mid:])]
                elif len(sentences) == 4:
                    paragraphs = [" ".join(sentences[:2]), " ".join(sentences[2:])]

            out = []
            for idx, p in enumerate(paragraphs):
                mb = "16px" if idx < len(paragraphs) - 1 else "0"
                out.append(
                    f'<p style="margin: 0 0 {mb} 0; line-height: 1.75; color: #292524;">'
                    f'{p.replace(chr(10), "<br>")}</p>'
                )
            return "".join(out)

        def to_clean_paragraphs(text: str) -> str:
            paragraphs = [p.strip() for p in text.strip().split("\n\n") if p.strip()]
            if not paragraphs:
                return f'<p style="margin: 0; line-height: 1.62; color: #292524;">{text.replace(chr(10), "<br>")}</p>'
            out = []
            for idx, p in enumerate(paragraphs):
                mb = "11px" if idx < len(paragraphs) - 1 else "0"
                out.append(
                    f'<p style="margin: 0 0 {mb} 0; line-height: 1.62; color: #292524;">'
                    f'{p.replace(chr(10), "<br>")}</p>'
                )
            return "".join(out)

        essay_html = format_essay_html(reflection)
        fb_html = to_clean_paragraphs(fb_post)
        ig_html = to_clean_paragraphs(ig_caption)
        wa_html = to_clean_paragraphs(whatsapp_status)

        # Share intents
        x_text = x_post[:280] if len(x_post) > 280 else x_post
        threads_text = threads_post[:490] if len(threads_post) > 490 else threads_post
        x_intent = f"https://twitter.com/intent/tweet?text={urllib.parse.quote(x_text)}"
        threads_intent = f"https://threads.com/intent/post?text={urllib.parse.quote(threads_text)}"
        wa_intent = f"https://api.whatsapp.com/send?text={urllib.parse.quote(whatsapp_status)}"
        fb_text = fb_post[:400] if len(fb_post) > 400 else fb_post
        fb_intent = f"https://www.facebook.com/sharer/sharer.php?quote={urllib.parse.quote(fb_text)}"

        # Source attribution (clean non-breaking link so arrow never orphans onto next line)
        if verified_meta and verified_meta.get("speaker"):
            provenance_html = f"""
            <div style="margin-top: 16px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 13px; color: #57534E; line-height: 1.55;">
              From <strong style="color: #1C1917;">{verified_meta.get('speaker')}</strong> &middot;
              <a href="{verified_meta.get('url')}" target="_blank" style="color: #9A3412; text-decoration: none; font-weight: 700; white-space: nowrap;">Watch clip &rarr;</a>
            </div>
            """
        else:
            provenance_html = """
            <div style="margin-top: 16px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 13px; color: #57534E;">
              Today's Kingdom Journal morning note
            </div>
            """

        # Worth Watching index
        radar_section_html = ""
        if radar_videos:
            radar_items = []
            for idx, v in enumerate(radar_videos[:5], 1):
                radar_items.append(f"""
                <tr>
                  <td valign="top" style="padding: 11px 0; border-bottom: 1px solid #E7E0D8; width: 26px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 13px; color: #9A3412; font-weight: 700;">
                    {idx}.
                  </td>
                  <td valign="top" style="padding: 11px 0; border-bottom: 1px solid #E7E0D8;">
                    <a href="{v.get('url', '#')}" target="_blank" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 14px; font-weight: 600; color: #1C1917; text-decoration: none; line-height: 1.4; display: inline-block; word-break: break-word;">
                      {v.get('title', '')}
                    </a>
                    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 12px; color: #57534E; margin-top: 2px;">
                      {v.get('channel', '')}
                    </div>
                  </td>
                </tr>
                """)
            radar_section_html = f"""
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-top: 32px;">
              <tr>
                <td colspan="2" style="padding-bottom: 10px; border-bottom: 2px solid #D97706;">
                  <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 15px; color: #9A3412; font-weight: 700;">
                    Worth watching this week
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
  body {{ margin: 0; padding: 0; background-color: #F6F2ED; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1C1917; -webkit-font-smoothing: antialiased; width: 100% !important; }}
  table {{ border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt; }}
  img {{ -ms-interpolation-mode: bicubic; display: block; border: 0; outline: none; max-width: 100%; height: auto; }}
  a {{ color: #9A3412; }}
  @media only screen and (max-width: 620px) {{
    .outer-pad {{ padding: 12px 8px !important; }}
    .sheet-pad {{ padding: 24px 18px !important; }}
    .sheet-table {{ width: 100% !important; max-width: 100% !important; }}
    .stack-col {{ display: block !important; width: 100% !important; padding-left: 0 !important; padding-right: 0 !important; border-right: none !important; box-sizing: border-box !important; }}
    .stack-col-divider {{ border-bottom: 1px solid #E5E7EB !important; padding-bottom: 18px !important; margin-bottom: 18px !important; }}
    .hero-title {{ font-size: 24px !important; }}
  }}
</style>
</head>
<body style="margin: 0; padding: 0; background-color: #F6F2ED; color: #1C1917;">

<!-- Hidden Preheader -->
<div style="display: none; max-height: 0px; overflow: hidden; font-size: 1px; line-height: 1px; color: #F6F2ED;">
  Issue {issue_number}: {hook} &mdash; morning reflection, today's graphics, and channel captions.
</div>

<!-- Outer Studio Canvas -->
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #F6F2ED">
  <tr>
    <td class="outer-pad" align="center" style="padding: 24px 12px;">
      <!--[if mso]>
      <table role="presentation" width="620" align="center" cellspacing="0" cellpadding="0" border="0">
      <tr>
      <td>
      <![endif]-->
      <!-- Warm Terracotta & Burnt Amber Reading Sheet -->
      <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" class="sheet-table" style="max-width: 620px; width: 100%; margin: 0 auto; background-color: #FFFFFF; border: 1px solid #E7E0D8; border-radius: 6px; overflow: hidden;">
        
        <!-- Rich Branded Masthead Banner in Warm Terracotta & Burnt Amber -->
        <tr>
          <td style="background-color: #9A3412; border-bottom: 4px solid #D97706; padding: 22px 28px;">
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
              <tr>
                <td align="left" valign="middle">
                  <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 11px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: #FDE68A;">
                    ✦ THE KINGDOM JOURNAL &middot; DAILY DISPATCH ✦
                  </div>
                  <div style="font-family: Georgia, 'Times New Roman', serif; font-size: 23px; font-weight: 700; color: #FFFFFF; margin-top: 4px; letter-spacing: -0.01em;">
                    Warm Terracotta &amp; Amber Edition
                  </div>
                </td>
                <td align="right" valign="middle" style="white-space: nowrap;">
                  <span style="display: inline-block; background-color: #D97706; color: #FFFFFF; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 11px; font-weight: 700; padding: 4px 11px; border-radius: 999px; text-transform: uppercase; letter-spacing: 0.05em;">
                    Issue {issue_number}
                  </span>
                  <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 11px; color: #FED7AA; margin-top: 5px;">
                    {today_str}
                  </div>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <tr>
          <td class="sheet-pad" style="padding: 34px 36px; word-wrap: break-word; overflow-wrap: break-word;">

            <!-- Editorial Title & Theme Badge -->
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="border-bottom: 1px solid #E7E0D8;">
              <tr>
                <td align="left" style="padding-bottom: 22px;">
                  <div style="margin-bottom: 10px;">
                    <span style="display: inline-block; background-color: #FAF6F1; color: #9A3412; border: 1.5px solid #D97706; padding: 4px 13px; border-radius: 999px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 12px; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase;">
                      ✦ Theme: {theme}
                    </span>
                  </div>
                  <h1 class="hero-title" style="margin: 0; font-family: Georgia, 'Times New Roman', serif; font-size: 28px; line-height: 1.25; font-weight: 700; color: #1C1917;">
                    {hook}
                  </h1>
                </td>
              </tr>
            </table>

            <!-- Morning Reflection -->
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
              <tr>
                <td style="padding: 26px 0; border-bottom: 1px solid #E7E0D8;">
                  <div style="font-family: Georgia, 'Times New Roman', serif; font-size: 16.5px; color: #292524;">
                    {essay_html}
                  </div>

                  <!-- Clean Scripture Pull Quote with Burnt Amber Card Styling -->
                  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-top: 24px;">
                    <tr>
                      <td style="border-left: 4px solid #D97706; border-top: 1px solid #F3E8DC; border-bottom: 1px solid #F3E8DC; border-right: 1px solid #F3E8DC; padding: 12px 18px; background-color: #FAF6F1; border-radius: 0 4px 4px 0;">
                        <div style="font-family: Georgia, 'Times New Roman', serif; font-size: 15.5px; line-height: 1.62; color: #1C1917; font-style: italic; padding-right: 12px;">
                          "{scripture.get('text', '')}"
                        </div>
                        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 12px; font-weight: 700; color: #9A3412; margin-top: 8px;">
                          {scripture.get('ref', '')} ({scripture.get('translation', 'WEB')})
                        </div>
                      </td>
                    </tr>
                  </table>

                  {provenance_html}
                </td>
              </tr>
            </table>

            <!-- Today's Artwork Preview -->
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
              <tr>
                <td style="padding: 28px 0; border-bottom: 1px solid #E7E0D8;">
                  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-bottom: 14px;">
                    <tr>
                      <td align="left">
                        <span style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 15px; font-weight: 700; color: #1C1917;">
                          Today's flyer
                        </span>
                      </td>
                      <td align="right">
                        <span style="display: inline-block; background-color: #FAF6F1; color: #9A3412; border: 1px solid #D97706; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 11px; font-weight: 700; padding: 3px 9px; border-radius: 4px; text-transform: uppercase;">
                          Terracotta &amp; Amber Edition
                        </span>
                      </td>
                    </tr>
                  </table>
                  <div align="center">
                    <img src="cid:flyer_primary_4_5" alt="{theme} Graphic" style="width: 100%; max-width: 490px; height: auto; display: block; margin: 0 auto; border: 1px solid #E7E0D8; border-radius: 4px;">
                  </div>
                  <div align="center" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 12.5px; color: #57534E; margin-top: 12px; line-height: 1.5;">
                    4:5 feed edition previewed above &middot; 1:1 square, 9:16 story, and alternate design attached.
                  </div>
                </td>
              </tr>
            </table>

            <!-- Ready-to-Post Captions -->
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-top: 28px">
              <tr>
                <td style="padding-bottom: 12px; border-bottom: 2px solid #D97706;">
                  <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 15px; color: #9A3412; font-weight: 700;">
                    Captions for publishing
                  </div>
                </td>
              </tr>

              <!-- Facebook -->
              <tr>
                <td style="padding: 18px 0; border-bottom: 1px solid #E7E0D8;">
                  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-bottom: 8px;">
                    <tr>
                      <td align="left" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 13px; color: #1C1917; font-weight: 700;">
                        Facebook
                      </td>
                      <td align="right">
                        <a href="{fb_intent}" target="_blank" style="background-color: #9A3412; color: #FFFFFF !important; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 12px; font-weight: 700; text-decoration: none; padding: 5px 12px; border-radius: 4px; display: inline-block; white-space: nowrap;">
                          Share post &rarr;
                        </a>
                      </td>
                    </tr>
                  </table>
                  <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 14px; color: #292524; user-select: all; word-wrap: break-word;">
                    {fb_html}
                  </div>
                </td>
              </tr>

              <!-- Instagram -->
              <tr>
                <td style="padding: 18px 0; border-bottom: 1px solid #E7E0D8;">
                  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-bottom: 8px;">
                    <tr>
                      <td align="left" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 13px; color: #1C1917; font-weight: 700;">
                        Instagram
                      </td>
                      <td align="right">
                        <a href="https://www.instagram.com/" target="_blank" style="background-color: #9A3412; color: #FFFFFF !important; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 12px; font-weight: 700; text-decoration: none; padding: 5px 12px; border-radius: 4px; display: inline-block; white-space: nowrap;">
                          Open Instagram &rarr;
                        </a>
                      </td>
                    </tr>
                  </table>
                  <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 14px; color: #292524; user-select: all; word-wrap: break-word;">
                    {ig_html}
                  </div>
                </td>
              </tr>

              <!-- WhatsApp -->
              <tr>
                <td style="padding: 18px 0; border-bottom: 1px solid #E7E0D8;">
                  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-bottom: 8px;">
                    <tr>
                      <td align="left" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 13px; color: #1C1917; font-weight: 700;">
                        WhatsApp Status
                      </td>
                      <td align="right">
                        <a href="{wa_intent}" target="_blank" style="background-color: #9A3412; color: #FFFFFF !important; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 12px; font-weight: 700; text-decoration: none; padding: 5px 12px; border-radius: 4px; display: inline-block; white-space: nowrap;">
                          Send on WhatsApp &rarr;
                        </a>
                      </td>
                    </tr>
                  </table>
                  <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 14px; color: #292524; user-select: all; word-wrap: break-word;">
                    {wa_html}
                  </div>
                </td>
              </tr>

              <!-- Two-Column Row: X & Threads -->
              <tr>
                <td style="padding: 18px 0; border-bottom: 1px solid #E7E0D8;">
                  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                    <tr>
                      <td class="stack-col stack-col-divider" width="50%" valign="top" style="padding-right: 16px; border-right: 1px solid #E7E0D8;">
                        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-bottom: 6px;">
                          <tr>
                            <td align="left" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 13px; color: #1C1917; font-weight: 700;">
                              X
                            </td>
                            <td align="right">
                              <a href="{x_intent}" target="_blank" style="background-color: #9A3412; color: #FFFFFF !important; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 11px; font-weight: 700; text-decoration: none; padding: 3px 9px; border-radius: 3px; display: inline-block; white-space: nowrap;">
                                Post &rarr;
                              </a>
                            </td>
                          </tr>
                        </table>
                        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 13.5px; line-height: 1.58; color: #292524; user-select: all; word-wrap: break-word;">
                          {x_post}
                        </div>
                      </td>
                      <td class="stack-col" width="50%" valign="top" style="padding-left: 16px;">
                        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-bottom: 6px;">
                          <tr>
                            <td align="left" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 13px; color: #1C1917; font-weight: 700;">
                              Threads
                            </td>
                            <td align="right">
                              <a href="{threads_intent}" target="_blank" style="background-color: #9A3412; color: #FFFFFF !important; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 11px; font-weight: 700; text-decoration: none; padding: 3px 9px; border-radius: 3px; display: inline-block; white-space: nowrap;">
                                Post &rarr;
                              </a>
                            </td>
                          </tr>
                        </table>
                        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 13.5px; line-height: 1.58; color: #292524; user-select: all; word-wrap: break-word;">
                          {threads_post}
                        </div>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>

              <!-- Story Text & Closing Prayer -->
              <tr>
                <td style="padding: 18px 0 4px 0;">
                  <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 13.5px; color: #292524; line-height: 1.58; margin-bottom: 8px;">
                    <strong style="color: #9A3412;">Story line:</strong>
                    <span style="user-select: all;">{story_text}</span>
                  </div>
                  <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 13.5px; color: #292524; line-height: 1.58;">
                    <strong style="color: #9A3412;">Short prayer:</strong>
                    <span style="user-select: all;">{altar_invite}</span>
                  </div>
                </td>
              </tr>
            </table>

            {radar_section_html}

            <!-- Branded Terracotta & Amber Sign-off -->
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-top: 34px; border-top: 2px solid #D97706;">
              <tr>
                <td align="left" style="padding-top: 18px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 12.5px; line-height: 1.6; color: #57534E;">
                  <strong style="color: #9A3412;">The Kingdom Journal</strong> &middot; Warm Terracotta &amp; Burnt Amber Edition &middot; Ready for today's scheduling. Attached files contain full-resolution PNGs.
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
        """Dispatches the complete issue briefing email via SMTP."""
        html_content = self.build_email_html(
            issue_number=issue_number,
            package=package,
            verified_meta=verified_meta,
            radar_videos=radar_videos,
            quota_used=quota_used,
            review_flags=review_flags
        )

        plain_text = (
            f"The Kingdom Journal - Issue {issue_number} [Warm Terracotta & Burnt Amber Edition]\n"
            f"{package.get('theme')}: {package.get('hook')}\n\n"
            f"MORNING REFLECTION:\n{package.get('reflection')}\n\n"
            f"FACEBOOK:\n{package.get('facebook_post')}\n\n"
            f"INSTAGRAM:\n{package.get('instagram_caption')}\n\n"
            f"WHATSAPP:\n{package.get('whatsapp_status')}\n\n"
            f"X:\n{package.get('x_post')}\n"
        )

        out_dir = BASE_DIR / "out" / f"issue-{issue_number}"
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "email.html").write_text(html_content, encoding="utf-8")
        (out_dir / "briefing.txt").write_text(plain_text, encoding="utf-8")
        (out_dir / "package.json").write_text(json.dumps(package, indent=2, ensure_ascii=False), encoding="utf-8")

        for key, img in flyer_images.items():
            img.save(out_dir / f"{key}.png", format="PNG")

        logger.info(f"Successfully archived Issue {issue_number} assets to {out_dir}")

        if dry_run:
            logger.info("[DRY-RUN] Execution completed successfully. Live email dispatch skipped.")
            return True

        if not self.smtp_user or not self.smtp_password:
            raise ValueError("SMTP_USER and SMTP_PASSWORD must be configured in environment or .env")

        msg_root = email.mime.multipart.MIMEMultipart("mixed")
        msg_root["Subject"] = f"The Kingdom Journal · Issue {issue_number} [Warm Terracotta & Amber]: {package.get('hook', 'Daily Dispatch')}"
        msg_root["From"] = f"The Kingdom Journal <{self.smtp_user}>"
        msg_root["To"] = self.recipient

        msg_alt = email.mime.multipart.MIMEMultipart("alternative")
        msg_alt.attach(email.mime.text.MIMEText(plain_text, "plain", "utf-8"))

        msg_related = email.mime.multipart.MIMEMultipart("related")
        msg_related.attach(email.mime.text.MIMEText(html_content, "html", "utf-8"))

        if "flyer_primary_4_5" in flyer_images:
            jpeg_bytes = optimize_email_asset(flyer_images["flyer_primary_4_5"], max_kb=180)
            img_part = email.mime.image.MIMEImage(jpeg_bytes, _subtype="jpeg")
            img_part.add_header("Content-ID", "<flyer_primary_4_5>")
            img_part.add_header("Content-Disposition", "inline", filename="flyer_primary_4_5.jpg")
            msg_related.attach(img_part)

        msg_alt.attach(msg_related)
        msg_root.attach(msg_alt)

        for fname, img in flyer_images.items():
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            part = email.mime.application.MIMEApplication(buf.getvalue(), Name=f"{fname}.png")
            part["Content-Disposition"] = f'attachment; filename="{fname}.png"'
            msg_root.attach(part)

        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.sendmail(self.smtp_user, [self.recipient], msg_root.as_string())

        logger.info(f"Successfully sent Issue {issue_number} email briefing to {self.recipient}")
        return True
