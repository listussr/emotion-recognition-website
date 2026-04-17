import { useCallback, useRef, useState, type DragEvent } from 'react';
import { motion } from 'framer-motion';

interface FileUploadProps {
  accept: string;
  maxSizeMb: number;
  onFileSelect: (file: File) => void;
  label: string;
  hint: string;
  currentFile?: File | null;
  onClear?: () => void;
}

export function FileUpload({
  accept,
  maxSizeMb,
  onFileSelect,
  label,
  hint,
  currentFile,
  onClear,
}: FileUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const validate = useCallback(
    (file: File): string | null => {
      const sizeMb = file.size / (1024 * 1024);
      if (sizeMb > maxSizeMb) {
        return `Файл слишком большой. Максимум: ${maxSizeMb} МБ`;
      }
      return null;
    },
    [maxSizeMb],
  );

  const handleFile = useCallback(
    (file: File) => {
      const err = validate(file);
      if (err) {
        setError(err);
        return;
      }
      setError(null);
      onFileSelect(file);
    },
    [validate, onFileSelect],
  );

  const onDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleFile(file);
  };

  const onDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragOver(true);
  };

  const onDragLeave = () => setDragOver(false);

  if (currentFile) {
    return (
      <div className="card p-5 flex items-center justify-between gap-4">
        <div className="min-w-0">
          <p className="text-sm font-medium text-ink truncate">{currentFile.name}</p>
          <p className="text-xs text-ink-muted mt-0.5">
            {(currentFile.size / (1024 * 1024)).toFixed(2)} МБ
          </p>
        </div>
        <button
          type="button"
          onClick={() => {
            onClear?.();
            if (inputRef.current) inputRef.current.value = '';
          }}
          className="btn-ghost !py-2 !px-3 text-sm"
        >
          Убрать
        </button>
      </div>
    );
  }

  return (
    <div>
      <motion.div
        onDrop={onDrop}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onClick={() => inputRef.current?.click()}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') inputRef.current?.click();
        }}
        className={`relative cursor-pointer rounded-2xl border-2 border-dashed p-8 transition-all
          flex flex-col items-center justify-center gap-3 text-center
          ${dragOver ? 'border-primary bg-primary-soft' : 'border-line hover:border-primary/60 hover:bg-primary-soft/30'}`}
        animate={{ scale: dragOver ? 1.01 : 1 }}
      >
        <div className="w-12 h-12 rounded-xl bg-brand-gradient-soft flex items-center justify-center">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" className="text-primary-deep">
            <path
              d="M12 4v12m0-12l-4 4m4-4l4 4M5 20h14"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>
        <div>
          <p className="font-medium text-ink">{label}</p>
          <p className="text-sm text-ink-muted mt-1">{hint}</p>
        </div>
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) handleFile(file);
          }}
        />
      </motion.div>
      {error && <p className="mt-2 text-sm text-danger">{error}</p>}
    </div>
  );
}
