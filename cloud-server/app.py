from flask import Flask, request, jsonify
from language_detector import LanguageDetector
from flask_cors import CORS
from api_limiter import initialize_api_limiter  # New import
import time

app = Flask(__name__)
CORS(app)
detector = LanguageDetector()

# Initialize API limiter with 40 max concurrent requests
api_limiter = initialize_api_limiter(app, max_concurrent_calls=40)


@app.route('/', methods=['GET', 'POST'])
def convert_text():
    """
    API endpoint to convert text based on the last language.
    For POST: Converts the text
    For GET: Returns a health check
    """
    if request.method == 'GET':
        return jsonify({'status': 'healthy', 'message': 'Server is running'}), 200

    # Handle POST request
    try:
        data = request.get_json()
        text = data.get('text', '')

        if not text:
            return jsonify({'error': 'No text provided'}), 400

        # Convert the text using the detector
        converted_text = detector.convert_last_language(text)

        return jsonify({'convertedText': converted_text})

    except Exception as e:
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500


@app.route('/api/convert', methods=['POST'])
@api_limiter.limit_api(max_calls_per_minute=30)
def api_convert_text():
    """
    External API endpoint with rate limiting
    """
    try:
        data = request.get_json()
        text = data.get('text', '')

        if not text:
            return jsonify({'error': 'No text provided'}), 400

        # Convert the text using the detector
        converted_text = detector.convert_last_language(text)

        return jsonify({'convertedText': converted_text})

    except Exception as e:
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint with system information
    """
    status_info = {
        'status': 'healthy',
        'active_api_calls': api_limiter.active_calls,
        'time': time.time()
    }
    return jsonify(status_info), 200


@app.after_request
def after_request(response):
    """
    Add CORS headers to all responses
    """
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response


if __name__ == '__main__':
    app.run(debug=True)