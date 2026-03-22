import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './contexts/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['var(--font-inter)', 'Inter', 'system-ui', 'sans-serif'],
        display: ['var(--font-display)', '"DM Serif Display"', 'serif'],
        reading: ['var(--font-reading)', '"DM Serif Text"', 'serif'],
      },
      colors: {
        background: 'var(--background)',
        foreground: 'var(--foreground)',
        card: {
          DEFAULT: 'var(--card)',
          foreground: 'var(--card-foreground)',
          hover: 'var(--card-hover)',
        },
        popover: {
          DEFAULT: 'var(--popover)',
          foreground: 'var(--popover-foreground)',
        },
        primary: {
          DEFAULT: 'var(--primary)',
          foreground: 'var(--primary-foreground)',
        },
        secondary: {
          DEFAULT: 'var(--secondary)',
          foreground: 'var(--secondary-foreground)',
        },
        muted: {
          DEFAULT: 'var(--muted)',
          foreground: 'var(--muted-foreground)',
        },
        accent: {
          DEFAULT: 'var(--accent)',
          foreground: 'var(--accent-foreground)',
        },
        destructive: {
          DEFAULT: 'var(--destructive)',
          foreground: 'var(--destructive-foreground)',
        },
        border: 'var(--border)',
        input: 'var(--input)',
        ring: 'var(--ring)',
        // Design system surfaces
        surface: 'var(--surface)',
        frame: 'var(--frame)',
        // Text hierarchy
        'text-primary': 'var(--text-primary)',
        'text-secondary': 'var(--text-secondary)',
        'text-body': 'var(--text-body)',
        'text-body-reading': 'var(--text-body-reading)',
        'text-muted': 'var(--text-muted)',
        'text-faint': 'var(--text-faint)',
        // Accent palette
        gold: {
          DEFAULT: 'var(--gold)',
          bright: 'var(--gold-bright)',
        },
        blue: 'var(--blue)',
        green: 'var(--green)',
        red: 'var(--red)',
      },
      borderColor: {
        DEFAULT: 'var(--border)',
        subtle: 'var(--border-subtle)',
        strong: 'var(--border-strong)',
        divider: 'var(--border-divider)',
      },
      borderRadius: {
        xs: '0.375rem',
        sm: '0.4375rem',
        md: '0.5rem',
        lg: '0.625rem',
        xl: '0.75rem',
        '2xl': '0.875rem',
        '3xl': '1rem',
        hero: '1.125rem',
        'hero-lg': '1.25rem',
      },
      fontSize: {
        'display-xl': ['3rem', { lineHeight: '1.15' }],
        'display-lg': ['2.125rem', { lineHeight: '1.25' }],
        'display-md': ['1.75rem', { lineHeight: '1.25' }],
        'display-sm': ['1.375rem', { lineHeight: '1.3' }],
        'display-xs': ['1rem', { lineHeight: '1.3' }],
        'stat-lg': ['2.5rem', { lineHeight: '1' }],
        'stat-md': ['2.25rem', { lineHeight: '1' }],
        'body-lg': ['1.25rem', { lineHeight: '1.85' }],
        'body-md': ['1.0625rem', { lineHeight: '1.9' }],
        'body-sm': ['0.9375rem', { lineHeight: '1.75' }],
        'body-xs': ['0.8125rem', { lineHeight: '1.7' }],
        label: ['0.625rem', { lineHeight: '1.2', letterSpacing: '0.1em' }],
        caption: ['0.5625rem', { lineHeight: '1.2' }],
      },
      maxWidth: {
        reading: '42.5rem',
        'reading-hero': '50rem',
        content: '70rem',
      },
      boxShadow: {
        sm: 'var(--shadow-sm)',
        md: 'var(--shadow-md)',
        lg: 'var(--shadow-lg)',
        dropdown: 'var(--shadow-dropdown)',
      },
    },
  },
  plugins: [],
};

export default config;
