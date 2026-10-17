/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { scrollMainIntoView } from './scrollMain'

function fakeEl(top, scrollTop = 0) {
  return { scrollTop, getBoundingClientRect: () => ({ top }) }
}

describe('scrollMainIntoView', () => {
  beforeEach(() => {
    window.scrollTo = vi.fn()
    window.matchMedia = vi.fn(() => ({ matches: false }))
    Object.defineProperty(window, 'scrollY', { value: 0, writable: true, configurable: true })
  })

  it('does nothing without an element', () => {
    expect(scrollMainIntoView(null)).toBe(false)
    expect(window.scrollTo).not.toHaveBeenCalled()
  })

  it('does not scroll when main content is already in view', () => {
    window.scrollY = 0
    expect(scrollMainIntoView(fakeEl(90))).toBe(false)
    expect(window.scrollTo).not.toHaveBeenCalled()
  })

  it('smooth-scrolls back to the main column when the page is scrolled down', () => {
    window.scrollY = 800
    expect(scrollMainIntoView(fakeEl(-710))).toBe(true)
    expect(window.scrollTo).toHaveBeenCalledWith({ top: 18, behavior: 'smooth' })
  })

  it('respects prefers-reduced-motion', () => {
    window.scrollY = 500
    window.matchMedia = vi.fn(() => ({ matches: true }))
    scrollMainIntoView(fakeEl(-400))
    expect(window.scrollTo).toHaveBeenCalledWith({ top: 28, behavior: 'auto' })
  })

  it('resets the element own scroll position', () => {
    const el = fakeEl(100, 250)
    scrollMainIntoView(el)
    expect(el.scrollTop).toBe(0)
  })
})
