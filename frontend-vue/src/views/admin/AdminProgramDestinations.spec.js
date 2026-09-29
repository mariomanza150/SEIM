/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import { createRouter, createMemoryHistory } from 'vue-router'
import en from '@/locales/en.json'
import SearchableSelect from '@/components/SearchableSelect.vue'
import AdminProgramDestinations from './AdminProgramDestinations.vue'

const { mockGet, mockPost, mockPatch } = vi.hoisted(() => ({
  mockGet: vi.fn(),
  mockPost: vi.fn(),
  mockPatch: vi.fn(),
}))

vi.mock('@/services/api', () => ({
  default: { get: mockGet, post: mockPost, patch: mockPatch },
}))

let wrapper

function apiGet(url) {
  if (String(url).includes('/api/grades/scales/active/')) {
    return Promise.resolve({
      data: {
        results: [
          { id: 'gs-us', name: 'US GPA', code: 'US', country: 'United States' },
          { id: 'gs-ects', name: 'ECTS', code: 'ECTS', country: 'European Union' },
          { id: 'gs-mx', name: 'MX 0-100', code: 'MX', country: 'Mexico' },
        ],
      },
    })
  }
  if (String(url).includes('/api/accounts/catalogs/countries/')) {
    return Promise.resolve({
      data: [
        { value: 'España', label: 'España', aliases: ['Spain'] },
        { value: 'EUA', label: 'EUA', aliases: ['United States', 'USA'] },
        { value: 'Alemania', label: 'Alemania', aliases: ['Germany'] },
      ],
    })
  }
  if (String(url).includes('/api/host-institutions/') && !String(url).includes('/schools')) {
    // Catalog list (top-level) vs nested program list handled below for programs URL.
    if (!String(url).includes('/api/programs/')) {
      return Promise.resolve({
        data: {
          results: [
            {
              id: 'cat-1',
              name: 'Universidad de León',
              country: 'España',
              grade_scale: 'gs-ects',
              is_active: true,
            },
            {
              id: 'cat-2',
              name: 'MIT',
              country: 'EUA',
              grade_scale: 'gs-us',
              is_active: true,
            },
          ],
        },
      })
    }
  }
  if (String(url).match(/\/api\/programs\/prog-1\/?$/)) {
    return Promise.resolve({ data: { id: 'prog-1', name: 'Mobility A' } })
  }
  if (String(url).includes('/api/programs/prog-1/host-institutions/')) {
    return Promise.resolve({ data: [] })
  }
  if (String(url).includes('/schools/')) {
    return Promise.resolve({ data: [] })
  }
  if (String(url).includes('/api/host-subjects/')) {
    return Promise.resolve({ data: [] })
  }
  if (String(url).includes('/academic-programs/')) {
    return Promise.resolve({ data: [] })
  }
  return Promise.resolve({ data: [] })
}

async function mountPage() {
  const i18n = createI18n({ legacy: false, locale: 'en', messages: { en } })
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', name: 'Dashboard', component: { template: '<div />' } },
        { path: '/help', name: 'HelpCenter', component: { template: '<div />' } },
      { path: '/admin/programs', name: 'AdminPrograms', component: { template: '<div />' } },
      {
        path: '/admin/programs/:id/destinations',
        name: 'AdminProgramDestinations',
        component: AdminProgramDestinations,
      },
    ],
  })
  await router.push({ name: 'AdminProgramDestinations', params: { id: 'prog-1' } })
  return mount(AdminProgramDestinations, {
    global: {
      plugins: [i18n, router],
      stubs: { Teleport: true },
    },
  })
}

describe('AdminProgramDestinations', () => {
  beforeEach(() => {
    mockGet.mockImplementation((url) => apiGet(url))
    mockPost.mockResolvedValue({ data: { id: 'new-1' } })
    mockPatch.mockResolvedValue({ data: {} })
  })

  afterEach(() => {
    wrapper?.unmount()
    vi.clearAllMocks()
  })

  it('autocompletes country and grade scale from catalog host suggestions', async () => {
    wrapper = await mountPage()
    await flushPromises()

    expect(wrapper.get('[data-testid="add-university-card"]').text()).toContain(
      'Add host university',
    )

    const nameInput = wrapper.get('[data-testid="add-university-name"]')
    await nameInput.trigger('focus')
    await nameInput.setValue('León')
    await flushPromises()

    const suggestion = wrapper
      .findAll('.searchable-select-dropdown .list-group-item')
      .find((li) => li.text().includes('Universidad de León'))
    expect(suggestion).toBeTruthy()
    await suggestion.trigger('mousedown')
    await flushPromises()

    expect(wrapper.vm.newUni.name).toBe('Universidad de León')
    expect(wrapper.vm.newUni.country).toBe('España')
    expect(wrapper.vm.newUni.grade_scale).toBe('gs-ects')

    const gradeSelect = wrapper.findAllComponents(SearchableSelect).find(
      (c) => c.props('dataTestid') === 'add-university-grade-scale',
    )
    const labels = gradeSelect.props('options').map((o) => o.label).join(' | ')
    expect(labels).toContain('ECTS')
    expect(labels).not.toContain('US GPA')
  })

  it('posts a new host university with selected fields', async () => {
    wrapper = await mountPage()
    await flushPromises()

    wrapper.vm.newUni.name = 'New Partner U'
    wrapper.vm.newUni.country = 'EUA'
    wrapper.vm.newUni.grade_scale = 'gs-us'
    await wrapper.vm.createUniversity()
    await flushPromises()

    expect(mockPost).toHaveBeenCalledWith(
      '/api/programs/prog-1/host-institutions/',
      expect.objectContaining({
        name: 'New Partner U',
        country: 'EUA',
        grade_scale: 'gs-us',
        is_active: true,
      }),
    )
  })
})
