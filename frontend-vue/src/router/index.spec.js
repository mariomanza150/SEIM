/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import router from './index.js'
import { routeBusy } from './routeBusy'

const { mockAxios } = vi.hoisted(() => ({
  mockAxios: {
    get: vi.fn(),
    post: vi.fn(),
    create: vi.fn(() => ({
      interceptors: { request: { use: vi.fn() }, response: { use: vi.fn() } },
    })),
  },
}))

vi.mock('axios', () => ({ default: mockAxios }))

const profileStudent = {
  id: 1,
  email: 'student@test.com',
  role: 'student',
  first_name: 'S',
  last_name: 'T',
  full_name: 'S T',
  username: 'student',
}

describe('router beforeEach + resolveAuthenticatedNavigation (MQ-014)', () => {
  beforeEach(async () => {
    routeBusy.value = false
    mockAxios.get.mockResolvedValue({ data: profileStudent })
    localStorage.clear()
    localStorage.setItem('access_token', 'test-jwt')
    setActivePinia(createPinia())
    await router.push({ name: 'Login' })
  })

  it('redirects student to Applications when cold-navigating to a staff-only route', async () => {
    await router.push({ name: 'NotificationRouting' })
    expect(router.currentRoute.value.name).toBe('Applications')
  })

  it('clears routeBusy after navigation completes', async () => {
    expect(routeBusy.value).toBe(false)
    const p = router.push({ name: 'Login' })
    // During async navigation, busy may be true until afterEach runs
    await p
    expect(routeBusy.value).toBe(false)
  })

  it('aliases leftover /seim/admin and /seim/analytics paths', async () => {
    mockAxios.get.mockResolvedValue({
      data: { ...profileStudent, role: 'admin', is_admin: true, is_staff: true },
    })
    localStorage.setItem('access_token', 'admin-jwt')
    setActivePinia(createPinia())
    await router.push({ name: 'Login' })
    await router.push('/admin')
    expect(router.currentRoute.value.name).toBe('AdminPrograms')
    await router.push('/analytics')
    expect(router.currentRoute.value.name).toBe('AnalyticsForecasts')
  })

  it('allows coordinator to reach staff-only route after checkAuth', async () => {
    mockAxios.get.mockResolvedValue({
      data: { ...profileStudent, role: 'coordinator' },
    })
    localStorage.setItem('access_token', 'coord-jwt')
    setActivePinia(createPinia())
    await router.push({ name: 'Login' })
    await router.push({ name: 'NotificationRouting' })
    expect(router.currentRoute.value.name).toBe('NotificationRouting')
  })

  it('redirects coordinator away from SPA admin and partner portal', async () => {
    mockAxios.get.mockResolvedValue({
      data: {
        ...profileStudent,
        role: 'coordinator',
        is_admin: true,
        is_staff: true,
      },
    })
    localStorage.setItem('access_token', 'coord-jwt')
    setActivePinia(createPinia())
    await router.push({ name: 'Login' })
    await router.push({ name: 'AdminPrograms' })
    expect(router.currentRoute.value.name).toBe('Applications')
    await router.push({ name: 'PartnerPortal' })
    expect(router.currentRoute.value.name).toBe('Applications')
  })
})
