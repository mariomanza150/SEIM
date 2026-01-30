/**
 * Auth Store - Pinia store for authentication state
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const accessToken = ref(localStorage.getItem('access_token') || null)
  const refreshToken = ref(localStorage.getItem('refresh_token') || null)
  const isLoading = ref(false)
  const error = ref(null)

  // Getters
  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)
  const userRole = computed(() => user.value?.role || null)
  const userName = computed(() => {
    if (!user.value) return ''
    return user.value.full_name || user.value.email || 'User'
  })

  // Actions
  async function login(email, password) {
    isLoading.value = true
    error.value = null

    try {
      // Get JWT tokens from Django
      const response = await axios.post(`${API_BASE_URL}/api/token/`, {
        email,
        password,
      })

      accessToken.value = response.data.access
      refreshToken.value = response.data.refresh

      // Save tokens to localStorage
      localStorage.setItem('access_token', accessToken.value)
      localStorage.setItem('refresh_token', refreshToken.value)

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
    // Clear tokens
    accessToken.value = null
    refreshToken.value = null
    user.value = null

    // Clear localStorage
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')

    // Optional: Call Django logout endpoint to invalidate session
    try {
      await axios.post(`${API_BASE_URL}/api/accounts/logout/`)
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
      localStorage.setItem('access_token', accessToken.value)

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

      user.value = response.data
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
    // Actions
    login,
    logout,
    refreshToken: refreshAccessToken,
    fetchUserProfile,
    checkAuth,
  }
})
