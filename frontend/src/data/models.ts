import type { ModelSpec } from '../types/models';

// Значения точности/F1 взяты из classification_report ноутбука nir_copy.ipynb.
// Задержки/FPS соответствуют PyTorch GPU при batch=1 из scientific_benchmark_final.csv.
// Размеры файлов — итоговые размеры .pth артефактов.

export const MODELS: ModelSpec[] = [
  {
    key: 'resnet_50',
    name: 'ResNet-50',
    shortName: 'ResNet',
    tagline: 'Классическая CNN с остаточными связями',
    description:
      'Глубокая свёрточная сеть с блоками-«шорткатами», обеспечивающими стабильный градиентный поток при обучении.',
    family: 'CNN',
    params: '25.6M',
    sizeMb: 98,
    inputSize: '224 × 224',
    inferenceMs: 5.16,
    accuracy: 0.7165,
    confusionStubSeed: 1,
    performanceNote: 'Производственный стандарт свёрточных моделей',
    longDescription:
      'ResNet-50 — одна из первых архитектур, показавших, что очень глубокие сети могут обучаться устойчиво при наличии остаточных соединений. Применяется как базовый энкодер в задачах компьютерного зрения.',
  },
  {
    key: 'efficientnet_b3',
    name: 'EfficientNet-B3',
    shortName: 'EfficientNet',
    tagline: 'Сбалансированная CNN с составным масштабированием',
    description:
      'Архитектура, разработанная с помощью поиска и составного масштабирования глубины, ширины и разрешения.',
    family: 'CNN',
    params: '12.2M',
    sizeMb: 49,
    inputSize: '300 × 300',
    inferenceMs: 13.9,
    accuracy: 0.6879,
    confusionStubSeed: 2,
    performanceNote: 'Лучшее соотношение точности и скорости',
    longDescription:
      'EfficientNet-B3 — представитель семейства EfficientNet. Использует блоки MBConv и применяет единый коэффициент масштабирования. Даёт конкурентные результаты при малом числе параметров.',
  },
  {
    key: 'convnext',
    name: 'ConvNeXt-Tiny',
    shortName: 'ConvNeXt',
    tagline: 'Современная свёртка в духе трансформеров',
    description:
      'Переосмысленная CNN-архитектура, заимствующая идеи ViT: большие ядра, GELU, LayerNorm, инвертированные блоки.',
    family: 'CNN',
    params: '28.6M',
    sizeMb: 107,
    inputSize: '224 × 224',
    inferenceMs: 4.69,
    accuracy: 0.7404,
    confusionStubSeed: 3,
    performanceNote: 'Наиболее точная модель в сборке',
    longDescription:
      'ConvNeXt-Tiny показывает, что классические свёртки, дополненные современными приёмами, способны соперничать с трансформерами. Основа — инвертированные bottleneck-блоки с крупными ядрами 7×7.',
  },
  {
    key: 'swin',
    name: 'Swin Transformer Tiny',
    shortName: 'Swin',
    tagline: 'Оконный трансформер с иерархией',
    description:
      'Визуальный трансформер со сдвигающимися окнами внимания — позволяет строить иерархические признаки при линейной сложности.',
    family: 'ViT',
    params: '28.3M',
    sizeMb: 110,
    inputSize: '224 × 224',
    inferenceMs: 9.85,
    accuracy: 0.7265,
    confusionStubSeed: 4,
    performanceNote: 'Трансформер с эффективным вниманием',
    longDescription:
      'Swin Transformer вводит механизм сдвигающихся окон: self-attention считается внутри фиксированных окон, а между слоями окна сдвигаются, позволяя обмениваться информацией между ними.',
  },
];

export function getModel(key: string): ModelSpec | undefined {
  return MODELS.find((m) => m.key === key);
}
