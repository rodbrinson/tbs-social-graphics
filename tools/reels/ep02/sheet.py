"""Contact sheet: python3 sheet.py <video> <out.jpg> <step_sec> [cols] [thumb_w]"""
import subprocess, sys, json
from PIL import Image, ImageDraw
vid, out, step = sys.argv[1], sys.argv[2], float(sys.argv[3])
cols = int(sys.argv[4]) if len(sys.argv) > 4 else 8
tw = int(sys.argv[5]) if len(sys.argv) > 5 else 216
dur = float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',vid]).decode())
ts = []
t = 1.0
while t < dur:
    ts.append(round(t, 2)); t += step
ims = []
for i, t in enumerate(ts):
    p = f'/tmp/_sh_{i}.jpg'
    subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',vid,'-frames:v','1','-vf',f'scale={tw}:-1',p], check=True)
    im = Image.open(p).convert('RGB'); d = ImageDraw.Draw(im)
    d.rectangle([0,0,70,18], fill=(0,0,0)); d.text((3,3), f'{t:.0f}s', fill=(255,255,0))
    ims.append(im)
th = ims[0].height
rows = (len(ims)+cols-1)//cols
sheet = Image.new('RGB', (tw*cols, th*rows), (30,30,30))
for i, im in enumerate(ims):
    sheet.paste(im, ((i%cols)*tw, (i//cols)*th))
sheet.save(out, quality=82)
print(out, len(ims), sheet.size)
