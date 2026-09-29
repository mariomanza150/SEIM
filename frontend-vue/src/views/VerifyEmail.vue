<template>
  <div class="text-center">
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
