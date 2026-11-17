"""Render an Episode 2 reel: his voice, hook card, word captions, progress bar. No music since Nov 17 (USE_MUSIC).

usage: python3 render.py <clip> [--test SECONDS]      (run from /home/claude/wm)
       python3 render.py --swap-audio RENDERED_DIR OUT_DIR <clip> ...   (new sound, same picture)
The end card that is already on the clip is left alone; everything added fades out with the clip's own crossfade.
"""
import json
import re
import subprocess
import sys

sys.path.insert(0, '/home/claude/wm/scripts')
from caps import CLIPS, XFADE  # noqa: E402

WM = '/home/claude/wm'
MUSIC = ('/mnt/user-data/uploads/Podcast Episodes/Music/inspiring-hip-hop-ambient/'
         'Inspiring Hip-Hop Ambient by Nicolas T/Main Version (1 min 56 sec).wav')
MUSIC_LUFS = -8.5        # measured
BED_LUFS = -25.0         # bed level before ducking; lands near -28 dBFS in his pauses, as in the Episode 1 reels
TARGET_LUFS = -14.0
USE_MUSIC = False        # Rod, Nov 17: "lets do these clips without the music". True brings the bed back.
HOOK_Y = 98              # card top lands at y=112, where the Episode 1 hook cards sat


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


def loudness(path):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-map', '0:a', '-af', 'ebur128=peak=true:framelog=quiet', '-f', 'null', '-'],
                       capture_output=True, text=True)
    tail = r.stderr[r.stderr.rfind('Summary:'):]
    i = float(re.search(r'I:\s+(-?[\d.]+) LUFS', tail).group(1))
    pk = float(re.search(r'Peak:\s+(-?[\d.]+) dBFS', tail).group(1))
    return i, pk


def mix_audio(k, music=None):
    """Write mix/<k>.wav: his voice at the target level, with the ducked bed only when music is on."""
    body = CLIPS[k]['body']
    src = f'{WM}/src/{k}.mp4'
    out = f'{WM}/mix/{k}.wav'
    i, _ = loudness(src)
    gain = TARGET_LUFS - i
    if not (USE_MUSIC if music is None else music):
        # voice only: the same gain and limiter the music mix used, so his level does not change
        fc = (f"[0:a]aresample=48000,volume={gain:.2f}dB,"
              "alimiter=limit=0.89:attack=5:release=60:level=disabled[a]")
        run(['ffmpeg', '-y', '-v', 'error', '-i', src, '-filter_complex', fc, '-map', '[a]',
             '-ar', '48000', '-ac', '2', '-c:a', 'pcm_s16le', out])
        return dict(src_lufs=i, gain=round(gain, 2), music=False, out_lufs=loudness(out))
    bed = BED_LUFS - MUSIC_LUFS
    fo_st = body - 1.3
    if body <= 112:
        music = (f"[1:a]atrim=0.8:{0.8 + body:.3f},asetpts=PTS-STARTPTS,aresample=48000,"
                 f"volume={bed:.2f}dB,afade=t=in:d=0.8,afade=t=out:st={fo_st:.3f}:d=1.0[m]")
        ins = ['-i', MUSIC]
    else:
        # the bed is 1:56 long; bring a second pass in under the tail of the first
        second_at = 106.0
        music = (f"[1:a]atrim=0.8:112.8,asetpts=PTS-STARTPTS,aresample=48000,afade=t=in:d=0.8,afade=t=out:st=106:d=6[ma];"
                 f"[2:a]atrim=13:{13 + body - second_at:.3f},asetpts=PTS-STARTPTS,aresample=48000,afade=t=in:d=6,"
                 f"adelay={int(second_at * 1000)}:all=1[mb];"
                 f"[ma][mb]amix=inputs=2:normalize=0:duration=longest,volume={bed:.2f}dB,"
                 f"afade=t=out:st={fo_st:.3f}:d=1.0[m]")
        ins = ['-i', MUSIC, '-i', MUSIC]
    fc = (f"[0:a]aresample=48000,volume={gain:.2f}dB,asplit=2[v][key];" + music +
          ";[m][key]sidechaincompress=threshold=0.05:ratio=3:attack=20:release=300:makeup=1[duck];"
          "[v][duck]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.89:attack=5:release=60:level=disabled[a]")
    run(['ffmpeg', '-y', '-v', 'error', '-i', src, *ins, '-filter_complex', fc, '-map', '[a]', '-ar', '48000', '-ac', '2', '-c:a', 'pcm_s16le', out])
    return dict(src_lufs=i, gain=round(gain, 2), music=True, out_lufs=loudness(out))


def swap_audio(k, video, out):
    """Put mix/<k>.wav on a reel that is already rendered. The picture is copied, not re-encoded."""
    run(['ffmpeg', '-y', '-v', 'error', '-i', video, '-i', f'{WM}/mix/{k}.wav', '-map', '0:v', '-map', '1:a',
         '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart', out])
    return out


def render(k, test=None):
    body = CLIPS[k]['body']
    fade_st = body - XFADE
    src = f'{WM}/src/{k}.mp4'
    fc = (
        f"[1:v]format=rgba,fade=t=in:st=0:d=0.3:alpha=1,fade=t=out:st=4.55:d=0.4:alpha=1[hook];"
        f"[3:v]format=rgba,colorchannelmixer=aa=0.6,fade=t=out:st={fade_st:.3f}:d={XFADE}:alpha=1[track];"
        f"[2:v]format=rgba,fade=t=out:st={fade_st:.3f}:d={XFADE}:alpha=1[bar];"
        f"[0:v]ass={WM}/ass/{k}.ass:fontsdir=/home/claude/fonts[c];"
        f"[c][track]overlay=x=0:y=1906:eof_action=pass[c1];"
        f"[c1][bar]overlay=x='-1080+1080*t/{body:.3f}':y=1906:eof_action=pass[c2];"
        f"[c2][hook]overlay=x=0:y='if(lt(t,0.3),{HOOK_Y}-36*(0.3-t)/0.3,{HOOK_Y})':eof_action=pass[v]"
    )
    out = f'{WM}/out/{k}.mp4' if test is None else f'{WM}/out/{k}_test.mp4'
    cmd = ['ffmpeg', '-y', '-v', 'error', '-i', src,
           '-loop', '1', '-framerate', '30', '-t', '5.0', '-i', f'{WM}/ass/{k}_hook.png',
           '-f', 'lavfi', '-t', f'{body:.3f}', '-i', 'color=c=0xf16b2e:s=1080x14:r=30',
           '-f', 'lavfi', '-t', f'{body:.3f}', '-i', 'color=c=0x231f20:s=1080x14:r=30',
           '-i', f'{WM}/mix/{k}.wav',
           '-filter_complex', fc, '-map', '[v]', '-map', '4:a',
           '-c:v', 'libx264', '-preset', 'fast', '-crf', '21', '-maxrate', '6M', '-bufsize', '12M',
           '-pix_fmt', 'yuv420p', '-r', '30', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart']
    if test is not None:
        cmd += ['-t', str(test)]
    cmd.append(out)
    run(cmd)
    return out


if __name__ == '__main__':
    import os
    import time
    os.makedirs(f'{WM}/mix', exist_ok=True)
    os.makedirs(f'{WM}/out', exist_ok=True)
    args = sys.argv[1:]
    test = None
    if '--test' in args:
        j = args.index('--test')
        test = float(args[j + 1])
        args = args[:j] + args[j + 2:]
    if '--swap-audio' in args:
        # new sound on reels that are already rendered:
        #   python3 render.py --swap-audio RENDERED_DIR OUT_DIR c1 c2 ...
        j = args.index('--swap-audio')
        src_dir, out_dir, keys = args[j + 1], args[j + 2], args[j + 3:]
        os.makedirs(out_dir, exist_ok=True)
        for k in keys:
            a = mix_audio(k)
            name = f'ep02-clip{int(k[1:]):02d}.mp4'
            o = swap_audio(k, f'{src_dir}/{name}', f'{out_dir}/{name}')
            print(k, json.dumps(a), o, flush=True)
        sys.exit(0)
    for k in args:
        t0 = time.time()
        a = mix_audio(k)
        o = render(k, test)
        print(k, json.dumps(a), o, f'{time.time() - t0:.0f}s', flush=True)
