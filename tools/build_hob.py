#!/usr/bin/env python3
"""House of Brand renderer: white base, electric blue + orange, neon pop. 1080x1350.
Usage: OUT=<dir> python3 build_hob.py --brand brands/house-of-brand [post ids]
Templates: cover, text, photo, event, quote. Markup in copy: *orange*, _blue_, ~outline~, **bold**.
"""
import json, os, sys, pathlib, html, re, math, random
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).parent
FONTS = ROOT / 'assets' / 'fonts'

def _brand_dir():
    if '--brand' in sys.argv:
        i = sys.argv.index('--brand'); d = sys.argv[i+1]; del sys.argv[i:i+2]; return pathlib.Path(d).resolve()
    return (ROOT.parent / 'brands' / 'house-of-brand').resolve()

BDIR = _brand_dir()
B = json.load(open(BDIR / 'brand.json'))
OUT = pathlib.Path(os.environ.get('OUT', BDIR / 'out')).resolve()
PHOTOS = BDIR / B.get('photos', 'photos')
P = B['palette']  # white, blue, cyan, orange, ink, tint
P.setdefault('teal', P['blue'])
LOGO = BDIR / B['logo']['plus']
D = B.get('defaults', {})

def ff(name, file, w=400):
    return f"@font-face{{font-family:'{name}';src:url('file://{FONTS/file}') format('woff2');font-weight:{w};}}"
CSS_FONTS = "\n".join(ff(f['family'], f['file'], f.get('weight', 400)) for f in B['font_files'])

CSS = CSS_FONTS + f"""
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:1080px;height:1350px;overflow:hidden;background:{P['white']};color:{P['ink']};font-family:'Space Grotesk',sans-serif;-webkit-font-smoothing:antialiased}}
.s{{position:relative;width:1080px;height:1350px;overflow:hidden;background:{P['white']}}}
.h{{font-family:'Unbounded';font-weight:900;line-height:.98;letter-spacing:-.025em;text-transform:uppercase}}
.h .o{{color:{P['orange']}}}
.h .b{{color:{P['blue']}}}
.h .k{{color:transparent;-webkit-text-stroke:3px {P['blue']}}}
.h b{{font-weight:900}}
.body{{font-family:'Space Grotesk';font-weight:500;font-size:38px;line-height:1.3;color:{P['ink']}}}
.body b{{font-weight:700}}
.body .o{{color:{P['orange']};font-weight:700}}.body .b{{color:{P['blue']};font-weight:700}}
.kick{{font-family:'Space Grotesk';font-weight:700;font-size:22px;letter-spacing:.2em;text-transform:uppercase;color:{P['blue']}}}
.pill{{display:inline-block;font-family:'Space Grotesk';font-weight:700;font-size:24px;letter-spacing:.08em;text-transform:uppercase;padding:14px 26px;border-radius:999px}}
.pill.o{{background:{P['orange']};color:{P['white']};box-shadow:0 0 28px rgba(255,106,31,.55)}}
.pill.b{{background:{P['blue']};color:{P['white']};box-shadow:0 0 28px rgba(31,63,255,.45)}}
.pill.w{{background:{P['white']};color:{P['blue']};border:3px solid {P['blue']}}}
.blob{{position:absolute;border-radius:50%;filter:blur(70px);pointer-events:none}}
.pad{{position:absolute;left:72px;right:72px}}
.card{{position:absolute;border-radius:30px;overflow:hidden;border:8px solid {P['white']};box-shadow:0 0 0 6px {P['blue']},0 40px 80px rgba(21,19,26,.22)}}
.card .img{{position:absolute;inset:0;background-size:cover;background-position:center}}
.shadowblk{{position:absolute;border-radius:36px;background:{P['orange']};box-shadow:0 0 40px rgba(255,106,31,.5)}}
.brand{{position:absolute;left:64px;top:56px;display:flex;align-items:center;gap:16px}}
.brand .nm{{font-family:'Unbounded';font-weight:700;font-size:20px;letter-spacing:.12em;text-transform:uppercase;color:{P['ink']}}}
.chip{{position:absolute;right:64px;top:60px;font-family:'Space Grotesk';font-weight:700;font-size:20px;letter-spacing:.16em;text-transform:uppercase;color:{P['blue']};border:3px solid {P['blue']};border-radius:999px;padding:10px 20px}}
.url{{position:absolute;right:72px;bottom:72px;font-family:'Space Grotesk';font-weight:700;font-size:24px;color:{P['ink']};letter-spacing:.02em}}
.url span{{color:{P['orange']}}}
.inv .h,.inv .body,.inv .kick,.inv .brand .nm,.inv .url{{color:{P['white']}}}
.inv .h .k{{-webkit-text-stroke:3px {P['white']}}}
.inv .chip{{color:{P['white']};border-color:{P['white']}}}
"""

def esc(s): return html.escape(s, quote=False)
def rich(s):
    s = esc(s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'\*(.+?)\*', r'<span class="o">\1</span>', s)
    s = re.sub(r'_(.+?)_', r'<span class="b">\1</span>', s)
    s = re.sub(r'~(.+?)~', r'<span class="k">\1</span>', s)
    return s.replace('\n', '<br>')

def hsize(lines, base=150, width=936, cw=0.86, maxh=760):
    longest = max(len(l) for l in lines)
    return int(min(base, width / (cw * longest), maxh / (len(lines) * 0.98)))

def photo(name, pos='center'):
    return f"background-image:url('file://{PHOTOS/name}');background-position:{pos};"

# ---------- decorations ----------
def blobs(seed, strength=1.0):
    """Two glows in opposite corners (never overlapping, so no grey), corner pair rotates with the seed."""
    corners = [(-260, -260), (700, -260), (700, 900), (-260, 900)]
    i = seed % 4
    (bx, by), (ox, oy) = corners[i], corners[(i + 2) % 4]
    return (f'<div class="blob" style="left:{bx}px;top:{by}px;width:640px;height:640px;background:{P["cyan"]};opacity:{.55*strength:.2f}"></div>'
            f'<div class="blob" style="left:{ox}px;top:{oy}px;width:620px;height:620px;background:{P["orange"]};opacity:{.42*strength:.2f}"></div>')

def sparks(seed, n=5, area=None):
    """Small plus marks in the margins only (never over copy)."""
    r = random.Random(seed + 7); out = []
    for _ in range(n):
        side = r.choice('lrtb')
        if side == 'l': x, y = r.randint(14, 48), r.randint(200, 1150)
        elif side == 'r': x, y = r.randint(1010, 1050), r.randint(200, 1150)
        elif side == 't': x, y = r.randint(200, 900), r.randint(118, 150)
        else: x, y = r.randint(120, 960), r.randint(1180, 1215)
        sz = r.choice((18, 26, 34)); rot = r.randint(-25, 25); col = r.choice((P['orange'], P['blue'], P['cyan']))
        out.append(f'<svg style="position:absolute;left:{x}px;top:{y}px;transform:rotate({rot}deg)" width="{sz}" height="{sz}" viewBox="0 0 10 10"><path d="M5 0v10M0 5h10" stroke="{col}" stroke-width="2.6" stroke-linecap="round"/></svg>')
    return ''.join(out)

def rings(x, y, r_, col=None, w=10, op=.9):
    col = col or P['blue']
    return f'<div style="position:absolute;left:{x}px;top:{y}px;width:{r_*2}px;height:{r_*2}px;border-radius:50%;border:{w}px solid {col};opacity:{op};box-shadow:0 0 30px rgba(31,63,255,.35),inset 0 0 30px rgba(31,63,255,.25)"></div>'

SKY = "M0,160 L0,120 L40,120 L40,80 L70,80 L70,120 L110,120 L110,60 L130,60 L130,30 L150,30 L150,60 L170,60 L170,120 L210,120 L210,90 L250,90 L250,120 L290,120 L290,40 L300,20 L330,20 L340,40 L340,120 L380,120 L380,70 L420,70 L420,120 L450,120 L450,0 L470,0 L470,120 L500,120 L500,50 L540,50 L540,120 L570,120 L570,95 L610,95 L610,120 L640,120 L640,30 L660,10 L680,30 L680,120 L720,120 L720,80 L760,80 L760,120 L790,120 L790,55 L830,55 L830,120 L860,120 L860,100 L900,100 L900,120 L930,120 L930,40 L950,40 L950,120 L990,120 L990,85 L1030,85 L1030,120 L1080,120 L1080,160 Z"

def skyline(y=1150, h=200, inv=False):
    fill = f"url(#sg)"
    g = (f'<linearGradient id="sg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{P["blue"]}"/><stop offset="1" stop-color="{P["cyan"]}"/></linearGradient>')
    glow = f'<path d="{SKY}" fill="none" stroke="{P["cyan"]}" stroke-width="5" opacity=".9" style="filter:drop-shadow(0 0 14px {P["cyan"]})"/>'
    return f'<svg style="position:absolute;left:0;top:{y}px" width="1080" height="{h}" viewBox="0 0 1080 160" preserveAspectRatio="none"><defs>{g}</defs><path d="{SKY}" fill="{fill}" opacity="{.95 if inv else .9}"/>{glow}</svg>'

def plus_row(idx, total, cover=False, inv=False):
    if total <= 1: return ''
    gap = 44; w = total * gap; x0 = 540 - w / 2 + gap / 2
    out = []
    for i in range(1, total + 1):
        on = i == idx
        col = P['orange'] if on else (P['white'] if inv else P['blue'])
        s = 26 if on else 18; op = 1 if on else .35
        sh = f'filter:drop-shadow(0 0 10px {P["orange"]})' if on else ''
        out.append(f'<svg style="position:absolute;left:{x0 + (i-1)*gap - s/2:.0f}px;top:{1250 - s/2}px;{sh}" width="{s}" height="{s}" viewBox="0 0 10 10"><path d="M5 0v10M0 5h10" stroke="{col}" stroke-width="2.8" stroke-linecap="round" opacity="{op}"/></svg>')
    if cover:
        out.append(f'<div class="pill {"w" if not inv else "o"}" style="position:absolute;right:64px;bottom:60px;font-size:20px;padding:12px 22px">Swipe &nbsp;→</div>')
    return ''.join(out)

def brand(inv=False, chip=None):
    chip = chip if chip is not None else D.get('chip', '')
    return (f'<div class="brand"><img src="file://{LOGO}" style="width:62px;height:auto;display:block"><div class="nm">House of Brand</div></div>'
            + (f'<div class="chip">{esc(chip)}</div>' if chip else ''))

def card(name, x, y, w, h, rot=-3, pos='center', shadow=True):
    sb = f'<div class="shadowblk" style="left:{x+22}px;top:{y+26}px;width:{w}px;height:{h}px;transform:rotate({rot}deg)"></div>' if shadow else ''
    return sb + f'<div class="card" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;transform:rotate({rot}deg)"><div class="img" style="{photo(name,pos)}"></div></div>'

# ---------- templates ----------
def t_cover(d, idx, total):
    lines = d['lines']; size = hsize(lines, d.get('size', 150))
    seed = d.get('seed', idx)
    return f"""{blobs(seed)}{sparks(seed, 6, (0,560,1080,1200))}
    {rings(-150, 620, 240, w=12, op=.75)}
    {card(d['photo'], 300, 150, 710, 560, rot=d.get('rot', 4), pos=d.get('pos','center'))}
    {brand()}
    <div class="pad" style="top:{d.get('top', 790)}px">
      {f'<div class="kick" style="margin-bottom:22px">{esc(d["kicker"])}</div>' if d.get('kicker') else ''}
      <div class="h" style="font-size:{size}px">{'<br>'.join(rich(l) for l in lines)}</div>
      {f'<div class="body" style="margin-top:26px;font-size:34px">{rich(d["sub"])}</div>' if d.get('sub') else ''}
    </div>
    {plus_row(idx, total, cover=True)}"""

def t_text(d, idx, total):
    lines = d.get('lines', []); size = hsize(lines, d.get('size', 160)) if lines else 0
    inv = d.get('bg') == 'blue'
    seed = d.get('seed', idx * 3)
    bg = f'<div style="position:absolute;inset:0;background:{P["blue"]}"></div>' if inv else ''
    deco = (blobs(seed, .35) + sparks(seed, 7)) if not inv else (f'<div class="blob" style="left:520px;top:-200px;width:760px;height:760px;background:{P["cyan"]};opacity:.55"></div><div class="blob" style="left:-260px;top:820px;width:700px;height:700px;background:{P["white"]};opacity:.45"></div>' + sparks(seed, 7))
    return f"""{bg}{deco}
    <div class="{'inv' if inv else ''}" style="position:absolute;inset:0">
    {brand(inv)}
    <div class="pad" style="top:200px;bottom:200px;display:flex;flex-direction:column;justify-content:{d.get('justify','center')}">
      {f'<div class="kick" style="margin-bottom:30px">{esc(d["kicker"])}</div>' if d.get('kicker') else ''}
      {f'<div class="h" style="font-size:{size}px">{"<br>".join(rich(l) for l in lines)}</div>' if lines else ''}
      {f'<div class="body" style="margin-top:40px;font-size:{d.get("bodysize",38)}px">{rich(d["body"])}</div>' if d.get('body') else ''}
      {f'<div style="margin-top:44px"><span class="pill o">{esc(d["pill"])}</span></div>' if d.get('pill') else ''}
    </div>
    {plus_row(idx, total, inv=inv)}</div>"""

def t_photo(d, idx, total):
    lines = d.get('lines', []); size = hsize(lines, d.get('size', 130), maxh=420) if lines else 0
    seed = d.get('seed', idx * 5)
    return f"""{blobs(seed, .5)}{sparks(seed, 5, (0,700,1080,1250))}
    {rings(820, 80, 170, col=P['orange'], w=10, op=.85)}
    {card(d['photo'], 72, 170, 936, 600, rot=d.get('rot', -2), pos=d.get('pos','center'))}
    {brand()}
    <div class="pad" style="top:{d.get('top', 830)}px">
      {f'<div class="kick" style="margin-bottom:20px">{esc(d["kicker"])}</div>' if d.get('kicker') else ''}
      {f'<div class="h" style="font-size:{size}px">{"<br>".join(rich(l) for l in lines)}</div>' if lines else ''}
      {f'<div class="body" style="margin-top:24px;font-size:{d.get("bodysize",34)}px">{rich(d["body"])}</div>' if d.get('body') else ''}
    </div>
    {plus_row(idx, total)}"""

def t_event(d, idx=1, total=1):
    lines = d.get('lines', ['Connect &', '~Cultivate~']); size = hsize(lines, d.get('size', 150), maxh=360)
    chips = d.get('chips', ['Sat Nov 7', '4 PM', 'Buckhead', '$35'])
    chip_html = ''.join(f'<span class="pill {c}" style="margin-right:14px;margin-bottom:14px">{esc(t)}</span>' for t, c in zip(chips, ['o', 'b', 'w', 'o']))
    seed = d.get('seed', 11)
    return f"""{blobs(seed, .6)}{sparks(seed, 6)}
    {skyline(1070, 230)}
    {brand(chip='In person · Atlanta')}
    <div class="pad" style="top:{d.get('top', 180)}px">
      {f'<div class="kick" style="margin-bottom:22px">{esc(d["kicker"])}</div>' if d.get('kicker') else ''}
      <div class="h" style="font-size:{size}px">{'<br>'.join(rich(l) for l in lines)}</div>
      <div style="margin-top:30px;display:flex;flex-wrap:wrap">{chip_html}</div>
      {f'<div class="body" style="margin-top:18px;font-size:30px;max-width:520px">{rich(d["body"])}</div>' if d.get('body') else ''}
    </div>
    {card(d['photo'], 590, 660, 430, 380, rot=d.get('rot', 5), pos=d.get('pos','center'))}
    <div style="position:absolute;left:72px;bottom:64px;font-family:'Space Grotesk';font-weight:700;font-size:24px;color:{P['white']};letter-spacing:.02em;text-shadow:0 2px 8px rgba(0,0,0,.35)">{esc(d.get('url', D.get('url','')))}<div style="font-weight:500;font-size:18px;letter-spacing:.12em;text-transform:uppercase;opacity:.9;margin-top:6px">{esc(d.get('foot',''))}</div></div>"""

def t_quote(d, idx=1, total=1):
    lines = d['lines']; size = hsize(lines, d.get('size', 100), maxh=520)
    seed = d.get('seed', 21)
    who = d.get('who', D.get('who', 'House of Brand')); role = d.get('role', D.get('role', ''))
    return f"""{blobs(seed, .55)}{sparks(seed, 5, (0,0,1080,560))}
    {rings(860, 560, 150, col=P['orange'], w=10, op=.8)}
    {brand()}
    {card(d['photo'], 72, 150, 936, 520, rot=d.get('rot', -2), pos=d.get('pos','center'))}
    <div class="pad" style="top:740px">
      <div style="font-family:'Unbounded';font-weight:900;font-size:150px;line-height:.5;color:{P['orange']};text-shadow:0 0 22px rgba(255,106,31,.6);margin-bottom:6px">“</div>
      <div class="h" style="font-size:{size}px;text-transform:none;letter-spacing:-.02em">{'<br>'.join(rich(l) for l in lines)}</div>
      <div style="margin-top:30px;display:flex;align-items:center;gap:16px"><div style="width:52px;height:6px;background:{P['blue']};border-radius:3px"></div>
        <div><div style="font-family:'Unbounded';font-weight:700;font-size:22px;letter-spacing:.1em;text-transform:uppercase">{esc(who)}</div>
        <div style="font-size:20px;color:{P['blue']};font-weight:700;margin-top:4px">{esc(role)}</div></div></div>
    </div>"""

T = dict(cover=t_cover, text=t_text, photo=t_photo, event=t_event, quote=t_quote)

# ---------- single-post templates (no pills, no swipe, no progress row) ----------
def footer_line(d, inv=False):
    txt = d.get('foot', D.get('foot', 'Sat Nov 7  ·  4pm  ·  Buckhead  ·  $35'))
    url = d.get('url', D.get('url', 'houseofbrand.net'))
    col = P['white'] if inv else P['ink']
    return f"""<div style="position:absolute;left:72px;right:72px;bottom:64px;display:flex;justify-content:space-between;align-items:flex-end;font-family:'Space Grotesk';font-weight:700;font-size:21px;letter-spacing:.04em;color:{col}">
      <div>{esc(txt)}</div><div style="color:{P['orange']}">{esc(url)}</div></div>"""

def brand_plain(inv=False):
    col = P['white'] if inv else P['ink']
    return f'<div class="brand"><img src="file://{LOGO}" style="width:58px;height:auto;display:block"><div class="nm" style="color:{col}">House of Brand</div></div>'

def t_reason(d, idx=1, total=1):
    """Numbered reason poster. Header: Connect & Cultivate | Nov. 7th, Atlanta clear. Photo band with a diagonal cut, giant number, one line."""
    n = d['n']; lines = d['lines']; size = hsize(lines, d.get('size', 92), maxh=300, cw=.78)
    top = 262; ph = d.get('ph', 550)
    return f"""
    {brand_plain()}
    <div style="position:absolute;left:64px;top:118px;white-space:nowrap;font-family:'Unbounded';font-weight:900;font-size:43px;line-height:1;letter-spacing:-.02em;color:{P['ink']};text-transform:uppercase">Connect &amp; Cultivate <span style="color:{P['blue']}">|</span> Nov. 7th</div>
    <div style="position:absolute;left:64px;top:176px;font-family:'Unbounded';font-weight:700;font-size:34px;letter-spacing:.06em;text-transform:uppercase;color:{P['orange']}">Atlanta, GA</div>
    <div style="position:absolute;left:0;top:{top}px;width:1080px;height:{ph}px;{photo(d['photo'], d.get('pos','center'))}background-size:cover;clip-path:polygon(0 0,100% 0,100% {ph-100}px,0 100%)"></div>
    <svg style="position:absolute;left:0;top:{top}px" width="1080" height="{ph+10}"><line x1="0" y1="{ph}" x2="1080" y2="{ph-100}" stroke="{P['orange']}" stroke-width="7" style="filter:drop-shadow(0 0 12px {P['orange']})"/></svg>
    <div class="blob" style="left:640px;top:{top+ph-140}px;width:600px;height:600px;background:{P['cyan']};opacity:.36"></div>
    <div style="position:absolute;left:64px;top:{top+ph-170}px;font-family:'Unbounded';font-weight:900;font-size:270px;line-height:.8;color:{P['orange']};text-shadow:0 0 30px rgba(255,106,31,.5);letter-spacing:-.06em">{n:02d}</div>
    <div class="pad" style="top:{top+ph+70}px">
      <div class="kick" style="margin-bottom:16px">Reason No. {n} to be in this room</div>
      <div class="h" style="font-size:{size}px;text-transform:none;letter-spacing:-.02em">{'<br>'.join(rich(l) for l in lines)}</div>
    </div>
    {footer_line(d)}"""

def t_tribe(d, idx=1, total=1):
    """Framed photo with a statement underneath and a plain join line. Lots of air."""
    lines = d['lines']; size = hsize(lines, d.get('size', 104), maxh=300)
    return f"""{blobs(d.get('seed', 3), .4)}
    {brand_plain()}
    <div style="position:absolute;left:72px;top:150px;width:936px;height:{d.get('ph',560)}px;border-radius:6px;overflow:hidden;box-shadow:0 30px 70px rgba(21,19,26,.22)"><div style="position:absolute;inset:0;{photo(d['photo'], d.get('pos','center'))}background-size:cover"></div>
      <div style="position:absolute;left:0;right:0;bottom:0;height:8px;background:linear-gradient(90deg,{P['blue']},{P['cyan']},{P['orange']})"></div></div>
    <div class="pad" style="top:{d.get('top', 790)}px">
      {f'<div class="kick" style="margin-bottom:18px">{esc(d["kicker"])}</div>' if d.get('kicker') else ''}
      <div class="h" style="font-size:{size}px">{'<br>'.join(rich(l) for l in lines)}</div>
      {f'<div class="body" style="margin-top:22px;font-size:32px">{rich(d["body"])}</div>' if d.get('body') else ''}
      <div class="body" style="margin-top:{'26' if d.get('body') else '38'}px;font-weight:700;font-size:34px">{rich(d.get('join', 'Join us Nov. 7th. *Link in bio.*'))}</div>
    </div>
    {footer_line(d)}"""

def t_countdown(d, idx=1, total=1):
    """Evening event post: giant day count, typeset details, skyline, photo strip."""
    days = d['days']
    return f"""{blobs(d.get('seed', 5), .5)}
    {skyline(1040, 240)}
    {brand_plain()}
    <div style="position:absolute;left:64px;top:150px;display:flex;align-items:flex-end;gap:26px">
      <div style="font-family:'Unbounded';font-weight:900;font-size:360px;line-height:.78;color:{P['blue']};text-shadow:0 0 34px rgba(31,63,255,.45);letter-spacing:-.06em">{days}</div>
      <div style="font-family:'Unbounded';font-weight:900;font-size:64px;line-height:.9;color:{P['ink']};padding-bottom:14px;text-transform:uppercase">days<br><span style="color:{P['orange']}">out.</span></div>
    </div>
    <div class="pad" style="top:{d.get('top', 490)}px">
      <div class="h" style="font-size:112px">Connect &amp;<br><span class="k">Cultivate</span></div>
      <div style="margin-top:30px;font-family:'Space Grotesk';font-weight:700;font-size:34px;line-height:1.35;color:{P['ink']}">Saturday, November 7 · 4pm<br>Buckhead, Atlanta · <span style="color:{P['orange']}">$35</span></div>
      <div class="body" style="margin-top:16px;font-size:28px;max-width:600px">{rich(d.get('body','60 seats. None at the door. House of Brand, in person.'))}</div>
    </div>
    <div style="position:absolute;right:64px;top:{d.get('ptop', 780)}px;width:300px;height:330px;border-radius:6px;overflow:hidden;box-shadow:0 30px 70px rgba(21,19,26,.25);transform:rotate({d.get('rot',3)}deg)"><div style="position:absolute;inset:0;{photo(d['photo'], d.get('pos','center'))}background-size:cover"></div></div>
    <div style="position:absolute;left:72px;bottom:64px;font-family:'Space Grotesk';font-weight:700;font-size:24px;color:{P['white']};text-shadow:0 2px 10px rgba(0,0,0,.4)">{esc(d.get('url', D.get('url','')))}</div>"""

T.update(reason=t_reason, tribe=t_tribe, countdown=t_countdown)

def t_say(d, idx=1, total=1):
    """Testimony card: real meetup photo, a Brand Mate's words, their first name, the join line."""
    lines = d['lines']; size = hsize(lines, d.get('size', 84), maxh=330, cw=.78)
    return f"""{blobs(d.get('seed', 9), .4)}
    {brand_plain()}
    <div style="position:absolute;left:72px;top:150px;width:936px;height:{d.get('ph',470)}px;border-radius:6px;overflow:hidden;box-shadow:0 30px 70px rgba(21,19,26,.22)"><div style="position:absolute;inset:0;{photo(d['photo'], d.get('pos','center'))}background-size:cover"></div>
      <div style="position:absolute;left:0;right:0;bottom:0;height:8px;background:linear-gradient(90deg,{P['blue']},{P['cyan']},{P['orange']})"></div></div>
    <div class="pad" style="top:{d.get('top', 680)}px">
      <div style="font-family:'Unbounded';font-weight:900;font-size:120px;line-height:.5;color:{P['orange']};text-shadow:0 0 22px rgba(255,106,31,.55);margin-bottom:14px">\u201c</div>
      <div class="h" style="font-size:{size}px;text-transform:none;letter-spacing:-.02em">{'<br>'.join(rich(l) for l in lines)}</div>
      <div style="margin-top:26px;display:flex;align-items:center;gap:16px"><div style="width:48px;height:6px;background:{P['blue']};border-radius:3px"></div>
        <div style="font-family:'Space Grotesk';font-weight:700;font-size:28px;color:{P['ink']}">{esc(d.get('who',''))} <span style="color:{P['blue']};font-weight:500">{esc(d.get('role','Brand Mate'))}</span></div></div>
      <div class="body" style="margin-top:28px;font-weight:700;font-size:32px">{rich(d.get('join', 'Join us Nov. 7th. *Link in bio.*'))}</div>
    </div>
    {footer_line(d)}"""

T.update(say=t_say)

# ---------- unified flyer (Rod, Oct 22): title line, subheader, photo, phrase, CTA ----------
FACES = json.load(open(BDIR / 'faces.json')) if (BDIR / 'faces.json').exists() else {}
from PIL import Image as _PI
_DIM = {}
def face_pos(name, override=None, box=(952, 560)):
    """Background-position (px) so the mean face center sits at the middle of a cover-fit box."""
    if override: return override
    f = FACES.get(name)
    if name not in _DIM: _DIM[name] = _PI.open(PHOTOS / name).size
    iw, ih = _DIM[name]; bw, bh = box
    sc = max(bw / iw, bh / ih); sw, sh = iw * sc, ih * sc
    fx = (f['cx'] / 100 if f and f.get('n') else .5); fy = (f['cy'] / 100 if f and f.get('n') else .42)
    # heads sit above face centers; aim the face a bit above box center
    ox = min(max(fx * sw - bw / 2, 0), sw - bw); oy = min(max(fy * sh - bh * .46, 0), sh - bh)
    return f"-{ox:.0f}px -{oy:.0f}px"

def _gx(day):
    return 140 + (day * 397) % 800

def grid_plus(day):
    """Plus marks that hand off vertically: the one half-off the bottom edge of day d lines up with the one half-off the top edge of day d-1 (the tile below it on the grid)."""
    r = random.Random(day * 11)
    marks = [(_gx(day), 1350, 30, P['orange'] if day % 2 == 0 else P['teal']),      # bottom edge
             (_gx(day + 1), 0, 30, P['orange'] if (day + 1) % 2 == 0 else P['teal']),  # top edge (matches tile above's bottom)
             (r.choice((28, 1052)), r.randint(300, 1100), 18, P['teal']),
             (r.randint(640, 1000), r.randint(228, 246), 14, P['orange'])]
    out = []
    for x, y, sz, col in marks:
        out.append(f'<svg style="position:absolute;left:{x-sz/2:.0f}px;top:{y-sz/2:.0f}px;transform:rotate({r.randint(-15,15)}deg)" width="{sz}" height="{sz}" viewBox="0 0 10 10"><path d="M5 0v10M0 5h10" stroke="{col}" stroke-width="2.4" stroke-linecap="round" opacity=".95"/></svg>')
    return ''.join(out)

def _rgba(h, a):
    h = h.lstrip('#'); return f"rgba({int(h[:2],16)},{int(h[2:4],16)},{int(h[4:],16)},{a})"

def soft_bg(day):
    """Vertical wash that flows down the column: even days teal at top fading to orange at bottom, odd days the reverse, so the bottom of one tile matches the top of the tile below it."""
    top, bot = (P['teal'], P['orange']) if day % 2 == 0 else (P['orange'], P['teal'])
    return f'<div style="position:absolute;inset:0;background:linear-gradient(180deg,{_rgba(top,.26)} 0%,{_rgba(top,.06)} 34%,rgba(255,255,255,0) 50%,{_rgba(bot,.06)} 66%,{_rgba(bot,.26)} 100%)"></div>'

def t_flyer(d, idx=1, total=1):
    lines = d['lines']; is_say = bool(d.get('who')); has_body = bool(d.get('body'))
    ph = 520 if (is_say or has_body) else 560
    size = hsize(lines, d.get('size', 78 if is_say else 92), maxh=250 if (is_say or has_body) else 290, cw=.78 if is_say else .86)
    title = B.get('title', 'Connect & Cultivate'); sub = d.get('sub', B.get('subheader', ''))
    cta = d.get('cta', B.get('cta', 'Sign up today. *Only 60 seats.* Link in bio.'))
    quote = f"""<span style="font-family:'Unbounded';font-weight:900;color:{P['orange']};margin-right:6px">\u201c</span>""" if is_say else ''
    day = d.get('day', idx)
    return f"""{soft_bg(day)}{grid_plus(day)}
    <div class="brand" style="top:52px"><img src="file://{LOGO}" style="width:44px;height:auto;display:block"><div style="font-family:'Space Grotesk';font-weight:500;font-size:22px;color:{P['ink']};opacity:.85">House of Brand, in person</div></div>
    <div style="position:absolute;left:64px;right:64px;top:108px;font-family:'Archivo Black';font-size:{B.get('title_size',80)}px;line-height:1;letter-spacing:-.02em;color:{P['ink']};text-transform:uppercase;white-space:nowrap">{title.replace('&','<span style="color:'+P['orange']+'">&amp;</span>')}</div>
    <div style="position:absolute;left:66px;top:{108+B.get('title_size',80)+14}px;font-family:'Space Grotesk';font-weight:700;font-size:25px;letter-spacing:.12em;text-transform:uppercase;color:{P['teal']}">{esc(sub)}</div>
    <div style="position:absolute;left:64px;right:64px;top:{d.get('ptop',262)}px;height:{ph}px;border-radius:14px;overflow:hidden;box-shadow:0 24px 60px rgba(42,31,26,.22)"><div style="position:absolute;inset:0;{photo(d['photo'], face_pos(d['photo'], d.get('pos'), (952, ph)))}background-size:cover"></div>
      <div style="position:absolute;left:0;right:0;bottom:0;height:9px;background:linear-gradient(90deg,{P['teal']},{P['orange']})"></div></div>
    <div class="pad" style="top:{d.get('ptop',262)+ph+46}px;left:64px;right:64px">
      {f'<div class="kick" style="margin-bottom:12px;color:{P["orange"]}">{esc(d["kicker"])}</div>' if d.get('kicker') else ''}
      <div class="h" style="font-size:{size}px;{'text-transform:none;letter-spacing:-.02em;' if is_say else ''}">{quote}{'<br>'.join(rich(l) for l in lines)}</div>
      {f'<div style="margin-top:14px;font-family:Space Grotesk;font-weight:700;font-size:24px;color:{P["ink"]}">{esc(d["who"])} <span style="color:{P["teal"]};font-weight:500">{esc(d.get("role","Brand Mate"))}</span></div>' if is_say else ''}
      {f'<div class="body" style="margin-top:14px;font-size:27px;line-height:1.3">{rich(d["body"])}</div>' if has_body else ''}
      <div class="body" style="margin-top:{'18' if (is_say or has_body) else '26'}px;font-weight:700;font-size:30px">{rich(cta)}</div>
    </div>
    {footer_line(d)}"""

T.update(flyer=t_flyer)

def render(d, idx, total):
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body><div class='s'>{T[d['t']](d, idx, total)}</div></body></html>"

def build(ids=None):
    content = json.load(open(BDIR / 'content.json'))
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 1350})
        for post in content['posts']:
            if ids and post['id'] not in ids: continue
            n = len(post['slides'])
            for i, s in enumerate(post['slides'], 1):
                f = OUT / f"{post['id']}-{i:02d}.html"; f.write_text(render(s, i, n))
                pg.goto(f.as_uri()); pg.wait_for_timeout(300); pg.screenshot(path=str(OUT / f"{post['id']}-{i:02d}.png"))
            print('built', post['id'], n)
        b.close()

if __name__ == '__main__':
    build(sys.argv[1:] or None)
