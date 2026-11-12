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
    "gemini-2.5-flash",
    "gemini-flash-latest",
    "gemini-3-flash-preview",
    "gemini-flash-lite-latest"
]

STORYTELLING_FRAMEWORKS = [
    {
        "id": "concrete_encounter",
        "name": "The Concrete Human Encounter",
        "guidance": (
            "NARRATIVE ANGLE: The Concrete Human Encounter.\n"
            "- OPENING RULE: Open directly with a grounded human situation, dialogue, or specific struggle.\n"
            "- Example: 'A young man spoke with me yesterday, his shoulders slumped under the weight of silent expectations...' or 'I remember speaking with a sister who had prayed for three years without an apparent shift...'\n"
            "- STRICTLY BANNED OPENERS: Never start with 'My friend', 'There are seasons', 'In a world', or 'Have you ever'.\n"
            "- Connect that specific human reality to today's ministration with raw warmth and hope."
        )
    },
    {
        "id": "piercing_paradox",
        "name": "The Piercing Paradoxical Truth",
        "guidance": (
            "NARRATIVE ANGLE: The Piercing Paradoxical Truth.\n"
            "- OPENING RULE: Open directly with a sharp, unexpected, counter-intuitive spiritual truth stated in plain English.\n"
            "- Example: 'Most spiritual burnout does not come from doing too much for God; it comes from carrying what only God was built to shoulder.'\n"
            "- STRICTLY BANNED OPENERS: Never start with 'My friend', 'There are seasons', 'In a world', or 'Have you ever'.\n"
            "- Reframe the listener's perspective with quiet clarity."
        )
    },
    {
        "id": "daily_friction",
        "name": "The Visceral Daily Friction",
        "guidance": (
            "NARRATIVE ANGLE: The Visceral Daily Friction.\n"
            "- OPENING RULE: Open with a vivid, physical anchor from everyday modern life.\n"
            "- Example: 'There is a heavy quiet that settles when the laptop closes at 9:00 p.m. and the house finally goes dark...' or 'Sitting in evening traffic, watching brake lights stretch into the distance, it is easy to wonder if God notices our small, private battles.'\n"
            "- STRICTLY BANNED OPENERS: Never start with 'My friend', 'There are seasons', 'In a world', or 'Have you ever'.\n"
            "- Show how Christ invades ordinary, unglamorous moments."
        )
    },
    {
        "id": "biblical_drama",
        "name": "The Dramatic Biblical Moment",
        "guidance": (
            "NARRATIVE ANGLE: The Dramatic Biblical Moment.\n"
            "- OPENING RULE: Open inside a cinema-grade biblical scene with physical sensory texture.\n"
            "- Example: 'Peter's feet were dripping with cold Galilean spray before his rational mind had even processed that he was walking on water.' or 'In the deepest cell in Philippi, Paul's back was bleeding against stone, yet his voice carried a song.'\n"
            "- STRICTLY BANNED OPENERS: Never start with 'My friend', 'There are seasons', 'In a world', or 'Have you ever'.\n"
            "- Bridge that ancient grit directly to the reader's battle today."
        )
    },
    {
        "id": "pastoral_confession",
        "name": "The Honest Pastoral Confession",
        "guidance": (
            "NARRATIVE ANGLE: The Honest Pastoral Confession.\n"
            "- OPENING RULE: Open with a raw, disarming personal insight from ministry or prayer.\n"
            "- Example: 'For a long time, I treated prayer like an emergency switch instead of a breathing pattern.' or 'It took me years to realize that God is never intimidated by our honest frustration.'\n"
            "- STRICTLY BANNED OPENERS: Never start with 'My friend', 'There are seasons', 'In a world', or 'Have you ever'.\n"
            "- Lead the reader gently into genuine intimacy with God."
        )
    },
    {
        "id": "unvarnished_observation",
        "name": "The Unvarnished Cultural Observation",
        "guidance": (
            "NARRATIVE ANGLE: The Unvarnished Cultural Observation.\n"
            "- OPENING RULE: Open with a sharp, perceptive observation about how people live today.\n"
            "- Example: 'We live in an age obsessed with public announcements, but heaven has always done its heaviest work underground.'\n"
            "- STRICTLY BANNED OPENERS: Never start with 'My friend', 'There are seasons', 'In a world', or 'Have you ever'.\n"
            "- Anchor the observation in biblical hope."
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
    flyer_template: Optional[str] = Field(default="asymmetric_split", description="Template: asymmetric_split, heritage_serif, heavy_impact, quiet_light")
    emotional_tone: Optional[str] = Field(default=None, description="Quote emotion: 'encouragement', 'authority', 'reflection', 'grace', or 'victory'")
    emphasized_words: Optional[List[str]] = Field(default=None, description="1-3 verbatim emotionally critical words/short phrase appearing inside the quote for contrasting display treatment")
    typography_style: Optional[str] = Field(default=None, description="Optional art style: encouragement_brush, authority_condensed, reflection_editorial, grace_calligraphy, victory_statement")

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

        prompt = f"""You are the Executive Editor of 'The Kingdom Journal'—a distinguished, contemplative daily Christian publication.
Your writing must feel 100% human-crafted: authentic, conversational, deeply spiritual, and completely free of AI clichés.

Theme: {clean_theme}
{quote_instruction}
Scripture: "{scripture.text}" ({scripture.ref} [{scripture.translation}])

TODAY'S MANDATED STORYTELLING ANGLE:
{framework['name']}
{framework['guidance']}

VOICE & ANTI-AI EDITORIAL MANDATES:
1. VOICE: Plainspoken, mature, pastoral warmth (like an experienced pastor writing a personal note—zero theatrical AI drama).
2. STRICTLY FORBIDDEN OPENERS & CLICHÉS (ANY USE WILL BE REJECTED):
   - NEVER begin with "My friend", "Good morning, dear one", "There are seasons/moments when...", "In a world...", "Have you ever...", or "A profound lesson...".
   - NEVER invent melodramatic sob stories ("I sat with a crying stranger...") or atmospheric fluff ("breath misting in the dim evening air", "rawest petitions", "unlit corners", "silent expectations", "forged in the crucible").
   - BANNED WORDS: clarion call, spiritual lethargy, lingering in shadows, tapestry, beacon, delve, testament, unlock, embark, harness, intimate sanctuary, gentle sovereign, inner storm, cease striving, myriad, juxtaposition, pivotal, cornerstone, unleash, elevate, profound reminder, resonant, multifaceted, nuanced, profound truth, deep knowing, quietude, clamour, sacred space, deep wellspring, speaks volumes, dear one, re-framing, unveiling.
3. ZERO ANTITHESIS OVERUSE:
   - Do NOT lean on repetitive "This isn't X; it's Y" or "not to X, but to Y" contrasts. State affirmative truth plainly.
4. ZERO DUPLICATE COPY ACROSS CHANNELS (CRITICAL!):
   - NEVER reuse or copy sentences from `reflection` into `facebook_post` or `instagram_caption`. Each field must have its OWN fresh opening line, structure, and voice!
   - `reflection`: Personal morning devotional essay (95-130 words, 2 natural paragraphs, varied sentence lengths).
   - `facebook_post`: Distinct conversational community reflection (different opening, practical application for today's workday, 1 honest question at the end, 2-3 quiet hashtags like #Prayer #Faith).
   - `instagram_caption`: Short poetic mobile caption (40-70 words, 2 crisp micro-stanzas completely distinct from `reflection` and `facebook_post`, 2-3 simple hashtags).
   - `whatsapp_status`: Casual, warm friend-to-friend morning check-in (25-45 words, zero `"dear one"`, 0-1 natural emojis).
   - `x_post`: One crisp standalone sentence strictly <= 240 chars.
   - `threads_post`: Sharp leadership/ministry insight (30-55 words).
5. FLYER ART DIRECTION & VIRAL COLOR CATALOGUE (11 CANVASES):
   Choose the canvas and emotion that create scroll-stopping contrast for today's quote:
   - 'diagonal_royal_gold': Crisp white/silver with navy & gold ribbons -> best for leadership, kingdom victory, clarity, integrity (renders Deep Navy + Crimson/Gold).
   - 'deep_cobalt_wave': Rich royal blue wave + gold curve -> best for authority, hope, triumph, overcoming (renders Crisp White + Electric Solar Yellow).
   - 'emerald_white_wave': Clean ivory paper + forest/lime waves -> best for spiritual growth, fruitfulness, healing, peace (renders Deep Forest Emerald + Crimson/Gold).
   - 'crimson_cream_wave': Warm parchment + bold scarlet waves -> best for urgency, prayer fire, the Cross, consecration (renders Obsidian Black + Vivid Scarlet).
   - 'golden_sunburst_clouds': Warm sunlit sky + amber clouds -> best for worship, dawn mercy, revival, joy (renders Rich Espresso + Copper-Crimson).
   - 'cross_sunrise', 'open_bible', 'mountain_summit', 'green_sprout', 'royal_crown', 'study_desk' also available for photographic themes.
   Return:
   - `flyer_template`: 'asymmetric_split', 'heritage_serif', 'heavy_impact', or 'quiet_light'
   - `emotional_tone`: 'encouragement', 'authority', 'reflection', 'grace', or 'victory'
   - `emphasized_words`: 1-3 exact words present verbatim inside the quote headline to spotlight in contrasting type/color
   - `viral_headline_pre`, `viral_accent_word`, `viral_accent_color` ('yellow', 'red', or 'gold'), `viral_subline` (max 90 chars, NO em-dashes), `viral_background_archetype` (from the 11 canvases above).

RETURN STRICT JSON matching this schema:
{{
  "theme": "{clean_theme}",
  "hook": "Sharp natural hook under 8 words",
  "quote": {{"text": "...", "speaker": "...", "video_title": "...", "url": "...", "start_sec": 0}} or null,
  "reflection": "95-130 word personal devotional essay...",
  "facebook_post": "Distinct conversational Facebook post (NOT copied from reflection)...",
  "instagram_caption": "Distinct concise 40-70 word Instagram caption...",
  "x_post": "One crisp standalone sentence under 240 chars",
  "threads_post": "Sharp leadership reflection...",
  "whatsapp_status": "Natural morning friend-to-friend check-in...",
  "story_text": "Under 16 words for vertical story",
  "altar_invite": "Simple honest closing prayer...",
  "flyer_template": "asymmetric_split",
  "emotional_tone": "encouragement",
  "emphasized_words": ["word1", "word2"],
  "viral_headline_pre": "Hook phrase before accent word",
  "viral_accent_word": "Accent punchline word",
  "viral_accent_color": "gold",
  "viral_subline": "Short clear supporting line under 90 chars",
  "viral_background_archetype": "deep_cobalt_wave"
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
                    if " — " in v_sub:
                        v_sub = v_sub.split(" — ")[0].strip()
                    elif "—" in v_sub:
                        v_sub = v_sub.split("—")[0].strip()
                    v_arch = raw_json.get("viral_background_archetype", "cross_sunrise")
                    v_template = raw_json.get("flyer_template", "asymmetric_split")
                    if v_template not in ("asymmetric_split", "heritage_serif", "heavy_impact", "quiet_light"):
                        v_template = "asymmetric_split"
                    v_tone = raw_json.get("emotional_tone")
                    v_emph = raw_json.get("emphasized_words")
                    if isinstance(v_emph, str):
                        v_emph = [v_emph]
                    v_style = raw_json.get("typography_style")
                    v_tone = raw_json.get("emotional_tone")
                    v_emph = raw_json.get("emphasized_words")
                    if isinstance(v_emph, str):
                        v_emph = [v_emph]
                    v_style = raw_json.get("typography_style")

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
                        viral_background_archetype=v_arch,
                        flyer_template=v_template,
                        emotional_tone=v_tone,
                        emphasized_words=v_emph,
                        typography_style=v_style,
                    )
                    return pkg
                except Exception as e:
                    logger.warning(f"Schema validation attempt {attempt+1} failed: {e}")

        # Deterministic Fail-Soft Degradation
        logger.info("Degrading to verified deterministic editorial package.")
        return self._build_deterministic_package(clean_theme, verified_quote, scripture, palette_id, framework)

    def _build_deterministic_package(
        self,
        theme: str,
        quote: Optional[Dict],
        scripture: ScripturePayload,
        palette_id: str,
        framework: Optional[Dict] = None
    ) -> IssuePackage:
        theme = clean_theme_title(theme)
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

        canvases = [
            "deep_cobalt_wave",
            "diagonal_royal_gold",
            "emerald_white_wave",
            "crimson_cream_wave",
            "golden_sunburst_clouds",
            "cross_sunrise",
            "open_bible",
            "mountain_summit",
            "green_sprout",
            "royal_crown",
            "study_desk",
        ]
        idx_seed = abs(sum(ord(c) for c in f"{theme}{scripture.ref}")) % len(canvases)
        chosen_bg = canvases[idx_seed]
        if quote:
            tags = f"#{quote['speaker'].replace(' ', '')} #Prayer #Faith"
        else:
            tags = "#Prayer #DailyWord #ChristianLiving"

        fb = (
            f"Before checking notifications this morning, read {scripture.ref} slowly: \"{scripture.text}\"\n\n"
            f"Most of us carry pressure into the workday as if outcomes depend solely on our speed. "
            f"Pause before your first call today and ask God to govern what you cannot control.\n\n"
            f"What weight are you choosing to lay down as this week unfolds?\n\n"
            f"{tags}"
        )

        words = headline.split()
        if len(words) > 3:
            v_pre = " ".join(words[:-2])
            v_acc = " ".join(words[-2:])
        else:
            v_pre = "Stand steady in"
            v_acc = "God's peace."

        flyers = [
            FlyerSpec(
                template="viral_quote_poster",
                headline=headline,
                subline="Steady your heart in prayer before the noise begins.",
                credit=credit,
                image_prompt=generate_text_free_image_prompt(theme, palette_id),
                scripture_badge=scripture.ref,
                scripture_ref=scripture.ref,
                headline_pre=v_pre,
                accent_word=v_acc,
                accent_color="gold",
                background_archetype=chosen_bg
            ),
            FlyerSpec(
                template="modern_quote_card",
                headline=headline,
                subline="Rest in His peace today.",
                credit=credit,
                image_prompt=generate_text_free_image_prompt(theme, palette_id),
                scripture_badge=scripture.ref,
                scripture_ref=scripture.ref,
                headline_pre=v_pre,
                accent_word=v_acc,
                accent_color="gold",
                background_archetype=chosen_bg
            )
        ]

        return IssuePackage(
            theme=theme,
            hook="Steady Faith Before The Day Begins",
            quote=q_payload,
            scripture=scripture,
            reflection=(
                f"Quiet mornings carry more spiritual weight than crowded calendars ever will. "
                f"Years of ministry teach you that outward activity runs dry whenever private communion grows thin.\n\n"
                f"Notice how {scripture.ref} anchors today's theme around {theme.lower()}: God guides one clear step at a time. "
                f"Leave yesterday's anxiety on the floor and take today's assignment with a calm, unhurried spirit."
            ),
            facebook_post=fb,
            instagram_caption=(
                f"\"{headline}\" {credit}\n\n"
                f"Carry that sentence with {scripture.ref} into today's commute. One grounded prayer changes the pace of an entire morning.\n\n"
                f"{tags}"
            ),
            x_post=f"{headline} {credit}"[:280],
            threads_post=(
                f"{headline}\n\n"
                f"Public endurance grows straight out of unhurried mornings in the Word ({scripture.ref})."
            ),
            whatsapp_status=(
                f"Good morning. Take sixty quiet seconds with {scripture.ref} before stepping out today: "
                f"\"{scripture.text}\" Wishing you peace and clear direction."
            ),
            story_text="One grounded prayer changes the pace of your morning.",
            altar_invite="Lord Jesus, steady my thoughts this morning and lead every decision ahead of me.",
            flyers=flyers,
            viral_headline_pre=v_pre,
            viral_accent_word=v_acc,
            viral_accent_color="gold",
            viral_subline="Steady your heart in prayer before the noise begins.",
            viral_background_archetype=chosen_bg
        )
