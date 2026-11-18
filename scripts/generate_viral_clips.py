"""
Script: scripts/generate_viral_clips.py
Discovers, extracts 90-second viral climaxes, and renders vertical shorts
for the user's curated roster:
- 3 Preaching: Bro. Gbile Akanni, Apostle Arome Osayi, Apostle Michael Orokpo
- 1 Nigerian Gospel Music: Minister Theophilus Sunday
- 1 Foreign Gospel Music: Josiah Queen ("Queen Josiah")
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
        "category_name": "Discipleship & Consecration (Nigeria)",
        "video_id": "mO0HTfBrdl4",
        "speaker": "Bro. Gbile Akanni",
        "title": "Why Regular Intimacy is Not Optional",
        "start_sec": 135, # 00:02:15
        "duration_sec": 90,
        "raw_file": "raw_gbile_90s.mp4",
        "quote": "If you lose your secret place, you have lost your spiritual bearing. Power is not demonstrated in the crowd; it is conceived in quietness.",
        "scripture_ref": "Psalm 91:1",
        "scripture_text": "He that dwelleth in the secret place of the most High shall abide under the shadow of the Almighty."
    },
    {
        "category": "preaching_2",
        "category_name": "Apostolic Priesthood & Prayer (Nigeria)",
        "video_id": "GrDCZBrxlAw",
        "speaker": "Apostle Arome Osayi",
        "title": "How God Raises Men of Spiritual Authority",
        "start_sec": 1520, # 00:25:20
        "duration_sec": 90,
        "raw_file": "raw_arome_90s.mp4",
        "quote": "God does not use men because they are gifted; He uses men who have yielded their will at the altar of consecrated prayer.",
        "scripture_ref": "Romans 12:1",
        "scripture_text": "Present your bodies a living sacrifice, holy, acceptable unto God, which is your reasonable service."
    },
    {
        "category": "preaching_3",
        "category_name": "Spiritual Mysteries & Priesthood (Nigeria)",
        "video_id": "OR3Jgw-OofA",
        "speaker": "Apostle Michael Orokpo",
        "title": "The Making of Men: The Divine Presence",
        "start_sec": 750, # 00:12:30
        "duration_sec": 90,
        "raw_file": "raw_orokpo_90s.mp4",
        "quote": "You cannot carry the presence of God and remain ordinary. When the Holy Ghost rests upon a man, he becomes an eternal wonder.",
        "scripture_ref": "Acts 1:8",
        "scripture_text": "But ye shall receive power, after that the Holy Ghost is come upon you: and ye shall be witnesses unto me."
    },
    {
        "category": "music_nigerian",
        "category_name": "Prophetic Chants & Deep Worship (Nigeria)",
        "video_id": "kA6V3TIRDQE",
        "speaker": "Minister Theophilus Sunday",
        "title": "I Believe Live (Chants & Intimacy)",
        "start_sec": 525, # 00:08:45
        "duration_sec": 90,
        "raw_file": "raw_theophilus_90s.mp4",
        "quote": "I live by faith and not by sight. My spirit pants after You, Jesus, my firm foundation!",
        "scripture_ref": "2 Corinthians 5:7",
        "scripture_text": "For we walk by faith, not by sight."
    },
    {
        "category": "music_foreign",
        "category_name": "Acoustic Revival & Folk Worship (Foreign)",
        "video_id": "3B3hC706X90",
        "speaker": "Josiah Queen (Queen Josiah)",
        "title": "The Prodigal (Acoustic Folk Worship)",
        "start_sec": 65, # 00:01:05
        "duration_sec": 90,
        "raw_file": "raw_josiah_queen_90s.webm",
        "quote": "I took what was mine and threw it away, but when I came running home, You ran right out to meet me with boundless grace!",
        "scripture_ref": "Luke 15:20",
        "scripture_text": "And he arose, and came to his father. But when he was yet a great way off, his father saw him, and had compassion, and ran."
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

    # Render primary test short: Bro. Gbile Akanni
    primary = VIRAL_TARGETS[0]
    print("\n-----------------------------------------------------------------")
    print(f"PRIMARY TEST SHORT: {primary['speaker']}...")
    print("-----------------------------------------------------------------")

    raw_slice = clipper.output_dir / primary["raw_file"]
    if not raw_slice.is_file():
        print(f"Downloading slice for {primary['speaker']}...")
        raw_slice = clipper.download_90s_slice(
            primary["video_id"],
            primary["start_sec"],
            primary["duration_sec"],
            output_filename=primary["raw_file"]
        )

    out_vertical = clipper.output_dir / "gbile_akanni_intimacy_90s.mp4"
    rendered = clipper.composite_vertical_short(
        video_path=raw_slice,
        speaker=primary["speaker"],
        title=primary["title"],
        quote=primary["quote"],
        scripture_ref=primary["scripture_ref"],
        scripture_text=primary["scripture_text"],
        output_filename="gbile_akanni_intimacy_90s.mp4"
    )

    if rendered and rendered.is_file():
        print(f"\n>>> Successfully rendered 9:16 short: {rendered.name} ({rendered.stat().st_size / (1024*1024):.2f} MB)")
        # Extract preview
        prev = clipper.extract_preview_frame(rendered)
        if prev and prev.is_file():
            print(f">>> Snapshot preview generated: {prev.name}")
            if artifact_dir.is_dir():
                shutil.copy2(rendered, artifact_dir / rendered.name)
                shutil.copy2(prev, artifact_dir / prev.name)
                print(f">>> Copied to brain artifacts: {artifact_dir}")

if __name__ == "__main__":
    main()
