import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        neon: '#39FF14',
        background: '#070b10'
      }
    }
  },
  plugins: [],
};

export default config;
