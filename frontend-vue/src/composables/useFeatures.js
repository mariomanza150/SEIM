import { computed, ref, readonly } from 'vue'

import api from '@/services/api'

const features = ref(null)
const loading = ref(false)
const error = ref('')
let fetchPromise = null

const FALLBACK = {
  scholarships_enabled: true,
  document_version_history_enabled: true,
  document_version_history_student: false,
  document_version_history_coordinator: true,
  document_version_history_admin: true,
}

function normalizeFeatures(data) {
  return {
    scholarships_enabled:
      data?.scholarships_enabled === undefined
        ? FALLBACK.scholarships_enabled
        : Boolean(data.scholarships_enabled),
    document_version_history_enabled:
      data?.document_version_history_enabled === undefined
        ? FALLBACK.document_version_history_enabled
        : Boolean(data.document_version_history_enabled),
    document_version_history_student:
      data?.document_version_history_student === undefined
        ? FALLBACK.document_version_history_student
        : Boolean(data.document_version_history_student),
    document_version_history_coordinator:
      data?.document_version_history_coordinator === undefined
        ? FALLBACK.document_version_history_coordinator
        : Boolean(data.document_version_history_coordinator),
    document_version_history_admin:
      data?.document_version_history_admin === undefined
        ? FALLBACK.document_version_history_admin
        : Boolean(data.document_version_history_admin),
    updated_at: data?.updated_at || null,
  }
}

export function scholarshipsEnabledFromState(state) {
  if (!state) return FALLBACK.scholarships_enabled
  return state.scholarships_enabled !== false
}

export function useFeatures() {
  const scholarshipsEnabled = computed(() => scholarshipsEnabledFromState(features.value))

  const documentVersionHistoryEnabled = computed(
    () => features.value?.document_version_history_enabled !== false,
  )

  async function loadFeatures(force = false) {
    if (features.value && !force) return features.value
    if (fetchPromise && !force) return fetchPromise

    loading.value = true
    error.value = ''

    fetchPromise = api
      .get('/api/features/')
      .then(({ data }) => {
        features.value = normalizeFeatures(data)
        return features.value
      })
      .catch((err) => {
        error.value = err?.message || 'Failed to load features'
        // Fail open: keep scholarship surfaces visible if the flag API is unreachable.
        features.value = { ...FALLBACK }
        return features.value
      })
      .finally(() => {
        loading.value = false
        fetchPromise = null
      })

    return fetchPromise
  }

  async function updateFeatures(payload) {
    const { data } = await api.patch('/api/features/', payload)
    features.value = normalizeFeatures(data)
    return features.value
  }

  /** Reset module state (tests). */
  function _resetFeaturesState() {
    features.value = null
    loading.value = false
    error.value = ''
    fetchPromise = null
  }

  return {
    features: readonly(features),
    loading: readonly(loading),
    error: readonly(error),
    scholarshipsEnabled,
    documentVersionHistoryEnabled,
    loadFeatures,
    updateFeatures,
    _resetFeaturesState,
  }
}
