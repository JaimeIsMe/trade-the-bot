/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'aster-purple': '#8B5CF6',
        'aster-blue': '#3B82F6',
      }
    },
  },
  plugins: [],
}

