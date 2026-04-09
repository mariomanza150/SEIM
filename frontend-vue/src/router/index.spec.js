/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import router from './index.js'

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
})
