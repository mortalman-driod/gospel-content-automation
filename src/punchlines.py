"""
Milestone 2: Punchline Extraction & Verification Engine (src/punchlines.py)
Extracts standalone spoken punchlines (6-25 words) from transcripts using Gemini,
and strictly enforces code-level fuzzy verification (ratio >= 0.92) against raw transcript tokens.
Never fabricates, paraphrases, or attributes unverified text to real speakers.
"""

import json
import logging
import os
import re
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from src.verify import (
    fuzzy_verify_quote,
    scan_risk_flags,
    format_timestamp_url
)

logger = logging.getLogger("kingdom_journal.punchlines")
BASE_DIR = Path(__file__).resolve().parent.parent

MODELS_CASCADE = [
    "gemini-3-flash-preview",
    "gemini-2.5-flash",
    "gemini-flash-latest"
]

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

CHANNEL_PREACHER_MAP = {
    "koinonia global": "Apostle Joshua Selman",
    "koinonia": "Apostle Joshua Selman",
    "joshua selman": "Apostle Joshua Selman",
    "apostle joshua selman": "Apostle Joshua Selman",
    "emmanuel iren": "Pastor Emmanuel Iren",
    "celebration church international": "Pastor Emmanuel Iren",
    "dunsin oyekan": "Dunsin Oyekan",
    "nathaniel bassey": "Nathaniel Bassey",
    "nathaniel bassey main": "Nathaniel Bassey",
    "victoria orenze": "Victoria Orenze",
    "theophilus sunday": "Theophilus Sunday",
    "sunmisola agbebi": "Sunmisola Agbebi",
    "moses bliss": "Moses Bliss",
    "harvesters": "Pastor Bolaji Idowu",
    "harvesters tv": "Pastor Bolaji Idowu",
    "elevation church": "Pastor Godman Akinlabi",
    "the elevation church": "Pastor Godman Akinlabi",
    "daystar": "Pastor Sam Adeyemi",
    "sam adeyemi": "Pastor Sam Adeyemi",
    "covenant christian centre": "Pastor Poju Oyemade",
    "poju oyemade": "Pastor Poju Oyemade",
    "celebration church tv": "Pastor Emmanuel Iren",
    "celebration church": "Pastor Emmanuel Iren",
    "streams of joy": "Pastor Jerry Eze",
    "streams of joy international": "Pastor Jerry Eze",
    "jerry eze": "Pastor Jerry Eze",
    "pastor jerry eze": "Pastor Jerry Eze",
    "the god life club": "Pastor Chingtok Ishaku",
    "chingtok ishaku": "Pastor Chingtok Ishaku"
}

def resolve_speaker_name(title: str, channel: str) -> str:
    """Resolves authentic minister name from title and channel; never returns raw channel/program titles."""
    clean_channel = (channel or "").strip().lower()
    for k, v in CHANNEL_PREACHER_MAP.items():
        if k in clean_channel:
            return v

    clean_title = (title or "").strip()
    for k, v in CHANNEL_PREACHER_MAP.items():
        if k in clean_title.lower():
            return v

    match = re.search(r'\b(Apostle|Pastor|Minister|Evangelist|Bishop|Rev\.|Dr\.)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})', clean_title)
    if match:
        return f"{match.group(1)} {match.group(2)}"

    banned_channel_words = ["tv", "media", "ministries", "global", "church", "network", "assembly", "highlights", "channel", "broadcast", "music", "records", "sounds", "official", "sessions"]
    if any(bw in clean_channel for bw in banned_channel_words):
        return "The Kingdom Journal"

    return channel or "The Kingdom Journal"

def chunk_transcript(snippets: List[Dict], target_seconds: int = 60) -> List[Dict]:
    """
    Groups transcript snippets into ~60-second temporal windows.
    Returns: [{start_sec: int, end_sec: int, text: str}]
    """
    if not snippets:
        return []

    chunks = []
    current_text = []
    chunk_start = float(snippets[0].get("start", 0.0))
    chunk_end = chunk_start

    for snip in snippets:
        snip_start = float(snip.get("start", 0.0))
        snip_dur = float(snip.get("duration", 0.0))
        text = snip.get("text", "").strip()

        if not text:
            continue

        if (snip_start + snip_dur) - chunk_start >= target_seconds and current_text:
            chunks.append({
                "start_sec": int(chunk_start),
                "end_sec": int(chunk_end),
                "text": " ".join(current_text)
            })
            current_text = [text]
            chunk_start = snip_start
            chunk_end = snip_start + snip_dur
        else:
            current_text.append(text)
            chunk_end = snip_start + snip_dur

    if current_text:
        chunks.append({
            "start_sec": int(chunk_start),
            "end_sec": int(chunk_end),
            "text": " ".join(current_text)
        })

    return chunks

class PunchlineExtractor:
    def __init__(self, api_key: Optional[str] = None):
        load_env()
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")

    def _call_gemini_json(self, prompt: str) -> Optional[dict | list]:
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not configured.")
            return None

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.3, # Low temperature for accurate extraction
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
                with urllib.request.urlopen(req, timeout=20) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = json.loads(text)
                    logger.info(f"Punchline extraction prompt answered by {model}")
                    return parsed
            except Exception as e:
                logger.debug(f"Gemini model {model} pass: {e}")
                continue

        return None

    def extract_punchlines(
        self,
        video_meta: Dict,
        raw_transcript: Optional[List[Dict]]
    ) -> Dict:
        """
        Extracts and verifies punchlines from a video transcript.
        Returns:
            {
                "video_id": str,
                "video_title": str,
                "speaker": str,
                "candidates": list,
                "verified_quotes": list,
                "primary_quote": dict or None,
                "alternate_quote": dict or None,
                "status": "verified" | "degraded_no_transcript" | "degraded_no_verified_quote"
            }
        """
        video_id = video_meta.get("id") or video_meta.get("video_id")
        title = video_meta.get("title", "")
        raw_speaker = video_meta.get("channel_title") or video_meta.get("channel", "")
        speaker = resolve_speaker_name(title, raw_speaker)

        # Fallback if no transcript is available
        if not raw_transcript:
            logger.info(f"No transcript for video {video_id}. Degraded fail-soft mode active.")
            return {
                "video_id": video_id,
                "video_title": title,
                "speaker": speaker,
                "candidates": [],
                "verified_quotes": [],
                "primary_quote": None,
                "alternate_quote": None,
                "status": "degraded_no_transcript",
                "note": "Transcript was unavailable. Editorial reflections only; no quotes attributed."
            }

        # Check for single manual entry directly
        if len(raw_transcript) == 1 and raw_transcript[0].get("manual_entry"):
            manual = raw_transcript[0]
            q_text = manual["text"]
            speaker = manual.get("speaker") or speaker
            verified_quote = {
                "video_id": video_id,
                "speaker": speaker,
                "video_title": manual.get("video_title") or title,
                "start_sec": int(manual["start"]),
                "text_verbatim": q_text,
                "structure": "manual_verified",
                "word_count": len(q_text.split()),
                "url": format_timestamp_url(video_id, int(manual["start"])),
                "match_score": 1.0,
                "verified": True
            }
            return {
                "video_id": video_id,
                "video_title": title,
                "speaker": speaker,
                "candidates": [verified_quote],
                "verified_quotes": [verified_quote],
                "primary_quote": verified_quote,
                "alternate_quote": None,
                "status": "verified"
            }

        # Chunk transcript
        chunks = chunk_transcript(raw_transcript, target_seconds=60)
        
        # Sample evenly across the entire sermon (intro, core teaching, and closing altar charge)
        if len(chunks) <= 45:
            sampled_chunks = chunks
        else:
            step = len(chunks) / 45.0
            sampled_chunks = [chunks[int(i * step)] for i in range(45)]

        chunks_formatted = [
            f"[{c['start_sec']}s - {c['end_sec']}s]: {c['text']}"
            for c in sampled_chunks
        ]
        transcript_sample = "\n".join(chunks_formatted)

        prompt = f"""You are an Editorial Art Director and Theological Curator looking for HIGHLY INSPIRING Christian quotes suitable for viral social-media flyers.
Video Title: "{title}"
Speaker: "{speaker}"

Analyze the transcript excerpts and extract up to 8 candidate INSPIRATIONAL PUNCHLINES.

CRITICAL SELECTION RULES:
1. text_verbatim MUST BE THE EXACT WORDS SPOKEN in the transcript. Do NOT edit, polish, embellish, or paraphrase.
2. Word count MUST be between 7 and 20 words so it fits cleanly on a visual flyer with massive readability.
3. HIGH INSPIRATION & STANDALONE CLARITY: Every quote MUST immediately uplift, strengthen faith, ignite hope, or deliver timeless spiritual wisdom (themes like faith, grace, purpose, stillness, resilience, love, God's faithfulness).
4. STRICTLY REJECT unfinished conversational clauses or awkward setup fragments starting with "When there are...", "So when you...", "The prayer becomes...", "And that's why...", "Because if...", "Let me tell you...". Pick clean, complete, memorable sentences!
5. Prioritize vivid contrast, reversal, imagery, or bold affirmation (e.g., "They want stages. God wants secrets.", "Your private altar determines your public strength.").
6. REJECT private personal anecdotes, church housekeeping, crowd greetings, or prosperity/instant-miracle guarantees.

TRANSCRIPT EXCERPT:
{transcript_sample}

RETURN STRICT JSON ARRAY:
[
  {{
    "start_sec": 120,
    "text_verbatim": "exact words spoken",
    "structure": "contrast | reversal | metaphor | affirmation | declaration",
    "inspiration_score": 9,
    "word_count": 12,
    "why_it_works": "1-sentence explanation of why readers will save and share this quote"
  }}
]
"""

        raw_candidates = self._call_gemini_json(prompt) or []
        if isinstance(raw_candidates, dict) and "candidates" in raw_candidates:
            raw_candidates = raw_candidates["candidates"]

        candidates = []
        verified_quotes = []

        for cand in raw_candidates:
            if not isinstance(cand, dict) or "text_verbatim" not in cand:
                continue

            q_text = cand["text_verbatim"].strip()
            claimed_start = cand.get("start_sec", 0)
            words = q_text.split()
            word_len = len(words)

            # Word count guard (6-25 words)
            if word_len < 6 or word_len > 25:
                continue

            # Risk flags guard
            risk_flags = scan_risk_flags(q_text)
            if risk_flags:
                logger.warning(f"Candidate rejected due to risk flags: {q_text} ({risk_flags})")
                continue

            # CODE-LEVEL FUZZY VERIFICATION
            is_verified, score, match_meta = fuzzy_verify_quote(
                q_text,
                raw_transcript,
                threshold=0.92,
                claimed_start_sec=claimed_start
            )

            actual_start = match_meta["start_sec"] if match_meta else claimed_start
            insp_raw = cand.get("inspiration_score", 7)
            try:
                insp_val = max(1, min(10, int(insp_raw)))
            except Exception:
                insp_val = 7

            quote_record = {
                "video_id": video_id,
                "speaker": speaker,
                "video_title": title,
                "start_sec": actual_start,
                "text_verbatim": q_text,
                "structure": cand.get("structure", "declaration"),
                "inspiration_score": insp_val,
                "word_count": word_len,
                "why_it_works": cand.get("why_it_works", ""),
                "url": format_timestamp_url(video_id, actual_start),
                "match_score": score,
                "verified": is_verified,
                "low_confidence": (0.80 <= score < 0.92)
            }
            candidates.append(quote_record)

            if is_verified:
                verified_quotes.append(quote_record)

        def score_quote(q):
            low = q["text_verbatim"].lower().strip()
            length_bonus = 1.15 if 7 <= q["word_count"] <= 16 else (1.0 if q["word_count"] <= 20 else 0.72)
            structure_bonus = 1.18 if q["structure"] in ["contrast", "reversal", "metaphor", "affirmation"] else 1.0
            insp_factor = 0.65 + 0.055 * q.get("inspiration_score", 7)

            uplift_words = {
                "faith", "grace", "hope", "peace", "strength", "purpose", "god", "light",
                "mercy", "wisdom", "love", "patience", "courage", "trust", "anchor", "renew",
                "victory", "promise", "still", "faithful", "eternal", "secret", "altar"
            }
            uplift_hits = sum(1 for w in uplift_words if re.search(r"\b" + re.escape(w) + r"\b", low))
            uplift_bonus = min(1.20, 1.0 + uplift_hits * 0.05)

            # Penalize unfinished conversational clauses that read flat on posters
            fragment_starts = (
                "when there are ", "so when ", "and when ", "because if ", "that is why ",
                "that's why ", "the prayer becomes", "so if you ", "and then ", "now watch"
            )
            fragment_penalty = 0.55 if low.startswith(fragment_starts) else 1.0

            final_score = q["match_score"] * length_bonus * structure_bonus * insp_factor * uplift_bonus * fragment_penalty
            q["poster_score"] = round(final_score, 4)
            return final_score

        verified_quotes.sort(key=score_quote, reverse=True)

        primary_quote = verified_quotes[0] if verified_quotes else None
        alternate_quote = verified_quotes[1] if len(verified_quotes) > 1 else None

        status = "verified" if primary_quote else "degraded_no_verified_quote"
        note = None if primary_quote else "Could not verify candidate quotes with ratio >= 0.92. Degraded to editorial reflection only."

        return {
            "video_id": video_id,
            "video_title": title,
            "speaker": speaker,
            "candidates": candidates,
            "verified_quotes": verified_quotes,
            "primary_quote": primary_quote,
            "alternate_quote": alternate_quote,
            "status": status,
            "note": note
        }
