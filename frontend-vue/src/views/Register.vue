<template>
  <div
    v-if="successMessage"
    class="alert alert-success"
    role="status"
    aria-live="polite"
    data-testid="register-success"
  >
    {{ successMessage }}
    <div class="mt-2">
      <router-link :to="{ name: 'Login' }" class="alert-link">
        {{ t('register.goToLogin') }}
      </router-link>
    </div>
  </div>

  <template v-else>
    <form @submit.prevent="handleRegister" data-testid="register-form">
      <div class="mb-3">
        <label for="email" class="form-label">{{ t('register.instituteEmailLabel') }}</label>
        <input
          type="email"
          class="form-control"
          id="email"
          v-model="email"
          name="email"
          autocomplete="email"
          required
          :disabled="isLoading"
          :placeholder="t('register.emailPlaceholder')"
          data-testid="register-email"
          :class="{ 'is-invalid': !!authStore.fieldErrors?.email }"
          :aria-invalid="!!error || !!authStore.fieldErrors?.email"
          :aria-describedby="error ? 'register-form-error' : undefined"
        />
        <div v-if="authStore.fieldErrors?.email" class="invalid-feedback d-block">
          {{ authStore.fieldErrors.email.join(' ') }}
        </div>
        <div v-if="allowedDomains.length" class="form-text">
          {{ t('register.allowedDomains', { domains: allowedDomains.join(', ') }) }}
        </div>
      </div>

      <div class="row">
        <div class="col-md-6 mb-3">
          <label for="first_name" class="form-label">{{ t('register.firstNameLabel') }}</label>
          <input
            type="text"
            class="form-control"
            id="first_name"
            v-model="firstName"
            name="first_name"
            autocomplete="given-name"
            required
            :disabled="isLoading"
            :placeholder="t('register.firstNamePlaceholder')"
            data-testid="register-first-name"
            :class="fieldClass('first_name')"
            :aria-invalid="ariaInvalid('first_name')"
            :aria-describedby="describeId('first_name')"
          />
          <div v-if="fieldErrors.first_name" :id="describeId('first_name')" class="invalid-feedback d-block">
            {{ fieldErrors.first_name }}
          </div>
        </div>
        <div class="col-md-6 mb-3">
          <label for="middle_name" class="form-label">{{ t('register.middleNameLabel') }}</label>
          <input
            type="text"
            class="form-control"
            id="middle_name"
            v-model="middleName"
            name="middle_name"
            autocomplete="additional-name"
            :disabled="isLoading"
            :placeholder="t('register.middleNamePlaceholder')"
            data-testid="register-middle-name"
          />
        </div>
        <div class="col-md-6 mb-3">
          <label for="last_name" class="form-label">{{ t('register.lastNameLabel') }}</label>
          <input
            type="text"
            class="form-control"
            id="last_name"
            v-model="lastName"
            name="last_name"
            autocomplete="family-name"
            required
            :disabled="isLoading"
            :placeholder="t('register.lastNamePlaceholder')"
            data-testid="register-last-name"
            :class="fieldClass('last_name')"
            :aria-invalid="ariaInvalid('last_name')"
            :aria-describedby="describeId('last_name')"
          />
          <div v-if="fieldErrors.last_name" :id="describeId('last_name')" class="invalid-feedback d-block">
            {{ fieldErrors.last_name }}
          </div>
        </div>
        <div class="col-md-6 mb-3">
          <label for="mothers_last_name" class="form-label">{{ t('register.mothersLastNameLabel') }}</label>
          <input
            type="text"
            class="form-control"
            id="mothers_last_name"
            v-model="mothersLastName"
            name="mothers_last_name"
            autocomplete="family-name"
            :disabled="isLoading"
            :placeholder="t('register.mothersLastNamePlaceholder')"
            data-testid="register-mothers-last-name"
          />
        </div>
      </div>

      <div class="mb-3">
        <label for="password" class="form-label">{{ t('register.passwordLabel') }}</label>
        <input
          type="password"
          class="form-control"
          id="password"
          v-model="password"
          name="password"
          autocomplete="new-password"
          required
          :disabled="isLoading"
          :placeholder="t('register.passwordPlaceholder')"
          data-testid="register-password"
          :class="{ 'is-invalid': !!authStore.fieldErrors?.password }"
        />
        <div v-if="authStore.fieldErrors?.password" class="invalid-feedback d-block">
          {{ authStore.fieldErrors.password.join(' ') }}
        </div>
      </div>

      <div class="mb-3">
        <label for="password2" class="form-label">{{ t('register.confirmPasswordLabel') }}</label>
        <input
          type="password"
          class="form-control"
          id="password2"
          v-model="password2"
          name="password2"
          autocomplete="new-password"
          required
          :disabled="isLoading"
          :placeholder="t('register.confirmPasswordPlaceholder')"
          data-testid="register-password2"
          :class="fieldClass('password2')"
          :aria-invalid="ariaInvalid('password2')"
          :aria-describedby="describeId('password2') || (error ? 'register-form-error' : undefined)"
        />
        <div v-if="fieldErrors.password2" :id="describeId('password2')" class="invalid-feedback d-block">
          {{ fieldErrors.password2 }}
        </div>
      </div>

      <div
        v-if="error"
        id="register-form-error"
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
        data-testid="register-submit"
      >
        <span v-if="isLoading">
          <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
          {{ t('register.creating') }}
        </span>
        <span v-else>{{ t('register.createAccount') }}</span>
      </button>
    </form>

    <div class="text-center mt-3">
      <router-link :to="{ name: 'Login' }" class="text-decoration-none">
        {{ t('register.haveAccount') }}
      </router-link>
    </div>
  </template>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '@/services/api'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import { useFormFields } from '@/composables/useFormFields'

const { t } = useI18n()
const authStore = useAuthStore()
const { success: successToast, error: errorToast } = useToast()
const {
  fieldErrors,
  setFieldError,
  clearFieldErrors,
  fieldClass,
  ariaInvalid,
  describeId,
} = useFormFields()

const email = ref('')
const firstName = ref('')
const middleName = ref('')
const lastName = ref('')
const mothersLastName = ref('')
const password = ref('')
const password2 = ref('')
const isLoading = ref(false)
const error = ref(null)
const successMessage = ref(null)
const allowedDomains = ref([])

function getEmailDomain(value) {
  const parts = String(value || '').trim().toLowerCase().split('@')
  return parts.length === 2 ? parts[1] : ''
}

async function fetchAllowedDomains() {
  try {
    const { data } = await api.get('/api/accounts/catalogs/allowed-email-domains/')
    const rows = data.results || data
    allowedDomains.value = (Array.isArray(rows) ? rows : [])
      .map((row) => String(row.domain || row.name || '').trim().toLowerCase())
      .filter(Boolean)
  } catch {
    allowedDomains.value = []
  }
}

async function handleRegister() {
  isLoading.value = true
  error.value = null
  successMessage.value = null
  clearFieldErrors()

  if (!firstName.value.trim()) {
    setFieldError('first_name', t('common.fieldRequired'))
  }
  if (!lastName.value.trim()) {
    setFieldError('last_name', t('common.fieldRequired'))
  }
  if (password.value !== password2.value) {
    setFieldError('password2', t('register.passwordMismatch'))
  }
  if (Object.keys(fieldErrors.value).length) {
    isLoading.value = false
    return
  }

  const domain = getEmailDomain(email.value)
  if (allowedDomains.value.length && !allowedDomains.value.includes(domain)) {
    error.value = t('register.invalidInstituteDomain', {
      domains: allowedDomains.value.join(', '),
    })
    isLoading.value = false
    return
  }

  try {
    const ok = await authStore.register({
      email: email.value,
      password: password.value,
      password2: password2.value,
      first_name: firstName.value,
      middle_name: middleName.value,
      last_name: lastName.value,
      mothers_last_name: mothersLastName.value,
    })

    if (ok) {
      successMessage.value = t('register.success')
      successToast(successMessage.value)
    } else {
      error.value = authStore.error || t('register.failedGeneric')
    }
  } catch (err) {
    error.value = t('register.unexpectedError')
    errorToast(error.value)
    console.error('Registration error:', err)
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchAllowedDomains)
</script>
