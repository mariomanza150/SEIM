import { ref, readonly } from 'vue'

import api from '@/services/api'

import { applyBrandTheme } from '@/utils/brandTheme'



const branding = ref(null)

const loading = ref(false)

const error = ref('')

let fetchPromise = null



const FALLBACK = {

  logo_url: '/static/uadec/logos/institution-logo.png',

  nav_brand: 'SEIM',

  short_name: 'SEIM',

  name: 'SEIM',

  theme_css: 'uadec/theme.css',

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



function normalizeBranding(data) {

  return {

    logo_url: data.logo_url || FALLBACK.logo_url,

    nav_brand: data.nav_brand || data.short_name || FALLBACK.nav_brand,

    short_name: data.short_name || FALLBACK.short_name,

    name: data.name || FALLBACK.name,

    theme_css: data.theme_css || FALLBACK.theme_css,

    theme: { ...FALLBACK.theme, ...(data.theme || {}) },

  }

}



export function useBranding() {

  async function loadBranding(force = false) {

    if (branding.value && !force) return branding.value

    if (fetchPromise && !force) return fetchPromise



    loading.value = true

    error.value = ''

    fetchPromise = api

      .get('/api/branding/')

      .then(({ data }) => {

        branding.value = normalizeBranding(data)

        applyBrandTheme(branding.value)

        return branding.value

      })

      .catch((err) => {

        error.value = err?.message || 'Failed to load branding'

        branding.value = { ...FALLBACK }

        applyBrandTheme(branding.value)

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

