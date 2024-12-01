import keyboard
import pyperclip  # הוספנו את זה בתחילת הקובץ
from language_detector import LanguageDetector
from typing import Callable


class KeyboardFixer:
    def __init__(self):
        self.detector = LanguageDetector()
        self.current_text = ""
        self.conversion_callback = None

    def set_conversion_callback(self, callback: Callable[[str, str], None]):
        self.conversion_callback = callback

    def on_hotkey(self):
        try:
            # Get text from clipboard
            text = pyperclip.paste()
            print(f"Received text: {text}")  # Debug print

            if text:
                converted_text, conversion_type = self.detector.convert_text(text)
                print(f"Converted to: {converted_text}")  # Debug print

                if converted_text != text and self.conversion_callback:
                    pyperclip.copy(converted_text)
                    self.conversion_callback(converted_text, conversion_type)
        except Exception as e:
            print(f"Error details: {str(e)}")
            raise  # This will show us the full error trace

    def start(self):
        """Start listening for the hotkey"""
        keyboard.add_hotkey('ctrl+alt', self.on_hotkey)
        print("KeyboardFixer started - Press Ctrl+Alt to convert selected text")

    def stop(self):
        """Stop listening and clear resources"""
        keyboard.unhook_all()