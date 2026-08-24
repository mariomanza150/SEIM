import { describe, it, expect, vi, beforeEach } from 'vitest'

import { useBranding } from '@/composables/useBranding'



vi.mock('@/services/api', () => ({

  default: {

    get: vi.fn(),

  },

}))



vi.mock('@/utils/brandTheme', () => ({

  applyBrandTheme: vi.fn(),

}))



import api from '@/services/api'

import { applyBrandTheme } from '@/utils/brandTheme'



describe('useBranding', () => {

  beforeEach(() => {

    vi.clearAllMocks()

  })



  it('loads branding from API and applies theme', async () => {

    api.get.mockResolvedValue({

      data: {

        logo_url: '/static/logo.png',

        nav_brand: 'UAdeC Intercambio',

        short_name: 'UAdeC',

        name: 'Universidad Autónoma de Coahuila',

        theme_css: 'uadec/theme.css',

        theme: { primary: '#2E5790', accent: '#BF9B4C' },

      },

    })



    const { branding, loadBranding } = useBranding()

    const result = await loadBranding(true)

    expect(result.nav_brand).toBe('UAdeC Intercambio')

    expect(branding.value.logo_url).toBe('/static/logo.png')

    expect(branding.value.theme.primary).toBe('#2E5790')

    expect(applyBrandTheme).toHaveBeenCalled()

  })



  it('falls back when API fails', async () => {

    api.get.mockRejectedValue(new Error('Network error'))

    const { branding, loadBranding } = useBranding()

    const result = await loadBranding(true)

    expect(result.nav_brand).toBe('SEIM')

    expect(branding.value.short_name).toBe('SEIM')

    expect(applyBrandTheme).toHaveBeenCalled()

  })

})

