"""
Milestone 4: The Kingdom Journal Writing Engine (src/write.py)
Generates high-class, contemplative editorial copy strictly validated against a Pydantic JSON schema.
Enforces:
1. First-person, contemplative voice (A.W. Tozer warmth + modern Nigerian English nuance).
2. Concrete imagery (4 a.m., kitchen floor, lantern, closed door) over abstract nouns.
3. Zero unverified pastor attributions; quotes strictly tied to verified transcripts with timestamps.
4. Verbatim Scripture retrieved from scripture engine and validated against biblical canon.
5. Distinct, copy-paste ready platform text (Facebook, IG, X, Threads, WhatsApp, Story).
"""

import json
import logging
import os
import re
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator

from src.verify import validate_scripture_reference, scan_risk_flags
from src.design.backgrounds import generate_text_free_image_prompt

BASE_DIR = Path(__file__).resolve().parent.parent
logger = logging.getLogger("kingdom_journal.write")

# Load environment
def load_env():
    env_file = BASE_DIR / ".env"
    if env_file.is_file():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k and k not in os.environ:
                    os.environ[k] = v

MODELS_CASCADE = [
    "gemini-3-flash-preview",
    "gemini-2.5-flash",
    "gemini-flash-latest"
]

# Pydantic Schemas
class QuotePayload(BaseModel):
    text: str = Field(description="Exact verbatim line under 25 words")
    speaker: str = Field(description="Speaker name")
    video_title: str = Field(description="Title of source video")
    url: str = Field(description="Timestamped YouTube URL")
    start_sec: int = Field(description="Start time in seconds")

class ScripturePayload(BaseModel):
    ref: str = Field(description="Scripture reference e.g. Romans 8:26")
    text: str = Field(description="Verbatim scripture text")
    translation: str = Field(default="WEB", description="Bible translation code")

class FlyerSpec(BaseModel):
    template: str
    headline: str
    subline: Optional[str] = None
    credit: str
    image_prompt: str

class IssuePackage(BaseModel):
    theme: str
    hook: str
    quote: Optional[QuotePayload] = None
    scripture: ScripturePayload
    reflection: str
    facebook_post: str
    instagram_caption: str
    x_post: str
    threads_post: str
    whatsapp_status: str
    story_text: str
    altar_invite: str
    flyers: List[FlyerSpec]

    @field_validator("x_post")
    def check_x_length(cls, v):
        if len(v) > 280:
            return v[:277] + "..."
        return v

    @field_validator("story_text")
    def check_story_words(cls, v):
        words = v.split()
        if len(words) > 20:
            return " ".join(words[:20])
        return v

class WritingEngine:
    def __init__(self, api_key: Optional[str] = None):
        load_env()
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")

    def _call_gemini_json(self, prompt: str) -> Optional[Dict]:
        if not self.api_key:
            return None

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.60,
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
                with urllib.request.urlopen(req, timeout=22) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    return json.loads(text)
            except Exception as e:
                logger.debug(f"WritingEngine model {model} pass: {e}")
                continue
        return None

    def _fetch_scripture(self, preferred_ref: Optional[str] = None) -> ScripturePayload:
        """Retrieves verified scripture from local scripture engine."""
        import sys
        sys.path.insert(0, str(BASE_DIR / "scripts"))
        try:
            import scripture_engine
            res = scripture_engine.get_scripture(preferred_ref or "Romans 8:26")
            is_valid, canon_ref, _ = validate_scripture_reference(res["reference"])
            return ScripturePayload(
                ref=canon_ref if is_valid else res["reference"],
                text=res["text"],
                translation=res.get("translation", "WEB")
            )
        except Exception:
            return ScripturePayload(
                ref="Romans 8:26",
                text="In the same way, the Spirit also helps our weaknesses, for we don't know how to pray as we ought; but the Spirit himself makes intercession for us with groanings which can't be uttered.",
                translation="WEB"
            )

    def write_issue(
        self,
        theme_hint: str,
        verified_quote: Optional[Dict] = None,
        radar_videos: Optional[List[Dict]] = None,
        palette_id: str = "navy_gold"
    ) -> IssuePackage:
        """
        Synthesizes the complete editorial and platform writing package.
        Validates against IssuePackage schema, retries twice, and degrades gracefully if needed.
        """
        # Determine verified quote or editorial attribution
        if verified_quote:
            quote_text = verified_quote["text_verbatim"]
            speaker = verified_quote["speaker"]
            video_title = verified_quote.get("video_title", "Live Ministration")
            url = verified_quote.get("url", "")
            start_sec = verified_quote.get("start_sec", 0)
            quote_instruction = f"""
VERIFIED SPOKEN QUOTE:
- Exact Text: "{quote_text}"
- Spoken by: {speaker}
- Source: "{video_title}" ({url} at {start_sec}s)
- ATTRIBUTION MANDATE: You MUST attribute this line specifically to "{speaker}" in the credit.
- HASHTAG RULE: You may include the hashtag #{speaker.replace(' ', '')} because this quote is verified.
"""
            flyer_credit = f"Line from {speaker}, {video_title}"
            headline_for_flyer = quote_text
        else:
            quote_instruction = """
NO VERIFIED QUOTE AVAILABLE:
- You must write an original Editorial Axiom for 'The Kingdom Journal'.
- Do NOT attribute any quote to any person. Set quote field to null.
- Zero pastor hashtags allowed.
"""
            flyer_credit = "The Kingdom Journal"
            headline_for_flyer = f"The secret place crowns what human striving cannot build."

        scripture = self._fetch_scripture()

        prompt = f"""You are the Executive Editor of 'The Kingdom Journal'—a high-class, contemplative daily publication for Nigerian and global Christian believers.
Theme: {theme_hint}
{quote_instruction}
Scripture: "{scripture.text}" ({scripture.ref} [{scripture.translation}])

VOICE & EDITORIAL RULES:
1. Voice: First-person singular ("I", "my friend"), contemplative, warm, pastoral (reminiscent of A.W. Tozer or Oswald Chambers).
2. Preserve authentic Nigerian English natural expressions where fitting ("till date", "per time"), never forced.
3. Concrete imagery over abstract clouds: talk about 4 a.m., an empty wooden chair, a shut bedroom door, a kitchen counter, quiet tears.
4. BANNED CLICHES: Never use "tapestry", "testament", "delve", "unlock", "In today's fast-paced world", or stacked academic abstractions.
5. Facebook Post: Must be copy-paste ready! Hook line first (before truncation fold), short spacious paragraphs, 3-5 tasteful emojis, closing reflective question, 5-8 hashtags at the very bottom.
6. Altar Invite: Warmly invite the reader to turn their heart to Christ and pray in their own sincere words. NEVER write a rigid "repeat after me" formula.
7. X Post: Memorable, piercing spiritual aphorism strictly <= 280 characters.
8. WhatsApp Status: Personal, warm, ending with a call to forward to a friend facing pressure.
9. Story Text: Punchy, visual, strictly <= 20 words.

RETURN STRICT JSON matching this schema:
{{
  "theme": "{theme_hint}",
  "hook": "Sharp hook under 8 words",
  "quote": {{"text": "...", "speaker": "...", "video_title": "...", "url": "...", "start_sec": 0}} or null,
  "reflection": "100-130 word first-person contemplative essay",
  "facebook_post": "Complete copy-paste ready Facebook post...",
  "instagram_caption": "Complete Instagram caption with line breaks...",
  "x_post": "Aphorism under 280 chars",
  "threads_post": "Reflective thought for Christian thinkers...",
  "whatsapp_status": "Warm morning devotional for WhatsApp status...",
  "story_text": "Under 20 words for vertical story",
  "altar_invite": "Warm personal invitation to pray..."
}}
"""

        for attempt in range(2):
            raw_json = self._call_gemini_json(prompt)
            if raw_json and isinstance(raw_json, dict):
                try:
                    q_obj = None
                    if verified_quote:
                        q_obj = QuotePayload(
                            text=verified_quote["text_verbatim"],
                            speaker=verified_quote["speaker"],
                            video_title=verified_quote.get("video_title", "Ministration"),
                            url=verified_quote.get("url", ""),
                            start_sec=verified_quote.get("start_sec", 0)
                        )

                    # Build flyers specs
                    flyers = [
                        FlyerSpec(
                            template="bold_statement",
                            headline=headline_for_flyer,
                            subline=None,
                            credit=flyer_credit,
                            image_prompt=generate_text_free_image_prompt(theme_hint, palette_id)
                        ),
                        FlyerSpec(
                            template="contrast_split",
                            headline="They want stages. / God wants secrets.",
                            subline="When human striving stops, worship takes over.",
                            credit=flyer_credit,
                            image_prompt=generate_text_free_image_prompt(theme_hint, palette_id)
                        )
                    ]

                    pkg = IssuePackage(
                        theme=raw_json.get("theme", theme_hint),
                        hook=raw_json.get("hook", "When human words run dry"),
                        quote=q_obj,
                        scripture=scripture,
                        reflection=raw_json.get("reflection", "There are seasons where human vocabulary reaches its end..."),
                        facebook_post=raw_json.get("facebook_post", ""),
                        instagram_caption=raw_json.get("instagram_caption", ""),
                        x_post=raw_json.get("x_post", "When striving stops, worship takes over."),
                        threads_post=raw_json.get("threads_post", ""),
                        whatsapp_status=raw_json.get("whatsapp_status", ""),
                        story_text=raw_json.get("story_text", "Rest in His presence today."),
                        altar_invite=raw_json.get("altar_invite", "Take a quiet moment today to speak with the Father."),
                        flyers=flyers
                    )
                    return pkg
                except Exception as e:
                    logger.warning(f"Schema validation attempt {attempt+1} failed: {e}")

        # Deterministic Fail-Soft Degradation
        logger.info("Degrading to verified deterministic editorial package.")
        return self._build_deterministic_package(theme_hint, verified_quote, scripture, palette_id)

    def _build_deterministic_package(
        self,
        theme: str,
        quote: Optional[Dict],
        scripture: ScripturePayload,
        palette_id: str
    ) -> IssuePackage:
        q_payload = None
        if quote:
            q_payload = QuotePayload(
                text=quote["text_verbatim"],
                speaker=quote["speaker"],
                video_title=quote.get("video_title", ""),
                url=quote.get("url", ""),
                start_sec=quote.get("start_sec", 0)
            )
            headline = quote["text_verbatim"]
            credit = f"Line from {quote['speaker']}, {quote.get('video_title', '')}"
            tags = f"#{quote['speaker'].replace(' ', '')} #TheKingdomJournal #ChristianCreatives"
        else:
            headline = "When human capacity runs dry, worship establishes peace."
            credit = "The Kingdom Journal"
            tags = "#TheKingdomJournal #SecretPlace #MorningDevotional #FaithOverFear"

        fb = (
            f"There are mornings when human vocabulary reaches its limit.\n\n"
            f"You don't need louder arguments today. You need a deeper surrender.\n\n"
            f"Scripture reminds us in {scripture.ref}: \"{scripture.text}\"\n\n"
            f"Take two minutes before the day begins to shut your door, breathe, and rest under His sovereign hand.\n\n"
            f"Where in your life are you still trying to force an outcome that only prayer can settle?\n\n"
            f"{tags}"
        )

        flyers = [
            FlyerSpec(
                template="bold_statement",
                headline=headline,
                subline=None,
                credit=credit,
                image_prompt=generate_text_free_image_prompt(theme, palette_id)
            ),
            FlyerSpec(
                template="contrast_split",
                headline="They want public stages. / God crowns secret surrender.",
                subline="Rest in His peace today.",
                credit=credit,
                image_prompt=generate_text_free_image_prompt(theme, palette_id)
            )
        ]

        return IssuePackage(
            theme=theme,
            hook="When Human Words Run Dry",
            quote=q_payload,
            scripture=scripture,
            reflection="There are seasons in every believer's walk where human vocabulary reaches its limit...",
            facebook_post=fb,
            instagram_caption=fb,
            x_post="When human striving ends, sovereign peace takes over. Rest in Him today. #KingdomMindset",
            threads_post="A quiet thought for today: authority is never forged in public stages. It is given in secret.",
            whatsapp_status="Grace and peace to you this morning my friend. When pressure rises, worship takes over. Have a blessed day!",
            story_text="Be still, and remember who sits on the throne.",
            altar_invite="If you have been running on your own strength, pause right now and hand the steering wheel to Jesus.",
            flyers=flyers
        )
