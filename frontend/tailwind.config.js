/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        bg: {
          primary: "#09090b",
          secondary: "#111113",
          card: "#18181b",
          elevated: "#1e1e22",
          hover: "#27272a",
        },
        accent: {
          primary: "#8b5cf6",
          secondary: "#a78bfa",
          tertiary: "#c4b5fd",
          glow: "rgba(139, 92, 246, 0.12)",
          "glow-strong": "rgba(139, 92, 246, 0.25)",
        },
        text: {
          primary: "#fafafa",
          secondary: "#a1a1aa",
          muted: "#52525b",
        },
        success: "#22c55e",
        "success-muted": "rgba(34, 197, 94, 0.15)",
        danger: "#ef4444",
        "danger-muted": "rgba(239, 68, 68, 0.15)",
        warning: "#eab308",
        border: {
          DEFAULT: "rgba(255, 255, 255, 0.06)",
          hover: "rgba(255, 255, 255, 0.1)",
        },
      },
      borderRadius: {
        "2xl": "16px",
        "3xl": "20px",
        "4xl": "24px",
      },
      boxShadow: {
        glow: "0 0 20px rgba(139, 92, 246, 0.15)",
        "glow-lg": "0 0 40px rgba(139, 92, 246, 0.2)",
        card: "0 1px 3px rgba(0, 0, 0, 0.3), 0 1px 2px rgba(0, 0, 0, 0.2)",
        elevated: "0 4px 12px rgba(0, 0, 0, 0.4)",
      },
    },
  },
  plugins: [],
};
