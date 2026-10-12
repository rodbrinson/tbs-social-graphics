#!/usr/bin/env python3
"""Turn content.json into schedule.json: one entry per Metricool call (IG / FB+LinkedIn / Threads)."""
import json, sys, glob, os
ROOT = os.path.dirname(os.path.abspath(__file__))
BASE = sys.argv[1] if len(sys.argv) > 1 else 'https://raw.githubusercontent.com/OWNER/tbs-social-graphics/main/2026-10/'
DOORS = {'call': 'https://thecorporateexodus.com', 'speaker': 'https://rodbrinson.com/paid-keynote-speaker-brand-strategy-rod-brinson/'}
BRAND = '6295498'
TZ = 'America/New_York'
content = json.load(open(os.path.join(ROOT, 'content.json')))
out = []
for p in content['posts']:
    media = [BASE + os.path.basename(f)[:-4] + '.jpg' for f in sorted(glob.glob(os.path.join(ROOT, 'out', p['id'] + '-*.png')))]
    door = DOORS.get(p.get('door'))
    when = f"{p['date']}T{p['slot']}:00"
    cap = p['caption']
    ig = cap.replace('{door}', 'Link in bio.')
    fb = cap.replace('{door}', door or '')
    th = p['threads'].replace('{door}', door or '')
    if p.get('door') == 'speaker':
        ig = cap.replace('{door}', 'Speaker page is at the link in bio.')
    out.append(dict(id=p['id']+'-ig', date=when, networks=['instagram'], text=ig.strip(), firstComment=p.get('hashtags',''), media=media))
    out.append(dict(id=p['id']+'-fbli', date=when, networks=['facebook','linkedin'], text=fb.strip(), firstComment='', media=media))
    if p['kind'] != 'call':
        out.append(dict(id=p['id']+'-th', date=when, networks=['threads'], text=th.strip(), firstComment='', media=media))
json.dump(out, open(os.path.join(ROOT, 'schedule.json'), 'w'), indent=1, ensure_ascii=False)
print(len(out), 'calls')
for o in out:
    assert len(o['text']) <= 2200, o['id']
    if 'threads' in o['networks']: assert len(o['text']) <= 500, (o['id'], len(o['text']))
print('lengths ok')
