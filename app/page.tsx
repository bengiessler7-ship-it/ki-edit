import { HeroSection } from '@/components/HeroSection';
import { FeatureCard } from '@/components/FeatureCard';

export default function Home() {
  const features = ['Musik-Analyse','Beat-Sync','Automatische Highlights','4K Export','Browser-Rendering','Eigene Musik','TikTok-Format','MP4 Download'];
  return <main className='max-w-6xl mx-auto'><HeroSection/><section className='grid md:grid-cols-4 gap-4 p-8'>{features.map(f=><FeatureCard key={f} title={f}/>)}</section><p className='p-8 text-white/70'>Läuft direkt im Browser und ist Netlify-ready.</p></main>;
}
