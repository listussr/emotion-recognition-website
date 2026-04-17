import { Link } from 'react-router-dom';
import type { ComponentPropsWithoutRef, ReactNode } from 'react';

type Variant = 'primary' | 'secondary' | 'ghost';

interface BaseProps {
  variant?: Variant;
  children: ReactNode;
  className?: string;
}

function variantClass(variant: Variant = 'primary') {
  switch (variant) {
    case 'secondary':
      return 'btn-secondary';
    case 'ghost':
      return 'btn-ghost';
    default:
      return 'btn-primary';
  }
}

type ButtonProps = BaseProps & ComponentPropsWithoutRef<'button'>;

export function Button({ variant, className = '', children, ...rest }: ButtonProps) {
  return (
    <button className={`${variantClass(variant)} ${className}`} {...rest}>
      {children}
    </button>
  );
}

type LinkButtonProps = BaseProps & {
  to: string;
  onClick?: () => void;
};

export function LinkButton({ variant, className = '', children, to, onClick }: LinkButtonProps) {
  return (
    <Link to={to} onClick={onClick} className={`${variantClass(variant)} ${className}`}>
      {children}
    </Link>
  );
}
