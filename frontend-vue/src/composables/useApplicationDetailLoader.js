import { ref, shallowRef } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { usePageState } from '@/composables/usePageState'
import { useToast } from '@/composables/useToast'
import api from '@/services/api'

/**
 * Loads the primary application record for ApplicationDetail.
 * Secondary resources (timeline, documents, comments) stay in the view.
 */
export function useApplicationDetailLoader() {
  const route = useRoute()
  const { t } = useI18n()
  const { error: errorToast } = useToast()
  const application = shallowRef(null)

  const { loading, error, run } = usePageState(
    async () => {
      const response = await api.get(`/api/applications/${route.params.id}/`)
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
      const response = await api.get(`/api/applications/${route.params.id}/`)
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
  }
}
