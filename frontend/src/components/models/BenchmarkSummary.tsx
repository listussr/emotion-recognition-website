import type { ModelKey } from '../../types/api';
import { MODEL_BENCHMARK } from '../../data/metrics';

interface Props {
  modelKey: ModelKey;
}

// Карточка «лучших чисел» по модели.
export function BenchmarkSummary({ modelKey }: Props) {
  const rows = MODEL_BENCHMARK[modelKey];
  const b1 = rows.find((r) => r.batch === 1)!;
  const b16 = rows.find((r) => r.batch === 16)!;

  // Best number per mode — минимальная задержка batch=1 и максимальный FPS batch=16.
  const bestLatency = Math.min(b1.pt_gpu_ms, b1.onnx_gpu_ms);
  const bestLatencyLabel = b1.pt_gpu_ms <= b1.onnx_gpu_ms ? 'PyTorch · GPU' : 'ONNX · GPU';
  const bestFps = Math.max(b16.pt_gpu_fps, b16.onnx_gpu_fps);
  const bestFpsLabel = b16.pt_gpu_fps >= b16.onnx_gpu_fps ? 'PyTorch · GPU' : 'ONNX · GPU';

  return (
    <div className="card p-6 h-full">
      <h3 className="font-display font-semibold text-ink mb-1">Сводка</h3>
      <p className="text-xs text-ink-muted mb-5">Бенчмарк на валидационной выборке</p>

      <div className="space-y-4">
        <Row
          title="Минимальная задержка"
          value={`${bestLatency.toFixed(2)} мс`}
          caption={`batch = 1 · ${bestLatencyLabel}`}
          tone="primary"
        />
        <Row
          title="Максимальный FPS"
          value={`${bestFps.toFixed(0)}`}
          caption={`batch = 16 · ${bestFpsLabel}`}
          tone="accent"
        />
        <Row
          title="GPU-память"
          value={`${b1.gpu_mem_mb.toFixed(0)} МБ`}
          caption="в среднем на инференсе"
        />
        <Row
          title="CPU-инференс"
          value={`${b1.pt_cpu_ms.toFixed(1)} мс`}
          caption={`PyTorch · batch=1 · ${b1.pt_cpu_fps.toFixed(1)} FPS`}
        />
      </div>
    </div>
  );
}

function Row({
  title,
  value,
  caption,
  tone,
}: {
  title: string;
  value: string;
  caption: string;
  tone?: 'primary' | 'accent';
}) {
  return (
    <div className="flex items-start justify-between gap-3 py-2 border-b border-line-soft last:border-0">
      <div className="flex-1">
        <div className="text-xs text-ink-muted">{title}</div>
        <div className="text-[11px] text-ink-muted/80 mt-0.5">{caption}</div>
      </div>
      <div
        className={`font-mono text-lg ${
          tone === 'primary' ? 'brand-text font-semibold' : tone === 'accent' ? 'text-accent font-semibold' : 'text-ink'
        }`}
      >
        {value}
      </div>
    </div>
  );
}
