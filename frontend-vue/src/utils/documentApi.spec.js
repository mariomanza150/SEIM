import { describe, expect, it } from 'vitest'
import {
  applicationSelectLabel,
  documentApplicationId,
  documentApplicationProgramName,
  documentTypeLabel,
} from './documentApi'

describe('documentApi', () => {
  it('documentApplicationId handles UUID string and nested object', () => {
    expect(documentApplicationId('abc-123')).toBe('abc-123')
    expect(documentApplicationId({ id: 'x-1', program_name: 'P' })).toBe('x-1')
    expect(documentApplicationId(null)).toBe('')
  })

  it('documentApplicationProgramName prefers API program_name', () => {
    expect(
      documentApplicationProgramName({ id: 'a', program_name: 'Exchange A' }, [], ''),
    ).toBe('Exchange A')
    expect(
      documentApplicationProgramName('app-1', [{ id: 'app-1', program: { name: 'Via list' } }], ''),
    ).toBe('Via list')
    expect(documentApplicationProgramName('app-1', [], 'Unknown')).toBe('Unknown')
  })

  it('documentTypeLabel prefers nested name', () => {
    expect(documentTypeLabel({ id: 2, name: 'Passport' }, '')).toBe('Passport')
    expect(documentTypeLabel(2, 'N/A')).toBe('2')
    expect(documentTypeLabel(null, 'N/A')).toBe('N/A')
  })

  it('coerces stringified JSON application and type (MQ-012)', () => {
    const appRaw = JSON.stringify({ id: 'app-1', program_name: 'Exchange A' })
    expect(documentApplicationProgramName(appRaw, [], '')).toBe('Exchange A')
    expect(documentApplicationId(appRaw)).toBe('app-1')
    const typeRaw = JSON.stringify({ id: 3, name: 'Transcript' })
    expect(documentTypeLabel(typeRaw, '')).toBe('Transcript')
  })

  it('unwraps double-encoded JSON strings for application and type', () => {
    const once = JSON.stringify({ id: 'app-2', program_name: 'Double' })
    const twice = JSON.stringify(once)
    expect(documentApplicationProgramName(twice, [], '')).toBe('Double')
    expect(documentApplicationId(twice)).toBe('app-2')
    const typeOnce = JSON.stringify({ id: 9, name: 'Passport' })
    const typeTwice = JSON.stringify(typeOnce)
    expect(documentTypeLabel(typeTwice, '')).toBe('Passport')
  })

  it('extracts application fields from malformed JSON-like strings', () => {
    const broken = '{broken,"id":"app-z","program_name":"Loose \\"Name\\""}'
    expect(documentApplicationId(broken)).toBe('app-z')
    expect(documentApplicationProgramName(broken, [], 'Unknown')).toBe('Loose "Name"')
  })

  it('applicationSelectLabel prefers program_name then nested program name', () => {
    expect(applicationSelectLabel({ id: 'i', program_name: 'From API' })).toBe('From API')
    expect(applicationSelectLabel({ id: 'i', program: { name: 'Nested' } })).toBe('Nested')
    expect(applicationSelectLabel({ id: '550e8400-e29b-41d4-a716-446655440000' })).toBe(
      '550e8400-e29b-41d4-a716-446655440000',
    )
  })
})
