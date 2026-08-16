<template>
  <div class="profile-page">
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
      <div class="spinner-border text-primary" role="status" :aria-label="t('profilePage.loadingSpinner')"></div>
      <p class="mt-3 text-muted">{{ t('profilePage.loadingProfile') }}</p>
    </div>

    <div v-else class="row">
      <div class="col-lg-9">
        <div
          class="alert"
          :class="isReadyToApply ? 'alert-success' : 'alert-warning'"
          data-testid="profile-readiness"
        >
          <i class="bi me-2" :class="isReadyToApply ? 'bi-check-circle' : 'bi-exclamation-triangle'"></i>
          {{ isReadyToApply ? t('profilePage.readyToApply') : t('profilePage.completeRequired') }}
        </div>

        <form @submit.prevent="handleSubmit">
          <section class="card mb-4" data-testid="profile-account-section">
            <div class="card-header"><h5 class="mb-0">{{ t('profilePage.accountSection') }}</h5></div>
            <div class="card-body">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label" for="profile-email">{{ t('profilePage.instituteEmail') }}</label>
                  <input id="profile-email" v-model="form.email" type="email" class="form-control" autocomplete="email" readonly data-testid="profile-email">
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="profile-matricula">{{ t('profilePage.matricula') }} *</label>
                  <input id="profile-matricula" v-model="form.matricula" type="text" inputmode="numeric" pattern="[0-9]+" class="form-control" required>
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="profile-first-name">{{ t('profilePage.firstName') }} *</label>
                  <input id="profile-first-name" v-model="form.first_name" type="text" class="form-control" name="given-name" autocomplete="given-name" required data-testid="profile-first-name">
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="profile-middle-name">{{ t('profilePage.middleName') }} *</label>
                  <input id="profile-middle-name" v-model="form.middle_name" type="text" class="form-control" autocomplete="additional-name" required data-testid="profile-middle-name">
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="profile-last-name">{{ t('profilePage.lastName') }} *</label>
                  <input id="profile-last-name" v-model="form.last_name" type="text" class="form-control" name="family-name" autocomplete="family-name" required data-testid="profile-last-name">
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="profile-mothers-last-name">{{ t('profilePage.mothersLastName') }} *</label>
                  <input id="profile-mothers-last-name" v-model="form.mothers_last_name" type="text" class="form-control" autocomplete="family-name" required>
                </div>
              </div>
            </div>
          </section>

          <section class="card mb-4" data-testid="profile-personal-section">
            <div class="card-header"><h5 class="mb-0">{{ t('profilePage.personalSection') }}</h5></div>
            <div class="card-body">
              <div class="row g-3">
                <div class="col-md-4">
                  <label class="form-label" for="profile-gender">{{ t('profilePage.gender') }} *</label>
                  <select id="profile-gender" v-model="form.gender" class="form-select" required>
                    <option value="">{{ t('profilePage.selectOption') }}</option>
                    <option value="female">{{ t('profilePage.genderFemale') }}</option>
                    <option value="male">{{ t('profilePage.genderMale') }}</option>
                    <option value="non_binary">{{ t('profilePage.genderNonBinary') }}</option>
                    <option value="other">{{ t('profilePage.genderOther') }}</option>
                    <option value="prefer_not_to_say">{{ t('profilePage.genderPreferNot') }}</option>
                  </select>
                </div>
                <div class="col-md-4">
                  <label class="form-label" for="profile-dob">{{ t('profilePage.dateOfBirth') }} *</label>
                  <input id="profile-dob" v-model="form.date_of_birth" type="date" class="form-control" required>
                </div>
                <div class="col-md-4">
                  <label class="form-label" for="profile-birthplace">{{ t('profilePage.birthplace') }} *</label>
                  <input id="profile-birthplace" v-model="form.birthplace" type="text" class="form-control" required>
                </div>
                <div class="col-md-4">
                  <label class="form-label" for="profile-postal-code">{{ t('profilePage.postalCode') }} *</label>
                  <input id="profile-postal-code" v-model="form.postal_code" type="text" class="form-control" autocomplete="postal-code" required>
                </div>
                <div class="col-md-4">
                  <label class="form-label" for="profile-passport">{{ t('profilePage.passportNumber') }} *</label>
                  <input id="profile-passport" v-model="form.passport_number" type="text" class="form-control" required>
                </div>
                <div class="col-md-4">
                  <label class="form-label" for="profile-mobile">{{ t('profilePage.mobilePhone') }} *</label>
                  <input id="profile-mobile" v-model="form.mobile_phone" type="tel" class="form-control" autocomplete="tel" required>
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="profile-secondary-email">{{ t('profilePage.secondaryEmail') }} *</label>
                  <input id="profile-secondary-email" v-model="form.secondary_email" type="email" class="form-control" autocomplete="email" required>
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="profile-rfc">{{ t('profilePage.rfc') }} *</label>
                  <input id="profile-rfc" v-model="form.rfc" type="text" class="form-control text-uppercase" required>
                </div>
              </div>
            </div>
          </section>

          <section class="card mb-4" data-testid="profile-academic-section">
            <div class="card-header"><h5 class="mb-0">{{ t('profilePage.academicSection') }}</h5></div>
            <div class="card-body">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label" for="profile-academic-level">{{ t('profilePage.academicLevel') }} *</label>
                  <select id="profile-academic-level" v-model="form.academic_level" class="form-select" required data-testid="profile-academic-level">
                    <option value="">{{ t('profilePage.selectOption') }}</option>
                    <option v-for="item in catalogs.academicLevels" :key="item.id" :value="item.id">{{ item.name }}</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="profile-school">{{ t('profilePage.school') }} *</label>
                  <select id="profile-school" v-model="form.school" class="form-select" required data-testid="profile-school">
                    <option value="">{{ t('profilePage.selectOption') }}</option>
                    <option v-for="item in catalogs.schools" :key="item.id" :value="item.id">{{ item.name }}</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="profile-program">{{ t('profilePage.homeProgram') }} *</label>
                  <select id="profile-program" v-model="form.home_academic_program" class="form-select" :disabled="!form.school || programsLoading" required data-testid="profile-program">
                    <option value="">{{ programsLoading ? t('profilePage.loadingPrograms') : t('profilePage.selectOption') }}</option>
                    <option v-for="item in catalogs.programs" :key="item.id" :value="item.id">{{ item.name }}</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="profile-unidad">{{ t('profilePage.unidad') }} *</label>
                  <select id="profile-unidad" v-model="form.unidad" class="form-select" required data-testid="profile-unidad">
                    <option value="">{{ t('profilePage.selectOption') }}</option>
                    <option v-for="item in catalogs.unidades" :key="item.id" :value="item.id">{{ item.name }}</option>
                  </select>
                </div>
              </div>
            </div>
          </section>

          <section class="card mb-4" data-testid="profile-banking-section">
            <div class="card-header">
              <h5 class="mb-0">{{ t('profilePage.bankingSection') }} <span class="small text-muted">({{ t('profilePage.optional') }})</span></h5>
            </div>
            <div class="card-body">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label" for="profile-bank">{{ t('profilePage.bank') }}</label>
                  <select id="profile-bank" v-model="form.bank_institution" class="form-select" data-testid="profile-bank">
                    <option value="">{{ t('profilePage.selectOption') }}</option>
                    <option v-for="item in catalogs.banks" :key="item.id" :value="item.id">{{ item.name }}</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="profile-clabe">{{ t('profilePage.clabe') }}</label>
                  <input id="profile-clabe" v-model="form.clabe" type="text" inputmode="numeric" pattern="[0-9]{18}" maxlength="18" class="form-control" data-testid="profile-clabe">
                </div>
              </div>
            </div>
          </section>

          <section class="card mb-4" data-testid="profile-eligibility-section">
            <div class="card-header"><h5 class="mb-0">{{ t('profilePage.eligibilitySection') }}</h5></div>
            <div class="card-body">
              <p class="small text-muted">{{ t('profilePage.eligibilityIntro') }}</p>
              <div class="row g-3 mb-3">
                <div class="col-md-6">
                  <label class="form-label" for="profile-ingress-date">{{ t('profilePage.ingressDate') }}</label>
                  <input id="profile-ingress-date" v-model="form.ingress_date" type="date" class="form-control" data-testid="profile-ingress-date">
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="profile-current-semester">{{ t('profilePage.currentSemester') }}</label>
                  <input id="profile-current-semester" v-model.number="form.current_semester" type="number" min="1" step="1" class="form-control" :placeholder="computedSemesterPlaceholder" data-testid="profile-current-semester">
                  <div class="form-text">{{ t('profilePage.currentSemesterHelp') }}</div>
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="profile-credits-percent">{{ t('profilePage.creditsApprovedPercent') }}</label>
                  <input id="profile-credits-percent" v-model.number="form.credits_approved_percent" type="number" min="0" max="100" step="0.01" class="form-control" data-testid="profile-credits-percent">
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="profile-gpa">{{ t('profilePage.gpaLabel') }}</label>
                  <input id="profile-gpa" v-model.number="form.gpa" type="number" step="0.01" min="0" class="form-control" autocomplete="off" :placeholder="t('profilePage.gpaPlaceholder')" data-testid="profile-gpa">
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="profile-grade-scale">{{ t('profilePage.gradeScale') }}</label>
                  <select id="profile-grade-scale" v-model="form.grade_scale" class="form-select">
                    <option value="">{{ t('profilePage.notSetOption') }}</option>
                    <option v-for="item in catalogs.gradeScales" :key="item.id" :value="item.id">{{ item.name }}</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="profile-language">{{ t('profilePage.primaryLanguage') }}</label>
                  <input id="profile-language" v-model="form.language" type="text" class="form-control" autocomplete="language" :placeholder="t('profilePage.languagePlaceholder')" data-testid="profile-language">
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="profile-language-level">{{ t('profilePage.primaryLevelLabel') }}</label>
                  <select id="profile-language-level" v-model="form.language_level" class="form-select" autocomplete="off" data-testid="profile-language-level">
                    <option value="">{{ t('profilePage.notSetOption') }}</option>
                    <option v-for="level in cefrLevels" :key="level" :value="level">{{ t(`profilePage.cefr${level}`) }}</option>
                  </select>
                </div>
              </div>
              <div class="d-flex justify-content-between align-items-center mb-2">
                <label class="form-label mb-0">{{ t('profilePage.additionalLanguages') }}</label>
                <button type="button" class="btn btn-sm btn-outline-secondary" @click="addLanguageRow">
                  <i class="bi bi-plus-lg me-1"></i>{{ t('profilePage.addLanguage') }}
                </button>
              </div>
              <div v-for="(row, idx) in form.additional_languages" :key="idx" class="row g-2 mb-2">
                <div class="col-md-5"><input v-model="row.name" type="text" class="form-control form-control-sm" :placeholder="t('profilePage.languagePlaceholder')"></div>
                <div class="col-md-5">
                  <select v-model="row.level" class="form-select form-select-sm">
                    <option value="">{{ t('profilePage.notSetOption') }}</option>
                    <option v-for="level in cefrLevels" :key="level" :value="level">{{ level }}</option>
                  </select>
                </div>
                <div class="col-md-2">
                  <button type="button" class="btn btn-sm btn-outline-danger w-100" @click="removeLanguageRow(idx)">{{ t('profilePage.remove') }}</button>
                </div>
              </div>
            </div>
          </section>

          <div v-if="saveError" class="alert alert-danger" role="alert">{{ saveError }}</div>
          <div class="d-flex justify-content-between">
            <router-link :to="{ name: 'Dashboard' }" class="btn btn-outline-secondary">{{ t('profilePage.cancel') }}</router-link>
            <button type="submit" class="btn btn-primary" :disabled="saving">
              <span v-if="saving"><span class="spinner-border spinner-border-sm me-2"></span>{{ t('profilePage.saving') }}</span>
              <span v-else><i class="bi bi-check-circle me-2"></i>{{ t('profilePage.saveProfile') }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useToast } from '@/composables/useToast'
import api from '@/services/api'

const { t } = useI18n()
const { success, error: errorToast } = useToast()
const cefrLevels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
const loading = ref(true)
const saving = ref(false)
const programsLoading = ref(false)
const saveError = ref('')
const isReadyToApply = ref(false)
const catalogs = reactive({
  academicLevels: [], schools: [], unidades: [], banks: [], programs: [], gradeScales: [],
})

const emptyForm = {
  email: '', first_name: '', middle_name: '', last_name: '', mothers_last_name: '',
  matricula: '', gender: '', date_of_birth: '', birthplace: '', postal_code: '',
  passport_number: '', mobile_phone: '', secondary_email: '', rfc: '',
  academic_level: '', school: '', unidad: '', home_academic_program: '',
  bank_institution: '', clabe: '', gpa: null, grade_scale: '', language: '',
  language_level: '', additional_languages: [],
  ingress_date: '', current_semester: null, credits_approved_percent: null,
  computed_semester: null, effective_semester: null,
}
const form = ref({ ...emptyForm })

const computedSemesterPlaceholder = computed(() => {
  const computedSem = form.value.computed_semester
  if (computedSem != null) {
    return t('profilePage.computedSemesterPlaceholder', { n: computedSem })
  }
  return t('profilePage.semesterOverridePlaceholder')
})

function listFrom(data) {
  const rows = data?.results || data
  return Array.isArray(rows) ? rows : []
}

function idOf(value) {
  if (value && typeof value === 'object') return value.id ?? ''
  return value ?? ''
}

function errorMessage(data) {
  if (!data) return t('profilePage.saveFailedGeneric')
  if (typeof data === 'string') return data
  if (typeof data.detail === 'string') return data.detail
  const first = Object.values(data).flat(Infinity).find((value) => typeof value === 'string')
  return first || t('profilePage.saveFailedGeneric')
}

async function fetchCatalog(path) {
  const { data } = await api.get(`/api/accounts/catalogs/${path}/`)
  return listFrom(data)
}

async function fetchPrograms(schoolId, clearSelection = true) {
  if (clearSelection) form.value.home_academic_program = ''
  catalogs.programs = []
  if (!schoolId) return
  programsLoading.value = true
  try {
    const { data } = await api.get('/api/accounts/catalogs/programs/', { params: { school: schoolId } })
    catalogs.programs = listFrom(data)
  } catch {
    errorToast(t('profilePage.toastCatalogError'))
  } finally {
    programsLoading.value = false
  }
}

async function fetchProfileAndCatalogs() {
  try {
    const [profileResponse, academicLevels, schools, unidades, banks, gradeScaleResponse] = await Promise.all([
      api.get('/api/accounts/profile/'),
      fetchCatalog('academic-levels'),
      fetchCatalog('schools'),
      fetchCatalog('unidades'),
      fetchCatalog('banks'),
      api.get('/grades/api/scales/active/').catch(() => ({ data: [] })),
    ])
    catalogs.academicLevels = academicLevels
    catalogs.schools = schools
    catalogs.unidades = unidades
    catalogs.banks = banks
    catalogs.gradeScales = listFrom(gradeScaleResponse.data)

    const data = profileResponse.data
    form.value = {
      ...emptyForm,
      ...data,
      academic_level: idOf(data.academic_level),
      school: idOf(data.school),
      unidad: idOf(data.unidad),
      home_academic_program: idOf(data.home_academic_program),
      bank_institution: idOf(data.bank_institution),
      grade_scale: idOf(data.grade_scale),
      ingress_date: data.ingress_date || '',
      current_semester: data.current_semester ?? null,
      credits_approved_percent: data.credits_approved_percent ?? null,
      computed_semester: data.computed_semester ?? null,
      effective_semester: data.effective_semester ?? null,
      additional_languages: Array.isArray(data.additional_languages)
        ? data.additional_languages.map((row) => ({ name: row?.name || '', level: row?.level || '' }))
        : [],
    }
    isReadyToApply.value = Boolean(data.is_ready_to_apply)
    await fetchPrograms(form.value.school, false)
  } catch (err) {
    console.error('Failed to load profile:', err)
    errorToast(t('profilePage.toastLoadError'))
  } finally {
    loading.value = false
  }
}

function nullable(value) {
  return value === '' ? null : value
}

function normalizedAdditionalLanguages() {
  return form.value.additional_languages
    .map((row) => ({ name: String(row.name || '').trim(), level: String(row.level || '').trim() }))
    .filter((row) => row.name)
}

function buildPayload() {
  const payload = { ...form.value }
  delete payload.is_ready_to_apply
  delete payload.is_eligibility_complete
  delete payload.is_personal_academic_complete
  delete payload.computed_semester
  delete payload.effective_semester
  payload.academic_level = nullable(payload.academic_level)
  payload.school = nullable(payload.school)
  payload.unidad = nullable(payload.unidad)
  payload.home_academic_program = nullable(payload.home_academic_program)
  payload.bank_institution = nullable(payload.bank_institution)
  payload.grade_scale = nullable(payload.grade_scale)
  payload.gpa = nullable(payload.gpa)
  payload.language = nullable(payload.language)
  payload.language_level = nullable(payload.language_level)
  payload.secondary_email = nullable(payload.secondary_email)
  payload.ingress_date = nullable(payload.ingress_date)
  payload.current_semester = nullable(payload.current_semester)
  payload.credits_approved_percent = nullable(payload.credits_approved_percent)
  payload.additional_languages = normalizedAdditionalLanguages()
  return payload
}

async function handleSubmit() {
  saveError.value = ''
  saving.value = true
  try {
    const { data } = await api.patch('/api/accounts/profile/', buildPayload())
    isReadyToApply.value = Boolean(data.is_ready_to_apply)
    success(t('profilePage.toastSaved'))
  } catch (err) {
    saveError.value = errorMessage(err.response?.data)
    errorToast(t('profilePage.toastSaveError'))
  } finally {
    saving.value = false
  }
}

function addLanguageRow() {
  if (form.value.additional_languages.length < 20) {
    form.value.additional_languages.push({ name: '', level: '' })
  }
}

function removeLanguageRow(index) {
  form.value.additional_languages.splice(index, 1)
}

watch(() => form.value.school, (school, previous) => {
  if (!loading.value && String(school) !== String(previous)) fetchPrograms(school)
})

onMounted(fetchProfileAndCatalogs)
</script>

<style scoped>
.profile-page { min-height: 100vh; background-color: var(--seim-app-bg); }
.card { border: none; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05); }
.card-header { background: var(--bs-body-bg); border-bottom: 1px solid var(--bs-border-color); }
</style>
