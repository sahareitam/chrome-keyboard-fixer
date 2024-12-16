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
├── cloud-server/
│   ├── .gcloudignore
│   ├── app.py
│   ├── app.yaml
│   ├── keyboard_fixer.py
│   ├── language_detector.py
│   └── requirements.txt
├── extension/
│   ├── icons/
│   │   ├── icon128.png
│   │   ├── icon16.png
│   │   ├── icon48.png
│   │   └── keyboard-key-logo.svg
│   ├── background.js
│   ├── content.js
│   ├── manifest.json
│   ├── newtab.html
│   └── redirect.js
├── .gitignore
├── README.md
└── package-lock.json
```

## Installation

### Chrome Extension

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" in the top right
3. Click "Load unpacked" and select the `extension` folder
4. The extension icon should appear in your Chrome toolbar

### Cloud Server on GCP

1. Ensure you have the Google Cloud SDK installed and configured
2. Deploy the server to GCP using the following commands:
```bash
cd cloud-server
gcloud app deploy app.yaml
```
3. Verify the server is running at the deployed URL

### Local Python Backend (Optional)

1. Ensure Python 3.7+ is installed
2. Install required packages:
```bash
cd cloud-server
pip install -r requirements.txt
```
3. Start the server locally:
```bash
python app.py
```

## Usage

1. Ensure the server is running (GCP or locally)
2. Type text in any input field on any website
3. If you realize you typed with the wrong keyboard layout, press Ctrl+Shift+Z
4. The text will automatically be converted to the correct layout

## System Components

### Chrome Extension

- **manifest.json**: Extension permissions and configuration
- **background.js**: Handles communication with the backend server
- **content.js**: Manages text selection and conversion in web pages
- **newtab.html**: Custom New Tab page with redirection logic
- **redirect.js**: Redirects the New Tab to Google

### Cloud Server (GCP)

- **app.py**: Flask server providing the conversion API
- **app.yaml**: Configuration file for GCP deployment
- **keyboard_fixer.py**: Handles keyboard layout conversion logic
- **language_detector.py**: Core logic for language detection
- **requirements.txt**: List of dependencies
- **.gcloudignore**: Files excluded during deployment

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
- Google Cloud SDK (for deployment)
- Required Python packages:
  - flask
  - flask-cors
  - keyboard
  - pyperclip

## Troubleshooting

1. **Extension not converting text**
   - Ensure the server is running or connected to the remote GCP backend
   - Check Chrome console for error messages
   - Verify the keyboard shortcut isn't conflicting with other extensions

2. **Server connection issues**
   - Confirm the server is accessible on GCP
   - Check if antivirus/firewall is blocking the connection
   - Verify host permissions in manifest.json
