import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { getModel } from '../data/models';
import { MODEL_METRICS, GRADIENT_MAPS } from '../data/metrics';
import { ModelSchema } from '../components/models/ModelSchema';
import { ConfusionMatrix } from '../components/models/ConfusionMatrix';
import { PerClassMetrics } from '../components/models/PerClassMetrics';
import { PerformanceCharts } from '../components/models/PerformanceCharts';
import { BenchmarkSummary } from '../components/models/BenchmarkSummary';
import { GradientHeatmap } from '../components/models/GradientHeatmap';
import { Tabs } from '../components/ui/Tabs';
import { Badge } from '../components/ui/Badge';
import { LinkButton } from '../components/ui/Button';
import NotFoundPage from './NotFoundPage';

export default function ModelDetailPage() {
  const { id } = useParams<{ id: string }>();
  const model = id ? getModel(id) : undefined;
  if (!model) return <NotFoundPage />;

  const metrics = MODEL_METRICS[model.key];
  const hasGradients = (GRADIENT_MAPS[model.key] ?? []).length > 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -4 }}
      transition={{ duration: 0.3 }}
      className="mx-auto max-w-7xl px-4 md:px-8 py-8 md:py-12"
    >
      <Link
        to="/models"
        className="inline-flex items-center gap-1.5 text-sm text-ink-muted hover:text-ink mb-8"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path
            d="M19 12H5m0 0l5-5m-5 5l5 5"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
        Назад к архитектурам
      </Link>

      <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-6 mb-8">
        <div className="min-w-0">
          <div className="flex items-center gap-2 mb-3 flex-wrap">
            <Badge tone={model.family === 'ViT' ? 'accent' : 'primary'}>{model.family}</Badge>
            <span className="text-xs font-mono text-ink-muted">{model.params} параметров</span>
          </div>
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-display font-semibold text-ink break-words">
            {model.name}
          </h1>
          <p className="mt-2 text-base md:text-lg text-ink-muted">{model.tagline}</p>
        </div>
        <LinkButton
          to={`/process/photo?model=${model.key}`}
          variant="primary"
          className="w-full md:w-auto justify-center"
        >
          Попробовать модель
        </LinkButton>
      </div>

      <div className="grid gap-6 md:grid-cols-3 mb-10">
        <div className="md:col-span-2 card p-6">
          <h3 className="font-display font-semibold text-ink mb-4">Схема архитектуры</h3>
          <ModelSchema modelKey={model.key} />
          <p className="mt-4 text-xs text-ink-muted">
            Упрощённое изображение для обзорного понимания
          </p>
        </div>
        <div className="card p-6">
          <h3 className="font-display font-semibold text-ink mb-4">Характеристики</h3>
          <dl className="space-y-3 text-sm">
            {[
              ['Параметры', model.params],
              ['Размер файла', `${model.sizeMb} МБ`],
              ['Размер входа', model.inputSize],
              ['Инференс · GPU', `${model.inferenceMs.toFixed(2)} мс`],
              ['Accuracy', `${(metrics.accuracy * 100).toFixed(2)}%`],
              ['Macro-F1', metrics.macroF1.toFixed(4)],
            ].map(([label, value]) => (
              <div
                key={label}
                className="flex items-center justify-between gap-2 py-1 border-b border-line-soft last:border-0"
              >
                <dt className="text-ink-muted">{label}</dt>
                <dd className="font-mono text-ink">{value}</dd>
              </div>
            ))}
          </dl>
          <p className="mt-4 text-xs text-ink-muted leading-relaxed">{model.performanceNote}</p>
        </div>
      </div>

      <Tabs
        items={[
          {
            id: 'metrics',
            label: 'Метрики',
            content: (
              <div className="space-y-6">
                <ConfusionMatrix metrics={metrics} />
                <PerClassMetrics metrics={metrics} />
              </div>
            ),
          },
          {
            id: 'performance',
            label: 'Производительность',
            content: (
              <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
                <PerformanceCharts modelKey={model.key} />
                <BenchmarkSummary modelKey={model.key} />
              </div>
            ),
          },
          ...(hasGradients
            ? [
                {
                  id: 'gradients',
                  label: 'Карты градиентов',
                  content: <GradientHeatmap modelKey={model.key} />,
                },
              ]
            : []),
          {
            id: 'description',
            label: 'Описание',
            content: (
              <div className="card p-6 md:p-8">
                <div className="prose prose-sm max-w-none">
                  <p className="text-ink leading-relaxed text-base">{model.longDescription}</p>
                  <p className="mt-4 text-ink-muted leading-relaxed text-sm">
                    Модель используется в приложении как классификатор эмоций. Получает
                    выровненный кроп лица и возвращает вектор вероятностей по восьми классам:
                    гнев, презрение, отвращение, страх, радость, нейтральность, грусть, удивление.
                  </p>
                </div>
              </div>
            ),
          },
        ]}
      />
    </motion.div>
  );
}
