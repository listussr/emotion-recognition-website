import { useMemo, useState } from 'react';
import { EMOTION_KEYS, EMOTION_LABELS_RU } from '../../types/models';
import type { ModelMetrics } from '../../data/metrics';

interface Props {
  metrics: ModelMetrics;
  title?: string;
}

// Интерполяция между двумя hex-цветами (RGB, без sRGB-линеаризации — достаточно для UI).
function lerpHex(a: string, b: string, t: number): string {
  const toRGB = (h: string) => [
    parseInt(h.slice(1, 3), 16),
    parseInt(h.slice(3, 5), 16),
    parseInt(h.slice(5, 7), 16),
  ];
  const [ar, ag, ab] = toRGB(a);
  const [br, bg, bb] = toRGB(b);
  const mix = (x: number, y: number) => Math.round(x + (y - x) * t);
  const toHex = (n: number) => n.toString(16).padStart(2, '0');
  return `#${toHex(mix(ar, br))}${toHex(mix(ag, bg))}${toHex(mix(ab, bb))}`;
}

// Палитра: очень светлая лаванда → бренд-градиент (синий → фиолетовый).
function cellColor(value: number): string {
  if (value <= 0.001) return '#F5F7FB';
  // два сегмента: [0, 0.5] пастель → голубой, [0.5, 1] → фиолетовый.
  if (value <= 0.5) {
    return lerpHex('#EEF2FE', '#4F7CFF', value / 0.5);
  }
  return lerpHex('#4F7CFF', '#8B5CF6', (value - 0.5) / 0.5);
}

function textColor(value: number): string {
  return value > 0.35 ? '#FFFFFF' : '#1B2140';
}

export function ConfusionMatrix({ metrics, title = 'Матрица ошибок' }: Props) {
  const n = EMOTION_KEYS.length;
  const cells = useMemo(
    () => metrics.confusion.flatMap((row, i) => row.map((v, j) => ({ i, j, v }))),
    [metrics.confusion],
  );
  const [hover, setHover] = useState<{ i: number; j: number } | null>(null);

  // SVG-геометрия: фиксированная, viewBox масштабируется под ширину карточки.
  const cellSize = 56;
  const pad = { top: 14, left: 132, right: 14, bottom: 62 };
  const width = pad.left + cellSize * n + pad.right;
  const height = pad.top + cellSize * n + pad.bottom;

  return (
    <div className="card p-6">
      <div className="flex items-end justify-between flex-wrap gap-3 mb-4">
        <div>
          <h3 className="font-display font-semibold text-ink">{title}</h3>
          <p className="text-xs text-ink-muted mt-1">
            Значения нормализованы по строке · сумма строки = 1.0
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs text-ink-muted">
          <span>0.0</span>
          <div
            className="h-2.5 w-36 rounded-full"
            style={{
              background:
                'linear-gradient(to right, #EEF2FE 0%, #4F7CFF 50%, #8B5CF6 100%)',
            }}
          />
          <span>1.0</span>
        </div>
      </div>

      <div className="w-full overflow-x-auto">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          preserveAspectRatio="xMidYMid meet"
          className="block mx-auto h-auto"
          style={{ width: '100%', maxWidth: '640px', minWidth: '480px' }}
          role="img"
          aria-label="Нормализованная матрица ошибок"
        >
          {/* Подписи строк (истинный класс) */}
          {EMOTION_KEYS.map((k, i) => (
            <text
              key={`row-${k}`}
              x={pad.left - 10}
              y={pad.top + i * cellSize + cellSize / 2 + 4}
              textAnchor="end"
              className="fill-ink-muted"
              style={{ fontSize: 13, fontFamily: 'Inter, sans-serif' }}
            >
              {EMOTION_LABELS_RU[k]}
            </text>
          ))}

          {/* Подписи столбцов (предсказанный класс) — под углом */}
          {EMOTION_KEYS.map((k, j) => {
            const cx = pad.left + j * cellSize + cellSize / 2;
            const cy = pad.top + cellSize * n + 16;
            return (
              <text
                key={`col-${k}`}
                x={cx}
                y={cy}
                transform={`rotate(-40 ${cx} ${cy})`}
                textAnchor="end"
                className="fill-ink-muted"
                style={{ fontSize: 13, fontFamily: 'Inter, sans-serif' }}
              >
                {EMOTION_LABELS_RU[k]}
              </text>
            );
          })}

          {/* Ячейки */}
          {cells.map(({ i, j, v }) => {
            const isDiag = i === j;
            const isHover = hover && hover.i === i && hover.j === j;
            const x = pad.left + j * cellSize;
            const y = pad.top + i * cellSize;
            return (
              <g
                key={`${i}-${j}`}
                onMouseEnter={() => setHover({ i, j })}
                onMouseLeave={() => setHover(null)}
                style={{ cursor: 'pointer' }}
              >
                <rect
                  x={x + 2}
                  y={y + 2}
                  width={cellSize - 4}
                  height={cellSize - 4}
                  rx={8}
                  fill={cellColor(v)}
                  stroke={isDiag ? 'rgba(139,92,246,0.55)' : 'transparent'}
                  strokeWidth={isDiag ? 1.4 : 0}
                  style={{
                    transition: 'transform 150ms',
                    transformOrigin: `${x + cellSize / 2}px ${y + cellSize / 2}px`,
                    transform: isHover ? 'scale(1.06)' : 'scale(1)',
                    filter: isHover ? 'drop-shadow(0 6px 12px rgba(79,124,255,0.35))' : 'none',
                  }}
                />
                {v >= 0.01 && (
                  <text
                    x={x + cellSize / 2}
                    y={y + cellSize / 2 + 4}
                    textAnchor="middle"
                    style={{
                      fontSize: 13,
                      fontFamily: 'JetBrains Mono, monospace',
                      fill: textColor(v),
                      fontWeight: isDiag ? 600 : 400,
                      pointerEvents: 'none',
                    }}
                  >
                    {v >= 0.995 ? '1.00' : v.toFixed(2)}
                  </text>
                )}
              </g>
            );
          })}
        </svg>
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-3 text-xs text-ink-muted">
        <div className="flex items-center gap-2">
          <span>Ось Y — истинный класс</span>
        </div>
        <span className="text-line">·</span>
        <div className="flex items-center gap-2">
          <span>Ось X — предсказание</span>
        </div>
        {hover && (
          <>
            <span className="text-line">·</span>
            <div className="font-mono text-ink">
              {EMOTION_LABELS_RU[EMOTION_KEYS[hover.i]]}
              <span className="mx-1 text-ink-muted">→</span>
              {EMOTION_LABELS_RU[EMOTION_KEYS[hover.j]]}
              <span className="mx-1 text-ink-muted">=</span>
              <span className="brand-text font-semibold">
                {(metrics.confusion[hover.i][hover.j] * 100).toFixed(1)}%
              </span>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
