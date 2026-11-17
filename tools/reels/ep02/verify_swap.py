"""Check reels whose sound was swapped: same picture, same length, sane levels, and how quiet the pauses are.

usage: python3 verify_swap.py OLD_DIR NEW_DIR
"""
import subprocess
import sys

import numpy as np

sys.path.insert(0, '/home/claude/wm/scripts')
from render import loudness  # noqa: E402


def vhash(p):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-map', '0:v', '-c', 'copy', '-f', 'md5', '-'],
                       capture_output=True, text=True, check=True)
    return r.stdout.strip()[-8:]


def probe(p):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_name,width,height,r_frame_rate,sample_rate,duration',
                        '-of', 'csv=p=0', p], capture_output=True, text=True, check=True)
    return ' | '.join(r.stdout.split())


def pause_floor(p):
    """RMS of 0.4 sec windows, in dBFS: the quiet tenth, and the middle."""
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-map', '0:a', '-ac', '1', '-ar', '16000', '-f', 's16le', '-'],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
    n = 6400
    w = x[:len(x) // n * n].reshape(-1, n)
    db = 10 * np.log10((w ** 2).mean(axis=1) + 1e-12)
    return round(float(np.percentile(db, 10)), 1), round(float(np.percentile(db, 50)), 1)


old, new = sys.argv[1], sys.argv[2]
for i in range(1, 7):
    name = f'ep02-clip{i:02d}.mp4'
    a, b = f'{old}/{name}', f'{new}/{name}'
    print(name)
    print('  new streams:', probe(b))
    print('  same picture:', vhash(a) == vhash(b))
    print('  loudness LUFS / true peak dBFS  old:', loudness(a), ' new:', loudness(b))
    print('  pause floor (p10, p50 dBFS)     old:', pause_floor(a), ' new:', pause_floor(b))
