# EditKick AI Studio
Produktionsnahes MVP für automatische Fußball-Edits direkt im Browser.

## Stack
Next.js, TypeScript, Tailwind, Framer Motion, ffmpeg.wasm, Web Audio API, Canvas API.

## Start
```bash
npm install
npm run dev
```

## Build für Netlify
```bash
npm run build
```
Netlify dient für Hosting/Routing. Rendering läuft lokal im Browser, keine großen Video-Uploads an Functions.

## Funktionsweise
1. Nutzer lädt Video hoch (Hauptpfad) oder nutzt erlaubten direkten MP4-Link.
2. Optional Musikupload.
3. Prompt-Parsing + heuristische Audio/Video-Analyse.
4. Edit-Plan wird erzeugt.
5. ffmpeg.wasm rendert MP4 im Browser.
6. Download lokal als Blob-URL.

## Grenzen & 4K
- 4K kann langsam sein oder fehlschlagen.
- Empfehlung: 1080p für stabile Ergebnisse.
- Sehr große Dateien (>60s) sind im Browser kritisch.
- Browser-Optimierung statt echtem KI-Upscaling (MVP ehrlich benannt).

## Rechtliches
Bitte nur Inhalte mit eigenen Rechten/Bearbeitungsfreigabe nutzen.
YouTube/ZTube wird im MVP nicht illegal heruntergeladen.

## Erweiterungen
- Externer Render-Worker für schwere Jobs
- Echtes AI-Upscaling
- YouTube API + Rechteprüfung
- Bessere KI-Highlight-Erkennung

## Troubleshooting
- Wenn FFmpeg nicht lädt: Browser neu starten, Cache leeren, HTTPS prüfen.
- Wenn Rendern scheitert: kürzere Clips, 720p/1080p, weniger Effekte, ohne Upscaling.

## Browser-Kompatibilität
Empfohlen: aktuelle Chromium-Browser. Firefox/Safari je nach SharedArrayBuffer/COOP/COEP eingeschränkt.
