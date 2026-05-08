import type { GalleryItem } from '../types/models';

/**
 * Демо-карточки галереи — реальные результаты прогона пайплайна.
 * Медиа лежит в `public/demo_data/...` и раздаётся как статика.
 * Описания ассетов взяты из `description.md` каждой папки демо-набора.
 */
export const GALLERY: GalleryItem[] = [
  {
    id: 'demo-photo-1',
    title: 'Презрение — ConvNeXt',
    kind: 'photo',
    model: 'convnext',
    modelName: 'ConvNeXt-Tiny',
    description:
      'ConvNeXt-Tiny уверенно классифицирует выражение как «презрение» — характерную асимметрию уголков губ.',
    mediaUrl: '/demo_data/demo_photo_1/result.jpg',
    thumbnailGradient: 'linear-gradient(135deg, #FFE0B2 0%, #FFB74D 60%, #FF9800 100%)',
    stats: { faces: 1, dominantEmotion: 'Презрение', confidence: 55.1 },
  },
  {
    id: 'demo-photo-2',
    title: 'Презрение — Swin Transformer',
    kind: 'photo',
    model: 'swin',
    modelName: 'Swin Transformer Tiny',
    description:
      'Тот же класс эмоции, но Swin даёт заметно более высокую уверенность — трансформерная архитектура лучше ловит микро-мимику.',
    mediaUrl: '/demo_data/demo_photo_2/result.jpg',
    thumbnailGradient: 'linear-gradient(135deg, #CBD5FF 0%, #8B5CF6 60%, #4F7CFF 100%)',
    stats: { faces: 1, dominantEmotion: 'Презрение', confidence: 75.3 },
  },
  {
    id: 'demo-photo-3',
    title: 'Грусть — ResNet-50',
    kind: 'photo',
    model: 'resnet_50',
    modelName: 'ResNet-50',
    description:
      'ResNet-50 на размытом портрете определяет «грусть» с умеренной уверенностью — пограничный случай между нейтральностью и грустью.',
    mediaUrl: '/demo_data/demo_photo_3/result.jpg',
    thumbnailGradient: 'linear-gradient(135deg, #E0F2FE 0%, #60A5FA 60%, #2563EB 100%)',
    stats: { faces: 1, dominantEmotion: 'Грусть', confidence: 49.6 },
  },
  {
    id: 'demo-video-1',
    title: '«Карты, деньги, два ствола» — сцена в самоанском пабе',
    kind: 'video',
    model: 'convnext',
    modelName: 'ConvNeXt-Tiny',
    description:
      'Джейсон Стэтхэм сидит в самоанском пабе. Короткая сцена — три лица, статичная камера, подходящий пример для базовой проверки трекинга.',
    mediaUrl: '/demo_data/demo_video_1/result.mp4',
    statisticsUrl: '/demo_data/demo_video_1/statistics.html',
    stats: { duration: 11, faces: 3, dominantEmotion: 'Различные эмоции' },
  },
  {
    id: 'demo-video-2',
    title: '«Джентльмены» — напряжённая поездка',
    kind: 'video',
    model: 'convnext',
    modelName: 'ConvNeXt-Tiny',
    description:
      'Напряжённая поездка в автомобиле. Длинная сцена с тремя лицами — хорошо видно, как трекер удерживает идентичность через смены ракурса.',
    mediaUrl: '/demo_data/demo_video_2/result.mp4',
    statisticsUrl: '/demo_data/demo_video_2/statistics.html',
    stats: { duration: 27, faces: 3, dominantEmotion: 'Различные эмоции' },
  },
  {
    id: 'demo-video-3',
    title: '«Большой куш» — монолог про свиней',
    kind: 'video',
    model: 'convnext',
    modelName: 'ConvNeXt-Tiny',
    description:
      'Монолог про свиней. Демонстрация того, как окклюзии (руки, объекты в кадре, частичные перекрытия лица) влияют на распознавание эмоций.',
    mediaUrl: '/demo_data/demo_video_3/result.mp4',
    statisticsUrl: '/demo_data/demo_video_3/statistics.html',
    stats: {
      duration: 27,
      faces: 3,
      dominantEmotion: 'Различные эмоции',
      note: 'Демонстрирует влияние окклюзий на распознавание эмоций',
    },
  },
];

export function getGalleryItem(id: string): GalleryItem | undefined {
  return GALLERY.find((g) => g.id === id);
}
