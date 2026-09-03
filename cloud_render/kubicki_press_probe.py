#!/usr/bin/env python3
import requests
from pathlib import Path
out=Path('kubicki_press');out.mkdir(exist_ok=True)
url='https://www.fdp.de/sites/default/files/2026-06/wolfgang-kubicki.jpg'
r=requests.get(url,headers={'User-Agent':'Mozilla/5.0'},timeout=120);r.raise_for_status()
(out/'wolfgang-kubicki-fdp-2026.jpg').write_bytes(r.content)
print('downloaded',len(r.content),'bytes')
