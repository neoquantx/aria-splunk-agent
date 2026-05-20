/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        'soc-bg': '#0a0e1a',
        'soc-surface': '#111827',
        'soc-card': '#1a2235',
        'soc-border': '#1e3a5f',
        'soc-green': '#00ff88',
        'soc-amber': '#ffaa00',
        'soc-red': '#ff4444',
        'soc-blue': '#3b82f6',
        'soc-purple': '#8b5cf6',
        'soc-text': '#e2e8f0',
        'soc-muted': '#64748b',
      }
    }
  },
  plugins: []
}

