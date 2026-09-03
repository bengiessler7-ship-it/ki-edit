#!/usr/bin/env python3
import requests,urllib.parse,time
from pathlib import Path
api='https://commons.wikimedia.org/w/api.php'; title='File:Berlin Funkturm 2026-04-01.webm'; out=Path('berlin_asset');out.mkdir(exist_ok=True)
r=requests.get(api,params={'action':'query','format':'json','prop':'imageinfo','titles':title,'iiprop':'url|extmetadata'},headers={'User-Agent':'Mozilla/5.0 FDP-edit/1.0'},timeout=30);r.raise_for_status();page=next(iter(r.json()['query']['pages'].values()));ii=page['imageinfo'][0];u=urllib.parse.urlsplit(ii['url']);url=urllib.parse.urlunsplit((u.scheme,u.netloc,u.path,'',''))
for n in range(5):
 q=requests.get(url,headers={'User-Agent':'Mozilla/5.0','Referer':'https://commons.wikimedia.org/'},stream=True,timeout=120)
 if q.status_code==200:
  with open(out/'berlin-funkturm-2026.webm','wb') as f:
   for c in q.iter_content(1024*1024):
    if c:f.write(c)
  break
 time.sleep(3*(n+1))
else: raise SystemExit('download failed')
(out/'source.txt').write_text('https://commons.wikimedia.org/wiki/File:Berlin_Funkturm_2026-04-01.webm\n')
print('ok', (out/'berlin-funkturm-2026.webm').stat().st_size)
