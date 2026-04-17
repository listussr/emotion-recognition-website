import { motion } from 'framer-motion';
import { MODELS } from '../data/models';
import { ModelCard } from '../components/models/ModelCard';
import { ModelComparison } from '../components/models/ModelComparison';
import { PageHeading } from '../components/ui/SectionHeading';

export default function ModelsPage() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -4 }}
      transition={{ duration: 0.3 }}
      className="mx-auto max-w-7xl px-4 md:px-8 py-12 md:py-16"
    >
      <PageHeading
        eyebrow="Модели"
        title="Нейросетевые архитектуры"
        subtitle="Четыре подхода к классификации эмоций — от классических свёрточных сетей до современных визуальных трансформеров. Нажмите на карточку, чтобы увидеть метрики, карты градиентов и характеристики."
      />

      <div className="mb-10">
        <ModelComparison />
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {MODELS.map((model, i) => (
          <ModelCard key={model.key} model={model} index={i} />
        ))}
      </div>
    </motion.div>
  );
}
