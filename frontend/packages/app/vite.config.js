import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@genai-med-chat/shared': path.resolve(__dirname, '../shared/src'),
      '@genai-med-chat/auth': path.resolve(__dirname, '../auth/src'),
      '@genai-med-chat/chat': path.resolve(__dirname, '../chat/src'),
      '@genai-med-chat/store': path.resolve(__dirname, '../store/src')
    }
  },
  server: {
    port: 5173,
    host: '0.0.0.0',
    fs: {
      allow: ['..', '../../']
    }
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true
  }
})
