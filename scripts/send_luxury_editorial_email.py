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
                      Send Judah First
                    </h1>
                    <p style="font-family: Georgia, 'Times New Roman', serif; font-size: 15px; font-style: italic; color: #6e675f; margin: 0 auto 16px auto; max-width: 480px; line-height: 1.55;">
                      On praise as strategic defiance, the mystery of breakthrough before manifestation, and why thanksgiving leads the battle.
                    </p>
                    <div style="border-top: 1px solid #f0ede6; padding-top: 10px; font-size: 10px; letter-spacing: 2px; text-transform: uppercase; color: #a39c93;">
                      Vol. IV • Issue 45 • Friday, November 6, 2026
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
                In the twentieth chapter of Second Chronicles, King Jehoshaphat stood before an overwhelming military alliance. Three hostile nations had surrounded Jerusalem, and human reason demanded archers, barricades, and vanguard cavalry.
              </p>
              
              <p style="font-family: Georgia, 'Times New Roman', serif; font-size: 16px; line-height: 1.8; color: #2e2b27; margin: 0 0 18px 0;">
                Instead, the prophet Jahaziel delivered an instruction that defied all conventional military strategy: <em>Appoint worshippers to march at the very front of the army.</em>
              </p>

              <p style="font-family: Georgia, 'Times New Roman', serif; font-size: 16px; line-height: 1.8; color: #2e2b27; margin: 0 0 18px 0;">
                Judah—whose name literally signifies <em>praise</em>—was dispatched ahead of the spears. Before a single sword was unclasped, the moment their voices lifted in thanksgiving, supernatural ambushes scattered the opposition.
              </p>

              <p style="font-family: Georgia, 'Times New Roman', serif; font-size: 16px; line-height: 1.8; color: #2e2b27; margin: 0 0 24px 0;">
                Reflecting on this morning's live worship ministrations led by Nathaniel Bassey and Apostle Joshua Selman, the spiritual principle is unmistakable: <strong>Praise is not a celebration of a victory already completed; it is the strategic declaration of who God remains while the outcome is still contested.</strong> The breakthrough does not begin when the trial ends—it begins the moment your song changes.
              </p>

              <!-- Curated Pull Quote Accent -->
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin: 28px 0; border-left: 2px solid #b45309; background-color: #faf9f6;">
                <tr>
                  <td style="padding: 16px 20px;">
                    <div style="font-family: Georgia, 'Times New Roman', serif; font-size: 17px; font-style: italic; color: #1a1a1a; line-height: 1.55;">
                      “The breakthrough doesn't start when the trial ends; it begins when your song changes. Praise is not a celebration of what went right—it is a declaration of who God remains.”
                    </div>
                    <div style="font-size: 11px; letter-spacing: 1.5px; text-transform: uppercase; color: #8c827a; margin-top: 8px;">
                      — 2 CHRONICLES 20:21-22 • NATHANIEL BASSEY &amp; APOSTLE JOSHUA SELMAN
                    </div>
                  </td>
                </tr>
              </table>

            </td>
          </tr>

          <!-- ============================================== -->
          <!-- PART I: THE SQUARE MASTER ARTWORK              -->
          <!-- ============================================== -->
          <tr>
            <td class="content-padding" style="padding: 10px 48px 36px 48px;">
              <div style="border-top: 1px solid #f0ede6; padding-top: 30px;">
                
                <div style="font-size: 10px; font-weight: 700; letter-spacing: 2.5px; text-transform: uppercase; color: #a39c93; margin-bottom: 6px;">
                  THE ARTWORK • MASTER COMPOSITION (1:1)
                </div>
                <h3 style="font-family: Georgia, 'Times New Roman', serif; font-size: 21px; font-weight: normal; color: #1a1a1a; margin: 0 0 16px 0;">
                  Send Judah First: Praise as Strategic Defiance
                </h3>

                <!-- Native Studio Artwork Display -->
                <div style="text-align: center; margin: 16px 0 24px 0;">
                  <img src="cid:flyer_judah" alt="Send Judah First Artwork" width="504" style="max-width: 100%; width: 100%; height: auto; border: 1px solid #e5e2da; display: block; margin: 0 auto; box-shadow: 0 6px 24px rgba(0,0,0,0.06);" />
                </div>

                <!-- Editorial Social Copy Block -->
                <div style="background-color: #faf9f6; border-left: 2px solid #1a1a1a; padding: 20px 22px; font-size: 14px; line-height: 1.75; color: #3d3935; margin-bottom: 22px;">
                  <p style="margin: 0 0 12px 0; font-family: Georgia, 'Times New Roman', serif; font-size: 15px; color: #1a1a1a;">
                    The breakthrough doesn't start when the trial ends. It begins when your song changes.
                  </p>
                  <p style="margin: 0 0 12px 0;">
                    When Jehoshaphat faced three invading armies, he didn't put his swordsmen at the front—he sent worshippers. Judah means praise, and praise goes first.
                  </p>
                  <p style="margin: 0 0 12px 0; font-style: italic; color: #92400e;">
                    Praise is not a celebration of what went right; it is an uncompromising declaration of who God remains. Whatever feels heavy this morning, lead with worship.
                  </p>
                  <div style="font-size: 11px; color: #8c827a; border-top: 1px solid #e5e2da; padding-top: 10px; letter-spacing: 0.5px;">
                    #SendJudahFirst #TheKingdomJournal #NathanielBassey #ApostleJoshuaSelman #FaithOverFear #MorningDevotion
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
                  Give God Your Midnight
                </h3>

                <!-- Clean Vertical Flyer Display -->
                <div style="text-align: center; margin: 16px 0 24px 0;">
                  <img src="cid:flyer_midnight" alt="Give God Your Midnight Poster" width="300" style="max-width: 300px; width: 100%; height: auto; border: 1px solid #e5e2da; display: block; margin: 0 auto; box-shadow: 0 6px 24px rgba(0,0,0,0.06);" />
                </div>

                <!-- Warm Intimate Reflection -->
                <div style="background-color: #f7fcf8; border-left: 2px solid #16a34a; padding: 20px 22px; font-size: 14px; line-height: 1.75; color: #2e3b2e; margin-bottom: 22px;">
                  <p style="margin: 0 0 10px 0; font-weight: 600; color: #14532d; font-family: Georgia, 'Times New Roman', serif; font-size: 15px;">
                    Good morning my friend.
                  </p>
                  <p style="margin: 0 0 10px 0;">
                    A word for your Friday: Never let yesterday's weariness steal today's gratitude. Give God your midnight, and watch Him clear your morning.
                  </p>
                  <p style="margin: 0; font-size: 13px; color: #4b6350; font-style: italic;">
                    📖 “At midnight Paul and Silas were praying and singing hymns to God, and the other prisoners were listening to them. Suddenly there was such a violent earthquake that the foundations of the prison were shaken.” — Acts 16:25-26
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

    msg = MIMEMultipart("related")
    msg["Subject"] = subject
    msg["From"] = f"The Kingdom Journal <{smtp_user}>"
    msg["To"] = recipient

    # Fresh Humanized Captions for Issue 45 (Send Judah First)
    captions = {
        "twitter": "The breakthrough doesn't start when the trial ends.\n\nIt begins when your song changes.\n\nWhen Jehoshaphat faced three invading armies, he didn't put swordsmen at the front—he sent worshippers. Judah means praise, and praise goes first.\n\nSend Judah first today. 🕊️",
        "whatsapp": "Good morning my friend. A quick word for your Friday:\n\nNever let yesterday's weariness steal today's gratitude. Give God your midnight, and watch Him clear your morning.\n\nIn 2 Chronicles 20, God told Jehoshaphat to put worshippers at the front lines. The moment they began to sing, God set ambushes for their victory.\n\n📖 “Praise the Lord, for His mercy endures forever.” — 2 Chronicles 20:21\n\nHave a victorious and blessed day! Forward this to someone who needs courage today. ✨",
        "threads": "A thought for your Friday morning:\n\nMost people wait for the breakthrough before releasing their song.\n\nIn the kingdom, your song IS the breakthrough. In 2 Chronicles 20, King Jehoshaphat placed worshippers at the front lines ahead of the army. Praise wasn't the victory parade—it was the weapon.\n\nDon't wait for things to calm down before thanking God. Praise is a declaration of who He remains in every storm. What are you praising Him for today?",
        "facebook": "“The breakthrough doesn't start when the trial ends; it begins when your song changes. Praise is not a celebration of what went right—it is a declaration of who God remains.” (2 Chronicles 20:21-22)\n\nWhen you face an uphill battle, do not wait until the dust settles to give God your thanksgiving. Worship is spiritual defiance. Lead with praise today and let God handle the battle."
    }

    links = generate_social_intent_links(captions)
    html_content = build_luxury_email_html(links)
    plain_text = (
        "The Kingdom Journal • Morning Edition (Issue 45)\n\n"
        "Send Judah First\n"
        "“The breakthrough doesn't start when the trial ends; it begins when your song changes. Praise is not a celebration of what went right—it is a declaration of who God remains.” — 2 Chronicles 20:21-22\n\n"
        "Please view this email in an HTML-compatible email client to review today's artwork and pre-filled social actions."
    )

    alt_part = MIMEMultipart("alternative")
    alt_part.attach(MIMEText(plain_text, "plain", "utf-8"))
    alt_part.attach(MIMEText(html_content, "html", "utf-8"))
    msg.attach(alt_part)

    # Attach the two brand new authentic studio viral fliers
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
                quote_text="The breakthrough doesn't start when the trial ends; it begins when your song changes. Praise is not a celebration of what went right—it is a declaration of who God remains.",
                speaker="Nathaniel Bassey & Apostle Joshua Selman",
                scripture="2 Chronicles 20:21-22 • Acts 16:25-26"
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
        subject="🕊️ The Kingdom Journal • Send Judah First (Issue 45)",
        fliers_dir=fliers_dir
    )
