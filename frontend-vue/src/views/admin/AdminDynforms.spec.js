/**
 * @vitest-environment jsdom
 */
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import { createRouter, createMemoryHistory } from 'vue-router'
import en from '@/locales/en.json'
import AdminDynforms from './AdminDynforms.vue'

describe('AdminDynforms', () => {
  it('links to the SPA form builder and the Django dynforms UI', async () => {
    const i18n = createI18n({ legacy: false, locale: 'en', messages: { en } })
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', name: 'Dashboard', component: { template: '<div />' } },
        { path: '/admin/forms', name: 'AdminForms', component: { template: '<div />' } },
        { path: '/admin/dynforms', name: 'AdminDynforms', component: AdminDynforms },
      ],
    })
    await router.push({ name: 'AdminDynforms' })
    const wrapper = mount(AdminDynforms, { global: { plugins: [i18n, router] } })
    expect(wrapper.get('[data-testid="dynforms-legacy-builder"]').attributes('href')).toBe('/dynforms/')
    expect(wrapper.get('[data-testid="dynforms-spa-forms"]').attributes('href')).toBe('/admin/forms')
  })
})
