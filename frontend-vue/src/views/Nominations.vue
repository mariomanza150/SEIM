<template>
  <div class="nominations-page">
    <PageHeader :title="t('route.names.Nominations')" :subtitle="t('nominationsPage.subtitle')">
      <template #breadcrumb>
        <nav :aria-label="t('exchangeAgreementsPage.breadcrumbAria')">
          <ol class="breadcrumb">
            <li class="breadcrumb-item">
              <router-link :to="{ name: 'Dashboard' }">{{ t('route.names.Dashboard') }}</router-link>
            </li>
            <li class="breadcrumb-item active">{{ t('route.names.Nominations') }}</li>
          </ol>
        </nav>
      </template>
    </PageHeader>

    <div class="card mb-4">
      <div class="card-body row g-3 align-items-end">
        <div class="col-md-6">
          <label class="form-label" for="nom-program">{{ t('nominationsPage.programLabel') }}</label>
          <select
            id="nom-program"
            v-model="programId"
            class="form-select"
            data-testid="nominations-program"
            @change="loadNominations"
          >
            <option value="">{{ t('nominationsPage.programPlaceholder') }}</option>
            <option v-for="p in programs" :key="p.id" :value="p.id">{{ p.name }}</option>
          </select>
        </div>
        <div v-if="payload" class="col-md-6 small text-muted">
          <div>
            {{
              payload.enrollment_capacity == null
                ? t('nominationsPage.capacityUnlimited')
                : t('nominationsPage.capacity', { n: payload.enrollment_capacity })
            }}
          </div>
          <div v-if="payload.slots_remaining != null">
            {{ t('nominationsPage.slotsRemaining', { n: payload.slots_remaining }) }}
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="text-center py-4">
      <div class="spinner-border text-primary" role="status"></div>
    </div>
    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-else-if="programId && rows.length === 0" class="alert alert-info" data-testid="nominations-empty">
      {{ t('nominationsPage.empty') }}
    </div>
    <div v-else-if="rows.length" class="card" data-testid="nominations-table">
      <div class="table-responsive">
        <table class="table mb-0">
          <thead>
            <tr>
              <th>{{ t('nominationsPage.colStudent') }}</th>
              <th>{{ t('nominationsPage.colStatus') }}</th>
              <th>{{ t('nominationsPage.colRank') }}</th>
              <th>{{ t('nominationsPage.colSubmitted') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in rows" :key="row.id">
              <td>{{ row.student_display_name }}</td>
              <td>{{ row.status }}</td>
              <td style="max-width: 8rem">
                <input
                  v-model.number="row.nomination_rank"
                  type="number"
                  min="1"
                  class="form-control form-control-sm"
                  data-testid="nomination-rank"
                />
              </td>
              <td class="small text-muted">{{ row.submitted_at || '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="card-footer d-flex gap-2">
        <button type="button" class="btn btn-outline-primary" :disabled="busy" data-testid="nominations-save" @click="saveRanks">
          {{ t('nominationsPage.saveRanks') }}
        </button>
        <button type="button" class="btn btn-primary" :disabled="busy" data-testid="nominations-match" @click="runMatch">
          {{ t('nominationsPage.runMatch') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useToast } from '@/composables/useToast'
import api from '@/services/api'
import PageHeader from '@/components/PageHeader.vue'

const { t } = useI18n()
const { success: successToast, error: errorToast } = useToast()

const programs = ref([])
const programId = ref('')
const payload = ref(null)
const rows = ref([])
const loading = ref(false)
const busy = ref(false)
const error = ref('')

function applyPayload(data) {
  payload.value = data
  rows.value = (data.applications || []).map((r) => ({ ...r }))
}

async function loadPrograms() {
  const { data } = await api.get('/api/programs/', { params: { page_size: 200, ordering: 'name' } })
  programs.value = data.results ?? data ?? []
}

async function loadNominations() {
  if (!programId.value) {
    payload.value = null
    rows.value = []
    return
  }
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get(`/api/programs/${programId.value}/nominations/`)
    applyPayload(data)
  } catch {
    error.value = t('nominationsPage.loadError')
    errorToast(error.value)
  } finally {
    loading.value = false
  }
}

async function saveRanks() {
  busy.value = true
  try {
    const { data } = await api.put(`/api/programs/${programId.value}/nominations/`, {
      ranks: rows.value.map((r) => ({
        id: r.id,
        rank: r.nomination_rank === '' ? null : r.nomination_rank,
      })),
    })
    applyPayload(data)
    successToast(t('nominationsPage.saveSuccess'))
  } catch {
    errorToast(t('nominationsPage.loadError'))
  } finally {
    busy.value = false
  }
}

async function runMatch() {
  busy.value = true
  try {
    const { data } = await api.post(`/api/programs/${programId.value}/nominations/match/`)
    applyPayload(data)
    const m = data.matched || {}
    successToast(
      t('nominationsPage.matchSuccess', {
        nominated: m.nominated ?? 0,
        waitlisted: m.waitlisted ?? 0,
      }),
    )
  } catch {
    errorToast(t('nominationsPage.loadError'))
  } finally {
    busy.value = false
  }
}

onMounted(loadPrograms)
</script>
