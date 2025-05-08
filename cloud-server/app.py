from flask import Flask, request, jsonify
from langchain_vertex_analyzer import LangChainTextAnalyzer  #
from flask_cors import CORS
from api_limiter import initialize_api_limiter
import time
import logging

app = Flask(__name__)
CORS(app)

try:
    text_analyzer = LangChainTextAnalyzer()
    ai_analysis_available = text_analyzer.is_available()
    logging.info(f"AI text analysis available: {ai_analysis_available}")
except Exception as e:
    logging.error(f"Failed to initialize LangChainTextAnalyzer: {str(e)}")
    ai_analysis_available = False
    text_analyzer = None

# Initialize API limiter with 40 max concurrent requests
api_limiter = initialize_api_limiter(app, max_concurrent_calls=40)


@app.route('/', methods=['GET', 'POST'])
def convert_text():
    """
    API endpoint to convert text based on the new AI-powered analysis.
    For POST: Analyzes and corrects the text
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

        # Use the AI analyzer to get corrected text
        if ai_analysis_available and text_analyzer:
            result = text_analyzer.analyze_and_correct_text(text)
            return jsonify({'convertedText': result['corrected_text']})
        else:
            return jsonify({'error': 'AI text analysis is not available'}), 503

    except Exception as e:
        logging.error(f"Error in text analysis: {str(e)}")
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

        # Use the AI analyzer to get corrected text
        if ai_analysis_available and text_analyzer:
            result = text_analyzer.analyze_and_correct_text(text)
            return jsonify({'convertedText': result['corrected_text']})
        else:
            return jsonify({'error': 'AI text analysis is not available'}), 503

    except Exception as e:
        logging.error(f"Error in text analysis: {str(e)}")
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint with system information
    """
    status_info = {
        'status': 'healthy',
        'active_api_calls': api_limiter.active_calls,
        'ai_analysis_available': ai_analysis_available,
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