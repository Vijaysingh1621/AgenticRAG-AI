import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    proxy: {
      '/upload-pdf': 'http://localhost:8001',
      '/query': 'http://localhost:8001',
      '/voice-query': 'http://localhost:8001',
      '/upload-audio': 'http://localhost:8001',
      '/image': 'http://localhost:8001',
      '/images': 'http://localhost:8001',
      '/health': 'http://localhost:8001'
    }
  }
})
