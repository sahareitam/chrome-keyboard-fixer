# Keyboard Layout Fixer

A Chrome extension with a Python backend for fixing text typed with the wrong keyboard layout, specifically designed for Hebrew-English switching.

## Key Features

- Instant conversion of text typed in the wrong keyboard layout
- Support for bidirectional Hebrew-English conversion
- Works in any text input field on any website
- Simple keyboard shortcut (Ctrl+Shift+Z) to trigger conversion
- Smart handling of mixed language text
- Preserves cursor position based on text direction (RTL/LTR)

## Project Structure

```
chrome-keyboard-fixer/
├── extension/
│   ├── icons/
│   │   ├── icon.svg
│   │   ├── icon16.png
│   │   ├── icon48.png
│   │   └── icon128.png
│   ├── background.js
│   ├── content.js
│   └── manifest.json
└── python/
    ├── app.py
    ├── keyboard_fixer.py
    ├── language_detector.py
    └── test.py
```

## Installation

### Chrome Extension

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" in the top right
3. Click "Load unpacked" and select the `extension` folder
4. The extension icon should appear in your Chrome toolbar

### Python Backend

1. Ensure Python 3.7+ is installed
2. Install required packages:
```bash
cd python
pip install flask flask-cors keyboard pyperclip
```
3. Start the server:
```bash
python app.py
```

## Usage

1. Make sure the server is running
2. Type text in any input field on any website
3. If you realize you typed with the wrong keyboard layout, press Ctrl+Shift+Z
4. The text will automatically be converted to the correct layout

## System Components

### Chrome Extension

- **manifest.json**: Extension permissions and configuration
- **background.js**: Handles communication with Python backend
- **content.js**: Manages text selection and conversion in web pages

### Python Backend

- **app.py**: Flask server providing the conversion API
- **language_detector.py**: Core logic for language detection and conversion
- **keyboard_fixer.py**: Handles system-wide keyboard shortcuts
- **test.py**: Test script for conversion functionality

## API Endpoint

### POST /convert

Converts text between Hebrew and English layouts.

Request body:
```json
{
    "text": "string"
}
```

Response:
```json
{
    "convertedText": "string"
}
```

## System Requirements

- Python 3.7+
- Chrome browser
- Required Python packages:
  - flask
  - flask-cors
  - keyboard
  - pyperclip

## Troubleshooting

1. **Extension not converting text**
   - Ensure the server is running
   - Check Chrome console for error messages
   - Verify the keyboard shortcut isn't conflicting with other extensions

2. **Server connection issues**
   - Confirm the server is running on port 5000
   - Check if antivirus/firewall is blocking the connection
   - Verify host permissions in manifest.json