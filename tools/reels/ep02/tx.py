"""Transcribe a 16 kHz mono wav with word timestamps.

usage: python3 -I tx.py <model_dir> <stub_dir> <wav> <out.jsonl>
Each output line: {"s": start, "e": end, "t": text, "w": [[start, end, word], ...]}
"""
import sys

MODEL_DIR, STUB_DIR, WAV, OUT = sys.argv[1:5]
sys.path.insert(0, STUB_DIR)  # empty `av` stub so faster-whisper imports without PyAV

import json
import wave

import numpy as np
from faster_whisper import WhisperModel

PROMPT = (
    "Beyond the Brand, a podcast with Rod Brinson. Laid off after 20 years in corporate America. "
    "Severance, unemployment, COBRA, the Marketplace, 401(k), Canva, Bank of America, DocuSign, "
    "Joseph, Genesis 50:20, House of Brand."
)

w = wave.open(WAV)
assert w.getframerate() == 16000 and w.getnchannels() == 1, "need 16 kHz mono"
audio = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768

m = WhisperModel(MODEL_DIR, device="cpu", compute_type="int8", cpu_threads=2)
segs, info = m.transcribe(
    audio,
    language="en",
    beam_size=5,
    word_timestamps=True,
    condition_on_previous_text=False,
    initial_prompt=PROMPT,
    vad_filter=False,
)
with open(OUT, "w") as f:
    for s in segs:
        row = {
            "s": round(s.start, 2),
            "e": round(s.end, 2),
            "t": s.text.strip(),
            "w": [[round(x.start, 2), round(x.end, 2), x.word] for x in (s.words or [])],
        }
        f.write(json.dumps(row) + "\n")
        f.flush()
print("done", flush=True)
