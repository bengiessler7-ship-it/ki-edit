import { OutputFormat } from '@/lib/types';
export default function FormatSelector({value,onChange}:{value:OutputFormat;onChange:(v:OutputFormat)=>void}){return <div className='card flex gap-2'>{(['9:16','16:9','1:1'] as OutputFormat[]).map(f=><button key={f} className={`px-3 py-2 rounded ${value===f?'bg-neon text-black':'bg-white/10'}`} onClick={()=>onChange(f)}>{f}</button>)}</div>}
