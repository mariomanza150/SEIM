<template>
  <div class="document-upload">
    <div class="card">
      <div class="card-header">
        <h6 class="mb-0"><i class="bi bi-cloud-upload me-2" aria-hidden="true"></i>{{ t('documentUpload.cardTitle') }}</h6>
      </div>
      <div class="card-body">
        <p
          v-if="nothingToUpload"
          class="text-muted small mb-0"
          data-testid="document-upload-empty"
        >
          {{ t('documentUpload.nothingToUpload') }}
        </p>
        <form v-else @submit.prevent="handleSubmit">
          <div class="mb-3">
            <label class="form-label">{{ t('documentDetailPage.labelDocumentType') }} <span class="text-danger">*</span></label>
            <select
              ref="typeSelect"
              v-model="form.type"
              class="form-select"
              :class="{ 'is-invalid': errors.type }"
              required
              data-testid="document-type-select"
            >
              <option value="">{{ t('documentUpload.selectTypePlaceholder') }}</option>
              <option v-for="dt in selectableTypes" :key="dt.id" :value="dt.id">
                {{ documentTypeLabel(dt, dt.name, { t, te }) }}
              </option>
            </select>
            <div v-if="errors.type" class="invalid-feedback">{{ errors.type }}</div>
          </div>

          <div v-if="selectedType" class="mb-3" data-testid="document-file-field">
            <label class="form-label">{{ t('documentUpload.fileLabel') }} <span class="text-danger">*</span></label>
            <input
              ref="fileInput"
              type="file"
              class="form-control"
              :class="{ 'is-invalid': errors.file }"
              :accept="fileAccept"
              @change="onFileChange"
              data-testid="document-file-input"
            />
            <div v-if="errors.file" class="invalid-feedback">{{ errors.file }}</div>
            <div
              v-if="acceptedHintText"
              class="form-text"
              data-testid="document-accepted-hint"
            >
              {{ acceptedHintText }}
            </div>
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
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { useToast } from '@/composables/useToast'
import api from '@/services/api'
import {
  acceptAttributeFromExtensions,
  checklistUploadTargets,
  documentTypeAcceptedExtensions,
  documentTypeAcceptedHintText,
  documentTypeLabel,
  validateDocumentFile,
} from '@/utils/documentApi'

const { t, te } = useI18n()

const props = defineProps({
  applicationId: {
    type: String,
    required: true,
  },
  /** When provided, type picker is limited to checklist upload gaps. */
  checklist: {
    type: Object,
    default: null,
  },
  /** Prefill document-type select (checklist shortcut / deep link). */
  preselectedTypeId: {
    type: [String, Number],
    default: null,
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
const typeSelect = ref(null)

const usesChecklistFilter = computed(
  () => props.checklist != null && Array.isArray(props.checklist.items),
)

const selectableTypes = computed(() => {
  if (usesChecklistFilter.value) {
    return checklistUploadTargets(props.checklist).map((item) => ({
      id: item.document_type_id,
      name: item.name,
      slug: item.slug,
      description: item.description,
      accepted_extensions: item.accepted_extensions || '',
      resolved_accepted_extensions: item.accepted_extensions || '',
      max_file_size_mb: item.max_file_size_mb ?? null,
      file_type_families: item.file_type_families || [],
      allows_multiple: Boolean(item.allows_multiple),
    }))
  }
  return documentTypes.value
})

const selectedType = computed(() => {
  if (!form.value.type) return null
  return selectableTypes.value.find((dt) => String(dt.id) === String(form.value.type)) || null
})

const acceptedExtensions = computed(() =>
  selectedType.value ? documentTypeAcceptedExtensions(selectedType.value) : [],
)

const fileAccept = computed(() => acceptAttributeFromExtensions(acceptedExtensions.value))

const acceptedHintText = computed(() =>
  documentTypeAcceptedHintText(selectedType.value, t),
)

const nothingToUpload = computed(
  () => usesChecklistFilter.value && selectableTypes.value.length === 0,
)

function clearSelectedFile() {
  form.value.file = null
  errors.value.file = null
  if (fileInput.value) fileInput.value.value = ''
}

function applyPreselectedType(typeId = props.preselectedTypeId) {
  if (typeId == null || typeId === '') return false
  const match = selectableTypes.value.find((dt) => String(dt.id) === String(typeId))
  if (!match) return false
  form.value.type = match.id
  errors.value.type = null
  return true
}

watch(selectableTypes, (types) => {
  if (form.value.type) {
    const stillAvailable = types.some((dt) => String(dt.id) === String(form.value.type))
    if (!stillAvailable) form.value.type = ''
  }
  applyPreselectedType()
})

watch(
  () => props.preselectedTypeId,
  () => {
    applyPreselectedType()
  },
)

watch(
  () => form.value.type,
  (next, prev) => {
    if (String(next || '') === String(prev || '')) return
    clearSelectedFile()
    uploadError.value = ''
  },
)

async function fetchDocumentTypes() {
  if (usesChecklistFilter.value) return
  try {
    const all = []
    let url = '/api/document-types/?page_size=100'
    while (url) {
      const response = await api.get(url)
      const data = response.data
      const list = data.results || data
      if (Array.isArray(list)) all.push(...list)
      const next = data && data.next
      url = next
        ? String(next).replace(/^https?:\/\/[^/]+/, '')
        : null
    }
    documentTypes.value = all
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
  if (!file || !selectedType.value) return
  const result = validateDocumentFile(file, selectedType.value)
  if (!result.ok) {
    errors.value.file = t(result.errorKey, result.params)
    form.value.file = null
    if (fileInput.value) fileInput.value.value = ''
  }
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

  const clientCheck = validateDocumentFile(form.value.file, selectedType.value)
  if (!clientCheck.ok) {
    errors.value.file = t(clientCheck.errorKey, clientCheck.params)
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
  applyPreselectedType()
})

watch(
  () => props.checklist,
  () => {
    if (!usesChecklistFilter.value) fetchDocumentTypes()
  },
)

function focusUploadForm() {
  applyPreselectedType()
  nextTick(() => {
    if (fileInput.value && typeof fileInput.value.focus === 'function') {
      fileInput.value.focus()
    } else if (typeSelect.value && typeof typeSelect.value.focus === 'function') {
      typeSelect.value.focus()
    }
  })
}

defineExpose({
  focusUploadForm,
  applyPreselectedType,
})
</script>

<style scoped>
.document-upload .card {
  border: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}
</style>
