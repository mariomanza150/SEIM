/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi } from 'vitest'
import { resolveAuthenticatedNavigation } from './authNavigation'

function staffRoute() {
  return {
    meta: { requiresAuth: true, staffReviewQueue: true },
    fullPath: '/notification-routing',
  }
}

function adminRoute() {
  return {
    meta: { requiresAuth: true, adminOnly: true },
    fullPath: '/admin/programs',
  }
}

function studentStoreAfterCheckAuth() {
  let user = null
  return {
    accessToken: 'jwt',
    get isAuthenticated() {
      return !!(this.accessToken && user)
    },
    get isAdmin() {
      if (!user) return false
      return user.role === 'admin' || user.is_staff === true
    },
    get canUseStaffReviewQueue() {
      if (!user) return false
      return (
        user.role === 'coordinator' ||
        user.role === 'admin' ||
        user.is_staff === true
      )
    },
    checkAuth: vi.fn(async () => {
      user = { role: 'student' }
    }),
  }
}

describe('resolveAuthenticatedNavigation', () => {
  it('returns applications for staff route after checkAuth when user is student (MQ-014)', async () => {
    const authStore = studentStoreAfterCheckAuth()
    const outcome = await resolveAuthenticatedNavigation(staffRoute(), authStore)
    expect(outcome).toBe('applications')
    expect(authStore.checkAuth).toHaveBeenCalledOnce()
  })

  it('returns applications for adminOnly route after checkAuth when user is student', async () => {
    const authStore = studentStoreAfterCheckAuth()
    const outcome = await resolveAuthenticatedNavigation(adminRoute(), authStore)
    expect(outcome).toBe('applications')
    expect(authStore.checkAuth).toHaveBeenCalledOnce()
  })

  it('returns next for staff route after checkAuth when user is coordinator', async () => {
    let user = null
    const authStore = {
      accessToken: 'jwt',
      get isAuthenticated() {
        return !!(this.accessToken && user)
      },
      get isAdmin() {
        if (!user) return false
        return user.role === 'admin' || user.is_staff === true
      },
      get canUseStaffReviewQueue() {
        if (!user) return false
        return (
          user.role === 'coordinator' ||
          user.role === 'admin' ||
          user.is_staff === true
        )
      },
      checkAuth: vi.fn(async () => {
        user = { role: 'coordinator' }
      }),
    }
    const outcome = await resolveAuthenticatedNavigation(staffRoute(), authStore)
    expect(outcome).toBe('next')
  })

  it('returns login when there is no token and user is not authenticated', async () => {
    const authStore = {
      accessToken: null,
      isAuthenticated: false,
      isAdmin: false,
      canUseStaffReviewQueue: false,
      checkAuth: vi.fn(),
    }
    const to = { meta: { requiresAuth: true, staffReviewQueue: false }, fullPath: '/dashboard' }
    expect(await resolveAuthenticatedNavigation(to, authStore)).toBe('login')
    expect(authStore.checkAuth).not.toHaveBeenCalled()
  })

  it('returns login when checkAuth throws', async () => {
    const authStore = {
      accessToken: 'jwt',
      isAuthenticated: false,
      isAdmin: false,
      canUseStaffReviewQueue: false,
      checkAuth: vi.fn(async () => {
        throw new Error('network')
      }),
    }
    expect(await resolveAuthenticatedNavigation(staffRoute(), authStore)).toBe('login')
  })

  it('returns next for non-staff route when student is already authenticated', async () => {
    const authStore = {
      accessToken: 'jwt',
      isAuthenticated: true,
      isAdmin: false,
      canUseStaffReviewQueue: false,
      checkAuth: vi.fn(),
    }
    const to = { meta: { requiresAuth: true }, fullPath: '/dashboard' }
    expect(await resolveAuthenticatedNavigation(to, authStore)).toBe('next')
    expect(authStore.checkAuth).not.toHaveBeenCalled()
  })

  it('returns applications when student is already authenticated and targets staff route', async () => {
    const authStore = {
      accessToken: 'jwt',
      isAuthenticated: true,
      isAdmin: false,
      canUseStaffReviewQueue: false,
      checkAuth: vi.fn(),
    }
    expect(await resolveAuthenticatedNavigation(staffRoute(), authStore)).toBe('applications')
  })

  it('returns next when authenticated admin targets adminOnly route', async () => {
    const authStore = {
      accessToken: 'jwt',
      isAuthenticated: true,
      isAdmin: true,
      canUseStaffReviewQueue: true,
      checkAuth: vi.fn(),
    }
    expect(await resolveAuthenticatedNavigation(adminRoute(), authStore)).toBe('next')
  })
})
