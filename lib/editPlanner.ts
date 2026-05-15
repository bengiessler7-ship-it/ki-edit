import { EditPlan, OutputFormat, Resolution, VideoAnalysis, AudioAnalysis, EnhancementOptions } from './types';
import { parseEditPrompt } from './promptParser';
import { createClipSelection, findHighlightMoments } from './videoAnalysis';

export function generateEditPlan({ prompt, videoAnalysis, audioAnalysis, targetDuration, format, resolution, enhancementOptions }:{prompt:string; videoAnalysis:VideoAnalysis; audioAnalysis?:AudioAnalysis; targetDuration:number; format:OutputFormat; resolution:Resolution; enhancementOptions:EnhancementOptions;}): EditPlan {
  const parsed = parseEditPrompt(prompt);
  const highlights = findHighlightMoments(videoAnalysis, targetDuration);
  const beatTimeline = audioAnalysis?.beatTimeline ?? [];
  const clips = createClipSelection(highlights, beatTimeline, targetDuration).map((c, i)=>({ ...c, effects:[...(parsed.effects||[]).slice(0,2)], caption: c.caption ?? (i%2===0?'INSANE SKILLS':'COLD FINISH') }));
  return { duration: targetDuration, format, resolution, musicSegment: audioAnalysis?.bestSegment, clips, beatSync: parsed.beatSync, transitions:['flash','cut','zoom'], colorGrade:'high_contrast', enhanceQuality:Object.values(enhancementOptions).some(Boolean), style: parsed.style };
}
