from langdetect import detect
from typing import Tuple, Optional


class LanguageDetector:
    def __init__(self):
        # Mapping between Hebrew and English keyboard layouts
        self.hebrew_to_english = {
            'ק': 'e', 'ר': 'r', 'א': 't', 'ט': 'y', 'ו': 'u',
            'ן': 'i', 'ם': 'o', 'פ': 'p', 'ש': 'a', 'ד': 's',
            'ג': 'd', 'כ': 'f', 'ע': 'g', 'י': 'h', 'ח': 'j',
            'ל': 'k', 'ך': 'l', 'ז': 'z', 'ס': 'x', 'ב': 'c',
            'ה': 'v', 'נ': 'b', 'מ': 'n', 'צ': 'm'
        }
        self.english_to_hebrew = {v: k for k, v in self.hebrew_to_english.items()}

    def detect_language(self, text: str) -> str:
        """
        Detects the language of the input text
        Returns: 'he' for Hebrew, 'en' for English, 'unknown' for errors
        """
        try:
            return detect(text)
        except:
            return 'unknown'

    def should_convert(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Checks if text needs conversion and to which language
        Returns: (needs_conversion: bool, target_language: Optional[str])
        """
        detected_lang = self.detect_language(text)

        # Check if text looks like English typed in Hebrew layout
        hebrew_chars = sum(1 for c in text if '\u0590' <= c <= '\u05FF')
        if hebrew_chars > len(text) * 0.7 and detected_lang != 'he':
            return True, 'en'

        # Check if text looks like Hebrew typed in English layout
        if detected_lang == 'en' and all(c.isalpha() or c.isspace() for c in text):
            test_conversion = self.convert_to_hebrew(text)
            if self.detect_language(test_conversion) == 'he':
                return True, 'he'

        return False, None

    def convert_text(self, text: str, target_lang: str) -> str:
        """
        Converts text to target language
        Args:
            text: Input text to convert
            target_lang: Target language ('he' or 'en')
        """
        if target_lang == 'he':
            return self.convert_to_hebrew(text)
        else:
            return self.convert_to_english(text)

    def convert_to_hebrew(self, text: str) -> str:
        """Convert text from English layout to Hebrew layout"""
        return ''.join(self.english_to_hebrew.get(c.lower(), c) for c in text)

    def convert_to_english(self, text: str) -> str:
        """Convert text from Hebrew layout to English layout"""
        return ''.join(self.hebrew_to_english.get(c, c) for c in text)