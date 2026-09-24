import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), vueDevTools()],
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:5000',
      '/admin-panel': 'http://127.0.0.1:5000',
      '/login-admin': 'http://127.0.0.1:5000',
      '/media': 'http://127.0.0.1:5000',
      '/static': 'http://127.0.0.1:5000',
    },
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      '@shared': fileURLToPath(new URL('./src/components/shared', import.meta.url)),
      '@UI': fileURLToPath(new URL('./src/components/UI', import.meta.url)),
    },
  },
})
