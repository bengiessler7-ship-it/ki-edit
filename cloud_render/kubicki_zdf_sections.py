#!/usr/bin/env python3
import subprocess, json, math
from pathlib import Path
from PIL import Image, ImageDraw

OUT=Path('kubicki_sections'); SRC=OUT/'sources'; SHEETS=OUT/'sheets'
SRC.mkdir(parents=True, exist_ok=True); SHEETS.mkdir(parents=True, exist_ok=True)
URL='https://www.zdf.de/video/magazine/phoenix-collection-phoenix-1080805-1610/phoenix-fdp-parteitag-rede-des-neuen-vorsitzenden-kubicki-100'
# 12-second samples spread through the 39-minute speech
SECTIONS=[('k01',55,67),('k02',205,217),('k03',420,432),('k04',710,722),('k05',1030,1042),('k06',1390,1402),('k07',1810,1822),('k08',2160,2172)]
manifest=[]; errors=[]

def probe(p):
    x=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-show_entries','stream=width,height,r_frame_rate,codec_name','-of','json',str(p)],text=True))
    v=next((s for s in x.get('streams',[]) if 'width' in s),{})
    return {'duration':float(x['format']['duration']),**v}

def make_sheet(p,label):
    pr=probe(p); d=pr['duration']; ts=[min(d-.1,x) for x in [1,3,5,7,9,11] if x<d]
    ims=[]
    for i,t in enumerate(ts):
        q=SHEETS/f'{label}_{i}.jpg'
        subprocess.run(['ffmpeg','-y','-ss',str(t),'-i',str(p),'-frames:v','1','-vf','scale=500:-2','-q:v','2',str(q)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        if q.exists(): ims.append((q,t))
    if not ims:return
    opened=[Image.open(q).convert('RGB') for q,_ in ims]; W=500; H=max(i.height for i in opened); cols=3; rows=2
    c=Image.new('RGB',(W*cols,H*rows),(12,12,12)); dr=ImageDraw.Draw(c)
    for j,((q,t),im) in enumerate(zip(ims,opened)):
        if im.height!=H: im=im.resize((W,H))
        x=(j%cols)*W; y=(j//cols)*H; c.paste(im,(x,y)); dr.rectangle((x,y,x+90,y+24),fill=(0,0,0)); dr.text((x+5,y+4),f'{t:.1f}s',fill=(255,255,255))
    c.save(SHEETS/f'{label}_CONTACT.jpg',quality=90)

for label,start,end in SECTIONS:
    out=str(SRC/(label+'.%(ext)s'))
    cmd=['yt-dlp','--no-playlist','--no-warnings','--force-keyframes-at-cuts','--download-sections',f'*{start}-{end}','--merge-output-format','mp4','-f','bv*[height<=720]+ba/b[height<=720]/best','-o',out,URL]
    try:
        print('+',' '.join(cmd),flush=True); subprocess.run(cmd,check=True)
        cand=[p for p in SRC.glob(label+'.*') if p.suffix.lower() in {'.mp4','.mkv','.webm','.mov'}]
        if not cand: raise RuntimeError('no output')
        p=cand[0]; pr=probe(p); make_sheet(p,label)
        manifest.append({'label':label,'source_url':URL,'source_start':start,'source_end':end,'path':str(p),**pr}); print('OK',label,pr,flush=True)
    except Exception as e:
        errors.append({'label':label,'start':start,'end':end,'error':repr(e)}); print('FAIL',label,repr(e),flush=True)

(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)); (OUT/'errors.json').write_text(json.dumps(errors,indent=2,ensure_ascii=False))
print('SUCCESS',len(manifest)); print(json.dumps(manifest,indent=2,ensure_ascii=False)); print('ERRORS',json.dumps(errors,indent=2,ensure_ascii=False))
