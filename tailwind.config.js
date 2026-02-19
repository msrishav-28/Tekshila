/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Dark Lab Canvas
        void: '#050505',
        surface: '#0A0A0A',
        
        // Glass & Borders
        'glass-stroke': 'rgba(255, 255, 255, 0.08)',
        'glass-highlight': 'rgba(255, 255, 255, 0.2)',
        
        // Laser Crimson Accent
        crimson: {
          DEFAULT: '#F43F5E',
          dark: '#E11D48',
          glow: 'rgba(244, 63, 94, 0.4)',
        },
        
        // Electric Quicksilver
        quicksilver: {
          100: '#F5F5F5',
          200: '#E5E5E5',
          300: '#D4D4D4',
          400: '#A3A3A3',
          500: '#737373',
          600: '#525252',
          700: '#404040',
          800: '#262626',
          900: '#171717',
        },
        
        // Semantic Colors
        primary: '#F43F5E',
        secondary: '#A3A3A3',
        accent: '#E5E5E5',
      },
      fontFamily: {
        display: ['Space Grotesk', 'sans-serif'],
        ui: ['Plus Jakarta Sans', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      letterSpacing: {
        'micro': '0.2em',
      },
      fontSize: {
        'micro': ['10px', { lineHeight: '1.5', letterSpacing: '0.2em' }],
      },
      backdropBlur: {
        'glass': '12px',
      },
      saturate: {
        'glass': '180%',
      },
      animation: {
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 6s ease-in-out infinite',
        'grain': 'grain 8s steps(10) infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        grain: {
          '0%, 100%': { transform: 'translate(0, 0)' },
          '10%': { transform: 'translate(-5%, -10%)' },
          '20%': { transform: 'translate(-15%, 5%)' },
          '30%': { transform: 'translate(7%, -25%)' },
          '40%': { transform: 'translate(-5%, 25%)' },
          '50%': { transform: 'translate(-15%, 10%)' },
          '60%': { transform: 'translate(15%, 0%)' },
          '70%': { transform: 'translate(0%, 15%)' },
          '80%': { transform: 'translate(3%, 35%)' },
          '90%': { transform: 'translate(-10%, 10%)' },
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'highlight-stroke': 'linear-gradient(180deg, rgba(255,255,255,0.2) 0%, transparent 100%)',
      },
    },
  },
  plugins: [],
}
