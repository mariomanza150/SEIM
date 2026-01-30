<template>
  <div class="login-container">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-6 col-lg-4">
          <div class="card shadow-sm">
            <div class="card-body p-4">
              <div class="text-center mb-4">
                <h1 class="h3 mb-3 fw-normal">SEIM</h1>
                <p class="text-muted">Sign in to continue</p>
              </div>

              <form @submit.prevent="handleLogin">
                <div class="mb-3">
                  <label for="email" class="form-label">Email address</label>
                  <input
                    type="email"
                    class="form-control"
                    id="email"
                    v-model="email"
                    required
                    :disabled="isLoading"
                    placeholder="Enter your email"
                  />
                </div>

                <div class="mb-3">
                  <label for="password" class="form-label">Password</label>
                  <input
                    type="password"
                    class="form-control"
                    id="password"
                    v-model="password"
                    required
                    :disabled="isLoading"
                    placeholder="Enter your password"
                  />
                </div>

                <div class="mb-3 form-check">
                  <input
                    type="checkbox"
                    class="form-check-input"
                    id="remember"
                    v-model="rememberMe"
                  />
                  <label class="form-check-label" for="remember">
                    Remember me
                  </label>
                </div>

                <div v-if="error" class="alert alert-danger" role="alert">
                  {{ error }}
                </div>

                <button
                  type="submit"
                  class="btn btn-primary w-100"
                  :disabled="isLoading"
                >
                  <span v-if="isLoading">
                    <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Signing in...
                  </span>
                  <span v-else>Sign In</span>
                </button>
              </form>

              <div class="text-center mt-3">
                <a href="#" class="text-decoration-none">Forgot password?</a>
              </div>
            </div>
          </div>

          <div class="text-center mt-3 text-muted small">
            <p>SEIM Vue.js v{{ appVersion }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const { success: successToast, error: errorToast } = useToast()

const email = ref('')
const password = ref('')
const rememberMe = ref(false)
const isLoading = ref(false)
const error = ref(null)
const appVersion = import.meta.env.VITE_APP_VERSION || '2.0.0'

async function handleLogin() {
  isLoading.value = true
  error.value = null

  try {
    const success = await authStore.login(email.value, password.value)

    if (success) {
      successToast(`Welcome back, ${authStore.userName}!`)
      // Redirect to original destination or dashboard
      const redirect = route.query.redirect || '/dashboard'
      router.push(redirect)
    } else {
      error.value = authStore.error || 'Login failed. Please try again.'
      errorToast(error.value)
    }
  } catch (err) {
    error.value = 'An unexpected error occurred. Please try again.'
    errorToast(error.value)
    console.error('Login error:', err)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.card {
  border: none;
  border-radius: 1rem;
}

.form-control:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
}

.btn-primary {
  background-color: #667eea;
  border-color: #667eea;
}

.btn-primary:hover {
  background-color: #5568d3;
  border-color: #5568d3;
}

.btn-primary:disabled {
  background-color: #667eea;
  border-color: #667eea;
  opacity: 0.7;
}
</style>
