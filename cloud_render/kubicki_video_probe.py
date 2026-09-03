#!/usr/bin/env python3
import subprocess, json, os, math, re
from pathlib import Path
from PIL import Image, ImageDraw

OUT=Path('kubicki_probe'); SRC=OUT/'sources'; SHEETS=OUT/'sheets'
SRC.mkdir(parents=True, exist_ok=True); SHEETS.mkdir(parents=True, exist_ok=True)
VIDEOS=[
 ('kubicki_2013','https://www.youtube.com/watch?v=rcH4_SWCwSY','Rede Kubicki – FDP 2013'),
 ('kubicki_2017','https://www.youtube.com/watch?v=H2QOPDQaGBE','Rede Wolfgang Kubicki – FDP 2017'),
 ('kubicki_2019','https://www.youtube.com/watch?v=hohsW8aAMh4','Vorstellungsrede Wolfgang Kubicki – FDP 2019'),
 ('kubicki_2021','https://www.youtube.com/watch?v=6izesg8fNNg','Eröffnungsrede Wolfgang Kubicki – FDP 2021'),
]
manifest=[]; errors=[]

def probe(p):
    try:
        x=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-show_entries','stream=width,height,r_frame_rate,codec_name','-of','json',str(p)],text=True))
        v=next((s for s in x.get('streams',[]) if 'width' in s),{})
        return {'duration':float(x['format']['duration']),**v}
    except Exception as e: return {'probe_error':repr(e)}

def sheet(p,label):
    pr=probe(p); d=pr.get('duration',0)
    if not d: return
    # denser at start/middle/end to catch burned graphics and framing
    times=sorted(set([0.5,2,5,10,15,20,30,45,60,max(1,d*.25),max(1,d*.5),max(1,d*.75),max(1,d-5)]))
    times=[t for t in times if t<d]
    ims=[]
    for i,t in enumerate(times):
        q=SHEETS/f'{label}_{i:02d}.jpg'
        subprocess.run(['ffmpeg','-y','-ss',f'{t:.3f}','-i',str(p),'-frames:v','1','-vf','scale=420:-2','-q:v','2',str(q)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        if q.exists(): ims.append((q,t))
    if not ims: return
    opened=[Image.open(q).convert('RGB') for q,_ in ims]; W=420; H=max(i.height for i in opened); cols=3; rows=math.ceil(len(opened)/cols)
    c=Image.new('RGB',(W*cols,H*rows),(18,18,18)); dr=ImageDraw.Draw(c)
    for j,((q,t),im) in enumerate(zip(ims,opened)):
        if im.height!=H: im=im.resize((W,H))
        x=(j%cols)*W; y=(j//cols)*H; c.paste(im,(x,y)); dr.rectangle((x,y,x+85,y+24),fill=(0,0,0)); dr.text((x+4,y+4),f'{t:.1f}s',fill=(255,255,255))
    c.save(SHEETS/f'{label}_CONTACT.jpg',quality=90)

for label,url,title in VIDEOS:
    target=str(SRC/(label+'.%(ext)s'))
    attempts=[
      ['yt-dlp','--no-playlist','--no-warnings','--retries','2','--fragment-retries','2','--merge-output-format','mp4','-f','bv*[height<=1080]+ba/b[height<=1080]/best','-o',target,url],
      ['yt-dlp','--no-playlist','--no-warnings','--extractor-args','youtube:player_client=tv,web_safari','--retries','2','--merge-output-format','mp4','-f','bv*[height<=1080]+ba/b[height<=1080]/best','-o',target,url],
      ['yt-dlp','--no-playlist','--no-warnings','--extractor-args','youtube:player_client=android_vr','--retries','2','--merge-output-format','mp4','-f','bv*[height<=1080]+ba/b[height<=1080]/best','-o',target,url]
    ]
    ok=None
    for cmd in attempts:
        try:
            print('+',' '.join(cmd),flush=True); subprocess.run(cmd,check=True)
            cand=[p for p in SRC.glob(label+'.*') if p.suffix.lower() in {'.mp4','.webm','.mkv','.mov'}]
            if cand: ok=cand[0]; break
        except Exception as e: last=e
    if ok:
        pr=probe(ok); manifest.append({'label':label,'title':title,'url':url,'path':str(ok),**pr}); sheet(ok,label)
        print('OK',label,pr,flush=True)
    else:
        errors.append({'label':label,'url':url,'error':repr(last)}); print('FAILED',label,repr(last),flush=True)

(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False))
(OUT/'errors.json').write_text(json.dumps(errors,indent=2,ensure_ascii=False))
print('SUCCESS',len(manifest)); print(json.dumps(manifest,indent=2,ensure_ascii=False)); print('ERRORS',json.dumps(errors,indent=2,ensure_ascii=False))
