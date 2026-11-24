import { ref, readonly } from 'vue'

import api from '@/services/api'
import { applyBrandTheme } from '@/utils/brandTheme'

/** Neutral SPA chrome while /api/branding/ is loading or unavailable. */
export const FALLBACK_BRANDING = {
  logo_url: '',
  nav_brand: 'SEIM',
  short_name: 'SEIM',
  name: 'SEIM',
  tagline: 'Student Exchange',
  theme_css: '',
  theme: {
    primary: '#2E5790',
    primary_light: '#3251AC',
    primary_dark: '#1E3A5F',
    accent: '#BF9B4C',
    accent_light: '#EDB621',
    accent_dark: '#A6863D',
    navy: '#1E3A5F',
    orange: '#E67E22',
    text: '#2C3E50',
  },
}

const branding = ref({ ...FALLBACK_BRANDING })
const loading = ref(false)
const error = ref('')
const hydrated = ref(false)
let fetchPromise = null
let defaultsApplied = false

function ensureDefaultTheme() {
  if (defaultsApplied || typeof document === 'undefined') return
  applyBrandTheme(branding.value)
  defaultsApplied = true
}

function normalizeBranding(data) {
  const shortName = data.short_name || FALLBACK_BRANDING.short_name
  const tagline = data.tagline || FALLBACK_BRANDING.tagline
  return {
    logo_url: data.logo_url || FALLBACK_BRANDING.logo_url,
    nav_brand:
      data.nav_brand ||
      [shortName, tagline].filter(Boolean).join(' ') ||
      FALLBACK_BRANDING.nav_brand,
    short_name: shortName,
    name: data.name || FALLBACK_BRANDING.name,
    tagline,
    theme_css: data.theme_css || FALLBACK_BRANDING.theme_css,
    theme: { ...FALLBACK_BRANDING.theme, ...(data.theme || {}) },
  }
}

/** Browser-tab / og:site_name suffix from active institution branding. */
export function getBrandTitleSuffix() {
  ensureDefaultTheme()
  return branding.value?.short_name || FALLBACK_BRANDING.short_name
}

/** Test helper: restore neutral fallback and clear hydration. */
export function resetBrandingForTests() {
  branding.value = { ...FALLBACK_BRANDING }
  loading.value = false
  error.value = ''
  hydrated.value = false
  fetchPromise = null
  defaultsApplied = false
}

export function useBranding() {
  ensureDefaultTheme()

  async function loadBranding(force = false) {
    if (hydrated.value && !force) return branding.value
    if (fetchPromise && !force) return fetchPromise

    loading.value = true
    error.value = ''
    fetchPromise = api
      .get('/api/branding/')
      .then(({ data }) => {
        branding.value = normalizeBranding(data)
        applyBrandTheme(branding.value)
        defaultsApplied = true
        hydrated.value = true
        return branding.value
      })
      .catch((err) => {
        error.value = err?.message || 'Failed to load branding'
        branding.value = { ...FALLBACK_BRANDING }
        applyBrandTheme(branding.value)
        defaultsApplied = true
        hydrated.value = true
        return branding.value
      })
      .finally(() => {
        loading.value = false
        fetchPromise = null
      })

    return fetchPromise
  }

  return {
    branding: readonly(branding),
    loading: readonly(loading),
    error: readonly(error),
    loadBranding,
  }
}
