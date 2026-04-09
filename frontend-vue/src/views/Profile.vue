<template>
  <div class="profile-page">
    <div class="container-fluid mt-4">
      <nav :aria-label="t('profilePage.breadcrumbAria')">
        <ol class="breadcrumb">
          <li class="breadcrumb-item">
            <router-link :to="{ name: 'Dashboard' }">{{ t('route.names.Dashboard') }}</router-link>
          </li>
          <li class="breadcrumb-item active">{{ t('route.names.Profile') }}</li>
        </ol>
      </nav>

      <div class="row mb-4">
        <div class="col-md-8">
          <h2 data-testid="profile-page-heading">
            <i class="bi bi-person-gear me-2"></i>{{ t('route.names.Profile') }}
          </h2>
          <p class="text-muted">{{ t('profilePage.pageSubtitle') }}</p>
        </div>
      </div>

      <div v-if="loading" class="text-center py-5">
        <div
          class="spinner-border text-primary"
          role="status"
          :aria-label="t('documentsPage.loadingSpinner')"
        ></div>
        <p class="mt-3 text-muted">{{ t('profilePage.loadingProfile') }}</p>
      </div>

      <div v-else class="row">
        <div class="col-lg-8">
          <div class="card">
            <div class="card-body">
              <form @submit.prevent="handleSubmit">
                <h6 class="text-muted mb-3">{{ t('profilePage.accountSection') }}</h6>
                <div class="row mb-3">
                  <div class="col-md-6">
                    <label class="form-label">{{ t('profilePage.firstName') }}</label>
                    <input v-model="form.first_name" type="text" class="form-control" />
                  </div>
                  <div class="col-md-6">
                    <label class="form-label">{{ t('profilePage.lastName') }}</label>
                    <input v-model="form.last_name" type="text" class="form-control" />
                  </div>
                </div>
                <div class="mb-3">
                  <label class="form-label">{{ t('login.emailLabel') }}</label>
                  <input v-model="form.email" type="email" class="form-control" />
                </div>

                <hr class="my-4" />
                <h6 class="text-muted mb-3">{{ t('profilePage.eligibilitySection') }}</h6>
                <p class="small text-muted mb-3">
                  {{ t('profilePage.eligibilityIntro') }}
                </p>
                <div class="row mb-3">
                  <div class="col-md-6">
                    <label class="form-label">{{ t('profilePage.gpaLabel') }}</label>
                    <input
                      v-model.number="form.gpa"
                      type="number"
                      step="0.01"
                      min="0"
                      max="4"
                      class="form-control"
                      :placeholder="t('applicationFormPage.gpaPlaceholder')"
                    />
                    <div class="form-text">{{ t('profilePage.gpaScaleHelp') }}</div>
                  </div>
                </div>
                <div class="row mb-3">
                  <div class="col-md-6">
                    <label class="form-label">{{ t('profilePage.primaryLanguage') }}</label>
                    <input
                      v-model="form.language"
                      type="text"
                      class="form-control"
                      :placeholder="t('applicationFormPage.languagePlaceholder')"
                    />
                    <div class="form-text">{{ t('profilePage.primaryLanguageHelp') }}</div>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label">{{ t('profilePage.primaryLevelLabel') }}</label>
                    <select v-model="form.language_level" class="form-select">
                      <option value="">{{ t('profilePage.notSetOption') }}</option>
                      <option value="A1">{{ t('profilePage.cefrA1') }}</option>
                      <option value="A2">{{ t('profilePage.cefrA2') }}</option>
                      <option value="B1">{{ t('profilePage.cefrB1') }}</option>
                      <option value="B2">{{ t('profilePage.cefrB2') }}</option>
                      <option value="C1">{{ t('profilePage.cefrC1') }}</option>
                      <option value="C2">{{ t('profilePage.cefrC2') }}</option>
                    </select>
                    <div class="form-text">{{ t('profilePage.primaryLevelHelp') }}</div>
                  </div>
                </div>

                <div class="mb-3">
                  <div class="d-flex align-items-center justify-content-between mb-2">
                    <label class="form-label mb-0">{{ t('profilePage.additionalLanguages') }}</label>
                    <button
                      type="button"
                      class="btn btn-sm btn-outline-secondary"
                      :aria-label="t('profilePage.addLanguage')"
                      @click="addLanguageRow"
                    >
                      <i class="bi bi-plus-lg me-1" aria-hidden="true"></i>{{ t('profilePage.addLanguage') }}
                    </button>
                  </div>
                  <p class="small text-muted mb-2">{{ t('profilePage.additionalLanguagesHint') }}</p>
                  <div v-if="!form.additional_languages.length" class="text-muted small fst-italic">
                    {{ t('profilePage.noneYet') }}
                  </div>
                  <div v-for="(row, idx) in form.additional_languages" :key="idx" class="row g-2 mb-2 align-items-end">
                    <div class="col-md-5">
                      <label class="form-label small mb-0">{{ t('applicationFormPage.language') }}</label>
                      <input
                        v-model="row.name"
                        type="text"
                        class="form-control form-control-sm"
                        :placeholder="t('applicationFormPage.languagePlaceholder')"
                      />
                    </div>
                    <div class="col-md-5">
                      <label class="form-label small mb-0">{{ t('profilePage.levelCefrShort') }}</label>
                      <select v-model="row.level" class="form-select form-select-sm">
                        <option value="">{{ t('profilePage.notSetOption') }}</option>
                        <option value="A1">A1</option>
                        <option value="A2">A2</option>
                        <option value="B1">B1</option>
                        <option value="B2">B2</option>
                        <option value="C1">C1</option>
                        <option value="C2">C2</option>
                      </select>
                    </div>
                    <div class="col-md-2">
                      <button
                        type="button"
                        class="btn btn-sm btn-outline-danger w-100"
                        @click="removeLanguageRow(idx)"
                      >
                        {{ t('profilePage.remove') }}
                      </button>
                    </div>
                  </div>
                </div>

                <div v-if="saveError" class="alert alert-danger">{{ saveError }}</div>
                <div class="d-flex justify-content-between mt-4">
                  <router-link :to="{ name: 'Dashboard' }" class="btn btn-outline-secondary">{{
                    t('applicationFormPage.cancel')
                  }}</router-link>
                  <button type="submit" class="btn btn-primary" :disabled="saving">
                    <span v-if="saving"
                      ><span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span
                      >{{ t('profilePage.saving') }}</span
                    >
                    <span v-else
                      ><i class="bi bi-check-circle me-2" aria-hidden="true"></i>{{ t('profilePage.saveProfile') }}</span
                    >
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
        <div class="col-lg-4">
          <div class="card">
            <div class="card-header">
              <h6 class="mb-0"><i class="bi bi-info-circle me-2" aria-hidden="true"></i>{{ t('profilePage.tipTitle') }}</h6>
            </div>
            <div class="card-body small">
              <p class="mb-0">
                {{ t('profilePage.tipBody') }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useToast } from '@/composables/useToast'
import api from '@/services/api'

const { t } = useI18n()
const { success, error: errorToast } = useToast()
const loading = ref(true)
const saving = ref(false)
const saveError = ref('')

const form = ref({
  first_name: '',
  last_name: '',
  email: '',
  gpa: null,
  language: '',
  language_level: '',
  additional_languages: [],
})

function addLanguageRow() {
  if (form.value.additional_languages.length >= 20) return
  form.value.additional_languages.push({ name: '', level: '' })
}

function removeLanguageRow(idx) {
  form.value.additional_languages.splice(idx, 1)
}

function normalizedAdditionalLanguages() {
  return form.value.additional_languages
    .map((r) => ({ name: (r.name || '').trim(), level: (r.level || '').trim() }))
    .filter((r) => r.name)
}

async function fetchProfile() {
  try {
    const { data } = await api.get('/api/accounts/profile/')
    const extras = Array.isArray(data.additional_languages)
      ? data.additional_languages.map((r) => ({
          name: r?.name ?? '',
          level: r?.level ?? '',
        }))
      : []
    form.value = {
      first_name: data.first_name ?? '',
      last_name: data.last_name ?? '',
      email: data.email ?? '',
      gpa: data.gpa ?? null,
      language: data.language ?? '',
      language_level: data.language_level ?? '',
      additional_languages: extras,
    }
  } catch (err) {
    console.error('Failed to fetch profile:', err)
    errorToast(t('profilePage.toastLoadError'))
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  saveError.value = ''
  saving.value = true
  try {
    await api.patch('/api/accounts/profile/', {
      first_name: form.value.first_name,
      last_name: form.value.last_name,
      email: form.value.email,
      gpa: form.value.gpa || null,
      language: form.value.language || null,
      language_level: form.value.language_level || null,
      additional_languages: normalizedAdditionalLanguages(),
    })
    success(t('profilePage.toastSaved'))
  } catch (err) {
    const msg =
      err.response?.data?.detail ||
      err.response?.data?.email?.[0] ||
      err.response?.data?.first_name?.[0] ||
      t('profilePage.saveFailedGeneric')
    saveError.value = typeof msg === 'string' ? msg : JSON.stringify(msg)
    errorToast(t('profilePage.toastSaveError'))
  } finally {
    saving.value = false
  }
}

onMounted(fetchProfile)
</script>

<style scoped>
.profile-page { min-height: 100vh; background-color: #f8f9fa; }
.card { border: none; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05); }
</style>
