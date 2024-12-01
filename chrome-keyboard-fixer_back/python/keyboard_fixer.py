import keyboard
from language_detector import LanguageDetector
from typing import Callable


class KeyboardFixer:
    def __init__(self):
        """Initialize the KeyboardFixer with language detector and buffer"""
        self.detector = LanguageDetector()
        self.buffer = ""
        self.last_key_time = 0
        self.callback = None

    def set_callback(self, callback: Callable[[str], None]):
        """Set callback function for handling corrected text"""
        self.callback = callback

    def process_text(self, text: str) -> str:
        """
        Process text and return the corrected version if needed
        Returns original text if no correction is needed
        """
        should_convert, target_lang = self.detector.should_convert(text)
        if should_convert and target_lang:
            return self.detector.convert_text(text, target_lang)
        return text

    def on_key_event(self, event):
        """
        Handle keyboard events
        Collects text until space/enter is pressed, then processes it
        """
        if event.event_type == 'down':
            if event.name == 'space' or event.name == 'enter':
                if self.buffer:
                    corrected_text = self.process_text(self.buffer)
                    if corrected_text != self.buffer and self.callback:
                        self.callback(corrected_text)
                    self.buffer = ""
            elif len(event.name) == 1:  # Regular characters only
                self.buffer += event.name

    def start(self):
        """Start listening for keyboard events"""
        keyboard.on_release(self.on_key_event)

    def stop(self):
        """Stop listening for keyboard events"""
        keyboard.unhook_all()


# Test code
if __name__ == "__main__":
    def print_correction(corrected_text: str):
        print(f"Corrected text: {corrected_text}")


    fixer = KeyboardFixer()
    fixer.set_callback(print_correction)
    fixer.start()

    print("Running keyboard fixer... Press Ctrl+C to exit")
    try:
        import time

        while True:
            time.sleep(0.1)  # Keep the program running
    except KeyboardInterrupt:
        fixer.stop()