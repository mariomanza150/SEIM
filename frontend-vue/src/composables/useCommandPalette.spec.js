/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import {
  useCommandPalette,
  handleCommandPaletteShortcut,
  isCommandPaletteEditableTarget,
} from './useCommandPalette'

describe('useCommandPalette', () => {
  beforeEach(() => {
    const { closePalette } = useCommandPalette()
    closePalette()
  })

  it('opens, toggles, and closes the palette state', () => {
    const palette = useCommandPalette()
    expect(palette.paletteState.open).toBe(false)
    palette.openPalette()
    expect(palette.paletteState.open).toBe(true)
    palette.togglePalette()
    expect(palette.paletteState.open).toBe(false)
    palette.togglePalette()
    expect(palette.paletteState.open).toBe(true)
    palette.closePalette()
    expect(palette.paletteState.open).toBe(false)
  })

  it('consumes Ctrl/Cmd+K and toggles when already open', () => {
    const palette = useCommandPalette()
    palette.openPalette()
    const event = new KeyboardEvent('keydown', { key: 'k', ctrlKey: true })
    const preventDefault = vi.spyOn(event, 'preventDefault')
    expect(
      handleCommandPaletteShortcut(event, {
        open: true,
        openPalette: palette.openPalette,
        closePalette: palette.closePalette,
        togglePalette: palette.togglePalette,
      }),
    ).toBe(true)
    expect(preventDefault).toHaveBeenCalled()
    expect(palette.paletteState.open).toBe(false)
  })

  it('opens from Ctrl/Cmd+K when closed and target is not editable', () => {
    const palette = useCommandPalette()
    const event = new KeyboardEvent('keydown', { key: 'K', metaKey: true })
    Object.defineProperty(event, 'target', { value: document.body })
    expect(
      handleCommandPaletteShortcut(event, {
        open: false,
        openPalette: palette.openPalette,
        closePalette: palette.closePalette,
        togglePalette: palette.togglePalette,
      }),
    ).toBe(true)
    expect(palette.paletteState.open).toBe(true)
  })

  it('does not open when Ctrl/Cmd+K is pressed in an editable field', () => {
    const palette = useCommandPalette()
    const input = document.createElement('input')
    document.body.appendChild(input)
    const event = new KeyboardEvent('keydown', { key: 'k', ctrlKey: true })
    Object.defineProperty(event, 'target', { value: input })
    expect(
      handleCommandPaletteShortcut(event, {
        open: false,
        openPalette: palette.openPalette,
        closePalette: palette.closePalette,
        togglePalette: palette.togglePalette,
      }),
    ).toBe(false)
    expect(palette.paletteState.open).toBe(false)
    input.remove()
  })

  it('ignores non-shortcut key events', () => {
    expect(handleCommandPaletteShortcut(null, {})).toBe(false)
    expect(
      handleCommandPaletteShortcut(new KeyboardEvent('keydown', { key: 'k' }), {
        open: false,
        openPalette: () => {},
        closePalette: () => {},
        togglePalette: () => {},
      }),
    ).toBe(false)
    expect(
      handleCommandPaletteShortcut(new KeyboardEvent('keydown', { key: 'k', ctrlKey: true, altKey: true }), {
        open: false,
        openPalette: () => {},
        closePalette: () => {},
        togglePalette: () => {},
      }),
    ).toBe(false)
  })

  it('detects editable targets including contenteditable hosts', () => {
    expect(isCommandPaletteEditableTarget(null)).toBe(false)
    expect(isCommandPaletteEditableTarget(document.createElement('textarea'))).toBe(true)
    expect(isCommandPaletteEditableTarget(document.createElement('select'))).toBe(true)

    const editable = document.createElement('div')
    editable.setAttribute('contenteditable', 'true')
    document.body.appendChild(editable)
    expect(isCommandPaletteEditableTarget(editable)).toBe(true)
    editable.remove()

    const child = document.createElement('span')
    const host = document.createElement('div')
    host.setAttribute('contenteditable', 'true')
    host.appendChild(child)
    document.body.appendChild(host)
    expect(isCommandPaletteEditableTarget(child)).toBe(true)
    host.remove()
  })
})
