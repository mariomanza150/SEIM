<template>
  <div class="profile-page">
    <PageHeader
      :title="t('route.names.Profile')"
      :subtitle="t('profilePage.pageSubtitle')"
      icon-class="bi bi-person-gear"
      test-id="profile-page-heading"
    >
      <template #breadcrumb>
        <PageBreadcrumb
          :aria-label="t('profilePage.breadcrumbAria')"
          :items="[
            { to: { name: 'Dashboard' }, label: t('route.names.Dashboard') },
            { label: t('route.names.Profile') },
          ]"
        />
      </template>
    </PageHeader>

    <PageStateShell
      :loading="loading"
      skeleton="cards"
      :loading-label="t('profilePage.loadingProfile')"
    >
    <div class="row">
      <div class="col-lg-9">
        <div
          class="alert"
          :class="isReadyToApply ? 'alert-success' : 'alert-warning'"
          data-testid="profile-readiness"
        >
          <i class="bi me-2" :class="isReadyToApply ? 'bi-check-circle' : 'bi-exclamation-triangle'"></i>
          {{ isReadyToApply ? t('profilePage.readyToApply') : t('profilePage.completeRequired') }}
          <ul v-if="!isReadyToApply && missingApplyFields.length" class="mb-0 mt-2" data-testid="profile-missing-fields">
            <li v-for="key in missingApplyFields" :key="key">{{ t(`profilePage.missingFields.${key}`) }}</li>
          </ul>
        </div>

        <form autocomplete="off" @submit.prevent="handleSubmit">
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
                  <input
                    id="profile-matricula"
                    v-model="form.matricula"
                    type="text"
                    inputmode="numeric"
                    pattern="[0-9]+"
                    :class="fieldClass('matricula')"
                    :aria-invalid="ariaInvalid('matricula')"
                    :aria-describedby="describeId('matricula')"
                    required
                    data-testid="profile-matricula"
                  >
                  <div v-if="fieldErrors.matricula" :id="describeId('matricula')" class="invalid-feedback d-block">
                    {{ fieldErrors.matricula }}
                  </div>
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="profile-first-name">{{ t('profilePage.firstName') }} *</label>
                  <input
                    id="profile-first-name"
                    v-model="form.first_name"
                    type="text"
                    :class="fieldClass('first_name')"
                    :aria-invalid="ariaInvalid('first_name')"
                    :aria-describedby="describeId('first_name')"
                    name="given-name"
                    autocomplete="given-name"
                    required
                    data-testid="profile-first-name"
                  >
                  <div v-if="fieldErrors.first_name" :id="describeId('first_name')" class="invalid-feedback d-block">
                    {{ fieldErrors.first_name }}
                  </div>
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="profile-middle-name">{{ t('profilePage.middleName') }}</label>
                  <input id="profile-middle-name" v-model="form.middle_name" type="text" class="form-control" autocomplete="additional-name" data-testid="profile-middle-name">
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="profile-last-name">{{ t('profilePage.lastName') }} *</label>
                  <input
                    id="profile-last-name"
                    v-model="form.last_name"
                    type="text"
                    :class="fieldClass('last_name')"
                    :aria-invalid="ariaInvalid('last_name')"
                    :aria-describedby="describeId('last_name')"
                    name="family-name"
                    autocomplete="family-name"
                    required
                    data-testid="profile-last-name"
                  >
                  <div v-if="fieldErrors.last_name" :id="describeId('last_name')" class="invalid-feedback d-block">
                    {{ fieldErrors.last_name }}
                  </div>
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="profile-mothers-last-name">{{ t('profilePage.mothersLastName') }}</label>
                  <input id="profile-mothers-last-name" v-model="form.mothers_last_name" type="text" class="form-control" autocomplete="family-name" data-testid="profile-mothers-last-name">
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
                  <select
                    id="profile-gender"
                    v-model="form.gender"
                    :class="selectClass('gender')"
                    :aria-invalid="ariaInvalid('gender')"
                    :aria-describedby="describeId('gender')"
                    required
                    data-testid="profile-gender"
                  >
                    <option value="">{{ t('profilePage.selectOption') }}</option>
                    <option value="female">{{ t('profilePage.genderFemale') }}</option>
                    <option value="male">{{ t('profilePage.genderMale') }}</option>
                    <option value="non_binary">{{ t('profilePage.genderNonBinary') }}</option>
                    <option value="other">{{ t('profilePage.genderOther') }}</option>
                    <option value="prefer_not_to_say">{{ t('profilePage.genderPreferNot') }}</option>
                  </select>
                  <div v-if="fieldErrors.gender" :id="describeId('gender')" class="invalid-feedback d-block">
                    {{ fieldErrors.gender }}
                  </div>
                </div>
                <div class="col-md-4">
                  <label class="form-label" for="profile-dob">{{ t('profilePage.dateOfBirth') }} *</label>
                  <input id="profile-dob" v-model="form.date_of_birth" type="date" class="form-control" required data-testid="profile-dob">
                </div>
                <div class="col-md-4">
                  <label class="form-label" for="profile-birthplace">{{ t('profilePage.birthplace') }} *</label>
                  <input id="profile-birthplace" v-model="form.birthplace" type="text" class="form-control" required data-testid="profile-birthplace">
                </div>
                <div class="col-md-4">
                  <label class="form-label" for="profile-postal-code">{{ t('profilePage.postalCode') }} *</label>
                  <input id="profile-postal-code" v-model="form.postal_code" type="text" class="form-control" autocomplete="postal-code" required data-testid="profile-postal-code">
                </div>
                <div class="col-md-4">
                  <label class="form-label" for="profile-passport">{{ t('profilePage.passportNumber') }}<span v-if="fieldIsRequired('passport_number')"> *</span></label>
                  <input id="profile-passport" v-model="form.passport_number" type="text" class="form-control" data-testid="profile-passport">
                </div>
                <div class="col-md-4">
                  <label class="form-label" for="profile-mobile">{{ t('profilePage.mobilePhone') }} *</label>
                  <input id="profile-mobile" v-model="form.mobile_phone" type="tel" class="form-control" autocomplete="tel" required data-testid="profile-mobile">
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="profile-secondary-email">{{ t('profilePage.secondaryEmail') }} *</label>
                  <input id="profile-secondary-email" v-model="form.secondary_email" type="email" class="form-control" autocomplete="email" required data-testid="profile-secondary-email">
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="profile-rfc">{{ t('profilePage.rfc') }}<span v-if="fieldIsRequired('rfc')"> *</span></label>
                  <input id="profile-rfc" v-model="form.rfc" type="text" class="form-control text-uppercase" data-testid="profile-rfc">
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
                    <option v-for="item in catalogs.academicLevels" :key="item.id" :value="String(item.id)">{{ item.name }}</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="profile-unidad">{{ t('profilePage.unidad') }} *</label>
                  <select id="profile-unidad" v-model="form.unidad" class="form-select" required data-testid="profile-unidad">
                    <option value="">{{ t('profilePage.selectOption') }}</option>
                    <option v-for="item in catalogs.unidades" :key="item.id" :value="String(item.id)">{{ item.name }}</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="profile-school">{{ t('profilePage.school') }} *</label>
                  <select id="profile-school" v-model="form.school" class="form-select" :disabled="!form.unidad || schoolsLoading" required data-testid="profile-school">
                    <option value="">{{ schoolsLoading ? t('profilePage.loadingPrograms') : t('profilePage.selectOption') }}</option>
                    <option v-for="item in catalogs.schools" :key="item.id" :value="String(item.id)">{{ item.name }}</option>
                  </select>
                  <div
                    v-if="form.unidad && !schoolsLoading && catalogs.schools.length === 0"
                    class="form-text text-warning"
                    data-testid="profile-no-schools-warning"
                  >
                    {{ t('profilePage.noSchoolsForUnidad') }}
                  </div>
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="profile-program">{{ t('profilePage.homeProgram') }} *</label>
                  <select id="profile-program" v-model="form.home_academic_program" class="form-select" :disabled="!form.school || programsLoading" required data-testid="profile-program">
                    <option value="">{{ programsLoading ? t('profilePage.loadingPrograms') : t('profilePage.selectOption') }}</option>
                    <option v-for="item in catalogs.programs" :key="item.id" :value="String(item.id)">{{ item.name }}</option>
                  </select>
                </div>
              </div>
            </div>
          </section>

          <section class="card mb-4" data-testid="profile-banking-section">
            <div class="card-header">
              <h5 class="mb-0">
                {{ t('profilePage.bankingSection') }}
                <span v-if="!fieldIsRequired('clabe') && !fieldIsRequired('bank_institution')" class="small text-muted">({{ t('profilePage.optional') }})</span>
              </h5>
            </div>
            <div class="card-body">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label" for="profile-bank">{{ t('profilePage.bank') }}<span v-if="fieldIsRequired('bank_institution')"> *</span></label>
                  <select id="profile-bank" v-model="form.bank_institution" class="form-select" data-testid="profile-bank">
                    <option value="">{{ t('profilePage.selectOption') }}</option>
                    <option v-for="item in catalogs.banks" :key="item.id" :value="String(item.id)">{{ item.name }}</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="profile-clabe">{{ t('profilePage.clabe') }}<span v-if="fieldIsRequired('clabe')"> *</span></label>
                  <input
                    id="profile-clabe"
                    :value="form.clabe"
                    type="text"
                    inputmode="numeric"
                    maxlength="18"
                    class="form-control"
                    autocomplete="off"
                    :placeholder="t('profilePage.clabePlaceholder')"
                    :title="t('profilePage.clabeHelp')"
                    data-testid="profile-clabe"
                    @input="onClabeInput"
                  >
                  <div class="form-text" data-testid="profile-clabe-help">{{ t('profilePage.clabeHelp') }}</div>
                </div>
              </div>
            </div>
          </section>

          <section class="card mb-4" data-testid="profile-eligibility-section">
            <div class="card-header"><h5 class="mb-0">{{ t('profilePage.eligibilitySection') }} *</h5></div>
            <div class="card-body">
              <p class="small text-muted">{{ t('profilePage.eligibilityIntro') }}</p>
              <div class="row g-3 mb-3">
                <div class="col-md-6">
                  <label class="form-label" for="profile-ingress-date">{{ t('profilePage.ingressDate') }} *</label>
                  <input id="profile-ingress-date" v-model="form.ingress_date" type="date" class="form-control" :required="form.current_semester == null" data-testid="profile-ingress-date">
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="profile-current-semester">{{ t('profilePage.currentSemester') }}</label>
                  <input id="profile-current-semester" v-model="form.current_semester" type="number" min="1" step="1" class="form-control" :placeholder="computedSemesterPlaceholder" :required="!form.ingress_date" autocomplete="off" data-testid="profile-current-semester">
                  <div class="form-text">{{ t('profilePage.currentSemesterHelp') }}</div>
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="profile-credits-percent">{{ t('profilePage.creditsApprovedPercent') }} *</label>
                  <input id="profile-credits-percent" v-model="form.credits_approved_percent" type="number" min="0" max="100" step="0.01" class="form-control" required autocomplete="off" data-testid="profile-credits-percent">
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="profile-gpa">{{ t('profilePage.gpaLabel') }} *</label>
                  <input id="profile-gpa" v-model="form.gpa" type="number" step="0.01" min="0" class="form-control" autocomplete="off" required :placeholder="t('profilePage.gpaPlaceholder')" data-testid="profile-gpa">
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="profile-grade-scale">{{ t('profilePage.gradeScale') }} *</label>
                  <select id="profile-grade-scale" v-model="form.grade_scale" class="form-select" required data-testid="profile-grade-scale" :key="`scale-${form.grade_scale}-${catalogs.gradeScales.length}`">
                    <option value="">{{ t('profilePage.selectOption') }}</option>
                    <option v-for="item in catalogs.gradeScales" :key="item.id" :value="String(item.id)">{{ item.name }}</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="profile-language">{{ t('profilePage.primaryLanguage') }} *</label>
                  <input id="profile-language" v-model="form.language" type="text" class="form-control" autocomplete="off" required :placeholder="t('profilePage.languagePlaceholder')" data-testid="profile-language">
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="profile-language-level">{{ t('profilePage.primaryLevelLabel') }} *</label>
                  <select id="profile-language-level" v-model="form.language_level" class="form-select" autocomplete="off" required data-testid="profile-language-level">
                    <option value="">{{ t('profilePage.selectOption') }}</option>
                    <option v-for="level in cefrLevels" :key="level" :value="level">{{ t(`profilePage.cefr${level}`) }}</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="profile-toefl">{{ t('profilePage.toeflScore') }}</label>
                  <input id="profile-toefl" v-model="form.toefl_score" type="number" min="0" step="1" class="form-control" autocomplete="off" data-testid="profile-toefl">
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
    </PageStateShell>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useToast } from '@/composables/useToast'
import api from '@/services/api'
import PageHeader from '@/components/PageHeader.vue'
import PageBreadcrumb from '@/components/PageBreadcrumb.vue'
import PageStateShell from '@/components/State/PageStateShell.vue'
import { useFormFields } from '@/composables/useFormFields'

const { t } = useI18n()
const { success, error: errorToast } = useToast()
const {
  fieldErrors,
  setFieldError,
  clearFieldErrors,
  fieldClass,
  selectClass,
  ariaInvalid,
  describeId,
  applyApiFieldErrors,
} = useFormFields()
const cefrLevels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
const loading = ref(true)
const hydrating = ref(true)
const saving = ref(false)
const programsLoading = ref(false)
const schoolsLoading = ref(false)
const saveError = ref('')
const catalogs = reactive({
  academicLevels: [], schools: [], unidades: [], banks: [], programs: [], gradeScales: [],
})

const emptyForm = {
  email: '', first_name: '', middle_name: '', last_name: '', mothers_last_name: '',
  matricula: '', gender: '', date_of_birth: '', birthplace: '', postal_code: '',
  passport_number: '', mobile_phone: '', secondary_email: '', rfc: '',
  academic_level: '', school: '', unidad: '', home_academic_program: '',
  academic_level_name: '', school_name: '', unidad_name: '', home_academic_program_name: '',
  bank_institution: '', bank_institution_name: '', clabe: '', gpa: null, grade_scale: '', language: '',
  language_level: '', toefl_score: null, additional_languages: [],
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

const DEFAULT_APPLY_START = [
  'first_name', 'last_name', 'matricula', 'academic_level', 'school', 'unidad',
  'home_academic_program', 'gender', 'date_of_birth', 'birthplace', 'postal_code',
  'mobile_phone', 'secondary_email', 'gpa', 'grade_scale', 'language',
  'credits_approved_percent', 'semester',
]
const applyStartKeys = ref(new Set(DEFAULT_APPLY_START))
const dueProfileKeys = ref(new Set())

function fieldIsRequired(key) {
  return applyStartKeys.value.has(key) || dueProfileKeys.value.has(key)
}

const missingApplyFields = computed(() => {
  const missing = []
  const blank = (value) => value == null || !String(value).trim()
  const need = (key) => fieldIsRequired(key)
  if (need('first_name') && blank(form.value.first_name)) missing.push('first_name')
  if (need('last_name') && blank(form.value.last_name)) missing.push('last_name')
  if (need('matricula') && blank(form.value.matricula)) missing.push('matricula')
  if (need('academic_level') && !form.value.academic_level) missing.push('academic_level')
  if (need('school') && !form.value.school) missing.push('school')
  if (need('unidad') && !form.value.unidad) missing.push('unidad')
  if (need('home_academic_program') && !form.value.home_academic_program) missing.push('home_academic_program')
  if (need('gender') && blank(form.value.gender)) missing.push('gender')
  if (need('date_of_birth') && !form.value.date_of_birth) missing.push('date_of_birth')
  if (need('birthplace') && blank(form.value.birthplace)) missing.push('birthplace')
  if (need('postal_code') && blank(form.value.postal_code)) missing.push('postal_code')
  if (need('mobile_phone') && blank(form.value.mobile_phone)) missing.push('mobile_phone')
  if (need('secondary_email') && blank(form.value.secondary_email)) missing.push('secondary_email')
  if (need('gpa') && (form.value.gpa == null || form.value.gpa === '')) missing.push('gpa')
  if (need('grade_scale') && !form.value.grade_scale) missing.push('grade_scale')
  if (need('language') && blank(form.value.language)) missing.push('language')
  if (need('credits_approved_percent') && (form.value.credits_approved_percent == null || form.value.credits_approved_percent === '')) {
    missing.push('credits_approved_percent')
  }
  if (need('semester') && !form.value.ingress_date && (form.value.current_semester == null || form.value.current_semester === '')) {
    missing.push('semester')
  }
  if (need('passport_number') && blank(form.value.passport_number)) missing.push('passport_number')
  if (need('rfc') && blank(form.value.rfc)) missing.push('rfc')
  if (need('bank_institution') && !form.value.bank_institution) missing.push('bank_institution')
  if (need('clabe') && String(form.value.clabe || '').replace(/\D/g, '').length !== 18) missing.push('clabe')
  return missing
})
const isReadyToApply = computed(() => missingApplyFields.value.length === 0)

const PROFILE_FIELDS = [
  'first_name', 'middle_name', 'last_name', 'mothers_last_name',
  'matricula', 'gender', 'date_of_birth', 'birthplace', 'postal_code',
  'passport_number', 'mobile_phone', 'secondary_email', 'rfc',
  'academic_level', 'school', 'unidad', 'home_academic_program',
  'bank_institution', 'clabe', 'gpa', 'grade_scale', 'language',
  'language_level', 'toefl_score', 'additional_languages',
  'ingress_date', 'current_semester', 'credits_approved_percent',
]

function listFrom(data) {
  const rows = data?.results || data
  return Array.isArray(rows) ? rows : []
}

function catalogRow(item) {
  if (!item || item.id == null || item.id === '') return null
  return { id: String(item.id), name: item.name || String(item.id) }
}

function catalogList(data) {
  return listFrom(data).map(catalogRow).filter(Boolean)
}

function ensureSelected(list, selectedId, selectedName) {
  const id = idOf(selectedId)
  if (!id) return list
  if (list.some((row) => String(row.id) === id)) return list
  return [{ id, name: selectedName || id }, ...list]
}

function idOf(value) {
  if (value && typeof value === 'object') {
    return value.id == null || value.id === '' ? '' : String(value.id)
  }
  return value == null || value === '' ? '' : String(value)
}

function dateOf(value) {
  if (!value) return ''
  return String(value).slice(0, 10)
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
  return catalogList(data)
}

async function fetchSchools(unidadId, clearSelection = true, { notifyError = true } = {}) {
  if (clearSelection) {
    form.value.school = ''
    form.value.home_academic_program = ''
    catalogs.programs = []
  }
  if (!unidadId) {
    catalogs.schools = []
    return
  }
  schoolsLoading.value = true
  try {
    const { data } = await api.get('/api/accounts/catalogs/schools/', { params: { unidad: unidadId } })
    catalogs.schools = ensureSelected(
      catalogList(data),
      form.value.school,
      form.value.school_name,
    )
  } catch {
    catalogs.schools = ensureSelected(
      catalogs.schools,
      form.value.school,
      form.value.school_name,
    )
    if (notifyError) errorToast(t('profilePage.toastCatalogError'))
  } finally {
    schoolsLoading.value = false
  }
}

async function fetchPrograms(schoolId, clearSelection = true, { notifyError = true } = {}) {
  if (clearSelection) form.value.home_academic_program = ''
  if (!schoolId) {
    catalogs.programs = []
    return
  }
  programsLoading.value = true
  try {
    const { data } = await api.get('/api/accounts/catalogs/programs/', { params: { school: schoolId } })
    catalogs.programs = ensureSelected(
      catalogList(data),
      form.value.home_academic_program,
      form.value.home_academic_program_name,
    )
  } catch {
    catalogs.programs = ensureSelected(
      catalogs.programs,
      form.value.home_academic_program,
      form.value.home_academic_program_name,
    )
    if (notifyError) errorToast(t('profilePage.toastCatalogError'))
  } finally {
    programsLoading.value = false
  }
}

function numberOf(value) {
  if (value === '' || value == null) return null
  const n = Number(value)
  return Number.isNaN(n) ? null : n
}

function applyProfile(data) {
  applyStartKeys.value = new Set(data.apply_start_field_keys || DEFAULT_APPLY_START)
  dueProfileKeys.value = new Set(data.due_profile_fields || [])
  form.value = {
    ...emptyForm,
    email: data.email || '',
    first_name: data.first_name || '',
    middle_name: data.middle_name || '',
    last_name: data.last_name || '',
    mothers_last_name: data.mothers_last_name || '',
    matricula: data.matricula || '',
    gender: data.gender || '',
    date_of_birth: dateOf(data.date_of_birth),
    birthplace: data.birthplace || '',
    postal_code: data.postal_code || '',
    passport_number: data.passport_number || '',
    mobile_phone: data.mobile_phone || '',
    secondary_email: data.secondary_email || '',
    rfc: data.rfc || '',
    academic_level: idOf(data.academic_level),
    academic_level_name: data.academic_level_name || '',
    school: idOf(data.school),
    school_name: data.school_name || '',
    unidad: idOf(data.unidad),
    unidad_name: data.unidad_name || '',
    home_academic_program: idOf(data.home_academic_program),
    home_academic_program_name: data.home_academic_program_name || '',
    bank_institution: idOf(data.bank_institution),
    bank_institution_name: data.bank_institution_name || '',
    clabe: data.clabe || '',
    gpa: numberOf(data.gpa),
    grade_scale: idOf(data.grade_scale),
    language: data.language || '',
    language_level: data.language_level || '',
    toefl_score: numberOf(data.toefl_score),
    ingress_date: dateOf(data.ingress_date),
    current_semester: numberOf(data.current_semester),
    credits_approved_percent: numberOf(data.credits_approved_percent),
    computed_semester: data.computed_semester ?? null,
    effective_semester: data.effective_semester ?? null,
    additional_languages: Array.isArray(data.additional_languages)
      ? data.additional_languages.map((row) => ({ name: row?.name || '', level: row?.level || '' }))
      : [],
  }
  catalogs.academicLevels = ensureSelected(catalogs.academicLevels, form.value.academic_level, form.value.academic_level_name)
  catalogs.schools = ensureSelected(catalogs.schools, form.value.school, form.value.school_name)
  catalogs.unidades = ensureSelected(catalogs.unidades, form.value.unidad, form.value.unidad_name)
  catalogs.banks = ensureSelected(catalogs.banks, form.value.bank_institution, form.value.bank_institution_name)
  catalogs.gradeScales = ensureSelected(catalogs.gradeScales, form.value.grade_scale, data.grade_scale_name)
}

async function fetchActiveGradeScales() {
  const load = async (url) => {
    const { data } = await api.get(url)
    const rows = catalogList(data)
    if (!rows.length && !Array.isArray(data) && !Array.isArray(data?.results)) {
      throw new Error(`Invalid grade scale payload from ${url}`)
    }
    return rows
  }
  try {
    return await load('/api/grades/scales/active/')
  } catch {
    return await load('/grades/api/scales/active/')
  }
}

async function fetchProfileAndCatalogs() {
  hydrating.value = true
  const catalogSettled = await Promise.allSettled([
    fetchCatalog('academic-levels'),
    fetchCatalog('unidades'),
    fetchCatalog('banks'),
  ])
  const scalesSettled = await Promise.allSettled([fetchActiveGradeScales()])
  const catalogFailed = catalogSettled.some((result) => result.status === 'rejected')
  catalogs.academicLevels = catalogSettled[0].status === 'fulfilled' ? catalogSettled[0].value : []
  catalogs.unidades = catalogSettled[1].status === 'fulfilled' ? catalogSettled[1].value : []
  catalogs.banks = catalogSettled[2].status === 'fulfilled' ? catalogSettled[2].value : []
  catalogs.schools = []
  catalogs.programs = []
  catalogs.gradeScales = scalesSettled[0].status === 'fulfilled' ? scalesSettled[0].value : []
  if (catalogFailed) {
    errorToast(t('profilePage.toastCatalogError'))
  }

  try {
    const profileResponse = await api.get('/api/accounts/profile/')
    applyProfile(profileResponse.data || {})
    if (form.value.unidad) {
      await fetchSchools(form.value.unidad, false, { notifyError: !catalogFailed })
    }
    if (form.value.school) {
      await fetchPrograms(form.value.school, false, { notifyError: !catalogFailed })
    }
    await nextTick()
  } catch (err) {
    console.error('Failed to load profile:', err)
    errorToast(t('profilePage.toastLoadError'))
  } finally {
    loading.value = false
    await nextTick()
    hydrating.value = false
  }
}

function nullable(value) {
  if (value === '' || value === undefined || Number.isNaN(value)) return null
  return value
}

function normalizedAdditionalLanguages() {
  return form.value.additional_languages
    .map((row) => ({ name: String(row.name || '').trim(), level: String(row.level || '').trim() }))
    .filter((row) => row.name)
}

function buildPayload() {
  const payload = {}
  for (const key of PROFILE_FIELDS) {
    payload[key] = form.value[key]
  }
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
  payload.date_of_birth = nullable(payload.date_of_birth)
  payload.ingress_date = nullable(payload.ingress_date)
  payload.current_semester = nullable(payload.current_semester)
  payload.credits_approved_percent = nullable(payload.credits_approved_percent)
  payload.toefl_score = nullable(payload.toefl_score)
  payload.additional_languages = normalizedAdditionalLanguages()
  payload.rfc = String(payload.rfc || '').trim().toUpperCase()
  const clabeDigits = String(payload.clabe || '').replace(/\D/g, '')
  payload.clabe = clabeDigits.length === 18 ? clabeDigits : ''
  return payload
}

function onClabeInput(event) {
  form.value.clabe = String(event.target.value || '').replace(/\D/g, '').slice(0, 18)
}

async function handleSubmit() {
  saveError.value = ''
  clearFieldErrors()
  for (const key of missingApplyFields.value) {
    setFieldError(key, t(`profilePage.missingFields.${key}`))
  }
  if (missingApplyFields.value.length) {
    saveError.value = t('profilePage.completeRequired')
    return
  }
  saving.value = true
  try {
    const { data } = await api.patch('/api/accounts/profile/', buildPayload())
    applyProfile(data || {})
    if (form.value.unidad) {
      await fetchSchools(form.value.unidad, false)
    }
    if (form.value.school) {
      await fetchPrograms(form.value.school, false)
    }
    success(t('profilePage.toastSaved'))
  } catch (err) {
    applyApiFieldErrors(err.response?.data)
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

watch(() => form.value.unidad, (unidad, previous) => {
  if (loading.value || hydrating.value || saving.value) return
  if (String(unidad || '') === String(previous || '')) return
  fetchSchools(unidad)
})

watch(() => form.value.school, (school, previous) => {
  if (loading.value || hydrating.value || saving.value) return
  if (String(school || '') === String(previous || '')) return
  fetchPrograms(school)
})

onMounted(fetchProfileAndCatalogs)
</script>

<style scoped>
.profile-page { background-color: var(--seim-app-bg); }
.card { border: none; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05); }
.card-header { background: var(--bs-body-bg); border-bottom: 1px solid var(--bs-border-color); }
</style>
