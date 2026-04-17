import { useMemo, useState } from 'react';
import type { ModelKey } from '../../types/api';
import { MODEL_BENCHMARK, type BenchmarkRow } from '../../data/metrics';

interface Props {
  modelKey: ModelKey;
}

type Metric = 'latency' | 'throughput';
type Device = 'cpu' | 'gpu';

interface Backend {
  id: string;
  label: string;
  color: string;
  msField: keyof BenchmarkRow;
  fpsField: keyof BenchmarkRow;
}

const CPU_BACKENDS: Backend[] = [
  { id: 'pt_cpu', label: 'PyTorch', color: '#93A5C9', msField: 'pt_cpu_ms', fpsField: 'pt_cpu_fps' },
  { id: 'onnx_cpu', label: 'ONNX', color: '#C4B5FD', msField: 'onnx_cpu_ms', fpsField: 'onnx_cpu_fps' },
];

const GPU_BACKENDS: Backend[] = [
  { id: 'pt_gpu', label: 'PyTorch', color: '#4F7CFF', msField: 'pt_gpu_ms', fpsField: 'pt_gpu_fps' },
  { id: 'onnx_gpu', label: 'ONNX', color: '#8B5CF6', msField: 'onnx_gpu_ms', fpsField: 'onnx_gpu_fps' },
];

export function PerformanceCharts({ modelKey }: Props) {
  const rows = MODEL_BENCHMARK[modelKey];
  const [metric, setMetric] = useState<Metric>('latency');

  return (
    <div className="card p-6">
      <div className="flex items-start justify-between flex-wrap gap-3 mb-5">
        <div>
          <h3 className="font-display font-semibold text-ink">
            {metric === 'latency' ? 'Время обработки батча' : 'Пропускная способность'}
          </h3>
          <p className="text-xs text-ink-muted mt-1">
            CPU и GPU показаны отдельно — масштабы разные на порядок
          </p>
        </div>
        <div className="inline-flex rounded-xl bg-bg p-1 border border-line-soft text-xs">
          {(['latency', 'throughput'] as const).map((m) => (
            <button
              key={m}
              onClick={() => setMetric(m)}
              className={`px-3 py-1.5 rounded-lg transition-colors ${
                metric === m ? 'text-white shadow-sm' : 'text-ink-muted hover:text-ink'
              }`}
              style={
                metric === m
                  ? { background: 'linear-gradient(135deg,#4F7CFF,#8B5CF6)' }
                  : undefined
              }
            >
              {m === 'latency' ? 'Задержка' : 'FPS'}
            </button>
          ))}
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <SubChart
          title="CPU"
          rows={rows}
          backends={CPU_BACKENDS}
          metric={metric}
          device="cpu"
        />
        <SubChart
          title="GPU"
          rows={rows}
          backends={GPU_BACKENDS}
          metric={metric}
          device="gpu"
        />
      </div>
    </div>
  );
}

function SubChart({
  title,
  rows,
  backends,
  metric,
  device,
}: {
  title: string;
  rows: BenchmarkRow[];
  backends: Backend[];
  metric: Metric;
  device: Device;
}) {
  const { maxValue, unit } = useMemo(() => {
    const field = metric === 'latency' ? 'msField' : 'fpsField';
    let max = 0;
    rows.forEach((r) => {
      backends.forEach((b) => {
        const v = r[b[field]] as number;
        if (v > max) max = v;
      });
    });
    return {
      maxValue: max * 1.1 || 1,
      unit: metric === 'latency' ? 'мс' : 'FPS',
    };
  }, [rows, backends, metric]);

  // Геометрия SVG
  const width = 440;
  const height = 260;
  const pad = { top: 14, right: 14, bottom: 40, left: 48 };
  const plotW = width - pad.left - pad.right;
  const plotH = height - pad.top - pad.bottom;

  const groupWidth = plotW / rows.length;
  const innerPad = 14;
  const barW = (groupWidth - innerPad * 2) / backends.length;

  const ticks = 4;
  const tickStep = maxValue / ticks;

  const accentColor = device === 'cpu' ? '#93A5C9' : '#4F7CFF';

  return (
    <div>
      <div className="flex items-center gap-2 mb-3">
        <span
          className="inline-block w-2 h-2 rounded-full"
          style={{ background: accentColor }}
        />
        <h4 className="text-sm font-display font-semibold text-ink">{title}</h4>
      </div>

      <div className="w-full overflow-x-auto">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          preserveAspectRatio="xMidYMid meet"
          className="block w-full h-auto"
          style={{ minWidth: '320px' }}
        >
          {/* Сетка + Y-шкала */}
          {Array.from({ length: ticks + 1 }).map((_, i) => {
            const yVal = tickStep * i;
            const y = pad.top + plotH - (yVal / maxValue) * plotH;
            return (
              <g key={i}>
                <line
                  x1={pad.left}
                  x2={pad.left + plotW}
                  y1={y}
                  y2={y}
                  stroke="rgba(27,33,64,0.06)"
                  strokeDasharray={i === 0 ? '0' : '3 4'}
                />
                <text
                  x={pad.left - 8}
                  y={y + 4}
                  textAnchor="end"
                  style={{ fontSize: 10, fontFamily: 'JetBrains Mono, monospace' }}
                  className="fill-ink-muted"
                >
                  {yVal >= 1000 ? `${(yVal / 1000).toFixed(1)}k` : yVal.toFixed(0)}
                </text>
              </g>
            );
          })}

          {/* Столбцы */}
          {rows.map((row, gi) => {
            const gx = pad.left + gi * groupWidth + innerPad;
            return (
              <g key={row.batch}>
                {backends.map((b, bi) => {
                  const field = metric === 'latency' ? b.msField : b.fpsField;
                  const v = row[field] as number;
                  const h = (v / maxValue) * plotH;
                  const x = gx + bi * barW;
                  const y = pad.top + plotH - h;
                  return (
                    <rect
                      key={b.id}
                      x={x + 1}
                      y={y}
                      width={barW - 2}
                      height={Math.max(h, 0)}
                      rx={4}
                      fill={b.color}
                    >
                      <title>{`${b.label} · batch ${row.batch}: ${v.toFixed(2)} ${unit}`}</title>
                    </rect>
                  );
                })}
                <text
                  x={pad.left + gi * groupWidth + groupWidth / 2}
                  y={pad.top + plotH + 18}
                  textAnchor="middle"
                  className="fill-ink-muted"
                  style={{ fontSize: 11, fontFamily: 'Inter, sans-serif' }}
                >
                  batch = {row.batch}
                </text>
              </g>
            );
          })}

          {/* Y-ось метка */}
          <text
            x={8}
            y={pad.top + plotH / 2}
            transform={`rotate(-90 8 ${pad.top + plotH / 2})`}
            textAnchor="middle"
            className="fill-ink-muted"
            style={{ fontSize: 11, fontFamily: 'Inter, sans-serif' }}
          >
            {unit}
          </text>
        </svg>
      </div>

      <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-ink-muted">
        {backends.map((b) => (
          <div key={b.id} className="flex items-center gap-1.5">
            <span
              className="inline-block h-2.5 w-2.5 rounded-full"
              style={{ background: b.color }}
            />
            {b.label}
          </div>
        ))}
      </div>
    </div>
  );
}
