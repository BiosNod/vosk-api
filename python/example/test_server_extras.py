from flask import (
    Flask,
    jsonify,
    request,
    abort
)
from flask_cors import CORS
from flask_compress import Compress
from vosk import Model, KaldiRecognizer, SetLogLevel
import soundfile
import wave

port = 5100
host = "127.0.0.1"
# host = "localhost"
# host = "0.0.0.0"

app = Flask(__name__)
CORS(app)  # allow cross-domain requests
Compress(app)  # compress responses

print("Initializing Vosk speech-recognition (from ST request file)")
model = Model(lang="ru")

DEBUG_PREFIX = "<stt vosk module>"
RECORDING_FILE_PATH = "stt_test.wav"

def process_audio():
    """
    Transcript request audio file to text using Whisper
    """

    if model is None:
        print(DEBUG_PREFIX, "Vosk model not initialized yet.")
        return ""

    try:
        file = request.files.get('AudioFile')
        file.save(RECORDING_FILE_PATH)
        print("Save audio to: " + RECORDING_FILE_PATH)

        # Read and rewrite the file with soundfile
        data, samplerate = soundfile.read(RECORDING_FILE_PATH)
        soundfile.write(RECORDING_FILE_PATH, data, samplerate)

        wf = wave.open(RECORDING_FILE_PATH, "rb")
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
            print("Audio file must be WAV format mono PCM.")
            abort(500, DEBUG_PREFIX + " Audio file must be WAV format mono PCM.")

        rec = KaldiRecognizer(model, wf.getframerate())
        # rec.SetWords(True)
        # rec.SetPartialWords(True)

        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                print('Break due to zero data length')
                break
            if rec.AcceptWaveform(data):
                print('Break due to AcceptWaveform == True')
                break

        transcript = rec.Result()[14:-3]
        print(DEBUG_PREFIX, "Transcripted from request audio file:", transcript)
        return jsonify({"transcript": transcript})

    except Exception as e:  # No exception observed during test but we never know
        print(e)
        abort(500, DEBUG_PREFIX + " Exception occurs while processing audio")


app.add_url_rule(
    "/api/speech-recognition/vosk/process-audio",
    view_func=process_audio,
    methods=["POST"]
)

app.run(host=host, port=port)
