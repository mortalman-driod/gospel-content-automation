"""
Automated Email Dispatcher Script with Inline Fliers & Attachments
Sends HTML/Markdown-formatted reports via SMTP (e.g. Gmail SMTP)
with embedded graphic fliers and platform-ready captions.
"""

import argparse
import os
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from pathlib import Path

def load_env_file():
    """Load variables from .env if present in the project root."""
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
        except Exception as e:
            print(f"[DEBUG] Could not load .env: {e}", file=sys.stderr)

def send_email_with_fliers(subject: str, recipient: str, body_text: str, fliers_dir: Path = None) -> bool:
    load_env_file()
    
    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER", "").strip()
    smtp_pass = os.environ.get("SMTP_PASSWORD", "").strip().replace(" ", "")

    if not smtp_user or not smtp_pass:
        print("[WARNING] SMTP_USER or SMTP_PASSWORD is not set.", file=sys.stderr)
        return False

    # Outer container
    msg = MIMEMultipart("related")
    msg["Subject"] = subject
    msg["From"] = f"Gospel Content Pipeline <{smtp_user}>"
    msg["To"] = recipient

    # Collect images
    image_attachments = []
    if fliers_dir and fliers_dir.is_dir():
        for f in sorted(fliers_dir.glob("*.jpg")):
            cid = f.stem
            image_attachments.append((cid, f))

    # Build rich HTML
    fliers_html_cards = ""
    for cid, f_path in image_attachments:
        fliers_html_cards += f"""
        <div style="margin: 24px 0; background: #ffffff; border: 1px solid #e5e7eb; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
          <div style="padding: 10px 16px; background: #0f172a; color: #f59e0b; font-weight: bold; font-size: 13px; letter-spacing: 0.5px;">
            🎨 Flier Asset: {f_path.name}
          </div>
          <div style="text-align: center; padding: 12px; background: #1e1b4b;">
            <img src="cid:{cid}" style="max-width: 100%; height: auto; max-height: 480px; border-radius: 6px; display: inline-block;" alt="{f_path.stem}" />
          </div>
        </div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8">
      </head>
      <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #1e293b; background-color: #f8fafc; margin: 0; padding: 24px;">
        <div style="max-width: 800px; margin: 0 auto; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; padding: 32px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05);">
          
          <div style="border-bottom: 2px solid #f1f5f9; padding-bottom: 16px; margin-bottom: 24px;">
            <h1 style="color: #0f172a; font-size: 24px; margin: 0 0 8px 0;">🕊️ Daily Viral Gospel Trends & Multi-Platform Distribution</h1>
            <p style="color: #64748b; font-size: 14px; margin: 0;">Tailored social captions and graphic fliers for Facebook, Instagram, WhatsApp, Twitter, and Threads.</p>
          </div>

          <h2 style="color: #1e1b4b; font-size: 20px; border-left: 4px solid #f59e0b; padding-left: 10px; margin: 28px 0 14px 0;">🖼️ Generated Viral Flier Assets</h2>
          <p style="color: #475569; font-size: 14px;">The fliers below have been generated with typography, quotes, and aspect ratios matching each platform's standard:</p>
          {fliers_html_cards}

          <h2 style="color: #1e1b4b; font-size: 20px; border-left: 4px solid #3b82f6; padding-left: 10px; margin: 36px 0 14px 0;">📋 Multi-Platform Captions & Digest</h2>
          <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; font-size: 14px;">
            <pre style="white-space: pre-wrap; font-family: inherit; margin: 0; color: #334155; line-height: 1.7;">{body_text}</pre>
          </div>

          <div style="margin-top: 32px; padding-top: 16px; border-top: 1px solid #e2e8f0; color: #94a3b8; font-size: 12px; text-align: center;">
            Automated by Antigravity Gospel Content Pipeline • Sent to {recipient}
          </div>

        </div>
      </body>
    </html>
    """

    alt_part = MIMEMultipart("alternative")
    alt_part.attach(MIMEText(body_text, "plain", "utf-8"))
    alt_part.attach(MIMEText(html_content, "html", "utf-8"))
    msg.attach(alt_part)

    # Attach images as related inline assets
    for cid, f_path in image_attachments:
        try:
            with open(f_path, "rb") as img_f:
                mime_img = MIMEImage(img_f.read(), _subtype="jpeg")
                mime_img.add_header("Content-ID", f"<{cid}>")
                mime_img.add_header("Content-Disposition", "inline", filename=f_path.name)
                msg.attach(mime_img)
        except Exception as err:
            print(f"[WARNING] Could not attach image {f_path}: {err}", file=sys.stderr)

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=45) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, [recipient], msg.as_string())
        print(f"[SUCCESS] Email with {len(image_attachments)} fliers successfully delivered to {recipient}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description="Send an email report with attached fliers via SMTP.")
    parser.add_argument("--to", required=True, help="Recipient email address")
    parser.add_argument("--subject", required=True, help="Email subject line")
    parser.add_argument("--file", required=True, help="Path to markdown/text report file")
    parser.add_argument("--fliers-dir", default=None, help="Directory containing generated flier images")
    
    args = parser.parse_args()
    
    file_path = Path(args.file)
    if not file_path.is_file():
        print(f"[ERROR] Report file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    content = file_path.read_text(encoding="utf-8")
    fliers_dir = Path(args.fliers_dir) if args.fliers_dir else None

    success = send_email_with_fliers(
        subject=args.subject,
        recipient=args.to,
        body_text=content,
        fliers_dir=fliers_dir
    )
    
    if not success and not os.environ.get("SMTP_USER"):
        sys.exit(0)
    elif not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
