/**
 * @vitest-environment jsdom
 */
import { describe, it, expect } from 'vitest'
import { normalizeSpaLocation } from './navigation'

describe('normalizeSpaLocation', () => {
  it('maps legacy agreement-documents list to exchange agreements', () => {
    expect(normalizeSpaLocation('/seim/agreement-documents')).toEqual({ name: 'StaffExchangeAgreements' })
    expect(normalizeSpaLocation('https://example.org/seim/agreement-documents')).toEqual({
      name: 'StaffExchangeAgreements',
    })
  })

  it('maps agreement repository deep link', () => {
    expect(normalizeSpaLocation('/seim/exchange-agreements/abc-uuid/documents')).toEqual({
      name: 'StaffAgreementDocuments',
      params: { agreementId: 'abc-uuid' },
    })
  })

  it('maps exchange agreements registry', () => {
    expect(normalizeSpaLocation('/seim/exchange-agreements')).toEqual({ name: 'StaffExchangeAgreements' })
  })
})
