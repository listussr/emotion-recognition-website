// Реальные метрики, извлечённые из ноутбука nir_copy.ipynb.
// 8 классов эмоций в фиксированном порядке:
// anger, contempt, disgust, fear, happy, neutral, sad, surprise.

import type { ModelKey } from '../types/api';
import { EMOTION_KEYS } from '../types/models';

export interface ClassMetrics {
  precision: number;
  recall: number;
  f1: number;
  support: number;
}

export interface ModelMetrics {
  accuracy: number;
  macroF1: number;
  weightedF1: number;
  totalSupport: number;
  perClass: Record<(typeof EMOTION_KEYS)[number], ClassMetrics>;
  confusion: number[][]; // нормализовано по строке, 8×8
}

// ---------- ResNet-50 ----------
const RESNET_50: ModelMetrics = {
  accuracy: 0.7165,
  macroF1: 0.6837,
  weightedF1: 0.7158,
  totalSupport: 5813,
  perClass: {
    anger: { precision: 0.5967, recall: 0.5652, f1: 0.5805, support: 644 },
    contempt: { precision: 0.6865, recall: 0.7235, f1: 0.7045, support: 575 },
    disgust: { precision: 0.6009, recall: 0.5282, f1: 0.5622, support: 496 },
    fear: { precision: 0.5705, recall: 0.5597, f1: 0.5651, support: 636 },
    happy: { precision: 0.9417, recall: 0.9286, f1: 0.9351, support: 1009 },
    neutral: { precision: 0.8951, recall: 0.9064, f1: 0.9007, support: 1026 },
    sad: { precision: 0.5780, recall: 0.5929, f1: 0.5853, support: 619 },
    surprise: { precision: 0.6141, recall: 0.6597, f1: 0.6360, support: 808 },
  },
  confusion: [
    [0.56521739, 0.07608696, 0.09627329, 0.06677019, 0.0, 0.0, 0.12111801, 0.07453416],
    [0.06434783, 0.72347826, 0.05043478, 0.01391304, 0.00869565, 0.01217391, 0.06782609, 0.05913043],
    [0.17943548, 0.05645161, 0.52822581, 0.06451613, 0.00403226, 0.00806452, 0.08870968, 0.07056452],
    [0.05188679, 0.02201258, 0.03616352, 0.55974843, 0.0, 0.0, 0.11163522, 0.21855346],
    [0.0, 0.00099108, 0.0, 0.00099108, 0.92864222, 0.06144698, 0.00099108, 0.00693756],
    [0.00584795, 0.01169591, 0.00097466, 0.00487329, 0.04775828, 0.90643275, 0.00779727, 0.01461988],
    [0.10016155, 0.07592892, 0.06300485, 0.07592892, 0.0, 0.0, 0.59289176, 0.09208401],
    [0.02351485, 0.04826733, 0.02475248, 0.16336634, 0.00247525, 0.04455446, 0.03341584, 0.65965347],
  ],
};

// ---------- EfficientNet-B3 ----------
const EFFICIENTNET_B3: ModelMetrics = {
  accuracy: 0.6879,
  macroF1: 0.6570,
  weightedF1: 0.6875,
  totalSupport: 5813,
  perClass: {
    anger: { precision: 0.5495, recall: 0.5512, f1: 0.5504, support: 644 },
    contempt: { precision: 0.6091, recall: 0.7426, f1: 0.6693, support: 575 },
    disgust: { precision: 0.5816, recall: 0.5101, f1: 0.5435, support: 496 },
    fear: { precision: 0.5452, recall: 0.6258, f1: 0.5827, support: 636 },
    happy: { precision: 0.8886, recall: 0.9405, f1: 0.9138, support: 1009 },
    neutral: { precision: 0.9143, recall: 0.8216, f1: 0.8655, support: 1026 },
    sad: { precision: 0.5325, recall: 0.5961, f1: 0.5625, support: 619 },
    surprise: { precision: 0.6553, recall: 0.5012, f1: 0.5680, support: 808 },
  },
  confusion: [
    [0.55124224, 0.10869565, 0.09782609, 0.06832298, 0.0, 0.0, 0.13819876, 0.03571429],
    [0.07130435, 0.7426087, 0.03826087, 0.01565217, 0.01043478, 0.01043478, 0.05913043, 0.05217391],
    [0.19354839, 0.08669355, 0.51008065, 0.05846774, 0.00201613, 0.00403226, 0.10685484, 0.03830645],
    [0.06132075, 0.03459119, 0.03773585, 0.62578616, 0.0, 0.0, 0.12106918, 0.11949686],
    [0.0, 0.0049554, 0.00396432, 0.0, 0.94053518, 0.03964321, 0.00099108, 0.0099108],
    [0.00682261, 0.01461988, 0.00877193, 0.00389864, 0.10331384, 0.82163743, 0.01364522, 0.02729045],
    [0.11954766, 0.10662359, 0.04523425, 0.08885299, 0.0, 0.0, 0.59612278, 0.04361874],
    [0.04207921, 0.06559406, 0.03960396, 0.23638614, 0.00742574, 0.03836634, 0.06930693, 0.50123762],
  ],
};

// ---------- ConvNeXt-Tiny ----------
const CONVNEXT: ModelMetrics = {
  accuracy: 0.7404,
  macroF1: 0.7118,
  weightedF1: 0.7410,
  totalSupport: 5813,
  perClass: {
    anger: { precision: 0.5842, recall: 0.6413, f1: 0.6114, support: 644 },
    contempt: { precision: 0.7419, recall: 0.7200, f1: 0.7308, support: 575 },
    disgust: { precision: 0.6481, recall: 0.5645, f1: 0.6034, support: 496 },
    fear: { precision: 0.6412, recall: 0.5676, f1: 0.6022, support: 636 },
    happy: { precision: 0.9293, recall: 0.9514, f1: 0.9403, support: 1009 },
    neutral: { precision: 0.9403, recall: 0.8899, f1: 0.9144, support: 1026 },
    sad: { precision: 0.5829, recall: 0.6931, f1: 0.6332, support: 619 },
    surprise: { precision: 0.6568, recall: 0.6609, f1: 0.6589, support: 808 },
  },
  confusion: [
    [0.64130435, 0.0636646, 0.07763975, 0.04658385, 0.0, 0.0, 0.1242236, 0.04658385],
    [0.09391304, 0.72, 0.04521739, 0.00347826, 0.00695652, 0.01391304, 0.0626087, 0.05391304],
    [0.21169355, 0.0483871, 0.56451613, 0.03830645, 0.00403226, 0.00403226, 0.08870968, 0.04032258],
    [0.06289308, 0.01886792, 0.02987421, 0.56761006, 0.0, 0.0, 0.13836478, 0.18238994],
    [0.00099108, 0.00099108, 0.00099108, 0.0, 0.95143707, 0.03468781, 0.00099108, 0.0099108],
    [0.00779727, 0.00487329, 0.00389864, 0.00194932, 0.05847953, 0.88986355, 0.00779727, 0.02534113],
    [0.08077544, 0.04684976, 0.05169628, 0.05331179, 0.0, 0.0, 0.69305331, 0.07431341],
    [0.04455446, 0.03960396, 0.02475248, 0.14356436, 0.00866337, 0.01608911, 0.06188119, 0.66089109],
  ],
};

// ---------- Swin Transformer Tiny ----------
const SWIN: ModelMetrics = {
  accuracy: 0.7265,
  macroF1: 0.6952,
  weightedF1: 0.7266,
  totalSupport: 5813,
  perClass: {
    anger: { precision: 0.5706, recall: 0.6211, f1: 0.5948, support: 644 },
    contempt: { precision: 0.6985, recall: 0.7374, f1: 0.7174, support: 575 },
    disgust: { precision: 0.5606, recall: 0.5685, f1: 0.5646, support: 496 },
    fear: { precision: 0.5900, recall: 0.5928, f1: 0.5914, support: 636 },
    happy: { precision: 0.9268, recall: 0.9534, f1: 0.9399, support: 1009 },
    neutral: { precision: 0.9261, recall: 0.8918, f1: 0.9086, support: 1026 },
    sad: { precision: 0.6195, recall: 0.5945, f1: 0.6068, support: 619 },
    surprise: { precision: 0.6662, recall: 0.6126, f1: 0.6383, support: 808 },
  },
  confusion: [
    [0.62111801, 0.07919255, 0.11645963, 0.05900621, 0.0, 0.0, 0.08540373, 0.03881988],
    [0.08521739, 0.7373913, 0.04869565, 0.01043478, 0.00695652, 0.01391304, 0.0573913, 0.04],
    [0.18145161, 0.05040323, 0.56854839, 0.05443548, 0.00604839, 0.00806452, 0.0766129, 0.05443548],
    [0.06446541, 0.02044025, 0.05345912, 0.5927673, 0.0, 0.0, 0.10220126, 0.16666667],
    [0.0, 0.00198216, 0.0, 0.0, 0.95341923, 0.03766105, 0.0, 0.00693756],
    [0.00682261, 0.00779727, 0.00292398, 0.00097466, 0.06237817, 0.89181287, 0.00584795, 0.0214425],
    [0.12277868, 0.06462036, 0.08400646, 0.0726979, 0.0, 0.0, 0.59450727, 0.06138934],
    [0.0470297, 0.05445545, 0.03589109, 0.17945545, 0.00618812, 0.02846535, 0.03589109, 0.61262376],
  ],
};

export const MODEL_METRICS: Record<ModelKey, ModelMetrics> = {
  resnet_50: RESNET_50,
  efficientnet_b3: EFFICIENTNET_B3,
  convnext: CONVNEXT,
  swin: SWIN,
};

// --- Производительность (benchmark из scientific_benchmark_final.csv) ---

export interface BenchmarkRow {
  batch: number;
  pt_cpu_ms: number;
  pt_cpu_fps: number;
  pt_gpu_ms: number;
  pt_gpu_fps: number;
  onnx_cpu_ms: number;
  onnx_cpu_fps: number;
  onnx_gpu_ms: number;
  onnx_gpu_fps: number;
  gpu_mem_mb: number;
}

export const MODEL_BENCHMARK: Record<ModelKey, BenchmarkRow[]> = {
  convnext: [
    { batch: 1, pt_cpu_ms: 36.579, pt_cpu_fps: 27.338, pt_gpu_ms: 4.690, pt_gpu_fps: 213.235, onnx_cpu_ms: 31.758, onnx_cpu_fps: 31.488, onnx_gpu_ms: 5.657, onnx_gpu_fps: 176.772, gpu_mem_mb: 984.73 },
    { batch: 8, pt_cpu_ms: 276.298, pt_cpu_fps: 28.954, pt_gpu_ms: 8.855, pt_gpu_fps: 903.465, onnx_cpu_ms: 363.099, onnx_cpu_fps: 22.033, onnx_gpu_ms: 15.255, onnx_gpu_fps: 524.411, gpu_mem_mb: 984.73 },
    { batch: 16, pt_cpu_ms: 551.346, pt_cpu_fps: 29.020, pt_gpu_ms: 17.079, pt_gpu_fps: 936.817, onnx_cpu_ms: 792.618, onnx_cpu_fps: 20.186, onnx_gpu_ms: 29.860, onnx_gpu_fps: 535.841, gpu_mem_mb: 984.73 },
  ],
  swin: [
    { batch: 1, pt_cpu_ms: 41.454, pt_cpu_fps: 24.123, pt_gpu_ms: 9.845, pt_gpu_fps: 101.574, onnx_cpu_ms: 36.467, onnx_cpu_fps: 27.422, onnx_gpu_ms: 8.360, onnx_gpu_fps: 119.611, gpu_mem_mb: 879.35 },
    { batch: 8, pt_cpu_ms: 319.689, pt_cpu_fps: 25.024, pt_gpu_ms: 11.362, pt_gpu_fps: 704.112, onnx_cpu_ms: 390.036, onnx_cpu_fps: 20.511, onnx_gpu_ms: 18.509, onnx_gpu_fps: 432.212, gpu_mem_mb: 879.35 },
    { batch: 16, pt_cpu_ms: 678.874, pt_cpu_fps: 23.568, pt_gpu_ms: 22.101, pt_gpu_fps: 723.963, onnx_cpu_ms: 880.864, onnx_cpu_fps: 18.164, onnx_gpu_ms: 33.876, onnx_gpu_fps: 472.311, gpu_mem_mb: 879.35 },
  ],
  resnet_50: [
    { batch: 1, pt_cpu_ms: 37.482, pt_cpu_fps: 26.679, pt_gpu_ms: 5.161, pt_gpu_fps: 193.742, onnx_cpu_ms: 17.656, onnx_cpu_fps: 56.637, onnx_gpu_ms: 2.119, onnx_gpu_fps: 471.916, gpu_mem_mb: 766.23 },
    { batch: 8, pt_cpu_ms: 274.027, pt_cpu_fps: 29.194, pt_gpu_ms: 7.028, pt_gpu_fps: 1138.314, onnx_cpu_ms: 138.681, onnx_cpu_fps: 57.686, onnx_gpu_ms: 7.180, onnx_gpu_fps: 1114.271, gpu_mem_mb: 766.23 },
    { batch: 16, pt_cpu_ms: 595.988, pt_cpu_fps: 26.846, pt_gpu_ms: 14.569, pt_gpu_fps: 1098.190, onnx_cpu_ms: 318.272, onnx_cpu_fps: 50.272, onnx_gpu_ms: 14.897, onnx_gpu_fps: 1074.071, gpu_mem_mb: 766.23 },
  ],
  efficientnet_b3: [
    { batch: 1, pt_cpu_ms: 34.992, pt_cpu_fps: 28.578, pt_gpu_ms: 13.900, pt_gpu_fps: 71.941, onnx_cpu_ms: 10.421, onnx_cpu_fps: 95.957, onnx_gpu_ms: 2.578, onnx_gpu_fps: 387.848, gpu_mem_mb: 683.33 },
    { batch: 8, pt_cpu_ms: 260.557, pt_cpu_fps: 30.703, pt_gpu_ms: 13.956, pt_gpu_fps: 573.236, onnx_cpu_ms: 107.839, onnx_cpu_fps: 74.185, onnx_gpu_ms: 6.624, onnx_gpu_fps: 1207.693, gpu_mem_mb: 683.33 },
    { batch: 16, pt_cpu_ms: 641.382, pt_cpu_fps: 24.946, pt_gpu_ms: 19.890, pt_gpu_fps: 804.439, onnx_cpu_ms: 284.258, onnx_cpu_fps: 56.287, onnx_gpu_ms: 12.909, onnx_gpu_fps: 1239.455, gpu_mem_mb: 683.33 },
  ],
};

// --- Карточки «карт градиентов» (Grad-CAM / Attention), приложены из ноутбука ---

export interface GradientMap {
  src: string;
  caption: string;
}

export const GRADIENT_MAPS: Record<ModelKey, GradientMap[]> = {
  resnet_50: [
    { src: '/assets/gradients/resnet_50_gradcam.png', caption: 'Grad-CAM по финальному свёрточному блоку' },
  ],
  efficientnet_b3: [
    { src: '/assets/gradients/efficientnet_b3_gradcam.png', caption: 'Grad-CAM по последнему MBConv-блоку' },
  ],
  convnext: [
    { src: '/assets/gradients/convnext_tiny_gradcam_1.png', caption: 'Grad-CAM по последнему stage-блоку' },
    { src: '/assets/gradients/convnext_tiny_gradcam_2.png', caption: 'Grad-CAM по промежуточному stage-блоку' },
  ],
  swin: [
    { src: '/assets/gradients/swin_tiny_gradcam_1.png', caption: 'Attention rollout по последнему блоку' },
    { src: '/assets/gradients/swin_tiny_gradcam_2.png', caption: 'Attention rollout по промежуточному блоку' },
  ],
};
