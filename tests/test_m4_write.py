"""
Unit tests for Milestone 4: Writing Engine and Pydantic Schema Validation.
"""

import unittest
from src.write import WritingEngine, IssuePackage, QuotePayload, ScripturePayload, FlyerSpec
from src.verify import validate_scripture_reference

class TestWritingEngine(unittest.TestCase):
    def setUp(self):
        self.writer = WritingEngine()

    def test_schema_length_validators(self):
        long_x = "A" * 320
        long_story = "word " * 35

        pkg = IssuePackage(
            theme="The Secret Place",
            hook="When Words Fail",
            quote=None,
            scripture=ScripturePayload(ref="Romans 8:26", text="The Spirit intercedes...", translation="WEB"),
            reflection="Reflective essay text here...",
            facebook_post="Facebook post content...",
            instagram_caption="Instagram caption...",
            x_post=long_x,
            threads_post="Threads post...",
            whatsapp_status="WhatsApp devotional...",
            story_text=long_story,
            altar_invite="Turn your heart to God...",
            flyers=[]
        )
        # Check validators truncated cleanly
        self.assertLessEqual(len(pkg.x_post), 280)
        self.assertLessEqual(len(pkg.story_text.split()), 20)

    def test_unverified_quote_guarantee(self):
        # When no quote is passed, quote must be None and no speaker attributed
        pkg = self.writer.write_issue(theme_hint="Divine Rest", verified_quote=None)
        self.assertIsNone(pkg.quote)
        self.assertNotIn("Apostle", pkg.facebook_post)
        self.assertNotIn("Dunsin", pkg.facebook_post)
        self.assertNotIn("Nathaniel", pkg.facebook_post)

    def test_verified_quote_attribution(self):
        verified_data = {
            "text_verbatim": "The night is far spent. Wake up out of sleep.",
            "speaker": "Dunsin Oyekan",
            "video_title": "Wake Up Live Broadcast",
            "url": "https://youtu.be/C3pLDUNe87M?t=280",
            "start_sec": 280
        }
        pkg = self.writer.write_issue(theme_hint="Wake Up", verified_quote=verified_data, issue_number=3)
        self.assertIsNotNone(pkg.quote)
        self.assertEqual(pkg.quote.speaker, "Dunsin Oyekan")
        self.assertEqual(pkg.quote.text, "The night is far spent. Wake up out of sleep.")
        # Rule: Flyer credit must be clean preacher name without video broadcast title
        self.assertEqual(pkg.flyers[0].credit, "— Dunsin Oyekan")
        self.assertNotIn("Live Broadcast", pkg.flyers[0].credit)
        # Viral fields populated
        self.assertIsNotNone(pkg.viral_headline_pre)
        self.assertIsNotNone(pkg.viral_accent_word)
        self.assertIn(pkg.viral_accent_color, ["yellow", "gold", "red", "cobalt", "emerald", "amber"])
        self.assertIn(
            pkg.viral_background_archetype,
            [
                "cross_sunrise",
                "open_bible",
                "mountain_summit",
                "green_sprout",
                "royal_crown",
                "study_desk",
                "diagonal_royal_gold",
                "golden_sunburst_clouds",
                "deep_cobalt_wave",
                "emerald_white_wave",
                "crimson_cream_wave",
            ],
        )

if __name__ == "__main__":
    unittest.main()
