/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import i18n, { setAppLocale } from '@/i18n'
import { useThemeToggle } from './useThemeToggle'
import api from '@/services/api'
import {
  applyUiPreferences,
  readStoredUiPreferences,
} from '@/services/uiPreferences'

vi.mock('@/services/api', () => ({
  default: {
    patch: vi.fn(),
  },
}))

function mountComposable() {
  let expose
  const Comp = defineComponent({
    setup() {
      expose = useThemeToggle()
      return () => null
    },
  })
  mount(Comp, { global: { plugins: [i18n] } })
  return expose
}

describe('useThemeToggle', () => {
  beforeEach(() => {
    localStorage.clear()
    setAppLocale('en')
    vi.clearAllMocks()
    applyUiPreferences({
      theme: 'light',
      font_size: 'normal',
      high_contrast: false,
      reduce_motion: false,
    })
  })

  afterEach(() => {
    localStorage.clear()
    setAppLocale('en')
  })

  it('reports light theme and dark toggle aria by default', () => {
    const theme = mountComposable()
    expect(theme.resolvedIsDark.value).toBe(false)
    expect(theme.themeToggleAria.value).toContain('dark')
  })

  it('toggles theme locally and patches user settings', async () => {
    api.patch.mockResolvedValue({ data: {} })
    const theme = mountComposable()
    await theme.toggleTheme()
    expect(readStoredUiPreferences().theme).toBe('dark')
    expect(theme.resolvedIsDark.value).toBe(true)
    expect(api.patch).toHaveBeenCalledWith('/api/accounts/user-settings/', { theme: 'dark' })
  })

  it('keeps local theme when settings patch fails', async () => {
    api.patch.mockRejectedValue(new Error('offline'))
    const theme = mountComposable()
    await theme.toggleTheme()
    expect(readStoredUiPreferences().theme).toBe('dark')
    expect(theme.resolvedIsDark.value).toBe(true)
  })

  it('toggles back from dark to light', async () => {
    applyUiPreferences({
      theme: 'dark',
      font_size: 'normal',
      high_contrast: false,
      reduce_motion: false,
    })
    api.patch.mockResolvedValue({ data: {} })
    const theme = mountComposable()
    expect(theme.resolvedIsDark.value).toBe(true)
    await theme.toggleTheme()
    expect(readStoredUiPreferences().theme).toBe('light')
    expect(theme.resolvedIsDark.value).toBe(false)
  })
})
