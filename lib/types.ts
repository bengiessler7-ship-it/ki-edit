export type OutputFormat = '9:16' | '16:9' | '1:1';
export type Resolution = '4k' | '1080p' | '720p' | '480p';

export type EnhancementOptions = {
  upscale: boolean;
  sharpen: boolean;
  stabilize: boolean;
  denoise: boolean;
  colorBoost: boolean;
};

export type Beat = { time: number; strength: number };
export type MusicSegment = { start: number; end: number };

export type Clip = {
  videoStart: number;
  videoEnd: number;
  speed: number;
  effects: string[];
  caption?: string;
};

export type AudioAnalysis = {
  duration: number;
  beats: Beat[];
  energyPeaks: number[];
  bpm: number;
  bestSegment: MusicSegment;
  beatTimeline: Beat[];
};

export type FrameSample = { time: number; data: ImageData };
export type VideoAnalysis = {
  duration: number;
  sceneChanges: number[];
  motionScores: { time: number; score: number }[];
  highlights: number[];
};

export type EditPlan = {
  duration: number;
  format: OutputFormat;
  resolution: Resolution;
  musicSegment?: MusicSegment;
  clips: Clip[];
  beatSync: boolean;
  transitions: string[];
  colorGrade?: string;
  enhanceQuality: boolean;
  style?: string;
};

export type Project = {
  id: string;
  videoSourceType: 'upload' | 'youtube' | 'direct_link';
  videoUrl: string | null;
  videoFileName: string | null;
  musicFileName: string | null;
  editDescription: string;
  outputFormat: OutputFormat;
  resolution: Resolution;
  enhanceQuality: boolean;
  enhancementOptions: EnhancementOptions;
  status: 'created' | 'analyzing' | 'planning' | 'rendering' | 'done' | 'error';
  progress: number;
  editPlan: EditPlan | null;
  outputVideoUrl: string | null;
  createdAt: string;
};
