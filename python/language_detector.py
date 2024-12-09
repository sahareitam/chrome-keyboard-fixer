class LanguageDetector:
    def __init__(self):
        # Explicit mapping from Hebrew to English
        self.hebrew_to_english = {
            'ק': 'e', 'ר': 'r', 'א': 't', 'ט': 'y', 'ו': 'u',
            'ן': 'i', 'ם': 'o', 'פ': 'p', 'ש': 'a', 'ד': 's',
            'ג': 'd', 'כ': 'f', 'ע': 'g', 'י': 'h', 'ח': 'j',
            'ל': 'k', 'ך': 'l', 'ז': 'z', 'ס': 'x', 'ב': 'c',
            'ה': 'v', 'נ': 'b', 'מ': 'n', 'צ': 'm', 'ף': ';',
            'ץ': '.', 'ת': '/', '\'': 'w', ',': 't', '.': '/', '/': '.',
            ' ': ' ', '\n': '\n', '\t': '\t'
        }

        # Explicit mapping from English to Hebrew
        self.english_to_hebrew = {
            'e': 'ק', 'r': 'ר', 't': 'א', 'y': 'ט', 'u': 'ו',
            'i': 'ן', 'o': 'ם', 'p': 'פ', 'a': 'ש', 's': 'ד',
            'd': 'ג', 'f': 'כ', 'g': 'ע', 'h': 'י', 'j': 'ח',
            'k': 'ל', 'l': 'ך', 'z': 'ז', 'x': 'ס', 'c': 'ב',
            'v': 'ה', 'b': 'נ', 'n': 'מ', 'm': 'צ', ';': 'ף',
            '.': 'ץ', '/': 'ת', 'w': '\'', ',': 'ת', '\'': 'ו'
        }

    def detect_character_language(self, char: str) -> str:
        """
        Detects the language of a single character.
        """
        if '\u0590' <= char <= '\u05FF':
            return 'hebrew'
        elif char.isascii() and char.isalpha():
            return 'english'
        return 'unknown'

    def convert_last_language(self, text: str) -> str:
        """
        Converts the last segment of text written in a specific language.
        Starts from the last character and stops when encountering a different language.
        """
        if not text:
            return text

        # Start from the last character and detect the last language
        last_language = None
        segment_to_convert = []
        index = len(text) - 1

        # Traverse backwards to find the last segment
        while index >= 0:
            char = text[index]
            char_language = self.detect_character_language(char)

            # Initialize the language if not set
            if last_language is None and char_language in {"hebrew", "english"}:
                last_language = char_language

            # Stop collecting characters if the language changes
            if last_language and char_language != last_language and char_language in {"hebrew", "english"}:
                break

            # Add character to the segment
            segment_to_convert.insert(0, char)
            index -= 1

        # Convert the identified segment based on its language
        if last_language == "hebrew":
            converted_segment = [self.hebrew_to_english.get(char, char) for char in segment_to_convert]
        elif last_language == "english":
            converted_segment = [self.english_to_hebrew.get(char.lower(), char) for char in segment_to_convert]
        else:
            converted_segment = segment_to_convert

        # Combine the converted segment with the rest of the text
        return ''.join(text[:index + 1]) + ''.join(converted_segment)
