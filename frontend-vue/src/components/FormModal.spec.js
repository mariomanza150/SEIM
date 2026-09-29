/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import FormModal from './FormModal.vue'
import i18n from '@/i18n'

describe('FormModal', () => {
  let wrapper

  afterEach(() => {
    wrapper?.unmount()
    wrapper = undefined
  })

  it('renders when open with title and emits close on cancel', async () => {
    wrapper = mount(FormModal, {
      props: {
        open: true,
        title: 'Edit user',
      },
      global: { plugins: [i18n] },
      attachTo: document.body,
    })
    const modal = document.querySelector('[data-testid="form-modal"]')
    expect(modal).toBeTruthy()
    expect(modal.getAttribute('aria-modal')).toBe('true')
    expect(modal.textContent).toContain('Edit user')
    document.querySelector('[data-testid="form-modal-cancel"]').click()
    await wrapper.vm.$nextTick()
    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('shows error alert and emits submit', async () => {
    wrapper = mount(FormModal, {
      props: {
        open: true,
        title: 'Create',
        error: 'Validation failed',
      },
      global: { plugins: [i18n] },
      attachTo: document.body,
    })
    expect(document.querySelector('[data-testid="form-modal-error"]').textContent).toContain(
      'Validation failed',
    )
    document.querySelector('[data-testid="form-modal-submit"]').click()
    await wrapper.vm.$nextTick()
    expect(wrapper.emitted('submit')).toBeTruthy()
  })

  it('does not render when closed', () => {
    wrapper = mount(FormModal, {
      props: { open: false, title: 'Hidden' },
      global: { plugins: [i18n] },
      attachTo: document.body,
    })
    expect(document.querySelector('[data-testid="form-modal"]')).toBeNull()
  })
})
