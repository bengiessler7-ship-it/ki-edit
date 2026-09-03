#!/usr/bin/env python3
import os, re, json, math, subprocess, urllib.parse, requests, shutil
from pathlib import Path

OUT=Path('cloud_probe')
SRC=OUT/'sources'; SHEETS=OUT/'sheets'
SRC.mkdir(parents=True, exist_ok=True); SHEETS.mkdir(parents=True, exist_ok=True)
UA={'User-Agent':'FDP-edit-source-probe/1.0 (media research; contact: repository owner)'}
API='https://commons.wikimedia.org/w/api.php'
manifest=[]

def run(cmd, check=True):
    print('+', ' '.join(map(str,cmd)), flush=True)
    return subprocess.run(cmd, check=check)

def safe(s):
    s=re.sub(r'[^A-Za-z0-9._-]+','_',s).strip('_')
    return s[:120] or 'asset'

def commons_info(title):
    if not title.startswith('File:'): title='File:'+title
    r=requests.get(API,params={'action':'query','format':'json','prop':'imageinfo','titles':title,'iiprop':'url|mime|size|extmetadata'},headers=UA,timeout=45)
    r.raise_for_status(); data=r.json()['query']['pages']
    page=next(iter(data.values()))
    ii=page.get('imageinfo',[{}])[0]
    if not ii.get('url'): raise RuntimeError('no url for '+title)
    return {'title':page.get('title',title),'url':ii['url'],'mime':ii.get('mime',''),'width':ii.get('width'),'height':ii.get('height'),'extmetadata':ii.get('extmetadata',{})}

def commons_download(title, label, purpose, required=False):
    try:
        info=commons_info(title)
        ext=Path(urllib.parse.urlparse(info['url']).path).suffix or '.webm'
        dst=SRC/(safe(label)+ext)
        with requests.get(info['url'],headers=UA,stream=True,timeout=120) as rr:
            rr.raise_for_status()
            with open(dst,'wb') as f:
                for ch in rr.iter_content(1024*1024):
                    if ch: f.write(ch)
        info.update({'path':str(dst),'label':label,'purpose':purpose,'source_type':'Wikimedia Commons'})
        manifest.append(info); print('DOWNLOADED',dst,dst.stat().st_size)
        return dst
    except Exception as e:
        print('COMMONS FAILED',title,repr(e))
        if required: raise
        return None

def category_videos(cat, limit=8):
    r=requests.get(API,params={'action':'query','format':'json','list':'categorymembers','cmtitle':'Category:'+cat,'cmnamespace':6,'cmlimit':limit},headers=UA,timeout=45)
    r.raise_for_status(); return [x['title'] for x in r.json()['query']['categorymembers']]

def search_videos(q, limit=6):
    r=requests.get(API,params={'action':'query','format':'json','list':'search','srnamespace':6,'srlimit':limit*3,'srsearch':q},headers=UA,timeout=45)
    r.raise_for_status(); out=[]
    for x in r.json()['query']['search']:
        t=x['title']
        if re.search(r'\.(webm|ogv|mp4)$',t,re.I): out.append(t)
        if len(out)>=limit: break
    return out

def ytdlp(url,label,purpose):
    dst=SRC/(safe(label)+'.%(ext)s')
    cmd=['yt-dlp','--no-playlist','--no-warnings','--merge-output-format','mp4','-f','bv*[height<=2160]+ba/b[height<=2160]/best','-o',str(dst),url]
    try:
        run(cmd)
        found=sorted(SRC.glob(safe(label)+'.*'))
        found=[p for p in found if p.suffix.lower() in {'.mp4','.webm','.mkv','.mov'}]
        if not found: raise RuntimeError('yt-dlp produced no media')
        p=found[0]
        manifest.append({'title':label,'url':url,'path':str(p),'label':label,'purpose':purpose,'source_type':'official public media page'})
        return p
    except Exception as e:
        print('YTDLP FAILED',url,repr(e)); return None

def duration(p):
    try:
        x=subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nk=1:nw=1',str(p)],text=True).strip()
        return float(x)
    except: return 0

def sheet(p,label,n=12):
    d=duration(p)
    if d<=0: return None
    times=[max(0,min(d-0.05,(i+0.5)*d/n)) for i in range(n)]
    imgs=[]
    for i,t in enumerate(times):
        q=SHEETS/f'{safe(label)}_{i:02d}.jpg'
        subprocess.run(['ffmpeg','-y','-ss',f'{t:.3f}','-i',str(p),'-frames:v','1','-vf','scale=480:-2','-q:v','3',str(q)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        if q.exists(): imgs.append(q)
    if not imgs: return None
    from PIL import Image,ImageDraw
    opened=[Image.open(q).convert('RGB') for q in imgs]
    W=480; H=max(im.height for im in opened); rows=math.ceil(len(opened)/4)
    canvas=Image.new('RGB',(W*4,H*rows),(15,15,15)); draw=ImageDraw.Draw(canvas)
    for idx,(im,t) in enumerate(zip(opened,times)):
        x=(idx%4)*W; y=(idx//4)*H
        if im.height!=H: im=im.resize((W,H))
        canvas.paste(im,(x,y)); draw.rectangle((x,y,x+100,y+24),fill=(0,0,0)); draw.text((x+5,y+4),f'{t:.1f}s',fill=(255,255,255))
    canvas.save(SHEETS/f'{safe(label)}_CONTACT.jpg',quality=88)

commons_download('Sexismusdebatte in Deutschland - Anke Domscheit-Berg im Interview - YouTube.webm','kubicki_interview_ccby3','Wolfgang Kubicki real footage',required=True)

exclude={'File:Keine Informationen zum MEGALOCKDOWN für die Öffentlichkeit.webm'}
for t in category_videos('Videos by Fraktion der Freien Demokraten',limit=20):
    if t in exclude or 'Lindner' in t: continue
    if any(k in t for k in ['Freiheit hat viele Gesichter','Ukraine muss sich verteidigen','wirtschaftlichen Beziehungen zu Russland','Wir schaffen weitere Entlastungen']):
        commons_download(t,'fdp_'+Path(t[5:]).stem,'FDP/Fraktion event and politician footage')

try:
    for i,t in enumerate(category_videos('Videos of Christian Dürr',limit=10)):
        commons_download(t,f'christian_duerr_{i+1}','Christian Dürr real footage')
except Exception as e: print('DUERR CATEGORY FAILED',repr(e))

ytdlp('https://multimedia.europarl.europa.eu/en/video/the-future-of-the-european-defence-opening-statement-by-marie-agnes-strack-zimmermann-chair-of-sede-committee_I281575','strack_zimmermann_europarl','Marie-Agnes Strack-Zimmermann / European Parliament')

commons_download('(20260502 173648155) ICE train passing by Bitterfeld.webm','ice_bitterfeld_2026','Germany / mobility / ICE')
for t in category_videos('Videos of ICE',limit=40):
    if any(k in t for k in ['ICE at Elten 075033','Intercity express running through Elten135153','ICE Neumarkt im Oberpfalz 100956']):
        commons_download(t,'ice4k_'+Path(t[5:]).stem,'Germany / mobility / 4K ICE')
        break

for label,query in [('berlin','Berlin Reichstag video'),('eu_flags','European Parliament flags Brussels video'),('technology','Germany technology server data center video')]:
    try:
        titles=search_videos(query,limit=2)
        if titles: commons_download(titles[0],label+'_'+Path(titles[0][5:]).stem,label.replace('_',' '))
    except Exception as e: print('SEARCH FAILED',label,repr(e))

for m in manifest:
    p=Path(m['path']); m['duration']=duration(p)
    try:
        pr=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,codec_name','-of','json',str(p)],text=True))
        if pr.get('streams'): m['video_probe']=pr['streams'][0]
    except: pass
    sheet(p,m['label'])

(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False))
print(json.dumps(manifest,indent=2,ensure_ascii=False))
