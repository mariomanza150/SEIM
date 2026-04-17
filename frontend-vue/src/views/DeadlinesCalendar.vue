<template>
  <div class="deadlines-calendar-page" data-testid="deadlines-calendar-page">
    <nav :aria-label="t('calendarPage.breadcrumbAria')">
      <ol class="breadcrumb">
        <li class="breadcrumb-item">
          <router-link :to="{ name: 'Dashboard' }">{{ t('route.names.Dashboard') }}</router-link>
        </li>
        <li class="breadcrumb-item active">{{ t('route.names.DeadlinesCalendar') }}</li>
      </ol>
    </nav>

      <div class="row mb-4">
        <div class="col-lg-8">
          <h2><i class="bi bi-calendar3 me-2"></i>{{ t('route.names.DeadlinesCalendar') }}</h2>
          <p class="text-muted mb-0">
            {{ t('calendarPage.pageSubtitle') }}
          </p>
        </div>
        <div class="col-lg-4 mt-3 mt-lg-0">
          <div class="card border-secondary-subtle h-100">
            <div class="card-body py-3">
              <div class="fw-semibold mb-2">
                <i class="bi bi-rss me-1" aria-hidden="true" />{{ t('calendarPage.subscribeHeading') }}
              </div>
              <p class="small text-muted mb-2">
                {{ t('calendarPage.subscribeBody') }}
              </p>
              <div v-if="subscribeLoading" class="small text-muted">{{ t('calendarPage.subscribeLoading') }}</div>
              <template v-else-if="subscribeUrls">
                <label class="form-label small text-muted mb-1" for="cal-ics-url">{{
                  t('calendarPage.subscribeLabelHttps')
                }}</label>
                <div class="input-group input-group-sm mb-2">
                  <input id="cal-ics-url" :value="subscribeUrls.ics_url" type="text" class="form-control font-monospace small" readonly>
                  <button type="button" class="btn btn-outline-secondary" @click="copySubscribe(subscribeUrls.ics_url)">
                    {{ t('calendarPage.copy') }}
                  </button>
                </div>
                <label class="form-label small text-muted mb-1" for="cal-webcal-url">{{
                  t('calendarPage.subscribeLabelWebcal')
                }}</label>
                <div class="input-group input-group-sm">
                  <input id="cal-webcal-url" :value="subscribeUrls.webcal_url" type="text" class="form-control font-monospace small" readonly>
                  <button type="button" class="btn btn-outline-secondary" @click="copySubscribe(subscribeUrls.webcal_url)">
                    {{ t('calendarPage.copy') }}
                  </button>
                </div>
              </template>
              <div v-else class="small text-danger">{{ t('calendarPage.subscribeLoadError') }}</div>
            </div>
          </div>
        </div>
      </div>

      <div class="card mb-4">
        <div class="card-body">
          <div class="row g-3 align-items-end">
            <div class="col-md-4">
              <label class="form-label small text-muted">{{ t('calendarPage.rangeFrom') }}</label>
              <input v-model="rangeStart" type="date" class="form-control">
            </div>
            <div class="col-md-4">
              <label class="form-label small text-muted">{{ t('calendarPage.rangeTo') }}</label>
              <input v-model="rangeEnd" type="date" class="form-control">
            </div>
            <div class="col-md-4">
              <button type="button" class="btn btn-primary w-100" :disabled="loading" @click="loadEvents">
                {{ t('calendarPage.refresh') }}
              </button>
            </div>
            <div class="col-12">
              <span class="form-label small text-muted d-block mb-1">{{ t('calendarPage.showLabel') }}</span>
              <div class="d-flex flex-wrap gap-3">
                <div class="form-check">
                  <input id="cf-prog" v-model="show.program" class="form-check-input" type="checkbox">
                  <label class="form-check-label" for="cf-prog">{{ t('calendarPage.showProgramRun') }}</label>
                </div>
                <div class="form-check">
                  <input id="cf-dead" v-model="show.deadline" class="form-check-input" type="checkbox">
                  <label class="form-check-label" for="cf-dead">{{ t('calendarPage.showApplyWindows') }}</label>
                </div>
                <div class="form-check">
                  <input id="cf-app" v-model="show.application" class="form-check-input" type="checkbox">
                  <label class="form-check-label" for="cf-app">{{ t('calendarPage.showApplications') }}</label>
                </div>
                <div v-if="authStore.canUseStaffReviewQueue" class="form-check">
                  <input id="cf-agr" v-model="show.agreement" class="form-check-input" type="checkbox">
                  <label class="form-check-label" for="cf-agr">{{ t('calendarPage.showAgreementsStaff') }}</label>
                </div>
              </div>
            </div>
            <div class="col-12 border-top pt-3 mt-2">
              <span class="form-label small text-muted d-block mb-2">{{ t('calendarPage.savedViewsLabel') }}</span>
              <div class="d-flex flex-wrap align-items-end gap-2 mb-2">
                <div class="flex-grow-1" style="min-width: 200px">
                  <input
                    v-model="newPresetName"
                    type="text"
                    class="form-control form-control-sm"
                    :placeholder="t('calendarPage.presetNamePlaceholder')"
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
                  {{ t('calendarPage.saveView') }}
                </button>
                <div class="form-check mb-0">
                  <input id="cal-preset-def" v-model="saveAsDefault" class="form-check-input" type="checkbox">
                  <label class="form-check-label small" for="cal-preset-def">{{
                    t('calendarPage.presetDefaultCheckbox')
                  }}</label>
                </div>
              </div>
              <div v-if="savedPresets.length" class="small">
                <span class="text-muted me-2">{{ t('calendarPage.presetSavedPrefix') }}</span>
                <span
                  v-for="p in savedPresets"
                  :key="p.id"
                  class="d-inline-flex align-items-center gap-1 me-3 mb-1"
                >
                  <button type="button" class="btn btn-link btn-sm p-0" @click="applyPreset(p)">{{ p.name }}</button>
                  <i
                    v-if="p.is_default"
                    class="bi bi-star-fill text-warning"
                    :title="t('calendarPage.presetDefaultTitle')"
                    :aria-label="t('calendarPage.presetDefaultAria')"
                  ></i>
                  <button
                    v-else
                    type="button"
                    class="btn btn-link btn-sm p-0 text-secondary"
                    :title="t('calendarPage.presetSetDefaultTitle')"
                    :aria-label="t('calendarPage.presetSetDefaultAria')"
                    @click="setDefaultPreset(p)"
                  >
                    <i class="bi bi-star"></i>
                  </button>
                  <button
                    type="button"
                    class="btn btn-link btn-sm p-0 text-danger"
                    :title="t('calendarPage.presetRemoveTitle')"
                    :aria-label="t('calendarPage.presetRemoveAria')"
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
          <span class="visually-hidden">{{ t('calendarPage.loading') }}</span>
        </div>
      </div>
      <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
      <div v-else-if="!groupedDays.length" class="alert alert-info mb-0" data-testid="calendar-empty">
        {{ t('calendarPage.emptyRange') }}
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
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
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
const { t, locale } = useI18n()
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

function calendarLocaleTag() {
  return locale.value === 'es' ? 'es' : 'en-US'
}

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
  const loc = calendarLocaleTag()
  return keys.map((key) => ({
    key,
    label: new Date(`${key}T12:00:00`).toLocaleDateString(loc, {
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
    error.value = t('calendarPage.loadError')
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
    successToast(t('calendarPage.copiedToast'))
  } catch (e) {
    console.error(e)
    errorToast(t('calendarPage.copyErrorToast'))
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
