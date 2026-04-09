<template>
  <div class="document-upload">
    <div class="card">
      <div class="card-header">
        <h6 class="mb-0"><i class="bi bi-cloud-upload me-2" aria-hidden="true"></i>{{ t('documentUpload.cardTitle') }}</h6>
      </div>
      <div class="card-body">
        <form @submit.prevent="handleSubmit">
          <div class="mb-3">
            <label class="form-label">{{ t('documentDetailPage.labelDocumentType') }} <span class="text-danger">*</span></label>
            <select
              v-model="form.type"
              class="form-select"
              :class="{ 'is-invalid': errors.type }"
              required
              data-testid="document-type-select"
            >
              <option value="">{{ t('documentUpload.selectTypePlaceholder') }}</option>
              <option v-for="dt in documentTypes" :key="dt.id" :value="dt.id">
                {{ dt.name }}
              </option>
            </select>
            <div v-if="errors.type" class="invalid-feedback">{{ errors.type }}</div>
          </div>

          <div class="mb-3">
            <label class="form-label">{{ t('documentUpload.fileLabel') }} <span class="text-danger">*</span></label>
            <input
              ref="fileInput"
              type="file"
              class="form-control"
              :class="{ 'is-invalid': errors.file }"
              accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
              @change="onFileChange"
              data-testid="document-file-input"
            />
            <div v-if="errors.file" class="invalid-feedback">{{ errors.file }}</div>
            <div class="form-text">{{ t('documentUpload.acceptedHint') }}</div>
          </div>

          <div v-if="uploadError" class="alert alert-danger small">
            {{ uploadError }}
          </div>

          <button
            type="submit"
            class="btn btn-primary w-100"
            :disabled="uploading || !form.type || !form.file"
            data-testid="document-upload-btn"
          >
            <span v-if="uploading">
              <span class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>
              {{ t('documentUpload.uploading') }}
            </span>
            <span v-else>
              <i class="bi bi-cloud-upload me-2" aria-hidden="true"></i>{{ t('documentUpload.submit') }}
            </span>
          </button>
        </form>
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

const props = defineProps({
  applicationId: {
    type: String,
    required: true,
  },
})

const emit = defineEmits(['uploaded'])

const { success, error: errorToast } = useToast()

const documentTypes = ref([])
const form = ref({
  type: '',
  file: null,
})
const errors = ref({})
const uploading = ref(false)
const uploadError = ref('')
const fileInput = ref(null)

async function fetchDocumentTypes() {
  try {
    const response = await api.get('/api/document-types/')
    documentTypes.value = response.data.results || response.data
  } catch (err) {
    console.error('Failed to fetch document types:', err)
    errorToast(t('documentUpload.toastTypesError'))
  }
}

function onFileChange(event) {
  const file = event.target.files?.[0]
  form.value.file = file || null
  uploadError.value = ''
  errors.value.file = null
}

async function handleSubmit() {
  errors.value = {}
  uploadError.value = ''

  if (!form.value.type) {
    errors.value.type = t('documentUpload.typeRequired')
    return
  }
  if (!form.value.file) {
    errors.value.file = t('documentUpload.fileRequired')
    return
  }

  uploading.value = true

  try {
    const formData = new FormData()
    formData.append('application', props.applicationId)
    formData.append('type', form.value.type)
    formData.append('file', form.value.file)

    await api.post('/api/documents/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    success(t('documentUpload.toastSuccess'))
    form.value = { type: '', file: null }
    if (fileInput.value) fileInput.value.value = ''
    emit('uploaded')
  } catch (err) {
    console.error('Upload failed:', err)
    uploadError.value =
      err.response?.data?.file?.[0] || err.response?.data?.detail || t('documentUpload.uploadErrorGeneric')
    errorToast(t('documentUpload.toastFailed'))
  } finally {
    uploading.value = false
  }
}

onMounted(() => {
  fetchDocumentTypes()
})
</script>

<style scoped>
.document-upload .card {
  border: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}
</style>
