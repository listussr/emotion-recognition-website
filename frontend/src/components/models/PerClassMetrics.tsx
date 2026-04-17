import { EMOTION_KEYS, EMOTION_LABELS_RU } from '../../types/models';
import type { ModelMetrics } from '../../data/metrics';

interface Props {
  metrics: ModelMetrics;
}

// Горизонтальный бар-чарт per-class: precision / recall / f1 на одной оси.
export function PerClassMetrics({ metrics }: Props) {
  const rows = EMOTION_KEYS.map((k) => ({
    key: k,
    label: EMOTION_LABELS_RU[k],
    ...metrics.perClass[k],
  }));

  const colors = {
    precision: '#4F7CFF',
    recall: '#8B5CF6',
    f1: '#10B981',
  };

  return (
    <div className="card p-6">
      <div className="flex items-end justify-between mb-5 flex-wrap gap-2">
        <div>
          <h3 className="font-display font-semibold text-ink">Метрики по классам</h3>
          <p className="text-xs text-ink-muted mt-1">Precision · Recall · F1 на валидационной выборке</p>
        </div>
        <div className="flex items-center gap-4 text-xs text-ink-muted">
          {([
            ['precision', 'Precision'],
            ['recall', 'Recall'],
            ['f1', 'F1'],
          ] as const).map(([k, lbl]) => (
            <div key={k} className="flex items-center gap-1.5">
              <span
                className="inline-block h-2.5 w-2.5 rounded-full"
                style={{ background: colors[k] }}
              />
              {lbl}
            </div>
          ))}
        </div>
      </div>

      <div className="space-y-5">
        {rows.map((r) => (
          <div
            key={r.key}
            className="grid items-center gap-3 md:gap-4 grid-cols-[1fr_auto] md:grid-cols-[150px_1fr_72px]"
          >
            <div className="col-span-2 md:col-span-1">
              <span className="text-sm font-medium text-ink">{r.label}</span>
            </div>
            <div className="col-span-2 md:col-span-1 space-y-1.5">
              {(['precision', 'recall', 'f1'] as const).map((field) => (
                <div key={field} className="relative h-3 rounded-full bg-line-soft overflow-hidden">
                  <div
                    className="absolute inset-y-0 left-0 rounded-full"
                    style={{
                      width: `${r[field] * 100}%`,
                      background: colors[field],
                      transition: 'width 600ms cubic-bezier(.2,.8,.2,1)',
                    }}
                  />
                  <span className="absolute inset-y-0 right-2 flex items-center text-[10px] font-mono font-semibold text-ink">
                    {(r[field] * 100).toFixed(1)}
                  </span>
                </div>
              ))}
            </div>
            <div className="hidden md:block text-right">
              <div className="font-mono text-sm brand-text font-semibold">
                {(r.f1 * 100).toFixed(1)}
              </div>
              <div className="text-[10px] text-ink-muted uppercase tracking-wider">F1</div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-3 text-sm">
        {[
          ['Accuracy', metrics.accuracy],
          ['Macro-F1', metrics.macroF1],
          ['Weighted-F1', metrics.weightedF1],
        ].map(([label, val]) => (
          <div
            key={label as string}
            className="rounded-2xl border border-line-soft bg-bg/60 p-3"
          >
            <div className="text-[11px] uppercase tracking-wider text-ink-muted">{label}</div>
            <div className="mt-1 font-display text-2xl brand-text">
              {(val as number).toFixed(4)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
