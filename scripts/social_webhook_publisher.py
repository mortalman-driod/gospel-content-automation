"""
1-Click Social Media Webhook & Publishing Engine
Provides a unified bridge to publish or schedule gospel fliers and captions
to Instagram, Facebook, Twitter, and Threads via Ayrshare, Buffer, or Zapier/Make webhooks.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
import urllib.request
import urllib.parse

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

def stage_local_post(platform: str, caption: str, flier_path: str):
    """Stages the post into a local JSON archive for review or manual 1-click execution."""
    stage_file = Path(__file__).resolve().parent.parent / "reports" / "staged_posts.json"
    staged = []
    if stage_file.is_file():
        try:
            staged = json.loads(stage_file.read_text(encoding="utf-8"))
        except Exception:
            staged = []
            
    item = {
        "id": f"{platform}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        "platform": platform,
        "caption": caption,
        "flier_path": str(flier_path),
        "status": "READY_TO_PUBLISH"
    }
    staged.append(item)
    stage_file.write_text(json.dumps(staged, indent=2), encoding="utf-8")
    print(f"[STAGED] Post for {platform} staged in {stage_file.name}")
    return item

def publish_via_webhook(platform: str, caption: str, flier_path: str = None) -> bool:
    load_env_file()
    webhook_url = os.environ.get("SOCIAL_PUBLISH_WEBHOOK_URL")
    
    if not webhook_url:
        print("[NOTICE] SOCIAL_PUBLISH_WEBHOOK_URL not configured in .env. Staging post locally.")
        stage_local_post(platform, caption, flier_path)
        return True

    payload = {
        "platform": platform,
        "caption": caption,
        "flier_filename": Path(flier_path).name if flier_path else None,
        "timestamp": datetime.now().isoformat(),
        "token": os.environ.get("PUBLISH_SECRET_TOKEN", "default_secret")
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            webhook_url,
            data=data,
            headers={"Content-Type": "application/json", "User-Agent": "AntigravityGospelEngine/2.0"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            code = resp.getcode()
            print(f"[PUBLISH SUCCESS] Webhook dispatched to {webhook_url} with status {code}")
            return True
    except Exception as e:
        print(f"[PUBLISH ERROR] Failed to dispatch webhook: {e}", file=sys.stderr)
        stage_local_post(platform, caption, flier_path)
        return False

def main():
    parser = argparse.ArgumentParser(description="Dispatch or stage social media post.")
    parser.add_argument("--platform", required=True, choices=["instagram", "facebook", "whatsapp", "twitter", "threads", "all"])
    parser.add_argument("--caption", required=True, help="Post caption")
    parser.add_argument("--flier", default=None, help="Path to image flier")
    args = parser.parse_args()

    publish_via_webhook(args.platform, args.caption, args.flier)

if __name__ == "__main__":
    main()
