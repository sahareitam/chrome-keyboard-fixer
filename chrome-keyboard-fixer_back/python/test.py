from keyboard_fixer import KeyboardFixer


def on_text_converted(converted_text: str, conversion_type: str):
    print("\nConverted text:")
    print(f"Original text -> Converted text:")
    print(f"{converted_text}")
    print(f"Conversion type: {conversion_type}")
    print("\nPress Ctrl+Alt to convert between layouts")
    print("Press Ctrl+C to exit")


def main():
    fixer = KeyboardFixer()
    fixer.set_conversion_callback(on_text_converted)

    print("Keyboard Fixer Test")
    print("------------------")
    print("Press Ctrl+Alt to convert text between Hebrew and English layouts")
    print("Example test cases to try:")
    print("1. Hebrew in English: vhh nv eurv?")
    print("2. English in Hebrew: יקללם ״םצלד")
    print("\nPress Ctrl+C to exit")

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