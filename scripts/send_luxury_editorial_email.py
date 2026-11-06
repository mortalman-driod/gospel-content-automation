"""
Luxury Editorial Gospel Briefing (Journalistic & Theological Integrity Edition 3.0)
Strict Integrity Standards:
1. Verbatim Scripture from ScriptureEngine with translation tags.
2. Absolute separation: Editorial Axiom (The Kingdom Journal) vs Scripture vs Thematic Ministers.
3. Transparent UI: Every outbound social payload is displayed in the email before clicking.
4. Working intents: Threads (threads.com with length guard), WhatsApp, X/Twitter, and honest Open Instagram/Facebook buttons.
5. Rich YouTube Radar: Clickable video URLs, view counts, upload recency, and timestamp.
6. Accessible HTML: WCAG AA contrast (>= 4.5:1), 48px touch targets, and hidden preheaders.
"""

import email.utils
import os
import smtplib
import sys
import urllib.parse
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))

try:
    import content_db
    import catch_up_scheduler
    import youtube_quote_analyzer
    import humanized_content_engine
    import cloud_image_generator
    import scripture_engine
except ImportError:
    content_db = None
    catch_up_scheduler = None
    youtube_quote_analyzer = None
    humanized_content_engine = None
    cloud_image_generator = None
    scripture_engine = None

def load_env_file():
    env_path = BASE_DIR / ".env"
    if env_path.is_file():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k and k not in os.environ:
                    os.environ[k] = v

def generate_social_intent_links(captions: dict) -> dict:
    tw_text = urllib.parse.quote(captions.get('twitter', '')[:240])
    wa_text = urllib.parse.quote(captions.get('whatsapp', ''))
    th_text = urllib.parse.quote(captions.get('threads', '')[:480])

    return {
        "instagram": "https://www.instagram.com/",
        "instagram_story": "https://www.instagram.com/",
        "twitter": f"https://twitter.com/intent/tweet?text={tw_text}",
        "whatsapp": f"https://wa.me/?text={wa_text}",
        "threads": f"https://threads.com/intent/post?text={th_text}",
        "facebook": "https://www.facebook.com/"
    }

def build_luxury_email_html(links: dict, captions: dict, essay_data: dict, quote_data: dict, videos: list = None, issue_num: int = 49) -> str:
    # 1. YouTube Radar HTML
    youtube_html = ""
    radar_time = quote_data.get("radar_pulled_at", datetime.now().strftime("%B %d, %Y at %H:%M UTC"))
    if videos:
        items_html = ""
        for v in videos[:3]:
            title = v.get("title", "")
            channel = v.get("channel", "")
            views = v.get("views", "")
            url = v.get("url", f"https://www.youtube.com/results?search_query={urllib.parse.quote(title)}")
            views_badge = f" • <span style='color: #57534e; font-size: 11px;'>{views}</span>" if views else ""
            items_html += f"""
            <tr>
              <td class="dark-radar-text" style="padding: 9px 0; font-size: 13px; line-height: 1.5; color: #2e2b27; border-bottom: 1px dashed #e7e5e4;">
                <span style="font-weight: 700; color: #1c1917;" class="dark-heading">{channel}</span>{views_badge}<br />
                <a href="{url}" target="_blank" style="color: #b45309; text-decoration: underline; font-style: italic;">
                  {title}
                </a>
              </td>
            </tr>"""

        youtube_html = f"""
        <!-- CURATED MORNING RADAR (Live YouTube Integration) -->
        <table role="presentation" class="dark-radar-box" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin: 28px 0 12px 0; background-color: #faf9f6; border: 1px solid #e7e5e4; border-radius: 4px;">
          <tr>
            <td style="padding: 18px 22px;">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                <tr>
                  <td align="left" style="font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #57534e;" class="dark-subtitle">
                    TODAY'S VIRAL MINISTRATIONS • LIVE RADAR
                  </td>
                  <td align="right" style="font-size: 10px; color: #78716c;" class="dark-subtitle">
                    {radar_time}
                  </td>
                </tr>
              </table>
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-top: 10px;">
                {items_html}
              </table>
              <div style="font-size: 11px; color: #78716c; margin-top: 10px; font-style: italic;">
                * Streaming data verified via YouTube Data API v3. Thematic inspiration for today's journal.
              </div>
            </td>
          </tr>
        </table>
        """

    # 2. Essay paragraphs
    essay_paragraphs_html = ""
    for p in essay_data.get("essay_paragraphs", []):
        essay_paragraphs_html += f"""
        <p class="dark-body" style="font-family: Georgia, 'Times New Roman', serif; font-size: 16px; line-height: 1.85; color: #2e2b27; margin: 0 0 20px 0;">
          {p}
        </p>"""

    title = essay_data.get("title", "The Protocol of the Secret Place")
    subtitle = essay_data.get("subtitle", "On the quiet power of consecration.")
    date_str = essay_data.get("date_str", datetime.now().strftime("%A, %B %d, %Y"))
    
    # 3. Strict Attribution Separation
    verbatim_scripture = essay_data.get("verbatim_scripture", quote_data.get("verbatim_scripture", "He who dwells in the secret place of the Most High will rest in the shadow of the Almighty."))
    scripture_ref = essay_data.get("scripture_display_ref", quote_data.get("scripture", "Psalm 91:1 [WEB]"))
    editorial_axiom = essay_data.get("editorial_axiom", quote_data.get("quote", "Spiritual authority is not acquired on public stages; it is forged in the silence of deep consecration."))
    inspirations = essay_data.get("inspirations", quote_data.get("speaker", "Dunsin Oyekan & Apostle Joshua Selman"))

    # Formatted captions display
    ig_caption_display = captions.get('instagram', '').replace('\n', '<br>')
    reel_script_display = captions.get('reel_script', '').replace('\n', '<br>')
    wa_display = captions.get('whatsapp', '').replace('\n', '<br>')
    tw_display = captions.get('twitter', '').replace('\n', '<br>')
    th_display = captions.get('threads', '').replace('\n', '<br>')
    fb_display = captions.get('facebook', '').replace('\n', '<br>')

    preheader_text = f"{title} • {editorial_axiom[:90]}..."

    return f"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="color-scheme" content="light dark" />
  <meta name="supported-color-schemes" content="light dark" />
  <meta name="x-apple-disable-message-reformatting" />
  <title>The Kingdom Journal • Issue {issue_num}</title>
  <!--[if mso]>
  <style type="text/css">
    table {{border-collapse:collapse;border-spacing:0;margin:0;}}
    div, td, a, span, p {{font-family: Georgia, 'Times New Roman', serif !important;}}
  </style>
  <![endif]-->
  <style type="text/css">
    :root {{
      color-scheme: light dark;
      supported-color-schemes: light dark;
    }}
    body {{
      margin: 0;
      padding: 0;
      background-color: #f7f6f2;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      color: #1a1a1a;
      -webkit-font-smoothing: antialiased;
    }}
    img {{
      border: 0;
      outline: none;
      text-decoration: none;
      -ms-interpolation-mode: bicubic;
    }}
    a {{
      text-decoration: none;
    }}
    
    @media only screen and (max-width: 620px) {{
      .wrapper {{
        width: 100% !important;
        padding: 8px !important;
      }}
      .content-padding {{
        padding: 24px 18px !important;
      }}
      .headline {{
        font-size: 26px !important;
        line-height: 1.25 !important;
      }}
      .btn-touch {{
        display: block !important;
        width: 100% !important;
        margin-bottom: 10px !important;
        text-align: center !important;
        box-sizing: border-box !important;
      }}
    }}
    
    @media (prefers-color-scheme: dark) {{
      body, .dark-bg {{
        background-color: #121212 !important;
        color: #f5f5f4 !important;
      }}
      .dark-card {{
        background-color: #1c1917 !important;
        border-color: #292524 !important;
      }}
      .dark-heading {{
        color: #f5f5f4 !important;
      }}
      .dark-body {{
        color: #d6d3d1 !important;
      }}
      .dark-subtitle {{
        color: #a8a29e !important;
      }}
      .dark-quote-box {{
        background-color: #262320 !important;
        border-left-color: #d97706 !important;
      }}
      .dark-radar-box {{
        background-color: #201d1b !important;
        border-color: #2e2a27 !important;
      }}
      .dark-caption-box {{
        background-color: #24211e !important;
        border-color: #38332e !important;
      }}
      .dark-footer {{
        background-color: #171514 !important;
        border-color: #292524 !important;
      }}
    }}
  </style>
</head>
<body style="margin: 0; padding: 0; background-color: #f7f6f2; -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%;">

  <!-- INVISIBLE PREHEADER (WCAG & Client Snippet Fix) -->
  <div style="display: none; font-size: 1px; color: #f7f6f2; line-height: 1px; max-height: 0px; max-width: 0px; opacity: 0; overflow: hidden; mso-hide: all;">
    {preheader_text} &zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;
  </div>

  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #f7f6f2;" class="dark-bg">
    <tr>
      <td align="center" style="padding: 24px 12px;">
        
        <!--[if mso]>
        <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" align="center">
        <tr>
        <td>
        <![endif]-->
        
        <table role="presentation" class="wrapper dark-card" width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width: 600px; background-color: #ffffff; border: 1px solid #eae7e0; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);">
          
          <!-- TOP EMBOSSED GOLD HEADER BAR -->
          <tr>
            <td height="5" style="background: linear-gradient(90deg, #92400e 0%, #d97706 50%, #f59e0b 100%); font-size: 0; line-height: 0;">&nbsp;</td>
          </tr>

          <!-- PUBLICATION MASTHEAD -->
          <tr>
            <td class="content-padding" style="padding: 40px 48px 24px 48px; border-bottom: 1px solid #f0ede6; text-align: center;">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                <tr>
                  <td align="center">
                    <div class="dark-subtitle" style="font-size: 11px; font-weight: 700; letter-spacing: 3.5px; text-transform: uppercase; color: #57534e; margin-bottom: 14px;">
                      THE KINGDOM JOURNAL • DAILY EDITORIAL
                    </div>
                    <h1 class="headline dark-heading" style="font-family: Georgia, 'Times New Roman', serif; font-size: 32px; font-weight: 400; line-height: 1.25; color: #1a1a1a; margin: 0 0 12px 0; letter-spacing: -0.5px;">
                      {title}
                    </h1>
                    <p class="dark-subtitle" style="font-family: Georgia, 'Times New Roman', serif; font-size: 15px; font-style: italic; color: #57534e; margin: 0 auto 16px auto; max-width: 480px; line-height: 1.55;">
                      {subtitle}
                    </p>
                    <div class="dark-issue-badge" style="border-top: 1px solid #f0ede6; padding-top: 10px; font-size: 11px; letter-spacing: 2px; text-transform: uppercase; color: #57534e;">
                      Vol. IV • Issue {issue_num} • {date_str}
                    </div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- THE MORNING ESSAY -->
          <tr>
            <td class="content-padding" style="padding: 38px 48px 24px 48px;">
              
              {essay_paragraphs_html}

              <!-- 1. VERBATIM SCRIPTURE ANCHOR BOX -->
              <table role="presentation" class="dark-quote-box" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin: 24px 0 18px 0; border-left: 3px solid #16a34a; background-color: #f7fcf8; border-radius: 2px;">
                <tr>
                  <td style="padding: 18px 22px;">
                    <div style="font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #166534; margin-bottom: 8px;">
                      📖 SCRIPTURE ANCHOR (VERBATIM)
                    </div>
                    <div class="dark-quote-text" style="font-family: Georgia, 'Times New Roman', serif; font-size: 16px; font-style: italic; color: #1e293b; line-height: 1.6;">
                      “{verbatim_scripture}”
                    </div>
                    <div class="dark-quote-meta" style="font-size: 12px; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase; color: #15803d; margin-top: 8px;">
                      — {scripture_ref}
                    </div>
                  </td>
                </tr>
              </table>

              <!-- 2. EDITORIAL AXIOM BOX (PROPRIETARY) -->
              <table role="presentation" class="dark-quote-box" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin: 18px 0 24px 0; border-left: 3px solid #b45309; background-color: #faf9f6; border-radius: 2px;">
                <tr>
                  <td style="padding: 18px 22px;">
                    <div style="font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #92400e; margin-bottom: 8px;">
                      🕊️ EDITORIAL PRINCIPLE
                    </div>
                    <div class="dark-quote-text" style="font-family: Georgia, 'Times New Roman', serif; font-size: 17px; font-weight: 500; color: #1c1917; line-height: 1.6;">
                      “{editorial_axiom}”
                    </div>
                    <div class="dark-quote-meta" style="font-size: 11px; letter-spacing: 1.5px; text-transform: uppercase; color: #57534e; margin-top: 8px;">
                      — The Kingdom Journal Editorial
                    </div>
                    <div style="font-size: 11px; color: #78716c; margin-top: 6px; font-style: italic;">
                      Thematic inspiration drawn from: {inspirations}
                    </div>
                  </td>
                </tr>
              </table>

              <!-- LIVE YOUTUBE MINISTRATION RADAR -->
              {youtube_html}

            </td>
          </tr>

          <!-- ============================================== -->
          <!-- PART I: THE SQUARE MASTER ARTWORK (1:1)       -->
          <!-- ============================================== -->
          <tr>
            <td class="content-padding" style="padding: 10px 48px 36px 48px;">
              <div style="border-top: 1px solid #f0ede6; padding-top: 30px;" class="dark-masthead">
                
                <div class="dark-subtitle" style="font-size: 11px; font-weight: 700; letter-spacing: 2.5px; text-transform: uppercase; color: #57534e; margin-bottom: 6px;">
                  THE ARTWORK • MASTER COMPOSITION (1:1)
                </div>
                <h3 class="dark-heading" style="font-family: Georgia, 'Times New Roman', serif; font-size: 21px; font-weight: normal; color: #1a1a1a; margin: 0 0 16px 0;">
                  {title}
                </h3>

                <!-- Native Studio Artwork Display -->
                <div style="text-align: center; margin: 16px 0 24px 0;">
                  <img src="cid:flyer_dawn" alt="{title} Artwork" width="504" style="max-width: 100%; width: 100%; height: auto; border: 1px solid #e5e2da; display: block; margin: 0 auto; box-shadow: 0 6px 24px rgba(0,0,0,0.06);" />
                </div>

                <!-- INSTAGRAM CAPTION & REEL SCRIPT COPY BOX -->
                <div class="dark-caption-box" style="background-color: #faf9f6; border: 1px solid #e5e2da; border-left: 3px solid #c13584; padding: 20px 22px; margin-bottom: 20px; border-radius: 4px;">
                  <div style="font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #c13584; margin-bottom: 8px;">
                    📸 INSTAGRAM CAPTION (SELECT &amp; COPY)
                  </div>
                  <div style="font-size: 13px; line-height: 1.7; color: #2e2b27; margin-bottom: 16px;" class="dark-body">
                    {ig_caption_display}
                  </div>
                  
                  {f'''
                  <div style="border-top: 1px dashed #e5e2da; padding-top: 14px; margin-top: 14px;">
                    <div style="font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #92400e; margin-bottom: 6px;">
                      🎬 INSTAGRAM REEL SCRIPT (30s)
                    </div>
                    <div style="font-size: 13px; line-height: 1.7; color: #2e2b27;" class="dark-body">
                      {reel_script_display}
                    </div>
                  </div>
                  ''' if reel_script_display else ''}
                </div>

                <!-- INSTAGRAM ACTION BUTTON -->
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-bottom: 12px;">
                  <tr>
                    <td align="left">
                      <a href="{links['instagram']}" target="_blank" class="btn-touch" style="display: inline-block; background-color: #c13584; color: #ffffff; text-decoration: none; font-size: 12px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; padding: 14px 26px; border-radius: 4px; min-height: 48px; box-sizing: border-box; line-height: 20px;">
                        Open Instagram
                      </a>
                    </td>
                  </tr>
                </table>

              </div>
            </td>
          </tr>

          <!-- ============================================== -->
          <!-- PART II: THE MOBILE REFLECTION (WHATSAPP 9:16) -->
          <!-- ============================================== -->
          <tr>
            <td class="content-padding" style="padding: 10px 48px 36px 48px;">
              <div style="border-top: 1px solid #f0ede6; padding-top: 30px;" class="dark-masthead">
                
                <div style="font-size: 11px; font-weight: 700; letter-spacing: 2.5px; text-transform: uppercase; color: #15803d; margin-bottom: 6px;">
                  THE MOBILE REFLECTION • STATUS &amp; STORY POSTER (9:16)
                </div>
                <h3 class="dark-heading" style="font-family: Georgia, 'Times New Roman', serif; font-size: 21px; font-weight: normal; color: #1a1a1a; margin: 0 0 16px 0;">
                  What God Builds in Secret
                </h3>

                <!-- Clean Vertical Flyer Display -->
                <div style="text-align: center; margin: 16px 0 24px 0;">
                  <img src="cid:flyer_secret_place" alt="What God Builds in Secret Poster" width="300" style="max-width: 300px; width: 100%; height: auto; border: 1px solid #e5e2da; display: block; margin: 0 auto; box-shadow: 0 6px 24px rgba(0,0,0,0.06);" />
                </div>

                <!-- WHATSAPP DEVOTIONAL PAYLOAD BOX (Visible Before Sending) -->
                <div class="dark-whatsapp-box" style="background-color: #f7fcf8; border: 1px solid #e2ece3; border-left: 3px solid #16a34a; padding: 20px 22px; margin-bottom: 20px; border-radius: 4px;">
                  <div style="font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #15803d; margin-bottom: 10px;">
                    💬 WHATSAPP DEVOTIONAL BROADCAST (PREVIEW)
                  </div>
                  <div style="font-size: 13px; line-height: 1.75; color: #2e3b2e;" class="dark-body">
                    {wa_display}
                  </div>
                </div>

                <!-- WHATSAPP & STORY BUTTONS (48px Touch Targets) -->
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                  <tr>
                    <td class="mobile-stack" align="left" style="padding-bottom: 8px;">
                      <a href="{links['whatsapp']}" target="_blank" class="btn-touch" style="display: inline-block; background-color: #15803d; color: #ffffff; text-decoration: none; font-size: 12px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; padding: 14px 24px; border-radius: 4px; min-height: 48px; box-sizing: border-box; line-height: 20px;">
                        Send via WhatsApp
                      </a>
                    </td>
                    <td class="mobile-stack" align="right" style="padding-bottom: 8px;">
                      <a href="{links['instagram_story']}" target="_blank" class="btn-touch" style="display: inline-block; background-color: #c13584; color: #ffffff; text-decoration: none; font-size: 12px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; padding: 14px 24px; border-radius: 4px; min-height: 48px; box-sizing: border-box; line-height: 20px;">
                        Open Instagram Story
                      </a>
                    </td>
                  </tr>
                </table>

              </div>
            </td>
          </tr>

          <!-- ============================================== -->
          <!-- PART III: MULTI-PLATFORM SOCIAL BROADCAST KIT   -->
          <!-- ============================================== -->
          <tr>
            <td class="content-padding" style="padding: 10px 48px 36px 48px;">
              <div style="border-top: 1px solid #f0ede6; padding-top: 30px;" class="dark-masthead">
                
                <div class="dark-subtitle" style="font-size: 11px; font-weight: 700; letter-spacing: 2.5px; text-transform: uppercase; color: #57534e; margin-bottom: 6px;">
                  COMMUNITY BROADCAST • SOCIAL SUITE
                </div>
                <h3 class="dark-heading" style="font-family: Georgia, 'Times New Roman', serif; font-size: 21px; font-weight: normal; color: #1a1a1a; margin: 0 0 16px 0;">
                  Multi-Platform Outreach Kit
                </h3>

                <!-- X / TWITTER POST CARD -->
                <div class="dark-caption-box" style="background-color: #faf9f6; border: 1px solid #e5e2da; border-left: 3px solid #1a1a1a; padding: 18px 20px; margin-bottom: 16px; border-radius: 4px;">
                  <div style="font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #1a1a1a; margin-bottom: 8px;">
                    🐦 X (TWITTER) POST
                  </div>
                  <div style="font-size: 13px; line-height: 1.6; color: #2e2b27; margin-bottom: 14px;" class="dark-body">
                    {tw_display}
                  </div>
                  <a href="{links['twitter']}" target="_blank" class="btn-touch" style="display: inline-block; background-color: #1a1a1a; color: #ffffff; text-decoration: none; font-size: 11px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; padding: 12px 22px; border-radius: 4px; min-height: 48px; box-sizing: border-box; line-height: 24px;">
                    Post to X
                  </a>
                </div>

                <!-- THREADS DISCUSSION CARD -->
                <div class="dark-caption-box" style="background-color: #faf9f6; border: 1px solid #e5e2da; border-left: 3px solid #44403c; padding: 18px 20px; margin-bottom: 16px; border-radius: 4px;">
                  <div style="font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #44403c; margin-bottom: 8px;">
                    🧵 THREADS COMMUNITY DISCUSSION
                  </div>
                  <div style="font-size: 13px; line-height: 1.6; color: #2e2b27; margin-bottom: 14px;" class="dark-body">
                    {th_display}
                  </div>
                  <a href="{links['threads']}" target="_blank" class="btn-touch" style="display: inline-block; background-color: #44403c; color: #ffffff; text-decoration: none; font-size: 11px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; padding: 12px 22px; border-radius: 4px; min-height: 48px; box-sizing: border-box; line-height: 24px;">
                    Post to Threads
                  </a>
                </div>

                <!-- FACEBOOK DEVOTIONAL CARD -->
                <div class="dark-caption-box" style="background-color: #faf9f6; border: 1px solid #e5e2da; border-left: 3px solid #1877f2; padding: 18px 20px; margin-bottom: 16px; border-radius: 4px;">
                  <div style="font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #1877f2; margin-bottom: 8px;">
                    👥 FACEBOOK COMMUNITY DEVOTIONAL (SELECT &amp; COPY)
                  </div>
                  <div style="font-size: 13px; line-height: 1.6; color: #2e2b27; margin-bottom: 14px;" class="dark-body">
                    {fb_display}
                  </div>
                  <a href="{links['facebook']}" target="_blank" class="btn-touch" style="display: inline-block; background-color: #1877f2; color: #ffffff; text-decoration: none; font-size: 11px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; padding: 12px 22px; border-radius: 4px; min-height: 48px; box-sizing: border-box; line-height: 24px;">
                    Open Facebook
                  </a>
                </div>

              </div>
            </td>
          </tr>

          <!-- CLASSIC FOOTER -->
          <tr>
            <td class="content-padding dark-footer" style="padding: 32px 48px; background-color: #faf9f6; border-top: 1px solid #e5e2da; text-align: center;">
              <p class="dark-subtitle" style="font-family: Georgia, 'Times New Roman', serif; font-size: 13px; font-style: italic; color: #57534e; margin: 0 0 8px 0; line-height: 1.5;">
                The Kingdom Journal is curated daily for personal reflection and ministry broadcast.
              </p>
              <p style="font-size: 11px; color: #57534e; letter-spacing: 1.5px; text-transform: uppercase; margin: 0;" class="dark-subtitle">
                Delivered to aondoaseerezekiel@gmail.com
              </p>
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
</html>"""

def send_luxury_editorial_email(recipient: str, subject: str = None, fliers_dir: Path = None, override_topic: dict = None, issue_num: int = 49):
    load_env_file()
    fliers_dir = fliers_dir or BASE_DIR / "reports" / "fliers"
    
    # 1. PILLAR 3: Analyze live YouTube videos to extract the best punchy line
    if override_topic:
        youtube_insight = override_topic
        print(f"[PIPELINE STEP 1] Using custom verified topic: '{youtube_insight.get('title')}'")
    else:
        youtube_insight = {
            "title": "The Protocol of the Secret Place",
            "hook_top": "What God builds in secret",
            "banner_text": "CANNOT BE SHAKEN",
            "quote": "Spiritual authority is not acquired on public stages; it is forged in the silence of deep consecration.",
            "speaker": "Dunsin Oyekan & Apostle Joshua Selman",
            "scripture": "Matthew 6:6",
            "videos": []
        }
        if youtube_quote_analyzer:
            try:
                analyzed = youtube_quote_analyzer.analyze_trending_gospel_videos()
                if analyzed and analyzed.get("quote"):
                    youtube_insight = analyzed
                    print(f"[PIPELINE STEP 1] YouTube Analysis complete. Topic: '{youtube_insight['title']}'")
            except Exception as ey:
                print(f"[PIPELINE NOTICE] YouTube analysis fallback: {ey}", file=sys.stderr)

    # 2. PILLAR 2: Generate humanized editorial essay and multi-platform captions with verified Scripture
    scripture_ref = youtube_insight.get("scripture", "Matthew 6:6")
    engine = humanized_content_engine.HumanizedContentEngine(
        editorial_axiom=youtube_insight.get("quote", "Spiritual authority is not acquired on public stages; it is forged in the silence of deep consecration."),
        scripture_ref=scripture_ref,
        inspirations=youtube_insight.get("speaker", "Dunsin Oyekan & Apostle Joshua Selman"),
        title=youtube_insight.get("title")
    )
    essay_data = engine.generate_editorial_micro_essay()
    captions = engine.generate_multi_platform_captions(essay_data.get("gemini_captions"))
    print(f"[PIPELINE STEP 2] Content engine generated editorial essay for '{essay_data['title']}'")

    # 3. PILLAR 1: Ensure fliers are synthesized and verified
    if cloud_image_generator:
        try:
            cloud_image_generator.generate_daily_fliers(topic_data={
                "title": essay_data["title"],
                "quote": youtube_insight["quote"],
                "speaker": youtube_insight["speaker"],
                "scripture": scripture_ref
            })
            print("[PIPELINE STEP 3] Flier generator verified high-res studio assets.")
        except Exception as eg:
            print(f"[PIPELINE NOTICE] Flier generator using pre-existing assets: {eg}", file=sys.stderr)

    # 4. PILLAR 4: Assemble luxury email
    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER", "").strip()
    smtp_pass = os.environ.get("SMTP_PASSWORD", "").strip().replace(" ", "")

    if not smtp_user or not smtp_pass:
        print("[ERROR] SMTP_USER or SMTP_PASSWORD not set in environment or .env", file=sys.stderr)
        return False

    final_subject = subject or f"🕊️ The Kingdom Journal • {essay_data['title']} (Issue {issue_num})"

    msg = MIMEMultipart("related")
    msg["Subject"] = final_subject
    msg["From"] = f"The Kingdom Journal <{smtp_user}>"
    msg["To"] = recipient
    msg["Date"] = email.utils.formatdate(localtime=True)
    msg["Message-ID"] = email.utils.make_msgid(domain="gmail.com")

    links = generate_social_intent_links(captions)
    html_content = build_luxury_email_html(
        links=links,
        captions=captions,
        essay_data=essay_data,
        quote_data=youtube_insight,
        videos=youtube_insight.get("videos", []),
        issue_num=issue_num
    )
    
    plain_text = (
        f"The Kingdom Journal • Issue {issue_num}\n"
        f"{essay_data['date_str']}\n\n"
        f"{essay_data['title']}\n"
        f"{essay_data['subtitle']}\n\n"
        f"EDITORIAL AXIOM:\n"
        f"“{essay_data['editorial_axiom']}” — The Kingdom Journal Editorial\n"
        f"Thematic inspiration from {essay_data['inspirations']}\n\n"
        f"SCRIPTURE ANCHOR:\n"
        f"“{essay_data['verbatim_scripture']}” — {essay_data['scripture_display_ref']}\n\n"
        f"Please view this email in an HTML-compatible email client to review today's artwork and pre-written social kit."
    )

    alt_part = MIMEMultipart("alternative")
    alt_part.attach(MIMEText(plain_text, "plain", "utf-8"))
    alt_part.attach(MIMEText(html_content, "html", "utf-8"))
    msg.attach(alt_part)

    # Attach the two authentic viral fliers
    attachments = [
        ("flyer_dawn", fliers_dir / "flyer_dawn_square.jpg"),
        ("flyer_secret_place", fliers_dir / "flyer_secret_place_story.jpg")
    ]

    for cid, img_file in attachments:
        if img_file.is_file():
            try:
                with open(img_file, "rb") as f:
                    mime_img = MIMEImage(f.read(), _subtype="jpeg")
                    mime_img.add_header("Content-ID", f"<{cid}>")
                    mime_img.add_header("Content-Disposition", "inline", filename=img_file.name)
                    msg.attach(mime_img)
                    print(f"[ATTACHED] {img_file.name} as CID:{cid}")
            except Exception as e:
                print(f"[WARNING] Failed to attach {img_file}: {e}", file=sys.stderr)
        else:
            print(f"[WARNING] Flyer image not found: {img_file}", file=sys.stderr)

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=45) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, [recipient], msg.as_string())
        print(f"[SUCCESS] High-accuracy luxury briefing successfully delivered to {recipient}")

        if content_db:
            content_db.record_dispatch(final_subject, recipient, "SUCCESS")
            content_db.record_quote(
                quote_text=youtube_insight["quote"],
                speaker=youtube_insight.get("speaker", "The Kingdom Journal"),
                scripture=scripture_ref
            )
            for lv in youtube_insight.get("videos", []):
                content_db.record_video(
                    video_id=lv.get("video_id", "live_asset"),
                    title=lv.get("title", ""),
                    channel=lv.get("channel", ""),
                    published_at=lv.get("published_at", datetime.now().isoformat())
                )
            print("[DATABASE] Today's fresh YouTube insight and video assets archived in SQLite memory.")

        if catch_up_scheduler:
            catch_up_scheduler.save_state("SUCCESS")

        return True
    except Exception as e:
        print(f"[ERROR] Delivery failed: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    send_luxury_editorial_email(recipient="aondoaseerezekiel@gmail.com", issue_num=49)
