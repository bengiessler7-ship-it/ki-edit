import { FFmpeg } from '@ffmpeg/ffmpeg';
import { fetchFile } from '@ffmpeg/util';
import { EditPlan, EnhancementOptions, OutputFormat, Resolution } from './types';
import { RESOLUTION_MAP } from './constants';

let ffmpeg: FFmpeg | null = null;
export async function initFFmpeg(onProgress?: (progress:number)=>void) {
  if (!ffmpeg) ffmpeg = new FFmpeg();
  if (!ffmpeg.loaded) {
    ffmpeg.on('progress', ({ progress }) => onProgress?.(Math.round(progress * 100)));
    await ffmpeg.load({ coreURL: 'https://unpkg.com/@ffmpeg/core@0.12.6/dist/umd/ffmpeg-core.js' });
  }
  return ffmpeg;
}

export async function writeInputFiles(videoFile: File, musicFile?: File | null) {
  if (!ffmpeg) throw new Error('FFmpeg nicht initialisiert');
  await ffmpeg.writeFile('input.mp4', await fetchFile(videoFile));
  if (musicFile) await ffmpeg.writeFile('music', await fetchFile(musicFile));
}

export function applyCrop(format: OutputFormat) { return format === '9:16' ? 'crop=in_h*9/16:in_h' : format === '1:1' ? 'crop=min(in_w\,in_h):min(in_w\,in_h)' : 'scale=iw:ih'; }
export function applyResolution(resolution: Resolution, format: OutputFormat) { const { width, height } = RESOLUTION_MAP[format][resolution]; return `scale=${width}:${height}:force_original_aspect_ratio=increase,crop=${width}:${height}`; }
export function applyMusicSegment(segment?: {start:number;end:number}) { return segment ? ['-ss', String(segment.start), '-to', String(segment.end)] : []; }
export function applyCaptions() { return "drawtext=text='GOAL!':fontcolor=white:fontsize=52:x=(w-text_w)/2:y=h*0.15:enable='between(t,1,3)'"; }
export function applyEffects() { return 'eq=contrast=1.1:saturation=1.15'; }
export function applyQualityEnhancement(o: EnhancementOptions) { const filters = ['setsar=1','fps=30']; if (o.sharpen) filters.push('unsharp=5:5:1.0'); if (o.colorBoost) filters.push('eq=saturation=1.2:contrast=1.1'); if (o.denoise) filters.push('hqdn3d=1.5:1.5:6:6'); return filters.join(','); }

export async function renderEditWithFFmpeg(editPlan: EditPlan, enhancementOptions: EnhancementOptions) {
  if (!ffmpeg) throw new Error('FFmpeg nicht initialisiert');
  const base = [applyCrop(editPlan.format), applyResolution(editPlan.resolution, editPlan.format), applyEffects(), applyCaptions(), applyQualityEnhancement(enhancementOptions)].join(',');
  await ffmpeg.exec(['-i','input.mp4', ...applyMusicSegment(editPlan.musicSegment), '-filter:v', base, '-c:v','libx264','-preset','veryfast','-crf','22','-pix_fmt','yuv420p','-c:a','aac','-shortest','output.mp4']);
}

export async function exportMP4() { if (!ffmpeg) throw new Error('FFmpeg nicht initialisiert'); const data = await ffmpeg.readFile('output.mp4'); return new Blob([data], { type: 'video/mp4' }); }
