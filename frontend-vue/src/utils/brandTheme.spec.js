/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { applyBrandTheme, hexToRgbTriplet } from '@/utils/brandTheme'

describe('brandTheme', () => {
  beforeEach(() => {
    document.getElementById('seim-institution-theme-css')?.remove()
    document.getElementById('seim-institution-theme-vars')?.remove()
  })

  afterEach(() => {
    document.getElementById('seim-institution-theme-css')?.remove()
    document.getElementById('seim-institution-theme-vars')?.remove()
  })

  it('converts 6-digit hex to rgb triplet', () => {
    expect(hexToRgbTriplet('#2E5790')).toBe('46, 87, 144')
    expect(hexToRgbTriplet('667eea')).toBe('102, 126, 234')
  })

  it('converts 3-digit hex to rgb triplet', () => {
    expect(hexToRgbTriplet('#fff')).toBe('255, 255, 255')
  })

  it('returns null for invalid hex', () => {
    expect(hexToRgbTriplet('')).toBeNull()
    expect(hexToRgbTriplet('not-a-color')).toBeNull()
  })

  it('applies UAdeC CSS custom properties from branding payload', () => {
    applyBrandTheme({
      theme_css: 'uadec/theme.css',
      theme: { primary: '#2E5790', accent: '#BF9B4C' },
    })
    const link = document.getElementById('seim-institution-theme-css')
    const style = document.getElementById('seim-institution-theme-vars')
    expect(link.getAttribute('href')).toBe('/static/uadec/theme.css')
    expect(style.textContent).toContain('--brand-primary: #2E5790')
    expect(style.textContent).toContain('--brand-accent: #BF9B4C')
    expect(style.textContent).toContain('--bs-primary-rgb: 46, 87, 144')
  })

  it('uses packaged UAdeC color fallbacks when theme colors are missing', () => {
    applyBrandTheme({ theme_css: 'uadec/theme.css', theme: {} })
    const style = document.getElementById('seim-institution-theme-vars')
    expect(style.textContent).toContain('--brand-primary: #2E5790')
    expect(style.textContent).toContain('--brand-accent: #BF9B4C')
  })
})
