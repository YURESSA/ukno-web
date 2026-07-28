/**
 * Глобальный файл настройки тестового окружения.
 * Выполняется ПЕРЕД каждым тестовым файлом.
 *
 * Здесь можно:
 * - Добавлять глобальные моки (fetch, localStorage, IntersectionObserver)
 * - Настраивать @vue/test-utils глобальные плагины
 * - Подключать кастомные матчеры vitest-dom
 */

import { config } from '@vue/test-utils'
import { vi } from 'vitest'
import { createPinia } from 'pinia'

vi.stubGlobal('import.meta', {
  env: {
    VITE_FRONTEND_URL: 'http://localhost:8000/',
    MODE: 'test',
    DEV: false,
    PROD: false,
  },
})

global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  observe() {}
  unobserve() {}
  disconnect() {}
}

global.ResizeObserver = class ResizeObserver {
  constructor() {}
  observe() {}
  unobserve() {}
  disconnect() {}
}

config.global.plugins = []

const originalWarn = console.warn.bind(console)
beforeEach(() => {
  console.warn = (msg, ...args) => {
    if (typeof msg === 'string' && msg.includes('[Vue warn]') && msg.includes('Failed to resolve')) {
      return
    }
    originalWarn(msg, ...args)
  }
})

afterEach(() => {
  console.warn = originalWarn
  vi.clearAllMocks()
})
