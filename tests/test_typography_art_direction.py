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

    def test_viral_catalog_canvases_render_and_meet_wcag_aa(self):
        viral_cases = [
            ("diagonal_royal_gold", "4:5", "victory", ["faith"]),
            ("golden_sunburst_clouds", "4:5", "hope", ["light"]),
            ("deep_cobalt_wave", "4:5", "grace", ["know"]),
            ("deep_cobalt_wave", "1:1", "grace", ["still"]),
            ("emerald_white_wave", "4:5", "encouragement", ["seeds"]),
            ("crimson_cream_wave", "4:5", "warning", ["life"]),
            ("terracotta_amber_wave", "4:5", "hope", ["light", "peace"]),
            ("terracotta_amber_wave", "1:1", "encouragement", ["seeds"]),
        ]
        for arch, aspect, tone, emph in viral_cases:
            content = {
                "headline": "Faith gives you light and life so know and plant seeds in peace.",
                "emphasized_words": emph,
                "emotional_tone": tone,
                "subline": "Wait on God before you answer the pressure of the day.",
                "scripture_badge": "Psalm 46:10",
                "credit": "— Apostle Joshua Selman",
                "background_archetype": arch,
                "accent_color": "terracotta",
            }
            img, meta = self.engine.render_flyer("asymmetric_split", aspect, content)
            self.assertIsInstance(img, Image.Image)
            self.assertTrue(meta["wcag_aa_compliant"], f"{arch} ({aspect}) failed WCAG: {meta}")
            self.assertGreaterEqual(meta["contrast_ratio"], 4.5)

    def test_punchline_ranker_prefers_inspiring_declarative_over_fragment(self):
        from unittest.mock import patch
        from src.punchlines import PunchlineExtractor

        weak_fragment = "When there are contentions and threats the prayer becomes what we say."
        strong_quote = "Your secret faithfulness determines your public authority in every season."
        transcript = [
            {"start": 10.0, "duration": 8.0, "text": weak_fragment},
            {"start": 65.0, "duration": 8.0, "text": strong_quote},
        ]
        extractor = PunchlineExtractor(api_key="dummy-key")
        mock_cands = [
            {
                "start_sec": 10,
                "text_verbatim": weak_fragment,
                "structure": "declaration",
                "inspiration_score": 5,
                "why_it_works": "Setup clause",
            },
            {
                "start_sec": 65,
                "text_verbatim": strong_quote,
                "structure": "contrast",
                "inspiration_score": 10,
                "why_it_works": "Inspiring standalone truth",
            },
        ]
        with patch.object(extractor, "_call_gemini_json", return_value=mock_cands):
            res = extractor.extract_punchlines(
                {"id": "vid123", "title": "Steadfast Faith", "channel": "Koinonia Global"},
                transcript,
            )
        self.assertIsNotNone(res["primary_quote"])
        self.assertEqual(res["primary_quote"]["text_verbatim"], strong_quote)

    def test_de_ai_gate_flags_cross_channel_duplication_and_antithesis(self):
        from src.verify import verify_de_ai_compliance

        dup_text = (
            "Grace does not excuse compromise; it trains your heart for steady obedience. "
            "When everyone else panics in traffic, pray first and speak peace into the room. "
            "Your quiet faithfulness today builds tomorrow's witness."
        )
        ok_dup, viol_dup, _ = verify_de_ai_compliance(
            reflection=dup_text,
            facebook_post=dup_text,
            instagram_caption="Completely distinct Instagram devotion that stands on its own.",
        )
        self.assertFalse(ok_dup)
        self.assertTrue(any("cross-channel duplication" in v.lower() for v in viol_dup), viol_dup)

        antithesis_text = (
            "Prayer isn't a ritual; it's a lifeline. "
            "Your discipline is not passive waiting, but active trust. "
            "Faith is not avoiding reality; it is anchoring inside truth."
        )
        ok_anti, viol_anti, _ = verify_de_ai_compliance(
            reflection=antithesis_text,
            facebook_post="Walk through Monday morning with quiet courage and a steady prayer.",
        )
        self.assertFalse(ok_anti)
        self.assertTrue(any("antithesis" in v.lower() for v in viol_anti), viol_anti)


if __name__ == "__main__":
    unittest.main()
