import { apiClient } from './client';
import { MODEL_TO_BACKEND, type ModelKey, type PhotoResponse } from '../types/api';

export async function processPhoto(file: File, model: ModelKey): Promise<PhotoResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const { data } = await apiClient.post<PhotoResponse>('/api/photo/', formData, {
    params: { model: MODEL_TO_BACKEND[model] },
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}
