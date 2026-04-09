/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { focusMainContent } from './a11y'

describe('focusMainContent', () => {
  beforeEach(() => {
    document.body.innerHTML = ''
  })

  afterEach(() => {
    document.body.innerHTML = ''
  })

  it('focuses #main-content when present', () => {
    document.body.innerHTML = '<main id="main-content" tabindex="-1"></main>'
    const el = document.getElementById('main-content')
    const spy = vi.spyOn(el, 'focus')
    focusMainContent()
    expect(spy).toHaveBeenCalledWith({ preventScroll: true })
  })

  it('does not throw when landmark is missing', () => {
    expect(() => focusMainContent()).not.toThrow()
  })
})
