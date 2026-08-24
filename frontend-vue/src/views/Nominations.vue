<template>
  <div class="nominations-page">
    <PageHeader :title="t('route.names.Nominations')" :subtitle="t('nominationsPage.subtitle')">
      <template #breadcrumb>
        <PageBreadcrumb
          :aria-label="t('nominationsPage.breadcrumbAria')"
          :items="[
            { to: { name: 'Dashboard' }, label: t('route.names.Dashboard') },
            { label: t('route.names.Nominations') },
          ]"
        />
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
          <div v-if="payload.active_cycle" data-testid="nominations-active-cycle">
            {{
              t('nominationsPage.activeCycle', {
                name: payload.active_cycle.name,
                open: payload.active_cycle.is_open ? t('nominationsPage.cycleOpen') : t('nominationsPage.cycleClosed'),
              })
            }}
            <span v-if="payload.active_cycle.seat_quota != null">
              · {{ t('nominationsPage.cycleQuota', { n: payload.active_cycle.seat_quota }) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <div
      v-if="payload?.partner_allocations?.length"
      class="card mb-4"
      data-testid="nominations-partner-allocations"
    >
      <div class="card-header fw-medium">{{ t('nominationsPage.partnerAllocations') }}</div>
      <ul class="list-group list-group-flush">
        <li
          v-for="alloc in payload.partner_allocations"
          :key="alloc.id"
          class="list-group-item d-flex justify-content-between"
        >
          <span>{{ alloc.partner_institution_name }} — {{ alloc.agreement_title }}</span>
          <span class="text-muted">{{ t('nominationsPage.allocationSeats', { n: alloc.seat_quota }) }}</span>
        </li>
      </ul>
    </div>

    <PageStateShell
      v-if="programId"
      :loading="loading"
      :error="error"
      :empty="!loading && !error && rows.length === 0"
      :empty-body="t('nominationsPage.empty')"
      empty-test-id="nominations-empty"
      :loading-label="t('nominationsPage.loading')"
      skeleton="table"
      :skeleton-columns="4"
    >
      <ResponsiveList
        v-if="rows.length"
        :items="rows"
        :columns="nominationColumns"
        mobile-test-id="nominations-mobile"
      >
        <div class="card" data-testid="nominations-table">
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
                  <td data-testid="nomination-status">{{ formatStatus(row.status) }}</td>
                  <td style="max-width: 8rem">
                    <input
                      v-model.number="row.nomination_rank"
                      type="number"
                      min="1"
                      class="form-control form-control-sm"
                      data-testid="nomination-rank"
                    />
                  </td>
                  <td class="small text-muted" data-testid="nomination-submitted-at">{{ formatSubmittedAt(row.submitted_at) }}</td>
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
        <template #col-status="{ item }">
          {{ formatStatus(item.status) }}
        </template>
        <template #col-nomination_rank="{ item }">
          <input
            v-model.number="item.nomination_rank"
            type="number"
            min="1"
            class="form-control form-control-sm"
            data-testid="nomination-rank"
          />
        </template>
        <template #col-submitted_at="{ item }">
          <span class="small text-muted">{{ formatSubmittedAt(item.submitted_at) }}</span>
        </template>
      </ResponsiveList>
    </PageStateShell>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useToast } from '@/composables/useToast'
import api from '@/services/api'
import PageHeader from '@/components/PageHeader.vue'
import PageBreadcrumb from '@/components/PageBreadcrumb.vue'
import PageStateShell from '@/components/State/PageStateShell.vue'
import ResponsiveList from '@/components/ResponsiveList.vue'
import { formatApplicationStatus, formatDateTime as formatDateTimeUtil } from '@/utils/formatters'

const { t, te, locale } = useI18n()
const route = useRoute()
const { success: successToast, error: errorToast } = useToast()

const nominationColumns = computed(() => [
  { key: 'student_display_name', label: t('nominationsPage.colStudent') },
  { key: 'status', label: t('nominationsPage.colStatus') },
  { key: 'nomination_rank', label: t('nominationsPage.colRank') },
  { key: 'submitted_at', label: t('nominationsPage.colSubmitted') },
])

const programs = ref([])
const programId = ref('')
const payload = ref(null)
const rows = ref([])
const loading = ref(false)
const busy = ref(false)
const error = ref('')

function formatSubmittedAt(value) {
  return formatDateTimeUtil({ dateString: value, locale: locale.value, fallback: '—' })
}

function formatStatus(status) {
  return formatApplicationStatus({ status, t, te })
}

function applyPayload(data) {
  payload.value = data
  rows.value = (data.applications || []).map((r) => ({ ...r }))
}

async function loadPrograms() {
    const { data } = await api.get('/api/programs/', { params: { page_size: 100, ordering: 'name' } })
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

onMounted(async () => {
  await loadPrograms()
  const programFromQuery = route.query.program
  if (typeof programFromQuery === 'string' && programs.value.some((p) => p.id === programFromQuery)) {
    programId.value = programFromQuery
    await loadNominations()
  }
})
</script>
