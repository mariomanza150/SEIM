import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// https://vite.dev/config/
export default defineConfig({
  // In production we serve assets via Django/WhiteNoise under `/static/`.
  // This ensures the built SPA requests `/static/assets/...` instead of `/assets/...`.
  base: '/static/',
  plugins: [vue()],
  
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  
  server: {
    host: '0.0.0.0',  // Allow access from Docker network
    port: 5173,
    strictPort: true,
    
    // Proxy API requests to Django backend
    proxy: {
      '/api': {
        target: 'http://localhost:8001',  // Django in Docker (external port)
        changeOrigin: true,
        secure: false,
      },
      '/static': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        secure: false,
      },
      '/media': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        secure: false,
      },
      '/seim/admin': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        secure: false,
      },
      '/cms': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        secure: false,
      },
      '/ws': {
        target: 'http://localhost:8001',
        ws: true,
        changeOrigin: true,
      },
    }
  },
  
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    emptyOutDir: true,
    sourcemap: false,
    
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules/bpmn-js') || id.includes('node_modules/bpmn-moddle')) {
            return 'bpmn'
          }
          if (id.includes('node_modules/vue-i18n') || id.includes('node_modules/@intlify')) {
            return 'i18n'
          }
          if (id.includes('node_modules/axios')) {
            return 'axios'
          }
          if (
            id.includes('node_modules/vue/') ||
            id.includes('node_modules/vue-router') ||
            id.includes('node_modules/pinia')
          ) {
            return 'vendor'
          }
          if (id.includes('node_modules/bootstrap')) {
            return 'bootstrap'
          }
          return undefined
        },
      }
    }
  },
  
  // Environment variable prefix
  envPrefix: 'VITE_',

  // Vitest
  test: {
    environment: 'jsdom',
    globals: true,
    include: ['src/**/*.{spec,test}.{js,ts}'],
    pool: 'forks',
    maxForks: 4,
    testTimeout: 15000,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'lcov'],
      reportsDirectory: './coverage',
      include: ['src/stores/**', 'src/services/**'],
      exclude: ['**/*.spec.js', '**/*.test.js', 'node_modules'],
    },
  },
})
