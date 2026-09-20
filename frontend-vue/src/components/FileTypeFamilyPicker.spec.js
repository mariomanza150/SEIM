/**
 * @vitest-environment jsdom
 */
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import FileTypeFamilyPicker from './FileTypeFamilyPicker.vue'

const families = [
  { id: 1, slug: 'pdf', name: 'PDF', extensions: 'pdf', aliases: 'acrobat' },
  { id: 2, slug: 'image', name: 'Image', extensions: 'jpg,jpeg,png', aliases: 'photo, imagen' },
  { id: 3, slug: 'word', name: 'Word', extensions: 'doc,docx', aliases: 'docx' },
]

describe('FileTypeFamilyPicker', () => {
  it('marks selected families green with a check and toggles on click', async () => {
    const wrapper = mount(FileTypeFamilyPicker, {
      props: { families, modelValue: [1] },
    })
    const pdf = wrapper.get('[data-testid="file-type-family-pdf"]')
    const image = wrapper.get('[data-testid="file-type-family-image"]')
    expect(pdf.classes()).toContain('btn-success')
    expect(pdf.find('.bi-check-lg').exists()).toBe(true)
    expect(image.classes()).toContain('btn-outline-secondary')
    expect(image.find('.bi-check-lg').exists()).toBe(false)

    await image.trigger('click')
    expect(wrapper.emitted('update:modelValue')[0][0]).toEqual([1, 2])
  })
})
