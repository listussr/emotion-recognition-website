import { useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import { Button } from '../ui/Button';
import { downloadBase64, downloadHtml } from '../../utils/download';
import type { VideoResponse } from '../../types/api';

interface VideoResultViewProps {
  result: VideoResponse;
}

export function VideoResultView({ result }: VideoResultViewProps) {
  const videoSrc = useMemo(
    () => `data:video/mp4;base64,${result.result_video}`,
    [result.result_video],
  );
  const [showStats, setShowStats] = useState(false);

  const handleDownloadVideo = () => {
    downloadBase64(result.result_video, 'video/mp4', 'result.mp4');
  };
  const handleDownloadStats = () => {
    downloadHtml(result.statistics_html, 'statistics.html');
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className="flex flex-col gap-4"
    >
      <div className="card overflow-hidden bg-black">
        <video src={videoSrc} controls className="w-full h-auto block" />
      </div>

      <div className="card p-5 flex flex-wrap items-center gap-5 justify-between">
        <div className="flex flex-wrap gap-5">
          <div>
            <div className="text-xs text-ink-muted">Длительность</div>
            <div className="text-xl font-display font-semibold mono-stat">
              {result.duration_sec.toFixed(1)} с
            </div>
          </div>
          <div className="w-px bg-line" />
          <div>
            <div className="text-xs text-ink-muted">FPS обработки</div>
            <div className="text-xl font-display font-semibold mono-stat">
              {result.processing_fps.toFixed(2)}
            </div>
          </div>
          <div className="w-px bg-line" />
          <div>
            <div className="text-xs text-ink-muted">Кадров обработано</div>
            <div className="text-xl font-display font-semibold mono-stat">
              {result.total_frames_processed}
            </div>
          </div>
        </div>

        <div className="flex gap-2 flex-wrap">
          <Button variant="secondary" onClick={handleDownloadVideo}>
            Скачать видео
          </Button>
          {result.statistics_html && (
            <Button variant="primary" onClick={handleDownloadStats}>
              Скачать статистику
            </Button>
          )}
        </div>
      </div>

      {result.statistics_html && (
        <div className="card overflow-hidden">
          <button
            type="button"
            onClick={() => setShowStats((s) => !s)}
            className="w-full flex items-center justify-between p-5 text-left hover:bg-line-soft/40 transition-colors"
          >
            <div>
              <h4 className="font-display font-semibold text-ink">Подробная статистика</h4>
              <p className="text-xs text-ink-muted mt-0.5">
                Графики эмоций по каждому лицу, сводка сессии
              </p>
            </div>
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              className={`text-ink-muted transition-transform ${showStats ? 'rotate-180' : ''}`}
            >
              <path d="M6 9l6 6 6-6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
          {showStats && (
            <iframe
              srcDoc={result.statistics_html}
              title="Статистика"
              className="w-full border-0 bg-white"
              style={{ height: 900 }}
            />
          )}
        </div>
      )}
    </motion.div>
  );
}
