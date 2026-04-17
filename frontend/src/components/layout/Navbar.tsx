import { NavLink, Link } from 'react-router-dom';
import { useState } from 'react';

const navItems = [
  { to: '/', label: 'Главная', exact: true },
  { to: '/models', label: 'Архитектуры' },
  { to: '/process/photo', label: 'Обработка' },
  { to: '/gallery', label: 'Демо' },
];

export function Navbar() {
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-40 glass border-b border-line/60">
      <div className="mx-auto max-w-7xl px-4 md:px-8 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2.5 font-display font-semibold text-ink">
          <Logo />
          <span className="text-lg">Emotion AI</span>
        </Link>

        <nav className="hidden md:flex items-center gap-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.exact}
              className={({ isActive }) =>
                `relative px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                  isActive ? 'text-ink' : 'text-ink-muted hover:text-ink'
                }`
              }
            >
              {({ isActive }) => (
                <>
                  {item.label}
                  {isActive && (
                    <span className="absolute left-4 right-4 -bottom-[18px] h-[2px] bg-brand-gradient rounded-full" />
                  )}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        <button
          className="md:hidden btn-ghost !px-2.5 !py-2"
          onClick={() => setOpen((o) => !o)}
          aria-label="Меню"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            {open ? (
              <path d="M6 6l12 12M6 18L18 6" strokeWidth="2" strokeLinecap="round" />
            ) : (
              <path d="M4 7h16M4 12h16M4 17h16" strokeWidth="2" strokeLinecap="round" />
            )}
          </svg>
        </button>
      </div>

      {open && (
        <div className="md:hidden border-t border-line px-4 py-3 bg-white">
          <div className="flex flex-col">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.exact}
                onClick={() => setOpen(false)}
                className={({ isActive }) =>
                  `px-3 py-2.5 text-sm font-medium rounded-lg ${
                    isActive ? 'bg-primary-soft text-primary-deep' : 'text-ink-muted'
                  }`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </div>
        </div>
      )}
    </header>
  );
}

function Logo() {
  return (
    <svg width="28" height="28" viewBox="0 0 64 64" aria-hidden>
      <defs>
        <linearGradient id="logo-g" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#4F7CFF" />
          <stop offset="100%" stopColor="#8B5CF6" />
        </linearGradient>
      </defs>
      <path d="M32 4 L58 18 V46 L32 60 L6 46 V18 Z" fill="url(#logo-g)" />
      <circle cx="32" cy="32" r="9" fill="#fff" opacity="0.95" />
    </svg>
  );
}
