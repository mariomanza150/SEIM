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

  describe('register', () => {
    it('posts signup payload and returns true on success', async () => {
      axios.post.mockResolvedValueOnce({
        data: { detail: 'Registration successful. Please check your email to verify your account.' },
      })

      const store = useAuthStore()
      const result = await store.register({
        email: 'new@test.com',
        username: 'newuser',
        password: 'Passw0rd!',
        password2: 'Passw0rd!',
        first_name: 'New',
        middle_name: 'Middle',
        last_name: 'User',
        mothers_last_name: 'Family',
      })

      expect(result).toBe(true)
      expect(store.error).toBeNull()
      expect(axios.post).toHaveBeenCalledWith(
        expect.stringContaining('/api/accounts/register/'),
        {
          email: 'new@test.com',
          username: 'newuser',
          password: 'Passw0rd!',
          password2: 'Passw0rd!',
          first_name: 'New',
          middle_name: 'Middle',
          last_name: 'User',
          mothers_last_name: 'Family',
        },
      )
    })

    it('on failure sets error and returns false', async () => {
      axios.post.mockRejectedValueOnce({
        response: { data: { detail: 'Username already exists' } },
      })

      const store = useAuthStore()
      const result = await store.register({
        email: 'new@test.com',
        username: 'taken',
        password: 'Passw0rd!',
        password2: 'Passw0rd!',
      })

      expect(result).toBe(false)
      expect(store.error).toContain('Username')
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

    it('stores a rotated refresh token from the refresh response', async () => {
      localStorage.setItem('seim_refresh_token', 'old_rt')
      const store = useAuthStore()
      store.accessToken = 'old_at'
      axios.post.mockResolvedValueOnce({ data: { access: 'new_at', refresh: 'new_rt' } })

      await store.refreshToken()

      expect(localStorage.getItem('seim_refresh_token')).toBe('new_rt')
      expect(localStorage.getItem('refresh_token')).toBe('new_rt')
    })

    it('shares one in-flight refresh across concurrent callers', async () => {
      localStorage.setItem('seim_refresh_token', 'rt')
      const store = useAuthStore()
      store.accessToken = 'old_at'
      let resolveRefresh
      axios.post.mockImplementationOnce(
        () =>
          new Promise((resolve) => {
            resolveRefresh = resolve
          }),
      )

      const first = store.refreshToken()
      const second = store.refreshToken()
      resolveRefresh({ data: { access: 'new_at', refresh: 'new_rt' } })
      await Promise.all([first, second])

      expect(axios.post).toHaveBeenCalledTimes(1)
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
          middle_name: 'Middle',
          mothers_last_name: 'Family',
          secondary_email: 'student@example.net',
          is_ready_to_apply: true,
        },
      })

      const user = await store.fetchUserProfile()

      expect(user.email).toBe('u@test.com')
      expect(store.user?.full_name).toBe('Test User')
      expect(store.user?.role).toBe('student')
      expect(store.user?.middle_name).toBe('Middle')
      expect(store.user?.mothers_last_name).toBe('Family')
      expect(store.user?.secondary_email).toBe('student@example.net')
      expect(store.user?.is_ready_to_apply).toBe(true)
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
          role: 'admin',
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
      expect(store.canUsePartnerPortal).toBe(false)
    })

    it('does not treat coordinator staff as SPA admin or partner (MQ-2026-08-16-001/002)', () => {
      const store = useAuthStore()
      store.user = {
        role: 'coordinator',
        email: 'coordinator@test.com',
        is_admin: true,
        is_staff: true,
        is_superuser: false,
      }
      expect(store.isAdmin).toBe(false)
      expect(store.canUseStaffReviewQueue).toBe(true)
      expect(store.canUsePartnerPortal).toBe(false)
    })

    it('treats partner role as partner portal access', () => {
      const store = useAuthStore()
      store.user = { role: 'partner', email: 'iro@partner.edu' }
      expect(store.isPartner).toBe(true)
      expect(store.canUsePartnerPortal).toBe(true)
      expect(store.canUseStaffReviewQueue).toBe(false)
    })

    it('throws and sets error on failure', async () => {
      const store = useAuthStore()
      store.accessToken = 'at'
      axios.get.mockRejectedValueOnce(new Error('Network error'))

      await expect(store.fetchUserProfile()).rejects.toThrow('Network error')
      expect(store.error).toBe('Failed to fetch user profile')
    })
  })

  describe('verifyEmail', () => {
    it('posts token and returns true on success', async () => {
      const store = useAuthStore()
      axios.post.mockResolvedValueOnce({ data: { detail: 'ok' } })

      const ok = await store.verifyEmail('tok123')

      expect(ok).toBe(true)
      expect(axios.post).toHaveBeenCalledWith(
        expect.stringContaining('/api/accounts/verify-email/'),
        { token: 'tok123' },
      )
    })

    it('sets error and returns false on failure', async () => {
      const store = useAuthStore()
      axios.post.mockRejectedValueOnce({
        response: { data: { token: ['Invalid verification token.'] } },
      })

      const ok = await store.verifyEmail('bad')

      expect(ok).toBe(false)
      expect(store.error).toBeTruthy()
    })
  })

  describe('requestPasswordReset', () => {
    it('posts email and returns true on success', async () => {
      axios.post.mockResolvedValueOnce({ data: { message: 'Password reset email sent' } })
      const store = useAuthStore()
      const ok = await store.requestPasswordReset('ada@example.com')
      expect(ok).toBe(true)
      expect(axios.post).toHaveBeenCalledWith(
        expect.stringContaining('/api/accounts/password-reset-request/'),
        { email: 'ada@example.com' },
      )
    })
  })

  describe('confirmPasswordReset', () => {
    it('posts token payload and returns true on success', async () => {
      axios.post.mockResolvedValueOnce({ data: { detail: 'Password has been reset successfully.' } })
      const store = useAuthStore()
      const ok = await store.confirmPasswordReset({
        email: 'ada@example.com',
        token: 'tok123',
        new_password: 'Newpass1!',
      })
      expect(ok).toBe(true)
      expect(axios.post).toHaveBeenCalledWith(
        expect.stringContaining('/api/accounts/password-reset-confirm/'),
        {
          email: 'ada@example.com',
          token: 'tok123',
          new_password: 'Newpass1!',
        },
      )
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

    it('composes first and last name when full_name is missing', () => {
      const store = useAuthStore()
      store.user = { first_name: 'Sofia', last_name: 'Martinez', email: 's@test.com' }
      expect(store.userName).toBe('Sofia Martinez')
    })
  })
})
