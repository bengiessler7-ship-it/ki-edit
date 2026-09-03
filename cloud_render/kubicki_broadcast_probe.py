#!/usr/bin/env python3
import subprocess, json, math
from pathlib import Path
from PIL import Image, ImageDraw

OUT=Path('kubicki_broadcast'); SRC=OUT/'sources'; SHEETS=OUT/'sheets'
SRC.mkdir(parents=True, exist_ok=True); SHEETS.mkdir(parents=True, exist_ok=True)
VIDEOS=[
 ('phoenix_bpt2026','https://www.zdf.de/video/magazine/phoenix-collection-phoenix-1080805-1610/phoenix-fdp-parteitag-rede-des-neuen-vorsitzenden-kubicki-100','phoenix/ZDF – FDP-Parteitag Kubicki 30.05.2026'),
 ('maischberger_2026','https://www.ardmediathek.de/video/maischberger/wolfgang-kubicki-ueber-den-fdp-vorsitz-und-die-ausrichtung-der-partei/wdr/Y3JpZDovL3dkci5kZS9CZWl0cmFnLXNvcGhvcmEtNDk4ZWMxY2UtNDM0MS00ZTU3LWJmNGMtZmUzYTVkMDFlODc4','ARD/WDR – Kubicki bei maischberger 09.06.2026'),
 ('ndr_bpt_preview_2026','https://www.ardmediathek.de/video/schleswig-holstein-magazin/vor-dem-fdp-bundesparteitag-kubickis-letzter-coup/ndr/Y3JpZDovL25kci5kZS84Yjg5NjIxMC04YjBkLTQ1NDMtOWMxNy02MWM4ZTMxYzc1OWI','NDR – Kubickis letzter Coup 28.05.2026'),
]
manifest=[]; errors=[]

def probe(p):
    x=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-show_entries','stream=width,height,r_frame_rate,codec_name','-of','json',str(p)],text=True))
    v=next((s for s in x.get('streams',[]) if 'width' in s),{})
    return {'duration':float(x['format']['duration']),**v}

def sheet(p,label):
    pr=probe(p); d=pr['duration']; n=18
    times=[max(.2,min(d-.5,(i+.5)*d/n)) for i in range(n)]
    ims=[]
    for i,t in enumerate(times):
        q=SHEETS/f'{label}_{i:02d}.jpg'
        subprocess.run(['ffmpeg','-y','-ss',f'{t:.2f}','-i',str(p),'-frames:v','1','-vf','scale=420:-2','-q:v','2',str(q)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        if q.exists(): ims.append((q,t))
    if not ims:return
    opened=[Image.open(q).convert('RGB') for q,_ in ims]; W=420; H=max(i.height for i in opened); cols=3; rows=math.ceil(len(opened)/cols)
    c=Image.new('RGB',(W*cols,H*rows),(15,15,15)); dr=ImageDraw.Draw(c)
    for j,((q,t),im) in enumerate(zip(ims,opened)):
        if im.height!=H: im=im.resize((W,H))
        x=(j%cols)*W; y=(j//cols)*H; c.paste(im,(x,y)); dr.rectangle((x,y,x+88,y+22),fill=(0,0,0)); dr.text((x+3,y+3),f'{t:.0f}s',fill=(255,255,255))
    c.save(SHEETS/f'{label}_CONTACT.jpg',quality=90)

for label,url,title in VIDEOS:
    target=str(SRC/(label+'.%(ext)s'))
    cmd=['yt-dlp','--no-playlist','--no-warnings','--merge-output-format','mp4','-f','bv*[height<=1080]+ba/b[height<=1080]/best','-o',target,url]
    try:
        print('+',' '.join(cmd),flush=True); subprocess.run(cmd,check=True)
        cand=[p for p in SRC.glob(label+'.*') if p.suffix.lower() in {'.mp4','.mkv','.webm','.mov'}]
        if not cand: raise RuntimeError('no media produced')
        p=cand[0]; pr=probe(p); manifest.append({'label':label,'title':title,'url':url,'path':str(p),**pr}); sheet(p,label); print('OK',label,pr,flush=True)
    except Exception as e:
        errors.append({'label':label,'url':url,'error':repr(e)}); print('FAIL',label,repr(e),flush=True)

(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)); (OUT/'errors.json').write_text(json.dumps(errors,indent=2,ensure_ascii=False))
print('SUCCESS',len(manifest)); print(json.dumps(manifest,indent=2,ensure_ascii=False)); print('ERRORS',json.dumps(errors,indent=2,ensure_ascii=False))
