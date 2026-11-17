"""Energy-based voice activity for a 16 kHz mono wav.

speech_regions(wav) -> list of (start, end) seconds where the voice is on.
"""
import wave

import numpy as np

HOP = 0.01  # 10 ms


def envelope(path):
    w = wave.open(path)
    assert w.getframerate() == 16000 and w.getnchannels() == 1
    a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    n = int(16000 * HOP)
    win = n * 2
    frames = max(0, (len(a) - win) // n + 1)
    rms = np.array([np.sqrt(np.mean(a[i * n:i * n + win] ** 2) + 1e-12) for i in range(frames)])
    return 20 * np.log10(rms + 1e-9)


def speech_regions(path, min_sil=0.12, min_speech=0.06, margin_db=14.0):
    db = envelope(path)
    floor = np.percentile(db, 8)
    thr = floor + margin_db
    on = db > thr
    regs, start = [], None
    for i, v in enumerate(on):
        if v and start is None:
            start = i
        elif not v and start is not None:
            regs.append([start * HOP, i * HOP]); start = None
    if start is not None:
        regs.append([start * HOP, len(on) * HOP])
    # merge gaps shorter than min_sil
    merged = []
    for r in regs:
        if merged and r[0] - merged[-1][1] < min_sil:
            merged[-1][1] = r[1]
        else:
            merged.append(r)
    return [(round(a, 2), round(b, 2)) for a, b in merged if b - a >= min_speech], round(float(thr), 1), round(float(floor), 1)


if __name__ == '__main__':
    import sys
    regs, thr, floor = speech_regions(sys.argv[1])
    lo = float(sys.argv[2]) if len(sys.argv) > 2 else 0
    hi = float(sys.argv[3]) if len(sys.argv) > 3 else 1e9
    print('floor', floor, 'thr', thr)
    print(' '.join(f'{a:.2f}-{b:.2f}' for a, b in regs if b >= lo and a <= hi))
