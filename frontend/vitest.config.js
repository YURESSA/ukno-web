import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],

  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      '@shared': fileURLToPath(new URL('./src/components/shared', import.meta.url)),
      '@UI': fileURLToPath(new URL('./src/components/UI', import.meta.url)),
    },
  },

  test: {
    environment: 'jsdom',

    globals: true,

    setupFiles: ['./src/test/setup.js'],

    include: [
      'src/**/__tests__/**/*.{test,spec}.{js,ts}',
      'src/**/*.{test,spec}.{js,ts}',
    ],

    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'lcov'],
      reportsDirectory: './coverage',
      include: ['src/**/*.{js,vue}'],
      exclude: [
        'src/main.js',
        'src/router/**',
        'src/**/__tests__/**',
        'src/test/**',
      ],
      thresholds: {
        lines: 60,
        functions: 60,
        branches: 50,
      },
    },
  },
})
