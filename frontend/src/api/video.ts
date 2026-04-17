import { apiClient } from './client';
import { MODEL_TO_BACKEND, type ModelKey, type VideoResponse } from '../types/api';

export async function processVideo(file: File, model: ModelKey): Promise<VideoResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const { data } = await apiClient.post<VideoResponse>('/api/video/', formData, {
    params: { model: MODEL_TO_BACKEND[model] },
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}
