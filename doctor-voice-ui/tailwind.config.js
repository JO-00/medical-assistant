/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          DEFAULT: "#0F221D",
          soft: "#1B332C",
          faint: "#3A5850",
        },
        sage: {
          DEFAULT: "#4F7869",
          light: "#7FA695",
          pale: "#E4ECE7",
        },
        paper: {
          DEFAULT: "#EEF2EE",
          raised: "#F8FAF8",
        },
        brick: {
          DEFAULT: "#B85C4C",
          soft: "#E7CFC9",
        },
        line: "#D7DFD9",
      },
      fontFamily: {
        display: ["'Fraunces'", "serif"],
        sans: ["'IBM Plex Sans'", "system-ui", "sans-serif"],
        mono: ["'IBM Plex Mono'", "monospace"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(15,34,29,0.06), 0 8px 24px -8px rgba(15,34,29,0.12)",
      },
      keyframes: {
        breathe: {
          "0%, 100%": { opacity: 0.4 },
          "50%": { opacity: 1 },
        },
        rise: {
          "0%": { opacity: 0, transform: "translateY(6px)" },
          "100%": { opacity: 1, transform: "translateY(0)" },
        },
      },
      animation: {
        breathe: "breathe 2.4s ease-in-out infinite",
        rise: "rise 0.35s ease-out both",
      },
    },
  },
  plugins: [],
};
