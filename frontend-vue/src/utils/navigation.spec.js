/**
 * @vitest-environment jsdom
 */
import { describe, it, expect } from 'vitest'
import { isNewTabUrl, isSpaUrl, normalizeSpaLocation } from './navigation'

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

  it('maps leftover root and SPA alias paths used in notifications', () => {
    expect(normalizeSpaLocation('/applications/123/')).toEqual({
      name: 'ApplicationDetail',
      params: { id: '123' },
    })
    expect(normalizeSpaLocation('/calendar')).toEqual({ name: 'DeadlinesCalendar' })
    expect(normalizeSpaLocation('/seim/admin/dynforms/7')).toEqual({
      name: 'AdminDynformEditor',
      params: { id: '7' },
    })
    expect(normalizeSpaLocation('/seim/admin/programs/prog-1/destinations')).toEqual({
      name: 'AdminProgramDestinations',
      params: { id: 'prog-1' },
    })
    expect(normalizeSpaLocation('/seim/admin/data-management')).toEqual({
      name: 'AdminDataManagement',
    })
    expect(normalizeSpaLocation('/seim/admin/documents')).toEqual({
      name: 'AdminDocuments',
    })
    expect(normalizeSpaLocation('/seim/admin/documents/9')).toEqual({
      name: 'AdminDocumentTypeEdit',
      params: { id: '9' },
    })
    expect(normalizeSpaLocation('/seim/admin')).toEqual({ name: 'AdminPrograms' })
    expect(normalizeSpaLocation('/analytics')).toEqual({ name: 'AnalyticsForecasts' })
    expect(isSpaUrl('/seim/review-queue')).toBe(true)
  })
})

describe('isNewTabUrl', () => {
  it('opens CMS and Django admin in a new tab, not SPA admin routes', () => {
    expect(isNewTabUrl('/cms/')).toBe(true)
    expect(isNewTabUrl('/seim/django-admin/')).toBe(true)
    expect(isNewTabUrl('/seim/admin/dynforms')).toBe(false)
    expect(isNewTabUrl('/seim/admin/data-management')).toBe(false)
  })
})
