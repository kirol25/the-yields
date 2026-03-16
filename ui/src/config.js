// ── Backend ────────────────────────────────────────────────────────────
export const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'
export const APP_NAME = 'the-yields'

// The AWS region for Cognito authentication
export const REGION='eu-central-1'

// ── Feature flags ────────────────────────────────────────────────────────────
const REGISTRATION_ENABLED = import.meta.env.VITE_REGISTRATION_ENABLED === 'true'

// ── Brand colours ────────────────────────────────────────────────────────────
// These are the Tailwind CSS custom property values used across the app.
// Dark-mode values are Tailwind's built-in defaults; light-mode overrides are
// applied via `html.light { ... }` in style.css.
export const COLORS = {
  // Accent (emerald)
  emerald: {
    300: '#6ee7b7',
    400: '#34d399',
    500: '#10b981',
    600: '#059669',
  },
  // Chart palette
  chart: {
    dividends: 'rgba(16, 185, 129, 0.8)',   // emerald-500
    yields:    'rgba(96, 165, 250, 0.7)',    // blue-400
  },
  // Light-mode gray scale (oklch → closest hex approximations)
  light: {
    gray950: '#e5e7eb', // page background
    gray900: '#ffffff', // card backgrounds
    gray800: '#f5f5f6', // input backgrounds
    gray700: '#d1d5db', // borders
    gray600: '#b8bcc8', // muted borders / dividers
    gray500: '#6b7280', // secondary text
    gray400: '#4b5563',
    gray300: '#374151',
    gray200: '#1f2937',
    gray100: '#111827', // primary text (near black)
  },
}
