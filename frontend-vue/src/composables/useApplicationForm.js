import { computed, ref } from 'vue'
import api from '@/services/api'
import { unwrapPaginatedResults } from '@/utils/apiList'
import { flattenFieldMessages } from '@/utils/apiErrors'

export const HOST_DEST_NOT_LISTED = '__not_listed__'

export function catalogId(value) {
  if (value && typeof value === 'object') return value.id ?? ''
  return value ?? ''
}

export function isIncompleteProfileError(data) {
  const code = data?.code || data?.error_code || data?.detail?.code
  if (['profile_incomplete', 'incomplete_profile', 'profile_not_ready'].includes(code)) return true
  const message = flattenFieldMessages(data).join(' ').toLowerCase()
  return message.includes('profile') && (
    message.includes('incomplete') ||
    message.includes('complete your') ||
    message.includes('not ready')
  )
}

export function applyServerValidationErrors(raw, errors, dynamicFormErrors) {
  if (raw === undefined || raw === null) return false
  errors.value = typeof raw === 'string' ? { program: [raw] } : { ...raw }
  const df = typeof raw === 'object' && raw !== null ? raw.dynamic_form : undefined
  dynamicFormErrors.value = Array.isArray(df) ? df : (df ? [df] : [])
  return true
}

/**
 * Host destination cascade helpers.
 * @param {import('vue').Ref} form
 * @param {import('vue').Ref|import('vue').ComputedRef} [programRef] selected program row
 */
export function useHostDestinations(form, programRef = null) {
  const hostInstitutions = ref([])
  const hostSchools = ref([])
  const hostAcademicPrograms = ref([])
  const hostInstitutionsLoading = ref(false)
  const hostSchoolsLoading = ref(false)
  const hostAcademicProgramsLoading = ref(false)

  const hostDestinationMode = computed(() => {
    const mode = programRef?.value?.host_destination_mode
    if (mode === 'free_text' || mode === 'either' || mode === 'catalog') return mode
    return 'catalog'
  })

  const hostDestinationRequired = computed(() => {
    const program = programRef?.value
    if (program && Object.prototype.hasOwnProperty.call(program, 'host_destination_required')) {
      return Boolean(program.host_destination_required)
    }
    return true
  })

  const hostDestinationConfigured = computed(() => {
    if (hostDestinationMode.value === 'free_text') return true
    if (hostDestinationMode.value === 'either') return true
    return hostInstitutions.value.length > 0
  })

  const hostInstitutionUsesFreeText = computed(() => hostDestinationMode.value === 'free_text')

  const hostInstitutionNotListed = computed(
    () => hostDestinationMode.value === 'either'
      && form.value.host_institution === HOST_DEST_NOT_LISTED,
  )

  const hostSchoolNeedsFreeText = computed(() => {
    if (hostDestinationMode.value === 'free_text') return true
    if (hostDestinationMode.value === 'either') {
      if (hostInstitutionNotListed.value) return true
      return form.value.host_school === HOST_DEST_NOT_LISTED
    }
    // catalog: free-text when institution chosen and school catalog empty
    return Boolean(form.value.host_institution)
      && !hostSchoolsLoading.value
      && hostSchools.value.length === 0
  })

  const hostAcademicProgramNeedsFreeText = computed(() => {
    if (hostDestinationMode.value === 'free_text') return true
    if (hostDestinationMode.value === 'either') {
      if (hostSchoolNeedsFreeText.value) return true
      return form.value.host_academic_program === HOST_DEST_NOT_LISTED
    }
    if (hostSchoolNeedsFreeText.value) return true
    if (!form.value.host_school) return false
    return !hostAcademicProgramsLoading.value && hostAcademicPrograms.value.length === 0
  })

  async function fetchHostInstitutions(programId) {
    hostInstitutions.value = []
    hostSchools.value = []
    hostAcademicPrograms.value = []
    if (!programId) return
    if (hostDestinationMode.value === 'free_text') return
    hostInstitutionsLoading.value = true
    try {
      const { data } = await api.get(`/api/programs/${programId}/host-institutions/`)
      hostInstitutions.value = unwrapPaginatedResults(data)
    } catch (err) {
      console.error('Failed to load host institutions:', err)
      hostInstitutions.value = []
    } finally {
      hostInstitutionsLoading.value = false
    }
  }

  async function fetchHostSchools(institutionId) {
    hostSchools.value = []
    hostAcademicPrograms.value = []
    if (!institutionId || institutionId === HOST_DEST_NOT_LISTED) return
    if (hostDestinationMode.value === 'free_text') return
    hostSchoolsLoading.value = true
    try {
      const { data } = await api.get(`/api/host-institutions/${institutionId}/schools/`)
      hostSchools.value = unwrapPaginatedResults(data)
    } catch (err) {
      console.error('Failed to load host schools:', err)
      hostSchools.value = []
    } finally {
      hostSchoolsLoading.value = false
    }
  }

  async function fetchHostAcademicPrograms(schoolId) {
    hostAcademicPrograms.value = []
    if (!schoolId || schoolId === HOST_DEST_NOT_LISTED) return
    if (hostDestinationMode.value === 'free_text') return
    hostAcademicProgramsLoading.value = true
    try {
      const { data } = await api.get(`/api/schools/${schoolId}/academic-programs/`)
      hostAcademicPrograms.value = unwrapPaginatedResults(data)
    } catch (err) {
      console.error('Failed to load host academic programs:', err)
      hostAcademicPrograms.value = []
    } finally {
      hostAcademicProgramsLoading.value = false
    }
  }

  function hostDestinationPayload() {
    const mode = hostDestinationMode.value
    const institutionIsFree = hostInstitutionUsesFreeText.value || hostInstitutionNotListed.value
    const schoolIsFree = hostSchoolNeedsFreeText.value
    const academicIsFree = hostAcademicProgramNeedsFreeText.value

    const payload = {
      host_institution: institutionIsFree
        ? null
        : (form.value.host_institution && form.value.host_institution !== HOST_DEST_NOT_LISTED
          ? form.value.host_institution
          : null),
      host_school: schoolIsFree
        ? null
        : (form.value.host_school && form.value.host_school !== HOST_DEST_NOT_LISTED
          ? form.value.host_school
          : null),
      host_academic_program: academicIsFree
        ? null
        : (form.value.host_academic_program && form.value.host_academic_program !== HOST_DEST_NOT_LISTED
          ? form.value.host_academic_program
          : null),
    }

    if (mode === 'free_text' || mode === 'either') {
      if (institutionIsFree) {
        payload.host_institution_text = String(form.value.host_institution_text || '').trim()
      } else {
        payload.host_institution_text = ''
      }
      if (schoolIsFree) {
        payload.host_school_text = String(
          form.value.host_school_text || form.value.host_school_name || '',
        ).trim()
      } else {
        payload.host_school_text = ''
      }
      if (academicIsFree) {
        payload.host_academic_program_text = String(
          form.value.host_academic_program_text || form.value.host_academic_program_name || '',
        ).trim()
      } else {
        payload.host_academic_program_text = ''
      }
    } else {
      // catalog mode: legacy free-text when child catalogs are empty
      if (schoolIsFree) {
        payload.host_school_name = String(form.value.host_school_name || '').trim()
      }
      if (academicIsFree) {
        payload.host_academic_program_name = String(
          form.value.host_academic_program_name || '',
        ).trim()
      }
    }
    return payload
  }

  return {
    hostInstitutions,
    hostSchools,
    hostAcademicPrograms,
    hostInstitutionsLoading,
    hostSchoolsLoading,
    hostAcademicProgramsLoading,
    hostDestinationConfigured,
    hostDestinationMode,
    hostDestinationRequired,
    hostInstitutionUsesFreeText,
    hostInstitutionNotListed,
    hostSchoolNeedsFreeText,
    hostAcademicProgramNeedsFreeText,
    fetchHostInstitutions,
    fetchHostSchools,
    fetchHostAcademicPrograms,
    hostDestinationPayload,
  }
}
