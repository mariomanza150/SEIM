/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'

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
import { FALLBACK_BRANDING, getBrandTitleSuffix, useBranding } from '@/composables/useBranding'

describe('useBranding', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('exposes UAdeC fallback defaults before the API responds', () => {
    expect(FALLBACK_BRANDING.short_name).toBe('UAdeC')
    expect(FALLBACK_BRANDING.theme.primary).toBe('#2E5790')
    expect(getBrandTitleSuffix()).toBe('UAdeC')
    const { branding } = useBranding()
    expect(branding.value.short_name).toBe('UAdeC')
    expect(branding.value.nav_brand).toContain('UAdeC')
    expect(applyBrandTheme).toHaveBeenCalled()
  })

  it('loads branding from API and applies theme', async () => {
    api.get.mockResolvedValue({
      data: {
        logo_url: '/static/exampleu/logos/institution-logo.png',
        nav_brand: 'EXU Mobility',
        short_name: 'EXU',
        name: 'Example University',
        tagline: 'Student Mobility',
        theme_css: 'exampleu/theme.css',
        theme: { primary: '#111111', accent: '#ABCDEF' },
      },
    })

    const { branding, loadBranding } = useBranding()
    const result = await loadBranding(true)
    expect(result.nav_brand).toBe('EXU Mobility')
    expect(result.tagline).toBe('Student Mobility')
    expect(branding.value.logo_url).toBe('/static/exampleu/logos/institution-logo.png')
    expect(branding.value.theme.primary).toBe('#111111')
    expect(getBrandTitleSuffix()).toBe('EXU')
    expect(applyBrandTheme).toHaveBeenCalled()
  })

  it('falls back to UAdeC defaults when API fails', async () => {
    api.get.mockRejectedValue(new Error('Network error'))

    const { branding, loadBranding } = useBranding()
    const result = await loadBranding(true)
    expect(result.nav_brand).toBe(FALLBACK_BRANDING.nav_brand)
    expect(branding.value.short_name).toBe('UAdeC')
    expect(branding.value.theme.accent).toBe('#BF9B4C')
    expect(getBrandTitleSuffix()).toBe('UAdeC')
    expect(applyBrandTheme).toHaveBeenCalled()
  })
})
