import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { getGalleryItem } from '../data/gallery';
import { Badge } from '../components/ui/Badge';
import { Button, LinkButton } from '../components/ui/Button';
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
          <div
            className="aspect-video relative flex items-center justify-center"
            style={{ background: item.thumbnailGradient }}
          >
            <div className="text-center text-white/90">
              <div className="text-sm font-mono uppercase tracking-wider opacity-75">
                Плейсхолдер
              </div>
              <div className="mt-1 text-base font-display">
                Демо-медиа будет подгружено позднее
              </div>
            </div>
            {item.kind === 'video' && (
              <div className="absolute w-16 h-16 rounded-full bg-white/90 flex items-center justify-center shadow-xl">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" className="text-primary-deep ml-1">
                  <path d="M8 5v14l11-7z" />
                </svg>
              </div>
            )}
          </div>
        </div>

        <div className="flex flex-col gap-4">
          <div className="card p-5">
            <h4 className="font-display font-semibold text-ink mb-4">Сводка</h4>
            <dl className="space-y-3 text-sm">
              <div className="flex justify-between">
                <dt className="text-ink-muted">Лиц в сессии</dt>
                <dd className="font-mono text-ink">{item.stats.faces}</dd>
              </div>
              {item.stats.duration && (
                <div className="flex justify-between">
                  <dt className="text-ink-muted">Длительность</dt>
                  <dd className="font-mono text-ink">{item.stats.duration.toFixed(1)} с</dd>
                </div>
              )}
              <div className="flex justify-between">
                <dt className="text-ink-muted">Доминант</dt>
                <dd className="font-medium text-ink">{item.stats.dominantEmotion}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-ink-muted">Модель</dt>
                <dd className="font-medium text-ink">{item.modelName}</dd>
              </div>
            </dl>
          </div>

          <div className="flex flex-col gap-2">
            <Button variant="secondary" disabled>
              Скачать {item.kind === 'video' ? 'видео' : 'изображение'}
            </Button>
            {item.kind === 'video' && (
              <Button variant="secondary" disabled>
                Скачать статистику
              </Button>
            )}
            <LinkButton variant="primary" to={`/process/${item.kind}?model=${item.model}`}>
              Попробовать на своём медиа
            </LinkButton>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
