#!/usr/bin/env bash
set -euo pipefail

OUTDIR="${GITHUB_WORKSPACE:-$PWD}/eu-render"
mkdir -p "$OUTDIR/segments"
cd "$OUTDIR"

# Real, publicly available Pexels MP4 sources. No generated background footage.
URLS=(
"https://videos.pexels.com/video-files/29554995/12721896_1920_1080_30fps.mp4"
"https://videos.pexels.com/video-files/7054942/7054942-uhd_3840_2160_24fps.mp4"
"https://videos.pexels.com/video-files/36902059/15632214_3840_2160_25fps.mp4"
"https://videos.pexels.com/video-files/3105293/3105293-uhd_3840_2160_30fps.mp4"
"https://videos.pexels.com/video-files/7640090/7640090-hd_1920_1080_25fps.mp4"
"https://videos.pexels.com/video-files/34900372/14784771_1920_1080_24fps.mp4"
"https://videos.pexels.com/video-files/5750736/5750736-hd_1920_1080_30fps.mp4"
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
"https://videos.pexels.com/video-files/35084458/14863052_1080_1920_30fps.mp4"
"https://videos.pexels.com/video-files/12329724/12329724-uhd_3840_2160_25fps.mp4"
)

# Frame-accurate shot lengths at 30fps. Total: 429 frames = 14.300 s.
FRAMES=(35 27 23 19 17 16 47 12 12 12 12 12 12 12 12 12 12 12 12 12 12 12 12 26 27)
STARTS=(0.15 0.70 0.50 0.60 0.30 0.20 0.40 0.50 0.50 0.30 0.50 0.50 0.50 0.40 0.40 0.30 0.30 0.50 0.40 0.30 0.30 0.50 0.30 0.30 0.40)

FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"

make_segment() {
  local n="$1" url="$2" frames="$3" ss="$4" mood="$5"
  local out
  out=$(printf "segments/%02d.mp4" "$n")
  local grade
  if [[ "$mood" == "serious" ]]; then
    grade="eq=contrast=1.14:brightness=-0.045:saturation=0.82:gamma=0.98,colorbalance=bs=.025:rs=-.012"
  else
    grade="eq=contrast=1.10:brightness=0.025:saturation=1.14:gamma=1.01,colorbalance=rs=.018:bs=.012"
  fi

  ffmpeg -y -hide_banner -loglevel warning \
    -rw_timeout 60000000 -user_agent "$UA" -ss "$ss" -i "$url" \
    -an -vf "scale=1080:1080:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1080,fps=30,$grade,unsharp=5:5:0.28:5:5:0.0,format=yuv420p" \
    -frames:v "$frames" -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p -movflags +faststart "$out"
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

FILTER="
[0:v]
  drawbox=x=80:y=420:w=920:h=240:color=black@0.94:t=fill:enable='between(t,4.933,5.367)',
  drawtext=fontfile=${FONT}:text='SWITCH!':fontcolor=0xFF2D6F:fontsize=132:borderw=3:bordercolor=0xFF2D6F:x=(w-text_w)/2:y=462:enable='between(t,4.933,5.367)',
  drawbox=x=0:y=0:w=iw:h=ih:color=white@0.38:t=fill:enable='between(t,5.300,5.333)',
  drawtext=fontfile=${FONT}:text='EUROPE':fontcolor=white:fontsize=180:borderw=8:bordercolor=0x102A56:shadowcolor=black@0.65:shadowx=8:shadowy=10:x=(w-text_w)/2:y='if(lt(t,6.000),1080-(t-5.400)*(660/0.600),420)':enable='between(t,5.400,6.133)',
  drawbox=x=0:y=0:w=iw:h=ih:color=white@0.50:t=fill:enable='between(t,6.133,6.167)',
  drawtext=fontfile=${FONT}:text='EUROPE':fontcolor=white:fontsize=170:borderw=7:bordercolor=0x102A56:shadowcolor=black@0.6:shadowx=7:shadowy=9:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,6.133,6.533)',
  drawtext=fontfile=${FONT}:text='EUROPE':fontcolor=white:fontsize=132:borderw=6:bordercolor=0x102A56:shadowcolor=black@0.6:shadowx=6:shadowy=8:x=110:y=105:enable='between(t,6.533,6.933)',
  drawtext=fontfile=${FONT}:text='EUROPE':fontcolor=white:fontsize=100:borderw=5:bordercolor=0x102A56:shadowcolor=black@0.6:shadowx=5:shadowy=7:x=85:y=75:enable='between(t,6.933,7.333)',
  drawtext=fontfile=${FONT}:text='EUROPE':fontcolor=white:fontsize=72:borderw=4:bordercolor=0x102A56:shadowcolor=black@0.55:shadowx=4:shadowy=6:x=62:y=58:enable='between(t,7.333,8.933)',
  drawbox=x=0:y=0:w=iw:h=ih:color=white@0.42:t=fill:enable='between(t,10.133,10.167)',
  drawtext=fontfile=${FONT}:text='EUROPE IN MOTION':fontcolor=0x101010:fontsize=105:box=1:boxcolor=white@0.96:boxborderw=28:borderw=3:bordercolor=0xFFFFFF:shadowcolor=black@0.55:shadowx=10:shadowy=12:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,10.133,10.533)',
  drawtext=fontfile=${FONT}:text='EUROPE IN MOTION':fontcolor=0x101010:fontsize=82:box=1:boxcolor=white@0.96:boxborderw=22:shadowcolor=black@0.50:shadowx=8:shadowy=10:x=95:y=110:enable='between(t,10.533,10.933)',
  drawtext=fontfile=${FONT}:text='EUROPE IN MOTION':fontcolor=0x101010:fontsize=60:box=1:boxcolor=white@0.95:boxborderw=18:shadowcolor=black@0.48:shadowx=7:shadowy=8:x=70:y=78:enable='between(t,10.933,11.333)',
  drawtext=fontfile=${FONT}:text='EUROPE IN MOTION':fontcolor=0x101010:fontsize=42:box=1:boxcolor=white@0.94:boxborderw=13:shadowcolor=black@0.45:shadowx=5:shadowy=6:x=45:y=48:enable='between(t,11.333,13.600)',
  noise=alls=2.0:allf=t,
  format=yuv420p[v]
"

ffmpeg -y -hide_banner -loglevel warning -i background_real_footage.mp4 \
  -filter_complex "$FILTER" -map '[v]' -an -r 30 -frames:v 429 \
  -c:v libx264 -preset medium -crf 17 -pix_fmt yuv420p -movflags +faststart \
  EU_REAL_FOOTAGE_NEUTRAL_VIDEO_ONLY.mp4

ffprobe -v error -show_entries stream=width,height,r_frame_rate,nb_frames -show_entries format=duration,size -of json EU_REAL_FOOTAGE_NEUTRAL_VIDEO_ONLY.mp4 > render_probe.json
sha256sum EU_REAL_FOOTAGE_NEUTRAL_VIDEO_ONLY.mp4 > SHA256SUMS.txt

echo "DONE: $OUTDIR/EU_REAL_FOOTAGE_NEUTRAL_VIDEO_ONLY.mp4"
