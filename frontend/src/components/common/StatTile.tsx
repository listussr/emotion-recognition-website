interface StatTileProps {
  value: string;
  label: string;
  sublabel?: string;
  align?: 'left' | 'center';
}

export function StatTile({ value, label, sublabel, align = 'left' }: StatTileProps) {
  return (
    <div className={`flex flex-col gap-1 ${align === 'center' ? 'items-center text-center' : ''}`}>
      <div className="text-3xl md:text-4xl font-display font-semibold mono-stat brand-text">
        {value}
      </div>
      <div className="text-sm font-medium text-ink">{label}</div>
      {sublabel && <div className="text-xs text-ink-muted">{sublabel}</div>}
    </div>
  );
}
