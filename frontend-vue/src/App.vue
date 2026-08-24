<template>
  <a class="seim-skip-link" href="#main-content">{{ t('a11y.skipToMain') }}</a>
  <div class="seim-route-progress" :class="{ 'is-active': routeBusy }" aria-hidden="true">
    <div class="seim-route-progress__bar" />
  </div>
  <div
    id="seim-route-announce"
    class="visually-hidden"
    role="status"
    aria-live="polite"
    aria-atomic="true"
  />
  <main id="main-content" tabindex="-1" :aria-busy="routeBusy ? 'true' : undefined">
    <router-view />
  </main>
  <ToastContainer />
  <ConfirmDialog />
</template>

<script setup>
import { onBeforeUnmount, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import api from '@/services/api'
import { useNotificationWebSocket } from '@/services/websocket'
import { applyUiPreferences, clearUiPreferences, mergeUiPreferencesFromServer, readStoredUiPreferences } from '@/services/uiPreferences'
import router from '@/router'
import { routeBusy } from '@/router/routeBusy'
import { syncAppMetaDescription, syncAppSocialMeta, syncCanonicalLink } from '@/utils/documentTitle'
import { formatNotificationCopy } from '@/utils/notificationCopy'
import { useBranding } from '@/composables/useBranding'
import ToastContainer from '@/components/ToastContainer.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'

const { t, te, locale } = useI18n()
const authStore = useAuthStore()
const { loadBranding } = useBranding()
const { info } = useToast()
let mediaQuery = null
let mediaQueryListener = null

const { connectIfAuthenticated, disconnect } = useNotificationWebSocket(authStore, {
  onNotification(notification) {
    const copy = formatNotificationCopy(notification, { t, te })
    const message = copy.message || copy.title || t('notifications.fallbackToast')
    info(message, 6000)
    window.dispatchEvent(new CustomEvent('notification-new', { detail: notification }))
  },
})

async function loadUiPreferences() {
  try {
    const { data } = await api.get('/api/accounts/user-settings/')
    applyUiPreferences(mergeUiPreferencesFromServer(data))
  } catch (error) {
    const stored = readStoredUiPreferences()
    applyUiPreferences(stored || { theme: 'light' })
  }
}

onMounted(async () => {
  loadBranding()
  syncAppMetaDescription(t)
  syncAppSocialMeta(t, router.currentRoute.value)
  if (typeof window !== 'undefined') {
    const href = new URL(router.resolve(router.currentRoute.value).href, window.location.origin).href
    syncCanonicalLink(href)
  }
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

watch(locale, () => {
  syncAppMetaDescription(t)
  syncAppSocialMeta(t, router.currentRoute.value)
  if (typeof window !== 'undefined') {
    const href = new URL(router.resolve(router.currentRoute.value).href, window.location.origin).href
    syncCanonicalLink(href)
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
