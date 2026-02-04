/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        mediterranean: {
          navy: '#0A2F51',      // Bleu marine profond
          azure: '#0E7C7B',     // Bleu-vert méditerranéen
          turquoise: '#17B5B4', // Turquoise vif
          sky: '#9BDEDF',       // Bleu ciel clair
          sand: '#F4E8D8',      // Blanc cassé/sable
          terracotta: '#E76F51',// Terracotta
          ochre: '#F4A261',     // Ocre doré
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  },
  plugins: [],
}
