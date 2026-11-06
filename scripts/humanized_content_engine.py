"""
Gemini-Powered Humanized Editorial Content & Social Kit Engine
Strict Integrity Architecture:
1. Clear separation of Editorial Axiom (The Kingdom Journal) vs Verbatim Scripture vs Thematic Inspirations.
2. Verbatim Scripture retrieved from ScriptureEngine with translation labels.
3. Multi-platform distinct copy (Reel Script, IG Caption, WhatsApp Devotional, Twitter Aphorism, Threads Reflection).
4. Zero fabricated quotes or false pastor attributions.
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
sys.path.insert(0, str(BASE_DIR / "scripts"))
import scripture_engine

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
    def __init__(self, editorial_axiom: str, scripture_ref: str, inspirations: str = None, title: str = None):
        load_env()
        self.editorial_axiom = editorial_axiom.strip()
        self.scripture_ref = scripture_ref or "Matthew 6:6"
        self.inspirations = inspirations or "Dunsin Oyekan & Apostle Joshua Selman"
        self.title = title or self._derive_title(self.editorial_axiom)
        self.api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        
        # Retrieve verbatim scripture
        self.scripture_data = scripture_engine.get_scripture(self.scripture_ref)
        self.verbatim_scripture_text = self.scripture_data["text"]
        self.scripture_display_ref = f"{self.scripture_data['reference']} [{self.scripture_data['translation']}]"

    def _derive_title(self, text: str) -> str:
        words = text.split()
        if len(words) <= 5:
            return text.title()
        return " ".join(words[:5]).title()

    def generate_all_with_gemini(self) -> dict:
        """Invokes Gemini with strict journalistic & theological integrity rules."""
        if not self.api_key:
            return None

        prompt = f"""You are the Executive Editor of 'The Kingdom Journal', a high-class Christian publication.
Synthesize an editorial publication package based on these verified inputs:

INPUTS:
- Editorial Theme: "{self.title}"
- Editorial Axiom: "{self.editorial_axiom}"
- Verbatim Scripture Text: "{self.verbatim_scripture_text}" ({self.scripture_display_ref})
- Thematic Ministers (Inspirations only, NOT authors of the quote): "{self.inspirations}"

INTEGRITY & ATTRIBUTION RULES:
1. NEVER attribute the Editorial Axiom to the ministers. The ministers are thematic inspirations from today's worship radar; the axiom is authored by The Kingdom Journal.
2. The Scripture reference is {self.scripture_display_ref}. Use the exact verbatim text: "{self.verbatim_scripture_text}".
3. ABSOLUTELY NO AI bullet lists (NO "1/", "2/", "3/"), NO syllabus outlines ("Here are 3 principles").
4. Provide high-class, contemplative prose in the voice of A.W. Tozer with modern African worship reverence.
5. Create DISTINCT platform copy (avoid repeating the exact same sentence everywhere).

OUTPUT JSON STRUCTURE:
{{
  "title": "{self.title}",
  "subtitle": "Evocative, italicized one-sentence subtitle exploring the spiritual tension.",
  "essay_paragraphs": [
    "First paragraph setting the contemplative theological foundation...",
    "Second paragraph reflecting on {self.scripture_display_ref} and the biblical narrative...",
    "Third paragraph articulating the editorial principle of surrender and peace..."
  ],
  "reel_script": {{
    "hook": "Visual and spoken hook for the first 3 seconds",
    "voiceover": "Concise 15-second spoken voiceover delivering the core revelation",
    "call_to_action": "Closing 5-second action and reflection prompt"
  }},
  "instagram": "Compelling caption with narrative opening, scripture reflection, reflection question, and 8 relevant hashtags.",
  "whatsapp": "Warm personal devotional starting with 'Grace and peace to you today.', followed by verbatim scripture in italics and an uplifting reflection.",
  "twitter": "Sharp, memorable aphorism under 220 characters with 2 relevant hashtags.",
  "threads": "Engaging community question and theological thought under 450 characters.",
  "facebook": "Pastoral devotional for a Christian community group."
}}
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
                with urllib.request.urlopen(req, timeout=18) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    content_text = data["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = json.loads(content_text)
                    print(f"[GEMINI ENGINE] Successfully generated humanized editorial package via {model}")
                    return parsed
            except Exception as e:
                print(f"[GEMINI ENGINE NOTICE] Model {model} pass: {e}", file=sys.stderr)
                continue

        return None

    def generate_editorial_micro_essay(self) -> dict:
        """Generates editorial package with fallback to verified deterministic literary prose."""
        now = datetime.now()
        day_num = now.day # No zero-padded day
        date_str = f"{now.strftime('%A')}, {now.strftime('%B')} {day_num}, {now.year}"

        gemini_result = self.generate_all_with_gemini()
        if gemini_result and "essay_paragraphs" in gemini_result:
            return {
                "title": gemini_result.get("title", self.title),
                "subtitle": gemini_result.get("subtitle", "On the quiet power of consecration."),
                "essay_paragraphs": gemini_result.get("essay_paragraphs", []),
                "date_str": date_str,
                "editorial_axiom": self.editorial_axiom,
                "verbatim_scripture": self.verbatim_scripture_text,
                "scripture_display_ref": self.scripture_display_ref,
                "inspirations": self.inspirations,
                "gemini_captions": {
                    "instagram": gemini_result.get("instagram", ""),
                    "reel_script": gemini_result.get("reel_script", {}),
                    "whatsapp": gemini_result.get("whatsapp", ""),
                    "twitter": gemini_result.get("twitter", ""),
                    "threads": gemini_result.get("threads", ""),
                    "facebook": gemini_result.get("facebook", "")
                }
            }

        # Deterministic Literary Fallback with Strict Attribution Integrity
        p1 = (
            "There are seasons in every believer's walk where human vocabulary reaches its natural limit. "
            "You begin your day carrying burdens that cannot be neatly filed away into bulleted petitions, "
            "and the weight of what lies ahead defies effortless explanation."
        )
        p2 = (
            f"Scripture reminds us in {self.scripture_display_ref}: “{self.verbatim_scripture_text}” "
            "The kingdom has never demanded polished eloquence before divine help can intervene. "
            "God does not measure the complexity of our sentences; He responds to the quiet posture of our surrender."
        )
        p3 = (
            f"The editorial truth is timeless: {self.editorial_axiom} "
            "When you lay down the exhausting urge to orchestrate every outcome through human striving, "
            "His peace establishes an atmosphere where victory is already settled."
        )

        return {
            "title": self.title,
            "subtitle": "On letting faith speak when human words fail, and the quiet power of consecration.",
            "essay_paragraphs": [p1, p2, p3],
            "date_str": date_str,
            "editorial_axiom": self.editorial_axiom,
            "verbatim_scripture": self.verbatim_scripture_text,
            "scripture_display_ref": self.scripture_display_ref,
            "inspirations": self.inspirations,
            "gemini_captions": None
        }

    def generate_multi_platform_captions(self, gemini_captions: dict = None) -> dict:
        """Produces distinct, non-redundant copy for every platform."""
        if gemini_captions and gemini_captions.get("instagram"):
            rs = gemini_captions.get("reel_script", {})
            reel_str = ""
            if isinstance(rs, dict) and rs.get("hook"):
                reel_str = f"🎬 REEL SCRIPT (30s):\n• [0-3s Hook]: {rs.get('hook')}\n• [3-20s Audio]: {rs.get('voiceover')}\n• [20-30s CTA]: {rs.get('call_to_action')}\n\n"

            # Enforce Twitter character limit (< 240 chars)
            tw = gemini_captions.get("twitter", "").strip()
            if len(tw) > 240:
                tw = tw[:236] + "..."

            # Enforce Threads character limit (< 480 chars)
            th = gemini_captions.get("threads", "").strip()
            if len(th) > 480:
                th = th[:476] + "..."

            return {
                "instagram": gemini_captions.get("instagram", "").strip(),
                "reel_script": reel_str.strip(),
                "whatsapp": gemini_captions.get("whatsapp", "").strip(),
                "twitter": tw,
                "threads": th,
                "facebook": gemini_captions.get("facebook", "").strip()
            }

        # High-Integrity Deterministic Fallbacks (Distinct Across Platforms)
        ig = (
            f"What God builds in secret cannot be dismantled in public.\n\n"
            f"We live in a culture obsessed with public visibility. Yet throughout Scripture, heaven's greatest "
            f"deliverances were forged away from the spotlight.\n\n"
            f"📖 “{self.verbatim_scripture_text}” — {self.scripture_display_ref}\n\n"
            f"Take a moment today to step away from the noise and anchor your soul in His presence. "
            f"What is one area of your life where you need to choose quiet trust over human striving today?\n\n"
            f"Inspired by today's worship sessions by {self.inspirations}.\n\n"
            f"#TheKingdomJournal #SecretPlace #MorningPrayer #ChristianDevotional #KingdomMindset #FaithOverFear"
        )

        reel_script = (
            f"🎬 REEL SCRIPT (30s):\n"
            f"• [0-3s Hook]: (Show believer kneeling in quiet morning prayer) 'Stop trying to win publicly what you haven't prayed through privately.'\n"
            f"• [3-20s Audio Voiceover]: 'Spiritual authority is not acquired on public stages. It is forged in the silence of deep consecration. When human striving stops, God's peace takes over.'\n"
            f"• [20-30s CTA]: 'Build your altar first. Save this reminder for your morning devotion.'"
        )

        wa = (
            f"Grace and peace to you today.\n\n"
            f"A quiet reflection for your day:\n"
            f"“{self.verbatim_scripture_text}”\n"
            f"— {self.scripture_display_ref}\n\n"
            f"If you've felt drained or overwhelmed, don't force human striving. "
            f"God honours the posture of your heart louder than any spoken sentence.\n\n"
            f"Step into today with His peace. Forward this to someone who needs strength today! ✨"
        )

        tw = (
            f"Spiritual authority is never seized on public stages; it is received at the altar of quiet consecration.\n\n"
            f"“{self.scripture_display_ref}”\n"
            f"#KingdomJournal #Faith"
        )

        th = (
            f"A quiet thought for today:\n\n"
            f"Most people think authority comes from visibility and public recognition. "
            f"Scripture teaches the exact opposite in {self.scripture_display_ref}: true kingdom weight "
            f"is cultivated in the secret place when nobody is watching.\n\n"
            f"What are you building in the secret place this season?"
        )

        fb = (
            f"“{self.verbatim_scripture_text}” — {self.scripture_display_ref}\n\n"
            f"There are seasons when human capacity reaches its natural limit, and words simply are not enough. "
            f"In those moments, your quiet trust becomes your deepest prayer. When you choose surrender in the face "
            f"of pressure, you anchor your soul in God's unbroken peace.\n\n"
            f"May His strength meet you at the point of your need today. Have a blessed and favored day!"
        )

        return {
            "instagram": ig,
            "reel_script": reel_script,
            "whatsapp": wa,
            "twitter": tw,
            "threads": th,
            "facebook": fb
        }

if __name__ == "__main__":
    engine = HumanizedContentEngine(
        editorial_axiom="Spiritual authority is not acquired on public stages; it is forged in the silence of deep consecration.",
        scripture_ref="Matthew 6:6",
        inspirations="Dunsin Oyekan & Apostle Joshua Selman",
        title="The Protocol of the Secret Place"
    )
    essay = engine.generate_editorial_micro_essay()
    print("Title:", essay["title"])
    print("Scripture:", essay["scripture_display_ref"])
    print("Verbatim Text:", essay["verbatim_scripture"])
    caps = engine.generate_multi_platform_captions(essay.get("gemini_captions"))
    print("\nReel Script:\n", caps["reel_script"].encode('ascii', 'replace').decode())
    print("\nWhatsApp:\n", caps["whatsapp"][:100].encode('ascii', 'replace').decode(), "...")
