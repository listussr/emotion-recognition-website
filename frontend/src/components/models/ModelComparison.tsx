import { MODELS } from '../../data/models';
import { MODEL_METRICS, MODEL_BENCHMARK } from '../../data/metrics';

// Сводный мини-график: точность + macro-F1 + GPU-задержка на одной сетке.
export function ModelComparison() {
  // Сортируем от самой точной к самой слабой.
  const entries = MODELS.map((m) => {
    const metrics = MODEL_METRICS[m.key];
    const perf = MODEL_BENCHMARK[m.key].find((r) => r.batch === 1)!;
    return {
      key: m.key,
      name: m.shortName,
      fullName: m.name,
      family: m.family,
      accuracy: metrics.accuracy,
      macroF1: metrics.macroF1,
      latency: perf.pt_gpu_ms,
    };
  }).sort((a, b) => b.accuracy - a.accuracy);

  const maxAcc = Math.max(...entries.map((e) => e.accuracy));
  const maxLat = Math.max(...entries.map((e) => e.latency));

  return (
    <div className="card p-6 md:p-8">
      <div className="flex items-end justify-between mb-6 flex-wrap gap-2">
        <div>
          <h3 className="font-display font-semibold text-ink">Сравнение архитектур</h3>
          <p className="text-xs text-ink-muted mt-1">
            Accuracy и macro-F1 на валидации, задержка — PyTorch · GPU · batch 1
          </p>
        </div>
        <div className="flex items-center gap-4 text-xs text-ink-muted">
          <Legend color="#4F7CFF" label="Accuracy" />
          <Legend color="#8B5CF6" label="Macro-F1" />
          <Legend color="#10B981" label="Задержка, мс" />
        </div>
      </div>

      <div className="space-y-6">
        {entries.map((e) => (
          <div
            key={e.key}
            className="grid items-center gap-3 sm:gap-4 grid-cols-[1fr_auto] sm:grid-cols-[160px_1fr_70px]"
          >
            <div className="col-span-2 sm:col-span-1 flex items-center justify-between sm:block">
              <div className="text-sm font-medium text-ink">{e.name}</div>
              <div className="text-[11px] text-ink-muted sm:mt-0.5">{e.family}</div>
            </div>

            <div className="col-span-2 sm:col-span-1 space-y-1.5">
              <Bar value={e.accuracy} max={maxAcc} color="#4F7CFF" label={`${(e.accuracy * 100).toFixed(2)}%`} />
              <Bar value={e.macroF1} max={maxAcc} color="#8B5CF6" label={`${(e.macroF1 * 100).toFixed(2)}%`} />
              <Bar value={e.latency} max={maxLat} color="#10B981" label={`${e.latency.toFixed(2)} мс`} reverseTone />
            </div>

            <div className="hidden sm:block text-right">
              <div className="font-mono text-lg brand-text font-semibold">
                {(e.accuracy * 100).toFixed(1)}
              </div>
              <div className="text-[11px] text-ink-muted">accuracy, %</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function Legend({ color, label }: { color: string; label: string }) {
  return (
    <div className="flex items-center gap-1.5">
      <span className="inline-block h-2.5 w-2.5 rounded-full" style={{ background: color }} />
      {label}
    </div>
  );
}

function Bar({
  value,
  max,
  color,
  label,
  reverseTone = false,
}: {
  value: number;
  max: number;
  color: string;
  label: string;
  reverseTone?: boolean;
}) {
  const pct = (value / max) * 100;
  return (
    <div className="relative h-4 rounded-full bg-line-soft overflow-hidden">
      <div
        className="absolute inset-y-0 left-0 rounded-full"
        style={{
          width: `${pct}%`,
          background: color,
          opacity: reverseTone ? 0.55 : 0.85,
          transition: 'width 700ms cubic-bezier(.2,.8,.2,1)',
        }}
      />
      <span
        className="absolute inset-y-0 right-2 flex items-center text-[11px] font-mono font-semibold text-ink"
      >
        {label}
      </span>
    </div>
  );
}
