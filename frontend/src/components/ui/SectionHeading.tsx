import type { ReactNode } from 'react';

interface SectionHeadingProps {
  eyebrow?: string;
  title: string;
  subtitle?: string;
  children?: ReactNode;
  align?: 'left' | 'center';
  className?: string;
}

export function SectionHeading({
  eyebrow,
  title,
  subtitle,
  children,
  align = 'left',
  className = '',
}: SectionHeadingProps) {
  const alignClass = align === 'center' ? 'text-center items-center' : 'text-left items-start';
  return (
    <div className={`flex flex-col gap-3 ${alignClass} ${className}`}>
      {eyebrow && <span className="eyebrow">{eyebrow}</span>}
      <h2 className="text-3xl md:text-4xl font-display font-semibold text-ink">{title}</h2>
      {subtitle && (
        <p className="max-w-2xl text-ink-muted text-base md:text-lg leading-relaxed">{subtitle}</p>
      )}
      {children}
    </div>
  );
}

export function PageHeading({
  eyebrow,
  title,
  subtitle,
}: {
  eyebrow?: string;
  title: string;
  subtitle?: string;
}) {
  return (
    <div className="flex flex-col gap-3 mb-10">
      {eyebrow && <span className="eyebrow">{eyebrow}</span>}
      <h1 className="text-4xl md:text-5xl font-display font-semibold text-ink leading-tight">
        {title}
      </h1>
      {subtitle && (
        <p className="max-w-3xl text-ink-muted text-lg leading-relaxed">{subtitle}</p>
      )}
    </div>
  );
}
