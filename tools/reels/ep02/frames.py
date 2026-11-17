"""frames.py <video> <out.jpg> <thumb_w> t1 t2 ...  -> one row of frames at the given times"""
import subprocess, sys
from PIL import Image, ImageDraw
vid, out, tw = sys.argv[1], sys.argv[2], int(sys.argv[3])
ts = sys.argv[4:]
ims = []
for i, t in enumerate(ts):
    p = f'/tmp/_fr_{i}.png'
    subprocess.run(['ffmpeg','-v','error','-y','-ss',t,'-i',vid,'-frames:v','1','-vf',f'scale={tw}:-1:flags=lanczos',p], check=True)
    im = Image.open(p).convert('RGB'); d = ImageDraw.Draw(im)
    d.rectangle([0, im.height-22, 64, im.height], fill=(0,0,0)); d.text((4, im.height-18), f'{t}s', fill=(255,255,0))
    ims.append(im)
cols = min(len(ims), 6)
rows = (len(ims)+cols-1)//cols
s = Image.new('RGB', (tw*cols, ims[0].height*rows), (20,20,20))
for i, im in enumerate(ims): s.paste(im, ((i%cols)*tw, (i//cols)*ims[0].height))
s.save(out, quality=88); print(out, s.size)
