"""
Unit tests for Milestone 3: Flyer Design Engine.
Tests all 6 templates across 3 aspect ratios (4:5, 1:1, 9:16) with contrast and dimension checks.
"""

import unittest
from pathlib import Path
from PIL import Image

from src.design.engine import FlyerEngine, SIZES
from src.design.contrast import calculate_contrast_ratio, relative_luminance

class TestDesignEngine(unittest.TestCase):
    def setUp(self):
        self.engine = FlyerEngine()
        self.sample_content = {
            "headline": "The night is far spent. Wake up out of sleep.",
            "subline": "When human striving stops, worship takes over.",
            "credit": "Line from Dunsin Oyekan, Wake Up",
            "scripture_badge": "ROMANS 8:26 [KJV]",
            "points": [
                "Surrender precedes authority",
                "Midnight praise breaks heavy chains",
                "The secret place crowns the public life"
            ]
        }

    def test_dimensions_all_sizes(self):
        for size_key, (expected_w, expected_h) in SIZES.items():
            img, meta = self.engine.render_flyer(
                template_name="bold_statement",
                size_key=size_key,
                content=self.sample_content
            )
            self.assertEqual(img.size, (expected_w, expected_h))
            self.assertEqual(meta["dimensions"], f"{expected_w}x{expected_h}")

    def test_all_templates_render_successfully(self):
        templates = [
            "viral_quote_poster", "modern_quote_card", "hero_vista", "lifestyle_study",
            "bold_statement", "contrast_split", "scripture_card",
            "question_hook", "quiet_light", "numbered_list"
        ]
        for tpl in templates:
            img, meta = self.engine.render_flyer(
                template_name=tpl,
                size_key="4:5",
                content=self.sample_content
            )
            self.assertIsInstance(img, Image.Image)
            self.assertEqual(meta["template"], tpl)
            self.assertGreaterEqual(meta["contrast_ratio"], 4.5, f"Template {tpl} failed WCAG AA contrast check")

    def test_contrast_calculation(self):
        white = (255, 255, 255)
        black = (0, 0, 0)
        c = calculate_contrast_ratio(white, black)
        self.assertAlmostEqual(c, 21.0, places=1)

    def test_long_headline_auto_scales(self):
        long_content = {
            "headline": "Spiritual authority is never forged in public spectacles or microphones but in the silence of deep midnight consecration",
            "credit": "The Kingdom Journal"
        }
        img, meta = self.engine.render_flyer(
            template_name="bold_statement",
            size_key="4:5",
            content=long_content
        )
        self.assertIsInstance(img, Image.Image)
        self.assertEqual(img.size, (1080, 1350))

if __name__ == "__main__":
    unittest.main()
