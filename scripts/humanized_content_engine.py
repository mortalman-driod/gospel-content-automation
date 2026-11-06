"""
Gemini-Powered Humanized Editorial Content & Caption Engine (Model 3.8 Cascade)
Trained specifically for 'The Kingdom Journal' to produce luxury de-AI'd prose
and platform-tailored social copy using Google Gemini (3.8 -> 3.5 -> 2.5 cascade).
"""

import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def load_env():
    env_path = BASE_DIR / ".env"
    if env_path.is_file():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k and k not in os.environ:
                    os.environ[k] = v

MODELS_CASCADE = ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-2.5-flash"]

class HumanizedContentEngine:
    def __init__(self, quote: str, speaker: str = None, scripture: str = None, title: str = None):
        load_env()
        self.quote = quote.strip()
        self.speaker = speaker or "Nathaniel Bassey & Apostle Joshua Selman"
        self.scripture = scripture or "Psalm 46:5 • Isaiah 40:31"
        self.title = title or self._derive_title(self.quote)
        self.api_key = os.environ.get("GEMINI_API_KEY", "").strip()

    def _derive_title(self, quote: str) -> str:
        words = quote.split()
        if len(words) <= 5:
            return quote.title()
        return " ".join(words[:5]).title()

    def generate_all_with_gemini(self) -> dict:
        """Invokes Gemini 3.8 Flash (cascading fallback) with the trained Kingdom Journal editorial persona."""
        if not self.api_key:
            return None

        prompt = f"""You are the Executive Editor and Creative Director for 'The Kingdom Journal', a luxury Christian morning publication.
Transform this proprietary theological principle and scripture into an original, refined, humanized editorial package.

CORE REVELATION:
- Principle: "{self.quote}"
- Context: "{self.speaker}"
- Scripture: "{self.scripture}"
- Topic: "{self.title}"

STRICT EDITORIAL RULES:
1. ABSOLUTELY NO robotic bullet points (NO "1/", "2/", "3/", NO "Point 1:").
2. ABSOLUTELY NO syllabus outlines (NO "Here are 3 spiritual principles...", NO "In this issue, we explore...").
3. ABSOLUTELY NO AI clichés (NO "In today's fast-paced world...", NO "Have you ever wondered...", NO "It's not about X, it's about Y").
4. ABSOLUTELY NO church event invitations or promotional phrasing. This is 100% original, brand-building intellectual property.
5. Voice: The contemplative theological depth of A.W. Tozer combined with the vibrant spiritual warmth of contemporary worship leaders.
6. Produce pure JSON with exact keys:
   - "title": Evocative, literary title (3 to 5 words).
   - "subtitle": Italicized editorial subtitle capturing the spiritual tension (1 concise sentence).
   - "essay_paragraphs": Array of 3 to 4 flowing narrative paragraphs of high-class prose exploring the scripture and revelation.
   - "instagram": Full Instagram caption with striking 1-line hook, reflective commentary, a thought-provoking question, and 12 curated hashtags.
   - "whatsapp": Warm, personal devotional broadcast starting with "Good morning my friend. A quiet word for your morning:", italicized scripture, and a gentle forward prompt.
   - "twitter": Sharp, memorable aphorism under 240 characters with maximum viral resonance.
   - "threads": Narrative thought ending with an engaging community reflection question.
   - "facebook": Thoughtful pastoral devotional for a faith community.
"""

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.65,
                "topP": 0.95
            }
        }

        for model in MODELS_CASCADE:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
            try:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=16) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    content_text = data["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = json.loads(content_text)
                    parsed["date_str"] = datetime.now().strftime("%A, %B %d, %Y")
                    print(f"[GEMINI ENGINE SUCCESS] Generated humanized content via {model} for '{parsed.get('title')}'")
                    return parsed
            except Exception as e:
                print(f"[GEMINI ENGINE NOTICE] Model {model} pass: {e}", file=sys.stderr)
                continue

        return None

    def generate_editorial_micro_essay(self) -> dict:
        """Tries Gemini first, falls back to deterministic literary prose."""
        gemini_result = self.generate_all_with_gemini()
        if gemini_result and "essay_paragraphs" in gemini_result:
            return {
                "title": gemini_result.get("title", self.title),
                "subtitle": gemini_result.get("subtitle", "On the quiet power of God's presence."),
                "essay_paragraphs": gemini_result.get("essay_paragraphs", []),
                "date_str": gemini_result.get("date_str", datetime.now().strftime("%A, %B %d, %Y")),
                "gemini_captions": {
                    "instagram": gemini_result.get("instagram", ""),
                    "whatsapp": gemini_result.get("whatsapp", ""),
                    "twitter": gemini_result.get("twitter", ""),
                    "threads": gemini_result.get("threads", ""),
                    "facebook": gemini_result.get("facebook", "")
                }
            }

        # Deterministic Literary Fallback (Pristine, 100% De-Promotional)
        today_date = datetime.now().strftime("%A, %B %d, %Y")
        p1 = (
            "There are seasons in every believer's walk where human vocabulary reaches its natural limit. "
            "You begin your morning with weights that cannot be neatly filed away into bulleted petitions, "
            "and the pressure of what lies ahead defies effortless explanation."
        )
        p2 = (
            f"Scripture reveals in {self.scripture} that the kingdom has never demanded polished eloquence "
            "before divine intervention can take place. God does not measure the complexity of our arguments; "
            "He responds to the genuine posture of our surrender. When human striving stops, heaven introduces a higher sound."
        )
        p3 = (
            f"The spiritual truth is timeless: {self.quote} When you lay down the exhausting urge to orchestrate "
            "every outcome on your own, God's peace establishes an atmosphere where victory is already settled."
        )

        return {
            "title": self.title,
            "subtitle": "On letting faith speak when human words fail, and the quiet power of the secret place.",
            "essay_paragraphs": [p1, p2, p3],
            "date_str": today_date,
            "gemini_captions": None
        }

    def generate_multi_platform_captions(self, gemini_captions: dict = None) -> dict:
        """Ensures all 5 platforms have pristine copy."""
        if gemini_captions and gemini_captions.get("instagram"):
            return {
                "instagram": gemini_captions.get("instagram", "").strip(),
                "whatsapp": gemini_captions.get("whatsapp", "").strip(),
                "twitter": gemini_captions.get("twitter", "").strip(),
                "threads": gemini_captions.get("threads", "").strip(),
                "facebook": gemini_captions.get("facebook", "").strip()
            }

        # High-Standard Fallback Captions
        ig = (
            f"When words are not enough, let your worship speak.\n\n"
            f"There are moments when pressure tries to dictate your thoughts. But Scripture reminds us: "
            f"'{self.quote}'\n\n"
            f"Lay down the need to figure out every detail today. Anchor your heart in His presence.\n\n"
            f"— {self.scripture} • {self.speaker}\n\n"
            f"#TheKingdomJournal #MorningPrayer #SecretPlace #WorshipAsWarfare #FaithOverFear "
            f"#ApostleJoshuaSelman #NathanielBassey #KingdomMindset #ChristianCreatives #DailyWord"
        )

        wa = (
            f"Good morning my friend. A quiet word for your morning:\n\n"
            f"“{self.quote}”\n\n"
            f"If you've felt overwhelmed or unsure of what to pray today, don't force human striving. "
            f"God hears the posture of your heart louder than any spoken sentence.\n\n"
            f"📖 “{self.scripture}”\n\n"
            f"Step into today with peace. Forward this to someone who needs strength this morning! ✨"
        )

        tw = (
            f"Adoration is not an escape from spiritual conflict—it is the decisive enthronement "
            f"of God's presence over the strongholds of fear.\n\n"
            f"Rest in His covenant today. 🕊️\n\n"
            f"— {self.scripture}"
        )

        th = (
            f"A quiet thought for this morning:\n\n"
            f"Most people think prayer is only effective when they have all the right words. "
            f"Scripture teaches the opposite. In Romans 8:26, the deepest intercession happens "
            f"when human words run dry and the Spirit steps in.\n\n"
            f"“{self.quote}”\n\n"
            f"Whatever feels heavy right now, you don't have to carry it alone. What are you trusting God for today?"
        )

        fb = (
            f"“{self.quote}” ({self.scripture})\n\n"
            f"There are seasons when human capacity reaches its end, and words simply are not enough. "
            f"In those moments, your worship becomes your deepest prayer. When you choose thanksgiving "
            f"in the face of pressure, you anchor your soul in God's unbroken peace.\n\n"
            f"May His strength meet you at the point of your need today. Have a blessed and favored day!"
        )

        return {
            "instagram": ig,
            "whatsapp": wa,
            "twitter": tw,
            "threads": th,
            "facebook": fb
        }

if __name__ == "__main__":
    engine = HumanizedContentEngine(
        quote="Adoration is not an escape from spiritual conflict, but the decisive enthronement of God's presence over the strongholds of darkness.",
        speaker="Nathaniel Bassey & Apostle Joshua Selman",
        scripture="2 Chronicles 20:22",
        title="Worship as Spiritual Warfare"
    )
    essay = engine.generate_editorial_micro_essay()
    print("\n--- HUMANIZED ESSAY RESULT ---")
    print("Title:", essay["title"])
    print("Subtitle:", essay["subtitle"])
    print("Paragraphs count:", len(essay["essay_paragraphs"]))
    captions = engine.generate_multi_platform_captions(essay.get("gemini_captions"))
    print("Instagram preview:\n", captions["instagram"][:150], "...")
