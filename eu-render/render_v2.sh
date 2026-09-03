#!/usr/bin/env bash
set -euo pipefail
OUTDIR="${GITHUB_WORKSPACE:-$PWD}/eu-render-v2"
mkdir -p "$OUTDIR/segments" "$OUTDIR/assets"
cd "$OUTDIR"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FDP_LOGO_URL="https://www.fdp.de/sites/default/files/styles/image/public/2026-06/cd_logo.png?itok=3LTtHCuz"
curl -L --fail --retry 3 -A "$UA" "$FDP_LOGO_URL" -o assets/fdp.png

URLS=(
"https://www.pexels.com/download/video/36842336/"
"https://videos.pexels.com/video-files/3105293/3105293-uhd_3840_2160_30fps.mp4"
"https://videos.pexels.com/video-files/29554995/12721896_1920_1080_30fps.mp4"
"https://videos.pexels.com/video-files/7640090/7640090-hd_1920_1080_25fps.mp4"
"https://www.pexels.com/download/video/34653156/"
"https://www.pexels.com/download/video/6171342/"
"https://www.pexels.com/download/video/37552289/"
"https://www.pexels.com/download/video/33438476/"
"https://videos.pexels.com/video-files/34141861/14475984_3840_2160_24fps.mp4"
"https://videos.pexels.com/video-files/33275316/14174837_3840_2160_24fps.mp4"
"https://videos.pexels.com/video-files/19780830/19780830-uhd_3840_2160_24fps.mp4"
"https://videos.pexels.com/video-files/34755021/14733313_1920_1080_25fps.mp4"
"https://videos.pexels.com/video-files/28050063/12291285_7680_4320_24fps.mp4"
"https://videos.pexels.com/video-files/32386529/13814863_3840_2160_100fps.mp4"
"https://videos.pexels.com/video-files/32386600/13814711_3840_2160_100fps.mp4"
"https://videos.pexels.com/video-files/5752849/5752849-uhd_3840_2160_30fps.mp4"
"https://videos.pexels.com/video-files/8534097/8534097-uhd_3840_2160_30fps.mp4"
"https://videos.pexels.com/video-files/1276083/1276083-hd_1280_720_30fps.mp4"
"https://videos.pexels.com/video-files/4733980/4733980-uhd_3840_2160_30fps.mp4"
"https://videos.pexels.com/video-files/12283404/12283404-uhd_3840_2160_25fps.mp4"
"https://videos.pexels.com/video-files/8632602/8632602-uhd_3840_2160_25fps.mp4"
"https://videos.pexels.com/video-files/7969378/7969378-uhd_2160_3840_30fps.mp4"
"https://videos.pexels.com/video-files/4766692/4766692-hd_1280_720_25fps.mp4"
"https://videos.pexels.com/video-files/34948069/14804256_3840_2160_60fps.mp4"
"https://videos.pexels.com/video-files/12329724/12329724-uhd_3840_2160_25fps.mp4"
)
FRAMES=(35 27 23 19 17 16 47 12 12 12 12 12 12 12 12 12 12 12 12 12 12 12 12 26 27)
STARTS=(0.2 0.6 0.15 0.3 0.4 0.8 0.3 0.3 0.5 0.5 0.5 0.5 0.5 0.4 0.4 0.3 0.3 0.5 0.4 0.3 0.3 0.5 0.3 0.5 0.4)

download_if_needed() {
  local n="$1" url="$2"
  if [[ "$url" == *"pexels.com/download/video/"* ]]; then
    local f
    f=$(printf "assets/src_%02d.mp4" "$n")
    curl -L --fail --retry 3 -A "$UA" "$url" -o "$f"
    echo "$f"
  else
    echo "$url"
  fi
}

for i in $(seq 1 25); do
  idx=$((i-1)); out=$(printf "segments/%02d.mp4" "$i")
  src=$(download_if_needed "$i" "${URLS[$idx]}")
  if [[ "$i" -le 7 ]]; then
    vf="scale=1080:1080:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1080,fps=30,eq=contrast=1.20:brightness=-0.075:saturation=0.68:gamma=0.95,colorbalance=bs=.040:rs=-.025,unsharp=5:5:.35:5:5:0,format=yuv420p"
  else
    phase=$((i%4))
    case "$phase" in
      0) pan="x='80+24*sin(n/8)':y='80+14*cos(n/9)'";;
      1) pan="x='80+18*cos(n/7)':y='80+22*sin(n/8)'";;
      2) pan="x='80-20*sin(n/9)':y='80+18*cos(n/7)'";;
      3) pan="x='80+16*cos(n/6)':y='80-20*sin(n/10)'";;
    esac
    vf="scale=1240:1240:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1080:${pan},setpts=0.86*PTS,fps=30,eq=contrast=1.14:brightness=.035:saturation=1.22:gamma=1.02,colorbalance=rs=.025:bs=.006,unsharp=5:5:.42:5:5:0,format=yuv420p"
  fi
  if [[ "$src" == assets/* ]]; then
    ffmpeg -y -hide_banner -loglevel warning -ss "${STARTS[$idx]}" -i "$src" -an -vf "$vf" -frames:v "${FRAMES[$idx]}" -c:v libx264 -preset veryfast -crf 17 -pix_fmt yuv420p "$out"
  else
    ffmpeg -y -hide_banner -loglevel warning -rw_timeout 60000000 -user_agent "$UA" -ss "${STARTS[$idx]}" -i "$src" -an -vf "$vf" -frames:v "${FRAMES[$idx]}" -c:v libx264 -preset veryfast -crf 17 -pix_fmt yuv420p "$out"
  fi
done

: > concat.txt
for i in $(seq -w 1 25); do echo "file 'segments/${i}.mp4'" >> concat.txt; done
ffmpeg -y -hide_banner -loglevel warning -f concat -safe 0 -i concat.txt -c copy background.mp4

FILTER=$(cat <<'FILT'
[0:v]format=rgba[bg];
color=c=black@0.94:s=920x220:r=30:d=0.434,format=rgba,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='MOGGED!':fontcolor=0xFF2D6F:fontsize=132:borderw=2:bordercolor=0xFF2D6F:x=(w-text_w)/2:y=(h-text_h)/2-8,scale=w='920*(1+0.065*exp(-8*t)*sin(30*t))':h='220*(1+0.065*exp(-8*t)*sin(30*t))':eval=frame,setpts=PTS+4.933/TB[mog];
[bg][mog]overlay=x='(W-w)/2+8*sin((t-4.933)*55)*exp(-12*(t-4.933))':y='430+5*cos((t-4.933)*48)*exp(-12*(t-4.933))':enable='between(t,4.933,5.367)'[m1];
[m1]drawbox=x=0:y=0:w=iw:h=ih:color=white@0.55:t=fill:enable='between(t,5.300,5.333)',drawbox=x=0:y=0:w=iw:h=ih:color=white@0.55:t=fill:enable='between(t,6.120,6.165)'[base];
[1:v]format=rgba,setpts=PTS-STARTPTS,scale=w='if(lt(t,6.133),720,if(lt(t,7.733),720-(t-6.133)*315,216))':h=-1:eval=frame,rotate='if(lt(t,6.133),0,if(lt(t,7.733),0.06*sin((t-6.133)*5.2),0.018*sin(t*2.1)))':c=none:ow=rotw(iw):oh=roth(ih),split=2[lg][sh];
[sh]colorchannelmixer=rr=0:gg=0:bb=0:aa=.34,gblur=sigma=16[shadow];
[base][shadow]overlay=x='if(lt(t,6.133),(W-w)/2+15,if(lt(t,7.733),(W-w)/2+(67-(W-w)/2)*(3*pow((t-6.133)/1.6,2)-2*pow((t-6.133)/1.6,3)),67))+7*sin(t*2.0)':y='if(lt(t,6.133),H-(t-5.400)*((H+h/2)/0.733)+14,if(lt(t,7.733),(H-h)/2+(67-(H-h)/2)*(3*pow((t-6.133)/1.6,2)-2*pow((t-6.133)/1.6,3)),67))+5*cos(t*1.8)':enable='between(t,5.400,9.000)'[b2];
[b2][lg]overlay=x='if(lt(t,6.133),(W-w)/2,if(lt(t,7.733),(W-w)/2+(52-(W-w)/2)*(3*pow((t-6.133)/1.6,2)-2*pow((t-6.133)/1.6,3)),52))+7*sin(t*2.0)':y='if(lt(t,6.133),H-(t-5.400)*((H+h/2)/0.733),if(lt(t,7.733),(H-h)/2+(52-(H-h)/2)*(3*pow((t-6.133)/1.6,2)-2*pow((t-6.133)/1.6,3)),52))+5*cos(t*1.8)':enable='between(t,5.400,9.000)'[b3];
[b3]drawbox=x=0:y=0:w=iw:h=ih:color=white@0.30:t=fill:enable='between(t,8.505,8.538)',drawbox=x=0:y=0:w=iw:h=ih:color=white@0.26:t=fill:enable='between(t,10.085,10.118)',drawbox=x=0:y=0:w=iw:h=ih:color=white@0.22:t=fill:enable='between(t,12.450,12.483)',noise=alls=1.2:allf=t,format=yuv420p[v]
FILT
)
ffmpeg -y -hide_banner -loglevel warning -i background.mp4 -loop 1 -framerate 30 -i assets/fdp.png -filter_complex "$FILTER" -map '[v]' -an -r 30 -frames:v 429 -c:v libx264 -preset medium -crf 16 -pix_fmt yuv420p -movflags +faststart EU_EDIT_V2_VIDEO_ONLY.mp4
ffprobe -v error -show_entries stream=width,height,r_frame_rate,nb_frames -show_entries format=duration,size -of json EU_EDIT_V2_VIDEO_ONLY.mp4 > render_probe.json
sha256sum EU_EDIT_V2_VIDEO_ONLY.mp4 > SHA256SUMS.txt
