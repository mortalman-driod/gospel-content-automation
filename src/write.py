"""
Milestone 4: Institutional Editorial & Copywriting Engine (src/write.py)
Transforms verified transcripts and thematic hints into high-converting,
pastorally rich social assets across 6 rotating storytelling frameworks.
Strictly eliminates all bot hallmarks, channel/program mentions, and enforces SSOT quote parity.
"""

import json
import logging
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator

from src.verify import validate_scripture_reference, scan_risk_flags
from src.scripture import get_scripture_for_theme
from src.design.backgrounds import generate_text_free_image_prompt

BASE_DIR = Path(__file__).resolve().parent.parent
logger = logging.getLogger("kingdom_journal.write")

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

def clean_theme_title(raw_title: str) -> str:
    """Strips broadcast dates, day numbers, session markers, and returns clean spiritual theme."""
    if not raw_title:
        return "The Secret Place"
    t = re.sub(r'\|\|.*?\|\|', '', raw_title)
    t = re.sub(r'\(.*?\)', '', t)
    t = re.sub(r'\[.*?\]', '', t)
    t = re.sub(r'\b(DAY\s+\d+|PART\s+\d+|SESSION\s+\d+|EPISODE\s+\d+|202[0-9])\b', '', t, flags=re.IGNORECASE)
    t = re.sub(r'\b(LIVE|BROADCAST|MINISTRATION|STREAM|FASTING|ONLINE)\b', '', t, flags=re.IGNORECASE)
    parts = [p.strip() for p in re.split(r'[-|:]', t) if p.strip()]
    for p in parts:
        words = p.split()
        if 2 <= len(words) <= 6:
            return p.strip().title()
    return "The Secret Place"

MODELS_CASCADE = [
    "gemini-3-flash-preview",
    "gemini-2.5-flash",
    "gemini-flash-latest"
]

STORYTELLING_FRAMEWORKS = [
    {
        "id": "paradigm_shift",
        "name": "The Paradigm Shift / Counter-Intuitive Truth",
        "guidance": (
            "NARRATIVE ANGLE: The Paradigm Shift.\n"
            "- Challenge a conventional religious assumption (e.g. that delay means denial, that God's silence is absence, or that spiritual authority comes through noise and crowds).\n"
            "- Reframe the listener's perspective with quiet, piercing biblical truth.\n"
            "- BANNED TROPE: Do NOT mention sitting at 4 a.m., cold wood palms, or kitchen counters."
        )
    },
    {
        "id": "visceral_everyday",
        "name": "The Visceral Everyday Tension",
        "guidance": (
            "NARRATIVE ANGLE: The Visceral Everyday Tension.\n"
            "- Ground the spiritual truth in modern daily life: staring at an overdue invoice, sitting in motionless evening traffic, navigating a strained workplace conversation, or feeling the heavy silence of an unanswered message.\n"
            "- Show how God's presence invades ordinary, imperfect moments rather than idealized retreats.\n"
            "- BANNED TROPE: Do NOT mention sitting at 4 a.m., cold wood palms, or kitchen counters."
        )
    },
    {
        "id": "spiritual_diagnosis",
        "name": "The Spiritual Diagnosis & Surrender",
        "guidance": (
            "NARRATIVE ANGLE: The Spiritual Diagnosis & Surrender.\n"
            "- Act as a tender physician of the soul. Diagnose the root of spiritual fatigue: subtle self-reliance, trying to carry what only sovereign shoulders were built to bear, or the exhausting cycle of spiritual performance.\n"
            "- Lead the reader gently into the relief of releasing control to Christ.\n"
            "- BANNED TROPE: Do NOT mention sitting at 4 a.m., cold wood palms, or kitchen counters."
        )
    },
    {
        "id": "biblical_drama",
        "name": "The Biblical Dramatic Scene",
        "guidance": (
            "NARRATIVE ANGLE: The Biblical Dramatic Scene.\n"
            "- Immerse the reader inside a visceral biblical moment with vivid cinematic texture: Peter stepping onto the dark, icy swell of Galilee; Paul and Silas singing through torn flesh at midnight in Philippi; Elijah curled under the broom tree receiving warm bread from an angel; or the disciples behind locked doors when Jesus suddenly stands among them.\n"
            "- Bridge that ancient scene directly to the reader's battle today.\n"
            "- BANNED TROPE: Do NOT mention sitting at 4 a.m., cold wood palms, or kitchen counters."
        )
    },
    {
        "id": "prophetic_exhortation",
        "name": "The Urgent Prophetic Exhortation",
        "guidance": (
            "NARRATIVE ANGLE: The Urgent Prophetic Exhortation.\n"
            "- A stirring clarion call to rise up, break agreements with defeat, shake off spiritual lethargy, refuse mediocrity, and step boldly into kingdom inheritance.\n"
            "- Bold, energetic, hopeful, commanding.\n"
            "- BANNED TROPE: Do NOT mention sitting at 4 a.m., cold wood palms, or kitchen counters."
        )
    },
    {
        "id": "contemplative_sanctuary",
        "name": "The Intimate Contemplative Sanctuary",
        "guidance": (
            "NARRATIVE ANGLE: The Intimate Contemplative Sanctuary.\n"
            "- Deep stillness, awe, beholding the majesty and gentle sovereignty of God.\n"
            "- Contemplative devotion in the tradition of A.W. Tozer or Andrew Murray: learning to be quiet before Him until our inner storm subsides.\n"
            "- BANNED TROPE: Do NOT mention sitting at 4 a.m., cold wood palms, or kitchen counters."
        )
    }
]

# Pydantic Schemas
class QuotePayload(BaseModel):
    text: str = Field(description="Exact verbatim line under 25 words")
    speaker: str = Field(description="Speaker name")
    video_title: str = Field(description="Title of source video (internal audit only)")
    url: str = Field(description="Timestamped YouTube URL")
    start_sec: int = Field(description="Start time in seconds")

class ScripturePayload(BaseModel):
    ref: str = Field(description="Scripture reference e.g. Hebrews 11:1")
    text: str = Field(description="Verbatim scripture text")
    translation: str = Field(default="WEB", description="Bible translation code")

class FlyerSpec(BaseModel):
    template: str
    headline: str
    subline: Optional[str] = None
    credit: str
    image_prompt: str
    scripture_badge: Optional[str] = None
    scripture_ref: Optional[str] = None
    headline_pre: Optional[str] = None
    accent_word: Optional[str] = None
    accent_color: Optional[str] = "yellow"
    background_archetype: Optional[str] = "cross_sunrise"

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
    # Structured Viral Poster Fields
    viral_headline_pre: Optional[str] = Field(default=None, description="Hook phrase preceding accent word")
    viral_accent_word: Optional[str] = Field(default=None, description="Dominant viral accent punchline word/phrase")
    viral_accent_color: Optional[str] = Field(default="yellow", description="Accent color: 'yellow' or 'red'")
    viral_subline: Optional[str] = Field(default=None, description="2-3 line comforting rhythmic pastoral subline")
    viral_background_archetype: Optional[str] = Field(default="cross_sunrise", description="Archetype canvas")

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

    def _fetch_scripture(
        self,
        theme: str = "",
        quote_text: str = "",
        preferred_ref: Optional[str] = None
    ) -> ScripturePayload:
        """Retrieves verified scripture dynamically matched to sermon theme with zero monoculture defaults."""
        try:
            res = get_scripture_for_theme(theme=theme, quote_text=quote_text, preferred_ref=preferred_ref)
            is_valid, canon_ref, _ = validate_scripture_reference(res["reference"])
            return ScripturePayload(
                ref=canon_ref if is_valid else res["reference"],
                text=res["text"],
                translation=res.get("translation", "WEB")
            )
        except Exception as e:
            logger.warning(f"Scripture retrieval fallback: {e}")
            return ScripturePayload(
                ref="Psalm 119:105",
                text="Your word is a lamp to my feet, and a light for my path.",
                translation="WEB"
            )

    def write_issue(
        self,
        theme_hint: str,
        verified_quote: Optional[Dict] = None,
        radar_videos: Optional[List[Dict]] = None,
        palette_id: str = "navy_gold",
        issue_number: int = 1
    ) -> IssuePackage:
        """
        Synthesizes the complete editorial and platform writing package.
        Validates against IssuePackage schema, retries twice, and degrades gracefully if needed.
        """
        clean_theme = clean_theme_title(theme_hint)
        # Determine storytelling framework based on issue number
        framework = STORYTELLING_FRAMEWORKS[issue_number % len(STORYTELLING_FRAMEWORKS)]

        # Determine verified quote or editorial attribution
        if verified_quote:
            quote_text = verified_quote["text_verbatim"]
            speaker = verified_quote["speaker"]
            quote_instruction = f"""
VERIFIED SPOKEN INSIGHT:
- Exact Verbatim Line: "{quote_text}"
- Spoken by: {speaker}
- MANDATE: Treat this ministration strictly as a spiritual inspiration point to draw out timeless kingdom virality.
- STRICT EXCLUSION: NEVER mention or output any YouTube channel names or video broadcast titles in the copy, reflections, captions, or flyer credits!
- You may refer to {speaker} by name (e.g. 'As {speaker} shared...'), but NEVER cite program titles or broadcast channels.
- ATTRIBUTION MANDATE: Credit line on flyers must be strictly "— {speaker}".
- HASHTAG RULE: You may include #{speaker.replace(' ', '')} because this insight is verified.
"""
            flyer_credit = f"— {speaker}"
            headline_for_flyer = quote_text
        else:
            quote_instruction = """
NO VERIFIED QUOTE AVAILABLE:
- You must write an original Editorial Axiom for 'The Kingdom Journal'.
- Do NOT attribute any quote to any preacher. Set quote field to null.
- Zero pastor hashtags allowed.
- Attribution must be strictly 'The Kingdom Journal'.
"""
            flyer_credit = "The Kingdom Journal"
            headline_for_flyer = "When human striving ends, sovereign peace takes over."

        # Dynamically fetch scripture contextually matched to today's sermon theme
        scripture = self._fetch_scripture(theme=clean_theme, quote_text=headline_for_flyer)

        prompt = f"""You are the Executive Editor of 'The Kingdom Journal'—a high-class, contemplative daily publication for Nigerian and global Christian believers.
Theme: {clean_theme}
{quote_instruction}
Scripture: "{scripture.text}" ({scripture.ref} [{scripture.translation}])

STORYTELLING ANGLE (TODAY'S MANDATED FRAMEWORK):
Framework: {framework['name']}
{framework['guidance']}

VOICE & EDITORIAL RULES:
1. Voice: First-person singular ("I", "my friend"), contemplative, warm, pastoral (reminiscent of A.W. Tozer or Oswald Chambers).
2. Preserve authentic Nigerian English natural expressions where fitting ("till date", "per time"), never forced.
3. BANNED CLICHES & TROPES:
   - Absolutely NO "sitting at 4 a.m. with cold wood palms on my kitchen counter" or repeating kitchen floor/counter narratives!
   - Never use "tapestry", "testament", "delve", "unlock", "In today's fast-paced world", or stacked academic abstractions.
4. ABSOLUTE CHANNEL/PROGRAM PROHIBITION: Never write out YouTube channel names or video program titles in any post, reflection, or caption.
   - HASHTAG PURITY: Absolutely NO hashtags created from video/program titles or channel names (e.g. NO #DailyPropheticPrayers, NO #TheGeneralAssembly, NO #TACTV). Use only timeless spiritual tags like #TheKingdomJournal #Prayer #HolySpirit #Grace #Faith #SecretPlace.
5. Facebook Post: Must be copy-paste ready! Hook line first (before truncation fold), short spacious paragraphs, 3-5 tasteful emojis, closing reflective question, 5-8 hashtags at the very bottom.
6. Altar Invite: Warmly invite the reader to turn their heart to Christ and pray in their own sincere words. NEVER write a rigid "repeat after me" formula.
7. X Post: Memorable, piercing spiritual aphorism strictly <= 280 characters.
8. WhatsApp Status: Personal, warm, ending with a call to forward to a friend facing pressure.
9. Story Text: Punchy, visual, strictly <= 20 words.
10. Viral Flyer Copy:
    - viral_headline_pre: The hook phrase leading into the punchline
    - viral_accent_word: The dominant contrast punchline word or phrase
    - viral_accent_color: 'yellow' or 'red'
    - viral_subline: 2-3 lines of rhythmic, comforting pastoral wisdom
    - viral_background_archetype: Choose from 'cross_sunrise', 'open_bible', 'mountain_summit', 'green_sprout', 'royal_crown', 'study_desk'.

RETURN STRICT JSON matching this schema:
{{
  "theme": "{clean_theme}",
  "hook": "Sharp hook under 8 words",
  "quote": {{"text": "...", "speaker": "...", "video_title": "...", "url": "...", "start_sec": 0}} or null,
  "reflection": "100-130 word first-person contemplative essay following today's narrative framework",
  "facebook_post": "Complete copy-paste ready Facebook post...",
  "instagram_caption": "Complete Instagram caption with line breaks...",
  "x_post": "Aphorism under 280 chars",
  "threads_post": "Reflective thought for Christian thinkers...",
  "whatsapp_status": "Warm morning devotional for WhatsApp status...",
  "story_text": "Under 20 words for vertical story",
  "altar_invite": "Warm personal invitation to pray...",
  "viral_headline_pre": "Hook phrase before accent word",
  "viral_accent_word": "Accent punchline word",
  "viral_accent_color": "yellow",
  "viral_subline": "2-3 rhythmic pastoral lines",
  "viral_background_archetype": "cross_sunrise"
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

                    # Parse viral fields with SSOT synchronization
                    v_pre = raw_json.get("viral_headline_pre")
                    v_acc = raw_json.get("viral_accent_word")
                    v_col = raw_json.get("viral_accent_color", "yellow")
                    v_sub = raw_json.get("viral_subline", "When human striving ends, divine illumination takes over.")
                    v_arch = raw_json.get("viral_background_archetype", "cross_sunrise")

                    if not v_pre or not v_acc:
                        words = headline_for_flyer.split()
                        if len(words) > 3:
                            v_pre = " ".join(words[:-2])
                            v_acc = " ".join(words[-2:])
                        else:
                            v_pre = words[0] if words else "Trust in God"
                            v_acc = "always."

                    # Build flyers specs carrying dynamic scripture anchor
                    flyers = [
                        FlyerSpec(
                            template="viral_quote_poster",
                            headline=headline_for_flyer,
                            subline=v_sub,
                            credit=flyer_credit,
                            image_prompt=generate_text_free_image_prompt(theme_hint, palette_id),
                            scripture_badge=scripture.ref,
                            scripture_ref=scripture.ref,
                            headline_pre=v_pre,
                            accent_word=v_acc,
                            accent_color=v_col,
                            background_archetype=v_arch
                        ),
                        FlyerSpec(
                            template="modern_quote_card",
                            headline=headline_for_flyer,
                            subline=None,
                            credit=flyer_credit,
                            image_prompt=generate_text_free_image_prompt(theme_hint, palette_id),
                            scripture_badge=scripture.ref,
                            scripture_ref=scripture.ref,
                            headline_pre=v_pre,
                            accent_word=v_acc,
                            accent_color=v_col,
                            background_archetype=v_arch
                        )
                    ]

                    pkg = IssuePackage(
                        theme=clean_theme_title(raw_json.get("theme", clean_theme)),
                        hook=raw_json.get("hook", "When human words run dry"),
                        quote=q_obj,
                        scripture=scripture,
                        reflection=raw_json.get("reflection", "In the stillness of prayer, we discover that God's grace speaks louder than our fears."),
                        facebook_post=raw_json.get("facebook_post", ""),
                        instagram_caption=raw_json.get("instagram_caption", ""),
                        x_post=raw_json.get("x_post", "When striving ends, prayer begins."),
                        threads_post=raw_json.get("threads_post", ""),
                        whatsapp_status=raw_json.get("whatsapp_status", ""),
                        story_text=raw_json.get("story_text", "Rest in His peace."),
                        altar_invite=raw_json.get("altar_invite", "Take a quiet moment right where you are to turn your burdens over to Jesus."),
                        flyers=flyers,
                        viral_headline_pre=v_pre,
                        viral_accent_word=v_acc,
                        viral_accent_color=v_col,
                        viral_subline=v_sub,
                        viral_background_archetype=v_arch
                    )
                    return pkg
                except Exception as e:
                    logger.warning(f"Schema validation attempt {attempt+1} failed: {e}")

        # Deterministic Fail-Soft Degradation
        logger.info("Degrading to verified deterministic editorial package.")
        return self._build_deterministic_package(theme_hint, verified_quote, scripture, palette_id, framework)

    def _build_deterministic_package(
        self,
        theme: str,
        quote: Optional[Dict],
        scripture: ScripturePayload,
        palette_id: str,
        framework: Optional[Dict] = None
    ) -> IssuePackage:
        if framework is None:
            framework = STORYTELLING_FRAMEWORKS[0]

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
            credit = f"— {quote['speaker']}"
            tags = f"#{quote['speaker'].replace(' ', '')} #TheKingdomJournal #ChristianCreatives"
        else:
            headline = "When human capacity runs dry, worship establishes peace."
            credit = "The Kingdom Journal"
            tags = "#TheKingdomJournal #SecretPlace #MorningDevotional #FaithOverFear"

        fb = (
            f"There are moments when human vocabulary reaches its limit.\n\n"
            f"You don't need louder arguments today. You need a deeper surrender.\n\n"
            f"Scripture reminds us in {scripture.ref}: \"{scripture.text}\"\n\n"
            f"Take two minutes before the rush of the day to breathe and rest under His sovereign hand.\n\n"
            f"Where in your life are you still trying to force an outcome that only prayer can settle?\n\n"
            f"{tags}"
        )

        words = headline.split()
        if len(words) > 3:
            v_pre = " ".join(words[:-2])
            v_acc = " ".join(words[-2:])
        else:
            v_pre = "There is divine glory in"
            v_acc = "quiet surrender."

        flyers = [
            FlyerSpec(
                template="viral_quote_poster",
                headline=headline,
                subline="When human striving ends, divine illumination takes over.",
                credit=credit,
                image_prompt=generate_text_free_image_prompt(theme, palette_id),
                scripture_badge=scripture.ref,
                scripture_ref=scripture.ref,
                headline_pre=v_pre,
                accent_word=v_acc,
                accent_color="yellow",
                background_archetype="cross_sunrise"
            ),
            FlyerSpec(
                template="modern_quote_card",
                headline="They want public stages. / God crowns secret surrender.",
                subline="Rest in His peace today.",
                credit=credit,
                image_prompt=generate_text_free_image_prompt(theme, palette_id),
                scripture_badge=scripture.ref,
                scripture_ref=scripture.ref,
                headline_pre=v_pre,
                accent_word=v_acc,
                accent_color="yellow",
                background_archetype="cross_sunrise"
            )
        ]

        return IssuePackage(
            theme=theme,
            hook="When Human Words Run Dry",
            quote=q_payload,
            scripture=scripture,
            reflection=(
                f"I used to believe that faith meant having an answer for every crisis. But the older I get in God, "
                f"the more I realize that peace is found when our questions run out of breath.\n\n"
                f"In {scripture.ref}, God promises that His word remains our lamp and guide. Not a spotlight ten miles ahead, "
                f"but a gentle lamp for the very next step. Stop demanding to see the whole horizon. "
                f"Trust the Shepherd for today."
            ),
            facebook_post=fb,
            instagram_caption=(
                f"You don't need louder striving today. You need quiet surrender.\n\n"
                f"\"{headline}\" {credit}\n\n"
                f"Scripture: {scripture.ref} — \"{scripture.text}\"\n\n"
                f"Drop an Amen if you are resting in His timing today.\n\n"
                f"{tags}"
            ),
            x_post=f"{headline} {credit} #TheKingdomJournal"[:280],
            threads_post=(
                f"A profound lesson from today's secret place: {headline}\n\n"
                f"True spiritual strength is rarely loud. It is the steady conviction that God is at work even when we cannot see the outcome."
            ),
            whatsapp_status=(
                f"🕊️ *Morning Devotional • The Kingdom Journal*\n\n"
                f"\"{headline}\"\n\n"
                f"📖 *{scripture.ref}:* \"{scripture.text}\"\n\n"
                f"Whatever feels heavy this morning, hand it over to Him. Share this with someone who needs peace today."
            ),
            story_text="God is working behind the scenes for you.",
            altar_invite="If you need peace today, pause where you are: 'Lord Jesus, I surrender my striving into Your hands.'",
            flyers=flyers,
            viral_headline_pre=v_pre,
            viral_accent_word=v_acc,
            viral_accent_color="yellow",
            viral_subline="When human striving ends, divine illumination takes over.",
            viral_background_archetype="cross_sunrise"
        )
