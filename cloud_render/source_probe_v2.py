#!/usr/bin/env python3
import re,json,math,subprocess,urllib.parse,time,requests
from pathlib import Path
OUT=Path('cloud_probe'); SRC=OUT/'sources'; SHEETS=OUT/'sheets'
SRC.mkdir(parents=True,exist_ok=True); SHEETS.mkdir(parents=True,exist_ok=True)
UA={'User-Agent':'Mozilla/5.0 FDP-edit-source-probe/2.0'}; API='https://commons.wikimedia.org/w/api.php'
manifest=[]; errors=[]
def run(cmd): print('+',' '.join(map(str,cmd)),flush=True); return subprocess.run(cmd,check=True)
def safe(s): return (re.sub(r'[^A-Za-z0-9._-]+','_',s).strip('_')[:120] or 'asset')
def probe(p):
 out={'duration':0}
 try:
  out['duration']=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nk=1:nw=1',str(p)],text=True).strip())
  j=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,codec_name','-of','json',str(p)],text=True));
  if j.get('streams'): out.update(j['streams'][0])
 except Exception as e: out['probe_error']=repr(e)
 return out
def sheet(p,label,n=12):
 d=probe(p).get('duration',0)
 if not d:return
 times=[max(0,min(d-.1,(i+.5)*d/n)) for i in range(n)]; frames=[]
 for i,t in enumerate(times):
  q=SHEETS/f'{safe(label)}_{i:02d}.jpg'; subprocess.run(['ffmpeg','-y','-loglevel','error','-ss',f'{t:.3f}','-i',str(p),'-frames:v','1','-vf','scale=480:-2','-q:v','3',str(q)])
  if q.exists(): frames.append((q,t))
 if not frames:return
 from PIL import Image,ImageDraw
 ims=[Image.open(q).convert('RGB') for q,_ in frames]; W=480; H=max(x.height for x in ims); rows=math.ceil(len(ims)/4); c=Image.new('RGB',(W*4,H*rows),(12,12,12)); dr=ImageDraw.Draw(c)
 for idx,((q,t),im) in enumerate(zip(frames,ims)):
  if im.height!=H: im=im.resize((W,H))
  x=(idx%4)*W;y=(idx//4)*H;c.paste(im,(x,y));dr.rectangle((x,y,x+100,y+24),fill='black');dr.text((x+5,y+4),f'{t:.1f}s',fill='white')
 c.save(SHEETS/f'{safe(label)}_CONTACT.jpg',quality=86)
def add(path,label,purpose,url,source_type,rights='source documented; reuse permission to verify'):
 if not path or not Path(path).exists():return
 r={'path':str(path),'label':label,'purpose':purpose,'url':url,'source_type':source_type,'rights':rights};r.update(probe(path));manifest.append(r);sheet(Path(path),label)
def commons_download(title,label,purpose):
 try:
  if not title.startswith('File:'): title='File:'+title
  r=requests.get(API,params={'action':'query','format':'json','prop':'imageinfo','titles':title,'iiprop':'url|mime|size|extmetadata'},headers=UA,timeout=30);r.raise_for_status();page=next(iter(r.json()['query']['pages'].values()));ii=page.get('imageinfo',[{}])[0]
  u=urllib.parse.urlsplit(ii['url']);url=urllib.parse.urlunsplit((u.scheme,u.netloc,u.path,'',''));ext=Path(urllib.parse.unquote(u.path)).suffix or '.webm';dst=SRC/(safe(label)+ext);ok=False
  for attempt in range(4):
   rr=requests.get(url,headers={**UA,'Referer':'https://commons.wikimedia.org/'},stream=True,timeout=120)
   if rr.status_code==200:
    with open(dst,'wb') as f:
     for ch in rr.iter_content(1024*1024):
      if ch:f.write(ch)
    ok=True;break
   print('commons attempt',attempt+1,'status',rr.status_code);time.sleep(3*(attempt+1))
  if not ok:raise RuntimeError(f'HTTP {rr.status_code}')
  rights=ii.get('extmetadata',{}).get('LicenseShortName',{}).get('value') or 'Wikimedia license metadata';add(dst,label,purpose,'https://commons.wikimedia.org/wiki/'+urllib.parse.quote(page.get('title',title).replace(' ','_')),'Wikimedia Commons',rights)
 except Exception as e:errors.append({'label':label,'source':title,'error':repr(e)});print('COMMONS FAILED',label,repr(e))
def ytdlp(url,label,purpose,max_h=1080,source_type='official source'):
 tmpl=str(SRC/(safe(label)+'.%(ext)s'));cmd=['yt-dlp','--no-playlist','--no-warnings','--retries','3','--fragment-retries','3','--merge-output-format','mp4','-f',f'bv*[height<={max_h}]+ba/b[height<={max_h}]/best','-o',tmpl,url]
 try:
  run(cmd);files=[p for p in SRC.glob(safe(label)+'.*') if p.suffix.lower() in {'.mp4','.webm','.mkv','.mov'}]
  if not files:raise RuntimeError('no media produced')
  add(files[0],label,purpose,url,source_type)
 except Exception as e:errors.append({'label':label,'source':url,'error':repr(e)});print('YTDLP FAILED',label,repr(e))
# New 2026 official FDP sources, not used in the earlier edits.
ytdlp('https://www.youtube.com/watch?v=RnoYkXVw7kg','kubicki_bpt26','Wolfgang Kubicki – 77. FDP-Bundesparteitag 2026',1080,'FDP verified YouTube channel')
ytdlp('https://www.youtube.com/watch?v=gErCWe5mvTQ','strack_bpt26','Marie-Agnes Strack-Zimmermann – FDP Bundesparteitag 2026',1080,'FDP verified YouTube channel')
ytdlp('https://www.youtube.com/watch?v=NrAlfYnJsq8','duerr_bpt26','Christian Dürr – FDP Bundesparteitag 2026',1080,'FDP verified YouTube channel')
ytdlp('https://www.youtube.com/watch?v=NjmDlbga21c','fdp_bpt26_day1','77. FDP-Bundesparteitag 2026 – stage, delegates, audience',720,'FDP verified YouTube channel')
# Official European Parliament source.
ytdlp('https://multimedia.europarl.europa.eu/en/video/the-future-of-the-european-defence-opening-statement-by-marie-agnes-strack-zimmermann-chair-of-sede-committee_I281575','strack_europarl','Marie-Agnes Strack-Zimmermann – European Parliament',1080,'European Parliament Multimedia Centre')
# CC sources, best effort if the Wikimedia CDN accepts this runner.
commons_download('Sexismusdebatte in Deutschland - Anke Domscheit-Berg im Interview - YouTube.webm','kubicki_ccby3','Wolfgang Kubicki – CC source')
commons_download('(20260502 173648155) ICE train passing by Bitterfeld.webm','ice_2026','ICE / Germany mobility')
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False));(OUT/'errors.json').write_text(json.dumps(errors,indent=2,ensure_ascii=False));print('SUCCESSFUL SOURCES',len(manifest));print(json.dumps(manifest,indent=2,ensure_ascii=False));print('ERRORS',json.dumps(errors,indent=2,ensure_ascii=False))
if not manifest:raise SystemExit('No source could be downloaded')
