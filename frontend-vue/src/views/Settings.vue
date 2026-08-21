<template>
  <div class="settings-page">
    <PageHeader :title="t('route.names.Settings')" :subtitle="t('settings.pageSubtitle')" icon-class="bi bi-gear">
      <template #breadcrumb>
        <nav :aria-label="t('settings.breadcrumbAria')">
          <ol class="breadcrumb">
            <li class="breadcrumb-item">
              <router-link :to="{ name: 'Dashboard' }">{{ t('route.names.Dashboard') }}</router-link>
            </li>
            <li class="breadcrumb-item active">{{ t('route.names.Settings') }}</li>
          </ol>
        </nav>
      </template>
    </PageHeader>

      <div v-if="loading" class="text-center py-5">
        <div
          class="spinner-border text-primary"
          role="status"
          :aria-label="t('settings.loading')"
        ></div>
        <p class="mt-3 text-muted">{{ t('settings.loading') }}</p>
      </div>

      <div v-else class="row">
        <div class="col-lg-8">
          <div class="card">
            <div class="card-body">
              <form @submit.prevent="handleSubmit">
                <h6 class="text-muted mb-3">{{ t('settings.sectionAppearance') }}</h6>
                <div class="row mb-3">
                  <div class="col-md-6">
                    <label class="form-label" for="ui_language">{{ t('settings.uiLanguage') }}</label>
                    <select
                      id="ui_language"
                      v-model="locale"
                      class="form-select"
                      name="ui_language"
                      autocomplete="off"
                      data-testid="settings-ui-language"
                      @change="onLocaleChange"
                    >
                      <option value="en">{{ t('settings.langOptionEn') }}</option>
                      <option value="es">{{ t('settings.langOptionEs') }}</option>
                    </select>
                    <div class="form-text">{{ t('settings.uiLanguageHelp') }}</div>
                  </div>
                </div>
                <div class="row mb-3">
                  <div class="col-md-6">
                    <label class="form-label" for="settings-theme">{{ t('settings.theme') }}</label>
                    <select
                      id="settings-theme"
                      v-model="form.theme"
                      class="form-select"
                      name="theme"
                      autocomplete="off"
                      data-testid="settings-theme"
                    >
                      <option value="light">{{ t('settings.themeLight') }}</option>
                      <option value="dark">{{ t('settings.themeDark') }}</option>
                      <option value="auto">{{ t('settings.themeAuto') }}</option>
                    </select>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label" for="settings-font-size">{{ t('settings.fontSize') }}</label>
                    <select
                      id="settings-font-size"
                      v-model="form.font_size"
                      class="form-select"
                      name="font_size"
                      autocomplete="off"
                      data-testid="settings-font-size"
                    >
                      <option value="normal">{{ t('settings.fontNormal') }}</option>
                      <option value="large">{{ t('settings.fontLarge') }}</option>
                      <option value="x-large">{{ t('settings.fontXLarge') }}</option>
                    </select>
                  </div>
                </div>
                <div class="row mb-2">
                  <div class="col-md-6">
                    <div class="form-check mb-3">
                      <input
                        id="high_contrast"
                        v-model="form.high_contrast"
                        class="form-check-input"
                        type="checkbox"
                      >
                      <label class="form-check-label" for="high_contrast">
                        {{ t('settings.highContrast') }}
                      </label>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="form-check mb-3">
                      <input
                        id="reduce_motion"
                        v-model="form.reduce_motion"
                        class="form-check-input"
                        type="checkbox"
                      >
                      <label class="form-check-label" for="reduce_motion">
                        {{ t('settings.reduceMotion') }}
                      </label>
                    </div>
                  </div>
                </div>

                <hr class="my-4" />
                <h6 class="text-muted mb-3">{{ t('settings.sectionNotifications') }}</h6>
                <div class="row">
                  <div class="col-md-6">
                    <div
                      v-for="field in notificationFields.slice(0, 5)"
                      :key="field.key"
                      class="form-check mb-3"
                    >
                      <input
                        :id="field.key"
                        v-model="form[field.key]"
                        class="form-check-input"
                        type="checkbox"
                      >
                      <label class="form-check-label" :for="field.key">
                        {{ field.label }}
                      </label>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div
                      v-for="field in notificationFields.slice(5)"
                      :key="field.key"
                      class="form-check mb-3"
                    >
                      <input
                        :id="field.key"
                        v-model="form[field.key]"
                        class="form-check-input"
                        type="checkbox"
                      >
                      <label class="form-check-label" :for="field.key">
                        {{ field.label }}
                      </label>
                    </div>
                  </div>
                </div>
                <div class="row mt-2">
                  <div class="col-md-6">
                    <label class="form-label" for="notification_digest_frequency">{{ t('settings.digestLabel') }}</label>
                    <select
                      id="notification_digest_frequency"
                      v-model="form.notification_digest_frequency"
                      class="form-select"
                      name="notification_digest_frequency"
                      autocomplete="off"
                      data-testid="settings-digest-frequency"
                    >
                      <option value="off">{{ t('settings.digestOff') }}</option>
                      <option value="daily">{{ t('settings.digestDaily') }}</option>
                      <option value="weekly">{{ t('settings.digestWeekly') }}</option>
                    </select>
                    <div class="form-text">{{ t('settings.digestHelp') }}</div>
                  </div>
                  <div class="col-md-6 d-flex align-items-end">
                    <div class="form-check mb-3">
                      <input
                        id="email_notification_digest"
                        v-model="form.email_notification_digest"
                        class="form-check-input"
                        type="checkbox"
                        :disabled="form.notification_digest_frequency === 'off'"
                        data-testid="settings-email-digest"
                      >
                      <label class="form-check-label" for="email_notification_digest">
                        {{ t('settings.emailDigest') }}
                      </label>
                    </div>
                  </div>
                </div>
                <div
                  v-if="authStore.canUseStaffReviewQueue"
                  class="alert alert-light border mt-3 mb-0 small"
                >
                  <router-link
                    :to="{ name: 'NotificationRouting' }"
                    data-testid="settings-notification-routing-link"
                  >
                    {{ t('settings.notificationRoutingStaffLink') }}
                  </router-link>
                  <span class="text-muted"> — {{ t('settings.notificationRoutingStaffHelp') }}</span>
                </div>

                <hr class="my-4" />
                <h6 class="text-muted mb-3">{{ t('settings.sectionPrivacy') }}</h6>
                <div class="form-check mb-3">
                  <input
                    id="profile_public"
                    v-model="form.profile_public"
                    class="form-check-input"
                    type="checkbox"
                  >
                  <label class="form-check-label" for="profile_public">
                    {{ t('settings.profilePublic') }}
                  </label>
                </div>
                <div class="form-check mb-3">
                  <input
                    id="share_analytics"
                    v-model="form.share_analytics"
                    class="form-check-input"
                    type="checkbox"
                  >
                  <label class="form-check-label" for="share_analytics">
                    {{ t('settings.shareAnalytics') }}
                  </label>
                </div>

                <div v-if="saveError" class="alert alert-danger">{{ saveError }}</div>
                <div class="d-flex justify-content-between mt-4">
                  <router-link :to="{ name: 'Dashboard' }" class="btn btn-outline-secondary">{{ t('settings.cancel') }}</router-link>
                  <button
                    type="submit"
                    class="btn btn-primary"
                    :disabled="saving"
                    data-testid="save-settings-btn"
                  >
                    <span v-if="saving">
                      <span class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>
                      {{ t('settings.saving') }}
                    </span>
                    <span v-else><i class="bi bi-check-circle me-2"></i>{{ t('settings.saveButton') }}</span>
                  </button>
                </div>
              </form>
            </div>
          </div>

          <div class="card mt-3">
            <div class="card-body">
              <h6 class="text-muted mb-3">{{ t('settings.sectionPassword') }}</h6>
              <form @submit.prevent="handleChangePassword" data-testid="change-password-form">
                <div class="mb-3">
                  <label class="form-label" for="settings-current-password">{{ t('settings.currentPassword') }}</label>
                  <input
                    id="settings-current-password"
                    v-model="passwordForm.old_password"
                    type="password"
                    class="form-control"
                    name="current-password"
                    autocomplete="current-password"
                    required
                    :disabled="changingPassword"
                    data-testid="settings-current-password"
                  >
                </div>
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label class="form-label" for="settings-new-password">{{ t('settings.newPassword') }}</label>
                    <input
                      id="settings-new-password"
                      v-model="passwordForm.new_password"
                      type="password"
                      class="form-control"
                      name="new-password"
                      autocomplete="new-password"
                      required
                      :disabled="changingPassword"
                      data-testid="settings-new-password"
                    >
                  </div>
                  <div class="col-md-6 mb-3">
                    <label class="form-label" for="settings-confirm-password">{{ t('settings.confirmNewPassword') }}</label>
                    <input
                      id="settings-confirm-password"
                      v-model="passwordForm.new_password2"
                      type="password"
                      class="form-control"
                      name="new-password-confirm"
                      autocomplete="new-password"
                      required
                      :disabled="changingPassword"
                      data-testid="settings-confirm-password"
                    >
                  </div>
                </div>
                <div v-if="passwordError" class="alert alert-danger" role="alert">{{ passwordError }}</div>
                <div class="d-flex justify-content-end">
                  <button
                    type="submit"
                    class="btn btn-outline-primary"
                    :disabled="changingPassword"
                    data-testid="change-password-btn"
                  >
                    <span v-if="changingPassword">
                      <span class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>
                      {{ t('settings.changingPassword') }}
                    </span>
                    <span v-else>{{ t('settings.changePassword') }}</span>
                  </button>
                </div>
              </form>
            </div>
          </div>

          <div class="card mt-3" data-testid="google-calendar-card">
            <div class="card-body">
              <h6 class="text-muted mb-3">{{ t('settings.sectionGoogleCalendar') }}</h6>
              <p class="small text-muted">{{ t('settings.googleCalendarHelp') }}</p>
              <div v-if="googleCalLoading" class="text-muted small">{{ t('settings.googleCalendarLoading') }}</div>
              <template v-else>
                <p v-if="!googleCal.configured" class="alert alert-secondary small mb-2">
                  {{ t('settings.googleCalendarNotConfigured') }}
                </p>
                <p v-else-if="googleCal.connected" class="mb-2">
                  <span class="badge bg-success me-2">{{ t('settings.googleCalendarConnected') }}</span>
                  {{ googleCal.google_email }}
                </p>
                <p v-else class="mb-2">{{ t('settings.googleCalendarDisconnected') }}</p>
                <p v-if="googleCal.last_synced_at" class="small text-muted">
                  {{ t('settings.googleCalendarLastSync', { when: googleCal.last_synced_at }) }}
                </p>
                <p v-if="googleCal.last_sync_error" class="small text-danger">{{ googleCal.last_sync_error }}</p>
                <div class="d-flex flex-wrap gap-2">
                  <button
                    v-if="googleCal.configured && !googleCal.connected"
                    type="button"
                    class="btn btn-sm btn-primary"
                    data-testid="google-calendar-connect"
                    :disabled="googleCalBusy"
                    @click="connectGoogleCalendar"
                  >
                    {{ t('settings.googleCalendarConnect') }}
                  </button>
                  <button
                    v-if="googleCal.connected"
                    type="button"
                    class="btn btn-sm btn-outline-primary"
                    data-testid="google-calendar-sync"
                    :disabled="googleCalBusy"
                    @click="syncGoogleCalendar"
                  >
                    {{ t('settings.googleCalendarSync') }}
                  </button>
                  <button
                    v-if="googleCal.connected"
                    type="button"
                    class="btn btn-sm btn-outline-danger"
                    data-testid="google-calendar-disconnect"
                    :disabled="googleCalBusy"
                    @click="disconnectGoogleCalendar"
                  >
                    {{ t('settings.googleCalendarDisconnect') }}
                  </button>
                </div>
              </template>
            </div>
          </div>
        </div>

        <div class="col-lg-4">
          <div class="card mb-4">
            <div class="card-header"><h6 class="mb-0"><i class="bi bi-person me-2"></i>{{ t('settings.sidebarProfileTitle') }}</h6></div>
            <div class="card-body small">
              <p class="mb-3">{{ t('settings.sidebarProfileBody') }}</p>
              <router-link :to="{ name: 'Profile' }" class="btn btn-outline-primary btn-sm">
                {{ t('settings.sidebarProfileCta') }}
              </router-link>
            </div>
          </div>
          <div class="card mb-4" data-testid="settings-help-card">
            <div class="card-header"><h6 class="mb-0"><i class="bi bi-question-circle me-2"></i>{{ t('settings.sidebarHelpTitle') }}</h6></div>
            <div class="card-body small">
              <p class="mb-3">{{ t('settings.sidebarHelpBody') }}</p>
              <router-link :to="{ name: 'HelpCenter' }" class="btn btn-outline-primary btn-sm" data-testid="settings-help-link">
                {{ t('settings.sidebarHelpCta') }}
              </router-link>
            </div>
          </div>
          <div class="card">
            <div class="card-header"><h6 class="mb-0"><i class="bi bi-shield-check me-2"></i>{{ t('settings.sidebarNoteTitle') }}</h6></div>
            <div class="card-body small">
              {{ t('settings.sidebarNoteBody') }}
            </div>
          </div>
        </div>
      </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useToast } from '@/composables/useToast'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'
import PageHeader from '@/components/PageHeader.vue'
import { applyUiPreferences } from '@/services/uiPreferences'
import { setAppLocale } from '@/i18n'
import router from '@/router'
import { resolveDocumentTitle, syncAppSocialMeta } from '@/utils/documentTitle'

const authStore = useAuthStore()
const route = useRoute()
const { t, locale } = useI18n()

function onLocaleChange() {
  setAppLocale(locale.value)
  document.title = resolveDocumentTitle(router.currentRoute.value)
  syncAppSocialMeta(t, router.currentRoute.value)
}

const { success, error: errorToast } = useToast()
const loading = ref(true)
const saving = ref(false)
const saveError = ref('')
const changingPassword = ref(false)
const passwordError = ref('')
const passwordForm = ref({
  old_password: '',
  new_password: '',
  new_password2: '',
})
const googleCalLoading = ref(true)
const googleCalBusy = ref(false)
const googleCal = ref({
  configured: false,
  connected: false,
  google_email: '',
  last_synced_at: null,
  last_sync_error: '',
})

const defaultForm = () => ({
  theme: 'auto',
  font_size: 'normal',
  high_contrast: false,
  reduce_motion: false,
  email_applications: true,
  email_documents: true,
  email_comments: true,
  email_programs: false,
  email_system: true,
  inapp_applications: true,
  inapp_documents: true,
  inapp_comments: true,
  inapp_programs: true,
  inapp_system: true,
  notification_digest_frequency: 'off',
  email_notification_digest: false,
  profile_public: false,
  share_analytics: true,
})

const form = ref(defaultForm())

const NOTIFICATION_FIELD_KEYS = [
  'email_applications',
  'email_documents',
  'email_comments',
  'email_programs',
  'email_system',
  'inapp_applications',
  'inapp_documents',
  'inapp_comments',
  'inapp_programs',
  'inapp_system',
]

const notificationFields = computed(() =>
  NOTIFICATION_FIELD_KEYS.map((key) => ({
    key,
    label: t(`settings.notify.${key}`),
  })),
)

function applySettings(data) {
  const next = defaultForm()
  for (const key of Object.keys(next)) {
    if (data && Object.prototype.hasOwnProperty.call(data, key) && data[key] !== undefined) {
      next[key] = data[key]
    }
  }
  form.value = next
}

async function fetchSettings() {
  try {
    const { data } = await api.get('/api/accounts/user-settings/')
    applySettings(data)
    applyUiPreferences(form.value)
  } catch (err) {
    console.error('Failed to fetch settings:', err)
    errorToast(t('settings.toastLoadError'))
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  saveError.value = ''
  saving.value = true
  try {
    const { data } = await api.patch('/api/accounts/user-settings/', { ...form.value })
    applySettings(data && typeof data === 'object' ? { ...form.value, ...data } : form.value)
    applyUiPreferences(form.value)
    success(t('settings.toastSaved'))
  } catch (err) {
    const msg =
      err.response?.data?.detail ||
      err.response?.data?.theme?.[0] ||
      err.response?.data?.font_size?.[0] ||
      t('settings.saveFailedGeneric')
    saveError.value = typeof msg === 'string' ? msg : JSON.stringify(msg)
    errorToast(t('settings.toastSaveError'))
  } finally {
    saving.value = false
  }
}

async function handleChangePassword() {
  passwordError.value = ''
  if (passwordForm.value.new_password !== passwordForm.value.new_password2) {
    passwordError.value = t('settings.passwordMismatch')
    errorToast(passwordError.value)
    return
  }
  changingPassword.value = true
  try {
    await api.post('/api/accounts/change-password/', {
      old_password: passwordForm.value.old_password,
      new_password: passwordForm.value.new_password,
      new_password2: passwordForm.value.new_password2,
    })
    passwordForm.value = { old_password: '', new_password: '', new_password2: '' }
    success(t('settings.passwordChanged'))
  } catch (err) {
    const data = err.response?.data
    const msg =
      data?.detail ||
      data?.old_password?.[0] ||
      data?.new_password?.[0] ||
      t('settings.passwordChangeError')
    passwordError.value = typeof msg === 'string' ? msg : JSON.stringify(msg)
    errorToast(t('settings.passwordChangeError'))
  } finally {
    changingPassword.value = false
  }
}

async function fetchGoogleCalendar() {
  googleCalLoading.value = true
  try {
    const { data } = await api.get('/api/calendar/events/google-status/')
    googleCal.value = { ...googleCal.value, ...data }
  } catch {
    googleCal.value.configured = false
    googleCal.value.connected = false
  } finally {
    googleCalLoading.value = false
  }
}

async function connectGoogleCalendar() {
  googleCalBusy.value = true
  try {
    const { data } = await api.get('/api/calendar/events/google-authorize/')
    if (data.authorization_url) {
      window.location.href = data.authorization_url
      return
    }
    errorToast(t('settings.googleCalendarError'))
  } catch (err) {
    errorToast(err.response?.data?.detail || t('settings.googleCalendarError'))
  } finally {
    googleCalBusy.value = false
  }
}

async function syncGoogleCalendar() {
  googleCalBusy.value = true
  try {
    const { data } = await api.post('/api/calendar/events/google-sync/')
    googleCal.value = { ...googleCal.value, ...data }
    success(t('settings.googleCalendarSyncSuccess'))
  } catch (err) {
    errorToast(err.response?.data?.detail || t('settings.googleCalendarError'))
  } finally {
    googleCalBusy.value = false
  }
}

async function disconnectGoogleCalendar() {
  googleCalBusy.value = true
  try {
    const { data } = await api.post('/api/calendar/events/google-disconnect/')
    googleCal.value = { ...googleCal.value, ...data }
    success(t('settings.googleCalendarDisconnectedToast'))
  } catch {
    errorToast(t('settings.googleCalendarError'))
  } finally {
    googleCalBusy.value = false
  }
}

onMounted(async () => {
  await fetchSettings()
  await fetchGoogleCalendar()
  const flag = route?.query?.google_calendar
  if (flag === 'connected') success(t('settings.googleCalendarConnectedToast'))
  if (flag === 'error') errorToast(t('settings.googleCalendarError'))
})
</script>

<style scoped>
.settings-page { min-height: 100vh; background-color: var(--seim-app-bg); }
.card { border: none; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05); }
</style>
