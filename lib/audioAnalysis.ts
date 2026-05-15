import { AudioAnalysis, Beat } from './types';

export async function loadAudioFile(file: File): Promise<AudioBuffer> {
  const ctx = new AudioContext();
  const arr = await file.arrayBuffer();
  return ctx.decodeAudioData(arr);
}

export function detectEnergyPeaks(audioBuffer: AudioBuffer): number[] {
  const data = audioBuffer.getChannelData(0);
  const sr = audioBuffer.sampleRate;
  const win = Math.floor(sr * 0.05);
  const energies: number[] = [];
  for (let i = 0; i < data.length; i += win) {
    let sum = 0;
    for (let j = i; j < Math.min(i + win, data.length); j++) sum += data[j] * data[j];
    energies.push(Math.sqrt(sum / win));
  }
  const avg = energies.reduce((a, b) => a + b, 0) / Math.max(1, energies.length);
  return energies.map((e, i) => (e > avg * 1.3 ? i * 0.05 : -1)).filter((v) => v >= 0);
}

export function detectBeats(audioBuffer: AudioBuffer): Beat[] { return detectEnergyPeaks(audioBuffer).map((t) => ({ time: t, strength: 1 })); }
export function estimateBPM(beats: Beat[]): number { if (beats.length < 2) return 120; const diffs = beats.slice(1).map((b, i) => b.time - beats[i].time).filter((d) => d > 0.2 && d < 2); const avg = diffs.reduce((a, b) => a + b, 0) / Math.max(1, diffs.length); return Math.round(60 / Math.max(0.3, avg)); }

export function findBestMusicSegment(audioBuffer: AudioBuffer, targetDuration: number) {
  const peaks = detectEnergyPeaks(audioBuffer);
  if (!peaks.length) return { start: 0, end: Math.min(targetDuration, audioBuffer.duration) };
  const start = Math.max(0, peaks[Math.floor(peaks.length * 0.6)] - 1);
  return { start, end: Math.min(start + targetDuration, audioBuffer.duration) };
}

export function createBeatTimeline(beats: Beat[], selectedSegmentStart: number, targetDuration: number): Beat[] {
  return beats.filter((b) => b.time >= selectedSegmentStart && b.time <= selectedSegmentStart + targetDuration).map((b) => ({ ...b, time: b.time - selectedSegmentStart }));
}

export function analyzeAudioBuffer(audioBuffer: AudioBuffer, targetDuration = 15): AudioAnalysis {
  const beats = detectBeats(audioBuffer);
  const segment = findBestMusicSegment(audioBuffer, targetDuration);
  return { duration: audioBuffer.duration, beats, energyPeaks: detectEnergyPeaks(audioBuffer), bpm: estimateBPM(beats), bestSegment: segment, beatTimeline: createBeatTimeline(beats, segment.start, targetDuration) };
}
