<template>
  <div class="login-container">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-6 col-lg-4">
          <div class="card shadow-sm">
            <div class="card-body p-4">
              <div class="text-center mb-4">
                <h1 class="h3 mb-3 fw-normal">SEIM</h1>
                <p class="text-muted">{{ t('login.subtitle') }}</p>
              </div>

              <form @submit.prevent="handleLogin" data-testid="login-form">
                <div class="mb-3">
                  <label for="email" class="form-label">{{ t('login.emailLabel') }}</label>
                  <input
                    type="email"
                    class="form-control"
                    id="email"
                    v-model="email"
                    name="username"
                    autocomplete="username"
                    required
                    :disabled="isLoading"
                    :placeholder="t('login.emailPlaceholder')"
                    data-testid="login-email"
                    :aria-invalid="!!error"
                    :aria-describedby="error ? 'login-form-error' : undefined"
                  />
                </div>

                <div class="mb-3">
                  <label for="password" class="form-label">{{ t('login.passwordLabel') }}</label>
                  <input
                    type="password"
                    class="form-control"
                    id="password"
                    v-model="password"
                    name="password"
                    autocomplete="current-password"
                    required
                    :disabled="isLoading"
                    :placeholder="t('login.passwordPlaceholder')"
                    data-testid="login-password"
                    :aria-invalid="!!error"
                    :aria-describedby="error ? 'login-form-error' : undefined"
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
                    {{ t('login.rememberMe') }}
                  </label>
                </div>

                <div
                  v-if="error"
                  id="login-form-error"
                  class="alert alert-danger"
                  role="alert"
                  aria-live="assertive"
                >
                  {{ error }}
                </div>

                <button
                  type="submit"
                  class="btn btn-primary w-100"
                  :disabled="isLoading"
                  data-testid="login-submit"
                >
                  <span v-if="isLoading">
                    <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    {{ t('login.signingIn') }}
                  </span>
                  <span v-else>{{ t('login.signIn') }}</span>
                </button>
              </form>

              <div class="text-center mt-3">
                <a href="/password-reset/" class="text-decoration-none">{{ t('login.forgotPassword') }}</a>
              </div>
            </div>
          </div>

          <div class="text-center mt-3 text-muted small">
            <p>{{ versionCaption }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { version as vueRuntimeVersion } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'

const { t } = useI18n()
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const { success: successToast, error: errorToast } = useToast()

const email = ref('')
const password = ref('')
const rememberMe = ref(false)
const isLoading = ref(false)
const error = ref(null)
/** Optional CI/build tag (e.g. git or release id). Not the Vue major version. */
const buildTag = import.meta.env.VITE_APP_VERSION || ''

const versionCaption = computed(() => {
  const vue = vueRuntimeVersion
  if (buildTag) {
    return t('login.versionLineWithBuild', { build: buildTag, vue })
  }
  return t('login.versionLine', { vue })
})

async function handleLogin() {
  isLoading.value = true
  error.value = null

  try {
    const success = await authStore.login(email.value, password.value)

    if (success) {
      successToast(t('login.welcomeBack', { name: authStore.userName }))
      // Redirect to original destination or dashboard
      const redirect = route.query.redirect || { name: 'Dashboard' }
      router.push(redirect)
    } else {
      error.value = authStore.error || t('login.failedGeneric')
      errorToast(error.value)
    }
  } catch (err) {
    error.value = t('login.unexpectedError')
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
