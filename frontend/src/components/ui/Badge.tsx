import type { ReactNode } from 'react';

interface BadgeProps {
  children: ReactNode;
  tone?: 'primary' | 'accent' | 'muted';
  className?: string;
}

export function Badge({ children, tone = 'primary', className = '' }: BadgeProps) {
  const toneClass =
    tone === 'accent'
      ? 'bg-accent-soft text-accent-deep'
      : tone === 'muted'
        ? 'bg-line-soft text-ink-muted'
        : 'bg-primary-soft text-primary-deep';

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-wider ${toneClass} ${className}`}
    >
      {children}
    </span>
  );
}
