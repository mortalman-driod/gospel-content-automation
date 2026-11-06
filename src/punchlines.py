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
        speaker = video_meta.get("channel_title") or video_meta.get("channel", "Unknown Speaker")

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
        
        # Build prompt containing timestamped chunks
        chunks_formatted = []
        for c in chunks[:35]: # Limit to first 35 minutes to stay within token context
            chunks_formatted.append(f"[{c['start_sec']}s - {c['end_sec']}s]: {c['text']}")
        transcript_sample = "\n".join(chunks_formatted)

        prompt = f"""You are a strict Theological Copy Editor analyzing a gospel sermon transcript.
Video Title: "{title}"
Speaker: "{speaker}"

Analyze the following transcript excerpt and extract up to 8 candidate PUNCHLINES.

CRITICAL RULES:
1. text_verbatim MUST BE THE EXACT WORDS SPOKEN in the transcript. Do NOT edit, polish, embellish, or paraphrase.
2. Word count MUST be between 6 and 25 words.
3. Must stand completely alone as a powerful quote without needing context.
4. Must possess contrast, reversal, a vivid concrete metaphor, or a direct spiritual command (e.g. "They want stages. God wants secrets.").
5. REJECT private personal anecdotes, stories about specific individuals, or local church announcements.
6. STRICTLY REJECT any line making prosperity promises, instant miracles, guaranteed visas/healing/money, or financial seed declarations.

TRANSCRIPT EXCERPT:
{transcript_sample}

RETURN STRICT JSON ARRAY:
[
  {{
    "start_sec": 120,
    "text_verbatim": "exact words spoken",
    "structure": "contrast | reversal | metaphor | command | question | declaration",
    "word_count": 12,
    "why_it_works": "1-sentence explanation of the spiritual punch"
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
            quote_record = {
                "video_id": video_id,
                "speaker": speaker,
                "video_title": title,
                "start_sec": actual_start,
                "text_verbatim": q_text,
                "structure": cand.get("structure", "declaration"),
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

        # Sort verified quotes: priority to contrast/reversal, high match score, optimal length (8-18 words)
        def score_quote(q):
            length_bonus = 1.0 if 8 <= q["word_count"] <= 18 else 0.8
            structure_bonus = 1.2 if q["structure"] in ["contrast", "reversal", "metaphor"] else 1.0
            return q["match_score"] * length_bonus * structure_bonus

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
