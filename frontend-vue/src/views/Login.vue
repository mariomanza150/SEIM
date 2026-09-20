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
      class="alert"
      :class="showResendVerification ? 'alert-warning' : 'alert-danger'"
      role="alert"
      aria-live="assertive"
    >
      <div>{{ error }}</div>
      <div v-if="showResendVerification" class="mt-3">
        <button
          type="button"
          class="btn btn-outline-primary btn-sm"
          data-testid="login-resend-verification"
          :disabled="resendDisabled"
          @click="handleResendVerification"
        >
          <span v-if="isResending">
            <span
              class="spinner-border spinner-border-sm me-2"
              role="status"
              aria-hidden="true"
            ></span>
            {{ t('login.resending') }}
          </span>
          <span v-else-if="cooldownSeconds > 0">
            {{ t('login.resendWaitIn', { seconds: cooldownSeconds }) }}
          </span>
          <span v-else>{{ t('login.resendVerification') }}</span>
        </button>
      </div>
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
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'

const RESEND_COOLDOWN_SECONDS = 300
const COOLDOWN_STORAGE_PREFIX = 'seim_resend_verification_until:'

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
const errorCode = ref(null)
const isResending = ref(false)
const cooldownSeconds = ref(0)
let cooldownTimer = null

const showResendVerification = computed(() => {
  if (errorCode.value === 'email_not_verified') return true
  const msg = (error.value || '').toLowerCase()
  return msg.includes('not verified')
})

const resendDisabled = computed(
  () => isResending.value || cooldownSeconds.value > 0 || !email.value.trim(),
)

function cooldownStorageKey(addr) {
  return `${COOLDOWN_STORAGE_PREFIX}${addr.trim().toLowerCase()}`
}

function clearCooldownTimer() {
  if (cooldownTimer != null) {
    clearInterval(cooldownTimer)
    cooldownTimer = null
  }
}

function tickCooldown() {
  const addr = email.value.trim()
  if (!addr) {
    cooldownSeconds.value = 0
    clearCooldownTimer()
    return
  }
  const untilRaw = sessionStorage.getItem(cooldownStorageKey(addr))
  const until = untilRaw ? Number.parseInt(untilRaw, 10) : 0
  const remaining = Number.isFinite(until)
    ? Math.max(0, Math.ceil((until - Date.now()) / 1000))
    : 0
  cooldownSeconds.value = remaining
  if (remaining <= 0) {
    sessionStorage.removeItem(cooldownStorageKey(addr))
    clearCooldownTimer()
  }
}

function startCooldown(seconds) {
  const addr = email.value.trim()
  if (!addr || !seconds || seconds <= 0) return
  const until = Date.now() + seconds * 1000
  sessionStorage.setItem(cooldownStorageKey(addr), String(until))
  clearCooldownTimer()
  tickCooldown()
  cooldownTimer = setInterval(tickCooldown, 1000)
}

watch(email, () => {
  tickCooldown()
})

onMounted(() => {
  tickCooldown()
  if (cooldownSeconds.value > 0) {
    cooldownTimer = setInterval(tickCooldown, 1000)
  }
})

onBeforeUnmount(() => {
  clearCooldownTimer()
})

async function handleLogin() {
  isLoading.value = true
  error.value = null
  errorCode.value = null

  try {
    const success = await authStore.login(email.value, password.value)

    if (success) {
      successToast(t('login.welcomeBack', { name: authStore.userName }))
      const redirect = route.query.redirect || { name: 'Dashboard' }
      router.push(redirect)
    } else {
      error.value = authStore.error || t('login.failedGeneric')
      errorCode.value = authStore.errorCode || null
      errorToast(error.value)
      tickCooldown()
    }
  } catch (err) {
    error.value = t('login.unexpectedError')
    errorCode.value = null
    errorToast(error.value)
    console.error('Login error:', err)
  } finally {
    isLoading.value = false
  }
}

async function handleResendVerification() {
  if (resendDisabled.value) return
  isResending.value = true
  try {
    const result = await authStore.resendVerificationEmail(email.value.trim())
    if (result.ok) {
      successToast(t('login.resendSuccess'))
      startCooldown(RESEND_COOLDOWN_SECONDS)
      return
    }
    if (result.status === 429) {
      const wait = result.retryAfter > 0 ? result.retryAfter : RESEND_COOLDOWN_SECONDS
      startCooldown(wait)
      errorToast(result.message || t('login.resendRateLimited'))
      return
    }
    errorToast(result.message || t('login.resendFailed'))
  } finally {
    isResending.value = false
  }
}
</script>
