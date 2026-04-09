/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import HelloWorld from './HelloWorld.vue'
import i18n, { setAppLocale } from '@/i18n'

describe('HelloWorld', () => {
  beforeEach(() => {
    localStorage.clear()
    setAppLocale('en')
  })

  afterEach(() => {
    setAppLocale('en')
    localStorage.clear()
  })

  it('renders translated starter copy in English', () => {
    const wrapper = mount(HelloWorld, {
      props: { msg: 'Test' },
      global: { plugins: [i18n] },
    })
    expect(wrapper.get('h1').text()).toBe('Test')
    expect(wrapper.text()).toContain('Check out')
    expect(wrapper.text()).toContain('create-vue')
    expect(wrapper.text()).toContain('components/HelloWorld.vue')
  })

  it('uses Spanish strings when locale is es', () => {
    setAppLocale('es')
    const wrapper = mount(HelloWorld, {
      props: { msg: 'Hola' },
      global: { plugins: [i18n] },
    })
    expect(wrapper.text()).toContain('Consulta')
    expect(wrapper.text()).toContain('el contador es 0')
  })
})
