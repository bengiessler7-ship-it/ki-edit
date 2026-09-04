#!/usr/bin/env bash
set -euo pipefail

OUTDIR="${GITHUB_WORKSPACE:-$PWD}/eu-render-v4"
mkdir -p "$OUTDIR/segments" "$OUTDIR/assets"
cd "$OUTDIR"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"

# 25 real stock-video sources. First 7: dark / waste / urban decay.
# Remaining 18: money / finance / luxury / business / infrastructure / technology.
URLS=(
"https://www.pexels.com/download/video/28827630/"
"https://www.pexels.com/download/video/4279368/"
"https://www.pexels.com/download/video/35039895/"
"https://www.pexels.com/download/video/11296534/"
"https://www.pexels.com/download/video/19676495/"
"https://www.pexels.com/download/video/12077148/"
"https://www.pexels.com/download/video/4876785/"
"https://www.pexels.com/download/video/856511/"
"https://www.pexels.com/download/video/31402662/"
"https://www.pexels.com/download/video/7579943/"
"https://www.pexels.com/download/video/27635978/"
"https://www.pexels.com/download/video/34233368/"
"https://www.pexels.com/download/video/35426470/"
"https://www.pexels.com/download/video/34867905/"
"https://www.pexels.com/download/video/35605168/"
"https://www.pexels.com/download/video/17477319/"
"https://www.pexels.com/download/video/36366350/"
"https://www.pexels.com/download/video/31401966/"
"https://videos.pexels.com/video-files/34755021/14733313_1920_1080_25fps.mp4"
"https://videos.pexels.com/video-files/28050063/12291285_7680_4320_24fps.mp4"
"https://videos.pexels.com/video-files/32386529/13814863_3840_2160_100fps.mp4"
"https://videos.pexels.com/video-files/32386600/13814711_3840_2160_100fps.mp4"
"https://videos.pexels.com/video-files/5752849/5752849-uhd_3840_2160_30fps.mp4"
"https://videos.pexels.com/video-files/4733980/4733980-uhd_3840_2160_30fps.mp4"
"https://videos.pexels.com/video-files/12329724/12329724-uhd_3840_2160_25fps.mp4"
)

# 429 frames = 14.300 seconds at 30fps. Drop at 184/30 = 6.133s.
FRAMES=(35 27 23 19 17 16 47 12 12 12 12 12 12 12 12 12 12 12 12 12 12 12 12 26 27)
STARTS=(0.20 0.25 0.35 0.45 0.40 0.35 0.25 0.20 0.40 0.30 0.50 0.35 0.40 0.30 0.35 0.50 0.35 0.40 0.50 0.50 0.40 0.40 0.30 0.45 0.40)

fetch_source() {
  local n="$1" url="$2"
  if [[ "$url" == *"www.pexels.com/download/video/"* ]]; then
    local f
    f=$(printf "assets/src_%02d.mp4" "$n")
    echo "Downloading source $n" >&2
    curl -L --fail --retry 3 --retry-delay 1 -A "$UA" "$url" -o "$f" >&2
    echo "$f"
  else
    echo "$url"
  fi
}

for i in $(seq 1 25); do
  idx=$((i-1))
  out=$(printf "segments/%02d.mp4" "$i")
  src=$(fetch_source "$i" "${URLS[$idx]}")
  ss="${STARTS[$idx]}"
  frames="${FRAMES[$idx]}"

  # Slightly different camera movement per shot.
  phase=$((i%4))
  case "$phase" in
    0) pan="x='(in_w-out_w)/2+24*sin(n/8)':y='(in_h-out_h)/2+16*cos(n/10)'";;
    1) pan="x='(in_w-out_w)/2+20*cos(n/7)':y='(in_h-out_h)/2+18*sin(n/8)'";;
    2) pan="x='(in_w-out_w)/2-22*sin(n/9)':y='(in_h-out_h)/2+15*cos(n/7)'";;
    3) pan="x='(in_w-out_w)/2+18*cos(n/6)':y='(in_h-out_h)/2-18*sin(n/10)'";;
  esac

  if [[ "$i" -le 7 ]]; then
    vf="scale=1200:1200:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1080:${pan},fps=30,eq=contrast=1.26:brightness=-0.095:saturation=0.56:gamma=0.92,colorbalance=bs=.055:rs=-.030,vignette=PI/5,unsharp=5:5:.38:5:5:0,noise=alls=1.7:allf=t,format=yuv420p"
  else
    vf="scale=1260:1260:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1080:${pan},setpts=0.88*PTS,fps=30,eq=contrast=1.16:brightness=.045:saturation=1.27:gamma=1.03,colorbalance=rs=.035:gs=.006:bs=-.004,unsharp=5:5:.46:5:5:0,noise=alls=.8:allf=t,format=yuv420p"
  fi

  echo "Rendering shot $i/25" >&2
  if [[ "$src" == http* ]]; then
    ffmpeg -y -hide_banner -loglevel warning -rw_timeout 60000000 -user_agent "$UA" -ss "$ss" -i "$src" -an -vf "$vf" -frames:v "$frames" -c:v libx264 -preset veryfast -crf 17 -pix_fmt yuv420p "$out"
  else
    ffmpeg -y -hide_banner -loglevel warning -ss "$ss" -i "$src" -an -vf "$vf" -frames:v "$frames" -c:v libx264 -preset veryfast -crf 17 -pix_fmt yuv420p "$out"
  fi

done

: > concat.txt
for i in $(seq -w 1 25); do echo "file 'segments/${i}.mp4'" >> concat.txt; done
ffmpeg -y -hide_banner -loglevel warning -f concat -safe 0 -i concat.txt -c copy background_v4.mp4
ffprobe -v error -show_entries stream=width,height,r_frame_rate,nb_frames -show_entries format=duration,size -of json background_v4.mp4 > render_probe.json
sha256sum background_v4.mp4 > SHA256SUMS.txt

echo "DONE: $OUTDIR/background_v4.mp4"