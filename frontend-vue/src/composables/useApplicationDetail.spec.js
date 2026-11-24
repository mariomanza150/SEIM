/**
 * @vitest-environment jsdom
 */
import { describe, it, expect } from 'vitest'
import { ref } from 'vue'
import { useApplicationDisplay } from './useApplicationDetail'

describe('useApplicationDisplay', () => {
  const locale = ref('en')

  it('reads program and host fields from nested or flat application shapes', () => {
    const application = ref({
      program_name: 'Exchange Semester',
      host_institution_name: 'Host Campus North',
      host_institution_country: 'Exampleland',
      program_start_date: '2026-09-01',
      program_end_date: '2026-12-15',
    })
    const display = useApplicationDisplay(application, locale)
    expect(display.programDisplayName(application.value)).toBe('Exchange Semester')
    expect(display.hostInstitution(application.value)).toBe('Host Campus North')
    expect(display.hostCountry(application.value)).toBe('Exampleland')
    expect(display.programDuration(application.value)).toContain('2026')
  })

  it('falls back to nested program object fields', () => {
    const application = ref({
      program: {
        name: 'Winter Mobility',
        institution: 'Partner Campus West',
        country: 'Northland',
        duration: '4 months',
      },
    })
    const display = useApplicationDisplay(application, locale)
    expect(display.programDisplayName(application.value)).toBe('Winter Mobility')
    expect(display.hostInstitution(application.value)).toBe('Partner Campus West')
    expect(display.hostCountry(application.value)).toBe('Northland')
    expect(display.programDuration(application.value)).toBe('4 months')
  })

  it('blocks submit when required documents are incomplete', () => {
    const application = ref({
      document_checklist: { required_count: 2, complete: false },
      readiness: {
        host_destination: { required: false, complete: true },
        eligibility: { complete: true },
      },
    })
    const display = useApplicationDisplay(application, locale)
    expect(display.submitBlockedByDocuments.value).toBe(true)
    expect(display.submitBlocked.value).toBe(true)
  })

  it('blocks submit when host destination readiness is incomplete', () => {
    const application = ref({
      document_checklist: { required_count: 0, complete: true },
      readiness: {
        host_destination: { required: true, complete: false },
        eligibility: { complete: true },
      },
    })
    const display = useApplicationDisplay(application, locale)
    expect(display.submitBlockedByHost.value).toBe(true)
    expect(display.submitBlocked.value).toBe(true)
  })

  it('blocks submit when eligibility readiness is incomplete', () => {
    const application = ref({
      document_checklist: { required_count: 1, complete: true },
      readiness: {
        host_destination: { required: true, complete: true },
        eligibility: { complete: false },
      },
    })
    const display = useApplicationDisplay(application, locale)
    expect(display.submitBlockedByEligibility.value).toBe(true)
    expect(display.submitBlocked.value).toBe(true)
  })

  it('does not block submit when readiness gates are clear', () => {
    const application = ref({
      document_checklist: { required_count: 1, complete: true },
      readiness: {
        host_destination: { required: true, complete: true },
        eligibility: { complete: true },
      },
    })
    const display = useApplicationDisplay(application, locale)
    expect(display.submitBlockedByDocuments.value).toBe(false)
    expect(display.submitBlockedByHost.value).toBe(false)
    expect(display.submitBlockedByEligibility.value).toBe(false)
    expect(display.submitBlocked.value).toBe(false)
  })
})
