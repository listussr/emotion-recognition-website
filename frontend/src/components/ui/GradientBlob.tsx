interface GradientBlobProps {
  className?: string;
  variant?: 'primary' | 'accent';
}

/**
 * Декоративный «размытый шарик» на фоне. Используется в hero-секциях.
 */
export function GradientBlob({ className = '', variant = 'primary' }: GradientBlobProps) {
  const gradient =
    variant === 'accent'
      ? 'radial-gradient(circle at 30% 30%, #C4B5FD 0%, #818CF8 45%, transparent 70%)'
      : 'radial-gradient(circle at 30% 30%, #A5B4FC 0%, #60A5FA 45%, transparent 70%)';

  return (
    <div
      aria-hidden
      className={`pointer-events-none absolute -z-10 animate-float ${className}`}
      style={{
        background: gradient,
        filter: 'blur(110px)',
        opacity: 0.55,
      }}
    />
  );
}

export function GradientMesh() {
  return (
    <div aria-hidden className="pointer-events-none absolute inset-0 -z-10 overflow-hidden">
      <GradientBlob className="top-[-20%] left-[-10%] w-[600px] h-[600px]" variant="primary" />
      <GradientBlob className="top-[-30%] right-[-10%] w-[500px] h-[500px]" variant="accent" />
    </div>
  );
}
