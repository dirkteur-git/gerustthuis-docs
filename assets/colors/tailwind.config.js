// GerustThuis Tailwind CSS Configuration
// Version 1.0 - February 2026

module.exports = {
  theme: {
    extend: {
      colors: {
        'gt-green': {
          DEFAULT: '#10b981',
          50: '#ecfdf5',
          100: '#d1fae5',
          200: '#a7f3d0',
          300: '#6ee7b7',
          400: '#34d399',
          500: '#10b981',
          600: '#059669',
          700: '#047857',
          800: '#065f46',
          900: '#064e3b',
        },
        'gt-anthracite': '#111827',
        'gt-warm-gray': '#6b7280',
        'gt-light-gray': '#f3f4f6',
        'gt-status': {
          ok: '#10b981',
          warning: '#f59e0b',
          alert: '#ef4444',
          inactive: '#9ca3af',
        }
      },
      fontFamily: {
        'sans': ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      fontSize: {
        'gt-h1': ['24px', { lineHeight: '1.3', fontWeight: '600' }],
        'gt-h2': ['18px', { lineHeight: '1.4', fontWeight: '600' }],
        'gt-h3': ['16px', { lineHeight: '1.4', fontWeight: '600' }],
        'gt-body': ['14px', { lineHeight: '1.5', fontWeight: '400' }],
        'gt-small': ['12px', { lineHeight: '1.5', fontWeight: '400' }],
      },
      borderRadius: {
        'gt-sm': '6px',
        'gt-md': '8px',
        'gt-lg': '12px',
        'gt-xl': '14px',
      },
      spacing: {
        'gt-xs': '4px',
        'gt-sm': '8px',
        'gt-md': '16px',
        'gt-lg': '24px',
        'gt-xl': '32px',
        'gt-2xl': '48px',
      },
    }
  }
}
