import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { getGalleryItem } from '../data/gallery';
import { Badge } from '../components/ui/Badge';
import { LinkButton } from '../components/ui/Button';
import NotFoundPage from './NotFoundPage';

export default function GalleryDetailPage() {
  const { id } = useParams<{ id: string }>();
  const item = id ? getGalleryItem(id) : undefined;
  if (!item) return <NotFoundPage />;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -4 }}
      transition={{ duration: 0.3 }}
      className="mx-auto max-w-6xl px-4 md:px-8 py-12"
    >
      <Link
        to="/gallery"
        className="inline-flex items-center gap-1.5 text-sm text-ink-muted hover:text-ink mb-8"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M19 12H5m0 0l5-5m-5 5l5 5" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        Назад в галерею
      </Link>

      <div className="flex flex-wrap items-center gap-2 mb-4">
        <Badge tone={item.kind === 'video' ? 'accent' : 'primary'}>
          {item.kind === 'video' ? 'Видео' : 'Фото'}
        </Badge>
        <Badge tone="muted">{item.modelName}</Badge>
      </div>

      <h1 className="text-3xl md:text-4xl font-display font-semibold text-ink">{item.title}</h1>
      <p className="mt-3 text-ink-muted max-w-2xl">{item.description}</p>

      <div className="mt-8 grid gap-6 md:grid-cols-[1fr_300px]">
        <div className="card overflow-hidden">
          {item.kind === 'photo' ? (
            <img
              src={item.mediaUrl}
              alt={item.title}
              className="w-full max-h-[640px] object-contain bg-black"
            />
          ) : (
            <video
              src={item.mediaUrl}
              controls
              preload="metadata"
              playsInline
              className="w-full max-h-[640px] object-contain bg-black"
            />
          )}
        </div>

        <div className="flex flex-col gap-4">
          <div className="card p-5">
            <h4 className="font-display font-semibold text-ink mb-4">Сводка</h4>
            <dl className="space-y-3 text-sm">
              <div className="flex justify-between">
                <dt className="text-ink-muted">Лиц в сессии</dt>
                <dd className="font-mono text-ink">{item.stats.faces}</dd>
              </div>
              {item.stats.duration !== undefined && (
                <div className="flex justify-between">
                  <dt className="text-ink-muted">Длительность</dt>
                  <dd className="font-mono text-ink">{item.stats.duration.toFixed(0)} с</dd>
                </div>
              )}
              <div className="flex justify-between">
                <dt className="text-ink-muted">Доминант</dt>
                <dd className="font-medium text-ink">{item.stats.dominantEmotion}</dd>
              </div>
              {item.stats.confidence !== undefined && (
                <div className="flex justify-between">
                  <dt className="text-ink-muted">Уверенность</dt>
                  <dd className="font-mono text-ink">{item.stats.confidence.toFixed(1)}%</dd>
                </div>
              )}
              <div className="flex justify-between">
                <dt className="text-ink-muted">Модель</dt>
                <dd className="font-medium text-ink">{item.modelName}</dd>
              </div>
            </dl>
            {item.stats.note && (
              <p className="mt-4 pt-4 border-t border-line text-xs text-ink-muted leading-relaxed">
                {item.stats.note}
              </p>
            )}
          </div>

          <div className="flex flex-col gap-2">
            <a
              href={item.mediaUrl}
              download
              className="btn-secondary text-center"
            >
              Скачать {item.kind === 'video' ? 'видео' : 'изображение'}
            </a>
            {item.kind === 'video' && item.statisticsUrl && (
              <a
                href={item.statisticsUrl}
                download
                className="btn-secondary text-center"
              >
                Скачать статистику
              </a>
            )}
            <LinkButton variant="primary" to={`/process/${item.kind}?model=${item.model}`}>
              Попробовать на своём медиа
            </LinkButton>
          </div>
        </div>
      </div>

      {/* Для видео — встраиваем готовую Plotly-статистику ниже плеера. */}
      {item.kind === 'video' && item.statisticsUrl && (
        <section className="mt-10">
          <h2 className="text-xl md:text-2xl font-display font-semibold text-ink mb-4">
            Статистика по трекам
          </h2>
          <div className="card overflow-hidden">
            <iframe
              src={item.statisticsUrl}
              title={`Статистика — ${item.title}`}
              className="w-full"
              style={{ height: '1400px', border: 'none' }}
            />
          </div>
        </section>
      )}
    </motion.div>
  );
}
