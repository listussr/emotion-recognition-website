import { motion } from 'framer-motion';

interface LoadingRingsProps {
  message?: string;
  hint?: string;
}

/**
 * Три пульсирующих кольца с градиентной заливкой — индикатор ожидания обработки.
 */
export function LoadingRings({
  message = 'Обработка...',
  hint = 'Это займёт несколько секунд',
}: LoadingRingsProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-6 py-12">
      <div className="relative w-32 h-32">
        {[0, 1, 2].map((i) => (
          <motion.div
            key={i}
            className="absolute inset-0 rounded-full border-2 border-primary/70"
            style={{
              borderColor: i === 1 ? '#8B5CF6' : '#4F7CFF',
            }}
            animate={{
              scale: [0.9, 1.25, 0.9],
              opacity: [0.7, 0, 0.7],
            }}
            transition={{
              duration: 2.2,
              ease: 'easeInOut',
              repeat: Infinity,
              delay: i * 0.4,
            }}
          />
        ))}
        <div className="absolute inset-0 flex items-center justify-center">
          <motion.div
            className="w-8 h-8 rounded-full bg-brand-gradient shadow-glow"
            animate={{ scale: [1, 1.12, 1] }}
            transition={{ duration: 1.6, repeat: Infinity, ease: 'easeInOut' }}
          />
        </div>
      </div>
      <div className="text-center">
        <p className="text-lg font-display font-medium text-ink">{message}</p>
        <p className="text-sm text-ink-muted mt-1">{hint}</p>
      </div>
    </div>
  );
}
