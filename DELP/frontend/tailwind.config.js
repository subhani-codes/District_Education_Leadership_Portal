/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,jsx}',
    './components/**/*.{js,jsx}',
  ],
  theme: {
    extend: {
      colors: {
        navy:    '#0B3D91',
        saffron: '#FF9933',
        ink:     '#1a1a1a',
        paper:   '#f7f8fb',
        line:    '#e5e7eb',
      },
      fontFamily: {
        sans: ['"Noto Sans"', 'Roboto', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
