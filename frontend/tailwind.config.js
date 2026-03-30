/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        bg: {
          primary: "#0f0f0f",
          secondary: "#1a1a2e",
          card: "#16213e",
          hover: "#1e2a4a",
        },
        accent: {
          primary: "#6366f1",
          secondary: "#818cf8",
          glow: "rgba(99, 102, 241, 0.15)",
        },
        text: {
          primary: "#e2e8f0",
          secondary: "#94a3b8",
          muted: "#64748b",
        },
        success: "#10b981",
        danger: "#ef4444",
        warning: "#f59e0b",
      },
    },
  },
  plugins: [],
};
