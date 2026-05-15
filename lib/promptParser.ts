export function parseEditPrompt(description: string) {
  const text = description.toLowerCase();
  const effects = ['shake','zoom','flash','speed_ramp','slow_motion'].filter((e)=>text.includes(e.replace('_',' ')) || text.includes(e.split('_')[0]));
  return {
    style: text.includes('phonk') ? 'hard_phonk' : text.includes('cinematic') ? 'cinematic' : 'football_edit',
    pace: text.includes('schnell') ? 'fast' : 'smooth',
    format: text.includes('16:9') ? '16:9' : text.includes('1:1') ? '1:1' : '9:16',
    effects: effects.length ? effects : ['zoom','flash'],
    beatSync: !text.includes('ohne beat')
  };
}
