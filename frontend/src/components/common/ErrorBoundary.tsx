import { Component, type ErrorInfo, type ReactNode } from 'react';
import { Link } from 'react-router-dom';

interface Props {
  children: ReactNode;
  /** Ключ, меняющийся при навигации — сбрасывает состояние после перехода на другую страницу. */
  resetKey?: string;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

/**
 * Ловит любые исключения в рендере дочернего поддерева. Без этого
 * любое брошенное исключение внутри страницы «выбивает» AnimatePresence
 * и оставляет пустую белую область под навбаром.
 */
export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    // Чтобы увидеть стек в devtools при локальной разработке.
    // eslint-disable-next-line no-console
    console.error('[ErrorBoundary]', error, info);
  }

  componentDidUpdate(prevProps: Props): void {
    if (this.state.hasError && prevProps.resetKey !== this.props.resetKey) {
      this.setState({ hasError: false, error: null });
    }
  }

  private handleReload = () => {
    this.setState({ hasError: false, error: null });
  };

  render(): ReactNode {
    if (!this.state.hasError) return this.props.children;

    return (
      <div className="mx-auto max-w-3xl px-4 md:px-8 py-16">
        <div className="card p-8 md:p-10 text-center">
          <div className="mx-auto w-14 h-14 rounded-2xl bg-brand-gradient-soft flex items-center justify-center mb-5">
            <svg
              width="28"
              height="28"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              className="text-primary-deep"
            >
              <path d="M12 9v4m0 4h.01" strokeWidth="2" strokeLinecap="round" />
              <circle cx="12" cy="12" r="9" strokeWidth="1.5" />
            </svg>
          </div>
          <h2 className="font-display text-2xl font-semibold text-ink">
            Что-то пошло не так
          </h2>
          <p className="mt-2 text-ink-muted text-sm max-w-md mx-auto">
            Страница не смогла отобразиться. Попробуйте обновить её или вернуться на главную.
          </p>
          {this.state.error?.message && (
            <pre className="mt-5 mx-auto max-w-full overflow-auto rounded-lg bg-line-soft/70 p-3 text-left text-xs font-mono text-ink-muted whitespace-pre-wrap">
              {this.state.error.message}
            </pre>
          )}
          <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
            <button onClick={this.handleReload} className="btn-primary">
              Попробовать снова
            </button>
            <Link to="/" className="btn-secondary">
              На главную
            </Link>
          </div>
        </div>
      </div>
    );
  }
}
