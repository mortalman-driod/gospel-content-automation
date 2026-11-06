"""
Custom Dispatcher for Today's Second Trending Gospel Topic:
"The Protocol of the Secret Place" (Issue 49)
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))

import send_luxury_editorial_email

new_topic = {
    "title": "The Protocol of the Secret Place",
    "hook_top": "What God builds in secret",
    "banner_text": "CANNOT BE SHAKEN",
    "quote": "Spiritual authority is not acquired on public stages; it is forged in the silence of deep consecration.",
    "speaker": "Dunsin Oyekan & Apostle Joshua Selman",
    "scripture": "Matthew 6:6 • Psalm 91:1",
    "videos": [
        {"title": "DUNSIN OYEKAN || THE SECRET PLACE WORSHIP LIVE", "channel": "Dunsin Oyekan"},
        {"title": "APOSTLE JOSHUA SELMAN || KOINONIA 2026 LIVE", "channel": "Koinonia Global"},
        {"title": "VICTORIA ORENZE || DEEP CONSECRATION PRAYER SESSION", "channel": "Victoria Orenze"}
    ]
}

success = send_luxury_editorial_email.send_luxury_editorial_email(
    recipient="aondoaseerezekiel@gmail.com",
    subject="🕊️ The Kingdom Journal • The Protocol of the Secret Place (Issue 49)",
    override_topic=new_topic
)

if success:
    print("\n[DISPATCH CONFIRMED] Issue 49 successfully delivered to aondoaseerezekiel@gmail.com")
else:
    print("\n[DISPATCH FAILED] Email delivery failed.")
