import { EnhancementOptions, OutputFormat, Resolution } from './types';

export const DEFAULT_PROMPT = 'Schneller TikTok-Fußball-Edit mit Beat-Sync, Zooms, Flashs und GOAL-Text.';
export const FORMATS: OutputFormat[] = ['9:16', '16:9', '1:1'];
export const RESOLUTIONS: Resolution[] = ['4k', '1080p', '720p', '480p'];
export const DEFAULT_ENHANCEMENT: EnhancementOptions = { upscale: false, sharpen: true, stabilize: false, denoise: false, colorBoost: true };

export const RESOLUTION_MAP: Record<OutputFormat, Record<Resolution, { width: number; height: number }>> = {
  '9:16': { '4k': { width: 2160, height: 3840 }, '1080p': { width: 1080, height: 1920 }, '720p': { width: 720, height: 1280 }, '480p': { width: 480, height: 854 } },
  '16:9': { '4k': { width: 3840, height: 2160 }, '1080p': { width: 1920, height: 1080 }, '720p': { width: 1280, height: 720 }, '480p': { width: 854, height: 480 } },
  '1:1': { '4k': { width: 2160, height: 2160 }, '1080p': { width: 1080, height: 1080 }, '720p': { width: 720, height: 720 }, '480p': { width: 480, height: 480 } }
};
