import { MODELS } from '../../data/models';
import type { ModelKey } from '../../types/api';

interface ModelSelectorProps {
  value: ModelKey;
  onChange: (key: ModelKey) => void;
}

export function ModelSelector({ value, onChange }: ModelSelectorProps) {
  return (
    <div className="flex flex-col gap-2">
      {MODELS.map((model) => {
        const isActive = model.key === value;
        return (
          <button
            key={model.key}
            type="button"
            onClick={() => onChange(model.key)}
            className={`group flex items-center gap-3 p-3 rounded-xl border transition-all text-left
              ${
                isActive
                  ? 'border-primary bg-primary-soft/60'
                  : 'border-line bg-white hover:border-primary/40'
              }`}
          >
            <span
              className={`flex-shrink-0 w-5 h-5 rounded-full border-2 flex items-center justify-center
                ${isActive ? 'border-primary' : 'border-line group-hover:border-primary/50'}`}
            >
              {isActive && <span className="w-2.5 h-2.5 rounded-full bg-brand-gradient" />}
            </span>
            <span className="flex-1 min-w-0">
              <span className="block text-sm font-medium text-ink">{model.name}</span>
              <span className="block text-xs text-ink-muted mt-0.5 truncate">
                {model.family} · {model.params}
              </span>
            </span>
          </button>
        );
      })}
    </div>
  );
}
