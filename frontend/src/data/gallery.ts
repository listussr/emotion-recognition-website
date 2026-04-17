import type { GalleryItem } from '../types/models';

/**
 * Временные демо-карточки — реальные медиа заменим после получения ассетов.
 * thumbnailGradient — CSS-градиент, используемый как плейсхолдер превью.
 */
export const GALLERY: GalleryItem[] = [
  {
    id: 'demo-01',
    title: 'Групповое фото — радостные лица',
    kind: 'photo',
    model: 'convnext',
    modelName: 'ConvNeXt-Tiny',
    thumbnailGradient: 'linear-gradient(135deg, #FFE0B2 0%, #FFB74D 60%, #FF9800 100%)',
    description:
      'Пять человек улыбаются в кадре. Модель уверенно определяет доминирующую эмоцию радости.',
    stats: { faces: 5, dominantEmotion: 'Радость' },
  },
  {
    id: 'demo-02',
    title: 'Беседа — смена эмоций во времени',
    kind: 'video',
    model: 'swin',
    modelName: 'Swin Transformer Tiny',
    thumbnailGradient: 'linear-gradient(135deg, #CBD5FF 0%, #8B5CF6 60%, #4F7CFF 100%)',
    description:
      'Диалог двух человек на 18 секунд. Видно, как эмоции плавно переходят от нейтральности к удивлению.',
    stats: { duration: 18.4, faces: 2, dominantEmotion: 'Нейтральность' },
  },
  {
    id: 'demo-03',
    title: 'Портрет — спокойное выражение',
    kind: 'photo',
    model: 'efficientnet_b3',
    modelName: 'EfficientNet-B3',
    thumbnailGradient: 'linear-gradient(135deg, #E0F2FE 0%, #60A5FA 60%, #2563EB 100%)',
    description: 'Одиночный портрет анфас. Классический пример нейтрального состояния.',
    stats: { faces: 1, dominantEmotion: 'Нейтральность' },
  },
  {
    id: 'demo-04',
    title: 'Реакция на новости — удивление',
    kind: 'video',
    model: 'resnet_50',
    modelName: 'ResNet-50',
    thumbnailGradient: 'linear-gradient(135deg, #FEE2E2 0%, #FCA5A5 60%, #EF4444 100%)',
    description: 'Короткий ролик 12 секунд. Яркий переход от нейтральности к удивлению.',
    stats: { duration: 12.1, faces: 1, dominantEmotion: 'Удивление' },
  },
  {
    id: 'demo-05',
    title: 'Разнообразие поз и ракурсов',
    kind: 'photo',
    model: 'swin',
    modelName: 'Swin Transformer Tiny',
    thumbnailGradient: 'linear-gradient(135deg, #E9D5FF 0%, #C084FC 60%, #7C3AED 100%)',
    description:
      'Несколько лиц под разными углами. Проверка устойчивости модели к повороту головы.',
    stats: { faces: 3, dominantEmotion: 'Радость' },
  },
  {
    id: 'demo-06',
    title: 'Динамическая сцена — трекинг лиц',
    kind: 'video',
    model: 'convnext',
    modelName: 'ConvNeXt-Tiny',
    thumbnailGradient: 'linear-gradient(135deg, #D1FAE5 0%, #6EE7B7 60%, #10B981 100%)',
    description:
      'Активное движение в кадре. Хороший пример работы трекера через кратковременные окклюзии.',
    stats: { duration: 22.8, faces: 4, dominantEmotion: 'Радость' },
  },
];

export function getGalleryItem(id: string): GalleryItem | undefined {
  return GALLERY.find((g) => g.id === id);
}
