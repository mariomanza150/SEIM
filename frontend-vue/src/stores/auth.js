/**
 * Auth Store - Pinia store for authentication state
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import { formatApiErrorResponse, fieldErrorsFromResponse } from '@/utils/apiErrors'
import {
  ACCESS_TOKEN_KEYS,
  REFRESH_TOKEN_KEYS,
  getStoredToken,
  persistToken,
} from '@/utils/authTokens'
import { clearReviewQueueNav } from '@/utils/reviewQueueNav'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

const formatAuthErrorResponse = formatApiErrorResponse

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const accessToken = ref(getStoredToken(ACCESS_TOKEN_KEYS))
  const refreshToken = ref(getStoredToken(REFRESH_TOKEN_KEYS))
  const isLoading = ref(false)
  const error = ref(null)
  const errorCode = ref(null)
  const fieldErrors = ref({})

  // Getters
  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)
  const userRole = computed(() => user.value?.role || null)
  const isAdmin = computed(() => {
    const u = user.value
    if (!u) return false
    if (u.role === 'admin' || u.is_superuser === true) return true
    if (u.role === 'coordinator' || u.role === 'partner' || u.role === 'student') {
      return false
    }
    if (typeof u.is_admin === 'boolean') return u.is_admin
    return false
  })
  const isCoordinator = computed(() => user.value?.role === 'coordinator')
  const canUseStaffReviewQueue = computed(
    () => isAdmin.value || user.value?.role === 'coordinator',
  )
  const isPartner = computed(() => user.value?.role === 'partner')
  const canUsePartnerPortal = computed(() => isPartner.value)
  const userName = computed(() => {
    if (!user.value) return ''
    if (user.value.full_name) return user.value.full_name
    const parts = [
      user.value.first_name,
      user.value.middle_name,
      user.value.last_name,
      user.value.mothers_last_name,
    ].filter(Boolean)
    if (parts.length) return parts.join(' ')
    return user.value.email || user.value.username || 'User'
  })

  function extractErrorCode(body) {
    if (!body || typeof body !== 'object') return null
    if (typeof body.code === 'string') return body.code
    if (body.detail && typeof body.detail === 'object' && typeof body.detail.code === 'string') {
      return body.detail.code
    }
    return null
  }

  // Actions
  async function login(email, password) {
    isLoading.value = true
    error.value = null
    errorCode.value = null
    fieldErrors.value = {}

    try {
      // Create a Django session and JWTs together for cross-system navigation.
      const response = await axios.post(`${API_BASE_URL}/api/accounts/login/`, {
        login: email,
        password,
      })

      accessToken.value = response.data.access
      refreshToken.value = response.data.refresh

      persistToken(ACCESS_TOKEN_KEYS, accessToken.value)
      persistToken(REFRESH_TOKEN_KEYS, refreshToken.value)

      // Fetch user profile
      await fetchUserProfile()

      return true
    } catch (err) {
      const body = err.response?.data
      fieldErrors.value = fieldErrorsFromResponse(body)
      errorCode.value = extractErrorCode(body)
      error.value =
        formatAuthErrorResponse(body) ||
        (typeof body === 'string' ? body : null) ||
        'Login failed. Please check your credentials.'
      console.error('Login error:', err)
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Self-service signup. Creates an inactive user pending email verification.
   * @param {{ email: string, username?: string, password: string, password2: string, first_name: string, middle_name?: string, last_name: string, mothers_last_name?: string }} payload
   * @returns {Promise<boolean>}
   */
  async function register(payload) {
    isLoading.value = true
    error.value = null
    errorCode.value = null
    fieldErrors.value = {}

    try {
      await axios.post(`${API_BASE_URL}/api/accounts/register/`, {
        email: payload.email,
        ...(payload.username ? { username: payload.username } : {}),
        password: payload.password,
        password2: payload.password2,
        first_name: payload.first_name || '',
        middle_name: payload.middle_name || '',
        last_name: payload.last_name || '',
        mothers_last_name: payload.mothers_last_name || '',
      })
      return true
    } catch (err) {
      const body = err.response?.data
      fieldErrors.value = fieldErrorsFromResponse(body)
      error.value =
        formatAuthErrorResponse(body) ||
        (typeof body === 'string' ? body : null) ||
        'Registration failed. Please try again.'
      console.error('Registration error:', err)
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Request a password-reset email. Always returns true on HTTP 200
   * (the API does not reveal whether the address exists).
   * @param {string} email
   * @returns {Promise<boolean>}
   */
  async function requestPasswordReset(email) {
    isLoading.value = true
    error.value = null

    try {
      await axios.post(`${API_BASE_URL}/api/accounts/password-reset-request/`, { email })
      return true
    } catch (err) {
      const body = err.response?.data
      error.value =
        formatAuthErrorResponse(body) ||
        (typeof body === 'string' ? body : null) ||
        'Could not send a password reset email. Please try again.'
      console.error('Password reset request error:', err)
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Set a new password using the email + token from the reset message.
   * @param {{ email: string, token: string, new_password: string }} payload
   * @returns {Promise<boolean>}
   */
  async function confirmPasswordReset(payload) {
    isLoading.value = true
    error.value = null

    try {
      await axios.post(`${API_BASE_URL}/api/accounts/password-reset-confirm/`, {
        email: payload.email,
        token: payload.token,
        new_password: payload.new_password,
      })
      return true
    } catch (err) {
      const body = err.response?.data
      error.value =
        formatAuthErrorResponse(body) ||
        (typeof body === 'string' ? body : null) ||
        'Password reset failed. The link may be invalid or expired.'
      console.error('Password reset confirm error:', err)
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Confirm email ownership with the token from the verification link.
   * @param {string} token
   * @returns {Promise<boolean>}
   */
  async function verifyEmail(token) {
    isLoading.value = true
    error.value = null
    errorCode.value = null

    try {
      await axios.post(`${API_BASE_URL}/api/accounts/verify-email/`, { token })
      return true
    } catch (err) {
      const body = err.response?.data
      errorCode.value = extractErrorCode(body)
      error.value =
        formatAuthErrorResponse(body) ||
        (typeof body === 'string' ? body : null) ||
        'Email verification failed. The link may be invalid or expired.'
      console.error('Verify email error:', err)
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Resend the email-verification link. Rate-limited server-side (1 / 5 minutes / email).
   * @param {string} email
   * @returns {Promise<{ ok: boolean, status: number|null, message: string|null, retryAfter: number|null }>}
   */
  async function resendVerificationEmail(email) {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/accounts/resend-verification/`,
        { email },
      )
      return {
        ok: true,
        status: response.status,
        message: response.data?.message || null,
        retryAfter: null,
      }
    } catch (err) {
      const body = err.response?.data
      const status = err.response?.status ?? null
      const retryHeader = err.response?.headers?.['retry-after']
      const retryAfterRaw = retryHeader ?? body?.retry_after
      const retryAfter =
        retryAfterRaw != null && retryAfterRaw !== ''
          ? Number.parseInt(String(retryAfterRaw), 10)
          : null
      return {
        ok: false,
        status,
        message:
          formatAuthErrorResponse(body) ||
          body?.error ||
          (typeof body === 'string' ? body : null) ||
          'Could not resend the verification email.',
        retryAfter: Number.isFinite(retryAfter) ? retryAfter : null,
      }
    }
  }

  async function logout() {
    const refresh = refreshToken.value
    const access = accessToken.value

    // Clear local session first so the UI can navigate even if the API is slow/unreachable.
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    persistToken(ACCESS_TOKEN_KEYS, null)
    persistToken(REFRESH_TOKEN_KEYS, null)
    // Drop staff review-queue sibling ids so the next user on this browser
    // cannot see prev/next links into applications they cannot open.
    clearReviewQueueNav()

    // Best-effort server logout (blacklist refresh + clear Django session). JWT-only — MQ-008.
    // Do not await: a hung network must not block redirect to Login.
    if (!access && !refresh) return
    axios
      .post(
        `${API_BASE_URL}/api/accounts/logout/`,
        refresh ? { refresh } : {},
        {
          withCredentials: true,
          timeout: 10000,
          headers: access ? { Authorization: `Bearer ${access}` } : {},
        },
      )
      .catch((err) => {
        console.warn('Logout endpoint error:', err)
      })
  }

  let refreshInFlight = null

  async function refreshAccessToken() {
    if (refreshInFlight) {
      return refreshInFlight
    }

    refreshInFlight = (async () => {
      if (!refreshToken.value) {
        throw new Error('No refresh token available')
      }

      try {
        const response = await axios.post(`${API_BASE_URL}/api/token/refresh/`, {
          refresh: refreshToken.value,
        })

        accessToken.value = response.data.access
        persistToken(ACCESS_TOKEN_KEYS, accessToken.value)
        if (response.data.refresh) {
          refreshToken.value = response.data.refresh
          persistToken(REFRESH_TOKEN_KEYS, response.data.refresh)
        }

        return accessToken.value
      } catch (err) {
        console.error('Token refresh error:', err)
        await logout()
        throw err
      }
    })().finally(() => {
      refreshInFlight = null
    })

    return refreshInFlight
  }

  async function fetchUserProfile() {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/accounts/profile/`, {
        headers: {
          Authorization: `Bearer ${accessToken.value}`,
        },
      })

      // Profile API returns profile with nested user data
      // Transform to flat structure for easier use
      const profileData = response.data
      user.value = {
        id: profileData.id,
        email: profileData.email,
        first_name: profileData.first_name,
        middle_name: profileData.middle_name,
        last_name: profileData.last_name,
        mothers_last_name: profileData.mothers_last_name,
        full_name: profileData.full_name,
        role: profileData.role,
        username: profileData.username,
        is_admin: typeof profileData.is_admin === 'boolean' ? profileData.is_admin : undefined,
        is_staff: Boolean(profileData.is_staff),
        is_superuser: Boolean(profileData.is_superuser),
        // Add other profile fields
        secondary_email: profileData.secondary_email,
        gpa: profileData.gpa,
        grade_scale: profileData.grade_scale,
        language: profileData.language,
        language_level: profileData.language_level,
        is_ready_to_apply: Boolean(profileData.is_ready_to_apply),
      }
      
      return user.value
    } catch (err) {
      console.error('Fetch user profile error:', err)
      error.value = 'Failed to fetch user profile'
      throw err
    }
  }

  async function checkAuth() {
    if (accessToken.value && !user.value) {
      try {
        await fetchUserProfile()
      } catch (err) {
        // If profile fetch fails, try to refresh token
        try {
          await refreshAccessToken()
          await fetchUserProfile()
        } catch (refreshErr) {
          // Both failed - clear auth
          await logout()
        }
      }
    }
  }

  return {
    // State
    user,
    accessToken,
    refreshToken,
    isLoading,
    error,
    errorCode,
    fieldErrors,
    // Getters
    isAuthenticated,
    userRole,
    userName,
    isAdmin,
    isCoordinator,
    isPartner,
    canUseStaffReviewQueue,
    canUsePartnerPortal,
    // Actions
    login,
    register,
    requestPasswordReset,
    confirmPasswordReset,
    verifyEmail,
    resendVerificationEmail,
    logout,
    refreshToken: refreshAccessToken,
    fetchUserProfile,
    checkAuth,
  }
})
