from keyboard_fixer import KeyboardFixer


def on_text_converted(converted_text: str, conversion_type: str):
    print("\nConverted text:", converted_text)
    print("Conversion type:", conversion_type)
    print("\nYou can continue typing... Press Ctrl+C to exit")


def main():
    print("Keyboard Layout Converter")
    print("------------------------")
    print("Instructions:")
    print("1. Type text somewhere (e.g., Notepad)")
    print("2. Copy the text (Ctrl+C)")
    print("3. Press Ctrl+Alt to convert")
    print("4. The converted text will be in your clipboard")
    print("\nPress Ctrl+C in this window to exit")

    fixer = KeyboardFixer()
    fixer.set_conversion_callback(on_text_converted)
    fixer.start()

    try:
        while True:
            import time
            time.sleep(0.1)
    except KeyboardInterrupt:
        fixer.stop()
        print("\nTest ended")


if __name__ == "__main__":
    main()