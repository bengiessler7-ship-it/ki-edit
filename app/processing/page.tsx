'use client';
import ProcessingTimeline from '@/components/ProcessingTimeline'; import ProgressBar from '@/components/ProgressBar';
export default function Processing(){return <main className='max-w-2xl mx-auto p-6 space-y-4'><h1 className='text-2xl'>Verarbeitung</h1><ProcessingTimeline step='Video wird gerendert'/><ProgressBar progress={65}/><button className='px-4 py-2 border rounded'>Abbrechen</button></main>}
