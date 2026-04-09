/**
 * Auth Store - Pinia store for authentication state
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''
const ACCESS_TOKEN_KEYS = ['access_token', 'seim_access_token']
const REFRESH_TOKEN_KEYS = ['refresh_token', 'seim_refresh_token']

function getStoredToken(keys) {
  return keys.map(key => localStorage.getItem(key)).find(Boolean) || null
}

function persistToken(keys, value) {
  keys.forEach((key) => {
    if (value) {
      localStorage.setItem(key, value)
    } else {
      localStorage.removeItem(key)
    }
  })
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const accessToken = ref(getStoredToken(ACCESS_TOKEN_KEYS))
  const refreshToken = ref(getStoredToken(REFRESH_TOKEN_KEYS))
  const isLoading = ref(false)
  const error = ref(null)

  // Getters
  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)
  const userRole = computed(() => user.value?.role || null)
  const isAdmin = computed(() => user.value?.role === 'admin' || user.value?.is_staff === true)
  const isCoordinator = computed(() => user.value?.role === 'coordinator')
  const canUseStaffReviewQueue = computed(
    () => isAdmin.value || user.value?.role === 'coordinator' || user.value?.is_staff === true
  )
  const userName = computed(() => {
    if (!user.value) return ''
    return user.value.full_name || user.value.email || 'User'
  })

  // Actions
  async function login(email, password) {
    isLoading.value = true
    error.value = null

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
      error.value = err.response?.data?.detail || 'Login failed. Please check your credentials.'
      console.error('Login error:', err)
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function logout() {
    const refresh = refreshToken.value

    // Clear tokens
    accessToken.value = null
    refreshToken.value = null
    user.value = null

    persistToken(ACCESS_TOKEN_KEYS, null)
    persistToken(REFRESH_TOKEN_KEYS, null)

    // Clear both SPA and legacy token namespaces.
    try {
      await axios.post(`${API_BASE_URL}/api/accounts/logout/`, refresh ? { refresh } : {})
    } catch (err) {
      console.warn('Logout endpoint error:', err)
    }
  }

  async function refreshAccessToken() {
    if (!refreshToken.value) {
      throw new Error('No refresh token available')
    }

    try {
      const response = await axios.post(`${API_BASE_URL}/api/token/refresh/`, {
        refresh: refreshToken.value,
      })

      accessToken.value = response.data.access
      persistToken(ACCESS_TOKEN_KEYS, accessToken.value)

      return accessToken.value
    } catch (err) {
      console.error('Token refresh error:', err)
      // Refresh failed - clear everything
      await logout()
      throw err
    }
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
        last_name: profileData.last_name,
        full_name: profileData.full_name,
        role: profileData.role,
        username: profileData.username,
        // Add other profile fields
        secondary_email: profileData.secondary_email,
        gpa: profileData.gpa,
        language: profileData.language,
        language_level: profileData.language_level,
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
    // Getters
    isAuthenticated,
    userRole,
    userName,
    isAdmin,
    isCoordinator,
    canUseStaffReviewQueue,
    // Actions
    login,
    logout,
    refreshToken: refreshAccessToken,
    fetchUserProfile,
    checkAuth,
  }
})
