'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import VideoUploadCard from '@/components/VideoUploadCard'; import MusicUploadCard from '@/components/MusicUploadCard'; import LinkInput from '@/components/LinkInput'; import EditPromptBox from '@/components/EditPromptBox'; import FormatSelector from '@/components/FormatSelector'; import ResolutionSelector from '@/components/ResolutionSelector'; import EnhancementOptions from '@/components/EnhancementOptions'; import RightsCheckbox from '@/components/RightsCheckbox'; import ErrorCard from '@/components/ErrorCard';
import { DEFAULT_ENHANCEMENT, DEFAULT_PROMPT } from '@/lib/constants';
import { analyzeAudioBuffer, loadAudioFile } from '@/lib/audioAnalysis';
import { generateEditPlan } from '@/lib/editPlanner';
import { initFFmpeg, renderEditWithFFmpeg, writeInputFiles, exportMP4 } from '@/lib/browserRenderer';
import { loadVideoMetadata } from '@/lib/videoAnalysis';

export default function Editor(){
  const [video,setVideo]=useState<File|null>(null); const [music,setMusic]=useState<File|null>(null); const [link,setLink]=useState(''); const [prompt,setPrompt]=useState(''); const [format,setFormat]=useState<'9:16'|'16:9'|'1:1'>('9:16'); const [resolution,setResolution]=useState<'4k'|'1080p'|'720p'|'480p'>('1080p'); const [enh,setEnh]=useState(DEFAULT_ENHANCEMENT); const [rights,setRights]=useState(false); const [error,setError]=useState(''); const [loading,setLoading]=useState(false); const router=useRouter();

  const run=async()=>{try{setError(''); if(!rights) throw new Error('Bitte bestätige, dass du die Rechte an diesem Video hast.'); if(!video && !link) throw new Error('Bitte Video hochladen oder direkten MP4-Link nutzen.'); setLoading(true);
    let videoFile = video;
    if (!videoFile && link.endsWith('.mp4')) { const r = await fetch(link); videoFile = new File([await r.blob()], 'linked.mp4', {type:'video/mp4'}); }
    if (!videoFile) throw new Error('YouTube/ZTube-Link ist nur Vorschau im MVP. Bitte lade Datei hoch oder nutze direkten MP4-Link.');
    const meta = await loadVideoMetadata(videoFile);
    if (meta.duration > 60) setError('Diese Datei ist sehr groß. Für Browser-Rendering empfehlen wir kurze Clips unter 60 Sekunden.');
    const audioAnalysis = music ? analyzeAudioBuffer(await loadAudioFile(music), Math.min(15, meta.duration)) : undefined;
    const videoAnalysis = { duration: meta.duration, sceneChanges: [1,3,5], motionScores: Array.from({length:12}, (_,i)=>({time:i+1, score: Math.random()*100})), highlights:[2,4,8] };
    const plan = generateEditPlan({prompt: prompt || DEFAULT_PROMPT, videoAnalysis, audioAnalysis, targetDuration: Math.min(15, meta.duration), format, resolution, enhancementOptions: enh});
    await initFFmpeg(); await writeInputFiles(videoFile, music); await renderEditWithFFmpeg(plan, enh); const blob=await exportMP4(); const url=URL.createObjectURL(blob);
    sessionStorage.setItem('resultUrl', url); sessionStorage.setItem('plan', JSON.stringify(plan)); router.push('/result');
  }catch(e){setError((e as Error).message)}finally{setLoading(false)}};
  return <main className='max-w-4xl mx-auto p-6 space-y-4'><h1 className='text-2xl font-bold'>EditKick AI Studio</h1><VideoUploadCard onChange={setVideo}/><MusicUploadCard onChange={setMusic}/><LinkInput value={link} onChange={setLink}/><EditPromptBox value={prompt} onChange={setPrompt}/><FormatSelector value={format} onChange={setFormat}/><ResolutionSelector value={resolution} onChange={setResolution}/><EnhancementOptions value={enh} onChange={setEnh}/><RightsCheckbox value={rights} onChange={setRights}/>{error&&<ErrorCard message={error}/>}<button className='btn-primary' onClick={run} disabled={loading}>{loading?'Rendering...':'KI-Edit generieren'}</button></main>}
