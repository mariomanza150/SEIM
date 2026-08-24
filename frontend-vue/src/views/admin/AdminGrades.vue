<template>
  <div class="admin-grades-page">
    <PageHeader :title="t('adminGrades.title')" :subtitle="t('adminGrades.subtitle')">
      <template #breadcrumb>
        <PageBreadcrumb
          :aria-label="t('adminCommon.breadcrumbAria')"
          :items="[
            { to: { name: 'Dashboard' }, label: t('route.names.Dashboard') },
            { label: t('route.names.AdminGrades') },
          ]"
        />
      </template>
      <template #actions>
        <button type="button" class="btn btn-outline-secondary" :disabled="loading" @click="reload">
          <i class="bi bi-arrow-clockwise me-1" aria-hidden="true"></i>{{ t('adminCommon.refresh') }}
        </button>
      </template>
    </PageHeader>

    <PageStateShell
      :loading="loading"
      :error="error || ''"
      skeleton="none"
      :loading-label="t('adminCommon.loading')"
    >
    <div class="row g-3 mb-4">
        <div class="col-lg-4">
          <div class="card mb-3" data-testid="admin-grades-create-scale">
            <div class="card-header fw-medium">{{ t('adminGrades.createScale') }}</div>
            <div class="card-body">
              <div class="mb-2">
                <label class="form-label">{{ t('adminGrades.fields.name') }}</label>
                <input v-model="newScale.name" class="form-control" type="text" />
              </div>
              <div class="mb-2">
                <label class="form-label">{{ t('adminGrades.fields.code') }}</label>
                <input v-model="newScale.code" class="form-control" type="text" />
              </div>
              <div class="mb-2">
                <label class="form-label">{{ t('adminGrades.fields.country') }}</label>
                <SearchableSelect
                  v-model="newScale.country"
                  :options="countryOptions"
                  :placeholder="t('adminGrades.countryPlaceholder')"
                />
              </div>
              <div class="mb-2">
                <label class="form-label">{{ t('adminGrades.fields.description') }}</label>
                <textarea v-model="newScale.description" class="form-control" rows="2" />
              </div>
              <div class="row g-2 mb-2">
                <div class="col-4">
                  <label class="form-label">{{ t('adminGrades.fields.minValue') }}</label>
                  <input v-model.number="newScale.min_value" class="form-control" type="number" step="any" />
                </div>
                <div class="col-4">
                  <label class="form-label">{{ t('adminGrades.fields.maxValue') }}</label>
                  <input v-model.number="newScale.max_value" class="form-control" type="number" step="any" />
                </div>
                <div class="col-4">
                  <label class="form-label">{{ t('adminGrades.fields.passingValue') }}</label>
                  <input v-model.number="newScale.passing_value" class="form-control" type="number" step="any" />
                </div>
              </div>
              <div class="form-check mb-2">
                <input id="newScaleActive" v-model="newScale.is_active" class="form-check-input" type="checkbox" />
                <label class="form-check-label" for="newScaleActive">{{ t('adminGrades.fields.active') }}</label>
              </div>
              <div class="form-check mb-3">
                <input id="newScaleReverse" v-model="newScale.is_reverse_scale" class="form-check-input" type="checkbox" />
                <label class="form-check-label" for="newScaleReverse">{{ t('adminGrades.fields.reverse') }}</label>
              </div>
              <button
                type="button"
                class="btn btn-primary w-100"
                :disabled="busy || !newScale.name || !newScale.code"
                @click="createScale"
              >
                {{ t('adminCommon.save') }}
              </button>
            </div>
          </div>

          <div class="card" data-testid="admin-grades-scales">
            <div class="card-header fw-medium">{{ t('adminGrades.scales') }}</div>
            <div class="list-group list-group-flush">
              <div v-if="!scales.length" class="list-group-item text-muted">
                {{ t('adminGrades.emptyScales') }}
              </div>
              <button
                v-for="scale in scales"
                :key="scale.id"
                type="button"
                class="list-group-item list-group-item-action"
                :class="{ active: selectedId === scale.id }"
                @click="selectScale(scale)"
              >
                <div class="fw-medium">{{ scale.name }}</div>
                <div class="small opacity-75">{{ scale.code }} · {{ scale.country || t('adminCommon.notSet') }}</div>
              </button>
            </div>
          </div>
        </div>

        <div class="col-lg-8">
          <div v-if="!selectedId" class="alert alert-light border">
            {{ t('adminGrades.selectScale') }}
          </div>
          <template v-else>
            <div class="card mb-3">
              <div class="card-header d-flex flex-wrap gap-2 align-items-center">
                <span class="fw-medium me-auto">{{ scaleForm.name }}</span>
                <span class="badge" :class="scaleForm.is_active ? 'bg-success' : 'bg-secondary'">
                  {{ scaleForm.is_active ? t('adminCommon.yes') : t('adminCommon.no') }}
                </span>
                <button type="button" class="btn btn-sm btn-outline-secondary" :disabled="busy" @click="saveScale">
                  {{ t('adminCommon.save') }}
                </button>
                <button type="button" class="btn btn-sm btn-outline-danger" :disabled="busy" @click="deleteScale">
                  {{ t('adminCommon.delete') }}
                </button>
              </div>
              <div class="card-body">
                <div class="row g-3">
                  <div class="col-md-6">
                    <label class="form-label">{{ t('adminGrades.fields.name') }}</label>
                    <input v-model="scaleForm.name" class="form-control" type="text" />
                  </div>
                  <div class="col-md-3">
                    <label class="form-label">{{ t('adminGrades.fields.code') }}</label>
                    <input v-model="scaleForm.code" class="form-control" type="text" />
                  </div>
                  <div class="col-md-3">
                    <label class="form-label">{{ t('adminGrades.fields.country') }}</label>
                    <SearchableSelect
                      v-model="scaleForm.country"
                      :options="countryOptions"
                      :placeholder="t('adminGrades.countryPlaceholder')"
                    />
                  </div>
                  <div class="col-12">
                    <label class="form-label">{{ t('adminGrades.fields.description') }}</label>
                    <textarea v-model="scaleForm.description" class="form-control" rows="2" />
                  </div>
                  <div class="col-md-4">
                    <label class="form-label">{{ t('adminGrades.fields.minValue') }}</label>
                    <input v-model.number="scaleForm.min_value" class="form-control" type="number" step="any" />
                  </div>
                  <div class="col-md-4">
                    <label class="form-label">{{ t('adminGrades.fields.maxValue') }}</label>
                    <input v-model.number="scaleForm.max_value" class="form-control" type="number" step="any" />
                  </div>
                  <div class="col-md-4">
                    <label class="form-label">{{ t('adminGrades.fields.passingValue') }}</label>
                    <input v-model.number="scaleForm.passing_value" class="form-control" type="number" step="any" />
                  </div>
                  <div class="col-md-6">
                    <div class="form-check">
                      <input id="scaleActive" v-model="scaleForm.is_active" class="form-check-input" type="checkbox" />
                      <label class="form-check-label" for="scaleActive">{{ t('adminGrades.fields.active') }}</label>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="form-check">
                      <input id="scaleReverse" v-model="scaleForm.is_reverse_scale" class="form-check-input" type="checkbox" />
                      <label class="form-check-label" for="scaleReverse">{{ t('adminGrades.fields.reverse') }}</label>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="card" data-testid="admin-grades-values">
              <div class="card-header fw-medium">{{ t('adminGrades.values') }}</div>
              <div class="card-body">
                <div v-if="!values.length" class="text-muted mb-3">{{ t('adminGrades.emptyValues') }}</div>
                <div v-else class="table-responsive mb-3">
                  <ResponsiveList :items="values" :columns="valueMobileColumns" mobile-test-id="admin-grades-values-mobile">
                  <table class="table table-sm align-middle">
                    <thead>
                      <tr>
                        <th>{{ t('adminGrades.fields.label') }}</th>
                        <th>{{ t('adminGrades.fields.numericValue') }}</th>
                        <th>{{ t('adminGrades.fields.gpaEquivalent') }}</th>
                        <th>{{ t('adminGrades.fields.order') }}</th>
                        <th>{{ t('adminGrades.fields.isPassing') }}</th>
                        <th class="text-end">{{ t('adminCommon.actions') }}</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="value in values" :key="value.id">
                        <td><input v-model="value.label" class="form-control form-control-sm" type="text" /></td>
                        <td>
                          <input v-model.number="value.numeric_value" class="form-control form-control-sm" type="number" step="any" />
                        </td>
                        <td>
                          <input v-model.number="value.gpa_equivalent" class="form-control form-control-sm" type="number" step="any" />
                        </td>
                        <td>
                          <input v-model.number="value.order" class="form-control form-control-sm" type="number" />
                        </td>
                        <td>
                          <input v-model="value.is_passing" class="form-check-input" type="checkbox" />
                        </td>
                        <td class="text-end text-nowrap">
                          <button type="button" class="btn btn-sm btn-outline-secondary me-1" :disabled="busy" @click="saveValue(value)">
                            {{ t('adminCommon.save') }}
                          </button>
                          <button type="button" class="btn btn-sm btn-outline-danger" :disabled="busy" @click="deleteValue(value)">
                            {{ t('adminCommon.delete') }}
                          </button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                  <template #col-label="{ item }">
                    <input v-model="item.label" class="form-control form-control-sm" type="text" />
                  </template>
                  <template #col-numericValue="{ item }">
                    <input v-model.number="item.numeric_value" class="form-control form-control-sm" type="number" step="any" />
                  </template>
                  <template #col-gpaEquivalent="{ item }">
                    <input v-model.number="item.gpa_equivalent" class="form-control form-control-sm" type="number" step="any" />
                  </template>
                  <template #col-order="{ item }">
                    <input v-model.number="item.order" class="form-control form-control-sm" type="number" />
                  </template>
                  <template #col-isPassing="{ item }">
                    <input v-model="item.is_passing" class="form-check-input" type="checkbox" />
                  </template>
                  <template #actions="{ item }">
                    <button type="button" class="btn btn-sm btn-outline-secondary" :disabled="busy" @click="saveValue(item)">
                      {{ t('adminCommon.save') }}
                    </button>
                    <button type="button" class="btn btn-sm btn-outline-danger" :disabled="busy" @click="deleteValue(item)">
                      {{ t('adminCommon.delete') }}
                    </button>
                  </template>
                  </ResponsiveList>
                </div>
                <div class="row g-2 align-items-end">
                  <div class="col-md-3">
                    <label class="form-label">{{ t('adminGrades.fields.label') }}</label>
                    <input v-model="newValue.label" class="form-control" type="text" />
                  </div>
                  <div class="col-md-2">
                    <label class="form-label">{{ t('adminGrades.fields.numericValue') }}</label>
                    <input v-model.number="newValue.numeric_value" class="form-control" type="number" step="any" />
                  </div>
                  <div class="col-md-2">
                    <label class="form-label">{{ t('adminGrades.fields.gpaEquivalent') }}</label>
                    <input v-model.number="newValue.gpa_equivalent" class="form-control" type="number" step="any" />
                  </div>
                  <div class="col-md-2">
                    <label class="form-label">{{ t('adminGrades.fields.order') }}</label>
                    <input v-model.number="newValue.order" class="form-control" type="number" />
                  </div>
                  <div class="col-md-1">
                    <div class="form-check">
                      <input id="newValuePassing" v-model="newValue.is_passing" class="form-check-input" type="checkbox" />
                      <label class="form-check-label" for="newValuePassing">{{ t('adminGrades.fields.isPassing') }}</label>
                    </div>
                  </div>
                  <div class="col-md-2">
                    <button
                      type="button"
                      class="btn btn-outline-primary w-100"
                      :disabled="busy || !newValue.label"
                      @click="createValue"
                    >
                      {{ t('adminGrades.createValue') }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>

      <div class="card" data-testid="admin-grades-translations">
        <div class="card-header fw-medium">{{ t('adminGrades.translations') }}</div>
        <div class="card-body">
          <div v-if="!translations.length" class="text-muted mb-3">{{ t('adminGrades.emptyTranslations') }}</div>
          <div v-else class="table-responsive mb-3">
            <ResponsiveList :items="translations" :columns="translationMobileColumns" mobile-test-id="admin-grades-translations-mobile">
            <table class="table table-sm align-middle">
              <thead>
                <tr>
                  <th>{{ t('adminGrades.fields.sourceGrade') }}</th>
                  <th>{{ t('adminGrades.fields.targetGrade') }}</th>
                  <th>{{ t('adminGrades.fields.confidence') }}</th>
                  <th>{{ t('adminGrades.fields.notes') }}</th>
                  <th class="text-end">{{ t('adminCommon.actions') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="mapping in translations" :key="mapping.id">
                  <td>{{ gradeOptionLabel(mapping.source_grade, mapping.source_scale_code, mapping.source_grade_label) }}</td>
                  <td>{{ gradeOptionLabel(mapping.target_grade, mapping.target_scale_code, mapping.target_grade_label) }}</td>
                  <td>{{ mapping.confidence }}</td>
                  <td class="text-muted small">{{ mapping.notes }}</td>
                  <td class="text-end">
                    <button type="button" class="btn btn-sm btn-outline-danger" :disabled="busy" @click="deleteTranslation(mapping)">
                      {{ t('adminCommon.delete') }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
            <template #col-sourceGrade="{ item }">
              {{ gradeOptionLabel(item.source_grade, item.source_scale_code, item.source_grade_label) }}
            </template>
            <template #col-targetGrade="{ item }">
              {{ gradeOptionLabel(item.target_grade, item.target_scale_code, item.target_grade_label) }}
            </template>
            <template #col-confidence="{ item }">{{ item.confidence }}</template>
            <template #col-notes="{ item }"><span class="text-muted small">{{ item.notes }}</span></template>
            <template #actions="{ item }">
              <button type="button" class="btn btn-sm btn-outline-danger" :disabled="busy" @click="deleteTranslation(item)">
                {{ t('adminCommon.delete') }}
              </button>
            </template>
            </ResponsiveList>
          </div>
          <div class="row g-2 align-items-end">
            <div class="col-md-3">
              <label class="form-label">{{ t('adminGrades.fields.sourceGrade') }}</label>
              <select v-model="newTranslation.source_grade" class="form-select">
                <option value="">{{ t('adminGrades.selectScale') }}</option>
                <option v-for="value in allValues" :key="`src-${value.id}`" :value="value.id">
                  {{ gradeOptionLabel(value.id, value.grade_scale_code, value.label) }}
                </option>
              </select>
            </div>
            <div class="col-md-3">
              <label class="form-label">{{ t('adminGrades.fields.targetGrade') }}</label>
              <select v-model="newTranslation.target_grade" class="form-select">
                <option value="">{{ t('adminGrades.selectScale') }}</option>
                <option v-for="value in allValues" :key="`tgt-${value.id}`" :value="value.id">
                  {{ gradeOptionLabel(value.id, value.grade_scale_code, value.label) }}
                </option>
              </select>
            </div>
            <div class="col-md-2">
              <label class="form-label">{{ t('adminGrades.fields.confidence') }}</label>
              <input v-model.number="newTranslation.confidence" class="form-control" type="number" min="0" max="1" step="0.1" />
            </div>
            <div class="col-md-2">
              <label class="form-label">{{ t('adminGrades.fields.notes') }}</label>
              <input v-model="newTranslation.notes" class="form-control" type="text" />
            </div>
            <div class="col-md-2">
              <button
                type="button"
                class="btn btn-outline-primary w-100"
                :disabled="busy || !newTranslation.source_grade || !newTranslation.target_grade"
                @click="createTranslation"
              >
                {{ t('adminGrades.createTranslation') }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </PageStateShell>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useToast } from '@/composables/useToast'
import { useConfirm } from '@/composables/useConfirm'
import ResponsiveList from '@/components/ResponsiveList.vue'
import PageHeader from '@/components/PageHeader.vue'
import PageBreadcrumb from '@/components/PageBreadcrumb.vue'
import PageStateShell from '@/components/State/PageStateShell.vue'
import SearchableSelect from '@/components/SearchableSelect.vue'

const { t } = useI18n()
const { success, error: errorToast } = useToast()
const { confirm } = useConfirm()

const loading = ref(true)
const busy = ref(false)
const error = ref(null)
const scales = ref([])
const values = ref([])
const allValues = ref([])
const translations = ref([])
const selectedId = ref(null)
const countryOptions = ref([])

const newScale = reactive(emptyScale())
const scaleForm = reactive(emptyScale())
const newValue = reactive(emptyValue())
const newTranslation = reactive({
  source_grade: '',
  target_grade: '',
  confidence: 1,
  notes: '',
})

const valueMobileColumns = computed(() => [
  { key: 'label', label: t('adminGrades.fields.label') },
  { key: 'numericValue', label: t('adminGrades.fields.numericValue') },
  { key: 'gpaEquivalent', label: t('adminGrades.fields.gpaEquivalent') },
  { key: 'order', label: t('adminGrades.fields.order') },
  { key: 'isPassing', label: t('adminGrades.fields.isPassing') },
])

const translationMobileColumns = computed(() => [
  { key: 'sourceGrade', label: t('adminGrades.fields.sourceGrade') },
  { key: 'targetGrade', label: t('adminGrades.fields.targetGrade') },
  { key: 'confidence', label: t('adminGrades.fields.confidence') },
  { key: 'notes', label: t('adminGrades.fields.notes') },
])

function emptyScale() {
  return {
    name: '',
    code: '',
    country: '',
    description: '',
    min_value: 0,
    max_value: 4,
    passing_value: 2,
    is_active: true,
    is_reverse_scale: false,
  }
}

function emptyValue() {
  return {
    label: '',
    numeric_value: 0,
    gpa_equivalent: 0,
    order: 0,
    is_passing: true,
  }
}

function normalizeApiList(data) {
  if (data && typeof data === 'object' && Array.isArray(data.results)) return data.results
  return Array.isArray(data) ? data : []
}

function assignScale(target, source) {
  target.name = source.name || ''
  target.code = source.code || ''
  target.country = source.country || ''
  target.description = source.description || ''
  target.min_value = source.min_value ?? 0
  target.max_value = source.max_value ?? 4
  target.passing_value = source.passing_value ?? 2
  target.is_active = source.is_active !== false
  target.is_reverse_scale = Boolean(source.is_reverse_scale)
}

function scalePayload(form) {
  return {
    name: form.name,
    code: form.code,
    country: form.country,
    description: form.description,
    min_value: form.min_value,
    max_value: form.max_value,
    passing_value: form.passing_value,
    is_active: form.is_active,
    is_reverse_scale: form.is_reverse_scale,
  }
}

function gradeOptionLabel(id, scaleCode, label) {
  const code = scaleCode || ''
  const text = label || id
  return code ? `${code}: ${text}` : String(text)
}

async function fetchScales() {
  const res = await api.get('/api/grades/scales/')
  scales.value = normalizeApiList(res.data)
}

async function fetchValues(scaleId) {
  const res = await api.get('/api/grades/values/by_scale/', { params: { grade_scale: scaleId } })
  values.value = normalizeApiList(res.data)
}

async function fetchAllValues() {
  const lists = await Promise.all(
    scales.value.map((scale) =>
      api.get('/api/grades/values/by_scale/', { params: { grade_scale: scale.id } }),
    ),
  )
  allValues.value = lists.flatMap((res) => normalizeApiList(res.data))
}

async function fetchTranslations() {
  const res = await api.get('/api/grades/translations/')
  translations.value = normalizeApiList(res.data)
}

async function fetchCountryOptions() {
  const res = await api.get('/api/accounts/catalogs/countries/')
  countryOptions.value = normalizeApiList(res.data)
}

async function reload() {
  loading.value = true
  error.value = null
  try {
    await Promise.all([fetchScales(), fetchTranslations()])
    await fetchAllValues()
    if (selectedId.value) {
      await selectScale({ id: selectedId.value })
    }
  } catch (err) {
    console.error('Failed to load grade scales:', err)
    error.value = t('adminGrades.loadError')
  } finally {
    loading.value = false
  }
}

async function selectScale(scale) {
  selectedId.value = scale.id
  try {
    const res = await api.get(`/api/grades/scales/${scale.id}/`)
    assignScale(scaleForm, res.data)
    if (Array.isArray(res.data.grade_values) && res.data.grade_values.length) {
      values.value = res.data.grade_values
    } else {
      await fetchValues(scale.id)
    }
  } catch (err) {
    console.error('Failed to load scale:', err)
    errorToast(t('adminGrades.loadError'))
  }
}

async function createScale() {
  busy.value = true
  try {
    const res = await api.post('/api/grades/scales/', scalePayload(newScale))
    success(t('adminGrades.toastCreated'))
    assignScale(newScale, emptyScale())
    await fetchScales()
    await selectScale(res.data)
  } catch (err) {
    console.error('Failed to create scale:', err)
    errorToast(t('adminGrades.saveError'))
  } finally {
    busy.value = false
  }
}

async function saveScale() {
  if (!selectedId.value) return
  busy.value = true
  try {
    await api.patch(`/api/grades/scales/${selectedId.value}/`, scalePayload(scaleForm))
    success(t('adminGrades.toastCreated'))
    await fetchScales()
  } catch (err) {
    console.error('Failed to save scale:', err)
    errorToast(t('adminGrades.saveError'))
  } finally {
    busy.value = false
  }
}

async function deleteScale() {
  if (!selectedId.value) return
  const ok = await confirm({
    title: t('adminCommon.delete'),
    message: t('adminGrades.deleteConfirm', { name: scaleForm.name || scaleForm.code }),
    confirmText: t('adminCommon.delete'),
    cancelText: t('adminCommon.cancel'),
    variant: 'danger',
  })
  if (!ok) return
  busy.value = true
  try {
    await api.delete(`/api/grades/scales/${selectedId.value}/`)
    success(t('adminGrades.toastDeleted'))
    selectedId.value = null
    assignScale(scaleForm, emptyScale())
    values.value = []
    await Promise.all([fetchScales(), fetchTranslations(), fetchAllValues()])
  } catch (err) {
    console.error('Failed to delete scale:', err)
    errorToast(t('adminGrades.saveError'))
  } finally {
    busy.value = false
  }
}

async function createValue() {
  if (!selectedId.value) return
  busy.value = true
  try {
    await api.post('/api/grades/values/', {
      grade_scale: selectedId.value,
      label: newValue.label,
      numeric_value: newValue.numeric_value,
      gpa_equivalent: newValue.gpa_equivalent,
      order: newValue.order,
      is_passing: newValue.is_passing,
    })
    Object.assign(newValue, emptyValue())
    success(t('adminGrades.toastCreated'))
    await fetchValues(selectedId.value)
    await fetchAllValues()
  } catch (err) {
    console.error('Failed to create value:', err)
    errorToast(t('adminGrades.saveError'))
  } finally {
    busy.value = false
  }
}

async function saveValue(value) {
  busy.value = true
  try {
    await api.patch(`/api/grades/values/${value.id}/`, {
      label: value.label,
      numeric_value: value.numeric_value,
      gpa_equivalent: value.gpa_equivalent,
      order: value.order,
      is_passing: value.is_passing,
    })
    success(t('adminGrades.toastCreated'))
    await fetchAllValues()
  } catch (err) {
    console.error('Failed to save value:', err)
    errorToast(t('adminGrades.saveError'))
  } finally {
    busy.value = false
  }
}

async function deleteValue(value) {
  const ok = await confirm({
    title: t('adminCommon.delete'),
    message: t('adminGrades.deleteConfirm', { name: value.label }),
    confirmText: t('adminCommon.delete'),
    cancelText: t('adminCommon.cancel'),
    variant: 'danger',
  })
  if (!ok) return
  busy.value = true
  try {
    await api.delete(`/api/grades/values/${value.id}/`)
    success(t('adminGrades.toastDeleted'))
    await fetchValues(selectedId.value)
    await fetchAllValues()
  } catch (err) {
    console.error('Failed to delete value:', err)
    errorToast(t('adminGrades.saveError'))
  } finally {
    busy.value = false
  }
}

async function createTranslation() {
  busy.value = true
  try {
    await api.post('/api/grades/translations/', {
      source_grade: newTranslation.source_grade,
      target_grade: newTranslation.target_grade,
      confidence: newTranslation.confidence,
      notes: newTranslation.notes,
    })
    newTranslation.source_grade = ''
    newTranslation.target_grade = ''
    newTranslation.confidence = 1
    newTranslation.notes = ''
    success(t('adminGrades.toastCreated'))
    await fetchTranslations()
  } catch (err) {
    console.error('Failed to create translation:', err)
    errorToast(t('adminGrades.saveError'))
  } finally {
    busy.value = false
  }
}

async function deleteTranslation(mapping) {
  const name = `${mapping.source_grade_label || ''} → ${mapping.target_grade_label || ''}`
  const ok = await confirm({
    title: t('adminCommon.delete'),
    message: t('adminGrades.deleteConfirm', { name }),
    confirmText: t('adminCommon.delete'),
    cancelText: t('adminCommon.cancel'),
    variant: 'danger',
  })
  if (!ok) return
  busy.value = true
  try {
    await api.delete(`/api/grades/translations/${mapping.id}/`)
    success(t('adminGrades.toastDeleted'))
    await fetchTranslations()
  } catch (err) {
    console.error('Failed to delete translation:', err)
    errorToast(t('adminGrades.saveError'))
  } finally {
    busy.value = false
  }
}

onMounted(() => {
  Promise.all([reload(), fetchCountryOptions()])
})
</script>

<style scoped>
.admin-grades-page {
  min-height: 60vh;
}
</style>
