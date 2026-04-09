<template>
  <a class="seim-skip-link" href="#main-content">Skip to main content</a>
  <main id="main-content" tabindex="-1">
    <router-view />
  </main>
  <ToastContainer />
</template>

<script setup>
import { onBeforeUnmount, onMounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import api from '@/services/api'
import { useNotificationWebSocket } from '@/services/websocket'
import { applyUiPreferences, clearUiPreferences, readStoredUiPreferences } from '@/services/uiPreferences'
import ToastContainer from '@/components/ToastContainer.vue'

const authStore = useAuthStore()
const { info } = useToast()
let mediaQuery = null
let mediaQueryListener = null

const { connectIfAuthenticated, disconnect } = useNotificationWebSocket(authStore, {
  onNotification(notification) {
    const message = notification.message || notification.title || 'New notification'
    info(message, 6000)
    window.dispatchEvent(new CustomEvent('notification-new', { detail: notification }))
  },
})

async function loadUiPreferences() {
  try {
    const { data } = await api.get('/api/accounts/user-settings/')
    applyUiPreferences(data)
  } catch (error) {
    const stored = readStoredUiPreferences()
    applyUiPreferences(stored || undefined)
  }
}

onMounted(async () => {
  applyUiPreferences(readStoredUiPreferences() || undefined)
  await authStore.checkAuth()
  connectIfAuthenticated()

  if (authStore.isAuthenticated) {
    await loadUiPreferences()
  }

  if (typeof window !== 'undefined' && typeof window.matchMedia === 'function') {
    mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    mediaQueryListener = () => {
      if (document.documentElement.dataset.themePreference === 'auto') {
        applyUiPreferences(readStoredUiPreferences() || undefined)
      }
    }
    mediaQuery.addEventListener('change', mediaQueryListener)
  }
})

watch(() => authStore.isAuthenticated, async (isAuth) => {
  if (isAuth) {
    connectIfAuthenticated()
    await loadUiPreferences()
  } else {
    disconnect()
    clearUiPreferences()
    applyUiPreferences()
  }
})

onBeforeUnmount(() => {
  if (mediaQuery && mediaQueryListener) {
    mediaQuery.removeEventListener('change', mediaQueryListener)
  }
})
</script>

<style>
/* Global styles */
:root {
  --seim-app-bg: #f8f9fa;
  --seim-surface-bg: #ffffff;
  --seim-surface-text: #212529;
  --seim-border-color: #dee2e6;
  --seim-muted: #6c757d;
}

html[data-theme='dark'] {
  color-scheme: dark;
  --seim-app-bg: #111827;
  --seim-surface-bg: #1f2937;
  --seim-surface-text: #f9fafb;
  --seim-border-color: #374151;
  --seim-muted: #9ca3af;
}

html[data-high-contrast='true'] {
  --seim-border-color: #000000;
  --seim-muted: #495057;
}

#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  min-height: 100%;
  background-color: var(--seim-app-bg);
  color: var(--seim-surface-text);
}

/* Ensure full height */
html, body {
  height: 100%;
  margin: 0;
  padding: 0;
  background-color: var(--seim-app-bg);
  color: var(--seim-surface-text);
}

body,
.card,
.dropdown-menu,
.list-group-item,
.modal-content,
.offcanvas,
.table,
.table th,
.table td {
  transition: background-color 0.2s ease, color 0.2s ease, border-color 0.2s ease;
}

html[data-theme='dark'] body,
html[data-theme='dark'] .card,
html[data-theme='dark'] .dropdown-menu,
html[data-theme='dark'] .list-group-item,
html[data-theme='dark'] .modal-content,
html[data-theme='dark'] .offcanvas,
html[data-theme='dark'] .table,
html[data-theme='dark'] .table th,
html[data-theme='dark'] .table td,
html[data-theme='dark'] .breadcrumb,
html[data-theme='dark'] .alert-light {
  background-color: var(--seim-surface-bg);
  color: var(--seim-surface-text);
  border-color: var(--seim-border-color);
}

html[data-theme='dark'] .form-control,
html[data-theme='dark'] .form-select {
  background-color: #111827;
  color: var(--seim-surface-text);
  border-color: var(--seim-border-color);
}

html[data-theme='dark'] .text-muted,
html[data-theme='dark'] .form-text,
html[data-theme='dark'] .breadcrumb-item,
html[data-theme='dark'] .breadcrumb-item a {
  color: var(--seim-muted) !important;
}

html[data-high-contrast='true'] .card,
html[data-high-contrast='true'] .form-control,
html[data-high-contrast='true'] .form-select,
html[data-high-contrast='true'] .btn,
html[data-high-contrast='true'] .list-group-item {
  border-width: 2px;
}

html[data-reduce-motion='true'] *,
html[data-reduce-motion='true'] *::before,
html[data-reduce-motion='true'] *::after {
  animation-duration: 0.01ms !important;
  animation-iteration-count: 1 !important;
  scroll-behavior: auto !important;
  transition-duration: 0.01ms !important;
}

/* Skip link: off-screen until keyboard focus */
.seim-skip-link {
  position: absolute;
  left: -9999px;
  top: 0;
  z-index: 1080;
  padding: 0.5rem 1rem;
  background: var(--seim-surface-bg);
  color: var(--seim-surface-text);
  border: 2px solid var(--seim-border-color);
  border-radius: 0.25rem;
  font-weight: 600;
  text-decoration: none;
}

.seim-skip-link:focus,
.seim-skip-link:focus-visible {
  left: 0.75rem;
  top: 0.75rem;
  outline: none;
  box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.45);
}

#main-content:focus {
  outline: none;
}

/* Keyboard-visible focus rings (avoid mouse-click outline noise) */
a:focus-visible,
button:focus-visible,
.btn:focus-visible,
.form-control:focus-visible,
.form-select:focus-visible,
.form-check-input:focus-visible,
.nav-link:focus-visible,
.dropdown-item:focus-visible,
[role='button']:focus-visible {
  outline: 2px solid #0d6efd;
  outline-offset: 2px;
}

html[data-high-contrast='true'] a:focus-visible,
html[data-high-contrast='true'] button:focus-visible,
html[data-high-contrast='true'] .btn:focus-visible,
html[data-high-contrast='true'] .form-control:focus-visible,
html[data-high-contrast='true'] .form-select:focus-visible,
html[data-high-contrast='true'] .form-check-input:focus-visible,
html[data-high-contrast='true'] .nav-link:focus-visible,
html[data-high-contrast='true'] .dropdown-item:focus-visible,
html[data-high-contrast='true'] [role='button']:focus-visible {
  outline-width: 3px;
  outline-color: #000000;
}
</style>
