"""
Gemini-Powered Humanized Editorial Content & Caption Engine
Trained specifically for 'The Kingdom Journal' to produce luxury de-AI'd prose
and platform-tailored social copy using Google Gemini 2.5 Flash.
"""

import json
import os
import re
import sys
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

class HumanizedContentEngine:
    def __init__(self, quote: str, speaker: str = None, scripture: str = None, title: str = None):
        load_env()
        self.quote = quote.strip()
        self.speaker = speaker or "Nathaniel Bassey & Apostle Joshua Selman"
        self.scripture = scripture or "Psalm 46:5 • Isaiah 40:31"
        self.title = title or self._derive_title(self.quote)
        self.api_key = os.environ.get("GEMINI_API_KEY", "").strip()

    def _derive_title(self, quote: str) -> str:
        if "," in quote:
            first_clause = quote.split(",")[0].strip()
            if len(first_clause.split()) <= 7:
                return first_clause.title()
        words = quote.split()
        if len(words) <= 6:
            return quote.title()
        return " ".join(words[:6]).title()

    def generate_all_with_gemini(self) -> dict:
        """Invokes Gemini 2.5 Flash with the trained Kingdom Journal editorial persona."""
        if not self.api_key:
            return None

        prompt = f"""You are the Executive Editor and Creative Director for 'The Kingdom Journal', a luxury Christian morning publication.
Transform this quote and biblical context into a refined, humanized editorial package.

CORE INPUT:
- Quote: "{self.quote}"
- Speaker: "{self.speaker}"
- Scripture: "{self.scripture}"

STRICT EDITORIAL RULES:
1. ABSOLUTELY NO robotic bullet points (NO "1/", "2/", "3/", NO "Point 1:").
2. ABSOLUTELY NO syllabus outlines (NO "Here are 3 spiritual principles...", NO "In this email, we explore 3 keys...").
3. ABSOLUTELY NO AI clichés (NO "In today's fast-paced world...", NO "Have you ever wondered...", NO "It's not about X, it's about Y").
4. Maintain the contemplative theological depth of A.W. Tozer combined with the vibrant spiritual warmth of contemporary African gospel leaders (Nathaniel Bassey, Joshua Selman, Victoria Orenze, Mercy Chinwo).
5. Produce JSON output with exact keys:
   - "title": Evocative, literary title (4 to 6 words).
   - "subtitle": Italicized editorial subtitle explaining the spiritual tension.
   - "essay_paragraphs": Array of 3 to 4 narrative paragraphs of high-class prose exploring the scripture and quote without bullets.
   - "instagram": Full caption with striking hook in first 70 chars, line breaks, quote block, and 14 targeted hashtags.
   - "whatsapp": Warm, personal devotional broadcast starting "Good morning my friend. A quiet word for your morning:", scripture in italics, and a gentle forward prompt.
   - "twitter": Sharp aphorism under 240 characters with maximum punchiness.
   - "threads": Narrative thought ending with an engaging community reflection question.
   - "facebook": Thoughtful pastoral devotional for a faith community.
"""

        import time
        for attempt in range(2):
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "responseMimeType": "application/json",
                        "temperature": 0.65,
                        "topP": 0.95
                    }
                }
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=25) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    content_text = data["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = json.loads(content_text)
                    parsed["date_str"] = datetime.now().strftime("%A, %B %d, %Y")
                    print(f"[GEMINI ENGINE SUCCESS] Generated humanized editorial content for '{parsed.get('title')}'")
                    return parsed
            except Exception as e:
                if attempt == 0:
                    time.sleep(2)
                    continue
                print(f"[GEMINI ENGINE NOTICE] Falling back to deterministic model: {e}", file=sys.stderr)
                return None

    def generate_editorial_micro_essay(self) -> dict:
        """Tries Gemini first, falls back to deterministic template."""
        gemini_result = self.generate_all_with_gemini()
        if gemini_result and "essay_paragraphs" in gemini_result:
            return {
                "title": gemini_result.get("title", self.title),
                "subtitle": gemini_result.get("subtitle", "On divine help in quiet seasons."),
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

        # Deterministic High-Class Fallback
        today_date = datetime.now().strftime("%A, %B %d, %Y")
        essay = (
            f"There are seasons in every believer's walk where human vocabulary reaches its natural limit. "
            f"You begin your morning with burdens that cannot be neatly filed away into bulleted petitions, "
            f"and the weight of what you carry defies easy explanation.\n\n"
            f"In the eighth chapter of Romans, the Apostle Paul provides a profound consolation for this exact posture: "
            f"the Spirit Himself intercedes for us with groanings that cannot be uttered. "
            f"The kingdom has never demanded that you present polished eloquence before God can move on your behalf. "
            f"He does not measure the complexity of your sentences; He responds to the genuine surrender of your heart.\n\n"
            f"Throughout Scripture, whenever human capacity ran completely dry, heaven introduced a higher sound. "
            f"At the fourth watch of the night, when exhaustion peaked, divine help arrived. "
            f"When Jehoshaphat had no military solution left, worshippers were sent to the front lines. "
            f"When Paul and Silas were locked in the deepest dungeon, they did not debate their circumstances—they began to sing hymns to God at midnight.\n\n"
            f"Drawing from today's live worship ministrations across our fellowship, the spiritual truth is unmistakable: "
            f"<strong>{self.quote}</strong> When human striving stops, divine intervention takes over. "
            f"Lay down the need to orchestrate the outcome today, and let your worship establish His peace."
        )

        return {
            "title": self.title,
            "subtitle": "On letting faith speak when human words fail, and the quiet power of the secret place.",
            "essay_paragraphs": essay.split("\n\n"),
            "date_str": today_date,
            "gemini_captions": None
        }

    def generate_multi_platform_captions(self, gemini_captions: dict = None) -> dict:
        if gemini_captions and all(gemini_captions.values()):
            return gemini_captions

        quote = self.quote
        speaker = self.speaker
        scripture = self.scripture

        instagram = (
            f"{quote}.\n\n"
            f"There are days when human vocabulary isn't enough. You don't have the words to explain the pressure, "
            f"and you don't have the energy to formulate a polished argument.\n\n"
            f"Here is what Scripture reminds us in Romans 8:26: The Spirit Himself intercedes for us with groanings that words cannot express.\n\n"
            f"God never asked you to carry every outcome on your own shoulders. When human striving stops, worship takes over.\n\n"
            f"Take 2 minutes this morning to step away from the noise, anchor your heart in His presence, and remember who remains on the throne.\n\n"
            f"“{quote}”\n"
            f"— {scripture} • {speaker}\n\n"
            f"#DivineHelp #WorshipInSpirit #SecretPlace #MorningPrayer #ApostleJoshuaSelman #VictoriaOrenze "
            f"#NathanielBassey #MercyChinwo #FaithOverFear #KingdomMindset #ChristianCreatives #NigerianGospel #PraiseAndWorship #DailyWord"
        )

        whatsapp = (
            f"Good morning my friend. A quiet word for your morning:\n\n"
            f"“{quote}”\n\n"
            f"If you've felt drained, overwhelmed, or unsure of what to pray today, don't force human striving. "
            f"God hears the posture of your heart louder than any spoken sentence.\n\n"
            f"📖 “The Lord is near to all who call upon Him in truth.” — Psalm 145:18\n\n"
            f"Step into today with peace. Forward this to someone who needs strength this morning! ✨"
        )

        twitter = (
            f"{quote}.\n\n"
            f"When human capacity reaches its limit, you don't need louder arguments—you need deeper surrender.\n\n"
            f"Rest in His covenant today. 🕊️"
        )

        threads = (
            f"A quiet thought for this morning:\n\n"
            f"Most people think prayer is only effective when they have all the right words.\n\n"
            f"Scripture teaches the opposite. In Romans 8:26, the deepest intercession happens when human words run dry and the Spirit steps in.\n\n"
            f"{quote}.\n\n"
            f"Whatever feels heavy right now, you don't have to carry it alone. What are you trusting God for today?"
        )

        facebook = (
            f"“{quote}” ({scripture})\n\n"
            f"There are seasons when human capacity reaches its end, and words simply are not enough. "
            f"In those moments, your worship becomes your deepest prayer. When you choose thanksgiving in the face of pressure, "
            f"you anchor your soul in God's unbroken peace.\n\n"
            f"May His strength meet you at the point of your need today. Have a blessed and favored day!"
        )

        return {
            "instagram": instagram,
            "whatsapp": whatsapp,
            "twitter": twitter,
            "threads": threads,
            "facebook": facebook
        }

if __name__ == "__main__":
    engine = HumanizedContentEngine(
        quote="When words are not enough, let your worship speak",
        speaker="Mercy Chinwo & Apostle Joshua Selman",
        scripture="Romans 8:26 • Psalm 46:10"
    )
    essay = engine.generate_editorial_micro_essay()
    captions = engine.generate_multi_platform_captions(essay.get("gemini_captions"))
    print("=== FINAL TITLE ===")
    print(essay["title"])
    print("\n=== TWITTER CAPTION ===")
    print(captions["twitter"].encode("ascii", "replace").decode())
    print("\n=== INSTAGRAM HOOK ===")
    print(captions["instagram"][:140].encode("ascii", "replace").decode())
