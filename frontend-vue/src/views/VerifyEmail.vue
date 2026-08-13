<template>
  <div class="login-container">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-6 col-lg-4">
          <div class="card shadow-sm">
            <div class="card-body p-4 text-center">
              <h1 class="h3 mb-3 fw-normal">SEIM</h1>
              <p class="text-muted mb-4">{{ t('verifyEmail.subtitle') }}</p>

              <div
                v-if="status === 'loading'"
                class="alert alert-info"
                role="status"
                aria-live="polite"
                data-testid="verify-email-loading"
              >
                <span
                  class="spinner-border spinner-border-sm me-2"
                  role="status"
                  aria-hidden="true"
                ></span>
                {{ t('verifyEmail.verifying') }}
              </div>

              <div
                v-else-if="status === 'success'"
                class="alert alert-success"
                role="status"
                aria-live="polite"
                data-testid="verify-email-success"
              >
                {{ t('verifyEmail.success') }}
                <div class="mt-3">
                  <router-link :to="{ name: 'Login' }" class="btn btn-primary">
                    {{ t('verifyEmail.goToLogin') }}
                  </router-link>
                </div>
              </div>

              <div
                v-else
                class="alert alert-danger"
                role="alert"
                aria-live="assertive"
                data-testid="verify-email-error"
              >
                {{ errorMessage }}
                <div class="mt-3">
                  <router-link :to="{ name: 'Login' }" class="alert-link">
                    {{ t('verifyEmail.goToLogin') }}
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'

const { t } = useI18n()
const route = useRoute()
const authStore = useAuthStore()

const status = ref('loading')
const errorMessage = ref('')

onMounted(async () => {
  const token = typeof route.query.token === 'string' ? route.query.token.trim() : ''
  if (!token) {
    status.value = 'error'
    errorMessage.value = t('verifyEmail.missingToken')
    return
  }

  const ok = await authStore.verifyEmail(token)
  if (ok) {
    status.value = 'success'
  } else {
    status.value = 'error'
    errorMessage.value = authStore.error || t('verifyEmail.failedGeneric')
  }
})
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

.btn-primary {
  background-color: #667eea;
  border-color: #667eea;
}

.btn-primary:hover {
  background-color: #5568d3;
  border-color: #5568d3;
}
</style>
