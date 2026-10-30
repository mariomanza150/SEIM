/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
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

  it('matches English aliases and commits on blur', async () => {
    vi.useFakeTimers()
    const wrapper = mount(SearchableSelect, {
      props: {
        modelValue: '',
        options: [{ value: 'España', label: 'España', aliases: ['Spain'] }],
      },
    })

    const input = wrapper.get('input')
    await input.setValue('Spain')
    await input.trigger('blur')
    vi.advanceTimersByTime(150)
    await flushPromises()

    expect(wrapper.emitted('update:modelValue')?.at(-1)).toEqual(['España'])
    vi.useRealTimers()
  })

  it('selects the unique filtered option on Enter', async () => {
    const wrapper = mount(SearchableSelect, {
      props: {
        modelValue: '',
        options: [
          { value: 'España', label: 'España', aliases: ['Spain'] },
          { value: 'Francia', label: 'Francia', aliases: ['France'] },
        ],
      },
    })

    const input = wrapper.get('input')
    await input.setValue('spain')
    await input.trigger('keydown.enter')

    expect(wrapper.emitted('update:modelValue')?.at(-1)).toEqual(['España'])
  })

  it('opens the dropdown upward when placement is up', async () => {
    const wrapper = mount(SearchableSelect, {
      props: {
        modelValue: '',
        placement: 'up',
        options: [{ value: 'English', label: 'English' }],
      },
    })

    await wrapper.get('input').trigger('focus')
    expect(wrapper.get('.searchable-select-dropdown').classes()).toContain(
      'searchable-select-dropdown--up',
    )
  })

  it('keeps custom typed values when allowCustom is set', async () => {
    vi.useFakeTimers()
    const wrapper = mount(SearchableSelect, {
      props: {
        modelValue: '',
        allowCustom: true,
        options: [{ value: 'MIT', label: 'MIT · EUA' }],
      },
    })

    const input = wrapper.get('input')
    await input.setValue('Brand New College')
    expect(wrapper.emitted('query-change')?.at(-1)).toEqual(['Brand New College'])
    await input.trigger('blur')
    vi.advanceTimersByTime(150)
    await flushPromises()

    expect(wrapper.emitted('update:modelValue')?.at(-1)).toEqual(['Brand New College'])
    vi.useRealTimers()
  })

  it('includes empty-value options such as No scale', async () => {
    const wrapper = mount(SearchableSelect, {
      props: {
        modelValue: '',
        options: [
          { value: '', label: 'No scale' },
          { value: 'gs-1', label: 'ECTS' },
        ],
      },
    })

    await wrapper.get('input').trigger('focus')
    const items = wrapper.findAll('.searchable-select-dropdown .list-group-item')
    expect(items.map((li) => li.text())).toContain('No scale')
  })

  it('keeps a value picked from the list after blur', async () => {
    vi.useFakeTimers()
    const wrapper = mount(SearchableSelect, {
      props: {
        modelValue: '',
        options: [
          { value: 'Ecuador', label: 'Ecuador' },
          { value: 'Bolivia', label: 'Bolivia' },
          { value: 'Colombia', label: 'Colombia' },
        ],
      },
    })
    const input = wrapper.get('input')
    await input.trigger('focus')
    await input.setValue('o')
    const items = wrapper.findAll('.searchable-select-dropdown .list-group-item')
    await items.find((li) => li.text() === 'Bolivia').trigger('mousedown')
    // Parent has not echoed v-model yet when blur fires.
    await input.trigger('blur')
    vi.advanceTimersByTime(150)
    await flushPromises()
    const emitted = wrapper.emitted('update:modelValue').map((e) => e[0])
    expect(emitted).toContain('Bolivia')
    expect(emitted).not.toContain('')
    expect(emitted[emitted.length - 1]).toBe('Bolivia')
    expect(input.element.value).toBe('Bolivia')
    vi.useRealTimers()
  })
})
