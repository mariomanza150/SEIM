import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  applyUiPreferences,
  readStoredUiPreferences,
  resolveTheme,
} from '@/services/uiPreferences'
import api from '@/services/api'

/**
 * Shared light/dark theme toggle for AppShell and AuthLayout.
 */
export function useThemeToggle() {
  const { t } = useI18n()
  const themeUiTick = ref(0)

  const resolvedIsDark = computed(() => {
    themeUiTick.value
    const cur = readStoredUiPreferences() || {}
    return resolveTheme(cur.theme || 'auto') === 'dark'
  })

  const themeToggleAria = computed(() =>
    resolvedIsDark.value ? t('dashboard.themeToggleAriaLight') : t('dashboard.themeToggleAriaDark'),
  )

  async function toggleTheme() {
    const cur = readStoredUiPreferences() || {}
    const resolved = resolveTheme(cur.theme || 'auto')
    const nextTheme = resolved === 'dark' ? 'light' : 'dark'
    applyUiPreferences({
      ...cur,
      theme: nextTheme,
      font_size: cur.font_size || 'normal',
      high_contrast: Boolean(cur.high_contrast),
      reduce_motion: Boolean(cur.reduce_motion),
    })
    themeUiTick.value += 1
    try {
      await api.patch('/api/accounts/user-settings/', { theme: nextTheme })
    } catch {
      /* local preference already applied */
    }
  }

  return {
    resolvedIsDark,
    themeToggleAria,
    toggleTheme,
  }
}
