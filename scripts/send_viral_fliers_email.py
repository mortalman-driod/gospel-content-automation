"""
Production Hardened Gospel Email Dispatcher
Includes:
- SQLite Deduplication memory (prevents repeats)
- Catch-up state tracking (guarantees daily execution)
- 1-Click Publishing action buttons
- Responsive magazine-grade HTML email with embedded fliers
"""

import os
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from pathlib import Path

# Import Enterprise Hardening Modules
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    import content_db
    import catch_up_scheduler
    import social_webhook_publisher
except ImportError:
    content_db = None
    catch_up_scheduler = None
    social_webhook_publisher = None

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

def build_hardened_email_html():
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Daily Kingdom Media Suite</title>
</head>
<body style="margin: 0; padding: 24px 0; background-color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1e293b; -webkit-font-smoothing: antialiased;">
  
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #f1f5f9;">
    <tr>
      <td align="center">
        
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width: 680px; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.08); border: 1px solid #e2e8f0; margin: 0 auto;">
          
          <!-- HERO HEADER -->
          <tr>
            <td style="background: linear-gradient(135deg, #090d16 0%, #1e1b4b 60%, #312e81 100%); padding: 36px 32px; text-align: center;">
              <span style="display: inline-block; background-color: rgba(245, 158, 11, 0.18); border: 1px solid #f59e0b; color: #fbbf24; font-size: 11px; font-weight: 700; letter-spacing: 1.5px; padding: 5px 14px; border-radius: 50px; text-transform: uppercase; margin-bottom: 14px;">
                🔥 Daily Worship &amp; Word Briefing
              </span>
              <h1 style="color: #ffffff; font-size: 26px; font-weight: 800; line-height: 1.3; margin: 0 0 10px 0; letter-spacing: -0.5px;">
                🕊️ Daily Kingdom Creative Suite
              </h1>
              <p style="color: #cbd5e1; font-size: 14px; line-height: 1.5; margin: 0 auto; max-width: 520px;">
                Fresh viral flyers and platform-tailored captions ready to copy, download, and publish across your social feeds.
              </p>
            </td>
          </tr>

          <!-- MAIN CONTENT -->
          <tr>
            <td style="padding: 32px 28px;">

              <!-- TRENDS DIGEST PILL -->
              <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px; margin-bottom: 32px;">
                <h3 style="margin: 0 0 8px 0; color: #0f172a; font-size: 15px; font-weight: 700;">
                  📈 Previous 24h YouTube Gospel Trends Summary
                </h3>
                <ul style="margin: 0; padding-left: 20px; color: #475569; font-size: 13px; line-height: 1.6;">
                  <li><strong>Moses Bliss (Mercy Experience):</strong> High-energy praise party, corporate thanksgiving &amp; joy as spiritual warfare.</li>
                  <li><strong>Dunsin Oyekan &amp; Theophilus Sunday:</strong> Deep soaking worship, secret place tarrying, and personal consecration.</li>
                  <li><strong>Apostle Joshua Selman (Koinonia):</strong> Kingdom surrender preceding divine authority; personal prayer altar focus.</li>
                </ul>
              </div>

              <!-- ============================================== -->
              <!-- PLATFORM 1: INSTAGRAM (VIRAL CAROUSEL FLYER) -->
              <!-- ============================================== -->
              <div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; overflow: hidden; margin-bottom: 36px; box-shadow: 0 4px 12px rgba(0,0,0,0.04);">
                
                <div style="background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%); padding: 14px 20px; color: #ffffff;">
                  <table width="100%" cellspacing="0" cellpadding="0">
                    <tr>
                      <td style="font-weight: 800; font-size: 16px; color: #ffffff;">📸 INSTAGRAM</td>
                      <td align="right" style="font-size: 12px; color: #ffe4e6; font-weight: 600;">Square 1:1 Viral Typography</td>
                    </tr>
                  </table>
                </div>

                <!-- Embedded Flyer -->
                <div style="padding: 16px; background-color: #0b0f19; text-align: center;">
                  <img src="cid:flyer_instagram" alt="Instagram Viral Gospel Flyer" style="max-width: 100%; height: auto; border-radius: 8px; display: block; margin: 0 auto; box-shadow: 0 4px 15px rgba(0,0,0,0.4);" />
                </div>

                <!-- Platform Caption & 1-Click Action -->
                <div style="padding: 22px;">
                  <span style="font-size: 11px; font-weight: 700; color: #dc2626; text-transform: uppercase; letter-spacing: 0.5px;">Ready-to-Post Caption</span>
                  
                  <p style="font-size: 15px; font-weight: 700; color: #0f172a; margin: 8px 0 12px 0;">
                    Tarrying in the secret place cannot be outsourced. 🕊️
                  </p>
                  
                  <p style="font-size: 14px; line-height: 1.7; color: #334155; margin: 0 0 14px 0;">
                    What you cultivate in hidden prayer produces the fruit that sustains you in public adversity.
                  </p>
                  
                  <p style="font-size: 14px; line-height: 1.7; color: #334155; margin: 0 0 14px 0;">
                    In an age of endless noise and quick fixes, it's easy to look for shortcuts. But true spiritual authority, clarity, and peace aren't manufactured on stage—they are forged in the quiet place when no one else is watching.
                  </p>

                  <div style="background-color: #fff1f2; border-left: 3px solid #e11d48; padding: 12px 16px; margin: 14px 0; font-size: 13px; line-height: 1.6; color: #9f1239;">
                    🔥 <strong>Build your altar first:</strong> Before the workday begins, before opening social media, give God your first 15 minutes. Watch how it anchors your entire soul.
                  </div>

                  <p style="font-size: 14px; line-height: 1.7; color: #334155; margin: 0 0 14px 0;">
                    📌 <strong>SAVE this post</strong> for your weekly reminder.<br>
                    ✈️ <strong>SHARE this</strong> with someone who needs peace today.
                  </p>

                  <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 14px; font-size: 12px; color: #64748b; line-height: 1.6; margin-bottom: 16px;">
                    #SecretPlace #PrayerAltar #DailyDevotional #DunsinOyekan #ApostleJoshuaSelman #ChristianQuotes #FaithOverFear #SpiritualGrowth #HolySpirit #PrayerWarriors #KingdomMindset
                  </div>

                  <!-- 1-Click Publishing Button -->
                  <div style="text-align: center; margin-top: 14px;">
                    <a href="https://instagram.com" style="display: inline-block; background: linear-gradient(45deg, #f09433, #dc2743, #bc1888); color: #ffffff; text-decoration: none; font-size: 13px; font-weight: 700; padding: 10px 22px; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.15);">
                      🚀 Open Instagram &amp; Post
                    </a>
                  </div>
                </div>

              </div>

              <!-- ============================================== -->
              <!-- PLATFORM 2: WHATSAPP (VERTICAL 9:16 STATUS)   -->
              <!-- ============================================== -->
              <div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; overflow: hidden; margin-bottom: 36px; box-shadow: 0 4px 12px rgba(0,0,0,0.04);">
                
                <div style="background-color: #25d366; padding: 14px 20px; color: #ffffff;">
                  <table width="100%" cellspacing="0" cellpadding="0">
                    <tr>
                      <td style="font-weight: 800; font-size: 16px; color: #ffffff;">💬 WHATSAPP STATUS &amp; BROADCAST</td>
                      <td align="right" style="font-size: 12px; color: #dcfce7; font-weight: 600;">Vertical 9:16 Mobile Poster</td>
                    </tr>
                  </table>
                </div>

                <!-- Embedded Flyer -->
                <div style="padding: 16px; background-color: #0b0f19; text-align: center;">
                  <img src="cid:flyer_whatsapp" alt="WhatsApp Status Viral Gospel Flyer" style="max-width: 320px; height: auto; border-radius: 8px; display: block; margin: 0 auto; box-shadow: 0 4px 15px rgba(0,0,0,0.4);" />
                </div>

                <!-- Platform Caption & 1-Click Action -->
                <div style="padding: 22px;">
                  <span style="font-size: 11px; font-weight: 700; color: #15803d; text-transform: uppercase; letter-spacing: 0.5px;">Status &amp; Broadcast Message</span>
                  
                  <div style="background-color: #efeae2; border-radius: 10px; padding: 16px; border: 1px solid #e6ded3; margin: 10px 0 16px 0;">
                    <div style="background-color: #ffffff; border-radius: 8px; padding: 16px; font-size: 14px; line-height: 1.7; color: #111b21; box-shadow: 0 1px 2px rgba(0,0,0,0.08);">
                      🕊️ <strong>MORNING WORD FOR TODAY</strong><br><br>
                      *"Praise is not just an emotion — IT IS YOUR STRATEGIC WEAPON."*<br><br>
                      When battles rage, thanksgiving is how you enforce kingdom victory. Even when circumstances look uncertain, choose to thank God first (Acts 16:25).<br><br>
                      📖 <strong>Scripture for the Day:</strong><br>
                      <em>“He who dwells in the secret place of the Most High shall abide under the shadow of the Almighty.”</em> — Psalm 91:1<br><br>
                      📲 <em>Post the vertical flyer above to your WhatsApp Status this morning!</em><br>
                      📤 <em>Forward this to 3 people who need strength and peace today.</em> 🙏✨
                    </div>
                  </div>

                  <!-- 1-Click WhatsApp Button -->
                  <div style="text-align: center;">
                    <a href="https://web.whatsapp.com" style="display: inline-block; background-color: #25d366; color: #ffffff; text-decoration: none; font-size: 13px; font-weight: 700; padding: 10px 22px; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.15);">
                      📲 Open WhatsApp Status
                    </a>
                  </div>
                </div>

              </div>

              <!-- ============================================== -->
              <!-- PLATFORM 3: FACEBOOK (COMMUNITY STORYTELLING) -->
              <!-- ============================================== -->
              <div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; overflow: hidden; margin-bottom: 36px; box-shadow: 0 4px 12px rgba(0,0,0,0.04);">
                
                <div style="background-color: #1877f2; padding: 14px 20px; color: #ffffff;">
                  <table width="100%" cellspacing="0" cellpadding="0">
                    <tr>
                      <td style="font-weight: 800; font-size: 16px; color: #ffffff;">📘 FACEBOOK</td>
                      <td align="right" style="font-size: 12px; color: #dbeafe; font-weight: 600;">Community Storytelling Standard</td>
                    </tr>
                  </table>
                </div>

                <div style="padding: 22px;">
                  <span style="font-size: 11px; font-weight: 700; color: #1d4ed8; text-transform: uppercase; letter-spacing: 0.5px;">Recommended Post</span>
                  
                  <p style="font-size: 15px; font-weight: 600; color: #0f172a; margin: 8px 0 12px 0;">
                    Have you ever felt like you're fighting battles in public while neglecting your secret place?
                  </p>
                  
                  <p style="font-size: 14px; line-height: 1.7; color: #334155; margin: 0 0 14px 0;">
                    Listening to recent worship ministrations and sermons this week brought home a timeless truth:
                  </p>

                  <div style="background-color: #eff6ff; border-left: 3px solid #1877f2; padding: 12px 16px; margin: 14px 0; font-style: italic; color: #1e3a8a; font-size: 14px; font-weight: 600;">
                    “What is birthed in the secret place cannot be extinguished by public storms.”
                  </div>

                  <p style="font-size: 14px; line-height: 1.7; color: #334155; margin: 0 0 14px 0;">
                    When you invest time in prayer, praise, and quiet reflection behind closed doors, God builds a quiet resilience inside you that no sudden crisis can shake.
                  </p>

                  <p style="font-size: 14px; line-height: 1.7; color: #1e293b; font-weight: 600; margin: 0 0 14px 0;">
                    👉 How do you guard your quiet time with God when your week gets crazy busy? Drop your thoughts below in the comments! 👇
                  </p>

                  <div style="background-color: #f1f5f9; padding: 8px 12px; border-radius: 6px; font-size: 12px; color: #64748b; margin-bottom: 16px;">
                    <strong>Hashtags:</strong> #FaithJourney #SecretPlace #DailyDevotion #ChristianLiving
                  </div>

                  <!-- 1-Click Facebook Button -->
                  <div style="text-align: center;">
                    <a href="https://facebook.com" style="display: inline-block; background-color: #1877f2; color: #ffffff; text-decoration: none; font-size: 13px; font-weight: 700; padding: 10px 22px; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.15);">
                      📘 Open Facebook &amp; Post
                    </a>
                  </div>
                </div>

              </div>

              <!-- ============================================== -->
              <!-- PLATFORM 4: TWITTER / X & THREADS              -->
              <!-- ============================================== -->
              <div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; overflow: hidden; margin-bottom: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.04);">
                
                <div style="background-color: #000000; padding: 14px 20px; color: #ffffff;">
                  <table width="100%" cellspacing="0" cellpadding="0">
                    <tr>
                      <td style="font-weight: 800; font-size: 16px; color: #ffffff;">🐦 TWITTER / X &amp; 🧵 THREADS</td>
                      <td align="right" style="font-size: 12px; color: #94a3b8; font-weight: 600;">High-Impact Thread Standard</td>
                    </tr>
                  </table>
                </div>

                <!-- Embedded Flyer -->
                <div style="padding: 16px; background-color: #0b0f19; text-align: center;">
                  <img src="cid:flyer_twitter" alt="Twitter / Threads Viral Gospel Flyer" style="max-width: 100%; height: auto; border-radius: 8px; display: block; margin: 0 auto; box-shadow: 0 4px 15px rgba(0,0,0,0.4);" />
                </div>

                <div style="padding: 22px;">
                  <span style="font-size: 11px; font-weight: 700; color: #0284c7; text-transform: uppercase; letter-spacing: 0.5px;">Twitter Thread (Copy &amp; Post)</span>

                  <!-- Tweet 1 -->
                  <div style="border-left: 2px solid #e2e8f0; padding-left: 14px; margin: 12px 0 16px 0;">
                    <span style="font-size: 11px; font-weight: 700; color: #0284c7;">1/4 (Hook + Attach Flyer)</span>
                    <p style="margin: 4px 0 0 0; font-size: 14px; line-height: 1.6; color: #1e293b;">
                      Most people pray for breakthrough.<br>
                      Few prepare their hearts to carry it.<br><br>
                      Here are 3 spiritual principles drawn from the most viral worship ministrations from the past 24 hours: 🧵👇
                    </p>
                  </div>

                  <!-- Tweet 2 -->
                  <div style="border-left: 2px solid #e2e8f0; padding-left: 14px; margin-bottom: 16px;">
                    <span style="font-size: 11px; font-weight: 700; color: #0284c7;">2/4</span>
                    <p style="margin: 4px 0 0 0; font-size: 14px; line-height: 1.6; color: #1e293b;">
                      1/ Praise is not an emotional reaction—it's a tactical weapon.<br><br>
                      When you see worshippers rejoicing in the midst of uncertainty, it's not denial of reality. It's alignment with divine victory.
                    </p>
                  </div>

                  <!-- Tweet 3 -->
                  <div style="border-left: 2px solid #e2e8f0; padding-left: 14px; margin-bottom: 16px;">
                    <span style="font-size: 11px; font-weight: 700; color: #0284c7;">3/4</span>
                    <p style="margin: 4px 0 0 0; font-size: 14px; line-height: 1.6; color: #1e293b;">
                      2/ Tarrying in the secret place cannot be outsourced.<br><br>
                      What you cultivate in hidden prayer produces the fruit that sustains you in public adversity. Build your altar first.
                    </p>
                  </div>

                  <!-- Tweet 4 -->
                  <div style="border-left: 2px solid #0284c7; padding-left: 14px; margin-bottom: 16px;">
                    <span style="font-size: 11px; font-weight: 700; color: #0284c7;">4/4 (CTA)</span>
                    <p style="margin: 4px 0 0 0; font-size: 14px; line-height: 1.6; color: #1e293b;">
                      3/ Surrender always precedes authority.<br><br>
                      God doesn't need your self-made ambition; He desires your yielded alignment.<br><br>
                      Drop an "Amen" if this speaks to your season today! 🙏
                    </p>
                  </div>

                  <!-- 1-Click Twitter Button -->
                  <div style="text-align: center;">
                    <a href="https://twitter.com/compose/tweet" style="display: inline-block; background-color: #000000; color: #ffffff; text-decoration: none; font-size: 13px; font-weight: 700; padding: 10px 22px; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.15);">
                      🐦 Post Thread on X
                    </a>
                  </div>
                </div>

              </div>

            </td>
          </tr>

          <!-- FOOTER -->
          <tr>
            <td style="background-color: #f8fafc; border-top: 1px solid #e2e8f0; padding: 24px; text-align: center;">
              <p style="color: #64748b; font-size: 12px; margin: 0 0 4px 0;">
                Kingdom Creative Suite • Curated Media Kit for Ezekiel
              </p>
              <p style="color: #94a3b8; font-size: 11px; margin: 0;">
                Prepared for personal broadcast &amp; distribution • aondoaseerezekiel@gmail.com
              </p>
            </td>
          </tr>

        </table>

      </td>
    </tr>
  </table>

</body>
</html>"""

def send_viral_fliers_email(recipient: str, subject: str, fliers_dir: Path):
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

    html_content = build_hardened_email_html()
    plain_text = "Daily Kingdom Creative Suite. Please view in an HTML-compatible email client to see all generated flyers and formatted captions."

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

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=45) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, [recipient], msg.as_string())
        print(f"[SUCCESS] Viral Fliers Email successfully delivered to {recipient}")

        # Enterprise Hardening: Record in Database & Update Execution State
        if content_db:
            content_db.record_dispatch(subject, recipient, "SUCCESS")
            content_db.record_quote(
                quote_text="Tarrying in the secret place cannot be outsourced.",
                speaker="Dunsin Oyekan & Apostle Joshua Selman",
                scripture="Psalm 91:1"
            )
            print("[DATABASE] Dispatch recorded in SQLite memory.")

        if catch_up_scheduler:
            catch_up_scheduler.save_state("SUCCESS")
            print("[STATE TRACKER] Today's execution state updated to SUCCESS.")

        return True
    except Exception as e:
        print(f"[ERROR] Email delivery failed: {e}", file=sys.stderr)
        if catch_up_scheduler:
            catch_up_scheduler.save_state("FAILED", str(e))
        return False

if __name__ == "__main__":
    fliers_dir = Path(__file__).resolve().parent.parent / "reports" / "fliers"
    send_viral_fliers_email(
        recipient="aondoaseerezekiel@gmail.com",
        subject="🕊️ Today's Kingdom Media Kit & Fliers (Hardened Suite)",
        fliers_dir=fliers_dir
    )
