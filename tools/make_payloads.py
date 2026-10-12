#!/usr/bin/env python3
"""Turn schedule.json into payloads.json: ready-to-send Metricool createScheduledPost bodies.

Usage: python3 make_payloads.py [--tz America/New_York] [--offset -04:00] [--skip id1,id2]
Each payload = {"id", "date" (ISO with offset), "info" (JSON string for the MCP tool)}.
"""
import json, os, sys, argparse
ROOT = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument('brand_dir')
ap.add_argument('--tz', default=None)
ap.add_argument('--offset', default=None, help='UTC offset for the date field; defaults to brand utc_offset_dst')
ap.add_argument('--skip', default='', help='comma-separated schedule ids already sent')
a = ap.parse_args()
skip = set(filter(None, a.skip.split(',')))
BDIR = os.path.abspath(a.brand_dir)
brand = json.load(open(os.path.join(BDIR, 'brand.json')))
TZ = a.tz or brand['metricool']['timezone']
OFF = a.offset or brand['metricool']['utc_offset_dst']

NET_DATA = {
    'instagram': ('instagramData', {'type': 'POST', 'isAiGenerated': False}),
    'facebook': ('facebookData', {'type': 'POST'}),
    'linkedin': ('linkedinData', {'type': 'post', 'previewIncluded': True, 'publishImagesAsPDF': False}),
    'threads': ('threadsData', {'allowedCountryCodes': []}),
}
sched = json.load(open(os.path.join(BDIR, 'schedule.json')))
out = []
for s in sched:
    if s['id'] in skip:
        continue
    info = {
        'text': s['text'],
        'media': s['media'],
        'providers': [{'network': n} for n in s['networks']],
        'publicationDate': {'dateTime': s['date'], 'timezone': TZ},
        'autoPublish': True, 'draft': False, 'shortener': False,
    }
    if s.get('firstComment'):
        info['firstCommentText'] = s['firstComment']
    for n in s['networks']:
        key, val = NET_DATA[n]
        info[key] = val
    out.append({'id': s['id'], 'date': s['date'] + OFF, 'info': json.dumps(info, ensure_ascii=False)})
json.dump(out, open(os.path.join(BDIR, 'payloads.json'), 'w'), indent=1, ensure_ascii=False)
print(len(out), 'payloads')
