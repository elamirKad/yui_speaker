from flask import Flask, request, jsonify
import tempfile
import subprocess
import os
import json

app = Flask(__name__)


@app.route('/', methods=['POST'])
def handle_request():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file part"}), 400
    file = request.files['audio']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    with tempfile.TemporaryDirectory() as tmpdirname:
        tmpfile_path = os.path.join(tmpdirname, 'output.mp3')
        output_json_path = os.path.join(tmpdirname, 'output.json')

        file.save(tmpfile_path)

        command = ["whisper", tmpfile_path, "--model", "medium.en", "--language", "English", "--output_format", "json",
                   "-o", tmpdirname]
        subprocess.run(command, check=True)

        if os.path.exists(output_json_path):
            with open(output_json_path, 'r') as f:
                transcription_result = json.load(f)
            full_transcript = " ".join(segment["text"] for segment in transcription_result["segments"])
            full_transcript.strip()
        else:
            return jsonify({"error": "Failed to generate transcription output"}), 500

    return jsonify(full_transcript)


if __name__ == '__main__':
    print("HTTP server starting. Listening for MP3 files to transcribe.")
    app.run(debug=True, host='0.0.0.0', port=8765)
