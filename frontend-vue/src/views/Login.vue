<template>
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

    <div class="text-center mt-3">
      <router-link
        :to="{ name: 'PasswordReset' }"
        class="text-decoration-none"
        data-testid="login-forgot-password"
      >
        {{ t('login.forgotPassword') }}
      </router-link>
    </div>
    <div class="text-center mt-2">
      <router-link
        :to="{ name: 'Register' }"
        class="text-decoration-none"
        data-testid="login-create-account"
      >
        {{ t('login.createAccount') }}
      </router-link>
    </div>
  </form>
</template>

<script setup>
import { ref } from 'vue'
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

async function handleLogin() {
  isLoading.value = true
  error.value = null

  try {
    const success = await authStore.login(email.value, password.value)

    if (success) {
      successToast(t('login.welcomeBack', { name: authStore.userName }))
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
