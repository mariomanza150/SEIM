import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useToast } from '@/composables/useToast'
import api from '@/services/api'

/**
 * Load/save/delete/set-default for `/api/saved-searches/` rows of a given `search_type`.
 */
export function useStaffSavedPresets(searchType) {
  const { t } = useI18n()
  const savedPresets = ref([])
  const presetsLoading = ref(false)
  const newPresetName = ref('')
  const saveAsDefault = ref(false)
  const { success, error: errorToast } = useToast()

  async function loadPresets() {
    try {
      presetsLoading.value = true
      const { data } = await api.get('/api/saved-searches/', {
        params: { search_type: searchType, ordering: 'name', page_size: 100 },
      })
      savedPresets.value = data.results ?? data ?? []
    } catch {
      savedPresets.value = []
    } finally {
      presetsLoading.value = false
    }
  }

  async function savePreset(serializeFilters) {
    const name = newPresetName.value.trim()
    if (!name) return
    try {
      presetsLoading.value = true
      await api.post('/api/saved-searches/', {
        name,
        search_type: searchType,
        filters: serializeFilters(),
        is_default: saveAsDefault.value,
      })
      newPresetName.value = ''
      saveAsDefault.value = false
      await loadPresets()
      success(t('savedPresets.toastSaved'))
    } catch {
      errorToast(t('savedPresets.toastSaveError'))
    } finally {
      presetsLoading.value = false
    }
  }

  async function deletePreset(p) {
    if (!window.confirm(t('savedPresets.confirmRemove', { name: p.name }))) return
    try {
      presetsLoading.value = true
      await api.delete(`/api/saved-searches/${p.id}/`)
      await loadPresets()
      success(t('savedPresets.toastRemoved'))
    } catch {
      errorToast(t('savedPresets.toastRemoveError'))
    } finally {
      presetsLoading.value = false
    }
  }

  async function setDefaultPreset(p) {
    try {
      presetsLoading.value = true
      await api.post(`/api/saved-searches/${p.id}/set_default/`)
      await loadPresets()
      success(t('savedPresets.toastDefaultUpdated'))
    } catch {
      errorToast(t('savedPresets.toastDefaultError'))
    } finally {
      presetsLoading.value = false
    }
  }

  return {
    savedPresets,
    presetsLoading,
    newPresetName,
    saveAsDefault,
    loadPresets,
    savePreset,
    deletePreset,
    setDefaultPreset,
  }
}
