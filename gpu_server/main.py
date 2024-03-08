from flask import Flask, request, jsonify
import whisper
import tempfile
import os

app = Flask(__name__)


@app.route('/', methods=['POST'])
def handle_request():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file part"}), 400
    file = request.files['audio']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=True) as tmpfile:
        file.save(tmpfile.name)
        result = model.transcribe(tmpfile.name)
        text = result["text"]

    return jsonify({"transcription": text})


if __name__ == '__main__':
    print("loading...")
    model = whisper.load_model("medium.en.pt", device="cuda")
    print("HTTP server starting. Listening for MP3 files to transcribe.")
    app.run(debug=True, host='0.0.0.0', port=8765)
