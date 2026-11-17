"""Detect when the episode's own lower-third cards are on screen.
usage: python3 cards.py <video>  -> prints intervals where the lower band is a dark card or an orange callout
"""
import subprocess, sys
import numpy as np
vid = sys.argv[1]
raw = subprocess.run(['ffmpeg','-v','error','-i',vid,'-vf','crop=700:200:60:1540,scale=1:1:flags=area,format=rgb24','-f','rawvideo','-'],capture_output=True,check=True).stdout
a = np.frombuffer(raw, np.uint8).reshape(-1,3).astype(int)
fps = 30.0
def runs(mask, name):
    out=[]; st=None
    for i,v in enumerate(mask):
        if v and st is None: st=i
        elif not v and st is not None:
            if (i-st)/fps>=0.4: out.append((round(st/fps,2), round(i/fps,2)))
            st=None
    if st is not None and (len(mask)-st)/fps>=0.4: out.append((round(st/fps,2), round(len(mask)/fps,2)))
    print(name, out)
lum = a.mean(1)
dark = lum < 95
orange = (a[:,0] > 190) & (a[:,2] < 120) & (a[:,1] < 170)
print(vid, 'frames', len(a), 'median rgb', np.median(a,0).tolist())
runs(dark, ' dark card:')
runs(orange, ' orange callout:')
