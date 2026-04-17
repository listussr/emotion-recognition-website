import { useEffect, useState } from 'react';
import { useSearchParams, Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { PageHeading } from '../components/ui/SectionHeading';
import { FileUpload } from '../components/common/FileUpload';
import { ModelSelector } from '../components/common/ModelSelector';
import { Button } from '../components/ui/Button';
import { LoadingRings } from '../components/common/LoadingRings';
import { VideoResultView } from '../components/process/VideoResultView';
import { processVideo } from '../api/video';
import type { ModelKey, VideoResponse } from '../types/api';

type Status = 'idle' | 'processing' | 'done' | 'error';

const VALID_MODELS: ModelKey[] = ['resnet_50', 'efficientnet_b3', 'convnext', 'swin'];

function safeModel(raw: string | null): ModelKey {
  return (raw && (VALID_MODELS as string[]).includes(raw) ? raw : 'convnext') as ModelKey;
}

export default function ProcessVideoPage() {
  const [searchParams] = useSearchParams();
  const initialModel = safeModel(searchParams.get('model'));

  const [model, setModel] = useState<ModelKey>(initialModel);
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<Status>('idle');
  const [result, setResult] = useState<VideoResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setModel(initialModel);
  }, [initialModel]);

  const handleSubmit = async () => {
    if (!file) return;
    setStatus('processing');
    setError(null);
    try {
      const res = await processVideo(file, model);
      if (res.error) {
        setError(res.error);
        setStatus('error');
        return;
      }
      setResult(res);
      setStatus('done');
    } catch (e) {
      const err = e as { response?: { data?: { detail?: string } }; message?: string };
      setError(err.response?.data?.detail || err.message || 'Неизвестная ошибка');
      setStatus('error');
    }
  };

  const handleReset = () => {
    setFile(null);
    setResult(null);
    setStatus('idle');
    setError(null);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -4 }}
      transition={{ duration: 0.3 }}
      className="mx-auto max-w-7xl px-4 md:px-8 py-12"
    >
      <PageHeading
        eyebrow="Обработка"
        title="Обработка медиа"
        subtitle="Загрузите изображение или видео, выберите модель и получите результат с распределением эмоций."
      />

      <ProcessTabs />

      <div className="grid gap-8 lg:grid-cols-[minmax(0,380px)_1fr]">
        <div className="flex flex-col gap-6">
          <section>
            <h3 className="eyebrow mb-3">Выберите модель</h3>
            <ModelSelector value={model} onChange={setModel} />
          </section>

          <div className="divider-gradient" />

          <section>
            <h3 className="eyebrow mb-3">Файл</h3>
            <FileUpload
              accept="video/mp4,video/quicktime,video/x-msvideo"
              maxSizeMb={50}
              label="Перетащите видео или выберите"
              hint="MP4 · MOV · AVI, до 50 МБ, длительность до 30 с"
              currentFile={file}
              onFileSelect={setFile}
              onClear={() => setFile(null)}
            />
          </section>

          <div className="flex flex-col gap-3">
            <Button
              onClick={handleSubmit}
              disabled={!file || status === 'processing'}
              className="w-full"
            >
              {status === 'processing' ? 'Обрабатывается...' : 'Обработать'}
            </Button>
            {status !== 'idle' && (
              <Button variant="ghost" onClick={handleReset} className="w-full">
                Сбросить
              </Button>
            )}
          </div>
        </div>

        <div className="min-h-[400px]">
          {status === 'idle' && <EmptyState />}
          {status === 'processing' && (
            <div className="card p-8">
              <LoadingRings
                message="Обработка видео..."
                hint="Это может занять от нескольких секунд до минуты"
              />
            </div>
          )}
          {status === 'error' && (
            <div className="card p-8 border-danger/50">
              <h4 className="font-display font-semibold text-danger">Ошибка обработки</h4>
              <p className="mt-2 text-sm text-ink-muted">{error}</p>
            </div>
          )}
          {status === 'done' && result && <VideoResultView result={result} />}
        </div>
      </div>
    </motion.div>
  );
}

function ProcessTabs() {
  const { pathname } = useLocation();
  const items = [
    { to: '/process/photo', label: 'Фотография' },
    { to: '/process/video', label: 'Видео' },
  ];
  return (
    <div className="inline-flex bg-line-soft p-1 rounded-xl mb-8">
      {items.map((item) => {
        const active = pathname === item.to;
        return (
          <Link
            key={item.to}
            to={item.to}
            className={`px-5 py-2 rounded-lg text-sm font-medium transition-all ${
              active ? 'bg-white text-ink shadow-card' : 'text-ink-muted hover:text-ink'
            }`}
          >
            {item.label}
          </Link>
        );
      })}
    </div>
  );
}

function EmptyState() {
  return (
    <div className="card p-10 flex flex-col items-center justify-center text-center min-h-[400px]">
      <div className="w-16 h-16 rounded-2xl bg-brand-gradient-soft flex items-center justify-center mb-4">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" className="text-primary-deep">
          <rect x="3" y="6" width="13" height="12" rx="2" strokeWidth="1.5" />
          <path d="M16 10l5-3v10l-5-3z" strokeWidth="1.5" strokeLinejoin="round" />
        </svg>
      </div>
      <h3 className="font-display font-semibold text-ink">Загрузите видео</h3>
      <p className="mt-2 text-sm text-ink-muted max-w-sm">
        Выберите видеофайл слева, и аннотированный результат появится здесь
      </p>
    </div>
  );
}
