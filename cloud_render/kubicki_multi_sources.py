import subprocess, json, os, glob
from pathlib import Path

OUT = Path('kubicki_multi')
SRC = OUT/'sources'; SHEETS = OUT/'sheets'
SRC.mkdir(parents=True, exist_ok=True); SHEETS.mkdir(parents=True, exist_ok=True)

sources = [
    ('zdf_interview_2026', 'https://www.zdf.de/video/magazine/phoenix-collection-phoenix-1080805-1610/phoenix-fdp-parteitag-es-wird-keinerlei-zusammenarbeit-mit-der-afd-geben-100', '0-50'),
    ('maischberger_2026', 'https://www.ardmediathek.de/video/maischberger/wolfgang-kubicki-ueber-den-fdp-vorsitz-und-die-ausrichtung-der-partei/wdr/Y3JpZDovL3dkci5kZS9CZWl0cmFnLXNvcGhvcmEtNDk4ZWMxY2UtNDM0MS00ZTU3LWJmNGMtZmUzYTVkMDFlODc4', '0-50'),
    ('ndr_kandidatur_2025', 'https://www.ardmediathek.de/video/schleswig-holstein-magazin/wolfgang-kubicki-kandidatur-als-fdp-chef-statt-rueckzug/ndr/Y3JpZDovL25kci5kZS84ZTNmZjQwYy00Y2ExLTRiMWYtYmY3OS1iNDM2ZDhkM2NmZTg', '0-50'),
    ('ndr_spitzenkandidat_2025', 'https://www.ardmediathek.de/video/schleswig-holstein-magazin/fdp-spitzenkandidat-kubicki-kaempft-um-bundestag-einzug/ndr/Y3JpZDovL25kci5kZS9hZjcyODg4Yy04YWYyLTQ3OWYtOGQ4My0yMjNmNjU1Zjk3NTU', '0-50'),
    ('tagesschau24_2026', 'https://www.ardmediathek.de/video/tagesschau24/kubicki-in-kampfabstimmung-zum-neuen-vorsitzenden-der-fdp-gewaehlt/tagesschau24/Y3JpZDovL3RhZ2Vzc2NoYXUuZGUvNTg5YjU1ZWQtZDA0ZS00NjdhLTlmYWEtODJiOTlhODliZTJl', '0-50'),
    ('ndr_parteivorsitz_2026', 'https://www.ardmediathek.de/video/schleswig-holstein-magazin/fdp-waehlt-kubicki-zum-neuen-parteivorsitzenden/ndr/Y3JpZDovL25kci5kZS8wMmQxMDgwZS05YTkwLTRlN2QtODczOS1iOGExNWRmNDYyNDY', '0-50'),
]

def run(cmd):
    print('+', ' '.join(cmd), flush=True)
    return subprocess.run(cmd, check=True)

manifest=[]
for label,url,section in sources:
    tmpl = str(SRC/f'{label}.%(ext)s')
    try:
        cmd=['yt-dlp','--no-playlist','--no-warnings','--force-keyframes-at-cuts','--download-sections',f'*{section}','--merge-output-format','mp4','-f','bv*[height<=720]+ba/b[height<=720]/best','-o',tmpl,url]
        run(cmd)
        files=glob.glob(str(SRC/f'{label}.*'))
        mp4=next((f for f in files if f.endswith('.mp4')), files[0])
        probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-show_entries','stream=codec_name,width,height,r_frame_rate','-of','json',mp4]))
        # 5x4 contact sheet over 40 sec
        sheet=str(SHEETS/f'{label}.jpg')
        subprocess.run(['ffmpeg','-y','-i',mp4,'-vf','fps=1/2,scale=320:-2,tile=5x4','-frames:v','1',sheet], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        manifest.append({'label':label,'url':url,'file':mp4,'probe':probe})
        print('OK', label, mp4, flush=True)
    except Exception as e:
        manifest.append({'label':label,'url':url,'error':repr(e)})
        print('FAILED', label, repr(e), flush=True)

(OUT/'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
print(json.dumps(manifest, indent=2), flush=True)
