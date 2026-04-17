import { useState } from 'react';
import { motion } from 'framer-motion';
import { PageHeading } from '../components/ui/SectionHeading';
import { GalleryCard } from '../components/gallery/GalleryCard';
import { GALLERY } from '../data/gallery';

type Filter = 'all' | 'photo' | 'video';

const filters: { id: Filter; label: string }[] = [
  { id: 'all', label: 'Всё' },
  { id: 'photo', label: 'Фото' },
  { id: 'video', label: 'Видео' },
];

export default function GalleryPage() {
  const [filter, setFilter] = useState<Filter>('all');
  const items = GALLERY.filter((g) => (filter === 'all' ? true : g.kind === filter));

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -4 }}
      transition={{ duration: 0.3 }}
      className="mx-auto max-w-7xl px-4 md:px-8 py-12 md:py-16"
    >
      <PageHeading
        eyebrow="Примеры"
        title="Демо-результаты"
        subtitle="Готовые результаты работы моделей — можно посмотреть сразу, без собственных загрузок."
      />

      <div className="inline-flex bg-line-soft p-1 rounded-xl mb-8">
        {filters.map((f) => (
          <button
            key={f.id}
            onClick={() => setFilter(f.id)}
            className={`px-5 py-2 rounded-lg text-sm font-medium transition-all ${
              filter === f.id ? 'bg-white text-ink shadow-card' : 'text-ink-muted hover:text-ink'
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {items.map((item, i) => (
          <GalleryCard key={item.id} item={item} index={i} />
        ))}
      </div>

      {items.length === 0 && (
        <div className="card p-10 text-center text-ink-muted">Нет результатов для фильтра</div>
      )}
    </motion.div>
  );
}
