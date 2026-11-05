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
                Send Judah First
              </h1>
              <p style="font-family: Georgia, serif; font-size: 15px; font-style: italic; color: #78716c; margin: 0 auto 16px auto; max-width: 480px; line-height: 1.5;">
                On praise as strategic defiance, the power of midnight prayer, and why gratitude always precedes the open door.
              </p>
              <div style="border-top: 1px solid #f5f5f4; padding-top: 10px; font-size: 10px; letter-spacing: 1.5px; text-transform: uppercase; color: #a8a29e;">
                Vol. IV • Issue 43 • Thursday, November 5, 2026
              </div>
            </td>
          </tr>

          <!-- THE MORNING ESSAY (NO AI BULLETS) -->
          <tr>
            <td style="padding: 36px 44px 20px 44px;">
              <p style="font-family: Georgia, serif; font-size: 16px; line-height: 1.8; color: #292524; margin: 0 0 18px 0;">
                In ancient biblical warfare, King Jehoshaphat was confronted by three converging armies. Conventional military prudence would have placed the veteran archers, the heavy shields, and the frontline cavalry at the head of the formation. Instead, the king appointed worshippers to lead the march.
              </p>
              <p style="font-family: Georgia, serif; font-size: 16px; line-height: 1.8; color: #292524; margin: 0 0 20px 0;">
                He didn't send the army first. He sent Judah.
              </p>
              <p style="font-family: Georgia, serif; font-size: 16px; line-height: 1.8; color: #292524; margin: 0 0 24px 0;">
                Watching today's live ministrations from Nathaniel Bassey and Mercy Chinwo brought home a timeless spiritual order: the breakthrough rarely begins when the circumstance changes. It begins the exact moment your song shifts. Praise is not an emotional celebration of what went right—it is a defiant announcement of who God remains when the room is dark.
              </p>

              <!-- Curated Quote Accent -->
              <div style="border-left: 2px solid #b45309; padding: 8px 0 8px 20px; margin: 28px 0;">
                <div style="font-family: Georgia, serif; font-size: 18px; font-style: italic; color: #1c1917; line-height: 1.5;">
                  “The breakthrough doesn't start when the trial ends. It begins when your song changes.”
                </div>
                <div style="font-size: 11px; letter-spacing: 1px; text-transform: uppercase; color: #78716c; margin-top: 6px;">
                  — 2 Chronicles 20:21 • Nathaniel Bassey &amp; Mercy Chinwo
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
                  Send Judah First
                </h3>

                <!-- Clean Artwork Display -->
                <div style="text-align: center; margin: 16px 0 24px 0;">
                  <img src="cid:flyer_judah" alt="Send Judah First Artwork" style="max-width: 100%; height: auto; border-radius: 2px; border: 1px solid #e7e5e4; display: block; margin: 0 auto; box-shadow: 0 4px 20px rgba(0,0,0,0.04);" />
                </div>

                <!-- Editorial Post Draft -->
                <div style="background-color: #fafaf9; border-left: 2px solid #1c1917; padding: 18px 20px; font-size: 14px; line-height: 1.75; color: #44403c; margin-bottom: 20px;">
                  <p style="margin: 0 0 12px 0; font-family: Georgia, serif; font-size: 15px; color: #1c1917;">
                    Most of us wait for the storm to subside before we allow ourselves to breathe. But scripture paints a radically different picture.
                  </p>
                  <p style="margin: 0 0 12px 0;">
                    When King Jehoshaphat marched toward battle, he placed the singers on the front line. Praise was never designed as an emotional reaction to an easy week—it is your strategic weapon to enforce peace before the outcome is visible.
                  </p>
                  <p style="margin: 0 0 12px 0; font-style: italic; color: #92400e;">
                    If you are facing an uphill battle today, don't wait for Friday to thank God. Open your Bible, take a quiet breath, and send Judah first.
                  </p>
                  <div style="font-size: 12px; color: #a8a29e; border-top: 1px solid #f5f5f4; padding-top: 8px;">
                    #SendJudahFirst #PraiseWeapon #WorshipDevotional #NathanielBassey #MercyChinwo #FaithOverFear
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
          <!-- PART II: THE MIDNIGHT REFLECTION (WHATSAPP)   -->
          <!-- ============================================== -->
          <tr>
            <td style="padding: 10px 44px 36px 44px;">
              <div style="border-top: 1px solid #f5f5f4; padding-top: 28px;">
                
                <div style="font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #15803d; margin-bottom: 6px;">
                  THE MOBILE REFLECTION • STATUS CARD
                </div>
                <h3 style="font-family: Georgia, serif; font-size: 20px; font-weight: normal; color: #1c1917; margin: 0 0 16px 0;">
                  Give God Your Midnight
                </h3>

                <!-- Clean Vertical Flyer Display -->
                <div style="text-align: center; margin: 16px 0 24px 0;">
                  <img src="cid:flyer_midnight" alt="Midnight Thanksgiving Poster" style="max-width: 280px; height: auto; border-radius: 2px; border: 1px solid #e7e5e4; display: block; margin: 0 auto; box-shadow: 0 4px 20px rgba(0,0,0,0.04);" />
                </div>

                <!-- Intimate, Warm Message -->
                <div style="background-color: #fafaf9; border-left: 2px solid #16a34a; padding: 18px 20px; font-size: 14px; line-height: 1.75; color: #44403c; margin-bottom: 20px;">
                  <p style="margin: 0 0 10px 0; font-weight: 600; color: #1c1917;">
                    Good morning my friend.
                  </p>
                  <p style="margin: 0 0 10px 0;">
                    A quiet word for your day: Never let yesterday's weariness steal today's gratitude. When you give God your midnight, He gives you peace for the morning.
                  </p>
                  <p style="margin: 0; font-size: 13px; color: #78716c;">
                    📖 <em>“At midnight Paul and Silas were praying and singing hymns to God, and the prisoners were listening to them.”</em> — Acts 16:25
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

    # Fresh Humanized Captions for Today's New Topic
    captions = {
        "twitter": "The breakthrough doesn't start when the problem leaves.\n\nIt begins the moment your song changes.\n\nPraise is not a celebration of what went right—it is a declaration of who God remains in the dark.\n\nSend Judah first. 🕊️",
        "whatsapp": "Good morning my friend. A quiet word for your day:\n\nNever let yesterday's weariness steal today's gratitude. When you give God your midnight, He gives you peace for the morning.\n\n📖 “At midnight Paul and Silas prayed and sang praises unto God...” — Acts 16:25\n\nTake 2 minutes to thank Him today. Send this to someone who needs peace! ✨",
        "threads": "There is a quiet strength that comes when you stop waiting for life to become easy before you choose to worship.\n\nWhen King Jehoshaphat went into battle, he didn't send the army first. He sent the singers.\n\nBreakthrough doesn't start when the difficulty ends—it begins the moment your song changes. Send Judah first.",
        "facebook": "“The breakthrough doesn't start when the trial ends. It begins when your song changes.” Praise is not an emotional celebration of what went right; it is a declaration of who God remains when the room is dark. If you're facing an uphill climb today, don't wait for Friday to thank Him. Send Judah first."
    }

    links = generate_social_intent_links(captions)
    html_content = build_luxury_email_html(links)
    plain_text = "The Kingdom Journal • Morning Edition. Please view in an HTML-compatible email client to review today's artwork and pre-filled social drafts."

    alt_part = MIMEMultipart("alternative")
    alt_part.attach(MIMEText(plain_text, "plain", "utf-8"))
    alt_part.attach(MIMEText(html_content, "html", "utf-8"))
    msg.attach(alt_part)

    # Attach the two brand new topic flyers
    attachments = [
        ("flyer_judah", fliers_dir / "flyer_judah_square.jpg"),
        ("flyer_midnight", fliers_dir / "flyer_midnight_whatsapp.jpg")
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
                quote_text="The breakthrough doesn't start when the trial ends. It begins when your song changes.",
                speaker="Nathaniel Bassey & Mercy Chinwo",
                scripture="2 Chronicles 20:21"
            )
            print("[DATABASE] New topic archived in SQLite memory.")

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
        subject="🕊️ The Kingdom Journal • Send Judah First (Issue 43)",
        fliers_dir=fliers_dir
    )
