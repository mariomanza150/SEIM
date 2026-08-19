/**
 * @vitest-environment jsdom
 */
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SearchableSelect from './SearchableSelect.vue'

describe('SearchableSelect', () => {
  it('filters options and emits selected value', async () => {
    const wrapper = mount(SearchableSelect, {
      props: {
        modelValue: '',
        options: [
          { value: 'Mexico', label: 'Mexico' },
          { value: 'Spain', label: 'Spain' },
        ],
      },
    })

    const input = wrapper.get('input')
    await input.setValue('spa')
    await input.trigger('focus')
    await wrapper.get('.searchable-select-dropdown .list-group-item').trigger('mousedown')

    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')[0]).toEqual(['Spain'])
  })
})
