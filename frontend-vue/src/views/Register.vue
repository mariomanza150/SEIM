<template>
  <div class="login-container">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-6 col-lg-5">
          <div class="card shadow-sm">
            <div class="card-body p-4">
              <div class="text-center mb-4">
                <h1 class="h3 mb-3 fw-normal">SEIM</h1>
                <p class="text-muted">{{ t('register.subtitle') }}</p>
              </div>

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

              <form
                v-else
                @submit.prevent="handleRegister"
                data-testid="register-form"
              >
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
                    :aria-invalid="!!error"
                    :aria-describedby="error ? 'register-form-error' : undefined"
                  />
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
                    />
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
                    />
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
                  />
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
                  />
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
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import axios from 'axios'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'

const { t } = useI18n()
const authStore = useAuthStore()
const { success: successToast, error: errorToast } = useToast()

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
    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || ''
    const { data } = await axios.get(`${apiBaseUrl}/api/accounts/catalogs/allowed-email-domains/`)
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

  if (password.value !== password2.value) {
    error.value = t('register.passwordMismatch')
    errorToast(error.value)
    isLoading.value = false
    return
  }

  const domain = getEmailDomain(email.value)
  if (allowedDomains.value.length && !allowedDomains.value.includes(domain)) {
    error.value = t('register.invalidInstituteDomain', {
      domains: allowedDomains.value.join(', '),
    })
    errorToast(error.value)
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
      errorToast(error.value)
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
