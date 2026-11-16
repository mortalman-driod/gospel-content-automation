"""
Script: scripts/generate_viral_clips.py
Discovers, extracts 90-second viral climaxes, and renders vertical shorts
for 3 preaching and 2 gospel music videos (1 Nigerian, 1 Foreign).
"""

import json
import logging
import os
import shutil
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.clipper import ViralClipperEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("kingdom_journal.generate_clips")

VIRAL_TARGETS = [
    {
        "category": "preaching_1",
        "category_name": "Apostolic Preaching (Nigeria)",
        "video_id": "diUkTvCPNSI",
        "speaker": "Apostle Joshua Selman",
        "title": "The Covenant of Dominion",
        "start_sec": 9276, # 02:34:36
        "duration_sec": 90,
        "quote": "Though I do not know the way, I trust the one who created the way. A praise will come out from your spirit!",
        "scripture_ref": "2 Corinthians 5:7",
        "scripture_text": "For we walk by faith, not by sight."
    },
    {
        "category": "preaching_2",
        "category_name": "Teaching & Fire Revival (Nigeria)",
        "video_id": "pooWW6cTL5s",
        "speaker": "Pastor Emmanuel Iren",
        "title": "Reboot: Speed Through Waiting",
        "start_sec": 1104, # 00:18:24
        "duration_sec": 90,
        "quote": "In our kingdom, we move forward by waiting! Those who wait on the Lord shall renew their strength.",
        "scripture_ref": "Isaiah 40:31",
        "scripture_text": "They that wait upon the LORD shall renew their strength; they shall mount up with wings as eagles."
    },
    {
        "category": "preaching_3",
        "category_name": "Prophetic Prayer & Warfare (Nigeria)",
        "video_id": "P3pHh5n5MBA",
        "speaker": "Pastor Jerry Eze",
        "title": "NSPPD: Prophetic Altar of Fire",
        "start_sec": 790, # 00:13:10
        "duration_sec": 90,
        "quote": "Whatever is not in line with the will of God for your life must be altered by fire right now!",
        "scripture_ref": "Jeremiah 32:27",
        "scripture_text": "Behold, I am the LORD, the God of all flesh: is there any thing too hard for me?"
    },
    {
        "category": "music_nigerian",
        "category_name": "Gospel Worship (Nigerian)",
        "video_id": "WFaI6fIT-74",
        "speaker": "Nathaniel Bassey",
        "title": "Hallelujah Challenge Live",
        "start_sec": 110, # 00:01:50
        "duration_sec": 90,
        "quote": "You are the Alpha and Omega. Oh Lord, Your kingdom reigns forever!",
        "scripture_ref": "Revelation 1:8",
        "scripture_text": "I am Alpha and Omega, the beginning and the ending, saith the Lord."
    },
    {
        "category": "music_foreign",
        "category_name": "Gospel Worship (Foreign)",
        "video_id": "f2oxGYpuLkw",
        "speaker": "Elevation Worship",
        "title": "Praise (Live) ft. Brandon Lake",
        "start_sec": 165, # 02:45 bridge crescendo
        "duration_sec": 90,
        "quote": "I'll praise in the valley, I'll praise on the mountain! As long as I'm breathing, I've got a reason!",
        "scripture_ref": "Psalm 150:6",
        "scripture_text": "Let every thing that hath breath praise the LORD. Praise ye the LORD."
    }
]

def main():
    clipper = ViralClipperEngine()
    artifact_dir = Path("C:/Users/ezeki/.gemini/antigravity/brain/f8f5e9a2-d815-425e-baca-43eda4414c39")
    
    print("=================================================================")
    print("5 TARGET VIRAL MINISTRATIONS & 90-SECOND CLIMAX MATRIX")
    print("=================================================================")
    for t in VIRAL_TARGETS:
        print(f"\n[{t['category_name']}]")
        print(f"  Speaker:   {t['speaker']}")
        print(f"  Title:     {t['title']} (ID: {t['video_id']})")
        print(f"  Window:    {t['start_sec']}s - {t['start_sec'] + t['duration_sec']}s ({t['duration_sec']}s)")
        print(f"  Punchline: \"{t['quote']}\"")
        print(f"  Scripture: {t['scripture_ref']} - \"{t['scripture_text']}\"")

    # Let's render the primary viral short: Apostle Joshua Selman (diUkTvCPNSI)
    primary = VIRAL_TARGETS[0]
    print("\n-----------------------------------------------------------------")
    print(f"RENDERING 90-SECOND VIRAL SHORT: {primary['speaker']}...")
    print("-----------------------------------------------------------------")

    # Check if raw slice already downloaded
    existing_slice = None
    for cand_name in ["raw_selman_90s.webm", "raw_selman_90s.mp4"]:
        p = clipper.output_dir / cand_name
        if p.is_file() and p.stat().st_size > 1000:
            existing_slice = p
            print(f"Found existing raw slice at {existing_slice} ({existing_slice.stat().st_size} bytes)")
            break

    raw_slice = existing_slice or clipper.download_slice(
        primary["video_id"],
        start_sec=primary["start_sec"],
        duration_sec=primary["duration_sec"],
        temp_filename="raw_selman_90s.mp4"
    )

    if not raw_slice:
        print("Failed to download raw slice.")
        return

    result = clipper.render_vertical_short(
        raw_video_path=raw_slice,
        output_name="selman_covenant_dominion_90s",
        speaker=primary["speaker"],
        title=primary["title"],
        quote=primary["quote"],
        scripture_ref=primary["scripture_ref"],
        scripture_text=primary["scripture_text"],
        duration_limit_sec=primary["duration_sec"]
    )

    if result:
        out_video, out_preview = result
        print(f"\n[RENDER SUCCESS]")
        print(f"  Video:   {out_video} ({out_video.stat().st_size} bytes)")
        print(f"  Preview: {out_preview}")

        # Copy to artifact dir for instant user inspection
        if artifact_dir.is_dir():
            art_video = artifact_dir / "selman_covenant_dominion_90s.mp4"
            art_preview = artifact_dir / "selman_covenant_dominion_90s_preview.png"
            shutil.copy2(out_video, art_video)
            shutil.copy2(out_preview, art_preview)
            print(f"  Copied artifacts to:")
            print(f"    - {art_video}")
            print(f"    - {art_preview}")

    # Save candidates data
    cand_path = BASE_DIR / "data" / "viral_targets_90s.json"
    cand_path.write_text(json.dumps(VIRAL_TARGETS, indent=2), encoding="utf-8")
    print(f"\nSaved candidates registry to {cand_path}")

if __name__ == "__main__":
    main()
