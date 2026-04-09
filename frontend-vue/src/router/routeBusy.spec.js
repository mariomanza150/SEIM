/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach } from 'vitest'
import { routeBusy } from './routeBusy'

describe('routeBusy', () => {
  beforeEach(() => {
    routeBusy.value = false
  })

  it('defaults to false', () => {
    expect(routeBusy.value).toBe(false)
  })
})
