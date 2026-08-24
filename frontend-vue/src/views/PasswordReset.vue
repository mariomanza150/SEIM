<template>
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

  <template v-else>
    <form @submit.prevent="handleSubmit" data-testid="password-reset-form">
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
  </template>
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
