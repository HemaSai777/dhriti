/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        gov: {
          50: '#f0f7f6',
          100: '#d9ece9',
          500: '#1e7065',
          600: '#14574e',
          700: '#0f423b',
          800: '#0b322c',
          900: '#072420',
        },
        saffron: {
          500: '#ea580c',
          600: '#c2410c'
        }
      }
    },
  },
  plugins: [],
}
