import sys
MODEL_DIR, STUB_DIR = sys.argv[1:3]
sys.path.insert(0, STUB_DIR)
import wave, numpy as np
from faster_whisper import WhisperModel
m = WhisperModel(MODEL_DIR, device="cpu", compute_type="int8", cpu_threads=2)
for wav in sys.argv[3:]:
    w = wave.open(wav); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)/32768
    for label, kw in [('plain', dict(beam_size=5)), ('prompted', dict(beam_size=5, initial_prompt="He's from Atlanta. Y'all, I'mma tell you, they ain't finna do that. They ain't gonna do that.")), ('greedy', dict(beam_size=1, temperature=0.0))]:
        segs, _ = m.transcribe(a, language='en', word_timestamps=True, condition_on_previous_text=False, **kw)
        out = ' '.join(f"{x.word.strip()}({x.probability:.2f})" for s in segs for x in s.words)
        print(wav.split('/')[-1], label, '::', out)
