import { computed, ref } from 'vue'
import api from '@/services/api'
import { unwrapPaginatedResults } from '@/utils/apiList'
import { flattenFieldMessages } from '@/utils/apiErrors'

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

export function useHostDestinations(form) {
  const hostInstitutions = ref([])
  const hostSchools = ref([])
  const hostAcademicPrograms = ref([])
  const hostInstitutionsLoading = ref(false)
  const hostSchoolsLoading = ref(false)
  const hostAcademicProgramsLoading = ref(false)
  const hostDestinationConfigured = computed(() => hostInstitutions.value.length > 0)

  async function fetchHostInstitutions(programId) {
    hostInstitutions.value = []
    hostSchools.value = []
    hostAcademicPrograms.value = []
    if (!programId) return
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
    if (!institutionId) return
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
    if (!schoolId) return
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
    return {
      host_institution: form.value.host_institution || null,
      host_school: form.value.host_school || null,
      host_academic_program: form.value.host_academic_program || null,
    }
  }

  return {
    hostInstitutions,
    hostSchools,
    hostAcademicPrograms,
    hostInstitutionsLoading,
    hostSchoolsLoading,
    hostAcademicProgramsLoading,
    hostDestinationConfigured,
    fetchHostInstitutions,
    fetchHostSchools,
    fetchHostAcademicPrograms,
    hostDestinationPayload,
  }
}
