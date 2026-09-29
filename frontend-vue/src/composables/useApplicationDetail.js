import { computed } from 'vue'
import {
  applicationHostCountry,
  applicationHostInstitution,
  applicationProgramDisplayName,
  applicationProgramDuration,
} from '@/utils/formatters'

export function useApplicationDisplay(application, locale) {
  function programDisplayName(app) {
    return applicationProgramDisplayName(app)
  }

  function hostInstitution(app) {
    return applicationHostInstitution(app)
  }

  function hostCountry(app) {
    return applicationHostCountry(app)
  }

  function programDuration(app) {
    return applicationProgramDuration({
      app,
      locale: locale.value,
      fallback: '',
    })
  }

  const submitBlockedByDocuments = computed(() => {
    const c = application.value?.document_checklist
    if (!c?.required_count) return false
    return !c.complete
  })

  const submitBlockedByHost = computed(() => {
    const host = application.value?.readiness?.host_destination
    if (!host?.required) return false
    return !host.complete
  })

  const submitBlockedByEligibility = computed(() => {
    const el = application.value?.readiness?.eligibility
    if (!el) return false
    return el.complete === false
  })

  const submitBlocked = computed(
    () =>
      submitBlockedByDocuments.value
      || submitBlockedByHost.value
      || submitBlockedByEligibility.value,
  )

  return {
    programDisplayName,
    hostInstitution,
    hostCountry,
    programDuration,
    submitBlockedByDocuments,
    submitBlockedByHost,
    submitBlockedByEligibility,
    submitBlocked,
  }
}
