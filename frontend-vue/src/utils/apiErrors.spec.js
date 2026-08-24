/**
 * @vitest-environment jsdom
 */
import { describe, it, expect } from 'vitest'
import {
  fieldErrorsFromResponse,
  flattenFieldMessages,
  formatApiErrorResponse,
  getApiErrorMessage,
} from './apiErrors'

describe('apiErrors', () => {
  it('formats DRF detail strings', () => {
    expect(formatApiErrorResponse({ detail: 'Invalid credentials.' })).toBe(
      'Invalid credentials.',
    )
  })

  it('joins non_field_errors', () => {
    expect(formatApiErrorResponse({ non_field_errors: ['A', 'B'] })).toBe('A B')
  })

  it('maps field errors', () => {
    expect(fieldErrorsFromResponse({ email: ['Taken'], password: ['Too short'] })).toEqual({
      email: ['Taken'],
      password: ['Too short'],
    })
  })

  it('flattens nested messages', () => {
    expect(flattenFieldMessages({ program: ['Required'] })).toEqual(['Required'])
  })

  it('reads axios-style errors', () => {
    expect(getApiErrorMessage({ response: { data: { detail: 'Nope' } } }, 'x')).toBe('Nope')
  })
})
