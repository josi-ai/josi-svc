import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './contexts/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#6B5CE7',
          50: '#F0EEFE',
          100: '#E0DCFD',
          200: '#C1B9FB',
          300: '#A296F9',
          400: '#8379F0',
          500: '#6B5CE7',
          600: '#5644CC',
          700: '#4233A1',
          800: '#2F2576',
          900: '#1E184D',
        },
        cosmic: {
          DEFAULT: '#E78A5C',
          50: '#FDF3EE',
          100: '#FBE7DD',
          200: '#F7CFBB',
          300: '#F3B799',
          400: '#EFA077',
          500: '#E78A5C',
          600: '#D06B3A',
          700: '#A3522D',
          800: '#763B20',
          900: '#492514',
        },
        dark: {
          bg: '#0f0a1e',
          surface: '#1a1230',
          card: '#231845',
          border: '#2d2055',
          hover: '#362968',
        },
      },
      boxShadow: {
        glow: '0 0 20px rgba(107, 92, 231, 0.3)',
        'glow-lg': '0 0 40px rgba(107, 92, 231, 0.4)',
        'glow-cosmic': '0 0 20px rgba(231, 138, 92, 0.3)',
      },
      backgroundImage: {
        'nebula-gradient': 'linear-gradient(135deg, #0f0a1e 0%, #1a1230 50%, #231845 100%)',
        'cosmic-gradient': 'linear-gradient(135deg, #6B5CE7 0%, #E78A5C 100%)',
      },
    },
  },
  plugins: [],
};

export default config;
