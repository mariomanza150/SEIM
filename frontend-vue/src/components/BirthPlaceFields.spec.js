/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import BirthPlaceFields from './BirthPlaceFields.vue'
import api from '@/services/api'
import i18n, { setAppLocale } from '@/i18n'

vi.mock('@/services/api', () => ({ default: { get: vi.fn() } }))

function mockGeo() {
  api.get.mockImplementation((url, config) => {
    if (url === '/api/accounts/catalogs/geo/countries/') {
      return Promise.resolve({
        data: [
          { code: 'MX', value: 'México', label: 'México', has_states: true, aliases: ['Mexico'] },
          { code: 'ES', value: 'España', label: 'España', has_states: false },
        ],
      })
    }
    if (url === '/api/accounts/catalogs/geo/states/') {
      return Promise.resolve({ data: config.params.country === 'MX' ? [{ code: 'COA', value: 'Coahuila', label: 'Coahuila' }] : [] })
    }
    if (url === '/api/accounts/catalogs/geo/cities/') {
      return Promise.resolve({ data: config.params.state === 'Coahuila' ? [{ value: 'Saltillo', label: 'Saltillo' }] : [] })
    }
    return Promise.reject(new Error(`Unhandled ${url}`))
  })
}

function mountFields(props = {}) {
  return mount(BirthPlaceFields, {
    props: { country: '', state: '', city: '', ...props },
    global: { plugins: [i18n] },
  })
}

describe('BirthPlaceFields', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    setAppLocale('en')
    mockGeo()
  })

  it('loads states and cities for a Mexican birth place', async () => {
    const wrapper = mountFields({ country: 'México', state: 'Coahuila', city: 'Saltillo' })
    await flushPromises()
    expect(api.get).toHaveBeenCalledWith('/api/accounts/catalogs/geo/states/', { params: { country: 'MX' } })
    expect(api.get).toHaveBeenCalledWith('/api/accounts/catalogs/geo/cities/', { params: { country: 'MX', state: 'Coahuila' } })
    expect(wrapper.find('[data-testid="birth-city"]').element.value).toBe('Saltillo')
  })

  it('uses free-text inputs when the country has no state list', async () => {
    const wrapper = mountFields({ country: 'España' })
    await flushPromises()
    expect(wrapper.find('[data-testid="birth-state-manual"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="birth-city-manual"]').exists()).toBe(true)
    await wrapper.find('[data-testid="birth-city-manual"]').setValue('Madrid')
    expect(wrapper.emitted('update:city').at(-1)).toEqual(['Madrid'])
  })

  it('shows saved values that are not in the list as manual entries', async () => {
    const wrapper = mountFields({ country: 'México', state: 'Coahuila', city: 'Ejido La Rosa' })
    await flushPromises()
    const manual = wrapper.find('[data-testid="birth-city-manual"]')
    expect(manual.exists()).toBe(true)
    expect(manual.element.value).toBe('Ejido La Rosa')
  })

  it('offers an Other / not listed option that switches to manual entry', async () => {
    const wrapper = mountFields()
    await flushPromises()
    const input = wrapper.find('[data-testid="birth-country"]')
    await input.trigger('focus')
    const other = wrapper.findAll('li').find((li) => li.text().includes('not listed'))
    expect(other).toBeTruthy()
    await other.trigger('mousedown')
    await flushPromises()
    expect(wrapper.find('[data-testid="birth-country-manual"]').exists()).toBe(true)
    expect(wrapper.emitted('update:country').at(-1)).toEqual([''])
  })

  it('clears state and city when the country changes', async () => {
    const wrapper = mountFields({ country: 'México', state: 'Coahuila', city: 'Saltillo' })
    await flushPromises()
    await wrapper.find('[data-testid="birth-country"]').trigger('focus')
    await wrapper.find('[data-testid="birth-country"]').setValue('Esp')
    const spain = wrapper.findAll('li').find((li) => li.text() === 'España')
    await spain.trigger('mousedown')
    expect(wrapper.emitted('update:country').at(-1)).toEqual(['España'])
    expect(wrapper.emitted('update:state').at(-1)).toEqual([''])
    expect(wrapper.emitted('update:city').at(-1)).toEqual([''])
  })

  it('shows the legacy single-line birthplace as a hint', async () => {
    const wrapper = mountFields({ legacyBirthplace: 'Monterrey' })
    await flushPromises()
    expect(wrapper.find('[data-testid="birth-place-legacy"]').text()).toContain('Monterrey')
  })
})
