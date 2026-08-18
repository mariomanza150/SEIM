/**
 * @vitest-environment jsdom
 */
import { describe, it, expect } from 'vitest'
import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { useNavDropdown } from './useNavDropdown'

function mountDropdown() {
  return mount(
    defineComponent({
      setup() {
        return useNavDropdown()
      },
      template: `
        <div ref="rootEl">
          <button type="button" data-testid="toggle" @click="toggle">Open</button>
          <div v-if="open" data-testid="menu">Menu</div>
        </div>
      `,
    }),
    { attachTo: document.body },
  )
}

describe('useNavDropdown', () => {
  it('opens and closes from the toggle', async () => {
    const wrapper = mountDropdown()
    expect(wrapper.find('[data-testid="menu"]').exists()).toBe(false)

    await wrapper.get('[data-testid="toggle"]').trigger('click')
    expect(wrapper.find('[data-testid="menu"]').exists()).toBe(true)

    await wrapper.get('[data-testid="toggle"]').trigger('click')
    expect(wrapper.find('[data-testid="menu"]').exists()).toBe(false)
    wrapper.unmount()
  })

  it('closes on outside click and Escape', async () => {
    const wrapper = mountDropdown()
    await wrapper.get('[data-testid="toggle"]').trigger('click')
    expect(wrapper.find('[data-testid="menu"]').exists()).toBe(true)

    document.body.dispatchEvent(new MouseEvent('click', { bubbles: true }))
    await wrapper.vm.$nextTick()
    expect(wrapper.find('[data-testid="menu"]').exists()).toBe(false)

    await wrapper.get('[data-testid="toggle"]').trigger('click')
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }))
    await wrapper.vm.$nextTick()
    expect(wrapper.find('[data-testid="menu"]').exists()).toBe(false)
    wrapper.unmount()
  })

  it('closes the previously open dropdown when another opens', async () => {
    const a = mountDropdown()
    const b = mountDropdown()

    await a.get('[data-testid="toggle"]').trigger('click')
    expect(a.find('[data-testid="menu"]').exists()).toBe(true)

    await b.get('[data-testid="toggle"]').trigger('click')
    await a.vm.$nextTick()
    expect(a.find('[data-testid="menu"]').exists()).toBe(false)
    expect(b.find('[data-testid="menu"]').exists()).toBe(true)

    a.unmount()
    b.unmount()
  })
})
