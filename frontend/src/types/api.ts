export type ModelKey = 'resnet_50' | 'efficientnet_b3' | 'convnext' | 'swin';

/**
 * Все четыре модели конвертированы в ONNX и доступны на бэкенде напрямую.
 * Мэппинг оставлен 1:1 на случай будущих расхождений UI/бэкенд имён.
 */
export type BackendModel = 'convnext' | 'swin' | 'resnet_50' | 'efficientnet_b3';

export const MODEL_TO_BACKEND: Record<ModelKey, BackendModel> = {
  resnet_50: 'resnet_50',
  efficientnet_b3: 'efficientnet_b3',
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
