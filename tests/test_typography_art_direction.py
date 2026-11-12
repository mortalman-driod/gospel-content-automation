import unittest
from PIL import Image, ImageDraw

from src.design.engine import FlyerEngine
from src.design.text_layout import (
    FONT_REGISTRY,
    load_art_font,
    tokenize_with_emphasis,
    wrap_mixed_tokens,
)
from src.design.typography_system import (
    TYPOGRAPHY_STYLES,
    extract_emphasized_words,
    select_art_direction,
)


class TestTypographyArtDirection(unittest.TestCase):
    def setUp(self):
        self.engine = FlyerEngine()

    def test_all_art_fonts_bundled_and_loadable(self):
        for key, path in FONT_REGISTRY.items():
            self.assertTrue(path.is_file(), f"Missing bundled font file for '{key}': {path}")
            font = load_art_font(key, 36)
            self.assertGreater(font.size, 0)

    def test_style_directions_use_multi_font_hierarchy(self):
        self.assertGreaterEqual(len(TYPOGRAPHY_STYLES), 5)
        for style_id, style in TYPOGRAPHY_STYLES.items():
            fonts = style["fonts"]
            self.assertEqual(
                set(fonts.keys()),
                {"display", "accent", "support", "reference", "detail"},
                f"Style {style_id} missing required 5 hierarchy roles",
            )
            distinct_faces = set(fonts.values())
            self.assertGreaterEqual(
                len(distinct_faces),
                4,
                f"Style {style_id} must pair at least 4 distinct font files across roles",
            )
            self.assertNotEqual(
                fonts["display"],
                fonts["accent"],
                f"Style {style_id} display and accent fonts should clearly contrast",
            )

    def test_adaptive_luminance_polarity(self):
        for light_bg in ("cross_sunrise", "mountain_summit", "study_desk"):
            art = select_art_direction("grace", light_bg, "Be still and know.", bg_luminance=0.45)
            self.assertTrue(art["is_light_bg"])
            self.assertTrue(art["harmony"]["is_dark_text"])

        for dark_bg in ("open_bible", "green_sprout", "royal_crown"):
            art = select_art_direction("reflection", dark_bg, "God's Word is light.", bg_luminance=0.05)
            self.assertFalse(art["is_light_bg"])
            self.assertFalse(art["harmony"]["is_dark_text"])

    def test_mixed_tokenization_and_wrapping_preserve_words(self):
        quote = "Faith does not remove mountains, it gives strength to climb."
        tokens = tokenize_with_emphasis(quote, ["Faith", "strength to climb."])
        self.assertEqual(" ".join(w for w, _ in tokens), quote)
        self.assertTrue(tokens[0][1])   # Faith
        self.assertFalse(tokens[1][1])  # does
        self.assertTrue(tokens[-1][1])  # climb.

        dummy = Image.new("RGB", (600, 600))
        draw = ImageDraw.Draw(dummy)
        f_base = load_art_font("sans_bold", 48)
        f_acc = load_art_font("display_brush", 60)
        lines = wrap_mixed_tokens(tokens, f_base, f_acc, 420, draw)
        flattened = " ".join(w for line in lines for w, _ in line)
        self.assertEqual(flattened, quote)

    def test_extract_emphasized_words_caps_gracefully(self):
        res = extract_emphasized_words("The Cross proves His love and eternal grace.", max_words=3)
        self.assertGreaterEqual(len(res), 1)
        self.assertLessEqual(len(res), 3)

    def test_art_directed_renders_across_polarities_and_aspects(self):
        matrix = [
            ("asymmetric_split", "4:5", "mountain_summit", "encouragement", ["Faith"]),
            ("heavy_impact", "4:5", "green_sprout", "authority", ["plant the right seeds."]),
            ("heritage_serif", "1:1", "open_bible", "reflection", ["lamp", "light"]),
            ("quiet_light", "9:16", "cross_sunrise", "grace", ["I am God."]),
            ("viral_quote_poster", "4:5", "royal_crown", "victory", ["dominion"]),
        ]
        for tpl, aspect, arch, tone, emph in matrix:
            content = {
                "headline": "Faith gives you dominion to walk through the lamp and light, plant the right seeds, I am God.",
                "emphasized_words": emph,
                "emotional_tone": tone,
                "subline": "Trust Him deeply when the morning is still quiet.",
                "scripture_badge": "Hebrews 11:1",
                "credit": "— Apostle Joshua Selman",
                "background_archetype": arch,
            }
            if arch == "green_sprout":
                content["headline"] = "Don't just wish for change, plant the right seeds."
            elif arch == "open_bible":
                content["headline"] = "God's Word is a lamp and a light to my path."
            elif arch == "cross_sunrise":
                content["headline"] = "Be still and know that I am God."
            elif arch == "royal_crown":
                content["headline"] = "Step into kingdom dominion today."

            img, meta = self.engine.render_flyer(tpl, aspect, content)
            self.assertIsInstance(img, Image.Image)
            self.assertTrue(meta["wcag_aa_compliant"], f"{tpl} on {arch} ({aspect}) failed WCAG: {meta}")
            self.assertGreaterEqual(meta["contrast_ratio"], 4.5)


if __name__ == "__main__":
    unittest.main()
