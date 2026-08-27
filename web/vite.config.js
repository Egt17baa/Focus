import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

const API_TARGET = process.env.VITE_API_PROXY || 'http://localhost:5001'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': { target: API_TARGET, changeOrigin: true },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  },
})
