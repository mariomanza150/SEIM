<template>
  <div
    v-if="successMessage"
    class="alert alert-success"
    role="status"
    aria-live="polite"
    data-testid="password-reset-confirm-success"
  >
    {{ successMessage }}
    <div class="mt-3">
      <router-link :to="{ name: 'Login' }" class="btn btn-primary">
        {{ t('passwordResetConfirm.backToLogin') }}
      </router-link>
    </div>
  </div>

  <template v-else>
    <form @submit.prevent="handleSubmit" data-testid="password-reset-confirm-form">
      <p class="text-muted small">{{ t('passwordResetConfirm.helpText') }}</p>
      <div class="mb-3">
        <label for="email" class="form-label">{{ t('passwordResetConfirm.emailLabel') }}</label>
        <input
          type="email"
          class="form-control"
          id="email"
          v-model="email"
          name="email"
          autocomplete="email"
          required
          :disabled="isLoading"
          data-testid="password-reset-confirm-email"
          :aria-invalid="!!error"
          :aria-describedby="error ? 'password-reset-confirm-error' : undefined"
        />
      </div>
      <div class="mb-3">
        <label for="token" class="form-label">{{ t('passwordResetConfirm.tokenLabel') }}</label>
        <input
          type="text"
          class="form-control"
          id="token"
          v-model="token"
          name="token"
          autocomplete="off"
          required
          :disabled="isLoading"
          :placeholder="t('passwordResetConfirm.tokenPlaceholder')"
          data-testid="password-reset-confirm-token"
        />
      </div>
      <div class="mb-3">
        <label for="new_password" class="form-label">{{ t('passwordResetConfirm.newPasswordLabel') }}</label>
        <input
          type="password"
          class="form-control"
          id="new_password"
          v-model="newPassword"
          name="new-password"
          autocomplete="new-password"
          required
          :disabled="isLoading"
          data-testid="password-reset-confirm-password"
        />
      </div>
      <div class="mb-3">
        <label for="new_password2" class="form-label">{{ t('passwordResetConfirm.confirmPasswordLabel') }}</label>
        <input
          type="password"
          class="form-control"
          id="new_password2"
          v-model="newPassword2"
          name="new-password-confirm"
          autocomplete="new-password"
          required
          :disabled="isLoading"
          data-testid="password-reset-confirm-password2"
        />
      </div>

      <div
        v-if="error"
        id="password-reset-confirm-error"
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
        data-testid="password-reset-confirm-submit"
      >
        <span v-if="isLoading">
          <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
          {{ t('passwordResetConfirm.submitting') }}
        </span>
        <span v-else>{{ t('passwordResetConfirm.submit') }}</span>
      </button>
    </form>

    <div class="text-center mt-3">
      <router-link :to="{ name: 'PasswordReset' }" class="text-decoration-none">
        {{ t('passwordResetConfirm.requestNewLink') }}
      </router-link>
    </div>
  </template>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'

const { t } = useI18n()
const route = useRoute()
const authStore = useAuthStore()
const { success: successToast, error: errorToast } = useToast()

function queryString(name) {
  const value = route.query[name]
  return typeof value === 'string' ? value.trim() : ''
}

const email = ref(queryString('email'))
const token = ref(queryString('token'))
const newPassword = ref('')
const newPassword2 = ref('')
const isLoading = ref(false)
const error = ref(null)
const successMessage = ref(null)

async function handleSubmit() {
  error.value = null
  successMessage.value = null

  if (newPassword.value !== newPassword2.value) {
    error.value = t('passwordResetConfirm.passwordMismatch')
    errorToast(error.value)
    return
  }

  isLoading.value = true
  try {
    const ok = await authStore.confirmPasswordReset({
      email: email.value,
      token: token.value,
      new_password: newPassword.value,
    })
    if (ok) {
      successMessage.value = t('passwordResetConfirm.success')
      successToast(successMessage.value)
    } else {
      error.value = authStore.error || t('passwordResetConfirm.failedGeneric')
      errorToast(error.value)
    }
  } catch (err) {
    error.value = t('passwordResetConfirm.unexpectedError')
    errorToast(error.value)
    console.error('Password reset confirm error:', err)
  } finally {
    isLoading.value = false
  }
}
</script>
