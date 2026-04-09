<template>
  <div class="deadlines-calendar-page" data-testid="deadlines-calendar-page">
    <div class="container-fluid mt-4">
      <nav aria-label="breadcrumb">
        <ol class="breadcrumb">
          <li class="breadcrumb-item">
            <router-link :to="{ name: 'Dashboard' }">Dashboard</router-link>
          </li>
          <li class="breadcrumb-item active">Deadlines &amp; milestones</li>
        </ol>
      </nav>

      <div class="row mb-4">
        <div class="col-lg-8">
          <h2><i class="bi bi-calendar3 me-2"></i>Deadlines &amp; milestones</h2>
          <p class="text-muted mb-0">
            Program dates, application windows, your applications, and (for staff) agreement end dates from the SEIM calendar API.
          </p>
        </div>
        <div class="col-lg-4 mt-3 mt-lg-0">
          <div class="card border-secondary-subtle h-100">
            <div class="card-body py-3">
              <div class="fw-semibold mb-2">
                <i class="bi bi-rss me-1" aria-hidden="true" />Subscribe (ICS)
              </div>
              <p class="small text-muted mb-2">
                Private link for Google Calendar, Apple Calendar, etc. Same events as &ldquo;all types&rdquo; here (~90d past–730d ahead). Do not share the URL.
              </p>
              <div v-if="subscribeLoading" class="small text-muted">Loading link…</div>
              <template v-else-if="subscribeUrls">
                <label class="form-label small text-muted mb-1" for="cal-ics-url">HTTPS (paste / import by URL)</label>
                <div class="input-group input-group-sm mb-2">
                  <input id="cal-ics-url" :value="subscribeUrls.ics_url" type="text" class="form-control font-monospace small" readonly>
                  <button type="button" class="btn btn-outline-secondary" @click="copySubscribe(subscribeUrls.ics_url)">
                    Copy
                  </button>
                </div>
                <label class="form-label small text-muted mb-1" for="cal-webcal-url">Webcal (one-click subscribe)</label>
                <div class="input-group input-group-sm">
                  <input id="cal-webcal-url" :value="subscribeUrls.webcal_url" type="text" class="form-control font-monospace small" readonly>
                  <button type="button" class="btn btn-outline-secondary" @click="copySubscribe(subscribeUrls.webcal_url)">
                    Copy
                  </button>
                </div>
              </template>
              <div v-else class="small text-danger">Could not load subscribe link.</div>
            </div>
          </div>
        </div>
      </div>

      <div class="card mb-4">
        <div class="card-body">
          <div class="row g-3 align-items-end">
            <div class="col-md-4">
              <label class="form-label small text-muted">From</label>
              <input v-model="rangeStart" type="date" class="form-control">
            </div>
            <div class="col-md-4">
              <label class="form-label small text-muted">To</label>
              <input v-model="rangeEnd" type="date" class="form-control">
            </div>
            <div class="col-md-4">
              <button type="button" class="btn btn-primary w-100" :disabled="loading" @click="loadEvents">
                Refresh
              </button>
            </div>
            <div class="col-12">
              <span class="form-label small text-muted d-block mb-1">Show</span>
              <div class="d-flex flex-wrap gap-3">
                <div class="form-check">
                  <input id="cf-prog" v-model="show.program" class="form-check-input" type="checkbox">
                  <label class="form-check-label" for="cf-prog">Program run dates</label>
                </div>
                <div class="form-check">
                  <input id="cf-dead" v-model="show.deadline" class="form-check-input" type="checkbox">
                  <label class="form-check-label" for="cf-dead">Apply windows / deadlines</label>
                </div>
                <div class="form-check">
                  <input id="cf-app" v-model="show.application" class="form-check-input" type="checkbox">
                  <label class="form-check-label" for="cf-app">Applications</label>
                </div>
                <div v-if="authStore.canUseStaffReviewQueue" class="form-check">
                  <input id="cf-agr" v-model="show.agreement" class="form-check-input" type="checkbox">
                  <label class="form-check-label" for="cf-agr">Agreements (staff)</label>
                </div>
              </div>
            </div>
            <div class="col-12 border-top pt-3 mt-2">
              <span class="form-label small text-muted d-block mb-2">Saved views</span>
              <div class="d-flex flex-wrap align-items-end gap-2 mb-2">
                <div class="flex-grow-1" style="min-width: 200px">
                  <input
                    v-model="newPresetName"
                    type="text"
                    class="form-control form-control-sm"
                    placeholder="Preset name"
                    data-testid="calendar-preset-name"
                  >
                </div>
                <button
                  type="button"
                  class="btn btn-sm btn-outline-primary"
                  :disabled="!newPresetName.trim() || presetsLoading"
                  data-testid="calendar-preset-save"
                  @click="savePreset(() => serializeCalendarFilters({ rangeStart, rangeEnd, show }))"
                >
                  Save view
                </button>
                <div class="form-check mb-0">
                  <input id="cal-preset-def" v-model="saveAsDefault" class="form-check-input" type="checkbox">
                  <label class="form-check-label small" for="cal-preset-def">Default when opening this page</label>
                </div>
              </div>
              <div v-if="savedPresets.length" class="small">
                <span class="text-muted me-2">Saved:</span>
                <span
                  v-for="p in savedPresets"
                  :key="p.id"
                  class="d-inline-flex align-items-center gap-1 me-3 mb-1"
                >
                  <button type="button" class="btn btn-link btn-sm p-0" @click="applyPreset(p)">{{ p.name }}</button>
                  <i
                    v-if="p.is_default"
                    class="bi bi-star-fill text-warning"
                    title="Default preset"
                    aria-label="Default preset"
                  ></i>
                  <button
                    v-else
                    type="button"
                    class="btn btn-link btn-sm p-0 text-secondary"
                    title="Set as default"
                    aria-label="Set as default"
                    @click="setDefaultPreset(p)"
                  >
                    <i class="bi bi-star"></i>
                  </button>
                  <button
                    type="button"
                    class="btn btn-link btn-sm p-0 text-danger"
                    title="Remove preset"
                    aria-label="Remove preset"
                    @click="deletePreset(p)"
                  >
                    <i class="bi bi-trash"></i>
                  </button>
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading…</span>
        </div>
      </div>
      <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
      <div v-else-if="!groupedDays.length" class="alert alert-info mb-0">
        No events in this range with the current filters.
      </div>
      <div v-else class="card">
        <ul class="list-group list-group-flush">
          <li v-for="day in groupedDays" :key="day.key" class="list-group-item">
            <div class="fw-semibold mb-2">{{ day.label }}</div>
            <ul class="mb-0 ps-3">
              <li v-for="ev in day.events" :key="ev.id" class="mb-2">
                <button
                  type="button"
                  class="btn btn-link btn-sm p-0 text-start text-decoration-none"
                  :style="{ borderLeft: `3px solid ${ev.borderColor || '#6c757d'}`, paddingLeft: '0.5rem' }"
                  @click="openEvent(ev)"
                >
                  {{ ev.title }}
                </button>
              </li>
            </ul>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import { useStaffSavedPresets } from '@/composables/useStaffSavedPresets'
import {
  STAFF_SAVED_SEARCH_TYPE,
  deserializeCalendarFilters,
  serializeCalendarFilters,
} from '@/utils/staffListSearchPresets'

const router = useRouter()
const authStore = useAuthStore()
const { error: errorToast, success: successToast } = useToast()

const {
  savedPresets,
  newPresetName,
  saveAsDefault,
  presetsLoading,
  loadPresets,
  savePreset,
  deletePreset,
  setDefaultPreset,
} = useStaffSavedPresets(STAFF_SAVED_SEARCH_TYPE.DEADLINES_CALENDAR)

const loading = ref(true)
const error = ref('')
const rawEvents = ref([])
const subscribeUrls = ref(null)
const subscribeLoading = ref(true)

const rangeStart = ref('')
const rangeEnd = ref('')
const show = ref({
  program: true,
  deadline: true,
  application: true,
  agreement: true,
})

function defaultRange() {
  const a = new Date()
  const b = new Date()
  a.setMonth(a.getMonth() - 1)
  b.setMonth(b.getMonth() + 6)
  rangeStart.value = a.toISOString().slice(0, 10)
  rangeEnd.value = b.toISOString().slice(0, 10)
}

function eventCategory(ev) {
  const id = String(ev.id || '')
  if (id.startsWith('application-')) return 'application'
  if (id.startsWith('agreement-')) return 'agreement'
  if (id.startsWith('program-app-open-') || id.startsWith('program-app-deadline-')) return 'deadline'
  if (id.startsWith('program-start-') || id.startsWith('program-end-')) return 'program'
  return 'program'
}

const visibleEvents = computed(() => {
  return rawEvents.value.filter((ev) => {
    const cat = eventCategory(ev)
    if (cat === 'application') return show.value.application
    if (cat === 'agreement') return show.value.agreement && authStore.canUseStaffReviewQueue
    if (cat === 'deadline') return show.value.deadline
    if (cat === 'program') return show.value.program
    return true
  })
})

const groupedDays = computed(() => {
  const map = new Map()
  for (const ev of visibleEvents.value) {
    const d = new Date(ev.start)
    if (Number.isNaN(d.getTime())) continue
    const key = d.toISOString().slice(0, 10)
    if (!map.has(key)) map.set(key, [])
    map.get(key).push(ev)
  }
  const keys = [...map.keys()].sort()
  return keys.map((key) => ({
    key,
    label: new Date(`${key}T12:00:00`).toLocaleDateString(undefined, {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    }),
    events: map.get(key).sort((a, b) => String(a.title).localeCompare(String(b.title))),
  }))
})

async function loadEvents() {
  loading.value = true
  error.value = ''
  try {
    const start = new Date(`${rangeStart.value}T00:00:00`)
    const end = new Date(`${rangeEnd.value}T23:59:59`)
    const params = {
      start: start.toISOString(),
      end: end.toISOString(),
      type: 'all',
    }
    const { data } = await api.get('/api/calendar/events/', { params })
    rawEvents.value = Array.isArray(data) ? data : data.results || []
  } catch (e) {
    console.error(e)
    error.value = 'Could not load calendar events.'
    errorToast(error.value)
    rawEvents.value = []
  } finally {
    loading.value = false
  }
}

function openEvent(ev) {
  const path = ev.spa_path
  if (path && typeof path === 'string') {
    router.push(path)
  }
}

async function loadSubscribeUrls() {
  subscribeLoading.value = true
  try {
    const { data } = await api.get('/api/calendar/events/subscribe-token/')
    subscribeUrls.value = data
  } catch (e) {
    console.error(e)
    subscribeUrls.value = null
  } finally {
    subscribeLoading.value = false
  }
}

async function copySubscribe(text) {
  try {
    await navigator.clipboard.writeText(text)
    successToast('Copied to clipboard')
  } catch (e) {
    console.error(e)
    errorToast('Could not copy')
  }
}

function applyPreset(p) {
  const f = deserializeCalendarFilters(p.filters)
  if (f.rangeStart) rangeStart.value = f.rangeStart
  if (f.rangeEnd) rangeEnd.value = f.rangeEnd
  show.value = { ...show.value, ...f.show }
  loadEvents()
}

onMounted(async () => {
  defaultRange()
  loadSubscribeUrls()
  await loadPresets()
  const def = savedPresets.value.find((p) => p.is_default)
  if (def) {
    applyPreset(def)
  } else {
    await loadEvents()
  }
})
</script>

<style scoped>
.deadlines-calendar-page {
  min-height: 100vh;
  background-color: var(--seim-app-bg, #f8f9fa);
}
</style>
