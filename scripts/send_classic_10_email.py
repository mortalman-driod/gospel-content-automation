"""
Classic 10/10 Editorial Gospel Media Briefing
Features:
- Timeless, luxury editorial newsletter typography (Georgia serif + clean modern sans)
- Direct platform pre-fill deep links (Twitter intent, WhatsApp wa.me, Threads intent, Facebook share)
- Elegant minimalist card design with generous whitespace and subtle golden accents
- Full integration with content_db deduplication and catch_up_scheduler
"""

import os
import smtplib
import sys
import urllib.parse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from pathlib import Path

# Add parent path for hardening imports
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
        try:
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if key and key not in os.environ:
                        os.environ[key] = val
        except Exception:
            pass

def generate_social_intent_links(captions: dict) -> dict:
    return {
        "twitter": f"https://twitter.com/intent/tweet?text={urllib.parse.quote(captions['twitter'])}",
        "whatsapp": f"https://wa.me/?text={urllib.parse.quote(captions['whatsapp'])}",
        "threads": f"https://threads.net/intent/post?text={urllib.parse.quote(captions['threads'])}",
        "facebook": f"https://www.facebook.com/sharer/sharer.php?quote={urllib.parse.quote(captions['facebook_quote'])}"
    }

def build_classic_email_html(links: dict) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Daily Kingdom Executive Briefing</title>
</head>
<body style="margin: 0; padding: 32px 0; background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #0f172a; -webkit-font-smoothing: antialiased;">

  <!-- Outer Canvas -->
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #f8fafc;">
    <tr>
      <td align="center">
        
        <!-- Classic Document Container -->
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width: 640px; background-color: #ffffff; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05); border: 1px solid #e2e8f0; margin: 0 auto; text-align: left;">
          
          <!-- CLASSIC EDITORIAL MASTHEAD -->
          <tr>
            <td style="padding: 40px 48px 24px 48px; border-bottom: 2px solid #0f172a; text-align: center;">
              <div style="font-size: 11px; font-weight: 700; letter-spacing: 3px; text-transform: uppercase; color: #64748b; margin-bottom: 8px;">
                THE DAILY KINGDOM BRIEFING
              </div>
              <h1 style="font-family: Georgia, 'Times New Roman', serif; font-size: 32px; font-weight: normal; font-style: italic; color: #0f172a; margin: 0 0 12px 0; letter-spacing: -0.5px;">
                Worship, Word &amp; Viral Media Suite
              </h1>
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="border-top: 1px solid #e2e8f0; padding-top: 10px; margin-top: 14px;">
                <tr>
                  <td align="left" style="font-size: 11px; color: #94a3b8; letter-spacing: 1px; text-transform: uppercase;">
                    Thursday, November 5, 2026
                  </td>
                  <td align="right" style="font-size: 11px; color: #94a3b8; letter-spacing: 1px; text-transform: uppercase;">
                    Curated for Ezekiel
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- LEAD STORY / OVERVIEW -->
          <tr>
            <td style="padding: 32px 48px 24px 48px;">
              <p style="font-family: Georgia, serif; font-size: 17px; line-height: 1.7; color: #334155; margin: 0 0 20px 0;">
                Today's YouTube worship analysis reveals a massive surge in deep prayer devotionals and high-energy thanksgiving. Believers worldwide are gravitating towards two anchor themes: <strong style="color: #0f172a;">uncompromising intimacy in the secret place</strong> and <strong style="color: #0f172a;">praise as spiritual warfare</strong>.
              </p>
              
              <div style="background-color: #f8fafc; border-left: 3px solid #d97706; padding: 14px 20px; margin: 24px 0;">
                <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; color: #b45309; margin-bottom: 4px;">
                  Core Revelation of the Day
                </div>
                <div style="font-family: Georgia, serif; font-size: 16px; font-style: italic; color: #0f172a; line-height: 1.5;">
                  “What is birthed in the secret place cannot be extinguished by public storms.”
                </div>
              </div>
            </td>
          </tr>

          <!-- ============================================== -->
          <!-- SECTION 1: INSTAGRAM SUITE                    -->
          <!-- ============================================== -->
          <tr>
            <td style="padding: 0 48px 36px 48px;">
              <div style="border-top: 1px solid #e2e8f0; padding-top: 28px;">
                
                <table width="100%" cellspacing="0" cellpadding="0" style="margin-bottom: 16px;">
                  <tr>
                    <td align="left">
                      <span style="font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #64748b;">
                        PLATFORM I • INSTAGRAM
                      </span>
                      <h2 style="font-family: Georgia, serif; font-size: 22px; font-weight: normal; color: #0f172a; margin: 4px 0 0 0;">
                        Visual Devotional &amp; Carousel
                      </h2>
                    </td>
                    <td align="right" valign="top">
                      <span style="font-size: 11px; background-color: #f1f5f9; color: #475569; padding: 4px 10px; border-radius: 4px; font-weight: 600;">1080 × 1080</span>
                    </td>
                  </tr>
                </table>

                <!-- Flyer Artwork Display -->
                <div style="text-align: center; margin: 20px 0 24px 0;">
                  <img src="cid:flyer_instagram" alt="Instagram Viral Flyer" style="max-width: 100%; height: auto; border-radius: 4px; border: 1px solid #e2e8f0; display: block; margin: 0 auto; box-shadow: 0 6px 18px rgba(0,0,0,0.06);" />
                  <div style="font-family: Georgia, serif; font-size: 12px; font-style: italic; color: #64748b; margin-top: 8px;">
                    Fig 1.1 — Master square graphic with textured brushstroke ribbons &amp; Holy Bible backdrop.
                  </div>
                </div>

                <!-- Clean Editorial Caption -->
                <div style="background-color: #fafafa; border: 1px solid #f1f5f9; border-radius: 4px; padding: 20px; font-size: 14px; line-height: 1.7; color: #334155; margin-bottom: 18px;">
                  <p style="margin: 0 0 12px 0; font-weight: 600; color: #0f172a;">
                    Tarrying in the secret place cannot be outsourced. 🕊️
                  </p>
                  <p style="margin: 0 0 12px 0;">
                    What you cultivate in hidden prayer produces the fruit that sustains you in public adversity.
                  </p>
                  <p style="margin: 0 0 12px 0;">
                    In an age of relentless noise, it's tempting to look for quick public breakthroughs. But spiritual authority and discernment aren't manufactured on stage—they are forged in quiet communion when no one is watching.
                  </p>
                  <p style="margin: 0 0 14px 0; font-style: italic; color: #b45309;">
                    Build your altar first. Give God your first 15 unhurried minutes today and let Him anchor your soul.
                  </p>
                  <div style="font-size: 12px; color: #94a3b8; border-top: 1px solid #eaeaea; padding-top: 10px;">
                    #SecretPlace #PrayerAltar #DailyDevotional #DunsinOyekan #ApostleJoshuaSelman #FaithOverFear #KingdomMindset
                  </div>
                </div>

                <!-- Action Button -->
                <div style="text-align: right;">
                  <a href="https://instagram.com" style="display: inline-block; background-color: #0f172a; color: #ffffff; text-decoration: none; font-size: 12px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; padding: 10px 20px; border-radius: 2px;">
                    Open Instagram
                  </a>
                </div>

              </div>
            </td>
          </tr>

          <!-- ============================================== -->
          <!-- SECTION 2: WHATSAPP DIRECT SHARE              -->
          <!-- ============================================== -->
          <tr>
            <td style="padding: 0 48px 36px 48px;">
              <div style="border-top: 1px solid #e2e8f0; padding-top: 28px;">
                
                <table width="100%" cellspacing="0" cellpadding="0" style="margin-bottom: 16px;">
                  <tr>
                    <td align="left">
                      <span style="font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #16a34a;">
                        PLATFORM II • WHATSAPP
                      </span>
                      <h2 style="font-family: Georgia, serif; font-size: 22px; font-weight: normal; color: #0f172a; margin: 4px 0 0 0;">
                        Daily Status &amp; Broadcast
                      </h2>
                    </td>
                    <td align="right" valign="top">
                      <span style="font-size: 11px; background-color: #f1f5f9; color: #475569; padding: 4px 10px; border-radius: 4px; font-weight: 600;">9:16 Vertical</span>
                    </td>
                  </tr>
                </table>

                <!-- Flyer Artwork Display -->
                <div style="text-align: center; margin: 20px 0 24px 0;">
                  <img src="cid:flyer_whatsapp" alt="WhatsApp Status Flyer" style="max-width: 280px; height: auto; border-radius: 4px; border: 1px solid #e2e8f0; display: block; margin: 0 auto; box-shadow: 0 6px 18px rgba(0,0,0,0.06);" />
                  <div style="font-family: Georgia, serif; font-size: 12px; font-style: italic; color: #64748b; margin-top: 8px;">
                    Fig 1.2 — Full-screen mobile poster optimized for WhatsApp Status &amp; Stories.
                  </div>
                </div>

                <!-- Clean Broadcast Message Box -->
                <div style="background-color: #fafafa; border: 1px solid #f1f5f9; border-radius: 4px; padding: 20px; font-size: 14px; line-height: 1.7; color: #334155; margin-bottom: 18px;">
                  <p style="margin: 0 0 8px 0; font-weight: 600; color: #0f172a;">
                    🕊️ MORNING WORD FOR TODAY
                  </p>
                  <p style="margin: 0 0 8px 0; font-family: Georgia, serif; font-style: italic;">
                    “Praise is not just an emotion — IT IS YOUR STRATEGIC WEAPON.”
                  </p>
                  <p style="margin: 0 0 10px 0;">
                    When battles rage, thanksgiving is how you enforce kingdom victory. Even in uncertainty, choose to thank God first (Acts 16:25).
                  </p>
                  <p style="margin: 0; font-size: 13px; color: #64748b;">
                    📖 <em>“He who dwells in the secret place of the Most High shall abide under the shadow of the Almighty.”</em> — Psalm 91:1
                  </p>
                </div>

                <!-- PRE-FILLED WHATSAPP DIRECT SHARE BUTTON -->
                <div style="text-align: right;">
                  <a href="{links['whatsapp']}" style="display: inline-block; background-color: #16a34a; color: #ffffff; text-decoration: none; font-size: 12px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; padding: 10px 20px; border-radius: 2px;">
                    ⚡ Share to WhatsApp (Pre-Filled)
                  </a>
                </div>

              </div>
            </td>
          </tr>

          <!-- ============================================== -->
          <!-- SECTION 3: TWITTER / X DIRECT COMPOSE         -->
          <!-- ============================================== -->
          <tr>
            <td style="padding: 0 48px 36px 48px;">
              <div style="border-top: 1px solid #e2e8f0; padding-top: 28px;">
                
                <table width="100%" cellspacing="0" cellpadding="0" style="margin-bottom: 16px;">
                  <tr>
                    <td align="left">
                      <span style="font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #64748b;">
                        PLATFORM III • TWITTER / X
                      </span>
                      <h2 style="font-family: Georgia, serif; font-size: 22px; font-weight: normal; color: #0f172a; margin: 4px 0 0 0;">
                        High-Velocity Insight Thread
                      </h2>
                    </td>
                    <td align="right" valign="top">
                      <span style="font-size: 11px; background-color: #f1f5f9; color: #475569; padding: 4px 10px; border-radius: 4px; font-weight: 600;">Thread Draft</span>
                    </td>
                  </tr>
                </table>

                <!-- Flyer Artwork Display -->
                <div style="text-align: center; margin: 20px 0 24px 0;">
                  <img src="cid:flyer_twitter" alt="Twitter Flyer" style="max-width: 100%; height: auto; border-radius: 4px; border: 1px solid #e2e8f0; display: block; margin: 0 auto; box-shadow: 0 6px 18px rgba(0,0,0,0.06);" />
                </div>

                <!-- Thread Preview Box -->
                <div style="background-color: #fafafa; border: 1px solid #f1f5f9; border-radius: 4px; padding: 20px; font-size: 14px; line-height: 1.7; color: #334155; margin-bottom: 18px;">
                  <p style="margin: 0 0 10px 0;">
                    Most people pray for breakthrough.<br>
                    Few prepare their hearts to carry it.<br><br>
                    Here are 3 spiritual principles drawn from today's viral worship ministrations:
                  </p>
                  <p style="margin: 0 0 6px 0;"><strong>1/</strong> Praise is not an emotional reaction—it's a tactical weapon.</p>
                  <p style="margin: 0 0 6px 0;"><strong>2/</strong> Tarrying in the secret place cannot be outsourced.</p>
                  <p style="margin: 0;"><strong>3/</strong> Surrender always precedes authority.</p>
                </div>

                <!-- PRE-FILLED TWITTER / X DIRECT COMPOSE BUTTON -->
                <div style="text-align: right;">
                  <a href="{links['twitter']}" style="display: inline-block; background-color: #000000; color: #ffffff; text-decoration: none; font-size: 12px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; padding: 10px 20px; border-radius: 2px;">
                    ⚡ Post to X (Pre-Filled)
                  </a>
                </div>

              </div>
            </td>
          </tr>

          <!-- ============================================== -->
          <!-- SECTION 4: THREADS & FACEBOOK DIRECT SHARE    -->
          <!-- ============================================== -->
          <tr>
            <td style="padding: 0 48px 40px 48px;">
              <div style="border-top: 1px solid #e2e8f0; padding-top: 28px;">
                
                <span style="font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #64748b;">
                  PLATFORMS IV &amp; V • THREADS &amp; FACEBOOK
                </span>
                <h2 style="font-family: Georgia, serif; font-size: 22px; font-weight: normal; color: #0f172a; margin: 4px 0 16px 0;">
                  Conversational Thought Leadership
                </h2>

                <div style="background-color: #fafafa; border: 1px solid #f1f5f9; border-radius: 4px; padding: 20px; font-size: 14px; line-height: 1.7; color: #334155; margin-bottom: 20px;">
                  <p style="margin: 0 0 10px 0;">
                    A quick thought after listening to recent worship sets from Dunsin Oyekan and Apostle Selman:
                  </p>
                  <p style="margin: 0 0 10px 0; font-family: Georgia, serif; font-style: italic; color: #0f172a;">
                    You really can't pour from a cup that has run dry. Too many treat their prayer life like an emergency room rather than a daily dining table.
                  </p>
                  <p style="margin: 0;">
                    What shifts your entire week is moving from panic-praying to unhurried dwelling. Ten quiet minutes of thanksgiving before touching your phone does more for your mental clarity than an hour of scrolling.
                  </p>
                </div>

                <!-- PRE-FILLED DUAL DIRECT SHARE BUTTONS -->
                <table width="100%" cellspacing="0" cellpadding="0">
                  <tr>
                    <td align="left">
                      <a href="{links['threads']}" style="display: inline-block; background-color: #18181b; color: #ffffff; text-decoration: none; font-size: 12px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; padding: 10px 18px; border-radius: 2px;">
                        ⚡ Post on Threads (Pre-Filled)
                      </a>
                    </td>
                    <td align="right">
                      <a href="{links['facebook']}" style="display: inline-block; background-color: #1d4ed8; color: #ffffff; text-decoration: none; font-size: 12px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; padding: 10px 18px; border-radius: 2px;">
                        ⚡ Share on Facebook (Pre-Filled)
                      </a>
                    </td>
                  </tr>
                </table>

              </div>
            </td>
          </tr>

          <!-- CLASSIC EDITORIAL FOOTER -->
          <tr>
            <td style="padding: 32px 48px; background-color: #fafafa; border-top: 1px solid #e2e8f0; text-align: center;">
              <div style="font-family: Georgia, serif; font-size: 13px; font-style: italic; color: #64748b; margin-bottom: 8px;">
                Curated daily at 7:00 AM • Kingdom Creative Media
              </div>
              <div style="font-size: 11px; color: #94a3b8; letter-spacing: 1px; text-transform: uppercase;">
                Personal Media Dispatch for aondoaseerezekiel@gmail.com
              </div>
            </td>
          </tr>

        </table>

      </td>
    </tr>
  </table>

</body>
</html>"""

def send_classic_editorial_email(recipient: str, subject: str, fliers_dir: Path):
    load_env_file()
    
    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER", "").strip()
    smtp_pass = os.environ.get("SMTP_PASSWORD", "").strip().replace(" ", "")

    if not smtp_user or not smtp_pass:
        print("[ERROR] SMTP_USER or SMTP_PASSWORD not set in environment or .env", file=sys.stderr)
        return False

    msg = MIMEMultipart("related")
    msg["Subject"] = subject
    msg["From"] = f"Kingdom Creative Media <{smtp_user}>"
    msg["To"] = recipient

    # Content for intent URLs
    captions = {
        "twitter": "Most people pray for breakthrough. Few prepare their hearts to carry it.\n\n3 spiritual principles drawn from today's viral worship ministrations:\n\n1/ Praise is not an emotion—it's a tactical weapon.\n2/ Tarrying in the secret place cannot be outsourced.\n3/ Surrender precedes authority.\n\nBuild your altar first. 🙏",
        "whatsapp": "🕊️ *MORNING WORD FOR TODAY*\n\n*“Praise is not just an emotion — IT IS YOUR STRATEGIC WEAPON.”*\n\nWhen battles rage, thanksgiving is how you enforce kingdom victory. Even in uncertainty, choose to thank God first (Acts 16:25).\n\n📖 *Scripture:* “He who dwells in the secret place of the Most High shall abide under the shadow of the Almighty.” — Psalm 91:1\n\nForward this to 3 people who need strength today! ✨",
        "threads": "A quick thought after listening to recent worship sets from Dunsin Oyekan and Apostle Selman:\n\nYou really can't pour from a cup that has run dry. Too many treat their prayer life like an emergency room rather than a daily dining table.\n\nWhat shifts your entire week is moving from panic-praying to unhurried dwelling. 10 quiet minutes before touching your phone does more for your mental clarity than an hour of scrolling. How do you protect your peace?",
        "facebook_quote": "“What is birthed in the secret place cannot be extinguished by public storms.” In our fast-paced lives, spiritual authority and peace don't come from striving; they flow from surrender. Build your altar first."
    }

    links = generate_social_intent_links(captions)
    html_content = build_classic_email_html(links)
    plain_text = "The Daily Kingdom Briefing. Please open in an HTML-compatible email client to review the full editorial suite and pre-filled publishing links."

    alt_part = MIMEMultipart("alternative")
    alt_part.attach(MIMEText(plain_text, "plain", "utf-8"))
    alt_part.attach(MIMEText(html_content, "html", "utf-8"))
    msg.attach(alt_part)

    # Attach images matching CIDs
    attachments = [
        ("flyer_instagram", fliers_dir / "flyer_instagram_viral.jpg"),
        ("flyer_whatsapp", fliers_dir / "flyer_whatsapp_status_viral.jpg"),
        ("flyer_twitter", fliers_dir / "flyer_twitter_threads_viral.jpg")
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
            print(f"[WARNING] Flyer image not found on disk: {img_file}", file=sys.stderr)

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=45) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, [recipient], msg.as_string())
        print(f"[SUCCESS] Classic Editorial Briefing successfully delivered to {recipient}")

        if content_db:
            content_db.record_dispatch(subject, recipient, "SUCCESS")
            if youtube_api_client:
                live_vids = youtube_api_client.fetch_trending_gospel_videos()
                for lv in live_vids:
                    content_db.record_video(
                        video_id=lv.get("video_id", "live_vid"),
                        title=lv.get("title", ""),
                        channel=lv.get("channel", ""),
                        published_at=lv.get("published_at", "")
                    )
                print(f"[YOUTUBE INTEGRATION] {len(live_vids)} live video assets archived in database.")
        if catch_up_scheduler:
            catch_up_scheduler.save_state("SUCCESS")

        return True
    except Exception as e:
        print(f"[ERROR] Delivery failed: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    fliers_dir = Path(__file__).resolve().parent.parent / "reports" / "fliers"
    send_classic_editorial_email(
        recipient="aondoaseerezekiel@gmail.com",
        subject="🕊️ The Daily Kingdom Briefing • Issue No. 042 (Editorial Edition)",
        fliers_dir=fliers_dir
    )
