/**
 * SEIM Theme Manager
 * Light/dark toggle, localStorage `seim-theme`, and bridge to Vue `seim_ui_preferences`.
 */

const UI_PREFS_KEY = 'seim_ui_preferences'

function themeDebugEnabled() {
  try {
    if (typeof window === 'undefined') return false
    if (window.location && window.location.search && window.location.search.indexOf('debug_theme=1') !== -1) {
      return true
    }
    return localStorage.getItem('DEBUG_THEME') === '1'
  } catch (e) {
    return false
  }
}

function themeLog() {
  if (themeDebugEnabled() && typeof console !== 'undefined' && console.log) {
    console.log.apply(console, arguments)
  }
}

class ThemeManager {
  constructor() {
    this.themeKey = 'seim-theme'
    this.themeToggle = null
    const initial = this.resolveInitialResolvedTheme()
    this.currentTheme = initial.theme
    this.followSystemTheme = initial.followSystem

    themeLog('ThemeManager: initial', initial)

    this.init()
  }

  /**
   * Same rules as inline pre-init in base.html — keep in sync.
   * @returns {{ theme: 'light'|'dark', followSystem: boolean }}
   */
  resolveInitialResolvedTheme() {
    let explicit
    try {
      explicit = localStorage.getItem(this.themeKey)
    } catch (e) {
      explicit = null
    }
    if (explicit === 'light' || explicit === 'dark') {
      return { theme: explicit, followSystem: false }
    }

    let vueTheme = null
    try {
      const raw = localStorage.getItem(UI_PREFS_KEY)
      if (raw) {
        const p = JSON.parse(raw)
        if (p && typeof p.theme === 'string') vueTheme = p.theme
      }
    } catch (e) {
      vueTheme = null
    }

    if (vueTheme === 'light' || vueTheme === 'dark') {
      return { theme: vueTheme, followSystem: false }
    }

    const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    return { theme: isDark ? 'dark' : 'light', followSystem: true }
  }

  getStoredTheme() {
    try {
      return localStorage.getItem(this.themeKey)
    } catch (error) {
      return null
    }
  }

  getSystemTheme() {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  }

  storeTheme(theme) {
    try {
      localStorage.setItem(this.themeKey, theme)
    } catch (error) {
      themeLog('ThemeManager: could not store seim-theme', error)
    }
  }

  /**
   * Merge theme into Vue SPA storage so Settings stays aligned after toggling on Django pages.
   */
  syncVueUiPreferencesTheme(theme) {
    try {
      const raw = localStorage.getItem(UI_PREFS_KEY)
      let base = {}
      if (raw) {
        base = JSON.parse(raw)
      }
      base.theme = theme
      localStorage.setItem(UI_PREFS_KEY, JSON.stringify(base))
    } catch (e) {
      themeLog('ThemeManager: sync Vue prefs failed', e)
    }
  }

  setThemeDom(theme) {
    const html = document.documentElement
    if (theme === 'dark') {
      html.setAttribute('data-theme', 'dark')
    } else {
      html.setAttribute('data-theme', 'light')
    }
  }

  init() {
    this.setThemeDom(this.currentTheme)
    if (!this.followSystemTheme && !this.getStoredTheme()) {
      this.storeTheme(this.currentTheme)
    }
    this.createThemeToggle()
    this.setupEventListeners()
    this.updateToggleState()
  }

  applyTheme(theme) {
    this.followSystemTheme = false
    themeLog('ThemeManager: applyTheme', theme)

    this.setThemeDom(theme)
    this.storeTheme(theme)
    this.syncVueUiPreferencesTheme(theme)
    this.currentTheme = theme

    this.updateToggleState()

    window.dispatchEvent(
      new CustomEvent('themeChanged', {
        detail: { theme: theme },
      }),
    )

    this.showThemeFeedback(theme)
  }

  toggleTheme() {
    const newTheme = this.currentTheme === 'light' ? 'dark' : 'light'
    this.applyTheme(newTheme)
  }

  createThemeToggle() {
    this.themeToggle = document.getElementById('theme-toggle')

    if (this.themeToggle) {
      this.setupToggleEventListeners()
      return
    }

    const toggle = document.createElement('button')
    toggle.id = 'theme-toggle'
    toggle.className = 'btn btn-outline-secondary btn-sm theme-toggle'
    toggle.setAttribute('aria-label', 'Toggle dark mode')
    toggle.setAttribute('title', 'Toggle dark mode')
    toggle.setAttribute('type', 'button')

    const icon = document.createElement('i')
    icon.className = 'bi bi-moon-fill'
    toggle.appendChild(icon)

    const nav = document.querySelector('#navbarNav ul.navbar-nav.ms-auto')
    if (nav) {
      const navItem = document.createElement('li')
      navItem.className = 'nav-item'
      const wrap = document.createElement('div')
      wrap.className = 'theme-toggle-wrapper d-flex align-items-center'
      wrap.appendChild(toggle)
      const feedback = document.createElement('div')
      feedback.id = 'theme-feedback'
      feedback.className = 'theme-feedback'
      feedback.style.display = 'none'
      feedback.setAttribute('role', 'status')
      feedback.setAttribute('aria-live', 'polite')
      wrap.appendChild(feedback)
      navItem.appendChild(wrap)
      nav.insertBefore(navItem, nav.firstChild)
    } else {
      toggle.style.position = 'fixed'
      toggle.style.top = '20px'
      toggle.style.right = '20px'
      toggle.style.zIndex = '1000'
      document.body.appendChild(toggle)
    }

    this.themeToggle = toggle
    this.setupToggleEventListeners()
  }

  updateToggleState() {
    if (!this.themeToggle) return

    const icon = this.themeToggle.querySelector('i')
    if (!icon) return

    const isDark = this.currentTheme === 'dark'
    icon.className = isDark ? 'bi bi-sun-fill' : 'bi bi-moon-fill'

    const lightLabel = 'Switch to light mode'
    const darkLabel = 'Switch to dark mode'
    this.themeToggle.setAttribute('aria-label', isDark ? lightLabel : darkLabel)
    this.themeToggle.setAttribute('title', isDark ? lightLabel : darkLabel)
  }

  setupToggleEventListeners() {
    if (!this.themeToggle) return
    this.themeToggle.addEventListener('click', (e) => {
      e.preventDefault()
      this.toggleTheme()
    })
  }

  setupEventListeners() {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    mediaQuery.addEventListener('change', (e) => {
      if (!this.followSystemTheme) return
      const newTheme = e.matches ? 'dark' : 'light'
      this.currentTheme = newTheme
      this.setThemeDom(newTheme)
      this.updateToggleState()
    })

    document.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'T') {
        e.preventDefault()
        this.toggleTheme()
      }
    })
  }

  getCurrentTheme() {
    return this.currentTheme
  }

  isDarkMode() {
    return this.currentTheme === 'dark'
  }

  showThemeFeedback(theme) {
    const feedback = document.getElementById('theme-feedback')
    if (!feedback) return

    feedback.textContent = theme === 'dark' ? 'Dark theme on' : 'Light theme on'
    feedback.style.display = 'block'
    setTimeout(() => {
      feedback.classList.add('show')
    }, 10)
    setTimeout(() => {
      feedback.classList.remove('show')
      setTimeout(() => {
        feedback.style.display = 'none'
      }, 300)
    }, 2000)
  }

  refresh() {
    this.setThemeDom(this.currentTheme)
  }

  resetToSystem() {
    localStorage.removeItem(this.themeKey)
    this.followSystemTheme = true
    const systemTheme = this.getSystemTheme()
    this.currentTheme = systemTheme
    this.setThemeDom(systemTheme)
    this.updateToggleState()
  }

  forceLight() {
    this.applyTheme('light')
  }

  forceDark() {
    this.applyTheme('dark')
  }

  emergencyReset() {
    try {
      const allKeys = Object.keys(localStorage)
      const themeKeys = allKeys.filter((key) => key.toLowerCase().includes('theme'))
      themeKeys.forEach((key) => localStorage.removeItem(key))
      this.followSystemTheme = false
      this.applyTheme('light')
      setTimeout(() => {
        window.location.reload()
      }, 1000)
    } catch (error) {
      console.error('ThemeManager: Emergency reset failed:', error)
    }
  }

  debug() {
    console.log('=== Theme Manager Debug ===')
    console.log('Current theme:', this.currentTheme)
    console.log('Follow system:', this.followSystemTheme)
    console.log('Stored seim-theme:', this.getStoredTheme())
    console.log('System theme:', this.getSystemTheme())
    console.log('Toggle button found:', !!this.themeToggle)
    console.log('HTML data-theme:', document.documentElement.getAttribute('data-theme'))
    console.log('=== End Debug ===')
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.themeManager = new ThemeManager()
})

window.SEIMThemeUtils = {
  emergencyReset() {
    if (window.themeManager) window.themeManager.emergencyReset()
    else console.error('Theme manager not available')
  },
  debug() {
    if (window.themeManager) window.themeManager.debug()
    else console.error('Theme manager not available')
  },
  forceLight() {
    if (window.themeManager) window.themeManager.forceLight()
    else console.error('Theme manager not available')
  },
  forceDark() {
    if (window.themeManager) window.themeManager.forceDark()
    else console.error('Theme manager not available')
  },
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = ThemeManager
}
