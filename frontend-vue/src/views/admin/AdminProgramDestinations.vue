<template>
  <div class="admin-program-destinations-page">
    <PageHeader :title="headerTitle" :subtitle="t('adminProgramDestinations.subtitle')">
      <template #breadcrumb>
        <nav aria-label="Breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item">
              <router-link :to="{ name: 'Dashboard' }">{{ t('route.names.Dashboard') }}</router-link>
            </li>
            <li class="breadcrumb-item">
              <router-link :to="{ name: 'AdminPrograms' }">{{ t('route.names.AdminPrograms') }}</router-link>
            </li>
            <li class="breadcrumb-item active">{{ t('route.names.AdminProgramDestinations') }}</li>
          </ol>
        </nav>
      </template>
      <template #actions>
        <button type="button" class="btn btn-outline-secondary" :disabled="busy" @click="reload">
          <i class="bi bi-arrow-clockwise me-1"></i>{{ t('adminCommon.refresh') }}
        </button>
      </template>
    </PageHeader>

    <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>
    <div v-else-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">{{ t('adminCommon.loading') }}</span>
      </div>
    </div>

    <template v-else>
      <div class="card mb-3" data-testid="add-university-card">
        <div class="card-header fw-medium">{{ t('adminProgramDestinations.addUniversity') }}</div>
        <div class="card-body">
          <div class="row g-2 align-items-end">
            <div class="col-md-4">
              <label class="form-label">{{ t('adminProgramDestinations.name') }}</label>
              <input v-model="newUni.name" class="form-control" type="text">
            </div>
            <div class="col-md-3">
              <label class="form-label">{{ t('adminProgramDestinations.country') }}</label>
              <SearchableSelect
                v-model="newUni.country"
                :options="countryOptions"
                :placeholder="t('adminProgramDestinations.countryPlaceholder')"
                :disabled="busy"
              />
            </div>
            <div class="col-md-3">
              <label class="form-label">{{ t('adminProgramDestinations.gradeScale') }}</label>
              <select v-model="newUni.grade_scale" class="form-select">
                <option value="">{{ t('adminProgramDestinations.noGradeScale') }}</option>
                <option v-for="scale in gradeScales" :key="scale.id" :value="scale.id">
                  {{ scale.name }}
                </option>
              </select>
            </div>
            <div class="col-md-2">
              <button
                type="button"
                class="btn btn-primary w-100"
                data-testid="add-university-save"
                :disabled="busy || !newUni.name.trim() || !newUni.country"
                @click="createUniversity"
              >
                {{ t('adminCommon.save') }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="!institutions.length" class="alert alert-light border">
        {{ t('adminProgramDestinations.empty') }}
      </div>

      <div
        v-for="inst in institutions"
        :key="inst.id"
        class="card mb-3"
        :data-testid="`institution-${inst.id}`"
      >
        <div class="card-header d-flex flex-wrap gap-2 align-items-center">
          <strong class="me-auto">{{ inst.name }}</strong>
          <span class="badge" :class="inst.is_active ? 'bg-success' : 'bg-secondary'">
            {{ inst.is_active ? t('adminCommon.yes') : t('adminCommon.no') }}
          </span>
          <button type="button" class="btn btn-sm btn-outline-secondary" @click="toggleActive(inst)">
            {{ inst.is_active ? t('adminProgramDestinations.deactivate') : t('adminProgramDestinations.activate') }}
          </button>
        </div>
        <div class="card-body">
          <div class="row g-2 mb-3">
            <div class="col-md-4">
              <label class="form-label">{{ t('adminProgramDestinations.name') }}</label>
              <input v-model="inst.name" class="form-control" @change="saveInstitution(inst)">
            </div>
            <div class="col-md-3">
              <label class="form-label">{{ t('adminProgramDestinations.country') }}</label>
              <SearchableSelect
                v-model="inst.country"
                :options="countryOptions"
                :placeholder="t('adminProgramDestinations.countryPlaceholder')"
                :disabled="busy"
                @update:model-value="saveInstitution(inst)"
              />
            </div>
            <div class="col-md-5">
              <label class="form-label">{{ t('adminProgramDestinations.gradeScale') }}</label>
              <select v-model="inst.grade_scale" class="form-select" @change="saveInstitution(inst)">
                <option value="">{{ t('adminProgramDestinations.noGradeScale') }}</option>
                <option v-for="scale in gradeScales" :key="scale.id" :value="scale.id">
                  {{ scale.name }}
                </option>
              </select>
            </div>
          </div>

          <h6>{{ t('adminProgramDestinations.universitySubjects') }}</h6>
          <SubjectEditor
            :subjects="subjectsByParent.institution[inst.id] || []"
            parent-level="institution"
            :busy="busy"
            @create="(payload) => createSubject({ ...payload, institution: inst.id })"
            @toggle="toggleSubject"
          />

          <h6 class="mt-4">{{ t('adminProgramDestinations.schools') }}</h6>
          <div class="row g-2 mb-2">
            <div class="col-md-6">
              <input v-model="schoolDrafts[inst.id]" class="form-control" :placeholder="t('adminProgramDestinations.newSchool')">
            </div>
            <div class="col-md-3">
              <button
                type="button"
                class="btn btn-outline-primary"
                :disabled="busy || !schoolDrafts[inst.id]"
                @click="createSchool(inst)"
              >
                {{ t('adminProgramDestinations.addSchool') }}
              </button>
            </div>
          </div>
          <div v-for="school in schoolsByInst[inst.id] || []" :key="school.id" class="border rounded p-3 mb-2">
            <div class="d-flex gap-2 align-items-center mb-2">
              <input v-model="school.name" class="form-control" @change="saveSchool(school)">
              <button type="button" class="btn btn-sm btn-outline-secondary" @click="toggleActive(school, 'school')">
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
            <div class="row g-2 mt-2">
              <div class="col-md-6">
                <input v-model="programDrafts[school.id]" class="form-control" :placeholder="t('adminProgramDestinations.newProgram')">
              </div>
              <div class="col-md-3">
                <button
                  type="button"
                  class="btn btn-outline-primary btn-sm"
                  :disabled="busy || !programDrafts[school.id]"
                  @click="createAcademic(school)"
                >
                  {{ t('adminProgramDestinations.addProgram') }}
                </button>
              </div>
            </div>
            <div v-for="ap in programsBySchool[school.id] || []" :key="ap.id" class="ms-3 mt-2 border-start ps-3">
              <div class="d-flex gap-2 align-items-center mb-2">
                <input v-model="ap.name" class="form-control" @change="saveAcademic(ap)">
                <input v-model="ap.code" class="form-control" style="max-width: 8rem" @change="saveAcademic(ap)">
                <button type="button" class="btn btn-sm btn-outline-secondary" @click="toggleActive(ap, 'academic')">
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
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import PageHeader from '@/components/PageHeader.vue'
import SearchableSelect from '@/components/SearchableSelect.vue'
import api from '@/services/api'

const { t } = useI18n()
const route = useRoute()
const programId = computed(() => route.params.id)

const loading = ref(true)
const busy = ref(false)
const error = ref('')
const programName = ref('')
const institutions = ref([])
const gradeScales = ref([])
const schoolsByInst = ref({})
const programsBySchool = ref({})
const subjectsByParent = reactive({ institution: {}, school: {}, academic: {} })
const countryOptions = ref([])
const schoolDrafts = reactive({})
const programDrafts = reactive({})
const newUni = reactive({ name: '', country: '', grade_scale: '' })

const headerTitle = computed(() =>
  programName.value
    ? t('adminProgramDestinations.titleNamed', { name: programName.value })
    : t('adminProgramDestinations.title'),
)

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

function unwrap(data) {
  if (Array.isArray(data)) return data
  if (data?.results) return data.results
  return []
}

async function loadGradeScales() {
  const { data } = await api.get('/api/grades/scales/active/')
  gradeScales.value = unwrap(data)
}

async function loadCountryOptions() {
  const { data } = await api.get('/api/accounts/catalogs/countries/')
  countryOptions.value = unwrap(data)
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
    await reload()
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
  busy.value = true
  try {
    await api.post(`/api/host-institutions/${inst.id}/schools/`, {
      name: schoolDrafts[inst.id],
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
  busy.value = true
  try {
    await api.post(`/api/schools/${school.id}/academic-programs/`, {
      name: programDrafts[school.id],
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
  await Promise.all([loadGradeScales(), loadCountryOptions()])
  await reload()
})
</script>
