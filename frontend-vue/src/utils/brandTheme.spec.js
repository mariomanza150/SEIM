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

  it('applies brand CSS custom properties from branding payload', () => {
    applyBrandTheme({
      theme_css: 'exampleu/theme.css',
      theme: { primary: '#111111', accent: '#ABCDEF' },
    })
    const link = document.getElementById('seim-institution-theme-css')
    const style = document.getElementById('seim-institution-theme-vars')
    expect(link.getAttribute('href')).toBe('/static/exampleu/theme.css')
    expect(style.textContent).toContain('--brand-primary: #111111')
    expect(style.textContent).toContain('--brand-accent: #ABCDEF')
    expect(style.textContent).toContain('--bs-primary-rgb: 17, 17, 17')
    // Historical CSS aliases kept for template compatibility.
    expect(style.textContent).toContain('--uadec-blue: #111111')
  })

  it('uses packaged color fallbacks when theme colors are missing', () => {
    applyBrandTheme({ theme_css: '', theme: {} })
    const style = document.getElementById('seim-institution-theme-vars')
    expect(style.textContent).toContain('--brand-primary: #2E5790')
    expect(style.textContent).toContain('--brand-accent: #BF9B4C')
  })
})
