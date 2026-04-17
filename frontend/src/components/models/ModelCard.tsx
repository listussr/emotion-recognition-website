import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Badge } from '../ui/Badge';
import type { ModelSpec } from '../../types/models';

interface ModelCardProps {
  model: ModelSpec;
  index?: number;
}

export function ModelCard({ model, index = 0 }: ModelCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay: index * 0.06 }}
    >
      <Link to={`/models/${model.key}`} className="block h-full">
        <div className="card-interactive h-full p-6 flex flex-col gap-4">
          <div className="flex items-center gap-2">
            <Badge tone={model.family === 'ViT' ? 'accent' : 'primary'}>{model.family}</Badge>
            <span className="text-xs text-ink-muted font-mono">{model.params} параметров</span>
          </div>

          <div>
            <h3 className="text-xl font-display font-semibold text-ink">{model.name}</h3>
            <p className="text-sm text-ink-muted mt-1">{model.tagline}</p>
          </div>

          <p className="text-sm text-ink-muted leading-relaxed flex-1">{model.description}</p>

          <div className="flex items-center gap-3 pt-3 border-t border-line-soft text-xs">
            <div className="flex flex-col">
              <span className="text-[10px] uppercase tracking-wider text-ink-muted">Accuracy</span>
              <span className="font-mono brand-text font-semibold text-sm">
                {(model.accuracy * 100).toFixed(2)}%
              </span>
            </div>
            <div className="flex flex-col">
              <span className="text-[10px] uppercase tracking-wider text-ink-muted">GPU</span>
              <span className="font-mono text-ink text-sm">{model.inferenceMs.toFixed(2)} мс</span>
            </div>
            <div className="flex flex-col">
              <span className="text-[10px] uppercase tracking-wider text-ink-muted">Размер</span>
              <span className="font-mono text-ink text-sm">{model.sizeMb} МБ</span>
            </div>
          </div>

          <div className="flex items-center justify-end pt-1">
            <span className="text-sm font-medium text-primary-deep flex items-center gap-1.5">
              Подробнее
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M5 12h14m0 0l-5-5m5 5l-5 5" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </span>
          </div>
        </div>
      </Link>
    </motion.div>
  );
}
