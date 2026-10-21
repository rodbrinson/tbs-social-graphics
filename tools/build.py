#!/usr/bin/env python3
"""Render social graphics (1080x1350) from content.json with Playwright.

Brand-aware: set BRAND=<dir> (or pass --brand <dir>) pointing at a folder with brand.json,
logo files and a photos/ folder. Defaults to Rod's brand (../brands/rod-brinson).
"""
import json, os, sys, base64, pathlib, html
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).parent
FONTS = ROOT / 'assets' / 'fonts'

def _brand_dir():
    if '--brand' in sys.argv:
        i = sys.argv.index('--brand'); d = sys.argv[i+1]; del sys.argv[i:i+2]; return pathlib.Path(d).resolve()
    return pathlib.Path(os.environ.get('BRAND', ROOT.parent / 'brands' / 'rod-brinson')).resolve()

BRAND_DIR = _brand_dir()
BRAND = json.load(open(BRAND_DIR / 'brand.json'))
OUT = pathlib.Path(os.environ.get('OUT', BRAND_DIR / 'out'))
PHOTOS = pathlib.Path(BRAND.get('photos', BRAND_DIR / 'photos'))
if not PHOTOS.is_absolute(): PHOTOS = BRAND_DIR / PHOTOS

# Palette roles: dark (main bg), light (alt bg + text on dark), accent (flow line, teal words), cta (orange words/badges), white, ink
_p = BRAND['palette']
PAL = dict(charcoal=_p['dark'], teal=_p['accent'], orange=_p['cta'], cream=_p['light'], white=_p.get('white', '#ffffff'), ink=_p.get('ink', _p['dark']))
def _rgb(h): h=h.lstrip('#'); return ','.join(str(int(h[i:i+2],16)) for i in (0,2,4))
# Light-theme support: text over photos, gradient colour over photos, and the colour a split photo fades into
PAL['ptext'] = _p.get('photo_text', PAL['cream'])
GRAD = _rgb(_p.get('photo_grad', '#161314'))
SPLIT = _rgb(_p['dark'])
FLOW = BRAND.get('flow', 'wave')
THEME_LIGHT = BRAND.get('theme') == 'light'
PAL['meta'] = _p.get('meta', PAL['teal'])
PAL['strong'] = PAL['ink'] if THEME_LIGHT else PAL['white']

# Fonts: roles display (condensed caps stack), serif (editorial), body (everything else)
_f = BRAND['fonts']
F_DISPLAY, F_SERIF, F_BODY = _f['display']['family'], _f['serif']['family'], _f['body']['family']
F_UTIL = _f.get('utility', {}).get('family', _f['body']['family'])
SERIF_W = _f['serif'].get('weight', 400)
SERIF_STYLE = _f['serif'].get('style', 'normal')
DISPLAY_UPPER = 'uppercase' if _f['display'].get('uppercase', True) else 'none'
DISPLAY_LH = _f['display'].get('line_height', .92)
DISPLAY_CHAR = _f['display'].get('char_width', .52)  # avg em width per char, for auto-sizing

def font_face(name, file, weight=400, style='normal'):
    return f"@font-face{{font-family:'{name}';src:url('file://{FONTS/file}') format('woff2');font-weight:{weight};font-style:{style};}}"

CSS_FONTS = "\n".join(font_face(ff['family'], ff['file'], ff.get('weight', 400), ff.get('style', 'normal')) for ff in BRAND['font_files'])

DEFAULTS = BRAND.get('defaults', {})
LOGO_DARK = BRAND_DIR / BRAND['logo']['on_dark']
LOGO_LIGHT = BRAND_DIR / BRAND['logo']['on_light']
LOGO_W = BRAND['logo'].get('width', 118)

BASE_CSS = CSS_FONTS + """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:1350px;overflow:hidden;background:%(charcoal)s;color:%(cream)s;font-family:'%(fbody)s',sans-serif;-webkit-font-smoothing:antialiased}
.slide{position:relative;width:1080px;height:1350px;overflow:hidden}
.photo{position:absolute;inset:0;background-size:cover;background-repeat:no-repeat}
.grad{position:absolute;inset:0}
.anton{font-family:'%(fdisplay)s',sans-serif;text-transform:%(dupper)s;line-height:%(dlh)s;letter-spacing:.005em}
.serif{font-family:'%(fserif)s',serif;font-weight:%(serifw)s;font-style:%(serifs)s;line-height:.95;letter-spacing:-.02em}
.serif i,.serif em{font-style:italic}
.meta{font-family:'%(futil)s';font-weight:700;font-size:22px;letter-spacing:.22em;text-transform:uppercase}
.p{color:%(ptext)s}
.meta.light{font-weight:500;letter-spacing:.14em;text-transform:none;font-size:24px}
.pad{position:absolute;left:72px;right:72px}
.o{color:%(orange)s}.t{color:%(teal)s}.c{color:%(cream)s}.w{color:%(white)s}
.body{font-family:'%(fbody)s';font-weight:500;font-size:40px;line-height:1.3;color:%(cream)s}
.body em{font-style:italic;font-weight:600;color:%(strong)s}
.body b{font-weight:800;color:%(strong)s}
.meta.t{color:%(meta)s}
.rule{height:6px;width:120px;background:%(teal)s}
.mark{position:absolute;left:72px;bottom:100px;display:flex;align-items:center;gap:18px}
.mark .rb{font-family:'%(fdisplay)s';font-size:34px;color:%(charcoal)s;background:%(cream)s;padding:6px 12px 2px;line-height:1}
.mark .nm{font-family:'%(fbody)s';font-weight:700;font-size:20px;letter-spacing:.2em;text-transform:uppercase;color:%(cream)s;opacity:.85}
.pg{position:absolute;right:72px;bottom:66px;font-family:'%(fbody)s';font-weight:600;font-size:24px;letter-spacing:.1em;color:%(cream)s;opacity:.7}
.corner{position:absolute;top:60px;font-family:'%(fbody)s';font-weight:600;font-size:22px;letter-spacing:.06em}
.corner.l{left:72px}.corner.r{right:72px}
.swipe{position:absolute;right:72px;bottom:64px;display:flex;align-items:center;gap:14px;font-family:'%(fbody)s';font-weight:700;font-size:22px;letter-spacing:.22em;text-transform:uppercase}
.swipe .arr{width:54px;height:54px;border:3px solid currentColor;border-radius:50%%;display:flex;align-items:center;justify-content:center;font-size:28px}
""" % dict(PAL, fbody=F_BODY, fdisplay=F_DISPLAY, fserif=F_SERIF, futil=F_UTIL, dupper=DISPLAY_UPPER, dlh=DISPLAY_LH, serifw=SERIF_W, serifs=SERIF_STYLE)

def esc(s):
    return html.escape(s, quote=False)

def rich(s):
    """Allow a tiny markup: *orange*, _teal_, **bold** inside body text; newlines to <br>."""
    import re
    s = esc(s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'\*(.+?)\*', r'<span class="o">\1</span>', s)
    s = re.sub(r'_(.+?)_', r'<span class="t">\1</span>', s)
    s = re.sub(r'~(.+?)~', r'<em>\1</em>', s)
    return s.replace('\n', '<br>')

def anton_size(lines, base=150):
    longest = max(len(l) for l in lines)
    # Anton is narrow; ~ 0.5em per char. Fit within 936px.
    size = min(base, int(936 / (DISPLAY_CHAR * longest)))
    # also cap by height: lines * size * .92 <= ~ 900
    size = min(size, int(920 / (len(lines) * 0.95)))
    return size

def photo_css(name, pos='center'):
    return f"background-image:url('file://{PHOTOS/name}');background-position:{pos};"

# ---------- templates ----------

def t_quote(d):
    lines = d['lines']
    size = anton_size(lines, d.get('size', 160))
    variant = d.get('variant', 'photo')
    attribution = d.get('attribution', DEFAULTS.get('name', ''))
    handle = d.get('handle', DEFAULTS.get('handle', ''))
    if variant == 'photo':
        body = f"""
        <div class="photo" style="{photo_css(d['photo'], d.get('pos','center'))}"></div>
        <div class="grad" style="background:linear-gradient(180deg,rgba({GRAD},.05) 0%,rgba({GRAD},.15) 35%,rgba({GRAD},.88) 68%,rgba({GRAD},.97) 100%)"></div>
        <div class="pad" style="bottom:250px">
          <div class="anton p" style="font-size:{size}px">{'<br>'.join(rich(l) for l in lines)}</div>
        </div>
        {mark_html(light=False)}{flow_html(1,1)}"""
    else:  # split: photo top, text bottom on charcoal
        body = f"""
        <div class="photo" style="{photo_css(d['photo'], d.get('pos','center'))};height:700px"></div>
        <div class="grad" style="height:700px;background:linear-gradient(180deg,rgba({SPLIT},0) 60%,rgba({SPLIT},1) 100%)"></div>
        <div class="pad" style="top:640px">
          <div class="rule" style="margin-bottom:34px"></div>
          <div class="anton c" style="font-size:{min(size,132,int(470/(len(lines)*0.95)))}px">{'<br>'.join(rich(l) for l in lines)}</div>
        </div>
        {mark_html()}{flow_html(1,1)}"""
    return body

def flow_html(idx, total, cover=False, light=False):
    """A continuous wave (or a dashed lane) along the bottom whose phase carries from slide to slide, with a marker that advances."""
    import math
    if FLOW == 'lane':
        return lane_html(idx, total, cover, light)
    W=1080; H=150; base=1350-70; amp=16; wl=720
    x0=(idx-1)*W
    pts=[]
    for x in range(0, W+1, 12):
        y=base+amp*math.sin(2*math.pi*((x+x0)/wl))
        pts.append(f"{x},{y:.1f}")
    path="M"+" L".join(pts)
    mx=int(W*(idx-0.5)/total); my=base+amp*math.sin(2*math.pi*((mx+x0)/wl))
    marker=f'<circle cx="{mx}" cy="{my:.1f}" r="11" fill="{PAL["orange"]}"/>'
    swipe=''
    if cover:
        swipe=f'<text x="{W-72}" y="{base-34}" text-anchor="end" font-family="{F_BODY}" font-weight="700" font-size="20" letter-spacing="5" fill="{PAL["cream"]}">SWIPE</text><path d="M{W-200},{base+amp*math.sin(2*math.pi*((W-200+x0)/wl)):.1f} L{W-72},{base+amp*math.sin(2*math.pi*((W-72+x0)/wl)):.1f}" stroke="{PAL["orange"]}" stroke-width="5" stroke-linecap="round"/><path d="M{W-96},{base+amp*math.sin(2*math.pi*((W-72+x0)/wl))-18:.1f} L{W-72},{base+amp*math.sin(2*math.pi*((W-72+x0)/wl)):.1f} L{W-96},{base+amp*math.sin(2*math.pi*((W-72+x0)/wl))+18:.1f}" stroke="{PAL["orange"]}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
    return f'<svg style="position:absolute;left:0;top:0" width="1080" height="1350" viewBox="0 0 1080 1350"><path d="{path}" stroke="{PAL["teal"]}" stroke-width="4" fill="none" opacity=".9"/>{marker}{swipe}</svg>'

def lane_html(idx, total, cover=False, light=False):
    """Dawn-style dashed lane marking: a road line across the bottom, dash phase carried across slides, marker advancing."""
    W=1080; y=1350-82; dash=64; gap=40; period=dash+gap
    x0=((idx-1)*W) % period
    segs=[]; x=-x0
    while x < W:
        segs.append(f"M{max(x,0)},{y} L{min(x+dash,W)},{y}" if x+dash>0 else "")
        x+=period
    col = PAL['teal']
    mx=int(W*(idx-0.5)/total)
    marker=f'<circle cx="{mx}" cy="{y}" r="12" fill="{PAL["orange"]}"/>'
    swipe=''
    if cover:
        tc = PAL['cream'] if light else PAL['ptext']
        swipe=f'<text x="{W-72}" y="{y-30}" text-anchor="end" font-family="{F_UTIL}" font-weight="700" font-size="22" letter-spacing="5" fill="{tc}">SWIPE</text><path d="M{W-200},{y} L{W-72},{y}" stroke="{PAL["orange"]}" stroke-width="6" stroke-linecap="round"/><path d="M{W-96},{y-18} L{W-72},{y} L{W-96},{y+18}" stroke="{PAL["orange"]}" stroke-width="6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
    return f'<svg style="position:absolute;left:0;top:0" width="1080" height="1350" viewBox="0 0 1080 1350"><path d="{" ".join(segs)}" stroke="{col}" stroke-width="7" fill="none" stroke-linecap="round" opacity=".95"/>{marker}{swipe}</svg>'

def mark_html(label='The Brand Strategist', light=None):
    if light is None: light = THEME_LIGHT
    src = LOGO_LIGHT if light else LOGO_DARK
    return f'<div class="mark"><img src="file://{src}" style="width:{LOGO_W}px;height:auto;display:block"></div>'

def t_bold(d, idx, total):
    """Ty-style: charcoal, cream Anton stack, Montserrat body."""
    lines = d.get('lines', [])
    body = d.get('body', '')
    kicker = d.get('kicker', '')
    size = anton_size(lines, d.get('size', 176)) if lines else 0
    top = 140
    parts = []
    if kicker:
        parts.append(f'<div class="meta t" style="margin-bottom:34px">{esc(kicker)}</div>')
    if lines:
        parts.append(f'<div class="anton c" style="font-size:{size}px">{"<br>".join(rich(l) for l in lines)}</div>')
    if body:
        parts.append(f'<div class="body" style="margin-top:{44 if lines else 0}px;font-size:{d.get("bodysize",40)}px">{rich(body)}</div>')
    if d.get('tail'):
        parts.append(f'<div class="anton c" style="font-size:{d.get("tailsize",110)}px;margin-top:48px">{rich(d["tail"])}</div>')
    if d.get('tail2'):
        parts.append(f'<div class="body" style="margin-top:26px;font-size:36px"><em>{rich(d["tail2"])}</em></div>')
    # pattern-break: bg = palette role name (accent | cta | ink | light); text flips to fg (default white)
    bgrole = d.get('bg'); fg = d.get('fg', PAL['white'])
    bgmap = dict(accent=PAL['teal'], cta=PAL['orange'], ink=PAL['ink'], light=PAL['cream'], dark=PAL['charcoal'])
    wrap_open = f'<div class="grad" style="background:{bgmap.get(bgrole, bgrole)}"></div><div style="position:absolute;inset:0;color:{fg}" class="pb">' if bgrole else ''
    wrap_close = '</div>' if bgrole else ''
    style = f'<style>.pb .anton,.pb .body,.pb .meta,.pb .body b,.pb .body em{{color:{fg}}}</style>' if bgrole else ''
    logo_light = (not THEME_LIGHT) if bgrole and bgrole != 'light' else None
    return f"""
    {style}{wrap_open}
    <div class="pad" style="top:{top}px;bottom:240px;display:flex;flex-direction:column;justify-content:{d.get('justify','center')}">{''.join(parts)}</div>
    {wrap_close}{mark_html(light=logo_light)}{flow_html(idx,total)}"""


def contain_photo_block(d):
    """Whole image shown, no crop: a framed card on charcoal (for screenshots / low-res stills)."""
    return f"""
    <div style="position:absolute;left:0;right:0;top:96px;height:{d.get('h',690)}px;display:flex;justify-content:center;align-items:flex-start">
      <img src="file://{PHOTOS/d['photo']}" style="height:{d.get('h',690)}px;width:auto;border-radius:22px;box-shadow:0 30px 60px rgba(0,0,0,.45);border:2px solid rgba(232,225,206,.12)">
    </div>"""

def split_photo_block(d):
    """Photo on the top ~58%, fading into charcoal; keeps faces clear of the headline."""
    return f"""
    <div class="photo" style="{photo_css(d['photo'], d.get('pos','center top'))};height:800px"></div>
    <div class="grad" style="height:800px;background:linear-gradient(180deg,rgba({SPLIT},0) 55%,rgba({SPLIT},.6) 80%,rgba({SPLIT},1) 100%)"></div>"""

def t_cover_bold(d, idx, total):
    lines = d['lines']
    split = d.get('variant') == 'split'
    size = min(anton_size(lines, d.get('size', 210)), int((520 if split else 620)/(len(lines)*0.95)))
    bg = split_photo_block(d) if split else f"""<div class="photo" style="{photo_css(d['photo'], d.get('pos','center'))}"></div>
    <div class="grad" style="background:linear-gradient(180deg,rgba({GRAD},.1) 0%,rgba({GRAD},.02) 38%,rgba({GRAD},.85) 64%,rgba({GRAD},.99) 100%)"></div>"""
    return f"""
    {bg}
    <div class="pad" style="bottom:250px">
      {f'<div class="meta t" style="margin-bottom:30px">{esc(d["kicker"])}</div>' if d.get('kicker') else ''}
      <div class="anton {'c' if split else 'p'}" style="font-size:{size}px">{'<br>'.join(rich(l) for l in lines)}</div>
      {f'<div class="body" style="margin-top:34px;font-size:36px;color:{PAL["cream"] if split else PAL["ptext"]}">{rich(d["sub"])}</div>' if d.get('sub') else ''}
    </div>
    {mark_html(light=(THEME_LIGHT and split))}{flow_html(idx,total,cover=True,light=split)}{f'<div style="position:absolute;right:72px;bottom:118px;font-family:{F_BODY};font-weight:500;font-size:18px;letter-spacing:.06em;color:{PAL["cream"]};opacity:.7">{esc(d["credit"])}</div>' if d.get('credit') else ''}"""

def t_editorial(d, idx, total):
    """Raktim-style: full-bleed photo, serif word, light sans subtitle, corner metadata."""
    word = d['word']
    sub = d.get('sub', '')
    size = d.get('size', 230)
    color = d.get('color', PAL['cream'])
    align = d.get('align', 'top')  # top | bottom
    pos_css = 'top:170px' if align == 'top' else 'bottom:250px'
    grad = (f'linear-gradient(180deg,rgba({GRAD},.75) 0%,rgba({GRAD},.25) 45%,rgba({GRAD},.55) 100%)' if align=='top'
            else f'linear-gradient(180deg,rgba({GRAD},.35) 0%,rgba({GRAD},.1) 40%,rgba({GRAD},.9) 100%)')
    return f"""
    <div class="photo" style="{photo_css(d['photo'], d.get('pos','center'))}"></div>
    <div class="grad" style="background:{grad}"></div>
    <div class="pad" style="{pos_css};text-align:{d.get('textalign','center')}">
      <div class="serif" style="font-size:{size}px;color:{color}">{rich(word)}</div>
      {f'<div style="font-family:{F_BODY};font-weight:500;font-size:{d.get("subsize",44)}px;letter-spacing:-.01em;margin-top:18px;color:{color}">{rich(sub)}</div>' if sub else ''}
    </div>
    {mark_html(light=False)}{(flow_html(idx,total,cover=True) if idx==1 and total>1 else flow_html(idx,total))}
    <div style="position:absolute;right:72px;bottom:118px;text-align:right">
      <div class="meta" style="color:{PAL['orange']};font-size:18px">{esc(d.get('tag', DEFAULTS.get('tag', '')))}</div>
      <div style="font-family:{F_BODY};font-weight:500;font-size:20px;color:{PAL['cream']}">{esc(d.get('tagline', DEFAULTS.get('tagline', '')))}</div>
    </div>"""

def t_editorial_text(d, idx, total):
    """Cream page with serif headline + body, for mid-carousel text slides."""
    return f"""
    <div class="grad" style="background:{PAL['cream']}"></div>
    <div class="pad" style="top:150px;bottom:250px;display:flex;flex-direction:column;justify-content:center">
      {f'<div class="meta" style="color:{PAL["orange"]};margin-bottom:30px">{esc(d["kicker"])}</div>' if d.get('kicker') else ''}
      <div class="serif" style="font-size:{d.get('size',150)}px;color:{PAL['charcoal']}">{rich(d['word'])}</div>
      {f'<div class="body" style="margin-top:40px;color:{PAL["charcoal"]};font-size:{d.get("bodysize",38)}px"><span style="color:{PAL["charcoal"]}">{rich(d["body"])}</span></div>' if d.get('body') else ''}
    </div>
    {mark_html(light=True)}{flow_html(idx,total)}
    <div style="position:absolute;right:72px;bottom:118px;text-align:right">
      <div class="meta" style="color:{PAL['orange']};font-size:18px">{esc(d.get('tag', DEFAULTS.get('tag', '')))}</div>
      <div style="font-family:{F_BODY};font-weight:500;font-size:20px;color:{PAL['charcoal']}">{esc(d.get('tagline', DEFAULTS.get('tagline', '')))}</div>
    </div>"""

def t_call(d, idx=1, total=1):
    """Corporate Entrepreneur promo card."""
    lines = d.get('lines', ['The Corporate', 'Entrepreneur'])
    size = anton_size(lines, d.get('size', 150))
    headline = d.get('headline', '')
    if d.get('variant') == 'split':
        bg = f"""<div class="photo" style="{photo_css(d['photo'], d.get('pos','center top'))};height:{d.get('ph',720)}px"></div>
    <div class="grad" style="height:{d.get('ph',720)}px;background:linear-gradient(180deg,rgba({SPLIT},0) 55%,rgba({SPLIT},.55) 80%,rgba({SPLIT},1) 100%)"></div>"""
    else:
        bg = f"""<div class="photo" style="{photo_css(d['photo'], d.get('pos','center'))}"></div>
    <div class="grad" style="background:linear-gradient(180deg,rgba({GRAD},.2) 0%,rgba({GRAD},.3) 30%,rgba({GRAD},.92) 58%,rgba({GRAD},1) 100%)"></div>"""
    return f"""
    {bg}
    <div style="position:absolute;left:72px;top:118px;background:{PAL['orange']};color:{PAL['charcoal']};font-family:{F_DISPLAY};font-size:30px;letter-spacing:.08em;text-transform:uppercase;padding:14px 22px 10px">{esc(d.get('badge', DEFAULTS.get('badge', '')))}</div>
    <div class="pad" style="bottom:360px">
      {f'<div class="body" style="font-size:40px;margin-bottom:28px;font-weight:600;color:{PAL["ptext"]}">{rich(headline)}</div>' if headline else ''}
      <div class="anton p" style="font-size:{size}px">{'<br>'.join(rich(l) for l in lines)}</div>
    </div>
    <div class="pad" style="bottom:250px;display:flex;flex-wrap:wrap;gap:16px 0;align-items:center">
      <div class="anton" style="font-size:54px;color:{PAL['orange']}">{esc(d.get('when', DEFAULTS.get('when', '')))}</div>
      <div class="anton p" style="font-size:54px;margin-left:30px">{esc(d.get('time','7PM EST'))}</div>
      <div class="anton t" style="font-size:54px;margin-left:30px">{esc(d.get('price','Free'))}</div>
    </div>
    {mark_html(light=False)}{flow_html(1,1)}
    <div style="position:absolute;right:72px;bottom:118px;text-align:right">
      <div class="meta p" style="letter-spacing:.12em;text-transform:none;font-size:24px">{esc(d.get('url',''))}</div>
      <div class="meta p" style="opacity:.8;font-size:18px;margin-top:6px">{esc(d.get('foot',''))}</div>
    </div>"""

def t_photo(d, idx, total):
    lines = d.get('lines', [])
    split = d.get('variant') == 'split'
    contain = d.get('variant') == 'contain'
    size = min(anton_size(lines, d.get('size', 190)), int((460 if (split or contain) else 560)/(len(lines)*0.95))) if lines else 0
    credit = f'<div style="position:absolute;right:72px;bottom:118px;font-family:{F_BODY};font-weight:500;font-size:18px;letter-spacing:.06em;color:{PAL["cream"]};opacity:.7">{esc(d["credit"])}</div>' if d.get('credit') else ''
    bg = contain_photo_block(d) if contain else split_photo_block(d) if split else f"""<div class="photo" style="{photo_css(d['photo'], d.get('pos','center'))}"></div>
    <div class="grad" style="background:linear-gradient(180deg,rgba({GRAD},.1) 0%,rgba({GRAD},.02) 36%,rgba({GRAD},.85) 62%,rgba({GRAD},.99) 100%)"></div>"""
    return f"""
    {bg}
    <div class="pad" style="bottom:250px">
      {f'<div class="meta t" style="margin-bottom:26px">{esc(d["kicker"])}</div>' if d.get('kicker') else ''}
      {f'<div class="anton {"c" if (split or contain) else "p"}" style="font-size:{size}px">{"<br>".join(rich(l) for l in lines)}</div>' if lines else ''}
      {f'<div class="body" style="margin-top:30px;font-size:{d.get("bodysize",38)}px;color:{PAL["cream"] if (split or contain) else PAL["ptext"]}">{rich(d["body"])}</div>' if d.get('body') else ''}
    </div>
    {mark_html(light=(THEME_LIGHT and (split or contain)))}{credit}{flow_html(idx,total)}"""

def t_quote_card(d, idx=1, total=1):
    """Standalone quote card: no flow line, real words, attribution. variants: photo (full bleed) | split (photo top, quote on light)."""
    lines = d['lines']
    variant = d.get('variant', 'photo')
    who = d.get('attribution', DEFAULTS.get('name', ''))
    role = d.get('role', DEFAULTS.get('tag', ''))
    qmark = f'<div class="serif" style="font-size:150px;line-height:.6;color:{PAL["orange"]};margin-bottom:10px">\u201c</div>'
    attrib = lambda col, sub: f"""<div style="margin-top:38px;display:flex;align-items:center;gap:18px">
          <div style="width:56px;height:4px;background:{PAL['orange']}"></div>
          <div><div style="font-family:{F_UTIL};font-weight:700;font-size:30px;letter-spacing:.12em;text-transform:uppercase;color:{col}">{esc(who)}</div>
          <div style="font-family:{F_BODY};font-weight:500;font-size:22px;letter-spacing:.02em;color:{sub};margin-top:4px">{esc(role)}</div></div></div>"""
    if variant == 'photo':
        size = min(anton_size(lines, d.get('size', 112)), int(620/(len(lines)*1.0)))
        return f"""
        <div class="photo" style="{photo_css(d['photo'], d.get('pos','center'))}"></div>
        <div class="grad" style="background:linear-gradient(180deg,rgba({GRAD},.08) 0%,rgba({GRAD},.2) 30%,rgba({GRAD},.9) 62%,rgba({GRAD},.98) 100%)"></div>
        <div class="pad" style="bottom:150px">
          {qmark}
          <div class="anton" style="font-size:{size}px;color:{PAL['ptext']}">{'<br>'.join(rich(l) for l in lines)}</div>
          {attrib(PAL['ptext'], 'rgba(255,255,255,.75)')}
        </div>
        <div style="position:absolute;right:72px;bottom:110px"><img src="file://{LOGO_DARK}" style="width:{LOGO_W}px;height:auto;display:block;opacity:.95"></div>"""
    else:
        size = min(anton_size(lines, d.get('size', 104)), int(430/(len(lines)*1.0)))
        return f"""
        <div class="grad" style="background:{PAL['charcoal']}"></div>
        <div class="photo" style="{photo_css(d['photo'], d.get('pos','center top'))};height:{d.get('ph',640)}px"></div>
        <div class="grad" style="height:{d.get('ph',640)}px;background:linear-gradient(180deg,rgba({SPLIT},0) 70%,rgba({SPLIT},1) 100%)"></div>
        <div class="pad" style="top:{d.get('ph',640)-60}px;bottom:200px;display:flex;flex-direction:column;justify-content:center">
          {qmark}
          <div class="anton" style="font-size:{size}px;color:{PAL['cream']}">{'<br>'.join(rich(l) for l in lines)}</div>
          {attrib(PAL['cream'], PAL['meta'])}
        </div>
        <div style="position:absolute;right:72px;bottom:110px"><img src="file://{LOGO_LIGHT}" style="width:{LOGO_W}px;height:auto;display:block"></div>"""

TEMPLATES = dict(quote_card=t_quote_card, photo=t_photo, quote=t_quote, bold=t_bold, cover_bold=t_cover_bold, editorial=t_editorial, editorial_text=t_editorial_text, call=t_call)

def render_slide(d, idx, total):
    t = d['t']
    inner = TEMPLATES[t](d, idx, total) if t != 'quote' else t_quote(d)
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{BASE_CSS}</style></head><body><div class='slide'>{inner}</div></body></html>"

def build(post_ids=None):
    content = json.load(open(BRAND_DIR / 'content.json'))
    OUT.mkdir(exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': 1080, 'height': 1350}, device_scale_factor=1)
        for post in content['posts']:
            if post_ids and post['id'] not in post_ids: continue
            slides = post['slides']
            for i, s in enumerate(slides, 1):
                htmlfile = OUT / f"{post['id']}-{i:02d}.html"
                htmlfile.write_text(render_slide(s, i, len(slides)))
                pg.goto(htmlfile.as_uri()); pg.wait_for_timeout(250)
                pg.screenshot(path=str(OUT / f"{post['id']}-{i:02d}.png"))
            print('built', post['id'], len(slides))
        b.close()

if __name__ == '__main__':
    build(sys.argv[1:] or None)
