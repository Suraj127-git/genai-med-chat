/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
    "../shared/src/**/*.{js,jsx,ts,tsx}",
    "../auth/src/**/*.{js,jsx,ts,tsx}",
    "../chat/src/**/*.{js,jsx,ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          blue: "#0366d6",
          light: "#dbeafe",
          dark: "#1e3a8a",
        },
      },
      boxShadow: {
        card: "0 2px 8px rgba(0, 0, 0, 0.1)",
      },
      borderRadius: {
        xl: "16px",
      },
    },
  },
  plugins: [],
}
