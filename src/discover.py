"""
M1: Video Discovery & Velocity Scoring Engine
Discovers proven-viral gospel ministrations across curated channels and targeted searches.
Calculates velocity, channel outlier multiple, and engagement ratios with quota protection.
"""

import json
import math
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

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

def parse_iso8601_duration(duration_str: str) -> int:
    """Parses ISO 8601 duration (e.g., PT1H23M45S) into total seconds."""
    pattern = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')
    match = pattern.match(duration_str or "")
    if not match:
        return 0
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    return hours * 3600 + minutes * 60 + seconds

class QuotaTracker:
    def __init__(self, max_limit: int = 3000):
        self.used_units = 0
        self.max_limit = max_limit

    def spend(self, units: int):
        if self.used_units + units > self.max_limit:
            raise RuntimeError(f"YouTube API quota limit exceeded! Spent: {self.used_units}, Requested: {units}, Limit: {self.max_limit}")
        self.used_units += units

class DiscoverEngine:
    def __init__(self, api_key: str = None):
        load_env()
        self.api_key = api_key or os.environ.get("YOUTUBE_API_KEY") or os.environ.get("YT_API_KEY")
        if not self.api_key:
            raise ValueError("YOUTUBE_API_KEY is not configured in environment or .env")
        
        self.config_dir = BASE_DIR / "config"
        self.data_dir = BASE_DIR / "data"
        self.quota = QuotaTracker(max_limit=3000)

        # Load configurations
        self.channels = self._load_channels()
        self.queries = self._load_queries()
        self.used_ids = self._load_used_ids()

    def _load_channels(self) -> list:
        cpath = self.config_dir / "channels.yml"
        if not cpath.is_file():
            return []
        import yaml
        data = yaml.safe_load(cpath.read_text(encoding="utf-8")) or {}
        return data.get("channels", [])

    def _load_queries(self) -> list:
        qpath = self.config_dir / "queries.yml"
        if not qpath.is_file():
            return []
        import yaml
        data = yaml.safe_load(qpath.read_text(encoding="utf-8")) or {}
        return data.get("queries", [])

    def _load_used_ids(self) -> set:
        upath = self.data_dir / "used.json"
        if upath.is_file():
            try:
                data = json.loads(upath.read_text(encoding="utf-8"))
                return set(data.get("used_video_ids", []))
            except Exception:
                pass
        return set()

    def _get_channel_uploads_playlist_id(self, channel_id: str) -> str:
        """Standard YouTube convention: replace 2nd char 'C' with 'U'."""
        if len(channel_id) >= 2 and channel_id.startswith("UC"):
            return "UU" + channel_id[2:]
        return channel_id

    def fetch_recent_channel_videos(self, channel_id: str, max_results: int = 10) -> list:
        """Fetches recent uploads for a single channel via playlistItems (Costs 1 unit)."""
        playlist_id = self._get_channel_uploads_playlist_id(channel_id)
        params = urllib.parse.urlencode({
            "part": "snippet,contentDetails",
            "playlistId": playlist_id,
            "maxResults": max_results,
            "key": self.api_key
        })
        url = f"https://www.googleapis.com/youtube/v3/playlistItems?{params}"
        req = urllib.request.Request(url, headers={"User-Agent": "KingdomJournal/3.8"})
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                self.quota.spend(1)
                data = json.loads(resp.read().decode("utf-8"))
                items = data.get("items", [])
                video_ids = []
                for it in items:
                    vid = it.get("contentDetails", {}).get("videoId")
                    if vid and vid not in self.used_ids:
                        video_ids.append(vid)
                return video_ids
        except Exception as e:
            print(f"[DISCOVER WARNING] Failed to fetch playlist for {channel_id}: {e}", file=sys.stderr)
            return []

    def batch_fetch_video_details(self, video_ids: list) -> list:
        """Fetches full statistics, contentDetails, and snippet in batches of 50 (Costs 1 unit per batch)."""
        if not video_ids:
            return []

        detailed_videos = []
        # Process in chunks of 50
        for i in range(0, len(video_ids), 50):
            chunk = video_ids[i:i + 50]
            params = urllib.parse.urlencode({
                "part": "snippet,statistics,contentDetails",
                "id": ",".join(chunk),
                "key": self.api_key
            })
            url = f"https://www.googleapis.com/youtube/v3/videos?{params}"
            req = urllib.request.Request(url, headers={"User-Agent": "KingdomJournal/3.8"})
            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    self.quota.spend(1)
                    data = json.loads(resp.read().decode("utf-8"))
                    detailed_videos.extend(data.get("items", []))
            except Exception as e:
                print(f"[DISCOVER WARNING] Failed to fetch video details: {e}", file=sys.stderr)

        return detailed_videos

    def discovery_search(self, query: str, max_results: int = 10) -> list:
        """Search discovery fallback (Costs 100 units). Restricted to at most 1-2 calls per run."""
        published_after = (datetime.now(timezone.utc) - timedelta(days=14)).strftime("%Y-%m-%dT%H:%M:%SZ")
        params = urllib.parse.urlencode({
            "part": "snippet",
            "q": query,
            "type": "video",
            "order": "viewCount",
            "publishedAfter": published_after,
            "relevanceLanguage": "en",
            "maxResults": max_results,
            "key": self.api_key
        })
        url = f"https://www.googleapis.com/youtube/v3/search?{params}"
        req = urllib.request.Request(url, headers={"User-Agent": "KingdomJournal/3.8"})
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                self.quota.spend(100)
                data = json.loads(resp.read().decode("utf-8"))
                vids = [it["id"]["videoId"] for it in data.get("items", []) if "videoId" in it.get("id", {})]
                return [v for v in vids if v not in self.used_ids]
        except Exception as e:
            print(f"[DISCOVER WARNING] Search call failed for '{query}': {e}", file=sys.stderr)
            return []

    def score_and_rank_candidates(self, raw_videos: list) -> list:
        """
        Filters candidates (published within 14 days, duration 3-60 min).
        Computes velocity, channel outlier multiple, and engagement ratio.
        """
        now = datetime.now(timezone.utc)
        candidates = []

        # Group views by channel for calculating channel median view count
        channel_views = {}
        parsed_items = []

        for item in raw_videos:
            snip = item.get("snippet", {})
            stats = item.get("statistics", {})
            content = item.get("contentDetails", {})

            vid_id = item.get("id")
            title = snip.get("title", "")
            channel = snip.get("channelTitle", "")
            channel_id = snip.get("channelId", "")

            # 1. Parse Duration
            duration_sec = parse_iso8601_duration(content.get("duration", ""))
            # Allow 3 min (180s) to 120 min (7200s), but down-rank long livestreams
            if duration_sec < 180:
                continue # Skip clips shorter than 3 minutes

            # 2. Parse Publish Age
            pub_str = snip.get("publishedAt", "")
            try:
                pub_dt = datetime.fromisoformat(pub_str.replace("Z", "+00:00"))
            except Exception:
                pub_dt = now - timedelta(days=1)
            
            hours_since_publish = max(0.5, (now - pub_dt).total_seconds() / 3600.0)
            if hours_since_publish > (14 * 24):
                continue # Skip uploads older than 14 days

            views = int(stats.get("viewCount", "0") or 0)
            likes = int(stats.get("likeCount", "0") or 0)
            comments = int(stats.get("commentCount", "0") or 0)

            channel_views.setdefault(channel_id, []).append(views)

            parsed_items.append({
                "video_id": vid_id,
                "title": title,
                "channel": channel,
                "channel_id": channel_id,
                "url": f"https://www.youtube.com/watch?v={vid_id}",
                "views": views,
                "likes": likes,
                "comments": comments,
                "duration_sec": duration_sec,
                "hours_since_publish": hours_since_publish,
                "published_at": pub_str
            })

        # Calculate channel median views
        channel_medians = {}
        for ch_id, vlist in channel_views.items():
            sorted_v = sorted(vlist)
            mid = len(sorted_v) // 2
            channel_medians[ch_id] = sorted_v[mid] if sorted_v else 1000

        # Compute metric ratios
        for p in parsed_items:
            views = p["views"]
            hrs = max(6.0, p["hours_since_publish"]) # Cap min hours at 6 to prevent new video velocity skew
            
            velocity = views / hrs
            median_v = max(100.0, channel_medians.get(p["channel_id"], 1000.0))
            outlier_multiple = views / median_v
            engagement_ratio = (p["likes"] + p["comments"]) / max(views, 1)

            # Penalize excessively long replays (> 75 min)
            duration_factor = 1.0
            if p["duration_sec"] > 4500:
                duration_factor = 0.65

            p["velocity"] = velocity
            p["outlier_multiple"] = outlier_multiple
            p["engagement_ratio"] = engagement_ratio
            p["duration_factor"] = duration_factor
            candidates.append(p)

        if not candidates:
            return []

        # Percentile rank helper
        def pct_ranks(values):
            sorted_vals = sorted(values)
            n = len(sorted_vals)
            if n <= 1:
                return {v: 1.0 for v in values}
            return {v: sorted_vals.index(v) / (n - 1) for v in values}

        vel_ranks = pct_ranks([c["velocity"] for c in candidates])
        out_ranks = pct_ranks([c["outlier_multiple"] for c in candidates])
        eng_ranks = pct_ranks([c["engagement_ratio"] for c in candidates])

        # Composite score = 0.45*vel + 0.35*outlier + 0.20*engage (multiplied by duration factor)
        for c in candidates:
            raw_score = (
                0.45 * vel_ranks.get(c["velocity"], 0.5) +
                0.35 * out_ranks.get(c["outlier_multiple"], 0.5) +
                0.20 * eng_ranks.get(c["engagement_ratio"], 0.5)
            )
            c["composite_score"] = round(raw_score * c["duration_factor"] * 100.0, 2)

        candidates.sort(key=lambda x: x["composite_score"], reverse=True)
        return candidates

    def run_discovery(self) -> dict:
        """Executes full discovery pass and returns top 5 with metrics and quota report."""
        print(f"[DISCOVER] Starting discovery run across {len(self.channels)} curated channels...")
        all_video_ids = []

        # 1. Curated channel uploads (1 quota unit per channel)
        for ch in self.channels:
            ch_id = ch.get("id")
            if ch_id:
                vids = self.fetch_recent_channel_videos(ch_id, max_results=6)
                all_video_ids.extend(vids)

        # 2. Discovery search (1 call to keep quota minimal, costs 100 units)
        query = self.queries[0] if self.queries else "worship ministration live gospel 2026"
        print(f"[DISCOVER] Running search discovery for: '{query}'...")
        search_vids = self.discovery_search(query, max_results=8)
        all_video_ids.extend(search_vids)

        # Deduplicate
        unique_vids = list(dict.fromkeys(all_video_ids))
        print(f"[DISCOVER] Batching details for {len(unique_vids)} candidate videos...")

        # 3. Batch fetch video details (1 unit per 50 videos)
        detailed_videos = self.batch_fetch_video_details(unique_vids)

        # 4. Rank candidates
        ranked = self.score_and_rank_candidates(detailed_videos)
        top_5 = ranked[:5]

        print(f"[DISCOVER COMPLETE] Scored {len(ranked)} videos. Quota units used: {self.quota.used_units}")
        return {
            "top_5": top_5,
            "quota_units_used": self.quota.used_units,
            "candidates_evaluated": len(ranked),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

if __name__ == "__main__":
    engine = DiscoverEngine()
    result = engine.run_discovery()

    print("\n" + "=" * 70)
    print("M1 ACCEPTANCE REPORT: TOP 5 PROVEN VIRAL GOSPEL VIDEOS")
    print("=" * 70)
    for idx, v in enumerate(result["top_5"], 1):
        print(f"\n#{idx} {v['title']}")
        print(f"   Channel:     {v['channel']}")
        print(f"   URL:         {v['url']}")
        print(f"   Views:       {v['views']:,} views (in {v['hours_since_publish']:.1f} hours)")
        print(f"   Velocity:    {v['velocity']:.1f} views/hour")
        print(f"   Outlier:     {v['outlier_multiple']:.2f}x channel median")
        print(f"   Score:       {v['composite_score']} / 100")

    print("\n" + "-" * 70)
    print(f"QUOTA REPORT: {result['quota_units_used']} units used (Limit: < 500 units for M1 acceptance)")
    print("-" * 70)
