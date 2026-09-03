#!/usr/bin/env bash
set -euo pipefail

OUTDIR="${GITHUB_WORKSPACE:-$PWD}/eu-render"
mkdir -p "$OUTDIR/segments" "$OUTDIR/assets"
cd "$OUTDIR"

# Current official FDP 2026 logo presentation from the FDP corporate-design page.
FDP_LOGO_URL="https://www.fdp.de/sites/default/files/styles/image/public/2026-06/cd_logo.png?itok=3LTtHCuz"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"
curl -L --fail --retry 3 -A "$UA" "$FDP_LOGO_URL" -o assets/fdp_official_2026.png

# Real stock footage. The first phase is intentionally free of animation/overlays
# until the MOGGED moment. No generated background footage is used.
URLS=(
"https://www.pexels.com/download/video/28827630/"
"https://www.pexels.com/download/video/17727248/"
"https://videos.pexels.com/video-files/36902059/15632214_3840_2160_25fps.mp4"
"https://videos.pexels.com/video-files/3105293/3105293-uhd_3840_2160_30fps.mp4"
"https://videos.pexels.com/video-files/7640090/7640090-hd_1920_1080_25fps.mp4"
"https://videos.pexels.com/video-files/29554995/12721896_1920_1080_30fps.mp4"
"https://videos.pexels.com/video-files/5750736/5750736-hd_1920_1080_30fps.mp4"
"https://videos.pexels.com/video-files/34900372/14784771_1920_1080_24fps.mp4"
"https://videos.pexels.com/video-files/19780830/19780830-uhd_3840_2160_24fps.mp4"
"https://videos.pexels.com/video-files/34948069/14804256_3840_2160_60fps.mp4"
"https://videos.pexels.com/video-files/4766692/4766692-hd_1280_720_25fps.mp4"
"https://videos.pexels.com/video-files/34141861/14475984_3840_2160_24fps.mp4"
"https://videos.pexels.com/video-files/33275316/14174837_3840_2160_24fps.mp4"
"https://videos.pexels.com/video-files/34755021/14733313_1920_1080_25fps.mp4"
"https://videos.pexels.com/video-files/32386529/13814863_3840_2160_100fps.mp4"
"https://videos.pexels.com/video-files/32386600/13814711_3840_2160_100fps.mp4"
"https://videos.pexels.com/video-files/5752849/5752849-uhd_3840_2160_30fps.mp4"
"https://videos.pexels.com/video-files/8534097/8534097-uhd_3840_2160_30fps.mp4"
"https://videos.pexels.com/video-files/1276083/1276083-hd_1280_720_30fps.mp4"
"https://videos.pexels.com/video-files/4733980/4733980-uhd_3840_2160_30fps.mp4"
"https://videos.pexels.com/video-files/12283404/12283404-uhd_3840_2160_25fps.mp4"
"https://videos.pexels.com/video-files/8632602/8632602-uhd_3840_2160_25fps.mp4"
"https://videos.pexels.com/video-files/28050063/12291285_7680_4320_24fps.mp4"
"https://videos.pexels.com/video-files/7969378/7969378-uhd_2160_3840_30fps.mp4"
"https://videos.pexels.com/video-files/12329724/12329724-uhd_3840_2160_25fps.mp4"
)

# 429 frames = 14.300 seconds at 30 fps. First seven shots end at frame 184 = 6.133 s.
FRAMES=(35 27 23 19 17 16 47 12 12 12 12 12 12 12 12 12 12 12 12 12 12 12 12 26 27)
STARTS=(0.20 0.30 0.50 0.60 0.30 0.15 0.40 0.20 0.50 0.50 0.30 0.50 0.50 0.50 0.40 0.40 0.30 0.30 0.50 0.40 0.30 0.30 0.50 0.30 0.40)
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

make_segment() {
  local n="$1" url="$2" frames="$3" ss="$4" mood="$5"
  local out source tmp=""
  out=$(printf "segments/%02d.mp4" "$n")
  source="$url"

  if [[ "$url" == *"pexels.com/download/video/"* ]]; then
    tmp=$(printf "segments/source_%02d.mp4" "$n")
    echo "Downloading real-footage source $n"
    curl -L --fail --retry 3 -A "$UA" "$url" -o "$tmp"
    source="$tmp"
  fi

  local grade
  if [[ "$mood" == "serious" ]]; then
    grade="eq=contrast=1.17:brightness=-0.065:saturation=0.72:gamma=0.96,colorbalance=bs=.035:rs=-.020"
  else
    grade="eq=contrast=1.11:brightness=0.035:saturation=1.18:gamma=1.02,colorbalance=rs=.022:bs=.008"
  fi

  if [[ -n "$tmp" ]]; then
    ffmpeg -y -hide_banner -loglevel warning \
      -ss "$ss" -i "$source" \
      -an -vf "scale=1080:1080:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1080,fps=30,$grade,unsharp=5:5:0.30:5:5:0.0,format=yuv420p" \
      -frames:v "$frames" -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p -movflags +faststart "$out"
  else
    ffmpeg -y -hide_banner -loglevel warning \
      -rw_timeout 60000000 -user_agent "$UA" -ss "$ss" -i "$source" \
      -an -vf "scale=1080:1080:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1080,fps=30,$grade,unsharp=5:5:0.30:5:5:0.0,format=yuv420p" \
      -frames:v "$frames" -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p -movflags +faststart "$out"
  fi

  [[ -n "$tmp" ]] && rm -f "$tmp"
}

for i in $(seq 1 25); do
  idx=$((i-1))
  mood="positive"
  [[ "$i" -le 7 ]] && mood="serious"
  echo "Rendering real-footage shot $i/25 (${FRAMES[$idx]} frames)"
  make_segment "$i" "${URLS[$idx]}" "${FRAMES[$idx]}" "${STARTS[$idx]}" "$mood"
done

: > concat.txt
for i in $(seq -w 1 25); do echo "file 'segments/${i}.mp4'" >> concat.txt; done
ffmpeg -y -hide_banner -loglevel warning -f concat -safe 0 -i concat.txt -c copy background_real_footage.mp4

# MOGGED timing follows the measured reference moment. The opening is untouched before 4.933 s.
# The FDP logo then rises from below, overshoots slightly, settles, shrinks toward top-left,
# rotates subtly across beats, floats briefly and exits on-beat. No other text is added.
FILTER="
[0:v]
  drawbox=x=80:y=420:w=920:h=240:color=black@0.94:t=fill:enable='between(t,4.933,5.367)',
  drawtext=fontfile=${FONT}:text='MOGGED!':fontcolor=0xFF2D6F:fontsize=132:borderw=3:bordercolor=0xFF2D6F:x=(w-text_w)/2:y=462:enable='between(t,4.933,5.367)',
  drawbox=x=0:y=0:w=iw:h=ih:color=white@0.40:t=fill:enable='between(t,5.300,5.333)',
  format=rgba[base];

[1:v]format=rgba,split=8[lr][l100][l80][l60][l45][l30][lp][le];
[lr]scale=720:-1[lr_s];
[l100]scale=720:-1,rotate=0:c=none:ow=rotw(iw):oh=roth(ih)[l100_s];
[l80]scale=576:-1,rotate=6*PI/180:c=none:ow=rotw(iw):oh=roth(ih)[l80_s];
[l60]scale=432:-1,rotate=-4*PI/180:c=none:ow=rotw(iw):oh=roth(ih)[l60_s];
[l45]scale=324:-1,rotate=3*PI/180:c=none:ow=rotw(iw):oh=roth(ih)[l45_s];
[l30]scale=216:-1,rotate=2*PI/180:c=none:ow=rotw(iw):oh=roth(ih)[l30_s];
[lp]scale=238:-1,rotate=-3*PI/180:c=none:ow=rotw(iw):oh=roth(ih)[lp_s];
[le]scale=120:-1,rotate=7*PI/180:c=none:ow=rotw(iw):oh=roth(ih)[le_s];

[base][lr_s]overlay=x='(W-w)/2':y='if(lt(t,5.950),H-(t-5.400)*((H-h)/0.550),if(lt(t,6.050),(H-h)/2-18+(t-5.950)*180,(H-h)/2))':enable='between(t,5.400,6.133)'[v1];
[v1][l100_s]overlay=x='(W-w)/2':y='(H-h)/2':enable='between(t,6.133,6.533)'[v2];
[v2][l80_s]overlay=x=185:y=210:enable='between(t,6.533,6.933)'[v3];
[v3][l60_s]overlay=x=105:y=115:enable='between(t,6.933,7.333)'[v4];
[v4][l45_s]overlay=x=65:y=68:enable='between(t,7.333,7.733)'[v5];
[v5][l30_s]overlay=x='48+5*sin(t*2.0)':y='48+4*cos(t*1.7)':enable='between(t,7.733,8.933)'[v6];
[v6][lp_s]overlay=x=43:y=43:enable='between(t,8.933,9.033)'[v7];
[v7][le_s]overlay=x=58:y=58:enable='between(t,9.033,9.133)'[v8];
[v8]noise=alls=2.0:allf=t,format=yuv420p[v]
"

ffmpeg -y -hide_banner -loglevel warning \
  -i background_real_footage.mp4 -loop 1 -framerate 30 -i assets/fdp_official_2026.png \
  -filter_complex "$FILTER" -map '[v]' -an -r 30 -frames:v 429 \
  -c:v libx264 -preset medium -crf 17 -pix_fmt yuv420p -movflags +faststart \
  EU_REAL_FOOTAGE_NEUTRAL_VIDEO_ONLY.mp4

ffprobe -v error -show_entries stream=width,height,r_frame_rate,nb_frames -show_entries format=duration,size -of json EU_REAL_FOOTAGE_NEUTRAL_VIDEO_ONLY.mp4 > render_probe.json
sha256sum EU_REAL_FOOTAGE_NEUTRAL_VIDEO_ONLY.mp4 > SHA256SUMS.txt

echo "DONE: $OUTDIR/EU_REAL_FOOTAGE_NEUTRAL_VIDEO_ONLY.mp4"
