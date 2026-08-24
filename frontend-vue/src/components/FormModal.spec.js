/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import FormModal from './FormModal.vue'
import i18n from '@/i18n'

describe('FormModal', () => {
  it('renders when open with title and emits close on cancel', async () => {
    const wrapper = mount(FormModal, {
      props: {
        open: true,
        title: 'Edit user',
      },
      global: { plugins: [i18n] },
    })
    expect(wrapper.get('[data-testid="form-modal"]').attributes('aria-modal')).toBe('true')
    expect(wrapper.text()).toContain('Edit user')
    await wrapper.get('[data-testid="form-modal-cancel"]').trigger('click')
    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('shows error alert and emits submit', async () => {
    const wrapper = mount(FormModal, {
      props: {
        open: true,
        title: 'Create',
        error: 'Validation failed',
      },
      global: { plugins: [i18n] },
    })
    expect(wrapper.get('[data-testid="form-modal-error"]').text()).toContain('Validation failed')
    await wrapper.get('[data-testid="form-modal-submit"]').trigger('click')
    expect(wrapper.emitted('submit')).toBeTruthy()
  })

  it('does not render when closed', () => {
    const wrapper = mount(FormModal, {
      props: { open: false, title: 'Hidden' },
      global: { plugins: [i18n] },
    })
    expect(wrapper.find('[data-testid="form-modal"]').exists()).toBe(false)
  })
})
