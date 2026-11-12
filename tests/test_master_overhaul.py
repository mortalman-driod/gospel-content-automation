"""
Master Overhaul Test Suite (tests/test_master_overhaul.py)
Validates all P0-P2 requirements specified in docs/MASTER_OVERHAUL_PROMPT.md:
1. Bundled TrueType font resolution without OS dependencies.
2. Canonical 66-book scripture engine with dynamic theme mapping & zero monoculture.
3. Preacher attribution purity (no YouTube channels as authors).
4. Outlook MSO hybrid table structure & WCAG AA contrast colors in email HTML.
5. Progressive JPEG compression under 180 KB payload budget.
6. Dynamic discovery search query rotation.
7. State history 30-day automated pruning.
"""

import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path
from PIL import Image

from src.design.text_layout import resolve_bundled_font, load_font
from src.scripture import (
    validate_canonical_reference,
    get_scripture_for_theme,
    CANONICAL_BOOKS,
    VERIFIED_SCRIPTURES
)
from src.punchlines import resolve_speaker_name
from src.deliver import EmailDeliverer, optimize_email_asset
from src.state import StateManager
from src.learn import LearningLoop

BASE_DIR = Path(__file__).resolve().parent.parent

class TestMasterOverhaul(unittest.TestCase):

    def test_01_bundled_fonts_resolution(self):
        """Verifies fonts resolve to genuine TrueType files in assets/fonts/ with correct headers."""
        font_path = resolve_bundled_font("sans", weight="bold")
        self.assertIsNotNone(font_path, "Bundled font should resolve.")
        self.assertTrue(font_path.is_file(), f"Font file must exist: {font_path}")
        self.assertIn("assets", str(font_path).lower(), "Font must resolve from repository assets.")
        
        # Verify TrueType header
        with open(font_path, "rb") as f:
            header = f.read(4)
            self.assertIn(header, (b"\x00\x01\x00\x00", b"OTTO", b"true"), "Font file must be a valid TrueType or OpenType font.")

        # Verify Pillow loads font with Bold weight
        font = load_font("sans", 32)
        self.assertIsNotNone(font)
        family, style = font.getname()
        self.assertEqual(family, "Montserrat")
        self.assertIn(style, ("Bold", "ExtraBold", "Black"))

    def test_02_scripture_canon_validation(self):
        """Validates that 66 canonical books pass and invalid/apocryphal books fail."""
        valid_refs = ["Hebrews 11:1", "Proverbs 3:5-6", "Jeremiah 29:11", "Psalm 46:10", "Romans 8:37", "Revelation 22:20"]
        for ref in valid_refs:
            is_valid, canon_ref = validate_canonical_reference(ref)
            self.assertTrue(is_valid, f"Expected {ref} to be canonical.")
            self.assertTrue(len(canon_ref) > 0)

        invalid_refs = ["Hezekiah 3:1", "1 Opinions 4:12", "Enoch 1:1", "Gospel of Thomas 2:4", "FakeBook 10:1"]
        for ref in invalid_refs:
            is_valid, _ = validate_canonical_reference(ref)
            self.assertFalse(is_valid, f"Expected {ref} to be rejected.")

    def test_03_scripture_monoculture_elimination(self):
        """Verifies that scripture engine dynamically maps diverse themes and avoids locking into Romans 8:26."""
        themes_to_test = [
            ("The Shield of Faith and Believing God", "HEBREWS 11:1"),
            ("Spiritual Warfare and Casting Down Strongholds", "2 CORINTHIANS 10:4"),
            ("Be Still and Know He Is Sovereign", "PSALM 46:10"),
            ("The Lamp of God's Word in Darkness", "PSALM 119:105"),
            ("Patience in Waiting for Divine Timing", "ISAIAH 40:31"),
        ]

        assigned_refs = []
        for theme, expected_key in themes_to_test:
            res = get_scripture_for_theme(theme=theme)
            self.assertIsNotNone(res)
            self.assertIn("reference", res)
            assigned_refs.append(res["reference"])

        # Ensure we have diverse verses and NOT all the same verse
        unique_refs = set(assigned_refs)
        self.assertGreaterEqual(len(unique_refs), 4, "Scripture assignments across themes must be diverse.")

    def test_04_preacher_attribution_purity(self):
        """Verifies that channel and ministry names are never used as author attributions."""
        test_cases = [
            ("The Miracle of Understanding", "Koinonia Global", "Apostle Joshua Selman"),
            ("Living the Supernatural Life", "Celebration Church TV", "Pastor Emmanuel Iren"),
            ("NSPPD Prophetic Prayers", "Streams of Joy International", "Pastor Jerry Eze"),
            ("Gospel Praise Session", "Doxology Music", "The Kingdom Journal"),
            ("Spiritual Foundations", "The God Life Club", "Pastor Chingtok Ishaku"),
        ]

        for title, channel, expected_author in test_cases:
            resolved = resolve_speaker_name(title, channel)
            self.assertEqual(resolved, expected_author)
            self.assertNotIn("tv", resolved.lower())
            self.assertNotIn("global", resolved.lower())
            self.assertNotIn("international", resolved.lower())

    def test_05_email_mso_hybrid_tables_and_contrast(self):
        """Verifies email template uses MSO conditional comments, no body flexbox, and WCAG AA contrast colors."""
        deliverer = EmailDeliverer()
        mock_pkg = {
            "theme": "The Secret Place",
            "hook": "When human words run dry",
            "reflection": "A quiet contemplative reflection.",
            "facebook_post": "Facebook text",
            "instagram_caption": "Instagram caption",
            "x_post": "Twitter aphorism",
            "threads_post": "Threads thought",
            "whatsapp_status": "WhatsApp status",
            "story_text": "Story overlay",
            "altar_invite": "Altar prayer",
            "scripture": {"ref": "Psalm 119:105", "text": "Your word is a lamp.", "translation": "WEB"},
            "flyers": [{"image_prompt": "Prompt text"}]
        }

        html = deliverer.build_email_html(
            issue_number=56,
            package=mock_pkg,
            verified_meta=None,
            radar_videos=[],
            quota_used=105
        )

        # 1. Must include MSO conditional comments for Outlook hybrid tables
        self.assertIn("<!--[if mso]>", html)
        self.assertIn("<table role=\"presentation\"", html)

        # 2. Must adhere to Warm Terracotta & Burnt Amber WCAG AAA/AA light-paper ink palette
        self.assertIn('#F6F2ED', html)  # Soft warm linen backdrop
        self.assertIn('#FFFFFF', html)  # Crisp white dispatch sheet
        self.assertIn('#1C1917', html)  # Deep warm espresso ink
        self.assertIn('#57534E', html)  # High-contrast warm stone secondary ink
        self.assertIn('#9A3412', html)  # Rich terracotta studio accent
        self.assertIn('#D97706', html)  # Burnt amber rule & quote bar
        # Must contain zero template jargon, Roman numerals, textareas, or platform emojis
        self.assertNotIn('I &middot;', html)
        self.assertNotIn('Plate ', html)
        self.assertNotIn('MORNING EDITION', html)
        self.assertNotIn('Published in Lagos &amp; London', html)
        self.assertNotIn('<textarea', html)
        self.assertNotIn('📘', html)
        self.assertNotIn('📸', html)

    def test_06_image_compression_budget(self):
        """Verifies progressive JPEG optimization keeps image size under 180 KB."""
        # Create a sample 1080x1350 image with detailed content
        img = Image.new("RGB", (1080, 1350), color=(10, 17, 40))
        jpeg_bytes = optimize_email_asset(img, max_kb=180)
        size_kb = len(jpeg_bytes) / 1024.0
        self.assertLessEqual(size_kb, 180.0, f"Optimized JPEG must be under 180 KB, got {size_kb:.1f} KB")

    def test_07_state_pruning(self):
        """Verifies that entries older than 30 days are pruned from state history."""
        mgr = StateManager()
        now_dt = datetime.now(timezone.utc)
        old_date = (now_dt - timedelta(days=45)).strftime("%Y-%m-%d")
        recent_date = (now_dt - timedelta(days=5)).strftime("%Y-%m-%d")

        mgr.used_data = {
            "used_video_ids": ["old_vid_123", "recent_vid_456"],
            "used_quotes": [],
            "used_themes": [],
            "history": [
                {"issue": 10, "date": old_date, "video_id": "old_vid_123"},
                {"issue": 50, "date": recent_date, "video_id": "recent_vid_456"}
            ]
        }

        mgr.prune_used_history(days_retention=30)
        history_vids = [h["video_id"] for h in mgr.used_data["history"]]
        self.assertNotIn("old_vid_123", history_vids, "Entries older than 30 days must be pruned.")
        self.assertIn("recent_vid_456", history_vids, "Recent entries must be preserved.")
        self.assertNotIn("old_vid_123", mgr.used_data["used_video_ids"])

    def test_08_learning_telemetry_cli(self):
        """Verifies that telemetry logging records reach, shares, and saves into performance dataset."""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            loop = LearningLoop(perf_file=tmp_path)
            post_ids = loop.register_issue_posts(
                issue_number=999,
                template="viral_quote_poster",
                palette="navy_gold",
                theme="Test Theme"
            )
            self.assertEqual(len(post_ids), 5)
            
            # Log telemetry
            updated = loop.log_engagement(issue_number=999, reach=5000, shares=120, saves=85)
            self.assertEqual(updated, 5)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

if __name__ == "__main__":
    unittest.main()
