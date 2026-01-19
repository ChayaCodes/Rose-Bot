"""
Tests for content filter (rule-based backend)
Run with: python -m pytest tests/test_content_filter.py
"""

import os
import sys
import unittest

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bot_core.content_filter import ContentModerator


class TestContentFilterRules(unittest.TestCase):
    """Rule-based moderation tests"""

    def setUp(self):
        self.moderator = ContentModerator(backend='rules')

    def test_supported_categories_rules(self):
        self.assertEqual(self.moderator.get_supported_categories(), ['spam', 'promotion', 'sexual'])

    def test_short_text_returns_safe(self):
        result = self.moderator.check_message("hi")
        self.assertFalse(result.is_flagged)
        self.assertEqual(result.reason, "Message too short to analyze")

    def test_spam_detection_two_keywords(self):
        text = "buy now click here"
        thresholds = {'spam': 0.7, 'promotion': 0.7, 'sexual': 0.7}
        result = self.moderator.check_message(text, thresholds)
        self.assertTrue(result.is_flagged)
        self.assertIn('spam', result.scores)
        self.assertGreaterEqual(result.scores['spam'], 0.7)

    def test_promotion_detection_patterns(self):
        text = "Check http://bit.ly/abc and https://t.me/test now"
        thresholds = {'spam': 0.7, 'promotion': 0.7, 'sexual': 0.7}
        result = self.moderator.check_message(text, thresholds)
        self.assertTrue(result.is_flagged)
        self.assertIn('promotion', result.scores)
        self.assertGreaterEqual(result.scores['promotion'], 0.7)

    def test_sexual_detection_single_keyword(self):
        text = "sex"
        thresholds = {'spam': 0.7, 'promotion': 0.7, 'sexual': 0.6}
        result = self.moderator.check_message(text, thresholds)
        self.assertTrue(result.is_flagged)
        self.assertIn('sexual', result.scores)
        self.assertGreaterEqual(result.scores['sexual'], 0.6)


if __name__ == "__main__":
    unittest.main()
