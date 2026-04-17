import { motion } from 'framer-motion';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import { downloadBase64 } from '../../utils/download';
import { EMOTION_LABELS_RU, EMOTION_COLORS, type EmotionKey } from '../../types/models';
import type { PhotoResponse } from '../../types/api';

interface PhotoResultViewProps {
  result: PhotoResponse;
}

export function PhotoResultView({ result }: PhotoResultViewProps) {
  const imageSrc = `data:image/jpeg;base64,${result.result_image}`;
  const faces = Object.entries(result.emotions);

  const handleDownload = () => {
    downloadBase64(result.result_image, 'image/jpeg', 'result.jpg');
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className="flex flex-col gap-4"
    >
      <div className="card overflow-hidden">
        <img src={imageSrc} alt="Результат" className="w-full h-auto block" />
      </div>

      <div className="card p-5 flex flex-wrap items-center gap-4 justify-between">
        <div className="flex gap-4">
          <div>
            <div className="text-xs text-ink-muted">Лиц обнаружено</div>
            <div className="text-xl font-display font-semibold mono-stat">{result.faces_num}</div>
          </div>
          <div className="w-px bg-line" />
          <div>
            <div className="text-xs text-ink-muted">Время обработки</div>
            <div className="text-xl font-display font-semibold mono-stat">
              {result.process_time.toFixed(2)} с
            </div>
          </div>
        </div>
        <Button variant="secondary" onClick={handleDownload}>
          Скачать изображение
        </Button>
      </div>

      {faces.length > 0 && (
        <div className="card p-5">
          <h4 className="font-display font-semibold text-ink mb-4">Эмоции по лицам</h4>
          <div className="grid gap-3">
            {faces.map(([faceId, emotion]) => {
              const emKey = emotion.label as EmotionKey;
              const ruLabel = EMOTION_LABELS_RU[emKey] ?? emotion.label;
              const topProb = emotion.probabilities[emotion.label] ?? 0;
              const color = EMOTION_COLORS[emKey] ?? '#4F7CFF';
              return (
                <div
                  key={faceId}
                  className="flex items-center justify-between gap-4 p-3 rounded-xl bg-line-soft/60"
                >
                  <div className="flex items-center gap-3">
                    <span
                      className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                      style={{ background: color }}
                    />
                    <span className="text-sm font-medium text-ink">
                      Лицо {faceId.replace('face_', '№')}
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    <Badge>{ruLabel}</Badge>
                    <span className="font-mono text-sm text-ink-muted">
                      {(topProb * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </motion.div>
  );
}
