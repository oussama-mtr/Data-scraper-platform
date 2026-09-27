/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        background: {
          DEFAULT: "#0F172A",
          alt: "#111827",
        },
        card: "#1E293B",
        primary: "#2563EB",
        accent: "#38BDF8",
        success: "#22C55E",
        warning: "#F59E0B",
        error: "#EF4444",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      boxShadow: {
        glow: "0 0 40px rgba(37, 99, 235, 0.25)",
        card: "0 10px 40px rgba(15, 23, 42, 0.45)",
      },
      animation: {
        pulseSoft: "pulseSoft 2s ease-in-out infinite",
        fadeIn: "fadeIn 0.35s ease-out",
        slideUp: "slideUp 0.4s ease-out",
      },
      keyframes: {
        pulseSoft: {
          "0%, 100%": { opacity: "0.65" },
          "50%": { opacity: "1" },
        },
        fadeIn: {
          from: { opacity: "0" },
          to: { opacity: "1" },
        },
        slideUp: {
          from: { opacity: "0", transform: "translateY(12px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
      },
    },
  },
  plugins: [],
};
