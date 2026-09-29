<template>
  <div class="admin-program-destinations-page">
    <PageHeader :title="headerTitle" :subtitle="t('adminProgramDestinations.subtitle')">
      <template #breadcrumb>
        <PageBreadcrumb
          :aria-label="t('adminCommon.breadcrumbAria')"
          :items="[
            { to: { name: 'Dashboard' }, label: t('route.names.Dashboard') },
            { to: { name: 'AdminPrograms' }, label: t('route.names.AdminPrograms') },
            { label: t('route.names.AdminProgramDestinations') },
          ]"
        />
      </template>
      <template #actions>
        <button type="button" class="btn btn-outline-secondary" :disabled="busy" @click="reload">
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
      <div class="card mb-4 shadow-sm" data-testid="add-university-card">
        <div class="card-header d-flex flex-wrap align-items-center gap-2">
          <span class="fw-medium">{{ t('adminProgramDestinations.addUniversity') }}</span>
          <span class="text-muted small ms-md-auto">{{ t('adminProgramDestinations.addUniversityHint') }}</span>
        </div>
        <div class="card-body">
          <div class="row g-3 align-items-end">
            <div class="col-md-4">
              <label class="form-label">{{ t('adminProgramDestinations.name') }}</label>
              <SearchableSelect
                :model-value="newUni.name"
                :options="newUniNameOptions"
                :placeholder="t('adminProgramDestinations.namePlaceholder')"
                :disabled="busy"
                allow-custom
                data-testid="add-university-name"
                @update:model-value="onNewUniNameUpdate"
                @query-change="onNewUniNameQuery"
              />
            </div>
            <div class="col-md-3">
              <label class="form-label">{{ t('adminProgramDestinations.country') }}</label>
              <SearchableSelect
                v-model="newUni.country"
                :options="filteredNewUniCountries"
                :placeholder="t('adminProgramDestinations.countryPlaceholder')"
                :disabled="busy"
                data-testid="add-university-country"
                @update:model-value="onNewUniCountryChange"
              />
            </div>
            <div class="col-md-3">
              <label class="form-label">{{ t('adminProgramDestinations.gradeScale') }}</label>
              <SearchableSelect
                :model-value="newUni.grade_scale"
                :options="newUniGradeScaleOptions"
                :placeholder="t('adminProgramDestinations.gradeScalePlaceholder')"
                :disabled="busy"
                data-testid="add-university-grade-scale"
                @update:model-value="onNewUniGradeScaleUpdate"
              />
              <div v-if="newUni.country && !filteredNewUniScales.length" class="form-text text-muted">
                {{ t('adminProgramDestinations.noMatchingGradeScales') }}
              </div>
            </div>
            <div class="col-md-2">
              <button
                type="button"
                class="btn btn-primary w-100"
                data-testid="add-university-save"
                :disabled="busy || !newUni.name.trim() || !newUni.country"
                @click="createUniversity"
              >
                <i class="bi bi-plus-lg me-1" aria-hidden="true"></i>{{ t('adminCommon.save') }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="institutions.length" class="row g-2 align-items-end mb-3">
        <div class="col-md-6">
          <label class="form-label" for="destinations-search">{{ t('adminCommon.searchLabel') }}</label>
          <input
            id="destinations-search"
            v-model="listSearch"
            class="form-control"
            type="search"
            data-testid="destinations-search"
            :placeholder="t('adminProgramDestinations.searchPlaceholder')"
          >
        </div>
        <div class="col-md-6 text-md-end text-muted small pb-2">
          {{ t('adminProgramDestinations.listCount', { shown: filteredInstitutions.length, total: institutions.length }) }}
        </div>
      </div>

      <div v-if="!institutions.length" class="alert alert-light border" data-testid="destinations-empty">
        <div class="fw-medium mb-1">{{ t('adminProgramDestinations.empty') }}</div>
        <div class="text-muted small">{{ t('adminProgramDestinations.emptyHint') }}</div>
      </div>

      <div
        v-else-if="!filteredInstitutions.length"
        class="alert alert-light border"
        data-testid="destinations-search-empty"
      >
        {{ t('adminProgramDestinations.searchEmpty') }}
      </div>

      <CollapsibleCard
        v-for="inst in filteredInstitutions"
        :key="inst.id"
        :default-open="filteredInstitutions.length <= 3"
        :test-id="`institution-${inst.id}`"
        title-class="mb-0 fw-medium text-truncate"
        compact-header
      >
        <template #title>
          <span class="d-inline-flex flex-wrap align-items-center gap-2 min-w-0">
            <span class="text-truncate">{{ inst.name }}</span>
            <span v-if="inst.country" class="badge text-bg-light border fw-normal">{{ inst.country }}</span>
            <span
              class="badge"
              :class="inst.is_active ? 'bg-success' : 'bg-secondary'"
            >
              {{ inst.is_active ? t('adminCommon.yes') : t('adminCommon.no') }}
            </span>
          </span>
        </template>
        <template #header-extra>
          <button
            type="button"
            class="btn btn-sm btn-outline-secondary"
            :disabled="busy"
            @click.stop="toggleActive(inst)"
          >
            {{ inst.is_active ? t('adminProgramDestinations.deactivate') : t('adminProgramDestinations.activate') }}
          </button>
        </template>

        <div class="row g-3 mb-3">
          <div class="col-md-4">
            <label class="form-label">{{ t('adminProgramDestinations.name') }}</label>
            <input v-model="inst.name" class="form-control" :disabled="busy" @change="saveInstitution(inst)">
          </div>
          <div class="col-md-4">
            <label class="form-label">{{ t('adminProgramDestinations.country') }}</label>
            <SearchableSelect
              v-model="inst.country"
              :options="countryOptions"
              :placeholder="t('adminProgramDestinations.countryPlaceholder')"
              :disabled="busy"
              @update:model-value="onInstitutionCountryChange(inst)"
            />
          </div>
          <div class="col-md-4">
            <label class="form-label">{{ t('adminProgramDestinations.gradeScale') }}</label>
            <SearchableSelect
              :model-value="inst.grade_scale || ''"
              :options="gradeScaleOptionsFor(inst.country, inst.grade_scale)"
              :placeholder="t('adminProgramDestinations.gradeScalePlaceholder')"
              :disabled="busy"
              @update:model-value="(value) => onInstitutionGradeScaleUpdate(inst, value)"
            />
          </div>
        </div>

        <h6 class="text-uppercase text-muted small fw-semibold mb-2">
          {{ t('adminProgramDestinations.universitySubjects') }}
        </h6>
        <SubjectEditor
          :subjects="subjectsByParent.institution[inst.id] || []"
          parent-level="institution"
          :busy="busy"
          @create="(payload) => createSubject({ ...payload, institution: inst.id })"
          @toggle="toggleSubject"
        />

        <h6 class="text-uppercase text-muted small fw-semibold mt-4 mb-2">
          {{ t('adminProgramDestinations.schools') }}
        </h6>
        <div class="row g-2 mb-3 align-items-end">
          <div class="col-md-7">
            <label class="form-label visually-hidden">
              {{ t('adminProgramDestinations.newSchool') }}
            </label>
            <SearchableSelect
              :model-value="schoolDrafts[inst.id] || ''"
              :options="schoolNameOptions"
              :placeholder="t('adminProgramDestinations.newSchool')"
              :disabled="busy"
              allow-custom
              @update:model-value="(value) => { schoolDrafts[inst.id] = decodePlainName(value) }"
            />
          </div>
          <div class="col-md-5 col-lg-3">
            <button
              type="button"
              class="btn btn-outline-primary w-100"
              :disabled="busy || !(schoolDrafts[inst.id] || '').trim()"
              @click="createSchool(inst)"
            >
              <i class="bi bi-plus-lg me-1" aria-hidden="true"></i>{{ t('adminProgramDestinations.addSchool') }}
            </button>
          </div>
        </div>

        <div
          v-for="school in schoolsByInst[inst.id] || []"
          :key="school.id"
          class="border rounded-3 p-3 mb-3 seim-surface-muted"
        >
          <div class="d-flex flex-wrap gap-2 align-items-center mb-3">
            <input
              v-model="school.name"
              class="form-control flex-grow-1"
              style="min-width: 12rem"
              :disabled="busy"
              @change="saveSchool(school)"
            >
            <button
              type="button"
              class="btn btn-sm btn-outline-secondary"
              :disabled="busy"
              @click="toggleActive(school, 'school')"
            >
              {{ school.is_active ? t('adminProgramDestinations.deactivate') : t('adminProgramDestinations.activate') }}
            </button>
          </div>
          <SubjectEditor
            :subjects="subjectsByParent.school[school.id] || []"
            parent-level="school"
            :busy="busy"
            @create="(payload) => createSubject({ ...payload, institution: inst.id, school: school.id })"
            @toggle="toggleSubject"
          />
          <div class="row g-2 mt-3 align-items-end">
            <div class="col-md-7">
              <SearchableSelect
                :model-value="programDrafts[school.id] || ''"
                :options="academicProgramNameOptions"
                :placeholder="t('adminProgramDestinations.newProgram')"
                :disabled="busy"
                allow-custom
                @update:model-value="(value) => { programDrafts[school.id] = decodePlainName(value) }"
              />
            </div>
            <div class="col-md-5 col-lg-3">
              <button
                type="button"
                class="btn btn-outline-primary btn-sm w-100"
                :disabled="busy || !(programDrafts[school.id] || '').trim()"
                @click="createAcademic(school)"
              >
                <i class="bi bi-plus-lg me-1" aria-hidden="true"></i>{{ t('adminProgramDestinations.addProgram') }}
              </button>
            </div>
          </div>
          <div
            v-for="ap in programsBySchool[school.id] || []"
            :key="ap.id"
            class="ms-0 ms-md-3 mt-3 border-start border-2 ps-3"
          >
            <div class="d-flex flex-wrap gap-2 align-items-center mb-2">
              <input
                v-model="ap.name"
                class="form-control flex-grow-1"
                style="min-width: 10rem"
                :disabled="busy"
                @change="saveAcademic(ap)"
              >
              <input
                v-model="ap.code"
                class="form-control"
                style="max-width: 8rem"
                :placeholder="t('adminProgramDestinations.subjectCode')"
                :disabled="busy"
                @change="saveAcademic(ap)"
              >
              <button
                type="button"
                class="btn btn-sm btn-outline-secondary"
                :disabled="busy"
                @click="toggleActive(ap, 'academic')"
              >
                {{ ap.is_active ? t('adminProgramDestinations.deactivate') : t('adminProgramDestinations.activate') }}
              </button>
            </div>
            <SubjectEditor
              :subjects="subjectsByParent.academic[ap.id] || []"
              parent-level="program"
              :busy="busy"
              @create="(payload) => createSubject({
                ...payload,
                institution: inst.id,
                school: school.id,
                academic_program: ap.id,
              })"
              @toggle="toggleSubject"
            />
          </div>
        </div>
      </CollapsibleCard>
    </PageStateShell>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import PageHeader from '@/components/PageHeader.vue'
import PageBreadcrumb from '@/components/PageBreadcrumb.vue'
import PageStateShell from '@/components/State/PageStateShell.vue'
import SearchableSelect from '@/components/SearchableSelect.vue'
import CollapsibleCard from '@/components/CollapsibleCard.vue'
import api from '@/services/api'
import {
  buildHostNameOptions,
  decodeHostSuggestion,
  filterCountryOptionsByHostName,
  filterGradeScalesByCountry,
  filterInstitutionsBySearch,
} from '@/utils/hostDestinationCatalog'

const { t } = useI18n()
const route = useRoute()
const programId = computed(() => route.params.id)

const loading = ref(true)
const busy = ref(false)
const error = ref('')
const programName = ref('')
const institutions = ref([])
const catalogInstitutions = ref([])
const gradeScales = ref([])
const schoolsByInst = ref({})
const programsBySchool = ref({})
const subjectsByParent = reactive({ institution: {}, school: {}, academic: {} })
const countryOptions = ref([])
const schoolDrafts = reactive({})
const programDrafts = reactive({})
const newUni = reactive({ name: '', country: '', grade_scale: '' })
const newUniNameQuery = ref('')
const listSearch = ref('')

const headerTitle = computed(() =>
  programName.value
    ? t('adminProgramDestinations.titleNamed', { name: programName.value })
    : t('adminProgramDestinations.title'),
)

const filteredInstitutions = computed(() =>
  filterInstitutionsBySearch(institutions.value, listSearch.value),
)

const filteredNewUniCountries = computed(() =>
  filterCountryOptionsByHostName(
    countryOptions.value,
    catalogInstitutions.value,
    newUniNameQuery.value || newUni.name,
  ),
)

const filteredNewUniScales = computed(() =>
  filterGradeScalesByCountry(gradeScales.value, newUni.country, countryOptions.value),
)

const newUniNameOptions = computed(() =>
  buildHostNameOptions(catalogInstitutions.value, {
    country: newUni.country,
    query: '',
  }),
)

const noneGradeScaleOption = computed(() => ({
  value: '',
  label: t('adminProgramDestinations.noGradeScale'),
}))

const newUniGradeScaleOptions = computed(() => [
  noneGradeScaleOption.value,
  ...filteredNewUniScales.value.map(scaleToOption),
])

const schoolNameOptions = computed(() => {
  const names = new Set()
  for (const schools of Object.values(schoolsByInst.value)) {
    for (const school of schools || []) {
      const name = String(school?.name || '').trim()
      if (name) names.add(name)
    }
  }
  return [...names]
    .sort((a, b) => a.localeCompare(b, undefined, { sensitivity: 'base' }))
    .map((name) => ({ value: name, label: name }))
})

const academicProgramNameOptions = computed(() => {
  const names = new Set()
  for (const programs of Object.values(programsBySchool.value)) {
    for (const ap of programs || []) {
      const name = String(ap?.name || '').trim()
      if (name) names.add(name)
    }
  }
  return [...names]
    .sort((a, b) => a.localeCompare(b, undefined, { sensitivity: 'base' }))
    .map((name) => ({ value: name, label: name }))
})

const SubjectEditor = {
  name: 'SubjectEditor',
  props: {
    subjects: { type: Array, default: () => [] },
    parentLevel: { type: String, default: 'institution' },
    busy: { type: Boolean, default: false },
  },
  emits: ['create', 'toggle'],
  data() {
    return { draft: { code: '', name: '', credits: '' } }
  },
  template: `
    <div class="subject-editor">
      <table class="table table-sm align-middle" v-if="subjects.length">
        <thead>
          <tr>
            <th>{{ $t('adminProgramDestinations.subjectCode') }}</th>
            <th>{{ $t('adminProgramDestinations.subjectName') }}</th>
            <th>{{ $t('adminProgramDestinations.subjectCredits') }}</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in subjects" :key="s.id">
            <td>{{ s.code || '—' }}</td>
            <td>{{ s.name }}</td>
            <td>{{ s.credits ?? '—' }}</td>
            <td class="text-end">
              <button type="button" class="btn btn-sm btn-outline-secondary" :disabled="busy" @click="$emit('toggle', s)">
                {{ s.is_active ? $t('adminProgramDestinations.deactivate') : $t('adminProgramDestinations.activate') }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="row g-2">
        <div class="col-md-3">
          <input v-model="draft.code" class="form-control form-control-sm" :placeholder="$t('adminProgramDestinations.subjectCode')">
        </div>
        <div class="col-md-5">
          <input v-model="draft.name" class="form-control form-control-sm" :placeholder="$t('adminProgramDestinations.subjectName')">
        </div>
        <div class="col-md-2">
          <input v-model="draft.credits" type="number" step="0.5" class="form-control form-control-sm" :placeholder="$t('adminProgramDestinations.subjectCredits')">
        </div>
        <div class="col-md-2">
          <button type="button" class="btn btn-sm btn-outline-primary w-100" :disabled="busy || !draft.name" @click="add">
            {{ $t('adminProgramDestinations.addSubject') }}
          </button>
        </div>
      </div>
    </div>
  `,
  methods: {
    add() {
      this.$emit('create', { ...this.draft })
      this.draft = { code: '', name: '', credits: '' }
    },
  },
}

function scaleToOption(scale) {
  const country = String(scale.country || '').trim()
  return {
    value: String(scale.id),
    label: country ? `${scale.name} (${country})` : scale.name,
    aliases: [scale.code, scale.name].filter(Boolean),
  }
}

function gradeScaleOptionsFor(country, currentScaleId) {
  const filtered = filterGradeScalesByCountry(gradeScales.value, country, countryOptions.value)
  const options = [noneGradeScaleOption.value, ...filtered.map(scaleToOption)]
  if (currentScaleId) {
    const id = String(currentScaleId)
    if (!options.some((opt) => opt.value === id)) {
      const current = gradeScales.value.find((s) => String(s.id) === id)
      if (current) options.splice(1, 0, scaleToOption(current))
    }
  }
  return options
}

function decodePlainName(value) {
  const decoded = decodeHostSuggestion(value)
  return decoded?.name || String(value || '').trim()
}

function pruneNewUniGradeScale() {
  if (!newUni.grade_scale) return
  const ok = filteredNewUniScales.value.some((s) => String(s.id) === String(newUni.grade_scale))
  if (!ok) newUni.grade_scale = ''
}

function onNewUniNameUpdate(value) {
  const decoded = decodeHostSuggestion(value)
  if (!decoded) {
    newUni.name = ''
    newUniNameQuery.value = ''
    return
  }
  newUni.name = decoded.name
  newUniNameQuery.value = decoded.name
  if (decoded.country) newUni.country = decoded.country
  if (decoded.grade_scale) {
    newUni.grade_scale = String(decoded.grade_scale)
  } else {
    pruneNewUniGradeScale()
  }
}

function onNewUniNameQuery(query) {
  // Labels look like "Name · Country"; keep the name portion for country narrowing.
  newUniNameQuery.value = String(query || '').split(' · ')[0].trim()
}

function onNewUniCountryChange() {
  pruneNewUniGradeScale()
}

function onNewUniGradeScaleUpdate(value) {
  newUni.grade_scale = value || ''
}

function onInstitutionCountryChange(inst) {
  const allowed = filterGradeScalesByCountry(gradeScales.value, inst.country, countryOptions.value)
  if (inst.grade_scale && !allowed.some((s) => String(s.id) === String(inst.grade_scale))) {
    inst.grade_scale = ''
  }
  saveInstitution(inst)
}

function onInstitutionGradeScaleUpdate(inst, value) {
  inst.grade_scale = value || ''
  saveInstitution(inst)
}

watch(
  () => newUni.country,
  () => pruneNewUniGradeScale(),
)

function unwrap(data) {
  if (Array.isArray(data)) return data
  if (data?.results) return data.results
  return []
}

async function fetchAllPages(url, params = {}) {
  const acc = []
  let page = 1
  for (;;) {
    const { data } = await api.get(url, { params: { ...params, page, page_size: 100 } })
    const chunk = unwrap(data)
    acc.push(...chunk)
    if (!data?.next) break
    page += 1
    if (page > 50) break
  }
  return acc
}

async function loadGradeScales() {
  gradeScales.value = await fetchAllPages('/api/grades/scales/active/')
}

async function loadCountryOptions() {
  const { data } = await api.get('/api/accounts/catalogs/countries/')
  countryOptions.value = unwrap(data)
}

async function loadCatalogInstitutions() {
  catalogInstitutions.value = await fetchAllPages('/api/host-institutions/', { is_active: true })
}

async function reload() {
  loading.value = true
  error.value = ''
  try {
    const prog = await api.get(`/api/programs/${programId.value}/`)
    programName.value = prog.data.name
    const instResp = await api.get(`/api/programs/${programId.value}/host-institutions/`)
    institutions.value = unwrap(instResp.data).map((i) => ({
      ...i,
      grade_scale: i.grade_scale || '',
    }))
    schoolsByInst.value = {}
    programsBySchool.value = {}
    subjectsByParent.institution = {}
    subjectsByParent.school = {}
    subjectsByParent.academic = {}
    await Promise.all(institutions.value.map((inst) => loadInstitutionTree(inst)))
  } catch (err) {
    console.error(err)
    error.value = t('adminProgramDestinations.loadError')
  } finally {
    loading.value = false
  }
}

async function loadInstitutionTree(inst) {
  const [schoolsResp, subjResp] = await Promise.all([
    api.get(`/api/host-institutions/${inst.id}/schools/`),
    api.get(`/api/host-subjects/`, { params: { institution: inst.id } }),
  ])
  const schools = unwrap(schoolsResp.data)
  schoolsByInst.value = { ...schoolsByInst.value, [inst.id]: schools }
  const subjects = unwrap(subjResp.data)
  subjectsByParent.institution[inst.id] = subjects.filter((s) => !s.school && !s.academic_program)
  for (const school of schools) {
    subjectsByParent.school[school.id] = subjects.filter(
      (s) => s.school === school.id && !s.academic_program,
    )
    const apResp = await api.get(`/api/schools/${school.id}/academic-programs/`)
    const aps = unwrap(apResp.data)
    programsBySchool.value = { ...programsBySchool.value, [school.id]: aps }
    for (const ap of aps) {
      subjectsByParent.academic[ap.id] = subjects.filter((s) => s.academic_program === ap.id)
    }
  }
}

async function createUniversity() {
  if (!newUni.name.trim() || !newUni.country) {
    error.value = t('adminProgramDestinations.countryRequired')
    return
  }
  busy.value = true
  error.value = ''
  try {
    await api.post(`/api/programs/${programId.value}/host-institutions/`, {
      name: newUni.name.trim(),
      country: newUni.country,
      grade_scale: newUni.grade_scale || null,
      is_active: true,
    })
    newUni.name = ''
    newUni.country = ''
    newUni.grade_scale = ''
    newUniNameQuery.value = ''
    await Promise.all([reload(), loadCatalogInstitutions()])
  } catch (err) {
    console.error(err)
    error.value = t('adminProgramDestinations.saveError')
  } finally {
    busy.value = false
  }
}

async function saveInstitution(inst) {
  busy.value = true
  try {
    await api.patch(`/api/host-institutions/${inst.id}/`, {
      name: inst.name,
      country: inst.country,
      grade_scale: inst.grade_scale || null,
    })
  } catch (err) {
    console.error(err)
    error.value = t('adminProgramDestinations.saveError')
  } finally {
    busy.value = false
  }
}

async function toggleActive(obj, kind = 'institution') {
  busy.value = true
  try {
    const url = {
      institution: `/api/host-institutions/${obj.id}/`,
      school: `/api/schools/${obj.id}/`,
      academic: `/api/academic-programs/${obj.id}/`,
    }[kind]
    await api.patch(url, { is_active: !obj.is_active })
    obj.is_active = !obj.is_active
  } catch (err) {
    console.error(err)
    error.value = t('adminProgramDestinations.saveError')
  } finally {
    busy.value = false
  }
}

async function createSchool(inst) {
  const name = String(schoolDrafts[inst.id] || '').trim()
  if (!name) return
  busy.value = true
  try {
    await api.post(`/api/host-institutions/${inst.id}/schools/`, {
      name,
      is_active: true,
    })
    schoolDrafts[inst.id] = ''
    await reload()
  } catch (err) {
    console.error(err)
    error.value = t('adminProgramDestinations.saveError')
  } finally {
    busy.value = false
  }
}

async function saveSchool(school) {
  busy.value = true
  try {
    await api.patch(`/api/schools/${school.id}/`, { name: school.name })
  } finally {
    busy.value = false
  }
}

async function createAcademic(school) {
  const name = String(programDrafts[school.id] || '').trim()
  if (!name) return
  busy.value = true
  try {
    await api.post(`/api/schools/${school.id}/academic-programs/`, {
      name,
      is_active: true,
    })
    programDrafts[school.id] = ''
    await reload()
  } catch (err) {
    console.error(err)
    error.value = t('adminProgramDestinations.saveError')
  } finally {
    busy.value = false
  }
}

async function saveAcademic(ap) {
  busy.value = true
  try {
    await api.patch(`/api/academic-programs/${ap.id}/`, { name: ap.name, code: ap.code })
  } finally {
    busy.value = false
  }
}

async function createSubject(payload) {
  busy.value = true
  try {
    const body = {
      name: payload.name,
      code: payload.code || '',
      credits: payload.credits === '' || payload.credits == null ? null : payload.credits,
      institution: payload.institution,
      school: payload.school || null,
      academic_program: payload.academic_program || null,
      is_active: true,
    }
    await api.post('/api/host-subjects/', body)
    await reload()
  } catch (err) {
    console.error(err)
    error.value = t('adminProgramDestinations.saveError')
  } finally {
    busy.value = false
  }
}

async function toggleSubject(subject) {
  busy.value = true
  try {
    await api.patch(`/api/host-subjects/${subject.id}/`, { is_active: !subject.is_active })
    subject.is_active = !subject.is_active
  } catch (err) {
    console.error(err)
    error.value = t('adminProgramDestinations.saveError')
  } finally {
    busy.value = false
  }
}

onMounted(async () => {
  await Promise.all([loadGradeScales(), loadCountryOptions(), loadCatalogInstitutions()])
  await reload()
})
</script>
