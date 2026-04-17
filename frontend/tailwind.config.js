/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: '#F5F7FB',
        surface: '#FFFFFF',
        primary: {
          DEFAULT: '#4F7CFF',
          deep: '#2563EB',
          soft: '#EEF2FF',
        },
        accent: {
          DEFAULT: '#8B5CF6',
          deep: '#7C3AED',
          soft: '#F3EEFF',
        },
        ink: {
          DEFAULT: '#0F172A',
          muted: '#64748B',
          soft: '#94A3B8',
        },
        line: {
          DEFAULT: '#E2E8F0',
          soft: '#EEF2FF',
        },
        success: '#10B981',
        danger: '#EF4444',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['"Space Grotesk"', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },
      borderRadius: {
        xl: '14px',
        '2xl': '18px',
        '3xl': '24px',
      },
      boxShadow: {
        card: '0 1px 3px rgba(15,23,42,.06), 0 8px 24px rgba(79,124,255,.06)',
        'card-hover': '0 2px 6px rgba(15,23,42,.08), 0 14px 40px rgba(79,124,255,.14)',
        glow: '0 10px 30px -10px rgba(79,124,255,.45)',
      },
      backgroundImage: {
        'brand-gradient': 'linear-gradient(135deg, #4F7CFF 0%, #8B5CF6 100%)',
        'brand-gradient-soft': 'linear-gradient(135deg, #EEF2FF 0%, #F3EEFF 100%)',
        'divider-gradient':
          'linear-gradient(90deg, transparent 0%, #4F7CFF 50%, transparent 100%)',
      },
      animation: {
        'ring-pulse': 'ringPulse 2.2s ease-in-out infinite',
        'slow-spin': 'spin 12s linear infinite',
        'fade-in': 'fadeIn .35s ease-out both',
        'float': 'float 8s ease-in-out infinite',
      },
      keyframes: {
        ringPulse: {
          '0%, 100%': { transform: 'scale(1)', opacity: '.7' },
          '50%': { transform: 'scale(1.18)', opacity: '0' },
        },
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(6px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0) translateX(0)' },
          '50%': { transform: 'translateY(-18px) translateX(10px)' },
        },
      },
    },
  },
  plugins: [],
};
