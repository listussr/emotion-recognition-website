import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Badge } from '../ui/Badge';
import type { GalleryItem } from '../../types/models';

interface GalleryCardProps {
  item: GalleryItem;
  index?: number;
}

export function GalleryCard({ item, index = 0 }: GalleryCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay: index * 0.05 }}
    >
      <Link to={`/gallery/${item.id}`} className="block h-full">
        <div className="card-interactive h-full overflow-hidden flex flex-col">
          <div
            className="aspect-[16/10] relative overflow-hidden"
            style={{ background: item.thumbnailGradient }}
          >
            <div className="absolute inset-0 flex items-end p-4">
              <div className="flex gap-2">
                <Badge tone={item.kind === 'video' ? 'accent' : 'primary'}>
                  {item.kind === 'video' ? 'Видео' : 'Фото'}
                </Badge>
                <Badge tone="muted">{item.modelName}</Badge>
              </div>
            </div>
            {item.kind === 'video' && (
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-14 h-14 rounded-full bg-white/85 flex items-center justify-center shadow-lg">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" className="text-primary-deep ml-1">
                  <path d="M8 5v14l11-7z" />
                </svg>
              </div>
            )}
          </div>

          <div className="p-5 flex-1 flex flex-col">
            <h3 className="font-display font-semibold text-ink">{item.title}</h3>
            <p className="text-sm text-ink-muted mt-1 flex-1 line-clamp-2">{item.description}</p>

            <div className="flex items-center justify-between mt-4 pt-4 border-t border-line text-xs font-mono text-ink-muted">
              <span>
                Лиц: <span className="text-ink">{item.stats.faces}</span>
              </span>
              {item.stats.duration && (
                <span>
                  Длит.: <span className="text-ink">{item.stats.duration.toFixed(1)} с</span>
                </span>
              )}
              <span className="text-primary-deep font-sans font-medium">Открыть →</span>
            </div>
          </div>
        </div>
      </Link>
    </motion.div>
  );
}
