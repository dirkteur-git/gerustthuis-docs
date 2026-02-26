// GerustThuis Tailwind CSS Configuration
// Version 3.0 — Deep Sage & Amber — February 2026

module.exports = {
  theme: {
    extend: {
      colors: {
        'gt-sage': {
          DEFAULT: '#3E6652',
          50: '#E0EDE4',
          100: '#C5DFC9',
          200: '#9EC8A8',
          300: '#7EB18A',
          400: '#5E9178',
          500: '#3E6652',
          600: '#2E5440',
          700: '#224030',
          800: '#162B20',
          900: '#0B1610',
        },
        'gt-amber': {
          DEFAULT: '#D4944C',
          50: '#F5EBD8',
          100: '#F0C88C',
          200: '#E8B06A',
          300: '#D4944C',
          400: '#C0803A',
          500: '#A06830',
          600: '#805028',
          700: '#603C1E',
        },
        'gt-ink': {
          DEFAULT: '#2C2C2C',
          soft: '#5A5A5A',
          muted: '#8A8A8A',
        },
        'gt-cream': '#FDFCF7',
        'gt-sand': '#F5F1EA',
        'gt-status': {
          ok: '#3E6652',
          notice: '#D4944C',
          urgent: '#C4645A',
          inactive: '#B8B3AD',
        }
      },
      fontFamily: {
        'display': ['DM Serif Display', 'Georgia', 'serif'],
        'sans': ['DM Sans', '-apple-system', 'sans-serif'],
      },
      fontSize: {
        'gt-h1': ['32px', { lineHeight: '1.2', fontWeight: '400' }],
        'gt-h2': ['24px', { lineHeight: '1.3', fontWeight: '400' }],
        'gt-h3': ['17px', { lineHeight: '1.4', fontWeight: '600' }],
        'gt-body': ['15px', { lineHeight: '1.6', fontWeight: '400' }],
        'gt-caption': ['12px', { lineHeight: '1.5', fontWeight: '500' }],
      },
      borderRadius: {
        'gt-sm': '8px',
        'gt-md': '10px',
        'gt-lg': '12px',
        'gt-xl': '16px',
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
