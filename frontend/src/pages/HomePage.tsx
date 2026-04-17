import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { GradientMesh } from '../components/ui/GradientBlob';
import { SectionHeading } from '../components/ui/SectionHeading';
import { LinkButton } from '../components/ui/Button';
import { StatTile } from '../components/common/StatTile';

const pageVariants = {
  initial: { opacity: 0, y: 10 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -6 },
};

const navCards = [
  {
    to: '/models',
    title: 'Архитектуры',
    description: 'Четыре нейросети для классификации эмоций — от классических CNN до визуальных трансформеров',
    cta: 'Подробнее',
  },
  {
    to: '/process/photo',
    title: 'Обработка',
    description: 'Загрузите своё фото или видео — увидите аннотированный результат и подробную статистику эмоций',
    cta: 'Перейти',
  },
  {
    to: '/gallery',
    title: 'Демо-галерея',
    description: 'Готовые примеры обработки — посмотрите результаты работы моделей без собственных загрузок',
    cta: 'Открыть',
  },
];

const steps = [
  { n: '1', title: 'Детекция', text: 'Находим лица на кадре при помощи MediaPipe' },
  { n: '2', title: 'Выравнивание', text: 'Приводим лица к каноническому виду ArcFace' },
  { n: '3', title: 'Трекинг', text: 'Следим за людьми по IoU и реидентификации' },
  { n: '4', title: 'Классификация', text: 'Определяем эмоцию выбранной нейросетью' },
];

export default function HomePage() {
  return (
    <motion.div variants={pageVariants} initial="initial" animate="animate" exit="exit">
      {/* Hero */}
      <section className="relative overflow-hidden">
        <GradientMesh />
        <div className="mx-auto max-w-7xl px-4 md:px-8 py-20 md:py-28 relative">
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="max-w-3xl"
          >
            <span className="eyebrow">Выпускной проект</span>
            <h1 className="mt-4 text-5xl md:text-6xl lg:text-7xl font-display font-semibold leading-[1.05]">
              Распознавание <span className="brand-text">эмоций</span>
              <br />
              на фото и видео
            </h1>
            <p className="mt-6 text-lg md:text-xl text-ink-muted max-w-2xl leading-relaxed">
              Интеллектуальный анализ лиц с помощью четырёх нейросетевых архитектур.
              Сравните модели, загрузите собственное медиа или посмотрите готовые примеры.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <LinkButton to="/process/photo" variant="primary">
                Начать
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M5 12h14m0 0l-5-5m5 5l-5 5" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </LinkButton>
              <LinkButton to="/gallery" variant="secondary">
                Посмотреть демо
              </LinkButton>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Navigation cards */}
      <section className="mx-auto max-w-7xl px-4 md:px-8 pb-16">
        <div className="grid gap-5 md:grid-cols-3">
          {navCards.map((card, i) => (
            <motion.div
              key={card.to}
              initial={{ opacity: 0, y: 14 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.08 }}
            >
              <Link to={card.to} className="block h-full">
                <div className="card-interactive p-7 h-full flex flex-col">
                  <div className="w-10 h-10 rounded-xl bg-brand-gradient shadow-glow mb-5" />
                  <h3 className="text-xl font-display font-semibold text-ink">{card.title}</h3>
                  <p className="mt-2 text-ink-muted leading-relaxed text-sm flex-1">
                    {card.description}
                  </p>
                  <div className="mt-5 flex items-center gap-1.5 text-primary-deep font-medium">
                    {card.cta}
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path d="M5 12h14m0 0l-5-5m5 5l-5 5" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </div>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="mx-auto max-w-7xl px-4 md:px-8 py-16 border-t border-line">
        <SectionHeading
          eyebrow="Процесс"
          title="Как это работает"
          subtitle="Каждое изображение проходит через четыре этапа. Результат — распределение вероятностей по восьми эмоциям для каждого найденного лица."
        />
        <div className="mt-10 grid gap-4 md:grid-cols-4 relative">
          <div className="hidden md:block absolute top-6 left-[12%] right-[12%] h-px bg-divider-gradient -z-0" />
          {steps.map((step, i) => (
            <motion.div
              key={step.n}
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.35, delay: i * 0.08 }}
              className="relative flex flex-col items-center text-center gap-3"
            >
              <div className="w-12 h-12 rounded-full bg-surface border-2 border-primary/40 flex items-center justify-center font-display font-semibold text-primary-deep z-10 shadow-card">
                {step.n}
              </div>
              <h4 className="font-display font-semibold text-ink">{step.title}</h4>
              <p className="text-sm text-ink-muted leading-relaxed max-w-[220px]">{step.text}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Stats */}
      <section className="mx-auto max-w-7xl px-4 md:px-8 py-16 border-t border-line">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          <StatTile value="8" label="эмоций" sublabel="полный спектр" />
          <StatTile value="4" label="модели" sublabel="CNN и трансформеры" />
          <StatTile value="74.0%" label="лучшая accuracy" sublabel="ConvNeXt-Tiny на валидации" />
          <StatTile value="4.7 мс" label="инференс · GPU" sublabel="ConvNeXt-Tiny · batch 1" />
        </div>
      </section>
    </motion.div>
  );
}
