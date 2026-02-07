import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // NCR Voyix Purple Brand
        ncr: {
          primary: '#5B3A9B',        // Main purple
          'primary-dark': '#4A2F7F',  // Darker purple
          'primary-light': '#7B5BBB', // Lighter purple
          'primary-pale': '#E8DFF5',  // Very light purple for backgrounds
          secondary: '#8B5FBF',       // Mid-tone purple
          dark: '#1F1F1F',           // Almost black text
          gray: {
            50: '#FAFAFA',
            100: '#F5F5F5',
            200: '#E5E5E5',
            300: '#D4D4D4',
            400: '#A3A3A3',
            500: '#737373',
            600: '#525252',
            700: '#404040',
            800: '#262626',
            900: '#1F1F1F',
          }
        },
        // Status colors
        status: {
          critical: '#DC2626',
          high: '#F97316',
          medium: '#F59E0B',
          low: '#10B981',
        }
      },
      backgroundImage: {
        'gradient-purple': 'linear-gradient(135deg, #5B3A9B 0%, #7B5BBB 100%)',
        'gradient-purple-dark': 'linear-gradient(135deg, #4A2F7F 0%, #5B3A9B 100%)',
      },
    },
  },
  plugins: [],
}
export default config