#!/usr/bin/env python3
import re,json,math,subprocess,urllib.parse,time,requests,zipfile,io
from pathlib import Path
OUT=Path('people_probe'); SRC=OUT/'sources'; SHEETS=OUT/'sheets'; DOCS=OUT/'docs'; ASSETS=OUT/'brand'
for d in (SRC,SHEETS,DOCS,ASSETS): d.mkdir(parents=True,exist_ok=True)
API='https://commons.wikimedia.org/w/api.php'; UA={'User-Agent':'Mozilla/5.0 FDP-edit-research/3.0'}
manifest=[]; candidates={}; errors=[]
def safe(s): return (re.sub(r'[^A-Za-z0-9._-]+','_',s).strip('_')[:120] or 'asset')
def probe(p):
 out={}
 try:
  out['duration']=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nk=1:nw=1',str(p)],text=True).strip())
  j=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,codec_name','-of','json',str(p)],text=True)); out.update(j.get('streams',[{}])[0])
 except Exception as e: out['probe_error']=repr(e)
 return out
def sheet(p,label,n=12):
 pr=probe(p); d=pr.get('duration',0)
 if not d:return
 times=[max(0,min(d-.05,(i+.5)*d/n)) for i in range(n)]; frames=[]
 for i,t in enumerate(times):
  q=SHEETS/f'{safe(label)}_{i:02d}.jpg'; subprocess.run(['ffmpeg','-y','-loglevel','error','-ss',f'{t:.3f}','-i',str(p),'-frames:v','1','-vf','scale=480:-2','-q:v','3',str(q)])
  if q.exists():frames.append((q,t))
 if not frames:return
 from PIL import Image,ImageDraw
 ims=[Image.open(q).convert('RGB') for q,_ in frames]; W=480; H=max(im.height for im in ims); rows=math.ceil(len(ims)/4); c=Image.new('RGB',(W*4,H*rows),(12,12,12)); dr=ImageDraw.Draw(c)
 for idx,((q,t),im) in enumerate(zip(frames,ims)):
  if im.height!=H: im=im.resize((W,H))
  x=(idx%4)*W;y=(idx//4)*H;c.paste(im,(x,y));dr.rectangle((x,y,x+100,y+24),fill='black');dr.text((x+5,y+4),f'{t:.1f}s',fill='white')
 c.save(SHEETS/f'{safe(label)}_CONTACT.jpg',quality=86)
def search(q,limit=20):
 r=requests.get(API,params={'action':'query','format':'json','list':'search','srnamespace':6,'srlimit':limit,'srsearch':q},headers=UA,timeout=30);r.raise_for_status();return [x['title'] for x in r.json()['query']['search']]
def cat(name,limit=50):
 r=requests.get(API,params={'action':'query','format':'json','list':'categorymembers','cmtitle':'Category:'+name,'cmnamespace':6,'cmlimit':limit},headers=UA,timeout=30);r.raise_for_status();return [x['title'] for x in r.json()['query']['categorymembers']]
def info(title):
 r=requests.get(API,params={'action':'query','format':'json','prop':'imageinfo','titles':title,'iiprop':'url|mime|size|extmetadata'},headers=UA,timeout=30);r.raise_for_status();page=next(iter(r.json()['query']['pages'].values()));ii=page.get('imageinfo',[{}])[0];return page,ii
def download(title,label,purpose,max_bytes=180_000_000):
 try:
  page,ii=info(title); url=ii.get('url'); sz=ii.get('size') or 0; mime=ii.get('mime','')
  if not url or not re.search(r'video|application/ogg',mime,re.I): raise RuntimeError(f'not video mime={mime}')
  if sz and sz>max_bytes: raise RuntimeError(f'original too large {sz}')
  u=urllib.parse.urlsplit(url); clean=urllib.parse.urlunsplit((u.scheme,u.netloc,u.path,'','')); ext=Path(urllib.parse.unquote(u.path)).suffix or '.webm'; dst=SRC/(safe(label)+ext)
  ok=False
  for attempt in range(5):
   rr=requests.get(clean,headers={**UA,'Referer':'https://commons.wikimedia.org/'},stream=True,timeout=180)
   if rr.status_code==200:
    with open(dst,'wb') as f:
     for ch in rr.iter_content(1024*1024):
      if ch:f.write(ch)
    ok=True;break
   time.sleep(4*(attempt+1))
  if not ok: raise RuntimeError(f'download HTTP {rr.status_code}')
  md=ii.get('extmetadata',{}); license_name=md.get('LicenseShortName',{}).get('value',''); author=md.get('Artist',{}).get('value',''); desc=md.get('ImageDescription',{}).get('value','')
  m={'title':page.get('title',title),'path':str(dst),'label':label,'purpose':purpose,'commons_page':'https://commons.wikimedia.org/wiki/'+urllib.parse.quote(page.get('title',title).replace(' ','_')),'license':license_name,'author':author,'description':desc,'original_size':sz};m.update(probe(dst));manifest.append(m);sheet(dst,label);print('OK',label,m['title'],m.get('width'),m.get('height'),m.get('duration'),license_name)
  return True
 except Exception as e: errors.append({'title':title,'label':label,'error':repr(e)});print('FAIL',label,title,repr(e));return False

def pick(query,label,purpose,prefer_name=None):
 ts=search(query,30); candidates[label]=ts
 videos=[t for t in ts if re.search(r'\.(webm|ogv|mp4)$',t,re.I)]
 if prefer_name:
  videos.sort(key=lambda t:(prefer_name.lower() not in t.lower(),len(t)))
 for t in videos:
  if download(t,label,purpose):return

# Exact named politician searches.
pick('"Christian Dürr"', 'christian_duerr_new','Christian Dürr / FDP', 'Christian Dürr')
pick('"Marie-Agnes Strack-Zimmermann"', 'strack_zimmermann_new','Marie-Agnes Strack-Zimmermann / FDP', 'Strack-Zimmermann')
pick('"Svenja Hahn"', 'svenja_hahn_new','Svenja Hahn / FDP / Europe', 'Svenja Hahn')
pick('"Martin Hagen" FDP', 'martin_hagen_new','Martin Hagen / FDP', 'Martin Hagen')
pick('"Henning Höne"', 'henning_hoene_new','Henning Höne / FDP', 'Henning Höne')
# Categories often surface clips that search misses.
for cname,label,purpose in [('Videos of Christian Dürr','duerr_category','Christian Dürr / FDP'),('Videos by Fraktion der Freien Demokraten','fdp_fraktion_new','FDP parliamentary group / party footage')]:
 try:
  ts=cat(cname,60); candidates[label]=ts
  for t in ts:
   if not re.search(r'\.(webm|ogv|mp4)$',t,re.I):continue
   if 'Keine Informationen zum MEGALOCKDOWN' in t or 'Christian Lindner' in t:continue
   if download(t,label,purpose):break
 except Exception as e: errors.append({'category':cname,'error':repr(e)})
# One additional FDP-branded video from Commons search, but exclude Lindner old sources.
for q in ['"Fraktion der Freien Demokraten" video','FDP Freie Demokraten video']:
 try:
  ts=search(q,40); candidates['fdp_extra_'+safe(q)]=ts
  for idx,t in enumerate(ts):
   if not re.search(r'\.(webm|ogv|mp4)$',t,re.I):continue
   if 'Lindner' in t or 'MEGALOCKDOWN' in t:continue
   if download(t,'fdp_extra','FDP real footage'):raise StopIteration
 except StopIteration:break
 except Exception as e:errors.append({'query':q,'error':repr(e)})
# Current official FDP 2026 logo package.
try:
 url='https://www.fdp.de/media/8047/download?inline='
 rr=requests.get(url,headers=UA,timeout=60);rr.raise_for_status();(ASSETS/'fdp_logo_print_2026_v1.zip').write_bytes(rr.content)
 with zipfile.ZipFile(io.BytesIO(rr.content)) as z:
  z.extractall(ASSETS/'logo_extracted')
 print('FDP LOGO ZIP OK',len(rr.content))
except Exception as e: errors.append({'logo_zip':'official FDP','error':repr(e)});print('LOGO FAIL',repr(e))
(DOCS/'candidate_titles.json').write_text(json.dumps(candidates,indent=2,ensure_ascii=False));(DOCS/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False));(DOCS/'errors.json').write_text(json.dumps(errors,indent=2,ensure_ascii=False))
print('SUCCESS',len(manifest));print(json.dumps(manifest,indent=2,ensure_ascii=False))
