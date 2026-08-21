/**
 * @vitest-environment jsdom
 */
import { describe, it, expect } from 'vitest'
import { sanitizeHelpHtml } from './helpHtml'

describe('sanitizeHelpHtml', () => {
  it('keeps safe markup and strips scripts', () => {
    const html = '<p>Hello</p><script>alert(1)</script><p onclick="x()">World</p>'
    const out = sanitizeHelpHtml(html)
    expect(out).toContain('Hello')
    expect(out).toContain('World')
    expect(out).not.toContain('script')
    expect(out).not.toContain('onclick')
  })

  it('rejects javascript URLs', () => {
    const out = sanitizeHelpHtml('<a href="javascript:alert(1)">x</a>')
    expect(out).not.toContain('javascript:')
  })
})
