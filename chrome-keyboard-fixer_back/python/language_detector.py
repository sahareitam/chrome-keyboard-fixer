from typing import Tuple, Optional


class LanguageDetector:
    def __init__(self):
        # Basic keyboard layout mapping
        self.hebrew_to_english = {
            # Hebrew to English
            'ק': 'e', 'ר': 'r', 'א': 't', 'ט': 'y', 'ו': 'u',
            'ן': 'i', 'ם': 'o', 'פ': 'p', 'ש': 'a', 'ד': 's',
            'ג': 'd', 'כ': 'f', 'ע': 'g', 'י': 'h', 'ח': 'j',
            'ל': 'k', 'ך': 'l', 'ז': 'z', 'ס': 'x', 'ב': 'c',
            'ה': 'v', 'נ': 'b', 'מ': 'n', 'צ': 'm',
            # Additional Hebrew characters
            'ף': ';', 'ץ': '.', 'ת': ',', 'ץ': 'x', 'ך': 'l',
            'ם': 'o', 'ן': 'i', "'": 'w', ',': 'w', 'ש': 'a',
            # Punctuation
            '.': '/', '?': '?', ' ': ' ', '\n': '\n', '\t': '\t'
        }
        # Create reverse mapping for English to Hebrew
        self.english_to_hebrew = {v: k for k, v in self.hebrew_to_english.items()}

    def detect_keyboard_layout(self, text: str) -> str:
        """
        Detect if text is typed in wrong keyboard layout
        Returns: 'he_in_en' for Hebrew typed in English
                'en_in_he' for English typed in Hebrew
                'unknown' if can't determine
        """
        hebrew_chars = sum(1 for c in text if '\u0590' <= c <= '\u05FF')
        english_chars = sum(1 for c in text if c.isascii() and c.isalpha())

        # If text contains mostly Hebrew characters but doesn't make sense in Hebrew
        if hebrew_chars > len(text) * 0.7:
            return 'en_in_he'
        # If text contains mostly English characters but has patterns of Hebrew
        elif english_chars > len(text) * 0.7 and self.has_hebrew_patterns(text):
            return 'he_in_en'
        return 'unknown'

    def has_hebrew_patterns(self, text: str) -> bool:
        """Check for common patterns of Hebrew typed in English"""
        patterns = ['th', 'ch', 'sh', 'ck', 'vv', 'hh', 'zv', 'tk', 'vut']
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in patterns)

    def convert_text(self, text: str) -> Tuple[str, str]:
        """
        Convert text between keyboard layouts
        Returns: (converted_text, conversion_type)
        """
        layout = self.detect_keyboard_layout(text)
        if layout == 'he_in_en':
            return (self.convert_to_hebrew(text), 'to_hebrew')
        elif layout == 'en_in_he':
            return (self.convert_to_english(text), 'to_english')
        return (text, 'no_conversion')

    def convert_to_hebrew(self, text: str) -> str:
        """Convert text from English layout to Hebrew layout"""
        return ''.join(self.english_to_hebrew.get(c.lower(), c) for c in text)

    def convert_to_english(self, text: str) -> str:
        """Convert text from Hebrew layout to English layout"""
        return ''.join(self.hebrew_to_english.get(c, c) for c in text)