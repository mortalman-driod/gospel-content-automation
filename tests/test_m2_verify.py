"""
Unit tests for Milestone 2: Transcript extraction, fuzzy quote verification, and scripture validation.
"""

import unittest
from src.verify import (
    fuzzy_verify_quote,
    validate_scripture_reference,
    scan_risk_flags,
    format_timestamp_url
)
from src.transcripts import ManualInboxSource

class TestQuoteVerification(unittest.TestCase):
    def setUp(self):
        self.sample_transcript = [
            {"start": 10.0, "duration": 4.0, "text": "and let me tell you something today"},
            {"start": 14.0, "duration": 5.0, "text": "spiritual authority is forged in secret"},
            {"start": 19.0, "duration": 4.5, "text": "not on public stages"},
            {"start": 23.5, "duration": 4.0, "text": "many people run around looking for visibility"}
        ]

    def test_verbatim_quote_passes(self):
        quote = "Spiritual authority is forged in secret not on public stages"
        is_verified, score, match = fuzzy_verify_quote(quote, self.sample_transcript, threshold=0.92)
        self.assertTrue(is_verified)
        self.assertGreaterEqual(score, 0.92)
        self.assertIsNotNone(match)
        self.assertEqual(match["start_sec"], 14)

    def test_reworded_fabricated_quote_rejected(self):
        quote = "True godly greatness only happens when you pray in public platforms with shouting"
        is_verified, score, match = fuzzy_verify_quote(quote, self.sample_transcript, threshold=0.92)
        self.assertFalse(is_verified)
        self.assertLess(score, 0.80)

    def test_filler_words_and_punctuation_handled(self):
        # Spoken fillers like "amen", punctuation, and casing
        quote = "Spiritual authority is forged in secret, not on public stages!"
        is_verified, score, match = fuzzy_verify_quote(quote, self.sample_transcript, threshold=0.92)
        self.assertTrue(is_verified)
        self.assertGreaterEqual(score, 0.92)

    def test_timestamp_url(self):
        url = format_timestamp_url("abc123XYZ00", 145)
        self.assertEqual(url, "https://youtu.be/abc123XYZ00?t=145")

class TestScriptureValidator(unittest.TestCase):
    def test_valid_scriptures(self):
        valid_cases = [
            ("Romans 8:26", "Romans 8:26"),
            ("psalm 46:5", "Psalm 46:5"),
            ("1 Cor 13:4-8", "1 Corinthians 13:4-8"),
            ("Matt 6:6", "Matthew 6:6"),
            ("Jude 1:20", "Jude 1:20")
        ]
        for ref_input, expected_canon in valid_cases:
            is_valid, formatted, err = validate_scripture_reference(ref_input)
            self.assertTrue(is_valid, f"Failed for {ref_input}: {err}")
            self.assertEqual(formatted, expected_canon)

    def test_invalid_scriptures_rejected(self):
        invalid_cases = [
            ("Hezekiah 3:16", "not recognized in the Biblical canon"),
            ("Romans 29:1", "has 16 chapters"),
            ("Genesis 55:1", "has 50 chapters"),
            ("1 Opinions 2:4", "not recognized in the Biblical canon"),
            ("", "Empty scripture reference")
        ]
        for ref_input, expected_err_sub in invalid_cases:
            is_valid, formatted, err = validate_scripture_reference(ref_input)
            self.assertFalse(is_valid, f"Should have failed for {ref_input}")
            self.assertIn(expected_err_sub, err)

class TestRiskFlagScanner(unittest.TestCase):
    def test_detects_guarantees(self):
        bad_line = "I declare that in 24 hours your bank account will receive instant credit"
        flags = scan_risk_flags(bad_line)
        self.assertTrue(len(flags) > 0)

    def test_clean_theological_line(self):
        clean_line = "When human striving stops, worship takes over."
        flags = scan_risk_flags(clean_line)
        self.assertEqual(len(flags), 0)

if __name__ == "__main__":
    unittest.main()
