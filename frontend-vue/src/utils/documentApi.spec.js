import { describe, expect, it } from 'vitest'
import {
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
})
