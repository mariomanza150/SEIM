import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ResponsiveList from '@/components/ResponsiveList.vue'

describe('ResponsiveList', () => {
  const items = [
    { id: '1', name: 'Alpha', status: 'active' },
    { id: '2', name: 'Beta', status: 'draft' },
  ]

  it('renders desktop table slot', () => {
    const wrapper = mount(ResponsiveList, {
      props: { items, columns: [{ key: 'name', label: 'Name' }] },
      slots: {
        default: '<table data-testid="desktop-table"><tbody><tr><td>Row</td></tr></tbody></table>',
      },
    })
    expect(wrapper.find('[data-testid="desktop-table"]').exists()).toBe(true)
  })

  it('renders mobile cards from columns', () => {
    const wrapper = mount(ResponsiveList, {
      props: {
        items,
        columns: [
          { key: 'name', label: 'Name' },
          { key: 'status', label: 'Status' },
        ],
        mobileTestId: 'mobile-row',
      },
    })
    expect(wrapper.find('[data-testid="mobile-row-0"]').text()).toContain('Alpha')
    expect(wrapper.find('[data-testid="mobile-row-1"]').text()).toContain('Beta')
  })
})
