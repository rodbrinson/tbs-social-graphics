#!/usr/bin/env python3
"""Turn content.json into schedule.json: one entry per Metricool call (IG / FB+LinkedIn / Threads)."""
import json, sys, glob, os
ROOT = os.path.dirname(os.path.abspath(__file__))
# Usage: python3 make_schedule.py <brand dir> <month folder e.g. 2026-10> [raw base url]
BDIR = os.path.abspath(sys.argv[1])
MONTH = sys.argv[2]
brand = json.load(open(os.path.join(BDIR, 'brand.json')))
BASE = sys.argv[3] if len(sys.argv) > 3 else f"https://raw.githubusercontent.com/rodbrinson/tbs-social-graphics/main/brands/{brand['slug']}/{MONTH}/"
DOORS = brand['doors']
NETS = set(brand['metricool']['networks'])
content = json.load(open(os.path.join(BDIR, 'content.json')))
out = []
for p in content['posts']:
    media = [BASE + os.path.basename(f)[:-4] + '.jpg' for f in sorted(glob.glob(os.path.join(BDIR, 'out', p['id'] + '-*.png')))]
    door = DOORS.get(p.get('door'))
    when = f"{p['date']}T{p['slot']}:00"
    cap = p['caption']
    ig = cap.replace('{door}', 'Link in bio.')
    fb = cap.replace('{door}', door or '')
    th = p['threads'].replace('{door}', door or '')
    if p.get('door') == 'speaker':
        ig = cap.replace('{door}', 'Speaker page is at the link in bio.')
    if 'instagram' in NETS:
        out.append(dict(id=p['id']+'-ig', date=when, networks=['instagram'], text=ig.strip(), firstComment=p.get('hashtags',''), media=media))
    li_comment = brand['metricool'].get('linkedin_link_in_comment', False)
    if li_comment:
        if 'facebook' in NETS:
            out.append(dict(id=p['id']+'-fb', date=when, networks=['facebook'], text=fb.strip(), firstComment='', media=media))
        if 'linkedin' in NETS:
            li = cap.replace('{door}', 'Registration link is in the first comment.')
            out.append(dict(id=p['id']+'-li', date=when, networks=['linkedin'], text=li.strip(), firstComment=(f"Save your seat: {door}" if door else ''), media=media))
    else:
        fbli = [n for n in ('facebook','linkedin') if n in NETS]
        if fbli:
            out.append(dict(id=p['id']+'-fbli', date=when, networks=fbli, text=fb.strip(), firstComment='', media=media))
    if 'threads' in NETS and p['kind'] != 'call' and p.get('threads'):
        out.append(dict(id=p['id']+'-th', date=when, networks=['threads'], text=th.strip(), firstComment='', media=media))
json.dump(out, open(os.path.join(BDIR, 'schedule.json'), 'w'), indent=1, ensure_ascii=False)
print(len(out), 'calls')
for o in out:
    assert len(o['text']) <= 2200, o['id']
    if 'threads' in o['networks']: assert len(o['text']) <= 500, (o['id'], len(o['text']))
print('lengths ok')
