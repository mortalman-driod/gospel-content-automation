"""
Luxury Editorial Gospel Briefing (High-Class Edition 2.0)
Unified Engine orchestrating:
1. YouTube Video Analyzer & Punchy Line Extractor (Pillar 3)
2. Humanized De-AI Content & Caption Engine (Pillar 2)
3. Cloud Image Generator & Studio Compositor (Pillar 1)
4. Luxury Responsive Email & Outlook Body Builder (Pillar 4)
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

# Add parent path for database & state imports
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    import content_db
    import catch_up_scheduler
    import youtube_quote_analyzer
    import humanized_content_engine
    import cloud_image_generator
except ImportError:
    content_db = None
    catch_up_scheduler = None
    youtube_quote_analyzer = None
    humanized_content_engine = None
    cloud_image_generator = None

def load_env_file():
    env_path = Path(__file__).resolve().parent.parent / ".env"
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
    return {
        "instagram": "https://www.instagram.com/create/select/",
        "instagram_story": "https://www.instagram.com/",
        "twitter": f"https://twitter.com/intent/tweet?text={urllib.parse.quote(captions['twitter'])}",
        "whatsapp": f"https://wa.me/?text={urllib.parse.quote(captions['whatsapp'])}",
        "threads": f"https://threads.net/intent/post?text={urllib.parse.quote(captions['threads'])}",
        "facebook": f"https://www.facebook.com/sharer/sharer.php?quote={urllib.parse.quote(captions['facebook'])}"
    }

def build_luxury_email_html(links: dict, captions: dict, essay_data: dict, quote_data: dict, videos: list = None) -> str:
    # Build the live listening section if YouTube videos are present
    youtube_html = ""
    if videos:
        items_html = ""
        for v in videos[:3]:
            title = v.get("title", "")
            channel = v.get("channel", "")
            items_html += f"""
            <tr>
              <td class="dark-radar-text" style="padding: 7px 0; font-size: 13px; line-height: 1.5; color: #44403c; border-bottom: 1px dashed #e7e5e4;">
                <span style="font-weight: 600; color: #1c1917;" class="dark-heading">{channel}</span> — <em>{title}</em>
              </td>
            </tr>"""

        youtube_html = f"""
        <!-- CURATED MORNING RADAR (Live YouTube Integration) -->
        <table role="presentation" class="dark-radar-box" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin: 24px 0 8px 0; background-color: #faf9f6; border: 1px solid #e7e5e4; border-radius: 2px;">
          <tr>
            <td style="padding: 16px 20px;">
              <div style="font-size: 10px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #8c827a; margin-bottom: 8px;" class="dark-subtitle">
                TODAY'S VIRAL MINISTRATIONS • LIVE RADAR
              </div>
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                {items_html}
              </table>
            </td>
          </tr>
        </table>
        """

    # Build essay paragraphs
    essay_paragraphs_html = ""
    for p in essay_data.get("essay_paragraphs", []):
        essay_paragraphs_html += f"""
        <p class="dark-body" style="font-family: Georgia, 'Times New Roman', serif; font-size: 16px; line-height: 1.8; color: #2e2b27; margin: 0 0 18px 0;">
          {p}
        </p>"""

    # Format the Instagram caption for clean display
    ig_caption_display = captions.get('instagram', '').replace('\n', '<br>')

    title = essay_data.get("title", "Divine Help at Break of Day")
    subtitle = essay_data.get("subtitle", "On the sacred mystery of God's timing and divine help in quiet seasons.")
    quote_text = quote_data.get("quote", "")
    speaker = quote_data.get("speaker", "Victoria Orenze & Apostle Joshua Selman")
    scripture = quote_data.get("scripture", "Psalm 46:5 • Isaiah 40:31")
    date_str = essay_data.get("date_str", "Friday, November 6, 2026")

    return f"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="color-scheme" content="light dark" />
  <meta name="supported-color-schemes" content="light dark" />
  <meta name="x-apple-disable-message-reformatting" />
  <title>The Kingdom Journal • Morning Edition</title>
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
    
    /* Responsive Mobile Layout */
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
      .mobile-stack {{
        display: block !important;
        width: 100% !important;
        text-align: center !important;
        margin-bottom: 8px !important;
      }}
      .btn-full {{
        display: block !important;
        width: 100% !important;
        margin: 6px 0 !important;
        text-align: center !important;
        box-sizing: border-box !important;
      }}
    }}

    /* Advanced Dark Mode Overrides */
    @media (prefers-color-scheme: dark) {{
      body, .dark-canvas {{
        background-color: #121212 !important;
        color: #e5e5e5 !important;
      }}
      .dark-card {{
        background-color: #1c1917 !important;
        border-color: #2e2a27 !important;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.6) !important;
      }}
      .dark-masthead {{
        border-bottom-color: #2e2a27 !important;
      }}
      .dark-heading {{
        color: #f5f5f4 !important;
      }}
      .dark-subtitle {{
        color: #a8a29e !important;
      }}
      .dark-issue-badge {{
        border-top-color: #2e2a27 !important;
        color: #78716c !important;
      }}
      .dark-body {{
        color: #d6d3d1 !important;
      }}
      .dark-quote-box {{
        background-color: #24201d !important;
        border-left-color: #d97706 !important;
      }}
      .dark-quote-text {{
        color: #fafaf9 !important;
      }}
      .dark-quote-meta {{
        color: #a8a29e !important;
      }}
      .dark-radar-box {{
        background-color: #24201d !important;
        border-color: #38332e !important;
      }}
      .dark-radar-text {{
        color: #d6d3d1 !important;
        border-bottom-color: #38332e !important;
      }}
      .dark-caption-box {{
        background-color: #24201d !important;
        border-color: #38332e !important;
        color: #e7e5e4 !important;
      }}
      .dark-whatsapp-box {{
        background-color: #152219 !important;
        border-left-color: #16a34a !important;
        color: #dcfce7 !important;
      }}
      .dark-footer {{
        background-color: #171513 !important;
        border-top-color: #2e2a27 !important;
        color: #a8a29e !important;
      }}
      .dark-btn-facebook {{
        border-color: #57534e !important;
        color: #e7e5e4 !important;
      }}
    }}
  </style>
</head>
<body class="dark-canvas" style="margin: 0; padding: 40px 0; background-color: #f7f6f2; color: #1a1a1a;">

  <!-- Outer Canvas Table -->
  <table role="presentation" class="dark-canvas" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #f7f6f2;">
    <tr>
      <td align="center" style="padding: 20px 10px;">
        
        <!-- Main Document Card (Outlook & Modern Responsive) -->
        <!--[if mso]>
        <table align="center" border="0" cellspacing="0" cellpadding="0" width="600">
        <tr>
        <td align="center" valign="top" width="600">
        <![endif]-->
        <table role="presentation" class="wrapper dark-card" width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width: 600px; background-color: #ffffff; border: 1px solid #e5e2da; box-shadow: 0 4px 30px rgba(0, 0, 0, 0.05); text-align: left;">
          
          <!-- BESPOKE EDITORIAL MASTHEAD -->
          <tr>
            <td class="content-padding dark-masthead" style="padding: 48px 48px 30px 48px; text-align: center; border-bottom: 1px solid #1a1a1a;">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                <tr>
                  <td align="center">
                    <div class="dark-subtitle" style="font-size: 10px; font-weight: 700; letter-spacing: 3.5px; text-transform: uppercase; color: #8c827a; margin-bottom: 14px;">
                      THE KINGDOM JOURNAL • DAILY EDITORIAL
                    </div>
                    <h1 class="headline dark-heading" style="font-family: Georgia, 'Times New Roman', serif; font-size: 32px; font-weight: 400; line-height: 1.25; color: #1a1a1a; margin: 0 0 12px 0; letter-spacing: -0.5px;">
                      {title}
                    </h1>
                    <p class="dark-subtitle" style="font-family: Georgia, 'Times New Roman', serif; font-size: 15px; font-style: italic; color: #6e675f; margin: 0 auto 16px auto; max-width: 480px; line-height: 1.55;">
                      {subtitle}
                    </p>
                    <div class="dark-issue-badge" style="border-top: 1px solid #f0ede6; padding-top: 10px; font-size: 10px; letter-spacing: 2px; text-transform: uppercase; color: #a39c93;">
                      Vol. IV • Issue 48 • {date_str}
                    </div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- THE MORNING ESSAY (NO AI BULLETS) -->
          <tr>
            <td class="content-padding" style="padding: 38px 48px 24px 48px;">
              
              {essay_paragraphs_html}

              <!-- Curated Pull Quote Accent -->
              <table role="presentation" class="dark-quote-box" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin: 28px 0; border-left: 2px solid #b45309; background-color: #faf9f6;">
                <tr>
                  <td style="padding: 16px 20px;">
                    <div class="dark-quote-text" style="font-family: Georgia, 'Times New Roman', serif; font-size: 17px; font-style: italic; color: #1a1a1a; line-height: 1.55;">
                      “{quote_text}”
                    </div>
                    <div class="dark-quote-meta" style="font-size: 11px; letter-spacing: 1.5px; text-transform: uppercase; color: #8c827a; margin-top: 8px;">
                      — {scripture} • {speaker}
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
                
                <div class="dark-subtitle" style="font-size: 10px; font-weight: 700; letter-spacing: 2.5px; text-transform: uppercase; color: #a39c93; margin-bottom: 6px;">
                  THE ARTWORK • MASTER COMPOSITION (1:1)
                </div>
                <h3 class="dark-heading" style="font-family: Georgia, 'Times New Roman', serif; font-size: 21px; font-weight: normal; color: #1a1a1a; margin: 0 0 16px 0;">
                  {title}
                </h3>

                <!-- Native Studio Artwork Display -->
                <div style="text-align: center; margin: 16px 0 24px 0;">
                  <img src="cid:flyer_dawn" alt="{title} Artwork" width="504" style="max-width: 100%; width: 100%; height: auto; border: 1px solid #e5e2da; display: block; margin: 0 auto; box-shadow: 0 6px 24px rgba(0,0,0,0.06);" />
                </div>

                <!-- INSTAGRAM READY CAPTION BOX -->
                <div class="dark-caption-box" style="background-color: #faf9f6; border: 1px solid #e5e2da; border-left: 3px solid #c13584; padding: 18px 20px; margin-bottom: 20px; border-radius: 2px;">
                  <div style="font-size: 10px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #c13584; margin-bottom: 10px;">
                    📸 INSTAGRAM CAPTION &amp; REEL SCRIPT (TAP TO COPY)
                  </div>
                  <div style="font-size: 13px; line-height: 1.7; color: #2e2b27;" class="dark-body">
                    {ig_caption_display}
                  </div>
                </div>

                <!-- ACTION BUTTONS: INSTAGRAM + X + THREADS + FACEBOOK -->
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-bottom: 12px;">
                  <tr>
                    <td class="mobile-stack" align="left" style="padding-bottom: 8px;">
                      <!-- Instagram Feed Button -->
                      <a href="{links['instagram']}" target="_blank" class="btn-full" style="display: inline-block; background-color: #c13584; color: #ffffff; text-decoration: none; font-size: 11px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; padding: 11px 22px; border-radius: 2px; margin-right: 8px;">
                        Post to Instagram
                      </a>
                      <!-- Post to X Button -->
                      <a href="{links['twitter']}" target="_blank" class="btn-full" style="display: inline-block; background-color: #1a1a1a; color: #ffffff; text-decoration: none; font-size: 11px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; padding: 11px 20px; border-radius: 2px;">
                        Post to X
                      </a>
                    </td>
                    <td class="mobile-stack" align="right" style="padding-bottom: 8px;">
                      <!-- Post to Threads -->
                      <a href="{links['threads']}" target="_blank" class="btn-full" style="display: inline-block; background-color: #44403c; color: #ffffff; text-decoration: none; font-size: 11px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; padding: 11px 18px; border-radius: 2px; margin-right: 8px;">
                        Threads
                      </a>
                      <!-- Share to Facebook -->
                      <a href="{links['facebook']}" target="_blank" class="btn-full dark-btn-facebook" style="display: inline-block; border: 1px solid #d6d3d1; color: #292524; text-decoration: none; font-size: 11px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; padding: 10px 16px; border-radius: 2px;">
                        Facebook
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
                
                <div style="font-size: 10px; font-weight: 700; letter-spacing: 2.5px; text-transform: uppercase; color: #15803d; margin-bottom: 6px;">
                  THE MOBILE REFLECTION • STATUS &amp; STORY POSTER (9:16)
                </div>
                <h3 class="dark-heading" style="font-family: Georgia, 'Times New Roman', serif; font-size: 21px; font-weight: normal; color: #1a1a1a; margin: 0 0 16px 0;">
                  What God Builds in Secret
                </h3>

                <!-- Clean Vertical Flyer Display -->
                <div style="text-align: center; margin: 16px 0 24px 0;">
                  <img src="cid:flyer_secret_place" alt="What God Builds in Secret Poster" width="300" style="max-width: 300px; width: 100%; height: auto; border: 1px solid #e5e2da; display: block; margin: 0 auto; box-shadow: 0 6px 24px rgba(0,0,0,0.06);" />
                </div>

                <!-- Warm Intimate Reflection -->
                <div class="dark-whatsapp-box" style="background-color: #f7fcf8; border-left: 2px solid #16a34a; padding: 20px 22px; font-size: 14px; line-height: 1.75; color: #2e3b2e; margin-bottom: 22px;">
                  <p style="margin: 0 0 10px 0; font-weight: 600; color: #14532d; font-family: Georgia, 'Times New Roman', serif; font-size: 15px;">
                    Good morning my friend.
                  </p>
                  <p style="margin: 0 0 10px 0;">
                    A quiet word for your morning: “{quote_text}” When human capacity reaches its end, let your worship establish God's atmosphere.
                  </p>
                  <p style="margin: 0; font-size: 13px; color: #4b6350; font-style: italic;">
                    📖 “The Spirit Himself makes intercession for us with groanings that cannot be uttered.” — Romans 8:26
                  </p>
                </div>

                <!-- DUAL ACTION BUTTONS: WHATSAPP + INSTAGRAM STORY -->
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                  <tr>
                    <td class="mobile-stack" align="left" style="padding-bottom: 6px;">
                      <a href="{links['whatsapp']}" target="_blank" class="btn-full" style="display: inline-block; background-color: #15803d; color: #ffffff; text-decoration: none; font-size: 11px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; padding: 11px 22px; border-radius: 2px;">
                        Send via WhatsApp
                      </a>
                    </td>
                    <td class="mobile-stack" align="right" style="padding-bottom: 6px;">
                      <a href="{links['instagram_story']}" target="_blank" class="btn-full" style="display: inline-block; background-color: #c13584; color: #ffffff; text-decoration: none; font-size: 11px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; padding: 11px 22px; border-radius: 2px;">
                        Post to Instagram Story
                      </a>
                    </td>
                  </tr>
                </table>

              </div>
            </td>
          </tr>

          <!-- CLASSIC FOOTER -->
          <tr>
            <td class="content-padding dark-footer" style="padding: 32px 48px; background-color: #faf9f6; border-top: 1px solid #e5e2da; text-align: center;">
              <p class="dark-subtitle" style="font-family: Georgia, 'Times New Roman', serif; font-size: 13px; font-style: italic; color: #8c827a; margin: 0 0 8px 0; line-height: 1.5;">
                The Kingdom Journal is curated daily for personal reflection and ministry broadcast.
              </p>
              <p style="font-size: 10px; color: #a39c93; letter-spacing: 1.5px; text-transform: uppercase; margin: 0;" class="dark-subtitle">
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

def send_luxury_editorial_email(recipient: str, subject: str = None, fliers_dir: Path = None):
    load_env_file()
    fliers_dir = fliers_dir or Path(__file__).resolve().parent.parent / "reports" / "fliers"
    
    # 1. PILLAR 3: Analyze live YouTube videos to extract the best punchy line
    youtube_insight = {
        "title": "When Words Are Not Enough",
        "hook_top": "When words are not enough",
        "banner_text": "Let Your Worship Speak",
        "quote": "When words are not enough, let your worship speak.",
        "speaker": "Mercy Chinwo & Apostle Joshua Selman",
        "scripture": "Romans 8:26 • Psalm 46:10",
        "videos": []
    }
    if youtube_quote_analyzer:
        try:
            analyzed = youtube_quote_analyzer.analyze_trending_gospel_videos()
            if analyzed and analyzed.get("quote"):
                youtube_insight = analyzed
                print(f"[PIPELINE STEP 1] YouTube Analysis complete. Extracted line: '{youtube_insight['quote']}'")
        except Exception as ey:
            print(f"[PIPELINE NOTICE] YouTube analysis fallback: {ey}", file=sys.stderr)

    # 2. PILLAR 2: Generate humanized editorial essay and multi-platform captions
    engine = humanized_content_engine.HumanizedContentEngine(
        quote=youtube_insight.get("quote", "When words are not enough, let your worship speak."),
        speaker=youtube_insight.get("speaker", "Mercy Chinwo & Apostle Joshua Selman"),
        scripture=youtube_insight.get("scripture", "Romans 8:26 • Psalm 46:10"),
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
                "scripture": youtube_insight["scripture"]
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

    final_subject = subject or f"🕊️ The Kingdom Journal • {essay_data['title']} (Issue 48)"

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
        videos=youtube_insight.get("videos", [])
    )
    
    plain_text = (
        f"The Kingdom Journal • Morning Edition (Issue 48)\n\n"
        f"{essay_data['title']}\n"
        f"“{youtube_insight['quote']}” — {youtube_insight['scripture']}\n\n"
        f"Please view this email in an HTML-compatible email client to review today's artwork and pre-filled social actions (Instagram, WhatsApp, X, Threads, Facebook)."
    )

    alt_part = MIMEMultipart("alternative")
    alt_part.attach(MIMEText(plain_text, "plain", "utf-8"))
    alt_part.attach(MIMEText(html_content, "html", "utf-8"))
    msg.attach(alt_part)

    # Attach the two brand new authentic studio viral fliers
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
                speaker=youtube_insight["speaker"],
                scripture=youtube_insight["scripture"]
            )
            for lv in youtube_insight.get("videos", []):
                content_db.record_video(
                    video_id=lv.get("video_id", "live_asset"),
                    title=lv.get("title", ""),
                    channel=lv.get("channel", ""),
                    published_at=datetime.now().isoformat()
                )
            print("[DATABASE] Today's fresh YouTube insight and video assets archived in SQLite memory.")

        if catch_up_scheduler:
            catch_up_scheduler.save_state("SUCCESS")

        return True
    except Exception as e:
        print(f"[ERROR] Delivery failed: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    send_luxury_editorial_email(recipient="aondoaseerezekiel@gmail.com")
