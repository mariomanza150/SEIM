<template>
  <div class="settings-page">
    <div class="container-fluid mt-4">
      <nav :aria-label="t('settings.breadcrumbAria')">
        <ol class="breadcrumb">
          <li class="breadcrumb-item">
            <router-link :to="{ name: 'Dashboard' }">{{ t('route.names.Dashboard') }}</router-link>
          </li>
          <li class="breadcrumb-item active">{{ t('route.names.Settings') }}</li>
        </ol>
      </nav>

      <div class="row mb-4">
        <div class="col-md-8">
          <h2><i class="bi bi-gear me-2"></i>{{ t('route.names.Settings') }}</h2>
          <p class="text-muted">{{ t('settings.pageSubtitle') }}</p>
        </div>
      </div>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
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
                    <label class="form-label">{{ t('settings.theme') }}</label>
                    <select v-model="form.theme" class="form-select" data-testid="settings-theme">
                      <option value="light">{{ t('settings.themeLight') }}</option>
                      <option value="dark">{{ t('settings.themeDark') }}</option>
                      <option value="auto">{{ t('settings.themeAuto') }}</option>
                    </select>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label">{{ t('settings.fontSize') }}</label>
                    <select v-model="form.font_size" class="form-select" data-testid="settings-font-size">
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
                  <router-link :to="{ name: 'Dashboard' }" class="btn btn-outline-secondary">{{ t('applicationFormPage.cancel') }}</router-link>
                  <button
                    type="submit"
                    class="btn btn-primary"
                    :disabled="saving"
                    data-testid="save-settings-btn"
                  >
                    <span v-if="saving"><span class="spinner-border spinner-border-sm me-2"></span>{{ t('settings.saving') }}</span>
                    <span v-else><i class="bi bi-check-circle me-2"></i>{{ t('settings.saveButton') }}</span>
                  </button>
                </div>
              </form>
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
          <div class="card">
            <div class="card-header"><h6 class="mb-0"><i class="bi bi-shield-check me-2"></i>{{ t('settings.sidebarNoteTitle') }}</h6></div>
            <div class="card-body small">
              {{ t('settings.sidebarNoteBody') }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useToast } from '@/composables/useToast'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'
import { applyUiPreferences } from '@/services/uiPreferences'
import { setAppLocale } from '@/i18n'
import router from '@/router'
import { resolveDocumentTitle } from '@/utils/documentTitle'

const authStore = useAuthStore()
const { t, locale } = useI18n()

function onLocaleChange() {
  setAppLocale(locale.value)
  document.title = resolveDocumentTitle(router.currentRoute.value)
}

const { success, error: errorToast } = useToast()
const loading = ref(true)
const saving = ref(false)
const saveError = ref('')

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

async function fetchSettings() {
  try {
    const { data } = await api.get('/api/accounts/user-settings/')
    form.value = {
      ...defaultForm(),
      ...data,
    }
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
    await api.patch('/api/accounts/user-settings/', { ...form.value })
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

onMounted(fetchSettings)
</script>

<style scoped>
.settings-page { min-height: 100vh; background-color: #f8f9fa; }
.card { border: none; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05); }
</style>
