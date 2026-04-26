import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        brand: {
          purple: '#8A2BE2',
          blue: '#1E40AF',
        },
        fg: {
          primary: '#1a1a1a',
          secondary: '#666666',
          tertiary: '#999999',
        },
        bg: {
          primary: '#fafafa',
          secondary: '#ffffff',
          tertiary: '#f5f5f5',
        },
        border: '#e5e5e5',
        success: '#059669',
        warning: '#d97706',
        error: '#dc2626',
      },
      fontFamily: {
        display: ['Fraunces', 'serif'],
        sans: ['Inter', 'sans-serif'],
      },
      keyframes: {
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
      animation: {
        shimmer: 'shimmer 1.5s infinite linear',
      },
    },
  },
  plugins: [],
};
export default config;
