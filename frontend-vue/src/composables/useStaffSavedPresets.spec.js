/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { defineComponent } from 'vue'
import { mount, flushPromises } from '@vue/test-utils'
import { useStaffSavedPresets } from './useStaffSavedPresets'
import api from '@/services/api'
import i18n, { setAppLocale } from '@/i18n'

const { mockSuccess, mockErrorToast } = vi.hoisted(() => ({
  mockSuccess: vi.fn(),
  mockErrorToast: vi.fn(),
}))

const { mockConfirm } = vi.hoisted(() => ({
  mockConfirm: vi.fn(),
}))

vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: mockSuccess, error: mockErrorToast }),
}))

vi.mock('@/composables/useConfirm', () => ({
  useConfirm: () => ({ confirm: mockConfirm }),
}))

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn(),
  },
}))

function mountComposable(searchType = 'program') {
  let apiExpose
  const Comp = defineComponent({
    setup() {
      apiExpose = useStaffSavedPresets(searchType)
      return () => null
    },
  })
  mount(Comp, { global: { plugins: [i18n] } })
  return apiExpose
}

describe('useStaffSavedPresets', () => {
  beforeEach(() => {
    localStorage.clear()
    setAppLocale('en')
    vi.clearAllMocks()
    mockConfirm.mockResolvedValue(true)
    api.get.mockResolvedValue({ data: { results: [] } })
  })

  afterEach(() => {
    setAppLocale('en')
    localStorage.clear()
  })

  it('calls success with translated message after savePreset', async () => {
    api.post.mockResolvedValue({ data: {} })
    const p = mountComposable('document')
    p.newPresetName.value = 'Filters A'
    await p.savePreset(() => ({ q: 1 }))
    await flushPromises()
    expect(api.post).toHaveBeenCalled()
    expect(mockSuccess).toHaveBeenCalledWith('Preset saved')
  })

  it('confirmRemove uses preset name from locale', async () => {
    mockConfirm.mockResolvedValue(false)
    const p = mountComposable()
    await p.deletePreset({ id: '1', name: 'My preset' })
    expect(mockConfirm).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'Remove preset',
        message: 'Remove preset "My preset"?',
        confirmText: 'Remove',
        cancelText: 'Cancel',
      }),
    )
    expect(api.delete).not.toHaveBeenCalled()
  })

  it('calls success with translated message after setDefaultPreset', async () => {
    api.post.mockResolvedValue({ data: {} })
    const p = mountComposable()
    await p.setDefaultPreset({ id: '9', name: 'x' })
    await flushPromises()
    expect(mockSuccess).toHaveBeenCalledWith('Default preset updated')
  })
})
