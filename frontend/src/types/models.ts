import type { ModelKey } from './api';

export type ModelFamily = 'CNN' | 'ViT';

export interface ModelSpec {
  key: ModelKey;
  name: string;
  shortName: string;
  tagline: string;
  description: string;
  family: ModelFamily;
  params: string;
  sizeMb: number;
  inputSize: string;
  inferenceMs: number;
  accuracy: number;
  confusionStubSeed: number;
  performanceNote: string;
  longDescription: string;
}

export interface GalleryItem {
  id: string;
  title: string;
  kind: 'photo' | 'video';
  model: ModelKey;
  modelName: string;
  thumbnailGradient: string;
  description: string;
  stats: {
    duration?: number;
    faces: number;
    dominantEmotion: string;
  };
}

export const EMOTION_KEYS = [
  'anger',
  'contempt',
  'disgust',
  'fear',
  'happy',
  'neutral',
  'sad',
  'surprise',
] as const;

export type EmotionKey = (typeof EMOTION_KEYS)[number];

export const EMOTION_LABELS_RU: Record<EmotionKey, string> = {
  anger: 'Гнев',
  contempt: 'Презрение',
  disgust: 'Отвращение',
  fear: 'Страх',
  happy: 'Радость',
  neutral: 'Нейтральность',
  sad: 'Грусть',
  surprise: 'Удивление',
};

export const EMOTION_COLORS: Record<EmotionKey, string> = {
  anger: '#ff3b30',
  contempt: '#af52de',
  disgust: '#34c759',
  fear: '#a5a500',
  happy: '#ffcc00',
  neutral: '#8e8e93',
  sad: '#007aff',
  surprise: '#ff9500',
};
