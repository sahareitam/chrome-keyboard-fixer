import keyboard
import pyperclip
from language_detector import LanguageDetector


class KeyboardFixer:
    def __init__(self):
        self.detector = LanguageDetector()

    def on_hotkey(self):
        """
        Handles the hotkey press to convert the last typed segment and adjust cursor position.
        """
        try:
            # Attempt to get the clipboard text
            text = pyperclip.paste()

            print(f"Received text: {text}")  # Debugging log

            if text:
                # Convert the last language part
                converted_text = self.detector.convert_last_language(text)
                print(f"Converted text: {converted_text}")  # Debugging log

                # Update the clipboard with the converted text
                pyperclip.copy(converted_text)

                # Simulate pasting the converted text
                keyboard.write(converted_text)

                # Adjust the cursor position
                last_segment_language = self.detector.detect_character_language(converted_text[-1])
                if last_segment_language == "hebrew":
                    keyboard.press_and_release('home')  # Move cursor to the start for RTL
                elif last_segment_language == "english":
                    keyboard.press_and_release('end')  # Move cursor to the end for LTR

        except Exception as e:
            print(f"Error during hotkey processing: {str(e)}")

    def start(self):
        """
        Start listening for the hotkey.
        """
        keyboard.add_hotkey('ctrl+shift+z', self.on_hotkey)
        print("KeyboardFixer started - Press Ctrl+Shift+Z to convert last segment of text")

    def stop(self):
        """
        Stop listening for hotkeys.
        """
        keyboard.unhook_all()


if __name__ == "__main__":
    fixer = KeyboardFixer()
    fixer.start()

    # Keep the script running until the user presses ESC
    try:
        keyboard.wait('esc')
    except KeyboardInterrupt:
        fixer.stop()
