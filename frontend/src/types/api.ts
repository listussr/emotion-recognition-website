export type ModelKey = 'resnet_50' | 'efficientnet_b3' | 'convnext' | 'swin';

/**
 * Бэкенд принимает только три значения. Пока обучение четвёртой модели идёт,
 * клиент отправляет один из этих ключей в `?model=`. Мэппинг ниже сокращает
 * расхождение между UI-именами и именами бэкенда.
 */
export type BackendModel = 'convnext' | 'swin' | 'se_resnet';

export const MODEL_TO_BACKEND: Record<ModelKey, BackendModel> = {
  resnet_50: 'se_resnet',
  efficientnet_b3: 'convnext',
  convnext: 'convnext',
  swin: 'swin',
};

export interface Emotion {
  label: string;
  probabilities: Record<string, number>;
  is_detected: boolean;
}

export interface PhotoResponse {
  faces_num: number;
  emotions: Record<string, Emotion>;
  process_time: number;
  result_image: string; // base64
}

export interface VideoResponse {
  processing_fps: number;
  duration_sec: number;
  total_frames_processed: number;
  result_video: string; // base64
  statistics_html: string;
  error?: string;
}
