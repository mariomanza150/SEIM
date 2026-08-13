<template>
  <div class="login-container">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-6 col-lg-4">
          <div class="card shadow-sm">
            <div class="card-body p-4">
              <div class="text-center mb-4">
                <h1 class="h3 mb-3 fw-normal">SEIM</h1>
                <p class="text-muted">{{ t('passwordReset.subtitle') }}</p>
              </div>

              <div
                v-if="successMessage"
                class="alert alert-success"
                role="status"
                aria-live="polite"
                data-testid="password-reset-success"
              >
                {{ successMessage }}
                <div class="mt-2">
                  <router-link :to="{ name: 'Login' }" class="alert-link">
                    {{ t('passwordReset.backToLogin') }}
                  </router-link>
                </div>
              </div>

              <form
                v-else
                @submit.prevent="handleSubmit"
                data-testid="password-reset-form"
              >
                <div class="mb-3">
                  <label for="email" class="form-label">{{ t('passwordReset.emailLabel') }}</label>
                  <input
                    type="email"
                    class="form-control"
                    id="email"
                    v-model="email"
                    name="email"
                    autocomplete="email"
                    required
                    :disabled="isLoading"
                    :placeholder="t('passwordReset.emailPlaceholder')"
                    data-testid="password-reset-email"
                    :aria-invalid="!!error"
                    :aria-describedby="error ? 'password-reset-form-error' : 'password-reset-help'"
                  />
                  <div id="password-reset-help" class="form-text">{{ t('passwordReset.helpText') }}</div>
                </div>

                <div
                  v-if="error"
                  id="password-reset-form-error"
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
                  data-testid="password-reset-submit"
                >
                  <span v-if="isLoading">
                    <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    {{ t('passwordReset.submitting') }}
                  </span>
                  <span v-else>{{ t('passwordReset.submit') }}</span>
                </button>
              </form>

              <div class="text-center mt-3">
                <router-link :to="{ name: 'Login' }" class="text-decoration-none">
                  {{ t('passwordReset.backToLogin') }}
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'

const { t } = useI18n()
const authStore = useAuthStore()
const { success: successToast, error: errorToast } = useToast()

const email = ref('')
const isLoading = ref(false)
const error = ref(null)
const successMessage = ref(null)

async function handleSubmit() {
  isLoading.value = true
  error.value = null
  successMessage.value = null

  try {
    const ok = await authStore.requestPasswordReset(email.value)
    if (ok) {
      successMessage.value = t('passwordReset.success')
      successToast(successMessage.value)
    } else {
      error.value = authStore.error || t('passwordReset.failedGeneric')
      errorToast(error.value)
    }
  } catch (err) {
    error.value = t('passwordReset.unexpectedError')
    errorToast(error.value)
    console.error('Password reset request error:', err)
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
