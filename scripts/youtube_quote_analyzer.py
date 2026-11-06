"""
YouTube Video Analyzer & Theological Extraction Engine (Gemini 3.8 Powered)
Pulls live trending Christian gospel ministrations via YouTube Data API v3,
purges all church announcements/promotional noise, and synthesizes 100% proprietary,
authoritative Kingdom principles for 'The Kingdom Journal'.
"""

import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
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

# Strict negative filter for external church announcements, services, and promotional noise
PROMOTIONAL_PATTERNS = [
    r"\bjoin us\b", r"\boutreach\b", r"\bprogram\b", r"\bconvention\b",
    r"\bconference\b", r"\btheme for\b", r"\bwelcome to\b", r"\bregister\b",
    r"\bchurch\b", r"\bheadquarters\b", r"\bbranch\b", r"\bnight of\b",
    r"\bfellowship\b", r"\bairing live\b", r"\blivestream\b", r"\bbroadcast\b",
    r"\bonline service\b", r"\bvenue\b", r"\bdoors open\b", r"\bministering\b",
    r"\bspecial guest\b", r"\bhost:\b", r"\badmission free\b", r"\boffering\b",
    r"\btithe\b", r"\bgiving\b", r"\baccount\b", r"\bsubscribe\b", r"\blike and share\b",
    r"\bclick the link\b", r"\blink in bio\b", r"\bstream on\b", r"\bdownload mp3\b",
    r"\bturn on notifications\b", r"\ball rights reserved\b", r"\bfollow us\b",
    r"\bday \d+\b", r"\bpart \d+\b", r"\bwatch live\b", r"\bzion ministry\b"
]

CURATED_THEMES = [
    {
        "title": "Worship as Spiritual Warfare",
        "hook_top": "When Praise Becomes a Weapon",
        "banner_text": "ENTHRONED IN PRAISE",
        "quote": "Adoration is not an escape from spiritual conflict, but the decisive enthronement of God's presence over the strongholds of darkness.",
        "speaker": "Nathaniel Bassey & Apostle Joshua Selman",
        "scripture": "2 Chronicles 20:22 • Acts 16:25"
    },
    {
        "title": "The Power of the Secret Place",
        "hook_top": "What God Builds in Secret",
        "banner_text": "CONSECRATED IN PRAYER",
        "quote": "What you cultivate in hidden prayer produces the spiritual authority that sustains you in public adversity.",
        "speaker": "Dunsin Oyekan & Victoria Orenze",
        "scripture": "Psalm 91:1 • Matthew 6:6"
    },
    {
        "title": "Divine Help at Break of Day",
        "hook_top": "When Human Striving Stops",
        "banner_text": "HELP AT DAWN",
        "quote": "When human capacity reaches its natural limit, quiet surrender invites the supernatural intervention of God.",
        "speaker": "Victoria Orenze & Apostle Joshua Selman",
        "scripture": "Psalm 46:5 • Isaiah 40:31"
    },
    {
        "title": "Surrender Precedes Victory",
        "hook_top": "The Posture of Kingdom Authority",
        "banner_text": "SURRENDER BRINGS PEACE",
        "quote": "Kingdom authority is never seized by human ambition; it is received at the altar of total surrender.",
        "speaker": "Apostle Joshua Selman & Nathaniel Bassey",
        "scripture": "James 4:7 • Romans 8:26"
    }
]

def synthesize_principle_with_gemini(video_titles: list, channels: list, gemini_key: str) -> dict:
    """Uses Gemini 3.8 Flash (cascading fallback) to synthesize a proprietary, brand-building Kingdom axiom."""
    if not gemini_key:
        return None

    titles_str = "\n".join([f"- {t} (Channel: {c})" for t, c in zip(video_titles[:5], channels[:5])])
    prompt = f"""You are the Chief Theologian and Executive Editor of 'The Kingdom Journal', an elite Christian morning publication.
Analyze these trending Christian worship ministrations and sermons from today:
{titles_str}

TASK:
Synthesize an ORIGINAL, PROPRIETARY, AUTHORITATIVE spiritual principle for today's journal that builds the author's own brand.
This publication does NOT advertise church programs, event dates, or outreach initiatives. It provides timeless kingdom revelation for daily devotions.

STRICT RULES:
1. NEVER use church program words ("Join us", "Outreach", "Night of", "Convention", "Live stream", "Service").
2. Produce an original, deeply contemplative theological axiom in the spirit of A.W. Tozer, Nathaniel Bassey, and Apostle Joshua Selman.
3. Return pure JSON with exact keys:
   - "title": Evocative editorial headline (3 to 5 words, Title Case)
   - "hook_top": Striking declarative opening hook (under 32 chars)
   - "banner_text": 2 to 4 bold words in ALL CAPS
   - "quote": One profound, original, declarative sentence (under 120 chars) that believers will quote and share
   - "speaker": Attribution of spiritual inspirations (e.g., "Nathaniel Bassey & Apostle Joshua Selman")
   - "scripture": Accurate biblical chapter & verse (e.g., "2 Chronicles 20:22 • Acts 16:25")
"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.4
        }
    }

    for model in MODELS_CASCADE:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini_key}"
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=14) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                parsed = json.loads(text)
                
                # Sanity check against promotional text
                quote_text = parsed.get("quote", "")
                if any(re.search(pat, quote_text, re.IGNORECASE) for pat in PROMOTIONAL_PATTERNS):
                    print(f"[ANALYZER NOTICE] Generated quote contained promotional noise, discarding.")
                    continue
                
                print(f"[ANALYZER GEMINI] Successfully synthesized proprietary theme via {model}: '{parsed.get('title')}'")
                return parsed
        except Exception as e:
            print(f"[ANALYZER NOTICE] Model {model} pass: {e}", file=sys.stderr)
            continue

    return None

def analyze_trending_gospel_videos(api_key: str = None) -> dict:
    """Queries live YouTube API v3, retrieves trending videos, and uses Gemini 3.8 to synthesize a proprietary principle."""
    load_env()
    yt_key = api_key or os.environ.get("YOUTUBE_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY")

    video_summaries = []
    titles = []
    channels = []

    if yt_key:
        try:
            published_after = (datetime.now(timezone.utc) - timedelta(hours=48)).strftime("%Y-%m-%dT%H:%M:%SZ")
            query_params = urllib.parse.urlencode({
                "part": "snippet",
                "q": "worship ministration live gospel 2026",
                "type": "video",
                "order": "viewCount",
                "publishedAfter": published_after,
                "maxResults": 6,
                "key": yt_key
            })

            search_url = f"https://www.googleapis.com/youtube/v3/search?{query_params}"
            req = urllib.request.Request(search_url, headers={"User-Agent": "KingdomJournal/3.8"})
            with urllib.request.urlopen(req, timeout=12) as resp:
                search_data = json.loads(resp.read().decode("utf-8"))
                items = search_data.get("items", [])
                vid_ids = [it["id"]["videoId"] for it in items if "videoId" in it.get("id", {})]

            if vid_ids:
                details_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id={','.join(vid_ids)}&key={yt_key}"
                req_d = urllib.request.Request(details_url, headers={"User-Agent": "KingdomJournal/3.8"})
                with urllib.request.urlopen(req_d, timeout=12) as resp_d:
                    details_data = json.loads(resp_d.read().decode("utf-8"))
                    video_items = details_data.get("items", [])

                for v in video_items:
                    snip = v.get("snippet", {})
                    v_title = snip.get("title", "")
                    ch_title = snip.get("channelTitle", "")
                    views = v.get("statistics", {}).get("viewCount", "0")

                    titles.append(v_title)
                    channels.append(ch_title)
                    video_summaries.append({
                        "title": v_title,
                        "channel": ch_title,
                        "video_id": v.get("id"),
                        "views": views
                    })
        except Exception as ey:
            print(f"[ANALYZER NOTICE] YouTube fetch exception: {ey}", file=sys.stderr)

    # Use Gemini 3.8 Flash to synthesize original proprietary editorial from the live signals
    if gemini_key and titles:
        synthesized = synthesize_principle_with_gemini(titles, channels, gemini_key)
        if synthesized:
            synthesized["videos"] = video_summaries
            return synthesized

    # Deterministic high-class curated fallback (100% de-promotional, brand building)
    idx = datetime.now().toordinal() % len(CURATED_THEMES)
    selected = dict(CURATED_THEMES[idx])
    selected["videos"] = video_summaries
    return selected

if __name__ == "__main__":
    result = analyze_trending_gospel_videos()
    print("\n--- SYNTHESIZED KINGDOM JOURNAL PRINCIPLE ---")
    print("Title:", result.get("title"))
    print("Hook:", result.get("hook_top"))
    print("Banner:", result.get("banner_text"))
    print("Quote:", result.get("quote"))
    print("Speaker:", result.get("speaker"))
    print("Scripture:", result.get("scripture"))
    print("Videos Count:", len(result.get("videos", [])))
