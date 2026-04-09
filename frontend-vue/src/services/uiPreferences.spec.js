import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import {
  applyUiPreferences,
  clearUiPreferences,
  readStoredUiPreferences,
  THEME_COLOR_DARK,
  THEME_COLOR_LIGHT,
} from './uiPreferences'

describe('uiPreferences', () => {
  let themeColorMeta

  beforeEach(() => {
    themeColorMeta = document.createElement('meta')
    themeColorMeta.setAttribute('name', 'theme-color')
    themeColorMeta.setAttribute('content', THEME_COLOR_LIGHT)
    document.head.appendChild(themeColorMeta)
  })

  afterEach(() => {
    clearUiPreferences()
    themeColorMeta.remove()
  })

  it('applies theme, font size, and accessibility attributes to the document', () => {
    applyUiPreferences({
      theme: 'dark',
      font_size: 'x-large',
      high_contrast: true,
      reduce_motion: true,
    })

    expect(document.documentElement.dataset.theme).toBe('dark')
    expect(document.documentElement.dataset.themePreference).toBe('dark')
    expect(document.documentElement.dataset.fontSize).toBe('x-large')
    expect(document.documentElement.dataset.highContrast).toBe('true')
    expect(document.documentElement.dataset.reduceMotion).toBe('true')
    expect(document.documentElement.style.fontSize).toBe('20px')
  })

  it('persists and reloads stored preferences', () => {
    applyUiPreferences({
      theme: 'light',
      font_size: 'large',
      high_contrast: false,
      reduce_motion: true,
    })

    expect(readStoredUiPreferences()).toEqual({
      theme: 'light',
      font_size: 'large',
      high_contrast: false,
      reduce_motion: true,
    })
  })

  it('syncs meta theme-color with resolved theme and resets on clear', () => {
    applyUiPreferences({ theme: 'dark', font_size: 'normal' })
    expect(themeColorMeta.getAttribute('content')).toBe(THEME_COLOR_DARK)
    applyUiPreferences({ theme: 'light', font_size: 'normal' })
    expect(themeColorMeta.getAttribute('content')).toBe(THEME_COLOR_LIGHT)
    applyUiPreferences({ theme: 'dark', font_size: 'normal' })
    clearUiPreferences()
    expect(themeColorMeta.getAttribute('content')).toBe(THEME_COLOR_LIGHT)
  })
})
