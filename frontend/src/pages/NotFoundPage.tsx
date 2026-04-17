import { motion } from 'framer-motion';
import { LinkButton } from '../components/ui/Button';

export default function NotFoundPage() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -4 }}
      transition={{ duration: 0.3 }}
      className="mx-auto max-w-2xl px-4 md:px-8 py-24 text-center"
    >
      <div className="text-7xl font-display font-semibold brand-text mb-4">404</div>
      <h1 className="text-2xl md:text-3xl font-display font-semibold text-ink">
        Страница не найдена
      </h1>
      <p className="mt-3 text-ink-muted">
        Возможно, вы перешли по устаревшей ссылке или ввели адрес с опечаткой.
      </p>
      <div className="mt-8">
        <LinkButton to="/" variant="primary">
          На главную
        </LinkButton>
      </div>
    </motion.div>
  );
}
