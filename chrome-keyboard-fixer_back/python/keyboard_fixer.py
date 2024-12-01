import keyboard
from language_detector import LanguageDetector
from typing import Callable

class KeyboardFixer:
    def __init__(self):
        """Initialize the KeyboardFixer"""
        self.detector = LanguageDetector()
        self.buffer = ""
        self.conversion_callback = None
        # Define hotkeys
        self.CONVERT_HOTKEY = 'ctrl+alt'  # Convert text with Ctrl+Alt

    def set_conversion_callback(self, callback: Callable[[str, str], None]):
        """Set callback for when text is converted"""
        self.conversion_callback = callback

    def convert_text_buffer(self):
        """Convert the current text buffer"""
        if self.buffer:
            converted_text, conversion_type = self.detector.convert_text(self.buffer)
            if converted_text != self.buffer and self.conversion_callback:
                self.conversion_callback(converted_text, conversion_type)

    def start(self):
        """Start listening for the hotkey"""
        keyboard.add_hotkey(self.CONVERT_HOTKEY, self.convert_text_buffer)

    def stop(self):
        """Stop listening and clear resources"""
        keyboard.unhook_all()