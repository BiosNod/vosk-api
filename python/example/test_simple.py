#!/usr/bin/env python3

import wave
import sys
import json
import numpy as np
import io

from vosk import Model, KaldiRecognizer, SetLogLevel


def stereo_to_mono(audio_data):
    return np.mean(audio_data, axis=1, dtype=audio_data.dtype)


# You can set log level to -1 to disable debug messages
SetLogLevel(0)

wf = wave.open(sys.argv[1], "rb")
if wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
    print("Audio file must be WAV format PCM.")
    sys.exit(1)

# Convert to mono if stereo
if wf.getnchannels() == 2:
    print("Converting stereo to mono")
    audio = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
    audio = audio.reshape(-1, 2)
    audio_mono = stereo_to_mono(audio)

    # Create a new in-memory wave file
    bytes_io = io.BytesIO()
    mono_wf = wave.open(bytes_io, 'wb')
    mono_wf.setnchannels(1)
    mono_wf.setsampwidth(wf.getsampwidth())
    mono_wf.setframerate(wf.getframerate())
    mono_wf.writeframes(audio_mono.tobytes())
    mono_wf.close()

    # Reopen the in-memory file for reading
    bytes_io.seek(0)
    wf = wave.open(bytes_io, 'rb')

#model = Model(lang="en-us")
model = Model(lang="ru")

# You can also init model by name or with a folder path
# model = Model(model_name="vosk-model-en-us-0.21")
# model = Model("models/en")

rec = KaldiRecognizer(model, wf.getframerate())
rec.SetWords(True)
rec.SetPartialWords(True)
recognizedText = ''

while True:
    data = wf.readframes(4000)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        stepResult = rec.Result()
        # print(stepResult)
        recognizedText += ' ' + json.loads(stepResult)['text'] + '.'
    else:
        # don't show this due to a lot of log messages
        partialResult = rec.PartialResult()
        # print(partialResult)

# print(rec.FinalResult())
recognizedText += ' ' + json.loads(rec.FinalResult())['text'] + '.'
print(json.dumps({'result': recognizedText}, ensure_ascii=False))
