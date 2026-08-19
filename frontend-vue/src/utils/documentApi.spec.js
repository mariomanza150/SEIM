import { describe, expect, it } from 'vitest'
import {
  applicationSelectLabel,
  documentApplicationId,
  documentApplicationProgramName,
  documentReviewStatus,
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

  it('documentTypeLabel prefers description when name is a slug', () => {
    expect(
      documentTypeLabel(
        { id: 1, name: 'transcript', slug: 'transcript', description: 'Academic transcript' },
        '',
      ),
    ).toBe('Academic transcript')
    expect(
      documentTypeLabel({ id: 2, name: 'Kardex Oficial', description: 'Kardex / historial académico oficial.' }, ''),
    ).toBe('Kardex Oficial')
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

  it('documentReviewStatus treats unreviewed uploads as pending, not invalid', () => {
    expect(documentReviewStatus({ is_valid: false, validated_at: null })).toBe('pending')
    expect(documentReviewStatus({ is_valid: false })).toBe('pending')
    expect(documentReviewStatus({ is_valid: false, validated_at: '' })).toBe('pending')
    expect(documentReviewStatus({ is_valid: false, validated_at: '2026-08-17T12:00:00Z' })).toBe(
      'invalid',
    )
    expect(documentReviewStatus({ is_valid: true, validated_at: null })).toBe('valid')
    expect(documentReviewStatus({ is_valid: true, validated_at: '2026-08-17T12:00:00Z' })).toBe(
      'valid',
    )
    expect(documentReviewStatus(null)).toBe('pending')
  })

  it('applicationSelectLabel prefers program_name then nested program name', () => {
    expect(applicationSelectLabel({ id: 'i', program_name: 'From API' })).toBe('From API')
    expect(applicationSelectLabel({ id: 'i', program: { name: 'Nested' } })).toBe('Nested')
    expect(applicationSelectLabel({ id: '550e8400-e29b-41d4-a716-446655440000' })).toBe(
      '550e8400-e29b-41d4-a716-446655440000',
    )
  })

  it('applicationSelectLabel appends status so duplicate program names stay distinct', () => {
    expect(
      applicationSelectLabel({
        id: 'a',
        program_name: 'Vue E2E Test Program',
        status: 'draft',
      }),
    ).toBe('Vue E2E Test Program (draft)')
    expect(
      applicationSelectLabel({
        id: 'b',
        program_name: 'Vue E2E Test Program',
        status: { name: 'under_review' },
      }),
    ).toBe('Vue E2E Test Program (under review)')
  })

  it('applicationSelectLabel uses formatStatus callback when provided', () => {
    const formatStatus = (s) =>
      String(s).replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
    expect(
      applicationSelectLabel(
        { id: 'a', program_name: 'DAAD', status: 'nominated' },
        '',
        null,
        formatStatus,
      ),
    ).toBe('DAAD (Nominated)')
    expect(
      applicationSelectLabel(
        { id: 'b', program_name: 'Vue E2E Test Program', status: 'under_review' },
        '',
        null,
        formatStatus,
      ),
    ).toBe('Vue E2E Test Program (Under Review)')
  })

  it('applicationSelectLabel suffixes short ids when the same program+status appears twice', () => {
    const siblings = [
      { id: 'c48638a4-2124-4d43-aceb-dadc54796b4b', program_name: 'Vue E2E Test Program', status: 'draft' },
      { id: '46991ada-6d7a-49f9-8158-fd44b3b63537', program_name: 'Vue E2E Test Program', status: 'draft' },
      { id: 'unique-1', program_name: 'Tokyo', status: 'draft' },
    ]
    expect(applicationSelectLabel(siblings[0], '', siblings)).toBe(
      'Vue E2E Test Program (draft) · c48638a4',
    )
    expect(applicationSelectLabel(siblings[1], '', siblings)).toBe(
      'Vue E2E Test Program (draft) · 46991ada',
    )
    expect(applicationSelectLabel(siblings[2], '', siblings)).toBe('Tokyo (draft)')
  })
})
