<template>
  <div class="admin-dynform-editor">
    <PageHeader :title="formName || t('adminDynforms.builderTitle')" :subtitle="t('adminDynforms.builderSubtitle')">
      <template #breadcrumb>
        <nav aria-label="Breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item">
              <router-link :to="{ name: 'AdminDynforms' }">{{ t('route.names.AdminDynforms') }}</router-link>
            </li>
            <li class="breadcrumb-item active">{{ t('route.names.AdminDynformEditor') }}</li>
          </ol>
        </nav>
      </template>
      <template #actions>
        <button type="button" class="btn btn-outline-secondary" data-testid="dynforms-preview-toggle" @click="showPreview = !showPreview">
          {{ showPreview ? t('adminDynforms.hidePreview') : t('adminDynforms.showPreview') }}
        </button>
        <button type="button" class="btn btn-primary" :disabled="saving" data-testid="dynforms-save" @click="save">
          {{ t('adminCommon.save') }}
        </button>
      </template>
    </PageHeader>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">{{ t('adminCommon.loading') }}</span>
      </div>
    </div>
    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-else class="row g-3">
      <div class="col-lg-3">
        <div class="card">
          <div class="card-header">{{ t('adminDynforms.palette') }}</div>
          <div class="list-group list-group-flush">
            <button
              v-for="fieldType in fieldTypes"
              :key="fieldType.type"
              type="button"
              class="list-group-item list-group-item-action"
              :data-testid="`dynforms-add-${fieldType.type}`"
              @click="addField(fieldType.type)"
            >
              <i :class="`bi ${fieldType.icon} me-2`" aria-hidden="true"></i>
              <span class="fw-medium">{{ fieldType.name }}</span>
              <div class="small text-muted">{{ fieldType.desc }}</div>
            </button>
          </div>
        </div>
      </div>

      <div class="col-lg-5">
        <div class="card mb-3">
          <div class="card-body">
            <label class="form-label">{{ t('adminForms.fields.name') }}</label>
            <input v-model="formName" class="form-control mb-3" type="text" data-testid="dynforms-form-name" />
            <label class="form-label">{{ t('adminForms.fields.description') }}</label>
            <textarea v-model="formDescription" class="form-control" rows="2" />
          </div>
        </div>
        <div class="card">
          <div class="card-header">{{ t('adminDynforms.canvas') }}</div>
          <div class="list-group list-group-flush" data-testid="dynforms-canvas">
            <div v-if="!fields.length" class="list-group-item text-muted">{{ t('adminDynforms.emptyCanvas') }}</div>
            <div
              v-for="(field, index) in fields"
              :key="field.id"
              class="list-group-item list-group-item-action"
              :class="{ active: selectedId === field.id }"
              role="button"
              tabindex="0"
              :aria-pressed="selectedId === field.id ? 'true' : 'false'"
              @click="selectField(field.id)"
              @keydown.enter.prevent="selectField(field.id)"
              @keydown.space.prevent="selectField(field.id)"
            >
              <div class="d-flex justify-content-between align-items-start gap-2">
                <div>
                  <div class="fw-medium">{{ field.label }}</div>
                  <div class="small">{{ field.type }}{{ field.required ? ` · ${t('adminDynforms.required')}` : '' }}</div>
                </div>
                <div class="btn-group btn-group-sm">
                  <button type="button" class="btn btn-outline-secondary" :disabled="index === 0" @click.stop="moveField(index, -1)">↑</button>
                  <button type="button" class="btn btn-outline-secondary" :disabled="index === fields.length - 1" @click.stop="moveField(index, 1)">↓</button>
                  <button
                    type="button"
                    class="btn btn-outline-danger"
                    data-testid="dynforms-remove-field"
                    @click.stop="removeField(index)"
                  >
                    ×
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-lg-4">
        <div v-if="selected" :key="selected.id" class="card mb-3" data-testid="dynforms-field-settings">
          <div class="card-header">{{ t('adminDynforms.fieldSettings') }}</div>
          <div class="card-body">
            <label class="form-label" for="dynforms-field-label">{{ t('adminDynforms.fieldLabel') }}</label>
            <input
              id="dynforms-field-label"
              ref="labelInput"
              v-model="selected.label"
              class="form-control mb-3"
              type="text"
              data-testid="dynforms-field-label"
            />
            <div class="form-check mb-3">
              <input id="fieldRequired" v-model="selected.required" class="form-check-input" type="checkbox" />
              <label class="form-check-label" for="fieldRequired">{{ t('adminDynforms.required') }}</label>
            </div>
            <label class="form-label">{{ t('adminDynforms.placeholder') }}</label>
            <input v-model="selected.placeholder" class="form-control mb-3" type="text" />
            <label class="form-label">{{ t('adminDynforms.helpText') }}</label>
            <input v-model="selected.helpText" class="form-control mb-3" type="text" />
            <div v-if="selected.type === 'select' || selected.type === 'radio'">
              <label class="form-label">{{ t('adminDynforms.options') }}</label>
              <textarea
                class="form-control"
                rows="4"
                :value="optionsText"
                data-testid="dynforms-field-options"
                @input="setOptions($event.target.value)"
              />
              <div class="form-text">{{ t('adminDynforms.optionsHelp') }}</div>
            </div>
          </div>
        </div>

        <div v-if="showPreview" class="card" data-testid="dynforms-preview">
          <div class="card-header">{{ t('adminDynforms.preview') }}</div>
          <div class="card-body">
            <div v-if="!fields.length" class="text-muted">{{ t('adminDynforms.emptyCanvas') }}</div>
            <div v-for="field in fields" :key="`preview-${field.id}`" class="mb-3">
              <label class="form-label">
                {{ field.label }}
                <span v-if="field.required" class="text-danger">*</span>
              </label>
              <textarea v-if="field.type === 'textarea'" class="form-control" rows="3" :placeholder="field.placeholder" disabled />
              <select v-else-if="field.type === 'select'" class="form-select" disabled>
                <option v-for="opt in field.options" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
              </select>
              <div v-else-if="field.type === 'radio'">
                <div v-for="opt in field.options" :key="opt.value" class="form-check">
                  <input class="form-check-input" type="radio" disabled />
                  <label class="form-check-label">{{ opt.label }}</label>
                </div>
              </div>
              <div v-else-if="field.type === 'checkbox'" class="form-check">
                <input class="form-check-input" type="checkbox" disabled />
                <label class="form-check-label">{{ field.label }}</label>
              </div>
              <input v-else class="form-control" :type="field.type === 'file' ? 'file' : field.type" :placeholder="field.placeholder" disabled />
              <div v-if="field.helpText" class="form-text">{{ field.helpText }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import PageHeader from '@/components/PageHeader.vue'
import api from '@/services/api'
import { useToast } from '@/composables/useToast'
import { FIELD_TYPES, createField, fieldsFromSchema, schemaFromFields } from '@/utils/formBuilderSchema'

const { t } = useI18n()
const route = useRoute()
const { success, error: errorToast } = useToast()

const fieldTypes = FIELD_TYPES
const loading = ref(true)
const saving = ref(false)
const error = ref(null)
const formName = ref('')
const formDescription = ref('')
const formType = ref('application')
const isActive = ref(true)
const stepDefinitions = ref([])
const fields = ref([])
const selectedId = ref(null)
const showPreview = ref(true)
const labelInput = ref(null)

const selected = computed(() => fields.value.find((field) => field.id === selectedId.value) || null)
const optionsText = computed(() =>
  (selected.value?.options || []).map((opt) => `${opt.label}|${opt.value}`).join('\n'),
)

async function selectField(id) {
  selectedId.value = id
  await nextTick()
  labelInput.value?.focus?.()
  labelInput.value?.select?.()
}

function addField(type) {
  const field = createField(type)
  fields.value.push(field)
  selectField(field.id)
}

function removeField(index) {
  const [removed] = fields.value.splice(index, 1)
  if (selectedId.value === removed?.id) {
    const nextId = fields.value[0]?.id || null
    if (nextId) selectField(nextId)
    else selectedId.value = null
  }
}

function moveField(index, delta) {
  const next = index + delta
  if (next < 0 || next >= fields.value.length) return
  const copy = [...fields.value]
  const [item] = copy.splice(index, 1)
  copy.splice(next, 0, item)
  fields.value = copy
}

function setOptions(text) {
  if (!selected.value) return
  selected.value.options = text
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => {
      const [label, value] = line.split('|')
      return { label: (label || value || '').trim(), value: (value || label || '').trim() }
    })
}

async function load() {
  loading.value = true
  error.value = null
  try {
    const response = await api.get(`/api/application-forms/form-types/${route.params.id}/`)
    const ft = response.data || {}
    formName.value = ft.name || ''
    formDescription.value = ft.description || ''
    formType.value = ft.form_type || 'application'
    isActive.value = Boolean(ft.is_active)
    stepDefinitions.value = ft.step_definitions || []
    fields.value = fieldsFromSchema(ft.schema || {}, ft.ui_schema || {})
    selectedId.value = fields.value[0]?.id || null
  } catch {
    error.value = t('adminDynforms.loadDetailError')
  } finally {
    loading.value = false
  }
}

async function save() {
  saving.value = true
  try {
    const { schema, uiSchema } = schemaFromFields(fields.value)
    await api.patch(`/api/application-forms/form-types/${route.params.id}/`, {
      name: formName.value,
      description: formDescription.value,
      form_type: formType.value,
      is_active: isActive.value,
      schema,
      ui_schema: uiSchema,
      step_definitions: stepDefinitions.value,
    })
    success(t('adminDynforms.toastSaved'))
  } catch {
    errorToast(t('adminDynforms.saveError'))
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>
