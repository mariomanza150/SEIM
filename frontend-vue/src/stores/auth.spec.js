/**
 * Auth store unit tests
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from './auth'

vi.mock('axios', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
  },
}))

// Import axios after mock so tests get the mocked instance
const axios = (await import('axios')).default

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    localStorage.clear()
  })

  describe('initial state', () => {
    it('is not authenticated when no token or user', () => {
      const store = useAuthStore()
      expect(store.isAuthenticated).toBe(false)
      expect(store.userName).toBe('')
      expect(store.userRole).toBeNull()
    })

    it('reads tokens from localStorage', () => {
      localStorage.setItem('seim_access_token', 'at')
      localStorage.setItem('seim_refresh_token', 'rt')
      const store = useAuthStore()
      expect(store.accessToken).toBe('at')
      expect(localStorage.getItem('seim_refresh_token')).toBe('rt')
    })
  })

  describe('logout', () => {
    it('clears state and localStorage', async () => {
      axios.post.mockResolvedValue({})
      localStorage.setItem('access_token', 'at')
      localStorage.setItem('refresh_token', 'rt')
      localStorage.setItem('seim_access_token', 'at')
      localStorage.setItem('seim_refresh_token', 'rt')
      const store = useAuthStore()
      store.user = { email: 'u@test.com' }

      await store.logout()

      expect(store.user).toBeNull()
      expect(store.accessToken).toBeNull()
      expect(localStorage.getItem('access_token')).toBeNull()
      expect(localStorage.getItem('refresh_token')).toBeNull()
      expect(localStorage.getItem('seim_access_token')).toBeNull()
      expect(localStorage.getItem('seim_refresh_token')).toBeNull()
      expect(axios.post).toHaveBeenCalledWith(
        expect.stringContaining('/logout/'),
        { refresh: 'rt' },
        expect.objectContaining({
          withCredentials: true,
          headers: { Authorization: 'Bearer at' },
        }),
      )
    })
  })

  describe('login', () => {
    it('on success sets tokens and fetches profile', async () => {
      axios.post
        .mockResolvedValueOnce({ data: { access: 'new_access', refresh: 'new_refresh' } })
      axios.get
        .mockResolvedValueOnce({
          data: {
            id: 1,
            email: 'u@test.com',
            first_name: 'First',
            last_name: 'Last',
            full_name: 'First Last',
            role: 'student',
            username: 'user',
          },
        })

      const store = useAuthStore()
      const result = await store.login('u@test.com', 'pass123')

      expect(result).toBe(true)
      expect(store.accessToken).toBe('new_access')
      expect(localStorage.getItem('refresh_token')).toBe('new_refresh')
      expect(localStorage.getItem('seim_access_token')).toBe('new_access')
      expect(localStorage.getItem('seim_refresh_token')).toBe('new_refresh')
      expect(store.user?.email).toBe('u@test.com')
      expect(store.user?.full_name).toBe('First Last')
      expect(store.isAuthenticated).toBe(true)
      expect(store.userName).toBe('First Last')
      expect(store.userRole).toBe('student')
      expect(axios.post).toHaveBeenCalledWith(
        expect.stringContaining('/api/accounts/login/'),
        { login: 'u@test.com', password: 'pass123' }
      )
      expect(axios.get).toHaveBeenCalledWith(
        expect.stringContaining('/profile/'),
        expect.objectContaining({ headers: { Authorization: 'Bearer new_access' } })
      )
    })

    it('on failure sets error and returns false', async () => {
      axios.post.mockRejectedValueOnce({ response: { data: { detail: 'Invalid credentials' } } })

      const store = useAuthStore()
      const result = await store.login('u@test.com', 'wrong')

      expect(result).toBe(false)
      expect(store.error).toContain('Invalid')
      expect(store.accessToken).toBeNull()
      expect(store.isAuthenticated).toBe(false)
    })

    it('maps field validation errors to a message', async () => {
      axios.post.mockRejectedValueOnce({
        response: { data: { login: ['Enter a valid email address.'] } },
      })

      const store = useAuthStore()
      const result = await store.login('bad', 'x')

      expect(result).toBe(false)
      expect(store.error).toContain('email')
    })
  })

  describe('refreshToken (refreshAccessToken)', () => {
    it('updates access token on success', async () => {
      localStorage.setItem('seim_refresh_token', 'rt')
      const store = useAuthStore()
      store.accessToken = 'old_at'
      axios.post.mockResolvedValueOnce({ data: { access: 'new_at' } })

      const result = await store.refreshToken()

      expect(result).toBe('new_at')
      expect(store.accessToken).toBe('new_at')
      expect(localStorage.getItem('access_token')).toBe('new_at')
      expect(localStorage.getItem('seim_access_token')).toBe('new_at')
      expect(axios.post).toHaveBeenCalledWith(
        expect.stringContaining('/token/refresh/'),
        { refresh: 'rt' }
      )
    })

    it('throws and clears auth when no refresh token', async () => {
      const store = useAuthStore()

      await expect(store.refreshToken()).rejects.toThrow('No refresh token')
    })

    it('calls logout when refresh fails', async () => {
      localStorage.setItem('refresh_token', 'rt')
      localStorage.setItem('seim_refresh_token', 'rt')
      const store = useAuthStore()
      store.accessToken = 'at'
      axios.post
        .mockRejectedValueOnce(new Error('Refresh failed'))
        .mockResolvedValueOnce({})

      await expect(store.refreshToken()).rejects.toThrow('Refresh failed')
      expect(store.accessToken).toBeNull()
    })
  })

  describe('fetchUserProfile', () => {
    it('sets user from profile response', async () => {
      const store = useAuthStore()
      store.accessToken = 'at'
      axios.get.mockResolvedValueOnce({
        data: {
          id: 1,
          email: 'u@test.com',
          full_name: 'Test User',
          role: 'student',
          username: 'user',
        },
      })

      const user = await store.fetchUserProfile()

      expect(user.email).toBe('u@test.com')
      expect(store.user?.full_name).toBe('Test User')
      expect(store.user?.role).toBe('student')
      expect(store.user?.is_staff).toBe(false)
      expect(store.user?.is_superuser).toBe(false)
    })

    it('maps is_staff and is_superuser for SPA permission gates', async () => {
      const store = useAuthStore()
      store.accessToken = 'at'
      axios.get.mockResolvedValueOnce({
        data: {
          id: 1,
          email: 'admin@test.com',
          full_name: 'Admin User',
          role: 'student',
          username: 'admin',
          is_admin: true,
          is_staff: true,
          is_superuser: true,
        },
      })

      await store.fetchUserProfile()

      expect(store.user?.is_admin).toBe(true)
      expect(store.user?.is_staff).toBe(true)
      expect(store.user?.is_superuser).toBe(true)
      expect(store.isAdmin).toBe(true)
      expect(store.canUseStaffReviewQueue).toBe(true)
    })

    it('throws and sets error on failure', async () => {
      const store = useAuthStore()
      store.accessToken = 'at'
      axios.get.mockRejectedValueOnce(new Error('Network error'))

      await expect(store.fetchUserProfile()).rejects.toThrow('Network error')
      expect(store.error).toBe('Failed to fetch user profile')
    })
  })

  describe('userName getter', () => {
    it('returns full_name when set', () => {
      const store = useAuthStore()
      store.user = { full_name: 'Jane Doe', email: 'j@test.com' }
      expect(store.userName).toBe('Jane Doe')
    })

    it('falls back to email when no full_name', () => {
      const store = useAuthStore()
      store.user = { email: 'j@test.com' }
      expect(store.userName).toBe('j@test.com')
    })

    it('returns "User" when user has no name or email', () => {
      const store = useAuthStore()
      store.user = {}
      expect(store.userName).toBe('User')
    })
  })
})
