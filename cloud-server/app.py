from flask import Flask, request, jsonify
from language_detector import LanguageDetector
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
detector = LanguageDetector()


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
    data = request.get_json()
    text = data.get('text', '')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    # Convert the text using the detector
    converted_text = detector.convert_last_language(text)

    return jsonify({'convertedText': converted_text})


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST')
    return response


if __name__ == '__main__':
    app.run(debug=True)