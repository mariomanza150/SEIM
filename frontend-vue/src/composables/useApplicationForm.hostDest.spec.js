/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { ref } from 'vue'
import { useHostDestinations } from './useApplicationForm'

vi.mock('@/services/api', () => ({
  default: { get: vi.fn() },
}))

const api = (await import('@/services/api')).default

describe('useHostDestinations free-text payload', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('includes free-text names when catalogs are empty', async () => {
    api.get.mockImplementation((url) => {
      if (url.includes('/host-institutions/') && !url.includes('/schools')) {
        return Promise.resolve({ data: [{ id: 'inst-1', name: 'U' }] })
      }
      if (url.includes('/schools/')) {
        return Promise.resolve({ data: [] })
      }
      return Promise.resolve({ data: [] })
    })

    const form = ref({
      host_institution: '',
      host_school: '',
      host_academic_program: '',
      host_school_name: '',
      host_academic_program_name: '',
    })
    const {
      fetchHostInstitutions,
      fetchHostSchools,
      hostSchoolNeedsFreeText,
      hostAcademicProgramNeedsFreeText,
      hostDestinationPayload,
    } = useHostDestinations(form)

    await fetchHostInstitutions('program-1')
    form.value.host_institution = 'inst-1'
    await fetchHostSchools('inst-1')

    expect(hostSchoolNeedsFreeText.value).toBe(true)
    expect(hostAcademicProgramNeedsFreeText.value).toBe(true)

    form.value.host_school_name = 'Faculty of Arts'
    form.value.host_academic_program_name = 'Fine Arts'
    expect(hostDestinationPayload()).toEqual({
      host_institution: 'inst-1',
      host_school: null,
      host_academic_program: null,
      host_school_name: 'Faculty of Arts',
      host_academic_program_name: 'Fine Arts',
    })
  })
})
