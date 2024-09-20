#!/usr/bin/env python3

import json
import gradio as gr

from vosk import KaldiRecognizer, Model

model = Model(lang="ru")
# model = Model(lang="en-us")

def transcribe(stream, new_chunk):
    if new_chunk:
        sample_rate, audio_data = new_chunk
        audio_data = audio_data.tobytes()
        rec = None

        rec, result = stream or (None, None)
        if rec is None:
            rec = KaldiRecognizer(model, sample_rate)
            result = []

        if rec.AcceptWaveform(audio_data):
            text_result = json.loads(rec.Result())["text"]
            if text_result != "":
                result.append(text_result)
            partial_result = ""
        else:
            partial_result = json.loads(rec.PartialResult())["partial"] + " "

        return (rec, result), "\n".join(result) + "\n" + partial_result
    else:
        print("Empty new_chunk, skip it")
        return (None, None), ""

gr.Interface(
    fn=transcribe,
    inputs=[
        "state", gr.Audio(sources=["microphone"], type="numpy", streaming=True),
    ],
    outputs=[
        "state", "text",
    ],
    live=True).launch(share=True)
