/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: {
          primary: "#0b1220",
          secondary: "#111827",
          tertiary: "#1f2937",
          soft: "#0f172a",
        },
        text: {
          primary: "#f3f4f6",
          secondary: "#9ca3af",
          muted: "#6b7280",
          inverted: "#0b1220",
        },
        brand: {
          primary: "#2563eb",
          secondary: "#7c3aed",
          accent: "#06b6d4",
        },
        status: {
          healthy: "#22c55e",
          warning: "#f59e0b",
          critical: "#ef4444",
          info: "#38bdf8",
        },
        chart: {
          1: "#06b6d4",
          2: "#7c3aed",
          3: "#22c55e",
          4: "#f97316",
          5: "#ef4444",
        },
      },
      borderRadius: {
        sm: "6px",
        md: "10px",
        lg: "16px",
      },
      boxShadow: {
        soft: "0 2px 10px rgba(0,0,0,0.25)",
        elevated: "0 8px 30px rgba(0,0,0,0.35)",
        "glow-blue": "0 0 20px rgba(37, 99, 235, 0.4)",
        "glow-cyan": "0 0 20px rgba(6, 182, 212, 0.4)",
      },
      animation: {
        "pulse-glow": "pulse-glow 2s infinite ease-in-out",
      },
      keyframes: {
        "pulse-glow": {
          "0%": { boxShadow: "0 0 0px rgba(6,182,212,0.4)" },
          "50%": { boxShadow: "0 0 20px rgba(6,182,212,0.6)" },
          "100%": { boxShadow: "0 0 0px rgba(6,182,212,0.4)" },
        },
      },
    },
  },
  plugins: [],
};
