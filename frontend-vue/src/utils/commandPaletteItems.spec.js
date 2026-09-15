/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach } from 'vitest'
import i18n, { setAppLocale } from '@/i18n'
import {
  handleCommandPaletteShortcut,
  useCommandPalette,
} from '@/composables/useCommandPalette'
import {
  buildCommandPaletteItems,
  filterCommandPaletteItems,
} from '@/utils/commandPaletteItems'

describe('commandPaletteItems', () => {
  beforeEach(() => {
    setAppLocale('en')
  })

  it('includes staff routes only when allowed', () => {
    const student = buildCommandPaletteItems({
      t: i18n.global.t,
      canUsePartnerPortal: false,
      canUseStaffReviewQueue: false,
      isAdmin: false,
    })
    expect(student.some((item) => item.id === 'reviewQueue')).toBe(false)

    const staff = buildCommandPaletteItems({
      t: i18n.global.t,
      canUsePartnerPortal: false,
      canUseStaffReviewQueue: true,
      isAdmin: false,
    })
    expect(staff.some((item) => item.id === 'reviewQueue')).toBe(true)
  })

  it('includes admin routes for admins', () => {
    const items = buildCommandPaletteItems({
      t: i18n.global.t,
      canUsePartnerPortal: false,
      canUseStaffReviewQueue: true,
      isAdmin: true,
    })
    expect(items.some((item) => item.id === 'adminUsers')).toBe(true)
  })

  it('filters by label tokens', () => {
    const items = buildCommandPaletteItems({
      t: i18n.global.t,
      canUsePartnerPortal: false,
      canUseStaffReviewQueue: true,
      isAdmin: false,
    })
    const filtered = filterCommandPaletteItems(items, 'review')
    expect(filtered.some((item) => item.id === 'reviewQueue')).toBe(true)
    expect(filtered.length).toBeGreaterThan(0)
  })
})

describe('useCommandPalette shortcut', () => {
  beforeEach(() => {
    useCommandPalette().closePalette()
  })

  it('opens on Ctrl+K when not in an editable field', () => {
    const api = useCommandPalette()
    const event = new KeyboardEvent('keydown', { key: 'k', ctrlKey: true, cancelable: true })
    Object.defineProperty(event, 'target', { value: document.body })
    expect(handleCommandPaletteShortcut(event, { ...api, open: api.paletteState.open })).toBe(true)
    expect(api.paletteState.open).toBe(true)
  })

  it('toggles closed when already open', () => {
    const api = useCommandPalette()
    api.openPalette()
    const event = new KeyboardEvent('keydown', { key: 'k', metaKey: true, cancelable: true })
    Object.defineProperty(event, 'target', { value: document.body })
    expect(handleCommandPaletteShortcut(event, { ...api, open: true })).toBe(true)
    expect(api.paletteState.open).toBe(false)
  })

  it('ignores Ctrl+K in inputs when closed', () => {
    const api = useCommandPalette()
    api.closePalette()
    const input = document.createElement('input')
    document.body.appendChild(input)
    const event = new KeyboardEvent('keydown', { key: 'k', ctrlKey: true, cancelable: true })
    Object.defineProperty(event, 'target', { value: input })
    expect(handleCommandPaletteShortcut(event, { ...api, open: false })).toBe(false)
    expect(api.paletteState.open).toBe(false)
    input.remove()
  })
})
