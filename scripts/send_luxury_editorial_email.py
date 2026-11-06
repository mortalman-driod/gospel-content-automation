"""
Luxury Editorial Gospel Briefing (High-Class Edition)
Completely removes all robotic AI templates (no '1/ 2/ 3/' lists, no formulaic bullet points).
Formats daily worship insights with bespoke editorial typography and pre-filled social actions.
"""

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
    from hybrid_flier_canvas import render_hybrid_flier
except ImportError:
    content_db = None
    catch_up_scheduler = None
    youtube_api_client = None
    render_hybrid_flier = None

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

def ensure_flyers(fliers_dir: Path):
    """Ensures required high-resolution flyers exist, rendering via canvas if missing."""
    fliers_dir.mkdir(parents=True, exist_ok=True)
    base_art = fliers_dir / "gemini_gospel_flyer.jpg"
    sq_path = fliers_dir / "flyer_praise_square.jpg"
    vert_path = fliers_dir / "flyer_praise_whatsapp.jpg"

    if render_hybrid_flier and base_art.is_file():
        if not sq_path.is_file():
            render_hybrid_flier(
                background_art=base_art,
                output_path=sq_path,
                hook_top="Put on the Garment of",
                highlight_word="PRAISE",
                body_quote="Praise is not an emotional reaction to an easy season; it is the spiritual posture that disarms heaviness.",
                speaker="Nathaniel Bassey & Apostle Joshua Selman",
                scripture="Isaiah 61:3",
                callout_badge="Joy is a spiritual weapon.",
                target_dim=(1080, 1080)
            )
        if not vert_path.is_file():
            render_hybrid_flier(
                background_art=base_art,
                output_path=vert_path,
                hook_top="Exchange Heaviness for",
                highlight_word="DIVINE JOY",
                body_quote="When praise precedes the breakthrough, faith ceases to be a wish—it becomes an unstoppable kingdom verdict.",
                speaker="Apostle Joshua Selman • Nathaniel Bassey",
                scripture="Psalm 30:11-12",
                callout_badge="Walk in victory today.",
                target_dim=(1080, 1920)
            )

def generate_social_intent_links(captions: dict) -> dict:
    return {
        "twitter": f"https://twitter.com/intent/tweet?text={urllib.parse.quote(captions['twitter'])}",
        "whatsapp": f"https://wa.me/?text={urllib.parse.quote(captions['whatsapp'])}",
        "threads": f"https://threads.net/intent/post?text={urllib.parse.quote(captions['threads'])}",
        "facebook": f"https://www.facebook.com/sharer/sharer.php?quote={urllib.parse.quote(captions['facebook'])}"
    }

def build_luxury_email_html(links: dict) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>The Kingdom Journal • Morning Edition</title>
</head>
<body style="margin: 0; padding: 40px 0; background-color: #fafaf9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1c1917; -webkit-font-smoothing: antialiased;">

  <!-- Outer Canvas -->
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #fafaf9;">
    <tr>
      <td align="center">
        
        <!-- Classic Document Container -->
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width: 600px; background-color: #ffffff; border-radius: 2px; overflow: hidden; box-shadow: 0 4px 25px rgba(0, 0, 0, 0.04); border: 1px solid #e7e5e4; margin: 0 auto; text-align: left;">
          
          <!-- BESPOKE EDITORIAL MASTHEAD -->
          <tr>
            <td style="padding: 44px 44px 28px 44px; text-align: center; border-bottom: 1px solid #1c1917;">
              <div style="font-size: 10px; font-weight: 700; letter-spacing: 3px; text-transform: uppercase; color: #78716c; margin-bottom: 12px;">
                THE KINGDOM JOURNAL • DAILY EDITORIAL
              </div>
              <h1 style="font-family: Georgia, 'Times New Roman', serif; font-size: 32px; font-weight: 400; line-height: 1.25; color: #1c1917; margin: 0 0 10px 0; letter-spacing: -0.5px;">
                The Garment of Praise
              </h1>
              <p style="font-family: Georgia, serif; font-size: 15px; font-style: italic; color: #78716c; margin: 0 auto 16px auto; max-width: 480px; line-height: 1.5;">
                On replacing the spirit of heaviness, praise as divine alignment, and why joy is an act of spiritual defiance.
              </p>
              <div style="border-top: 1px solid #f5f5f4; padding-top: 10px; font-size: 10px; letter-spacing: 1.5px; text-transform: uppercase; color: #a8a29e;">
                Vol. IV • Issue 44 • Friday, November 6, 2026
              </div>
            </td>
          </tr>

          <!-- THE MORNING ESSAY (NO AI BULLETS) -->
          <tr>
            <td style="padding: 36px 44px 20px 44px;">
              <p style="font-family: Georgia, serif; font-size: 16px; line-height: 1.8; color: #292524; margin: 0 0 18px 0;">
                In the sixty-first chapter of Isaiah, the prophet outlines a divine exchange that defies all human calculation: beauty for ashes, the oil of joy for mourning, and the garment of praise for the spirit of heaviness.
              </p>
              <p style="font-family: Georgia, serif; font-size: 16px; line-height: 1.8; color: #292524; margin: 0 0 18px 0;">
                Notice the deliberate distinction. Heaviness is identified as a spirit—an invisible weight that attempts to settle over your thoughts, paralyze your momentum, and whisper that your efforts are in vain. But praise is described as a garment. A garment is never passive. It is an intentional choice you make before you step out into the world.
              </p>
              <p style="font-family: Georgia, serif; font-size: 16px; line-height: 1.8; color: #292524; margin: 0 0 20px 0;">
                You do not wait until you feel warm before putting on a coat. In the same way, the kingdom never calls us to wait for pleasant circumstances before we choose to worship.
              </p>
              <p style="font-family: Georgia, serif; font-size: 16px; line-height: 1.8; color: #292524; margin: 0 0 24px 0;">
                Reflecting on this morning's live worship gatherings—from the sustained fervor of Nathaniel Bassey's Hallelujah Challenge to Apostle Joshua Selman's teachings on spiritual alignment—one reality becomes clear: joy is not an accidental emotional reaction. Joy is a weapon of warfare. When you choose thanksgiving in the face of pressure, you disarm heaviness because light and despair cannot occupy the same altar.
              </p>

              <!-- Curated Quote Accent -->
              <div style="border-left: 2px solid #b45309; padding: 8px 0 8px 20px; margin: 28px 0;">
                <div style="font-family: Georgia, serif; font-size: 18px; font-style: italic; color: #1c1917; line-height: 1.5;">
                  “Praise is not an emotional reaction to an easy season; it is the spiritual posture that disarms heaviness and summons the peace of God.”
                </div>
                <div style="font-size: 11px; letter-spacing: 1px; text-transform: uppercase; color: #78716c; margin-top: 6px;">
                  — Isaiah 61:3 • Nathaniel Bassey &amp; Apostle Joshua Selman
                </div>
              </div>
            </td>
          </tr>

          <!-- ============================================== -->
          <!-- PART I: THE SQUARE ARTWORK & REFLECTION       -->
          <!-- ============================================== -->
          <tr>
            <td style="padding: 10px 44px 36px 44px;">
              <div style="border-top: 1px solid #f5f5f4; padding-top: 28px;">
                
                <div style="font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #a8a29e; margin-bottom: 6px;">
                  THE ARTWORK • MASTER COMPOSITION
                </div>
                <h3 style="font-family: Georgia, serif; font-size: 20px; font-weight: normal; color: #1c1917; margin: 0 0 16px 0;">
                  Put on the Garment of Praise
                </h3>

                <!-- Clean Artwork Display -->
                <div style="text-align: center; margin: 16px 0 24px 0;">
                  <img src="cid:flyer_praise_square" alt="The Garment of Praise Artwork" style="max-width: 100%; height: auto; border-radius: 2px; border: 1px solid #e7e5e4; display: block; margin: 0 auto; box-shadow: 0 4px 20px rgba(0,0,0,0.04);" />
                </div>

                <!-- Editorial Post Draft -->
                <div style="background-color: #fafaf9; border-left: 2px solid #1c1917; padding: 18px 20px; font-size: 14px; line-height: 1.75; color: #44403c; margin-bottom: 20px;">
                  <p style="margin: 0 0 12px 0; font-family: Georgia, serif; font-size: 15px; color: #1c1917;">
                    Heaviness is a spirit, but praise is a garment.
                  </p>
                  <p style="margin: 0 0 12px 0;">
                    You don't wait to feel happy before you put on your clothes—and you don't wait for life to become simple before choosing to worship.
                  </p>
                  <p style="margin: 0 0 12px 0; font-style: italic; color: #92400e;">
                    When you offer God your gratitude in the middle of uncertainty, you break the cycle of anxious striving and anchor your spirit in His unbroken peace.
                  </p>
                  <div style="font-size: 12px; color: #a8a29e; border-top: 1px solid #f5f5f4; padding-top: 8px;">
                    #GarmentOfPraise #HallelujahChallenge #NathanielBassey #ApostleJoshuaSelman #FaithOverFear #MorningDevotion
                  </div>
                </div>

                <!-- Classic Understated Action Buttons -->
                <table width="100%" cellspacing="0" cellpadding="0">
                  <tr>
                    <td align="left">
                      <a href="{links['twitter']}" style="display: inline-block; background-color: #1c1917; color: #ffffff; text-decoration: none; font-size: 11px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; padding: 9px 18px; border-radius: 2px;">
                        Post to X
                      </a>
                      &nbsp;
                      <a href="{links['threads']}" style="display: inline-block; background-color: #44403c; color: #ffffff; text-decoration: none; font-size: 11px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; padding: 9px 18px; border-radius: 2px;">
                        Post on Threads
                      </a>
                    </td>
                    <td align="right">
                      <a href="{links['facebook']}" style="display: inline-block; border: 1px solid #d6d3d1; color: #292524; text-decoration: none; font-size: 11px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; padding: 8px 16px; border-radius: 2px;">
                        Share to Facebook
                      </a>
                    </td>
                  </tr>
                </table>

              </div>
            </td>
          </tr>

          <!-- ============================================== -->
          <!-- PART II: THE MOBILE REFLECTION (WHATSAPP)     -->
          <!-- ============================================== -->
          <tr>
            <td style="padding: 10px 44px 36px 44px;">
              <div style="border-top: 1px solid #f5f5f4; padding-top: 28px;">
                
                <div style="font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #15803d; margin-bottom: 6px;">
                  THE MOBILE REFLECTION • STATUS CARD
                </div>
                <h3 style="font-family: Georgia, serif; font-size: 20px; font-weight: normal; color: #1c1917; margin: 0 0 16px 0;">
                  Exchange Heaviness for Joy
                </h3>

                <!-- Clean Vertical Flyer Display -->
                <div style="text-align: center; margin: 16px 0 24px 0;">
                  <img src="cid:flyer_praise_whatsapp" alt="Divine Joy Status Card" style="max-width: 280px; height: auto; border-radius: 2px; border: 1px solid #e7e5e4; display: block; margin: 0 auto; box-shadow: 0 4px 20px rgba(0,0,0,0.04);" />
                </div>

                <!-- Intimate, Warm Message -->
                <div style="background-color: #fafaf9; border-left: 2px solid #16a34a; padding: 18px 20px; font-size: 14px; line-height: 1.75; color: #44403c; margin-bottom: 20px;">
                  <p style="margin: 0 0 10px 0; font-weight: 600; color: #1c1917;">
                    Good morning my friend.
                  </p>
                  <p style="margin: 0 0 10px 0;">
                    A quiet word for your Friday: In Isaiah 61:3, God promises <em>“the garment of praise for the spirit of heaviness.”</em> If you've carried weariness this week, lay it down today. When you dress your mind in gratitude, God clothes you in strength.
                  </p>
                  <p style="margin: 0; font-size: 13px; color: #78716c;">
                    📖 <em>“You turned my wailing into dancing; you removed my sackcloth and clothed me with joy.”</em> — Psalm 30:11
                  </p>
                </div>

                <!-- Pre-filled WhatsApp Button -->
                <div style="text-align: right;">
                  <a href="{links['whatsapp']}" style="display: inline-block; background-color: #15803d; color: #ffffff; text-decoration: none; font-size: 11px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; padding: 9px 20px; border-radius: 2px;">
                    Send via WhatsApp
                  </a>
                </div>

              </div>
            </td>
          </tr>

          <!-- CLASSIC FOOTER -->
          <tr>
            <td style="padding: 28px 44px; background-color: #fafaf9; border-top: 1px solid #e7e5e4; text-align: center;">
              <p style="font-family: Georgia, serif; font-size: 13px; font-style: italic; color: #78716c; margin: 0 0 6px 0;">
                The Kingdom Journal is curated daily for personal reflection and ministry distribution.
              </p>
              <p style="font-size: 10px; color: #a8a29e; letter-spacing: 1px; text-transform: uppercase; margin: 0;">
                Dispatched to aondoaseerezekiel@gmail.com
              </p>
            </td>
          </tr>

        </table>

      </td>
    </tr>
  </table>

</body>
</html>"""

def send_luxury_editorial_email(recipient: str, subject: str, fliers_dir: Path):
    load_env_file()
    ensure_flyers(fliers_dir)
    
    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER", "").strip()
    smtp_pass = os.environ.get("SMTP_PASSWORD", "").strip().replace(" ", "")

    if not smtp_user or not smtp_pass:
        print("[ERROR] SMTP_USER or SMTP_PASSWORD not set in environment or .env", file=sys.stderr)
        return False

    msg = MIMEMultipart("related")
    msg["Subject"] = subject
    msg["From"] = f"The Kingdom Journal <{smtp_user}>"
    msg["To"] = recipient

    # Fresh Humanized Captions for Issue 44 (The Garment of Praise)
    captions = {
        "twitter": "Heaviness is a spirit, but praise is a garment.\n\nYou don't wait to feel cheerful before you put on your clothes—and you don't wait for life to become easy before you choose to worship.\n\nJoy is not an emotional accident; it is an act of spiritual defiance.\n\nPut on praise today. 🕊️",
        "whatsapp": "Good morning my friend. A quick word for your Friday:\n\nIn Isaiah 61:3, God promises “the garment of praise for the spirit of heaviness.”\n\nNotice that praise is a garment—it is something you actively choose to put on. If you've felt drained or overwhelmed this week, don't let heaviness have the final word. Take 2 minutes right now to thank God for His faithfulness.\n\n📖 “You turned my wailing into dancing; you removed my sackcloth and clothed me with joy.” — Psalm 30:11\n\nHave a blessed and peaceful day! Forward this to someone who needs a lift today. ✨",
        "threads": "A quick thought for Friday morning:\n\nMost people treat joy like an emotional consequence—something that only happens when all their problems are solved.\n\nScripture treats joy as a spiritual decision. Heaviness tries to dictate the room, but praise establishes God's atmosphere.\n\nYou don't wait for the trial to end to put on praise. You put on praise to remind yourself who God remains in every season. What are you grateful for today?",
        "facebook": "“Praise is not an emotional reaction to an easy season; it is the spiritual posture that disarms heaviness and summons the peace of God.” (Isaiah 61:3)\n\nHeaviness is a spirit, but praise is a garment. You don't wait to feel cheerful before you choose to worship. When you give God your gratitude in the middle of uncertainty, you break the cycle of anxiety and anchor your peace. Step out today with thanksgiving in your heart."
    }

    links = generate_social_intent_links(captions)
    html_content = build_luxury_email_html(links)
    plain_text = (
        "The Kingdom Journal • Morning Edition (Issue 44)\n\n"
        "The Garment of Praise\n"
        "“Praise is not an emotional reaction to an easy season; it is the spiritual posture that disarms heaviness and summons the peace of God.” — Isaiah 61:3\n\n"
        "Please view this email in an HTML-compatible email client to review today's artwork and pre-filled social actions."
    )

    alt_part = MIMEMultipart("alternative")
    alt_part.attach(MIMEText(plain_text, "plain", "utf-8"))
    alt_part.attach(MIMEText(html_content, "html", "utf-8"))
    msg.attach(alt_part)

    # Attach the two brand new Issue 44 topic flyers
    attachments = [
        ("flyer_praise_square", fliers_dir / "flyer_praise_square.jpg"),
        ("flyer_praise_whatsapp", fliers_dir / "flyer_praise_whatsapp.jpg")
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
                quote_text="Praise is not an emotional reaction to an easy season; it is the spiritual posture that disarms heaviness and summons the peace of God.",
                speaker="Nathaniel Bassey & Apostle Joshua Selman",
                scripture="Isaiah 61:3 • Psalm 30:11-12"
            )
            if youtube_api_client:
                try:
                    live_vids = youtube_api_client.fetch_trending_gospel_videos()
                    for lv in live_vids:
                        content_db.record_video(
                            video_id=lv.get("video_id", "live_asset"),
                            title=lv.get("title", ""),
                            channel=lv.get("channel", ""),
                            published_at=lv.get("published_at", "")
                        )
                    print(f"[YOUTUBE INTEGRATION] {len(live_vids)} live video assets archived in database.")
                except Exception as ex:
                    print(f"[YOUTUBE WARNING] Live archival skipped: {ex}", file=sys.stderr)
            print("[DATABASE] Today's topic and video assets archived in SQLite memory.")

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
        subject="🕊️ The Kingdom Journal • The Garment of Praise (Issue 44)",
        fliers_dir=fliers_dir
    )
