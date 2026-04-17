import type { ModelKey } from '../../types/api';

interface ModelSchemaProps {
  modelKey: ModelKey;
  compact?: boolean;
}

/**
 * Упрощённая блок-схема архитектуры. Заглушка — заменим на полноценные
 * диаграммы или SVG-ассеты, когда они будут готовы.
 */
export function ModelSchema({ modelKey, compact = false }: ModelSchemaProps) {
  const blocks = getBlocks(modelKey);
  const height = compact ? 90 : 140;

  return (
    <div
      className="relative w-full rounded-xl bg-brand-gradient-soft overflow-hidden border border-line-soft"
      style={{ minHeight: height }}
    >
      <div className="absolute inset-0 flex items-center justify-between px-4 py-3 gap-1 md:gap-2">
        {blocks.map((block, i) => (
          <div key={i} className="flex items-center gap-1 md:gap-2 flex-1">
            <div
              className="flex-1 rounded-md flex items-center justify-center px-1 py-2 text-[10px] md:text-xs font-medium font-mono"
              style={{
                background: block.bg,
                color: block.color,
                minWidth: 0,
                minHeight: compact ? 46 : 70,
                border: `1px solid ${block.border}`,
              }}
            >
              <span className="truncate">{block.label}</span>
            </div>
            {i < blocks.length - 1 && (
              <svg width="14" height="14" viewBox="0 0 24 24" className="text-ink-soft flex-shrink-0">
                <path d="M5 12h14m0 0l-5-5m5 5l-5 5" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" />
              </svg>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

interface Block {
  label: string;
  bg: string;
  color: string;
  border: string;
}

function getBlocks(key: ModelKey): Block[] {
  const base = (label: string): Block => ({
    label,
    bg: 'rgba(255,255,255,0.9)',
    color: '#0F172A',
    border: '#DDE3F0',
  });
  const accent = (label: string, color: 'blue' | 'purple' = 'blue'): Block => ({
    label,
    bg:
      color === 'blue'
        ? 'linear-gradient(135deg, #DBEAFE, #BFDBFE)'
        : 'linear-gradient(135deg, #E9D5FF, #DDD6FE)',
    color: color === 'blue' ? '#1D4ED8' : '#6D28D9',
    border: color === 'blue' ? '#93C5FD' : '#C4B5FD',
  });

  switch (key) {
    case 'resnet_50':
      return [
        base('Вход 224×224'),
        accent('Conv 7×7'),
        accent('Res × 3'),
        accent('Res × 4'),
        accent('Res × 6'),
        accent('Res × 3'),
        base('Pool + FC'),
      ];
    case 'efficientnet_b3':
      return [
        base('Вход 300×300'),
        accent('Stem Conv'),
        accent('MBConv ×7'),
        accent('MBConv ×8'),
        accent('MBConv ×8'),
        base('Head + FC'),
      ];
    case 'convnext':
      return [
        base('Вход 224×224'),
        accent('Stem 4×4'),
        accent('Stage 1', 'purple'),
        accent('Stage 2', 'purple'),
        accent('Stage 3', 'purple'),
        accent('Stage 4', 'purple'),
        base('Norm + FC'),
      ];
    case 'swin':
      return [
        base('Вход 224×224'),
        accent('Patch 4×4', 'purple'),
        accent('W-MSA', 'purple'),
        accent('SW-MSA', 'purple'),
        accent('Merge', 'purple'),
        accent('Swin ×2', 'purple'),
        base('Norm + FC'),
      ];
    default:
      return [base('Вход'), base('Модель'), base('Выход')];
  }
}
