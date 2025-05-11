# KeyFixer – Switch Hebrew ↔ English Keyboard Layout

A Chrome extension with an AI-powered Python backend for fixing text typed with the wrong keyboard layout, specifically designed for Hebrew-English switching and translation.

## Key Features

- **Instant Conversion**: Instantly fix text typed with the wrong keyboard layout
- **Bidirectional Support**: Convert between Hebrew and English layouts seamlessly
- **AI-Powered Correction**: Uses LangChain with Vertex AI for smart text correction
- **Instant Translation**: Translate text between Hebrew and English with a keyboard shortcut
- **Cross-Website Compatibility**: Works in any text input field on any website
- **Keyboard Shortcuts**:
  - `Ctrl+Shift+Z`: Convert between keyboard layouts
  - `Ctrl+Shift+X`: Translate text between Hebrew and English
- **Smart Direction Handling**: Automatically positions cursor based on text direction (RTL/LTR)
- **Undo Support**: Easily revert back to original text with standard `Ctrl+Z`
- **Rate Limiting**: Built-in API rate limiting to prevent abuse
- **Cloud Deployment Ready**: Configured for Google Cloud Platform deployment

## Project Structure

```
chrome-keyboard-fixer/
├── cloud-server/                 # AI-powered backend server for GCP
│   ├── .gcloudignore             # Files to ignore during GCP deployment
│   ├── api_limiter.py            # API rate limiting implementation
│   ├── app.py                    # Main Flask server with API endpoints
│   ├── app.yaml                  # GCP configuration for deployment
│   ├── .env.example              # Environment variables template
│   ├── langchain_vertex_analyzer.py # LangChain integration with Vertex AI
│   ├── language_detector.py      # Core logic for language detection and conversion
│   └── requirements.txt          # Python dependencies
├── extension/                    # Chrome extension files
│   ├── icons/                    # Extension icons in various sizes
│   │   ├── icon128.png
│   │   ├── icon16.png
│   │   ├── icon48.png
│   │   └── keyboard-key-logo.svg # Vector logo for the extension
│   ├── background.js             # Extension background service worker
│   ├── content.js                # Content script for webpage interaction
│   ├── manifest.json             # Extension configuration
│   ├── newtab.html               # Custom new tab page
│   └── redirect.js               # Redirect script for new tab
├── .gitignore                    # Files excluded from version control
├── README.md                     # This documentation file
└── test_load.py                  # Load testing script for the API
```

## Advanced System Components

### Chrome Extension

- **manifest.json**: Extension permissions and configuration with manifest v3 support
- **background.js**: Service worker that handles communication with backend servers and manages request queuing
- **content.js**: Monitors and interacts with web page text inputs, handles keyboard shortcuts, and ensures proper cursor positioning
- **newtab.html & redirect.js**: Custom New Tab page that redirects to Google Israel

### Cloud Server (GCP)

- **app.py**: Flask server providing conversion and translation APIs with health checking
- **api_limiter.py**: Thread-safe rate limiting to protect the service
- **langchain_vertex_analyzer.py**: AI-powered text analysis using LangChain and Google Vertex AI
- **language_detector.py**: Core logic for keyboard layout conversion
- **app.yaml**: Configuration for Google Cloud App Engine deployment
- **.env.example**: Template for configuring environment variables

## LangChain Integration

The project uses LangChain with Google Vertex AI for enhanced text processing:

- **VertexAI Model**: Integration with Google's Vertex AI models (default: gemini-2.0-flash)
- **PromptTemplate**: Structured prompt engineering for text correction
- **Chain Construction**: Composable chains for text analysis and correction
- **Error Handling**: Robust retry logic and fallback mechanisms
- **Environment Detection**: Automatic configuration based on local or cloud environment

## API Endpoints

### POST /api/convert

Converts text between Hebrew and English keyboard layouts with AI enhancement.

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

### POST /api/translate

Translates text between Hebrew and English languages.

Request body:
```json
{
    "text": "string"
}
```

Response:
```json
{
    "translatedText": "string"
}
```

### GET /health

Returns system health status and metrics.

Response:
```json
{
    "status": "healthy",
    "active_api_calls": 0,
    "ai_analysis_available": true,
    "time": 1620000000.0
}
```

## Installation

### Chrome Extension

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" in the top right
3. Click "Load unpacked" and select the `extension` folder
4. The extension icon should appear in your Chrome toolbar

### Cloud Server on GCP

1. Ensure you have the Google Cloud SDK installed and configured
2. Create a `.env` file in the `cloud-server` directory using the `.env.example` template
3. Set up a Google Cloud project with Vertex AI enabled
4. Deploy the server to GCP using the following commands:
```bash
cd cloud-server
gcloud app deploy app.yaml
```
5. Update the `API_ENDPOINT` and `TRANSLATION_ENDPOINT` variables in `extension/background.js` to point to your deployed API

### Local Development Server

1. Ensure Python 3.9+ is installed
2. Install required packages:
```bash
cd cloud-server
pip install -r requirements.txt
```
3. Create a `.env` file from the `.env.example` template:
```bash
cp .env.example .env
```
4. Edit the `.env` file with your Google Cloud project details and credentials
5. Start the server locally:
```bash
python app.py
```
6. Update the `API_ENDPOINT` and `TRANSLATION_ENDPOINT` variables in `extension/background.js` to point to `http://localhost:5000/api/convert` and `http://localhost:5000/api/translate` respectively

## Usage

1. Ensure the server is running (GCP or locally)
2. Type text in any input field on any website
3. If you realize you typed with the wrong keyboard layout, press `Ctrl+Shift+Z`
4. To translate text between Hebrew and English, press `Ctrl+Shift+X`
5. The text will automatically be converted or translated

## System Requirements

- Python 3.9
- Chrome browser
- Google Cloud SDK (for deployment)
- Required Python packages:
  - flask
  - flask-cors
  - langchain
  - langchain-google-vertexai
  - google-cloud-aiplatform
  - python-dotenv

## Developer Notes

### Extension Development

- The extension uses manifest v3 and service workers
- Content scripts are injected into all web pages to monitor text inputs
- The `activeTab` permission is used to interact with the current tab
- Background scripts handle communication with the backend API

### Backend Development

- The server uses Flask for API endpoints
- Rate limiting is implemented to prevent abuse
- LangChain is used for AI-powered text correction and translation
- Vertex AI integration provides advanced language capabilities
- The server automatically detects whether it's running in GCP or locally

### Testing

- Use the included `test_load.py` script to test API performance
- Adjust the `MAX_CONCURRENT_CALLS` value in `app.yaml` to optimize performance

## Troubleshooting

1. **Extension not converting text**
   - Ensure the server is running or connected to the remote GCP backend
   - Check Chrome console for error messages
   - Verify the API endpoints in `background.js` are correct

2. **Server connection issues**
   - Confirm the server is accessible on GCP
   - Check if antivirus/firewall is blocking the connection
   - Verify host permissions in manifest.json

3. **AI analysis not working**
   - Check that your Google Cloud project has the Vertex AI API enabled
   - Verify the service account has the necessary permissions
   - Ensure the environment variables in `.env` are correctly set

4. **Rate limiting errors**
   - If you see "Too many requests" errors, adjust the rate limiting in `api_limiter.py`
   - For production, increase the `MAX_CONCURRENT_CALLS` value in `app.yaml`

