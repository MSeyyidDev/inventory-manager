/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      fontFamily: {
        sans: [
          "Inter",
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "Roboto",
          "sans-serif",
        ],
      },
      colors: {
        brand: {
          50: "#f3f6ff",
          100: "#e3ebff",
          200: "#c2d1ff",
          300: "#9fb4ff",
          400: "#7892fa",
          500: "#5670ee",
          600: "#3e54d6",
          700: "#3243ad",
          800: "#28368a",
          900: "#212c6e",
        },
      },
    },
  },
  plugins: [],
};
