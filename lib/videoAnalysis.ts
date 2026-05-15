import { FrameSample, VideoAnalysis } from './types';

export async function loadVideoMetadata(file: File): Promise<{ duration: number; width: number; height: number }> {
  const url = URL.createObjectURL(file);
  const video = document.createElement('video');
  video.src = url;
  await video.play().catch(() => undefined);
  await new Promise((resolve) => (video.onloadedmetadata = resolve));
  return { duration: video.duration, width: video.videoWidth, height: video.videoHeight };
}

export async function sampleVideoFrames(video: HTMLVideoElement, interval = 0.5): Promise<FrameSample[]> {
  const c = document.createElement('canvas'); c.width = 320; c.height = 180; const ctx = c.getContext('2d')!;
  const frames: FrameSample[] = [];
  for (let t = 0; t < video.duration; t += interval) {
    video.currentTime = t; await new Promise((r) => (video.onseeked = r)); ctx.drawImage(video, 0, 0, c.width, c.height); frames.push({ time: t, data: ctx.getImageData(0, 0, c.width, c.height) });
  }
  return frames;
}

const diff = (a: ImageData, b: ImageData) => { let d = 0; for (let i = 0; i < a.data.length; i += 16) d += Math.abs(a.data[i] - b.data[i]); return d / (a.data.length / 16); };
export function detectSceneChanges(frames: FrameSample[]): number[] { const out: number[] = []; for (let i = 1; i < frames.length; i++) if (diff(frames[i - 1].data, frames[i].data) > 20) out.push(frames[i].time); return out; }
export function detectMotionIntensity(frames: FrameSample[]) { return frames.slice(1).map((f, i) => ({ time: f.time, score: diff(frames[i].data, f.data) })); }
export function findHighlightMoments(videoAnalysis: VideoAnalysis, targetDuration: number): number[] { return videoAnalysis.motionScores.sort((a,b)=>b.score-a.score).slice(0, Math.ceil(targetDuration/2)).map((m)=>m.time).sort((a,b)=>a-b); }
export function createClipSelection(highlights: number[], beatTimeline: {time:number}[], duration: number) { return highlights.slice(0, Math.max(1, Math.floor(duration/2))).map((h,i)=>({ videoStart: Math.max(0,h-0.7), videoEnd: h+1.2, speed: beatTimeline[i]?1.05:1, effects: ['zoom'], caption: i%3===0?'GOAL!':undefined })); }
