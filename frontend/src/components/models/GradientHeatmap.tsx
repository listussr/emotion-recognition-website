import { useState } from 'react';
import type { ModelKey } from '../../types/api';
import { GRADIENT_MAPS } from '../../data/metrics';

interface Props {
  modelKey: ModelKey;
}

// Отображение Grad-CAM / attention rollout картинок, приложенных из ноутбука.
export function GradientHeatmap({ modelKey }: Props) {
  const maps = GRADIENT_MAPS[modelKey] ?? [];
  const [active, setActive] = useState(0);
  if (maps.length === 0) return null;
  const current = maps[active];

  return (
    <div className="card p-6">
      <div className="flex items-end justify-between gap-3 flex-wrap mb-4">
        <div>
          <h3 className="font-display font-semibold text-ink">Карты градиентов</h3>
          <p className="text-xs text-ink-muted mt-1">
            Активации, на которые модель опирается при принятии решения
          </p>
        </div>
        {maps.length > 1 && (
          <div className="inline-flex gap-1 rounded-xl bg-bg p-1 border border-line-soft text-xs">
            {maps.map((_, i) => (
              <button
                key={i}
                onClick={() => setActive(i)}
                className={`px-3 py-1.5 rounded-lg transition-colors ${
                  active === i ? 'text-white' : 'text-ink-muted hover:text-ink'
                }`}
                style={
                  active === i
                    ? { background: 'linear-gradient(135deg,#4F7CFF,#8B5CF6)' }
                    : undefined
                }
              >
                Вариант {i + 1}
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="relative rounded-2xl overflow-hidden border border-line-soft bg-bg">
        <img
          src={current.src}
          alt={current.caption}
          className="block w-full h-auto"
          loading="lazy"
        />
      </div>

      <p className="mt-3 text-xs text-ink-muted">{current.caption}</p>
    </div>
  );
}
