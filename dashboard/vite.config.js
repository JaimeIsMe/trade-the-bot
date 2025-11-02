import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Allow access from network
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://10.5.0.2:8000', // Use network IP instead of localhost
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://10.5.0.2:8000', // Use network IP instead of localhost
        ws: true,
      }
    }
  }
})

