/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx,js,jsx}"],
  theme: {
    extend: {
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      colors: {
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        chart: {
          1: "hsl(var(--chart-1))",
          2: "hsl(var(--chart-2))",
          3: "hsl(var(--chart-3))",
          4: "hsl(var(--chart-4))",
          5: "hsl(var(--chart-5))",
        },
        strava: "#fc4c02",
        success: {
          DEFAULT: "hsl(var(--success))",
          foreground: "hsl(var(--success-foreground))",
        },
      },
    },
    /*  Benjamin De Cock's Easing functions */
    animationTimingFunction: {
      "in-quad": "var(--ease-in-quad)",
      "in-cubic": "var(--ease-in-cubic)",
      "in-quart": "var(--ease-in-quart)",
      "in-quint": "var(--ease-in-quint)",
      "in-expo": "var(--ease-in-expo)",
      "in-circ": "var(--ease-in-circ)",
      "out-quad": "var(--ease-out-quad)",
      "out-cubic": "var(--ease-out-cubic)",
      "out-quart": "var(--ease-out-quart)",
      "out-quint": "var(--ease-out-quint)",
      "out-expo": "var(--ease-out-expo)",
      "out-circ": "var(--ease-out-circ)",
      "in-out-quad": "var(--ease-in-out-quad)",
      "in-out-cubic": "var(--ease-in-out-cubic)",
      "in-out-quart": "var(--ease-in-out-quart)",
      "in-out-quint": "var(--ease-in-out-quint)",
      "in-out-expo": "var(--ease-in-out-expo)",
      "in-out-circ": "var(--ease-in-out-circ)",
    },
  },
  plugins: [require("tailwindcss-animate")],
};
