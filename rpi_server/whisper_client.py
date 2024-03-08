import threading
from datetime import datetime

import sounddevice as sd
from pydub import AudioSegment
import requests
import wavio
import chat_completion


def record_audio():
    fs = 44100
    seconds = 3600
    print("Recording started. Press Enter to stop.")

    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2, dtype='int16')
    sd.wait()
    return myrecording


def save_recording(recording, fs):
    filename = "audio_files/output.wav"
    print(f"Saving recording as {filename}")
    wavio.write(filename, recording, fs, sampwidth=2)
    print(f"Recording saved as {filename}")


def send_audio_and_get_transcription(mp3_filename):
    url = 'http://100.101.173.98/'
    files = {'audio': open(mp3_filename, 'rb')}
    response = requests.post(url, files=files)
    return response.text


def trim_audio(file_path, start_time, end_time):
    duration_limit = end_time - start_time
    audio = AudioSegment.from_wav(file_path)
    trimmed_audio = audio[:int(duration_limit.total_seconds() * 1000)]
    trimmed_audio.export(file_path, format="wav")
    print(f"Audio trimmed to {end_time-start_time} seconds.")


def save_to_mp3(wav_filename):
    mp3_filename = wav_filename.replace(".wav", ".mp3")
    audio = AudioSegment.from_wav(wav_filename)
    audio.export(mp3_filename, format="mp3")
    print(f"{wav_filename} converted to {mp3_filename}")
    return mp3_filename


def main():
    history = []
    while True:
        input("Press Enter to start recording...")
        start_time = datetime.now()
        recording_thread = threading.Thread(target=lambda: save_recording(record_audio(), 44100))
        recording_thread.start()
        input()
        sd.stop()
        end_time = datetime.now()
        recording_thread.join()

        trim_audio("audio_files/output.wav", start_time, end_time)
        mp3_filename = save_to_mp3("audio_files/output.wav")
        result = send_audio_and_get_transcription(mp3_filename)
        print("Transcription:", result)

        answer = chat_completion.get_answer(result, history)
        print("Answer:", answer["response"], answer["tag"])
        history = answer["history"]


if __name__ == '__main__':
    main()
