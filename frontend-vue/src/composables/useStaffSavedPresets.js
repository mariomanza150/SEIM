import { ref } from 'vue'
import { useToast } from '@/composables/useToast'
import api from '@/services/api'

/**
 * Load/save/delete/set-default for `/api/saved-searches/` rows of a given `search_type`.
 */
export function useStaffSavedPresets(searchType) {
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
      success('Preset saved')
    } catch {
      errorToast('Could not save preset')
    } finally {
      presetsLoading.value = false
    }
  }

  async function deletePreset(p) {
    if (!window.confirm(`Remove preset "${p.name}"?`)) return
    try {
      presetsLoading.value = true
      await api.delete(`/api/saved-searches/${p.id}/`)
      await loadPresets()
      success('Preset removed')
    } catch {
      errorToast('Could not remove preset')
    } finally {
      presetsLoading.value = false
    }
  }

  async function setDefaultPreset(p) {
    try {
      presetsLoading.value = true
      await api.post(`/api/saved-searches/${p.id}/set_default/`)
      await loadPresets()
      success('Default preset updated')
    } catch {
      errorToast('Could not update default')
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
