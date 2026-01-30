<template>
  <div class="application-form-page">
    <div class="container-fluid mt-4">
      <!-- Breadcrumb -->
      <nav aria-label="breadcrumb">
        <ol class="breadcrumb">
          <li class="breadcrumb-item">
            <router-link to="/dashboard">Dashboard</router-link>
          </li>
          <li class="breadcrumb-item">
            <router-link to="/applications">Applications</router-link>
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
              <form @submit.prevent="handleSubmit">
                <!-- Program Selection -->
                <div class="mb-4">
                  <label for="program" class="form-label">
                    Exchange Program <span class="text-danger">*</span>
                  </label>
                  <select
                    id="program"
                    v-model="form.program"
                    class="form-select"
                    :class="{ 'is-invalid': errors.program }"
                    required
                    :disabled="isEditMode"
                  >
                    <option value="">-- Select a Program --</option>
                    <option v-for="program in programs" :key="program.id" :value="program.id">
                      {{ program.name }}
                    </option>
                  </select>
                  <div v-if="errors.program" class="invalid-feedback">{{ errors.program }}</div>
                  <div class="form-text">
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
                  <div v-if="selectedProgram.min_gpa" class="mt-2 small">
                    <strong>Requirements:</strong> Min GPA: {{ selectedProgram.min_gpa }}
                    <span v-if="selectedProgram.required_language">
                      | {{ selectedProgram.required_language }} ({{ selectedProgram.min_language_level }})
                    </span>
                  </div>
                </div>

                <!-- Personal Statement (Optional) -->
                <div class="mb-4">
                  <label for="statement" class="form-label">
                    Personal Statement <span class="text-muted small">(Optional)</span>
                  </label>
                  <textarea
                    id="statement"
                    v-model="form.statement"
                    class="form-control"
                    rows="6"
                    :class="{ 'is-invalid': errors.statement }"
                    placeholder="Explain why you want to participate in this exchange program..."
                  ></textarea>
                  <div v-if="errors.statement" class="invalid-feedback">{{ errors.statement }}</div>
                  <div class="form-text">
                    Share your motivation and goals for this exchange program
                  </div>
                </div>

                <!-- Error Messages -->
                <div v-if="Object.keys(errors).length > 0 && !errors.program && !errors.statement" class="alert alert-danger">
                  <h6 class="alert-heading">Please fix the following errors:</h6>
                  <ul class="mb-0">
                    <li v-for="(error, field) in errors" :key="field">{{ error }}</li>
                  </ul>
                </div>

                <!-- Actions -->
                <div class="d-flex justify-content-between">
                  <router-link to="/applications" class="btn btn-outline-secondary">
                    <i class="bi bi-x-circle me-2"></i>Cancel
                  </router-link>
                  <div>
                    <button
                      type="button"
                      class="btn btn-outline-primary me-2"
                      @click="saveDraft"
                      :disabled="submitting || !form.program"
                    >
                      <i class="bi bi-save me-2"></i>Save as Draft
                    </button>
                    <button
                      type="submit"
                      class="btn btn-primary"
                      :disabled="submitting || !form.program"
                    >
                      <span v-if="submitting">
                        <span class="spinner-border spinner-border-sm me-2"></span>
                        {{ isEditMode ? 'Updating...' : 'Creating...' }}
                      </span>
                      <span v-else>
                        <i class="bi bi-check-circle me-2"></i>
                        {{ isEditMode ? 'Update Application' : 'Create Application' }}
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
                <li>Write a compelling personal statement</li>
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
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'
import api from '@/services/api'

const route = useRoute()
const router = useRouter()
const { success, error: errorToast } = useToast()

const isEditMode = computed(() => route.params.id !== undefined)
const loading = ref(true)
const loadingMessage = ref('Loading...')
const submitting = ref(false)

const programs = ref([])
const form = ref({
  program: '',
  statement: '',
})

const errors = ref({})

const selectedProgram = computed(() => {
  if (!form.value.program) return null
  return programs.value.find(p => p.id === form.value.program)
})

async function fetchPrograms() {
  try {
    loadingMessage.value = 'Loading programs...'
    const response = await api.get('/api/programs/', {
      params: { is_active: true, ordering: 'name' }
    })
    programs.value = response.data.results || response.data
  } catch (err) {
    console.error('Failed to fetch programs:', err)
    errorToast('Failed to load programs')
  }
}

async function fetchApplication() {
  if (!isEditMode.value) return

  try {
    loadingMessage.value = 'Loading application...'
    const response = await api.get(`/api/applications/${route.params.id}/`)
    
    form.value = {
      program: response.data.program?.id || response.data.program,
      statement: response.data.statement || '',
    }
  } catch (err) {
    console.error('Failed to fetch application:', err)
    errorToast('Failed to load application')
    router.push('/applications')
  }
}

async function handleSubmit() {
  errors.value = {}
  submitting.value = true

  try {
    const data = {
      program: form.value.program,
      statement: form.value.statement || null,
    }

    let response
    if (isEditMode.value) {
      response = await api.patch(`/api/applications/${route.params.id}/`, data)
      success('Application updated successfully!')
    } else {
      response = await api.post('/api/applications/', data)
      success('Application created successfully!')
    }

    router.push(`/applications/${response.data.id}`)
  } catch (err) {
    console.error('Failed to save application:', err)
    
    if (err.response?.data) {
      errors.value = err.response.data
      errorToast('Please fix the errors in the form')
    } else {
      errorToast('Failed to save application')
    }
  } finally {
    submitting.value = false
  }
}

async function saveDraft() {
  // Draft is the default status, so just use handleSubmit
  await handleSubmit()
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
  
  await fetchPrograms()
  
  if (isEditMode.value) {
    await fetchApplication()
  }
  
  loading.value = false
})
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
</style>
