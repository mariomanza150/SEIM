import { createI18n } from 'vue-i18n'
import en from '../locales/en.json'
import es from '../locales/es.json'

export const LOCALE_STORAGE_KEY = 'seim.ui_locale'

const SUPPORTED = ['en', 'es']

export function getStoredLocale() {
  if (typeof localStorage === 'undefined') return null
  const v = localStorage.getItem(LOCALE_STORAGE_KEY)
  return SUPPORTED.includes(v) ? v : null
}

export function detectBrowserLocale() {
  if (typeof navigator === 'undefined') return 'en'
  const lang = (navigator.language || '').toLowerCase()
  if (lang.startsWith('es')) return 'es'
  return 'en'
}

export function getInitialLocale() {
  return getStoredLocale() || detectBrowserLocale()
}

function syncDocumentLang(locale) {
  if (typeof document !== 'undefined') {
    document.documentElement.lang = locale
  }
}

const initialLocale = getInitialLocale()

const i18n = createI18n({
  legacy: false,
  locale: initialLocale,
  fallbackLocale: 'en',
  messages: { en, es },
  globalInjection: true,
})

export function setAppLocale(locale) {
  if (!SUPPORTED.includes(locale)) return
  i18n.global.locale.value = locale
  if (typeof localStorage !== 'undefined') {
    localStorage.setItem(LOCALE_STORAGE_KEY, locale)
  }
  syncDocumentLang(locale)
}

syncDocumentLang(initialLocale)

export default i18n
