from flask import Flask, request, jsonify
from language_detector import LanguageDetector
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
detector = LanguageDetector()

@app.route('/convert', methods=['POST'])
def convert_text():
    """
    API endpoint to convert text based on the last language.
    """
    data = request.get_json()
    text = data.get('text', '')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    # Convert the text using the detector
    converted_text = detector.convert_last_language(text)

    return jsonify({'convertedText': converted_text})

if __name__ == '__main__':
    app.run(debug=True)
