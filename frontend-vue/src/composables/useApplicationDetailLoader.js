import { ref, shallowRef } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { usePageState } from '@/composables/usePageState'
import { useToast } from '@/composables/useToast'
import api from '@/services/api'

/**
 * Loads the primary application record for ApplicationDetail.
 * Secondary resources (timeline, documents, comments) stay in the view.
 *
 * @param {(() => string|number|null|undefined)|null} [resolveId] Optional id override (embedded mode).
 */
export function useApplicationDetailLoader(resolveId = null) {
  const route = useRoute()
  const { t } = useI18n()
  const { error: errorToast } = useToast()
  const application = shallowRef(null)

  function currentId() {
    if (typeof resolveId === 'function') {
      const override = resolveId()
      if (override != null && override !== '') return override
    }
    return route.params.id
  }

  const { loading, error, run } = usePageState(
    async () => {
      const id = currentId()
      const response = await api.get(`/api/applications/${id}/`)
      application.value = response.data
      return response.data
    },
    {
      errorFallback: t('applicationDetailPage.loadError'),
      onError: () => {
        errorToast(t('applicationDetailPage.loadToastError'))
      },
    },
  )

  async function loadApplication() {
    return run()
  }

  async function softReload() {
    try {
      const id = currentId()
      const response = await api.get(`/api/applications/${id}/`)
      application.value = response.data
      return response.data
    } catch (err) {
      console.warn('Live sync refresh failed:', err)
      return null
    }
  }

  return {
    application,
    loading,
    error,
    loadApplication,
    softReload,
    currentId,
  }
}
