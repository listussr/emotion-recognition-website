import type { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  className?: string;
  interactive?: boolean;
}

export function Card({ children, className = '', interactive = false }: CardProps) {
  return (
    <div className={`${interactive ? 'card-interactive' : 'card'} ${className}`}>{children}</div>
  );
}
