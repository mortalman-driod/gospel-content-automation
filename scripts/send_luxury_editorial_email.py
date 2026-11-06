"""
Luxury Editorial Gospel Briefing (High-Class Edition - Issue 46)
Topic: Divine Help at Break of Day (Psalm 46:5 • Isaiah 40:31)
Bespoke editorial prose, studio-grade viral artwork, live YouTube radar, and pre-filled social actions.
"""

import email.utils
import os
import smtplib
import sys
import urllib.parse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from pathlib import Path

# Add parent path for database & state imports
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    import content_db
    import catch_up_scheduler
    import youtube_api_client
except ImportError:
    content_db = None
    catch_up_scheduler = None
    youtube_api_client = None

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
        "twitter": f"https://twitter.com/intent/tweet?text={urllib.parse.quote(captions['twitter'])}",
        "whatsapp": f"https://wa.me/?text={urllib.parse.quote(captions['whatsapp'])}",
        "threads": f"https://threads.net/intent/post?text={urllib.parse.quote(captions['threads'])}",
        "facebook": f"https://www.facebook.com/sharer/sharer.php?quote={urllib.parse.quote(captions['facebook'])}"
    }

def build_luxury_email_html(links: dict, videos: list = None) -> str:
    # Build the live listening section if YouTube videos are present
    youtube_html = ""
    if videos:
        items_html = ""
        for v in videos[:3]:
            title = v.get("title", "")
            channel = v.get("channel", "")
            items_html += f"""
            <tr>
              <td style="padding: 6px 0; font-size: 13px; line-height: 1.5; color: #44403c; border-bottom: 1px dashed #e7e5e4;">
                <span style="font-weight: 600; color: #1c1917;">{channel}</span> — <em>{title}</em>
              </td>
            </tr>"""

        youtube_html = f"""
        <!-- CURATED MORNING RADAR (Live YouTube Integration) -->
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin: 24px 0 8px 0; background-color: #faf9f6; border: 1px solid #e7e5e4; border-radius: 2px;">
          <tr>
            <td style="padding: 16px 20px;">
              <div style="font-size: 10px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #8c827a; margin-bottom: 8px;">
                TODAY'S VIRAL MINISTRATIONS • LIVE RADAR
              </div>
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                {items_html}
              </table>
            </td>
          </tr>
        </table>
        """

    return f"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="x-apple-disable-message-reformatting" />
  <title>The Kingdom Journal • Morning Edition</title>
  <!--[if mso]>
  <style type="text/css">
    table {{border-collapse:collapse;border-spacing:0;margin:0;}}
    div, td, a, span, p {{font-family: Georgia, 'Times New Roman', serif !important;}}
  </style>
  <![endif]-->
  <style type="text/css">
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
        padding: 10px !important;
      }}
      .content-padding {{
        padding: 24px 20px !important;
      }}
      .headline {{
        font-size: 26px !important;
        line-height: 1.25 !important;
      }}
      .mobile-stack {{
        display: block !important;
        width: 100% !important;
        text-align: center !important;
        margin-bottom: 12px !important;
      }}
    }}
  </style>
</head>
<body style="margin: 0; padding: 40px 0; background-color: #f7f6f2; color: #1a1a1a;">

  <!-- Outer Canvas Table -->
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #f7f6f2;">
    <tr>
      <td align="center" style="padding: 20px 10px;">
        
        <!-- Main Document Card (Outlook & Modern Responsive) -->
        <!--[if mso]>
        <table align="center" border="0" cellspacing="0" cellpadding="0" width="600">
        <tr>
        <td align="center" valign="top" width="600">
        <![endif]-->
        <table role="presentation" class="wrapper" width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width: 600px; background-color: #ffffff; border: 1px solid #e5e2da; box-shadow: 0 4px 30px rgba(0, 0, 0, 0.05); text-align: left;">
          
          <!-- BESPOKE EDITORIAL MASTHEAD -->
          <tr>
            <td class="content-padding" style="padding: 48px 48px 30px 48px; text-align: center; border-bottom: 1px solid #1a1a1a;">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                <tr>
                  <td align="center">
                    <div style="font-size: 10px; font-weight: 700; letter-spacing: 3.5px; text-transform: uppercase; color: #8c827a; margin-bottom: 14px;">
                      THE KINGDOM JOURNAL • DAILY EDITORIAL
                    </div>
                    <h1 class="headline" style="font-family: Georgia, 'Times New Roman', serif; font-size: 32px; font-weight: 400; line-height: 1.25; color: #1a1a1a; margin: 0 0 12px 0; letter-spacing: -0.5px;">
                      Divine Help at Break of Day
                    </h1>
                    <p style="font-family: Georgia, 'Times New Roman', serif; font-size: 15px; font-style: italic; color: #6e675f; margin: 0 auto 16px auto; max-width: 480px; line-height: 1.55;">
                      On the sacred mystery of God's timing, why dawn dismantles human exhaustion, and what happens when capacity runs dry.
                    </p>
                    <div style="border-top: 1px solid #f0ede6; padding-top: 10px; font-size: 10px; letter-spacing: 2px; text-transform: uppercase; color: #a39c93;">
                      Vol. IV • Issue 46 • Friday, November 6, 2026
                    </div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- THE MORNING ESSAY (NO AI BULLETS) -->
          <tr>
            <td class="content-padding" style="padding: 38px 48px 24px 48px;">
              
              <p style="font-family: Georgia, 'Times New Roman', serif; font-size: 16px; line-height: 1.8; color: #2e2b27; margin: 0 0 18px 0;">
                In the forty-sixth Psalm, the scripture records an arresting promise: <em>“God is within her, she will not fall; God will help her at break of day.”</em>
              </p>
              
              <p style="font-family: Georgia, 'Times New Roman', serif; font-size: 16px; line-height: 1.8; color: #2e2b27; margin: 0 0 18px 0;">
                Consider the quiet precision of that timing. In ancient warfare, the final stretch of the night—the fourth watch between three and six in the morning—was when fatigue peaked and human defenses were at their absolute weakest. It was the hour when striving gave way to exhaustion.
              </p>

              <p style="font-family: Georgia, 'Times New Roman', serif; font-size: 16px; line-height: 1.8; color: #2e2b27; margin: 0 0 18px 0;">
                Yet throughout biblical history, the break of day is never an afterthought. It is heaven’s appointed hour for divine reversals. The waters of the Red Sea parted as the morning watch arrived. The manna settled with the dawn dew. And before the sun fully crested over Jerusalem on the third day, the stone was already rolled away.
              </p>

              <p style="font-family: Georgia, 'Times New Roman', serif; font-size: 16px; line-height: 1.8; color: #2e2b27; margin: 0 0 24px 0;">
                Drawing from this morning's live worship ministrations led by Victoria Orenze and Apostle Joshua Selman, the spiritual truth is liberating: <strong>You do not have to panic over battles God has already scheduled for dawn.</strong> When human capacity reaches its limit, divine assistance takes over.
              </p>

              <!-- Curated Pull Quote Accent -->
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin: 28px 0; border-left: 2px solid #b45309; background-color: #faf9f6;">
                <tr>
                  <td style="padding: 16px 20px;">
                    <div style="font-family: Georgia, 'Times New Roman', serif; font-size: 17px; font-style: italic; color: #1a1a1a; line-height: 1.55;">
                      “When human capacity reaches its end, divine help begins at dawn. You do not have to panic over battles God has already scheduled for your deliverance.”
                    </div>
                    <div style="font-size: 11px; letter-spacing: 1.5px; text-transform: uppercase; color: #8c827a; margin-top: 8px;">
                      — PSALM 46:5 • VICTORIA ORENZE &amp; APOSTLE JOSHUA SELMAN
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
              <div style="border-top: 1px solid #f0ede6; padding-top: 30px;">
                
                <div style="font-size: 10px; font-weight: 700; letter-spacing: 2.5px; text-transform: uppercase; color: #a39c93; margin-bottom: 6px;">
                  THE ARTWORK • MASTER COMPOSITION (1:1)
                </div>
                <h3 style="font-family: Georgia, 'Times New Roman', serif; font-size: 21px; font-weight: normal; color: #1a1a1a; margin: 0 0 16px 0;">
                  Divine Help Begins at Dawn
                </h3>

                <!-- Native Studio Artwork Display -->
                <div style="text-align: center; margin: 16px 0 24px 0;">
                  <img src="cid:flyer_dawn" alt="Divine Help at Dawn Artwork" width="504" style="max-width: 100%; width: 100%; height: auto; border: 1px solid #e5e2da; display: block; margin: 0 auto; box-shadow: 0 6px 24px rgba(0,0,0,0.06);" />
                </div>

                <!-- Editorial Social Copy Block -->
                <div style="background-color: #faf9f6; border-left: 2px solid #1a1a1a; padding: 20px 22px; font-size: 14px; line-height: 1.75; color: #3d3935; margin-bottom: 22px;">
                  <p style="margin: 0 0 12px 0; font-family: Georgia, 'Times New Roman', serif; font-size: 15px; color: #1a1a1a;">
                    When human capacity reaches its end, divine help begins at dawn.
                  </p>
                  <p style="margin: 0 0 12px 0;">
                    Psalm 46:5 promises that <em>“God will help her at break of day.”</em> The darkest hour of the night is always the forerunner to heaven's scheduled intervention.
                  </p>
                  <p style="margin: 0 0 12px 0; font-style: italic; color: #92400e;">
                    Stop carrying into today the exhaustion of yesterday's battles. God does not sleep, and His assistance arrives right on time.
                  </p>
                  <div style="font-size: 11px; color: #8c827a; border-top: 1px solid #e5e2da; padding-top: 10px; letter-spacing: 0.5px;">
                    #DivineHelp #BreakOfDay #TheKingdomJournal #VictoriaOrenze #JoshuaSelman #MorningPrayer
                  </div>
                </div>

                <!-- Classic Action Buttons Table -->
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                  <tr>
                    <td class="mobile-stack" align="left">
                      <a href="{links['twitter']}" target="_blank" style="display: inline-block; background-color: #1a1a1a; color: #ffffff; text-decoration: none; font-size: 11px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; padding: 11px 20px; border-radius: 2px;">
                        Post to X
                      </a>
                      &nbsp;&nbsp;
                      <a href="{links['threads']}" target="_blank" style="display: inline-block; background-color: #44403c; color: #ffffff; text-decoration: none; font-size: 11px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; padding: 11px 20px; border-radius: 2px;">
                        Post on Threads
                      </a>
                    </td>
                    <td class="mobile-stack" align="right">
                      <a href="{links['facebook']}" target="_blank" style="display: inline-block; border: 1px solid #d6d3d1; color: #292524; text-decoration: none; font-size: 11px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; padding: 10px 18px; border-radius: 2px;">
                        Share to Facebook
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
              <div style="border-top: 1px solid #f0ede6; padding-top: 30px;">
                
                <div style="font-size: 10px; font-weight: 700; letter-spacing: 2.5px; text-transform: uppercase; color: #15803d; margin-bottom: 6px;">
                  THE MOBILE REFLECTION • STATUS POSTER (9:16)
                </div>
                <h3 style="font-family: Georgia, 'Times New Roman', serif; font-size: 21px; font-weight: normal; color: #1a1a1a; margin: 0 0 16px 0;">
                  What God Builds in Secret
                </h3>

                <!-- Clean Vertical Flyer Display -->
                <div style="text-align: center; margin: 16px 0 24px 0;">
                  <img src="cid:flyer_secret_place" alt="What God Builds in Secret Poster" width="300" style="max-width: 300px; width: 100%; height: auto; border: 1px solid #e5e2da; display: block; margin: 0 auto; box-shadow: 0 6px 24px rgba(0,0,0,0.06);" />
                </div>

                <!-- Warm Intimate Reflection -->
                <div style="background-color: #f7fcf8; border-left: 2px solid #16a34a; padding: 20px 22px; font-size: 14px; line-height: 1.75; color: #2e3b2e; margin-bottom: 22px;">
                  <p style="margin: 0 0 10px 0; font-weight: 600; color: #14532d; font-family: Georgia, 'Times New Roman', serif; font-size: 15px;">
                    Good morning my friend.
                  </p>
                  <p style="margin: 0 0 10px 0;">
                    A quiet word for your Friday: Never underestimate the silent seasons of your life. What God builds in secret cannot be dismantled in public.
                  </p>
                  <p style="margin: 0; font-size: 13px; color: #4b6350; font-style: italic;">
                    📖 “Those who wait upon the Lord shall renew their strength; they shall mount up with wings as eagles; they shall run, and not be weary.” — Isaiah 40:31
                  </p>
                </div>

                <!-- Pre-filled WhatsApp Button -->
                <div style="text-align: right;">
                  <a href="{links['whatsapp']}" target="_blank" style="display: inline-block; background-color: #15803d; color: #ffffff; text-decoration: none; font-size: 11px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; padding: 11px 22px; border-radius: 2px;">
                    Send via WhatsApp
                  </a>
                </div>

              </div>
            </td>
          </tr>

          <!-- CLASSIC FOOTER -->
          <tr>
            <td class="content-padding" style="padding: 32px 48px; background-color: #faf9f6; border-top: 1px solid #e5e2da; text-align: center;">
              <p style="font-family: Georgia, 'Times New Roman', serif; font-size: 13px; font-style: italic; color: #8c827a; margin: 0 0 8px 0; line-height: 1.5;">
                The Kingdom Journal is curated daily for personal reflection and ministry broadcast.
              </p>
              <p style="font-size: 10px; color: #a39c93; letter-spacing: 1.5px; text-transform: uppercase; margin: 0;">
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

def send_luxury_editorial_email(recipient: str, subject: str, fliers_dir: Path):
    load_env_file()
    
    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER", "").strip()
    smtp_pass = os.environ.get("SMTP_PASSWORD", "").strip().replace(" ", "")

    if not smtp_user or not smtp_pass:
        print("[ERROR] SMTP_USER or SMTP_PASSWORD not set in environment or .env", file=sys.stderr)
        return False

    # 1. Fetch live YouTube videos for context and archival
    live_vids = []
    if youtube_api_client:
        try:
            live_vids = youtube_api_client.fetch_trending_gospel_videos()
            print(f"[YOUTUBE RADAR] Successfully fetched {len(live_vids)} trending ministrations.")
        except Exception as ey:
            print(f"[YOUTUBE NOTICE] Falling back: {ey}", file=sys.stderr)

    msg = MIMEMultipart("related")
    msg["Subject"] = subject
    msg["From"] = f"The Kingdom Journal <{smtp_user}>"
    msg["To"] = recipient
    msg["Date"] = email.utils.formatdate(localtime=True)
    msg["Message-ID"] = email.utils.make_msgid(domain="gmail.com")

    # Fresh Humanized Captions for Issue 46 (Divine Help at Break of Day)
    captions = {
        "twitter": "When human capacity reaches its end, divine help begins at dawn.\n\nPsalm 46:5 promises that God will help her at the break of day. The darkest hour is never the conclusion; it is heaven's appointed schedule for your turnaround.\n\nRest in His timing today. 🕊️",
        "whatsapp": "Good morning my friend. A quick word for your Friday:\n\nNever underestimate the silent seasons of your life. What God builds in secret cannot be dismantled in public.\n\nPsalm 46:5 says, “God is within her, she will not fall; God will help her at break of day.” Whatever felt exhausting this week, know that divine help is already scheduled.\n\n📖 “Those who wait upon the Lord shall renew their strength.” — Isaiah 40:31\n\nHave a peaceful, favored day! Forward this to someone who needs encouragement today. ✨",
        "threads": "A thought for your Friday morning:\n\nIn ancient times, the fourth watch of the night—just before dawn—was when exhaustion was deepest and defenses were weakest.\n\nYet throughout scripture, dawn is precisely when God moves: the Red Sea parted at dawn, manna fell at dawn, and the tomb was empty at dawn.\n\nYou don't have to carry anxiety over battles God has already scheduled for your deliverance. What are you trusting Him for today?",
        "facebook": "“When human capacity reaches its end, divine help begins at dawn. You do not have to panic over battles God has already scheduled for your deliverance.” (Psalm 46:5)\n\nStop carrying the exhaustion of yesterday's striving. When your strength runs dry, divine assistance takes over. Step out today with quiet confidence in His covenant."
    }

    links = generate_social_intent_links(captions)
    html_content = build_luxury_email_html(links, videos=live_vids)
    plain_text = (
        "The Kingdom Journal • Morning Edition (Issue 46)\n\n"
        "Divine Help at Break of Day\n"
        "“When human capacity reaches its end, divine help begins at dawn. You do not have to panic over battles God has already scheduled for your deliverance.” — Psalm 46:5\n\n"
        "Please view this email in an HTML-compatible email client to review today's artwork and pre-filled social actions."
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
        print(f"[SUCCESS] Luxury Editorial Briefing successfully delivered to {recipient}")

        if content_db:
            content_db.record_dispatch(subject, recipient, "SUCCESS")
            content_db.record_quote(
                quote_text="When human capacity reaches its end, divine help begins at dawn. You do not have to panic over battles God has already scheduled for your deliverance.",
                speaker="Victoria Orenze & Apostle Joshua Selman",
                scripture="Psalm 46:5 • Isaiah 40:31"
            )
            for lv in live_vids:
                content_db.record_video(
                    video_id=lv.get("video_id", "live_asset"),
                    title=lv.get("title", ""),
                    channel=lv.get("channel", ""),
                    published_at=lv.get("published_at", "")
                )
            print("[DATABASE] Today's fresh topic and video assets archived in SQLite memory.")

        if catch_up_scheduler:
            catch_up_scheduler.save_state("SUCCESS")

        return True
    except Exception as e:
        print(f"[ERROR] Delivery failed: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    fliers_dir = Path(__file__).resolve().parent.parent / "reports" / "fliers"
    send_luxury_editorial_email(
        recipient="aondoaseerezekiel@gmail.com",
        subject="🕊️ The Kingdom Journal • Divine Help at Break of Day (Issue 46)",
        fliers_dir=fliers_dir
    )
