const STORAGE_KEY = 'seim_ui_preferences'

/** Browser chrome / PWA status bar; keep in sync with `index.html` shell bootstrap. */
export const THEME_COLOR_LIGHT = '#667eea'
export const THEME_COLOR_DARK = '#111827'

const FONT_SIZE_MAP = {
  normal: '16px',
  large: '18px',
  'x-large': '20px',
}

function getRootElement() {
  return typeof document !== 'undefined' ? document.documentElement : null
}

export function syncThemeColorMeta(resolvedTheme) {
  if (typeof document === 'undefined') return
  const el = document.querySelector('meta[name="theme-color"]')
  if (!el) return
  el.setAttribute(
    'content',
    resolvedTheme === 'dark' ? THEME_COLOR_DARK : THEME_COLOR_LIGHT,
  )
}

export function readStoredUiPreferences() {
  if (typeof localStorage === 'undefined') return null

  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch (error) {
    console.warn('Failed to read stored UI preferences:', error)
    return null
  }
}

export function resolveTheme(themePreference = 'auto') {
  if (
    themePreference === 'auto'
    && typeof window !== 'undefined'
    && typeof window.matchMedia === 'function'
  ) {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  }

  return themePreference === 'dark' ? 'dark' : 'light'
}

export function applyUiPreferences(settings = {}) {
  const root = getRootElement()
  if (!root) return null

  const themePreference = settings.theme || 'auto'
  const resolvedTheme = resolveTheme(themePreference)
  const fontSize = settings.font_size || 'normal'
  const highContrast = Boolean(settings.high_contrast)
  const reduceMotion = Boolean(settings.reduce_motion)

  root.dataset.theme = resolvedTheme
  root.dataset.themePreference = themePreference
  root.dataset.fontSize = fontSize
  root.dataset.highContrast = highContrast ? 'true' : 'false'
  root.dataset.reduceMotion = reduceMotion ? 'true' : 'false'
  root.style.fontSize = FONT_SIZE_MAP[fontSize] || FONT_SIZE_MAP.normal

  syncThemeColorMeta(resolvedTheme)

  if (typeof localStorage !== 'undefined') {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        theme: themePreference,
        font_size: fontSize,
        high_contrast: highContrast,
        reduce_motion: reduceMotion,
      }),
    )
  }

  return {
    theme: themePreference,
    resolvedTheme,
    font_size: fontSize,
    high_contrast: highContrast,
    reduce_motion: reduceMotion,
  }
}

export function clearUiPreferences() {
  const root = getRootElement()
  if (root) {
    delete root.dataset.theme
    delete root.dataset.themePreference
    delete root.dataset.fontSize
    delete root.dataset.highContrast
    delete root.dataset.reduceMotion
    root.style.fontSize = FONT_SIZE_MAP.normal
  }

  if (typeof localStorage !== 'undefined') {
    localStorage.removeItem(STORAGE_KEY)
  }

  syncThemeColorMeta('light')
}
