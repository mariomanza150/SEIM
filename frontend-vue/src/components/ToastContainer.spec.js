/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import ToastContainer from './ToastContainer.vue'
import { useToast } from '@/composables/useToast'
import i18n, { setAppLocale } from '@/i18n'

describe('ToastContainer', () => {
  beforeEach(() => {
    useToast().toasts.value = []
    localStorage.clear()
    setAppLocale('en')
  })

  afterEach(() => {
    useToast().toasts.value = []
    setAppLocale('en')
    localStorage.clear()
  })

  it('renders translated type label for success toasts', () => {
    useToast().showToast('Saved.', 'success', 0)
    const wrapper = mount(ToastContainer, {
      global: { plugins: [i18n] },
    })
    expect(wrapper.text()).toContain('Success')
    expect(wrapper.text()).toContain('Saved.')
  })

  it('uses Spanish labels when locale is es', () => {
    setAppLocale('es')
    useToast().showToast('Listo', 'success', 0)
    const wrapper = mount(ToastContainer, {
      global: { plugins: [i18n] },
    })
    expect(wrapper.text()).toContain('Correcto')
    expect(wrapper.text()).toContain('Listo')
  })
})
