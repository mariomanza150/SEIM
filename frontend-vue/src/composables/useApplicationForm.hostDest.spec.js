/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { ref } from 'vue'
import { HOST_DEST_NOT_LISTED, useHostDestinations } from './useApplicationForm'

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
      host_institution_text: '',
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

  it('stores free-text fields in free_text mode', () => {
    const form = ref({
      host_institution: '',
      host_school: '',
      host_academic_program: '',
      host_institution_text: 'Typed U',
      host_school_name: 'Typed School',
      host_academic_program_name: 'Typed Program',
    })
    const program = ref({
      host_destination_mode: 'free_text',
      host_destination_required: true,
    })
    const { hostDestinationPayload, hostInstitutionUsesFreeText, hostDestinationRequired } = useHostDestinations(
      form,
      program,
    )
    expect(hostInstitutionUsesFreeText.value).toBe(true)
    expect(hostDestinationRequired.value).toBe(true)
    expect(hostDestinationPayload()).toEqual({
      host_institution: null,
      host_school: null,
      host_academic_program: null,
      host_institution_text: 'Typed U',
      host_school_text: 'Typed School',
      host_academic_program_text: 'Typed Program',
    })
  })

  it('uses not-listed option in either mode', () => {
    const form = ref({
      host_institution: HOST_DEST_NOT_LISTED,
      host_school: '',
      host_academic_program: '',
      host_institution_text: 'Other U',
      host_school_name: 'Other School',
      host_academic_program_name: 'Other Program',
    })
    const program = ref({
      host_destination_mode: 'either',
      host_destination_required: false,
    })
    const {
      hostDestinationPayload,
      hostInstitutionNotListed,
      hostDestinationRequired,
      hostSchoolNeedsFreeText,
    } = useHostDestinations(form, program)
    expect(hostDestinationRequired.value).toBe(false)
    expect(hostInstitutionNotListed.value).toBe(true)
    expect(hostSchoolNeedsFreeText.value).toBe(true)
    expect(hostDestinationPayload()).toEqual({
      host_institution: null,
      host_school: null,
      host_academic_program: null,
      host_institution_text: 'Other U',
      host_school_text: 'Other School',
      host_academic_program_text: 'Other Program',
    })
  })
})
