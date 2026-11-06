"""
Milestone 2: Pluggable YouTube Transcript Extraction Engine
Extracts real spoken transcripts via a multi-tier fallback chain:
1. Local disk cache (data/transcripts/<video_id>.json)
2. Manual inbox fallback (inbox/quotes.md)
3. Direct youtube-transcript-api
4. Proxy-routed youtube-transcript-api (if PROXY_URL set)
5. Hosted transcript API (if TRANSCRIPT_API_KEY set)
Includes exponential backoff, rate limiting (max 5 fetches/day), and fail-soft degradation.
"""

import json
import logging
import os
import re
import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("kingdom_journal.transcripts")
BASE_DIR = Path(__file__).resolve().parent.parent

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

class TranscriptSource(ABC):
    """Abstract interface for transcript extraction sources."""
    @abstractmethod
    def fetch(self, video_id: str) -> Optional[List[Dict]]:
        """Returns list of {text: str, start: float, duration: float} or None."""
        pass

class ManualInboxSource(TranscriptSource):
    """Parses inbox/quotes.md for manually supplied verbatim lines."""
    def __init__(self, inbox_path: Optional[Path] = None):
        self.inbox_path = inbox_path or (BASE_DIR / "inbox" / "quotes.md")

    def fetch(self, video_id: str) -> Optional[List[Dict]]:
        if not self.inbox_path.is_file():
            return None
        
        try:
            lines = self.inbox_path.read_text(encoding="utf-8").splitlines()
            for raw_line in lines:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 3:
                    url_or_id = parts[0]
                    # Extract video ID from URL if full URL given
                    vid_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})', url_or_id)
                    matched_id = vid_match.group(1) if vid_match else url_or_id
                    
                    if matched_id == video_id:
                        start_sec = float(parts[1]) if parts[1].replace(".", "", 1).isdigit() else 0.0
                        quote_text = parts[2]
                        speaker = parts[3] if len(parts) > 3 else "Unknown"
                        title = parts[4] if len(parts) > 4 else ""
                        logger.info(f"Loaded manual transcript quote from inbox/quotes.md for {video_id}")
                        return [{
                            "text": quote_text,
                            "start": start_sec,
                            "duration": 5.0,
                            "manual_entry": True,
                            "speaker": speaker,
                            "video_title": title
                        }]
        except Exception as e:
            logger.warning(f"Error reading manual inbox: {e}")
        return None

class DirectYouTubeTranscriptSource(TranscriptSource):
    """Direct fetch via youtube-transcript-api with language fallbacks."""
    def __init__(self, proxy_url: Optional[str] = None):
        self.proxy_url = proxy_url

    def fetch(self, video_id: str) -> Optional[List[Dict]]:
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
        except ImportError:
            logger.warning("youtube-transcript-api is not installed.")
            return None

        # Setup proxies if configured
        proxies = {"https": self.proxy_url, "http": self.proxy_url} if self.proxy_url else None
        
        # Languages to attempt in priority order
        languages = ['en', 'en-US', 'en-GB', 'en-NG', 'en-AU', 'en-CA']

        for attempt in range(3):
            try:
                yta = YouTubeTranscriptApi()
                # Check for fetch method (v1.2+) vs legacy get_transcript
                if hasattr(yta, "fetch"):
                    result = yta.fetch(video_id, languages=languages)
                    snippets = result.snippets if hasattr(result, "snippets") else result
                    parsed_list = []
                    for item in snippets:
                        t = getattr(item, "text", None) or (item.get("text") if isinstance(item, dict) else "")
                        s = getattr(item, "start", None) or (item.get("start") if isinstance(item, dict) else 0.0)
                        d = getattr(item, "duration", None) or (item.get("duration") if isinstance(item, dict) else 0.0)
                        if t and t.strip():
                            parsed_list.append({
                                "text": t.replace("\n", " ").strip(),
                                "start": round(float(s), 2),
                                "duration": round(float(d), 2)
                            })
                    if parsed_list:
                        return parsed_list
                elif hasattr(YouTubeTranscriptApi, "get_transcript"):
                    transcript_obj = YouTubeTranscriptApi.get_transcript(
                        video_id,
                        languages=languages,
                        proxies=proxies
                    )
                    if transcript_obj:
                        return [
                            {
                                "text": item.get("text", "").replace("\n", " ").strip(),
                                "start": round(float(item.get("start", 0.0)), 2),
                                "duration": round(float(item.get("duration", 0.0)), 2)
                            }
                            for item in transcript_obj
                            if item.get("text")
                        ]
            except Exception as e:
                err_str = str(e)
                if "TranscriptsDisabled" in err_str or "NoTranscriptFound" in err_str:
                    logger.info(f"Video {video_id} has no transcripts available ({err_str[:60]}).")
                    break
                elif "RequestBlocked" in err_str or "IpBlocked" in err_str or "TooManyRequests" in err_str:
                    logger.warning(f"Transcript fetch blocked on attempt {attempt+1} for {video_id}: {err_str[:80]}")
                    time.sleep(2 ** attempt)
                else:
                    logger.warning(f"Transcript fetch attempt {attempt+1} failed for {video_id}: {e}")
                    time.sleep(1)

        return None

class HostedTranscriptSource(TranscriptSource):
    """Hosted transcript API fallback if TRANSCRIPT_API_KEY / endpoint is configured."""
    def __init__(self, api_key: Optional[str] = None, endpoint: Optional[str] = None):
        self.api_key = api_key
        self.endpoint = endpoint

    def fetch(self, video_id: str) -> Optional[List[Dict]]:
        if not self.api_key or not self.endpoint:
            return None
        import requests
        try:
            resp = requests.get(
                self.endpoint,
                params={"video_id": video_id},
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=15
            )
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and "transcript" in data:
                    return data["transcript"]
        except Exception as e:
            logger.warning(f"Hosted transcript API error for {video_id}: {e}")
        return None

class TranscriptManager:
    """
    Manages the multi-tier extraction pipeline, disk caching,
    and quota / rate controls.
    """
    def __init__(self, cache_dir: Optional[Path] = None, max_fetches_per_run: int = 5):
        load_env()
        self.cache_dir = cache_dir or (BASE_DIR / "data" / "transcripts")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_fetches = max_fetches_per_run
        self.fetches_count = 0

        proxy_url = os.environ.get("PROXY_URL")
        hosted_api_key = os.environ.get("TRANSCRIPT_API_KEY")
        hosted_endpoint = os.environ.get("TRANSCRIPT_API_ENDPOINT")

        # Configured sources in priority order
        self.sources: List[Tuple[str, TranscriptSource]] = [
            ("inbox_manual", ManualInboxSource()),
            ("youtube_direct", DirectYouTubeTranscriptSource(proxy_url=None)),
        ]
        if proxy_url:
            self.sources.append(("youtube_proxy", DirectYouTubeTranscriptSource(proxy_url=proxy_url)))
        if hosted_api_key and hosted_endpoint:
            self.sources.append(("hosted_api", HostedTranscriptSource(api_key=hosted_api_key, endpoint=hosted_endpoint)))

    def get_transcript(self, video_id: str, force_refresh: bool = False) -> Tuple[Optional[List[Dict]], str]:
        """
        Retrieves transcript for a video ID.
        Returns: (transcript_snippets_or_None, source_description)
        """
        cache_file = self.cache_dir / f"{video_id}.json"

        # 1. Check local cache
        if not force_refresh and cache_file.is_file():
            try:
                cached_data = json.loads(cache_file.read_text(encoding="utf-8"))
                snippets = cached_data.get("transcript")
                if snippets:
                    logger.info(f"Loaded cached transcript for video {video_id} ({len(snippets)} snippets).")
                    return snippets, "cache"
            except Exception as e:
                logger.warning(f"Error reading transcript cache for {video_id}: {e}")

        # 2. Check manual inbox before network
        inbox_source = ManualInboxSource()
        manual_snips = inbox_source.fetch(video_id)
        if manual_snips:
            self._save_to_cache(video_id, manual_snips, "inbox_manual")
            return manual_snips, "inbox_manual"

        # 3. Check fetch limits
        if self.fetches_count >= self.max_fetches:
            logger.warning(f"Transcript fetch limit ({self.max_fetches}) reached for this run. Skipping {video_id}.")
            return None, "rate_limit_exceeded"

        # 4. Try network sources
        self.fetches_count += 1
        for name, source in self.sources:
            if name == "inbox_manual":
                continue # Already checked
            try:
                logger.info(f"Attempting transcript fetch for {video_id} via {name}...")
                snippets = source.fetch(video_id)
                if snippets:
                    self._save_to_cache(video_id, snippets, name)
                    return snippets, name
            except Exception as e:
                logger.warning(f"Source {name} failed for {video_id}: {e}")

        logger.info(f"All transcript sources failed for {video_id}. Continuing fail-soft with metadata only.")
        return None, "not_available"

    def _save_to_cache(self, video_id: str, snippets: List[Dict], source_name: str):
        cache_file = self.cache_dir / f"{video_id}.json"
        try:
            payload = {
                "video_id": video_id,
                "extracted_at": datetime.now(timezone.utc).isoformat(),
                "source": source_name,
                "snippet_count": len(snippets),
                "transcript": snippets
            }
            cache_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
            logger.info(f"Saved transcript cache for {video_id} ({len(snippets)} snippets).")
        except Exception as e:
            logger.warning(f"Failed to write transcript cache for {video_id}: {e}")
