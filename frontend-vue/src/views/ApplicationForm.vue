<template>
  <div class="application-form-page">
    <div class="container-fluid mt-4">
      <!-- Breadcrumb -->
      <nav aria-label="breadcrumb">
        <ol class="breadcrumb">
          <li class="breadcrumb-item">
            <router-link :to="{ name: 'Dashboard' }">Dashboard</router-link>
          </li>
          <li class="breadcrumb-item">
            <router-link :to="{ name: 'Applications' }">Applications</router-link>
          </li>
          <li class="breadcrumb-item active">
            {{ isEditMode ? 'Edit Application' : 'New Application' }}
          </li>
        </ol>
      </nav>

      <!-- Header -->
      <div class="row mb-4">
        <div class="col-md-8">
          <h2>
            <i class="bi bi-file-earmark-plus me-2"></i>
            {{ isEditMode ? 'Edit Application' : 'Create New Application' }}
          </h2>
          <p class="text-muted">
            {{ isEditMode ? 'Update your application details' : 'Start your exchange journey' }}
          </p>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-3 text-muted">{{ loadingMessage }}</p>
      </div>

      <!-- Form -->
      <div v-else class="row">
        <div class="col-lg-8">
          <div class="card">
            <div class="card-body">
              <form data-testid="application-form" @submit.prevent="handleSubmit">
                <!-- Program Selection -->
                <div class="mb-4">
                  <label for="program" class="form-label">
                    Exchange Program <span class="text-danger">*</span>
                  </label>
                  <div v-if="!isEditMode" class="card mb-3 border-0 bg-light">
                    <div class="card-body py-3">
                      <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-2">
                        <span class="small text-muted fw-semibold">Filter programs</span>
                        <button
                          type="button"
                          class="btn btn-link btn-sm p-0"
                          @click="clearProgramFilters"
                        >
                          Clear filters
                        </button>
                      </div>
                      <div class="row g-2">
                        <div class="col-md-6">
                          <label class="form-label small mb-0" for="program-filter-search">Search</label>
                          <input
                            id="program-filter-search"
                            v-model="programFilters.search"
                            type="search"
                            class="form-control form-control-sm"
                            placeholder="Name or description"
                            autocomplete="off"
                          >
                        </div>
                        <div class="col-md-6">
                          <label class="form-label small mb-0" for="program-filter-ordering">Sort by</label>
                          <select
                            id="program-filter-ordering"
                            v-model="programFilters.ordering"
                            class="form-select form-select-sm"
                          >
                            <option value="name">Name (A–Z)</option>
                            <option value="-start_date">Start date (newest first)</option>
                            <option value="start_date">Start date (soonest first)</option>
                            <option value="-end_date">End date (latest first)</option>
                          </select>
                        </div>
                        <div class="col-md-6">
                          <label class="form-label small mb-0" for="program-filter-language">Required language</label>
                          <input
                            id="program-filter-language"
                            v-model="programFilters.required_language"
                            type="text"
                            class="form-control form-control-sm"
                            placeholder="e.g. English"
                            autocomplete="off"
                          >
                        </div>
                        <div class="col-md-6">
                          <label class="form-label small mb-0" for="program-filter-cefr">Min. language level</label>
                          <select
                            id="program-filter-cefr"
                            v-model="programFilters.min_language_level"
                            class="form-select form-select-sm"
                          >
                            <option value="">Any</option>
                            <option value="A1">A1</option>
                            <option value="A2">A2</option>
                            <option value="B1">B1</option>
                            <option value="B2">B2</option>
                            <option value="C1">C1</option>
                            <option value="C2">C2</option>
                          </select>
                        </div>
                        <div class="col-md-6">
                          <label class="form-label small mb-0" for="program-filter-start-after">Program starts on or after</label>
                          <input
                            id="program-filter-start-after"
                            v-model="programFilters.start_date_after"
                            type="date"
                            class="form-control form-control-sm"
                          >
                        </div>
                        <div class="col-md-6">
                          <label class="form-label small mb-0" for="program-filter-start-before">Program starts on or before</label>
                          <input
                            id="program-filter-start-before"
                            v-model="programFilters.start_date_before"
                            type="date"
                            class="form-control form-control-sm"
                          >
                        </div>
                        <div class="col-md-6">
                          <label class="form-label small mb-0" for="program-filter-gpa">My GPA (show programs I may qualify for)</label>
                          <input
                            id="program-filter-gpa"
                            v-model="programFilters.min_gpa_max"
                            type="number"
                            step="0.1"
                            min="0"
                            max="4"
                            class="form-control form-control-sm"
                            placeholder="e.g. 3.2"
                          >
                        </div>
                        <div class="col-md-6 d-flex align-items-end">
                          <div class="form-check mb-0">
                            <input
                              id="program-filter-accepting"
                              v-model="programFilters.accepting_applications"
                              class="form-check-input"
                              type="checkbox"
                            >
                            <label class="form-check-label small" for="program-filter-accepting">
                              Only programs accepting applications now
                            </label>
                          </div>
                        </div>
                      </div>
                      <p v-if="programsLoading" class="small text-muted mb-0 mt-2" data-testid="programs-filter-loading">
                        Updating program list…
                      </p>
                      <p v-else class="small text-muted mb-0 mt-2">
                        {{ programs.length }} program{{ programs.length === 1 ? '' : 's' }} match
                      </p>
                      <div class="border-top pt-3 mt-3">
                        <div class="d-flex flex-wrap align-items-end gap-2 mb-2">
                          <div class="flex-grow-1" style="min-width: 200px">
                            <label class="form-label small text-muted mb-1">Save filters as preset</label>
                            <div class="input-group input-group-sm">
                              <input
                                v-model="newPresetName"
                                type="text"
                                class="form-control"
                                placeholder="Preset name"
                                data-testid="program-filter-preset-name"
                              >
                              <button
                                type="button"
                                class="btn btn-outline-primary"
                                :disabled="!newPresetName.trim() || presetsLoading"
                                data-testid="program-filter-preset-save"
                                @click="saveProgramFilterPreset"
                              >
                                Save
                              </button>
                            </div>
                          </div>
                          <div class="form-check mb-1">
                            <input
                              id="program-preset-default"
                              v-model="saveAsDefault"
                              class="form-check-input"
                              type="checkbox"
                            >
                            <label class="form-check-label small" for="program-preset-default">
                              Default when starting a new application
                            </label>
                          </div>
                        </div>
                        <div v-if="savedPresets.length" class="small">
                          <span class="text-muted me-2">Saved:</span>
                          <span
                            v-for="p in savedPresets"
                            :key="p.id"
                            class="d-inline-flex align-items-center gap-1 me-3 mb-1"
                          >
                            <button
                              type="button"
                              class="btn btn-link btn-sm p-0"
                              data-testid="program-filter-preset-apply"
                              @click="applyProgramFilterPreset(p)"
                            >
                              {{ p.name }}
                            </button>
                            <i
                              v-if="p.is_default"
                              class="bi bi-star-fill text-warning"
                              title="Default preset"
                              aria-label="Default preset"
                            />
                            <button
                              v-else
                              type="button"
                              class="btn btn-link btn-sm p-0 text-secondary"
                              title="Set as default"
                              aria-label="Set as default"
                              @click="setDefaultPreset(p)"
                            >
                              <i class="bi bi-star" />
                            </button>
                            <button
                              type="button"
                              class="btn btn-link btn-sm p-0 text-danger"
                              title="Remove preset"
                              aria-label="Remove preset"
                              @click="deletePreset(p)"
                            >
                              <i class="bi bi-trash" />
                            </button>
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <select
                    id="program"
                    v-model="form.program"
                    class="form-select"
                    :class="{ 'is-invalid': programErrors.length }"
                    required
                    :disabled="isEditMode"
                    data-testid="program-select"
                  >
                    <option value="">-- Select a Program --</option>
                    <option v-for="program in programs" :key="program.id" :value="program.id">
                      {{ program.name }}
                    </option>
                  </select>
                  <div v-if="programErrors.length" class="alert alert-danger mt-2 mb-0" role="alert" data-testid="eligibility-alert">
                    <h6 class="alert-heading mb-2">
                      <i class="bi bi-exclamation-triangle-fill me-2"></i>You don't meet this program's requirements
                    </h6>
                    <ul class="mb-0 ps-3">
                      <li v-for="(msg, i) in programErrors" :key="i">{{ msg }}</li>
                    </ul>
                  </div>
                  <div v-else class="form-text">
                    {{ isEditMode ? 'Program cannot be changed after creation' : 'Choose the exchange program you want to apply to' }}
                  </div>
                </div>

                <!-- Selected Program Info -->
                <div v-if="selectedProgram" class="alert alert-info mb-4">
                  <h6 class="alert-heading">
                    <i class="bi bi-info-circle me-2"></i>Program Information
                  </h6>
                  <p class="mb-2"><strong>{{ selectedProgram.name }}</strong></p>
                  <p class="small mb-2">{{ selectedProgram.description }}</p>
                  <div class="row small">
                    <div class="col-md-6">
                      <strong>Start Date:</strong> {{ formatDate(selectedProgram.start_date) }}
                    </div>
                    <div class="col-md-6">
                      <strong>End Date:</strong> {{ formatDate(selectedProgram.end_date) }}
                    </div>
                  </div>
                  <div
                    v-if="selectedProgram.application_open_date || selectedProgram.application_deadline"
                    class="row small mt-2"
                  >
                    <div class="col-md-6" v-if="selectedProgram.application_open_date">
                      <strong>Applications Open:</strong> {{ formatDate(selectedProgram.application_open_date) }}
                    </div>
                    <div class="col-md-6" v-if="selectedProgram.application_deadline">
                      <strong>Apply By:</strong> {{ formatDate(selectedProgram.application_deadline) }}
                    </div>
                  </div>
                  <div v-if="selectedProgram.min_gpa" class="mt-2 small">
                    <strong>Requirements:</strong> Min GPA: {{ selectedProgram.min_gpa }}
                    <span v-if="selectedProgram.required_language">
                      | {{ selectedProgram.required_language }} ({{ selectedProgram.min_language_level }})
                    </span>
                  </div>
                </div>

                <div
                  v-if="applicationWindowState && !applicationWindowState.canApply && !isEditMode"
                  class="alert mb-4"
                  :class="applicationWindowState.reason === 'not_open_yet' ? 'alert-info' : 'alert-warning'"
                  data-testid="application-window-alert"
                >
                  <h6 class="alert-heading mb-2">
                    <i class="bi bi-clock-history me-2"></i>Application window unavailable
                  </h6>
                  <p class="mb-0">{{ applicationWindowState.message }}</p>
                </div>

                <!-- Dynamic Program Form -->
                <div v-if="dynamicFormLoading" class="alert alert-light border mb-4" data-testid="dynamic-form-loading">
                  <div class="d-flex align-items-center">
                    <span class="spinner-border spinner-border-sm text-primary me-2" aria-hidden="true"></span>
                    <span>Loading additional program questions...</span>
                  </div>
                </div>

                <div v-else-if="dynamicFormLoadError" class="alert alert-warning mb-4" data-testid="dynamic-form-load-error">
                  {{ dynamicFormLoadError }}
                </div>

                <div v-else-if="hasDynamicFields" class="mb-4" data-testid="dynamic-form-section">
                  <div class="d-flex align-items-center justify-content-between mb-3">
                    <div>
                      <h5 class="mb-1">Program Questions</h5>
                      <p v-if="dynamicForm.description" class="text-muted small mb-0">
                        {{ dynamicForm.description }}
                      </p>
                      <p v-if="isMultiStep" class="text-muted small mb-0 mt-1">
                        Step {{ currentStepIndex + 1 }} of {{ dynamicForm.steps.length }}
                        <span v-if="currentStepTitle"> — {{ currentStepTitle }}</span>
                      </p>
                    </div>
                    <span class="badge bg-light text-dark border">
                      {{ visibleDynamicFields.length }} field{{ visibleDynamicFields.length === 1 ? '' : 's' }}
                      <span v-if="isMultiStep"> / {{ dynamicFields.length }}</span>
                    </span>
                  </div>

                  <div v-if="isMultiStep" class="d-flex gap-2 mb-3">
                    <button
                      type="button"
                      class="btn btn-sm btn-outline-secondary"
                      :disabled="currentStepIndex === 0"
                      data-testid="dynamic-step-prev"
                      @click="goToPreviousStep"
                    >
                      <i class="bi bi-chevron-left me-1"></i>Back
                    </button>
                  </div>

                  <div
                    v-for="field in visibleDynamicFields"
                    :key="field.name"
                    class="mb-4"
                  >
                    <label
                      :for="`dynamic-field-${field.name}`"
                      class="form-label"
                    >
                      {{ field.label }}
                      <span v-if="field.required" class="text-danger">*</span>
                    </label>

                    <textarea
                      v-if="isTextareaField(field)"
                      :id="`dynamic-field-${field.name}`"
                      v-model="dynamicFormValues[field.name]"
                      class="form-control"
                      :class="{ 'is-invalid': dynamicFieldErrors[field.name] }"
                      :rows="getTextareaRows(field)"
                      :placeholder="getFieldPlaceholder(field)"
                      :required="field.required"
                      :data-testid="`dynamic-field-${field.name}`"
                    ></textarea>

                    <select
                      v-else-if="isSelectField(field)"
                      :id="`dynamic-field-${field.name}`"
                      v-model="dynamicFormValues[field.name]"
                      class="form-select"
                      :class="{ 'is-invalid': dynamicFieldErrors[field.name] }"
                      :required="field.required"
                      :data-testid="`dynamic-field-${field.name}`"
                    >
                      <option value="">-- Select an option --</option>
                      <option
                        v-for="option in getFieldOptions(field)"
                        :key="option"
                        :value="option"
                      >
                        {{ option }}
                      </option>
                    </select>

                    <div
                      v-else-if="isArrayField(field)"
                      class="border rounded p-3"
                      :class="{ 'border-danger': dynamicFieldErrors[field.name] }"
                      :data-testid="`dynamic-field-${field.name}`"
                    >
                      <div
                        v-for="option in getFieldOptions(field)"
                        :key="option"
                        class="form-check"
                      >
                        <input
                          :id="`dynamic-field-${field.name}-${option}`"
                          v-model="dynamicFormValues[field.name]"
                          class="form-check-input"
                          type="checkbox"
                          :value="option"
                        />
                        <label
                          class="form-check-label"
                          :for="`dynamic-field-${field.name}-${option}`"
                        >
                          {{ option }}
                        </label>
                      </div>
                    </div>

                    <div
                      v-else-if="isBooleanField(field)"
                      class="form-check"
                    >
                      <input
                        :id="`dynamic-field-${field.name}`"
                        v-model="dynamicFormValues[field.name]"
                        class="form-check-input"
                        type="checkbox"
                        :data-testid="`dynamic-field-${field.name}`"
                      />
                      <label
                        class="form-check-label"
                        :for="`dynamic-field-${field.name}`"
                      >
                        {{ field.description || 'Yes' }}
                      </label>
                    </div>

                    <input
                      v-else-if="isNumericField(field)"
                      :id="`dynamic-field-${field.name}`"
                      v-model.number="dynamicFormValues[field.name]"
                      class="form-control"
                      :class="{ 'is-invalid': dynamicFieldErrors[field.name] }"
                      :type="getInputType(field)"
                      :min="field.config.minimum"
                      :max="field.config.maximum"
                      :placeholder="getFieldPlaceholder(field)"
                      :required="field.required"
                      :data-testid="`dynamic-field-${field.name}`"
                    />

                    <input
                      v-else
                      :id="`dynamic-field-${field.name}`"
                      v-model="dynamicFormValues[field.name]"
                      class="form-control"
                      :class="{ 'is-invalid': dynamicFieldErrors[field.name] }"
                      :type="getInputType(field)"
                      :placeholder="getFieldPlaceholder(field)"
                      :required="field.required"
                      :data-testid="`dynamic-field-${field.name}`"
                    />

                    <div v-if="dynamicFieldErrors[field.name]" class="invalid-feedback d-block">
                      {{ dynamicFieldErrors[field.name] }}
                    </div>
                    <div v-else-if="field.description && !isBooleanField(field)" class="form-text">
                      {{ field.description }}
                    </div>
                  </div>
                </div>

                <div v-else-if="selectedProgram" class="alert alert-light border mb-4" data-testid="dynamic-form-empty">
                  No additional program-specific questions are configured for this program.
                </div>

                <div v-if="dynamicFormErrors.length" class="alert alert-danger">
                  <h6 class="alert-heading">Form validation failed</h6>
                  <ul class="mb-0 ps-3">
                    <li v-for="(message, index) in dynamicFormErrors" :key="index">{{ message }}</li>
                  </ul>
                </div>

                <!-- Other field errors -->
                <div v-if="otherErrors.length" class="alert alert-danger">
                  <h6 class="alert-heading">Please fix the following:</h6>
                  <ul class="mb-0 ps-3">
                    <li v-for="(text, i) in otherErrors" :key="i">{{ text }}</li>
                  </ul>
                </div>

                <!-- Actions -->
                <div class="d-flex justify-content-between">
                  <router-link :to="{ name: 'Applications' }" class="btn btn-outline-secondary" data-testid="cancel-link">
                    <i class="bi bi-x-circle me-2"></i>Cancel
                  </router-link>
                  <div>
                    <button
                      type="button"
                      class="btn btn-outline-primary me-2"
                      @click="saveDraft"
                      :disabled="submitting || !form.program || dynamicFormLoading || createBlockedByWindow"
                      data-testid="save-draft-btn"
                    >
                      <i class="bi bi-save me-2"></i>Save as Draft
                    </button>
                    <button
                      type="submit"
                      class="btn btn-primary"
                      :disabled="submitting || !form.program || dynamicFormLoading || createBlockedByWindow"
                      data-testid="create-application-btn"
                    >
                      <span v-if="submitting">
                        <span class="spinner-border spinner-border-sm me-2"></span>
                        {{ isEditMode ? 'Updating...' : 'Creating...' }}
                      </span>
                      <span v-else>
                        <i class="bi bi-check-circle me-2"></i>
                        <template v-if="isMultiStep && !isLastStep">
                          Save &amp; continue
                        </template>
                        <template v-else>
                          {{ isEditMode ? 'Update Application' : 'Create Application' }}
                        </template>
                      </span>
                    </button>
                  </div>
                </div>
              </form>
            </div>
          </div>
        </div>

        <!-- Sidebar -->
        <div class="col-lg-4">
          <!-- Tips -->
          <div class="card mb-4">
            <div class="card-header">
              <h6 class="mb-0"><i class="bi bi-lightbulb me-2"></i>Application Tips</h6>
            </div>
            <div class="card-body">
              <ul class="small mb-0">
                <li>Review program requirements carefully</li>
                <li>Check your GPA and language proficiency</li>
                <li>Answer every program-specific question accurately</li>
                <li>Save as draft to continue later</li>
                <li>Submit when you're ready for review</li>
              </ul>
            </div>
          </div>

          <!-- Program Requirements -->
          <div v-if="selectedProgram" class="card">
            <div class="card-header">
              <h6 class="mb-0"><i class="bi bi-clipboard-check me-2"></i>Requirements</h6>
            </div>
            <div class="card-body">
              <div class="mb-3">
                <label class="text-muted small">Minimum GPA</label>
                <p class="fw-bold">{{ selectedProgram.min_gpa || 'None' }}</p>
              </div>
              <div v-if="selectedProgram.application_open_date || selectedProgram.application_deadline" class="mb-3">
                <label class="text-muted small">Application Window</label>
                <p class="fw-bold mb-1">
                  <span v-if="selectedProgram.application_open_date">
                    Opens {{ formatDate(selectedProgram.application_open_date) }}
                  </span>
                  <span v-if="selectedProgram.application_open_date && selectedProgram.application_deadline">
                    <br>
                  </span>
                  <span v-if="selectedProgram.application_deadline">
                    Closes {{ formatDate(selectedProgram.application_deadline) }}
                  </span>
                </p>
                <p v-if="applicationWindowState" class="small text-muted mb-0">
                  {{ applicationWindowState.message }}
                </p>
              </div>
              <div v-if="selectedProgram.required_language" class="mb-3">
                <label class="text-muted small">Language</label>
                <p class="fw-bold">
                  {{ selectedProgram.required_language }}
                  <span class="badge bg-secondary">{{ selectedProgram.min_language_level }}</span>
                </p>
              </div>
              <div class="mb-3">
                <label class="text-muted small">Duration</label>
                <p class="fw-bold">
                  {{ calculateDuration(selectedProgram.start_date, selectedProgram.end_date) }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { useStaffSavedPresets } from '@/composables/useStaffSavedPresets'
import {
  APPLICATION_PROGRAM_FILTER_SEARCH_TYPE,
  serializeApplicationProgramFilters,
  deserializeApplicationProgramFilters,
} from '@/utils/applicationProgramFilterPresets'
import api from '@/services/api'

const route = useRoute()
const router = useRouter()
const { success, error: errorToast } = useToast()

const {
  savedPresets,
  presetsLoading,
  newPresetName,
  saveAsDefault,
  loadPresets,
  savePreset: savePresetToApi,
  deletePreset,
  setDefaultPreset,
} = useStaffSavedPresets(APPLICATION_PROGRAM_FILTER_SEARCH_TYPE)

const isEditMode = computed(() => route.params.id !== undefined)
const loading = ref(true)
const loadingMessage = ref('Loading...')
const submitting = ref(false)

const programs = ref([])
const programsLoading = ref(false)
const programFilters = ref({
  search: '',
  required_language: '',
  min_language_level: '',
  start_date_after: '',
  start_date_before: '',
  min_gpa_max: '',
  accepting_applications: false,
  ordering: 'name',
})
let programFilterDebounce = null
let suppressProgramFilterWatch = false

const form = ref({
  program: '',
})
const errors = ref({})
const dynamicForm = ref({
  id: null,
  name: '',
  description: '',
  schema: {},
  ui_schema: {},
  required_fields: [],
  multi_step: false,
  steps: [],
})
const dynamicFormValues = ref({})
const dynamicFieldErrors = ref({})
const dynamicFormErrors = ref([])
const dynamicFormLoading = ref(false)
const dynamicFormLoadError = ref('')
const pendingDynamicResponses = ref(null)
const applicationDynamicLayout = ref(null)
const currentStepIndex = ref(0)

// Normalize program errors: backend may return string or array
const programErrors = computed(() => {
  const raw = errors.value?.program
  if (!raw) return []
  return Array.isArray(raw) ? raw : [raw]
})

// Errors for other fields (exclude program and dynamic-form specific messages) as list of strings
const otherErrors = computed(() => {
  const list = []
  const omit = ['program', 'dynamic_form']
  for (const [field, value] of Object.entries(errors.value || {})) {
    if (omit.includes(field)) continue
    const texts = Array.isArray(value) ? value : [value]
    list.push(...texts.map(t => (typeof t === 'string' ? t : `${field}: ${JSON.stringify(t)}`)))
  }
  return list
})

const selectedProgram = computed(() => {
  if (!form.value.program) return null
  return programs.value.find(p => String(p.id) === String(form.value.program))
})

const applicationWindowState = computed(() => {
  if (!selectedProgram.value) return null

  const fallbackOpen = selectedProgram.value.application_window_open
  const fallbackMessage = selectedProgram.value.application_window_message
  const openDate = parseDateOnly(selectedProgram.value.application_open_date)
  const deadline = parseDateOnly(selectedProgram.value.application_deadline)
  const today = startOfToday()

  if (openDate && today < openDate) {
    return {
      canApply: false,
      reason: 'not_open_yet',
      message: fallbackMessage || `Applications open on ${formatDate(selectedProgram.value.application_open_date)}.`,
    }
  }

  if (deadline && today > deadline) {
    return {
      canApply: false,
      reason: 'closed',
      message: fallbackMessage || `Applications closed on ${formatDate(selectedProgram.value.application_deadline)}.`,
    }
  }

  if (openDate && deadline) {
    return {
      canApply: true,
      reason: 'open',
      message: fallbackMessage || `Applications are open from ${formatDate(selectedProgram.value.application_open_date)} through ${formatDate(selectedProgram.value.application_deadline)}.`,
    }
  }

  if (deadline) {
    return {
      canApply: true,
      reason: 'open',
      message: fallbackMessage || `Applications are open until ${formatDate(selectedProgram.value.application_deadline)}.`,
    }
  }

  if (openDate) {
    return {
      canApply: true,
      reason: 'open',
      message: fallbackMessage || `Applications opened on ${formatDate(selectedProgram.value.application_open_date)}.`,
    }
  }

  if (fallbackOpen === false) {
    return {
      canApply: false,
      reason: 'closed',
      message: fallbackMessage || 'Applications are not currently open for this program.',
    }
  }

  return {
    canApply: true,
    reason: 'open',
    message: fallbackMessage || 'Applications are currently open.',
  }
})

const createBlockedByWindow = computed(() => (
  !isEditMode.value && Boolean(applicationWindowState.value && !applicationWindowState.value.canApply)
))

const dynamicFields = computed(() => (
  Object.entries(dynamicForm.value.schema?.properties || {}).map(([name, config]) => ({
    name,
    config,
    label: config.title || name,
    description: config.description || '',
    required: dynamicForm.value.required_fields.includes(name),
  }))
))

const hasDynamicFields = computed(() => dynamicFields.value.length > 0)

const isMultiStep = computed(() => (
  Boolean(dynamicForm.value.multi_step && dynamicForm.value.steps?.length)
))

const currentStepKey = computed(() => {
  if (!isMultiStep.value) return null
  const step = dynamicForm.value.steps[currentStepIndex.value]
  return step?.key ?? null
})

const currentStepTitle = computed(() => {
  if (!isMultiStep.value) return ''
  const step = dynamicForm.value.steps[currentStepIndex.value]
  return step?.title || ''
})

const isLastStep = computed(() => {
  if (!isMultiStep.value) return true
  return currentStepIndex.value >= dynamicForm.value.steps.length - 1
})

const visibleDynamicFields = computed(() => {
  if (!hasDynamicFields.value) return []
  if (!isMultiStep.value) return dynamicFields.value
  const step = dynamicForm.value.steps[currentStepIndex.value]
  if (!step?.field_names?.length) return dynamicFields.value
  const allow = new Set(step.field_names)
  return dynamicFields.value.filter((f) => allow.has(f.name))
})

function normalizeProgramMatch(value) {
  return String(value || '')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

function startOfToday() {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return today
}

function parseDateOnly(dateString) {
  if (!dateString) return null
  return new Date(`${dateString}T00:00:00`)
}

function applyProgramContext() {
  if (isEditMode.value || !route.query.program || !programs.value.length) return

  const requestedProgram = String(route.query.program)
  const matchedProgram = programs.value.find((program) => (
    String(program.id) === requestedProgram ||
    normalizeProgramMatch(program.name) === normalizeProgramMatch(requestedProgram)
  ))

  if (matchedProgram) {
    form.value.program = matchedProgram.id
  }
}

function buildProgramQueryParams() {
  const base = { is_active: true, ordering: 'name' }
  if (isEditMode.value) return base
  const p = { ...base }
  const f = programFilters.value
  if (f.ordering) p.ordering = f.ordering
  const q = (f.search || '').trim()
  if (q) p.search = q
  const lang = (f.required_language || '').trim()
  if (lang) p.required_language = lang
  if (f.min_language_level) p.min_language_level = f.min_language_level
  if (f.start_date_after) p.start_date_after = f.start_date_after
  if (f.start_date_before) p.start_date_before = f.start_date_before
  if (f.min_gpa_max !== '' && f.min_gpa_max != null) {
    const n = Number(f.min_gpa_max)
    if (!Number.isNaN(n)) p.min_gpa_max = n
  }
  if (f.accepting_applications) p.accepting_applications = true
  return p
}

function clearProgramFilters() {
  if (programFilterDebounce != null) {
    clearTimeout(programFilterDebounce)
    programFilterDebounce = null
  }
  suppressProgramFilterWatch = true
  programFilters.value = deserializeApplicationProgramFilters({})
  fetchPrograms().finally(() => {
    suppressProgramFilterWatch = false
  })
}

function saveProgramFilterPreset() {
  savePresetToApi(() => serializeApplicationProgramFilters(programFilters.value))
}

function applyProgramFilterPreset(p) {
  if (programFilterDebounce != null) {
    clearTimeout(programFilterDebounce)
    programFilterDebounce = null
  }
  suppressProgramFilterWatch = true
  programFilters.value = deserializeApplicationProgramFilters(p.filters)
  fetchPrograms().finally(() => {
    suppressProgramFilterWatch = false
  })
}

async function fetchPrograms() {
  if (!isEditMode.value) programsLoading.value = true
  try {
    loadingMessage.value = 'Loading programs...'
    const response = await api.get('/api/programs/', {
      params: buildProgramQueryParams(),
    })
    const list = response.data.results || response.data
    programs.value = Array.isArray(list) ? list : []
    if (
      form.value.program
      && !programs.value.some((pr) => String(pr.id) === String(form.value.program))
    ) {
      form.value.program = ''
    }
  } catch (err) {
    console.error('Failed to fetch programs:', err)
    errorToast('Failed to load programs')
  } finally {
    programsLoading.value = false
  }
}

function resetDynamicForm() {
  dynamicForm.value = {
    id: null,
    name: '',
    description: '',
    schema: {},
    ui_schema: {},
    required_fields: [],
    multi_step: false,
    steps: [],
  }
  dynamicFormValues.value = {}
  dynamicFieldErrors.value = {}
  dynamicFormErrors.value = []
  dynamicFormLoadError.value = ''
  currentStepIndex.value = 0
}

function syncStepFromApplicationLayout() {
  const layout = applicationDynamicLayout.value
  if (!layout?.multi_step || !layout.steps?.length) {
    currentStepIndex.value = 0
    return
  }
  const idx = layout.steps.findIndex((s) => s.key === layout.current_step)
  currentStepIndex.value = idx >= 0 ? idx : 0
}

function goToPreviousStep() {
  if (currentStepIndex.value > 0) {
    currentStepIndex.value -= 1
  }
}

function normalizeInitialFieldValue(field, value) {
  if (value === undefined || value === null) {
    if (field.type === 'array') return []
    if (field.type === 'boolean') return false
    return ''
  }

  if (field.type === 'array') {
    return Array.isArray(value) ? value : [value]
  }

  if (field.type === 'boolean') {
    return Boolean(value)
  }

  if (field.type === 'number' || field.type === 'integer') {
    return typeof value === 'number' ? value : Number(value)
  }

  return value
}

function initializeDynamicFormValues(schema, responses = {}) {
  const nextValues = {}
  const properties = schema?.properties || {}

  for (const [name, config] of Object.entries(properties)) {
    nextValues[name] = normalizeInitialFieldValue(config, responses[name])
  }

  dynamicFormValues.value = nextValues
  dynamicFieldErrors.value = {}
}

async function loadDynamicForm(formTypeId, responses = null) {
  if (!formTypeId) {
    resetDynamicForm()
    return
  }

  dynamicFormLoading.value = true
  dynamicFormLoadError.value = ''
  dynamicFormErrors.value = []

  try {
    const response = await api.get(`/api/application-forms/form-types/${formTypeId}/form_schema/`)
    dynamicForm.value = {
      ...response.data,
      multi_step: Boolean(response.data.multi_step),
      steps: Array.isArray(response.data.steps) ? response.data.steps : [],
    }
    initializeDynamicFormValues(response.data.schema, responses || {})
    syncStepFromApplicationLayout()
  } catch (err) {
    console.error('Failed to load dynamic form schema:', err)
    resetDynamicForm()
    dynamicFormLoadError.value = 'Failed to load additional program questions.'
  } finally {
    dynamicFormLoading.value = false
  }
}

async function fetchApplication() {
  if (!isEditMode.value) return

  try {
    loadingMessage.value = 'Loading application...'
    const response = await api.get(`/api/applications/${route.params.id}/`)
    
    form.value = {
      program: response.data.program?.id || response.data.program,
    }
    pendingDynamicResponses.value = response.data.dynamic_form_submission?.responses || null
    applicationDynamicLayout.value = response.data.dynamic_form_layout || null
  } catch (err) {
    console.error('Failed to fetch application:', err)
    errorToast('Failed to load application')
    router.push({ name: 'Applications' })
  }
}

function isSelectField(field) {
  return field.config.type === 'string' && Array.isArray(field.config.enum)
}

function isArrayField(field) {
  return field.config.type === 'array' && Array.isArray(field.config.items?.enum)
}

function isBooleanField(field) {
  return field.config.type === 'boolean'
}

function isNumericField(field) {
  return field.config.type === 'number' || field.config.type === 'integer'
}

function isTextareaField(field) {
  return !isSelectField(field)
    && field.config.type === 'string'
    && (
      field.config.maxLength > 200
      || dynamicForm.value.ui_schema?.[field.name]?.['ui:widget'] === 'textarea'
    )
}

function getFieldOptions(field) {
  if (isSelectField(field)) return field.config.enum
  if (isArrayField(field)) return field.config.items.enum
  return []
}

function getFieldPlaceholder(field) {
  return dynamicForm.value.ui_schema?.[field.name]?.['ui:placeholder'] || ''
}

function getTextareaRows(field) {
  return dynamicForm.value.ui_schema?.[field.name]?.['ui:rows'] || 4
}

function getInputType(field) {
  if (isNumericField(field)) return 'number'

  switch (field.config.format) {
    case 'email':
      return 'email'
    case 'url':
      return 'url'
    case 'date':
      return 'date'
    case 'datetime':
      return 'datetime-local'
    default:
      return 'text'
  }
}

function hasValue(value, field) {
  if (field.config.type === 'boolean') return value === true || value === false
  if (field.config.type === 'array') return Array.isArray(value) && value.length > 0
  return value !== null && value !== undefined && String(value).trim() !== ''
}

function validateDynamicForm(fieldList) {
  const nextErrors = {}
  const list = fieldList || dynamicFields.value

  for (const field of list) {
    if (field.required && !hasValue(dynamicFormValues.value[field.name], field)) {
      nextErrors[field.name] = 'This field is required.'
    }
  }

  dynamicFieldErrors.value = nextErrors
  return Object.keys(nextErrors).length === 0
}

function buildDynamicPayload(fieldList) {
  const payload = {}
  const list = fieldList || dynamicFields.value

  for (const field of list) {
    const value = dynamicFormValues.value[field.name]
    if (!hasValue(value, field)) continue
    payload[`df_${field.name}`] = value
  }

  return payload
}

async function handleSubmit() {
  errors.value = {}
  dynamicFormErrors.value = []

  if (hasDynamicFields.value) {
    if (isMultiStep.value && !isLastStep.value) {
      if (!validateDynamicForm(visibleDynamicFields.value)) {
        errorToast('Please fix the errors in the form')
        return
      }
    } else if (!validateDynamicForm(dynamicFields.value)) {
      errorToast('Please fix the errors in the form')
      return
    }
  }

  submitting.value = true

  try {
    const useMulti = isMultiStep.value
    const fieldsForPayload = useMulti ? visibleDynamicFields.value : dynamicFields.value
    const data = {
      program: form.value.program,
      ...buildDynamicPayload(fieldsForPayload),
    }
    if (useMulti && currentStepKey.value) {
      data.dynamic_form_current_step = currentStepKey.value
    }

    let response
    if (isEditMode.value) {
      response = await api.patch(`/api/applications/${route.params.id}/`, data)
      success('Application updated successfully!')
    } else {
      response = await api.post('/api/applications/', data)
      success('Application created successfully!')
    }

    if (useMulti && !isLastStep.value) {
      if (!isEditMode.value) {
        await router.replace({ name: 'ApplicationEdit', params: { id: response.data.id } })
      }
      applicationDynamicLayout.value = response.data.dynamic_form_layout || applicationDynamicLayout.value
      syncStepFromApplicationLayout()
      dynamicFieldErrors.value = {}
    } else {
      router.push({ name: 'ApplicationDetail', params: { id: response.data.id } })
    }
  } catch (err) {
    console.error('Failed to save application:', err)
    
    if (err.response?.data) {
      errors.value = err.response.data
      dynamicFormErrors.value = Array.isArray(err.response.data.dynamic_form)
        ? err.response.data.dynamic_form
        : (err.response.data.dynamic_form ? [err.response.data.dynamic_form] : [])
      errorToast('Please fix the errors in the form')
    } else {
      errorToast('Failed to save application')
    }
  } finally {
    submitting.value = false
  }
}

async function saveDraft() {
  errors.value = {}
  dynamicFormErrors.value = []

  if (hasDynamicFields.value && isMultiStep.value) {
    if (!validateDynamicForm(visibleDynamicFields.value)) {
      errorToast('Please fix the errors in the form')
      return
    }
  } else if (hasDynamicFields.value && !validateDynamicForm(dynamicFields.value)) {
    errorToast('Please fix the errors in the form')
    return
  }

  submitting.value = true
  try {
    const useMulti = isMultiStep.value
    const fieldsForPayload = useMulti ? visibleDynamicFields.value : dynamicFields.value
    const data = {
      program: form.value.program,
      ...buildDynamicPayload(fieldsForPayload),
    }
    if (useMulti && currentStepKey.value) {
      data.dynamic_form_current_step = currentStepKey.value
    }

    let response
    if (isEditMode.value) {
      response = await api.patch(`/api/applications/${route.params.id}/`, data)
    } else {
      response = await api.post('/api/applications/', data)
    }
    success('Draft saved.')
    applicationDynamicLayout.value = response.data.dynamic_form_layout || applicationDynamicLayout.value
    if (useMulti) {
      syncStepFromApplicationLayout()
      if (!isEditMode.value && response.data?.id) {
        await router.replace({ name: 'ApplicationEdit', params: { id: response.data.id } })
      }
    } else {
      router.push({ name: 'ApplicationDetail', params: { id: response.data.id } })
    }
  } catch (err) {
    console.error('Failed to save draft:', err)
    if (err.response?.data) {
      errors.value = err.response.data
      dynamicFormErrors.value = Array.isArray(err.response.data.dynamic_form)
        ? err.response.data.dynamic_form
        : (err.response.data.dynamic_form ? [err.response.data.dynamic_form] : [])
      errorToast('Please fix the errors in the form')
    } else {
      errorToast('Failed to save draft')
    }
  } finally {
    submitting.value = false
  }
}

function formatDate(dateString) {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

function calculateDuration(startDate, endDate) {
  if (!startDate || !endDate) return 'N/A'
  
  const start = new Date(startDate)
  const end = new Date(endDate)
  const days = Math.ceil((end - start) / (1000 * 60 * 60 * 24))
  const months = Math.round(days / 30)
  
  if (months < 2) return `${days} days`
  return `${months} months`
}

onMounted(async () => {
  loading.value = true

  if (!isEditMode.value) {
    await loadPresets()
    const defaultPreset = savedPresets.value.find((preset) => preset.is_default)
    if (defaultPreset) {
      programFilters.value = deserializeApplicationProgramFilters(defaultPreset.filters)
    }
  }

  await fetchPrograms()
  applyProgramContext()

  if (isEditMode.value) {
    await fetchApplication()
  }

  loading.value = false
})

watch(
  programFilters,
  () => {
    if (suppressProgramFilterWatch || isEditMode.value) return
    if (programFilterDebounce != null) clearTimeout(programFilterDebounce)
    programFilterDebounce = setTimeout(() => {
      programFilterDebounce = null
      fetchPrograms()
    }, 400)
  },
  { deep: true },
)

watch(
  () => selectedProgram.value?.application_form || null,
  async (formTypeId, previousFormTypeId) => {
    if (!formTypeId) {
      resetDynamicForm()
      pendingDynamicResponses.value = null
      applicationDynamicLayout.value = null
      return
    }

    if (previousFormTypeId !== formTypeId) {
      currentStepIndex.value = 0
    }

    const responses = previousFormTypeId === formTypeId
      ? dynamicFormValues.value
      : (pendingDynamicResponses.value || {})

    await loadDynamicForm(formTypeId, responses)
    pendingDynamicResponses.value = null
  }
)
</script>

<style scoped>
.application-form-page {
  min-height: 100vh;
  background-color: #f8f9fa;
}

.form-label {
  font-weight: 500;
}

.alert-info {
  background-color: #e7f3ff;
  border-color: #b3d7ff;
}

.card {
  border: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.alert-heading {
  font-size: 0.95rem;
  font-weight: 600;
}

.alert ul {
  font-size: 0.9rem;
}
</style>
