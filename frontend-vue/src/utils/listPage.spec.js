/**
 * @vitest-environment node
 */
import { describe, it, expect } from 'vitest'
import { resolveListPage } from './listPage'

describe('resolveListPage', () => {
  it('keeps integer page numbers', () => {
    expect(resolveListPage(2)).toBe(2)
    expect(resolveListPage('3')).toBe(3)
  })

  it('rejects DOM events and other non-page values', () => {
    expect(resolveListPage({ type: 'change' })).toBe(1)
    expect(resolveListPage('[object Event]')).toBe(1)
    expect(resolveListPage(0)).toBe(1)
    expect(resolveListPage(-1)).toBe(1)
    expect(resolveListPage(undefined)).toBe(1)
  })
})
