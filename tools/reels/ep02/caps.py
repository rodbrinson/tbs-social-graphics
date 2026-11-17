"""Episode 2 reel captions: corrected words -> pages -> ASS, plus the hook card PNG.

usage: python3 caps.py <clip> [...]     (run from /home/claude/wm)
"""
import json
import re
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, '/home/claude/wm/scripts')
import vad  # noqa: E402

WM = '/home/claude/wm'
FONTS = '/home/claude/fonts'
ANTON = f'{FONTS}/Anton-Regular.ttf'
SERIF = f'{FONTS}/InstrumentSerif-Italic.ttf'

# ASS sizes (libass sizes by line height, not em)
FS_CAP, FS_EMPH = 118, 150
MAX_W = 930          # widest caption page, px
MARGIN_V = 540       # caption bottom sits at y = 1920 - MARGIN_V = 1380 (cards start at 1400)
XFADE = 0.30         # clip crossfades into the end card over the last 0.3 s of the body

# body = seconds before the end card is fully up (clip length - 3.2)
CLIPS = {
    'c1': dict(body=58.40, hook=['LAID OFF BY EMAIL', 'AFTER 20 YEARS'], mute=[]),
    'c2': dict(body=49.78, hook=['COMPANIES ARE CALLING BACK', 'THE PEOPLE AI REPLACED'], mute=[]),
    # 0-8.5: he reads the step title that the episode's own orange callout already shows
    'c3': dict(body=111.95, hook=['YOU CAN NEGOTIATE', 'YOUR SEVERANCE'], mute=[(0.0, 8.5)]),
    'c4': dict(body=131.23, hook=['THE COMPANY THAT LAID ME OFF', 'HIRED MY COMPANY'], mute=[]),
    'c5': dict(body=49.83, hook=['SOMEBODY WILL PAY YOU', 'FOR WHAT YOU ALREADY KNOW'], mute=[]),
    # 17.5-28.0: he reads Genesis 50:20, which the episode's scripture card already shows in full
    'c6': dict(body=40.28, hook=['YOUR LAYOFF IS THE MIDDLE', 'OF YOUR STORY'], mute=[(17.5, 28.0)]),
}

# (heard phrase, corrected phrase). Matched on lowercase words with punctuation stripped.
EDITS = {
    'c1': [],
    'c2': [
        ('got acts to come back', 'got asked to come back.'),
        ('that they\'re cut too deep', 'that they cut too deep'),
        ('so hear me a layoff', 'So hear me. A layoff'),
        ('hear it clearly your worth', 'Hear it clearly. Your worth'),
    ],
    'c3': [
        ('and now today might', 'And now, today might'),
        ('remember this part when come back', 'remember this part and come back'),
        ('laid off in that that severance paper', 'laid off and that severance paper'),
        ('in your email don\'t sign', 'in your email, don\'t sign'),
        ('now why is that', 'Now, why is that'),
        ('the the agreement', 'The agreement'),
        ('before you sign on or contract', 'before you sign, or contract'),
        ('there\'s not somebody on youtube', 'That\'s not somebody on YouTube.'),
        ('i personally even ask for', 'I personally even asked for'),
        ('i think of health care i won at six', 'I think, of health care. I wanted six.'),
        ('what you asked for so', 'what you ask for. So'),
    ],
    'c4': [
        ('i dmed her', 'I DM\'d her'),
        ('i\'m a dmer', 'I\'mma DM her.'),
        ('i said oh here\'s', 'I said, "Oh, here\'s'),
        ('my opportunity', 'my opportunity."'),
        ('and i stay connected', 'and I stayed connected'),
        ('for the same company that laid', 'for? The same company that laid'),
        ('my w2 turned', 'My W-2 turned'),
    ],
    'c5': [
        ('that\'s consulting you were', 'That\'s consulting. You were'),
        ('printers cause nobody', 'printers, \'cause nobody'),
        ('see most times we', 'See, most times we'),
        ('in it probably', 'in I.T. probably.'),
    ],
    'c6': [
        ('stood in front of them', 'stood in front of him,'),
        ('that\'s the whole story', 'It\'s a whole story.'),
        ('actual word in genesis 50 verse 20', 'actual word. In Genesis 50, verse 20,'),
        ('the bible says this', 'the Bible says this:'),
    ],
}

# phrases set in the teal serif italic (matched on the corrected words)
EMPH = {
    'c1': ['laid off', 'email.', 'six figures.', 'trust God', 'purpose,', 'ceiling', 'desperation', 'anguish.', 'for me.'],
    'c2': ['19%', 'asked', 'come back.', 'too deep', 'spreadsheet.', 'your worth', 'by God.'],
    'c3': ['21 days', '45 days.', 'seven days', 'a lawyer.', 'questions,', 'wanted six.', 'counter.', 'say no.', 'ask.'],
    'c4': ['six months.', 'Canva well.', 'enterprise', 'trained.', 'laid me off', 'hired my company', 'W-2', '1099.', 'official vendor'],
    'c5': ['skilled', 'your skill', 'to you.', 'leadership.', 'consulting.', 'pay you', 'way more', 'out loud'],
    'c6': ['who they were.', 'whole story.', 'the middle', 'yours.', 'with you.'],
}


def norm(t):
    return re.sub(r"[^a-z0-9'%$-]", '', t.lower())


def load_words(k):
    W = []
    for line in open(f'{WM}/tx/{k}.jsonl'):
        for s, e, t in json.loads(line)['w']:
            t = t.strip()
            if not t:
                continue
            if W and (t[0] in "'-%" or t in ('%',)):
                W[-1][2] += t
                W[-1][1] = e
            else:
                W.append([s, e, t])
    return W


def apply_edits(W, edits):
    for heard, fixed in edits:
        h = [norm(x) for x in heard.split()]
        new = fixed.split()
        hit = False
        for i in range(len(W) - len(h) + 1):
            if [norm(w[2]) for w in W[i:i + len(h)]] == h:
                s, e = W[i][0], W[i + len(h) - 1][1]
                if len(new) == len(h):
                    rep = [[W[i + j][0], W[i + j][1], new[j]] for j in range(len(h))]
                else:
                    # spread the corrected words over the same stretch of time, by length
                    lens = np.array([len(x) + 1 for x in new], float)
                    cuts = s + (e - s) * np.concatenate([[0], np.cumsum(lens) / lens.sum()])
                    rep = [[round(float(cuts[j]), 2), round(float(cuts[j + 1]), 2), new[j]] for j in range(len(new))]
                W[i:i + len(h)] = rep
                hit = True
                break
        if not hit:
            raise SystemExit(f'edit not found: {heard!r}')
    return W


def snap_to_voice(W, wav):
    """Whisper stretches a word back into the pause before it. Move such starts to where the voice comes in."""
    db = vad.envelope(wav)
    thr = np.percentile(db, 90) - 24.0
    on = db > thr
    hop = vad.HOP

    def voiced(t):
        i = int(t / hop)
        return 0 <= i < len(on) and on[i]

    moved = 0
    for i, w in enumerate(W):
        s, e = w[0], w[1]
        nxt = W[i + 1][0] if i + 1 < len(W) else e + 1.0
        if not voiced(s) and not voiced(s + 0.03):
            t = s
            limit = min(max(e, s + 0.2) + 0.9, nxt - 0.04)
            while t < limit and not (voiced(t) and voiced(t + 0.02)):
                t += hop
            if t < limit and t - s > 0.08:
                w[0] = round(t, 2)
                w[1] = max(w[1], w[0] + 0.12)
                moved += 1
    # trim word ends that run into silence (keeps a caption from hanging in a pause)
    for i, w in enumerate(W):
        t = w[1]
        while t > w[0] + 0.15 and not voiced(t - 0.02):
            t -= hop
        w[1] = round(max(t, w[0] + 0.12), 2)
    for a, b in zip(W, W[1:]):
        if b[0] <= a[0]:
            b[0] = round(a[0] + 0.05, 2)
        a[1] = min(a[1], b[0]) if a[1] > b[0] else a[1]
    return moved


def mark_emph(W, phrases):
    """A phrase word that ends in punctuation only matches a spoken word ending the same way."""
    flags = [False] * len(W)

    def same(spoken, want):
        if norm(spoken) != norm(want):
            return False
        tail = want[-1]
        return tail not in '.,?!:' or spoken.rstrip('"')[-1:] == tail

    for ph in phrases:
        h = ph.split()
        found = False
        for i in range(len(W) - len(h) + 1):
            if all(same(W[i + j][2], h[j]) for j in range(len(h))):
                for j in range(len(h)):
                    flags[i + j] = True
                found = True
        if not found:
            raise SystemExit(f'emphasis phrase not found: {ph!r}')
    return flags


def _pil_font(path, ass_size):
    probe = ImageFont.truetype(path, 1000)
    asc, desc = probe.getmetrics()
    return ImageFont.truetype(path, max(1, int(round(ass_size * 1000 / (asc + desc)))))


F_CAP, F_EMPH = _pil_font(ANTON, FS_CAP), _pil_font(SERIF, FS_EMPH)
_D = ImageDraw.Draw(Image.new('L', (8, 8)))


def word_w(text, emph):
    if emph:
        return _D.textlength(text, font=F_EMPH)
    return _D.textlength(text.upper(), font=F_CAP) + 1.0 * len(text)  # +1px letter spacing


def page_w(pg):
    sp = _D.textlength(' ', font=F_CAP) + 6
    return sum(word_w(w[2], w[3]) for w in pg) + sp * (len(pg) - 1)


WEAK_END = {'the', 'a', 'an', 'to', 'of', 'my', 'your', 'our', 'in', 'on', 'for', 'with', 'that', 'and', 'i',
            'or', 'but', 'is', 'was', 'at', 'it\'s', 'they', 'you', 'we', 'he', 'she', 'this', 'from', 'by', 'so',
            'too', 'no', 'not', 'very'}
STRONG_START = {'and', 'but', 'or', 'so', 'because', '\'cause', 'when', 'who', 'where', 'if', 'before', 'without'}
PARTICLES = {'off', 'up', 'out', 'back', 'down', 'over', 'through', 'away', 'ahead'}


def ends_sentence(t):
    return t.rstrip('"')[-1:] in '.?!'


def split_run(run):
    """Break one spoken run into pages of 1 to 3 words, on natural phrase edges, never leaving one word stranded."""
    n = len(run)
    INF = 1e9
    best = [INF] * (n + 1)
    prev = [0] * (n + 1)
    best[0] = 0.0
    for j in range(1, n + 1):
        for size in (1, 2, 3):
            i = j - size
            if i < 0 or best[i] >= INF:
                continue
            pg = run[i:j]
            if page_w(pg) > MAX_W:
                continue
            cost = {1: 2.5 if n > 1 else 0.0, 2: 0.38, 3: 0.0}[size]
            last = pg[-1][2]
            if j < n:
                if last[-1] in ',:;':
                    cost -= 0.7
                elif norm(last) in WEAK_END:
                    cost += 0.6
                if norm(run[j][2]) in STRONG_START:
                    cost -= 0.35
                if norm(run[j][2]) in PARTICLES:
                    cost += 0.9    # keep "laid off", "come back", "walk away" together
                if any(w[2][-1] in ',:;' for w in pg[:-1]):
                    cost += 0.45   # a comma stuck in the middle of a page
            if best[i] + cost < best[j]:
                best[j] = best[i] + cost
                prev[j] = i
    if best[n] >= INF:   # a single word wider than the limit; fall back to one word per page
        return [[w] for w in run]
    out, j = [], n
    while j > 0:
        out.append(run[prev[j]:j])
        j = prev[j]
    return out[::-1]


def pages(W):
    runs, cur = [], []
    for w in W:
        if cur and w[0] - cur[-1][1] > 0.55:
            runs.append(cur)
            cur = []
        cur.append(w)
        if ends_sentence(w[2]):
            runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    P = []
    for r in runs:
        P.extend(split_run(r))
    return P


def t2(x):
    x = max(0.0, x)
    h = int(x // 3600)
    m = int(x % 3600 // 60)
    return f'{h}:{m:02d}:{x % 60:05.2f}'


ORANGE, TEAL, WHITE = '&H2E6BF1&', '&HB2AD00&', '&HFFFFFF&'


def fmt(word, active, emph):
    word = word.replace('{', '').replace('}', '')
    if emph:
        return r'{\fnInstrument Serif\i1\fs' + str(FS_EMPH) + r'\c' + (ORANGE if active else TEAL) + '}' + word
    return r'{\fnAnton\i0\fs' + str(FS_CAP) + r'\c' + (ORANGE if active else WHITE) + '}' + word.upper()


def build(k):
    cfg = CLIPS[k]
    W = apply_edits(load_words(k), EDITS[k])
    cut = cfg['body'] - XFADE - 0.05
    W = [w for w in W if w[0] < cut]
    moved = snap_to_voice(W, f'{WM}/aud/{k}.wav')
    flags = mark_emph(W, EMPH[k])
    W = [[w[0], min(w[1], cut), w[2], f] for w, f in zip(W, flags)]
    W = [w for w in W if not any(a <= w[0] < b for a, b in cfg['mute'])]
    PG = pages(W)
    ev = []
    for pi, pg in enumerate(PG):
        pend = min(pg[-1][1] + 0.25, cut)
        if pi + 1 < len(PG):
            pend = min(pend, PG[pi + 1][0][0])
        for i, w in enumerate(pg):
            st = w[0]
            en = pg[i + 1][0] if i + 1 < len(pg) else pend
            if en - st < 0.03:
                continue
            txt = ' '.join(fmt(x[2], j == i, x[3]) for j, x in enumerate(pg))
            pop = r'{\fscx93\fscy93\t(0,90,\fscx100\fscy100)}' if i == 0 else ''
            ev.append(f'Dialogue: 0,{t2(st)},{t2(en)},Cap,,0,0,0,,{pop}{txt}')
    hdr = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Anton,{FS_CAP},&H00FFFFFF,&H00FFFFFF,&H00000000,&H78000000,0,0,0,0,100,100,1,0,1,7,4,2,40,40,{MARGIN_V},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    open(f'{WM}/ass/{k}.ass', 'w').write(hdr + '\n'.join(ev) + '\n')
    json.dump({'words': W, 'pages': [[w[2] for w in pg] for pg in PG]}, open(f'{WM}/ass/{k}.json', 'w'), indent=0)
    widest = max(PG, key=page_w)
    return dict(words=len(W), pages=len(PG), moved=moved, widest=(round(page_w(widest)), ' '.join(w[2] for w in widest)))


def hook_png(k):
    """White card, black Anton, 12px corners. Sits at the top, over his head, for the first 5 seconds.
    Same build as the Episode 1 reels: type as large as fits in 900px, card hugging the type."""
    lines = CLIPS[k]['hook']
    W_ = 1080
    fs = 112
    d0 = ImageDraw.Draw(Image.new('RGBA', (8, 8)))
    while True:
        f = ImageFont.truetype(ANTON, fs)
        widths = [d0.textlength(line, font=f) for line in lines]
        if max(widths) <= 900:
            break
        fs -= 2
    lh = int(fs * 1.12)
    bw = int(max(widths) + 90)
    bh = lh * len(lines) + 70
    H_ = bh + 60
    im = Image.new('RGBA', (W_, H_), (0, 0, 0, 0))
    x0 = (W_ - bw) // 2
    y0 = 14
    sh = Image.new('RGBA', (W_, H_), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([x0 + 4, y0 + 10, x0 + bw + 4, y0 + bh + 10], 12, fill=(0, 0, 0, 120))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], 12, fill=(255, 255, 255, 255))
    asc, desc = f.getmetrics()
    cap_top = f.getbbox('H')[1]
    cap_h = f.getbbox('H')[3] - cap_top
    block = (len(lines) - 1) * lh + cap_h
    ty = y0 + (bh - block) / 2 - cap_top
    for i, line in enumerate(lines):
        d.text(((W_ - widths[i]) / 2, ty + i * lh), line, font=f, fill=(17, 17, 17, 255))
    im.save(f'{WM}/ass/{k}_hook.png')
    return dict(font=fs, card=(bw, bh))


if __name__ == '__main__':
    import os
    os.makedirs(f'{WM}/ass', exist_ok=True)
    for k in sys.argv[1:]:
        print(k, build(k), hook_png(k))
