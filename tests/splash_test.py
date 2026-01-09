# Ensure splash texts aren't too long and are imported correctly
import unittest
from core.consts import MAX_SPLASH_LEN
from core.splash_text import get_splash_text_file

class TestSplashText(unittest.TestCase):
    def test_splash_text_length(self):
        texts = get_splash_text_file()
        for line in range(len(texts)):
            self.assertLessEqual(len(texts[line]), 80, f"Splash text line {line+1} exceeds {MAX_SPLASH_LEN} characters")