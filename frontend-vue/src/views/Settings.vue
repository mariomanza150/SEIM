<template>
  <div class="settings-page">
    <div class="container-fluid mt-4">
      <nav aria-label="breadcrumb">
        <ol class="breadcrumb">
          <li class="breadcrumb-item">
            <router-link :to="{ name: 'Dashboard' }">Dashboard</router-link>
          </li>
          <li class="breadcrumb-item active">Settings</li>
        </ol>
      </nav>

      <div class="row mb-4">
        <div class="col-md-8">
          <h2><i class="bi bi-gear me-2"></i>Settings</h2>
          <p class="text-muted">Manage your appearance, notification, and privacy preferences.</p>
        </div>
      </div>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
        <p class="mt-3 text-muted">Loading settings...</p>
      </div>

      <div v-else class="row">
        <div class="col-lg-8">
          <div class="card">
            <div class="card-body">
              <form @submit.prevent="handleSubmit">
                <h6 class="text-muted mb-3">Appearance</h6>
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
                      <option value="en">English</option>
                      <option value="es">Español</option>
                    </select>
                    <div class="form-text">{{ t('settings.uiLanguageHelp') }}</div>
                  </div>
                </div>
                <div class="row mb-3">
                  <div class="col-md-6">
                    <label class="form-label">Theme</label>
                    <select v-model="form.theme" class="form-select" data-testid="settings-theme">
                      <option value="light">Light</option>
                      <option value="dark">Dark</option>
                      <option value="auto">Auto</option>
                    </select>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label">Font size</label>
                    <select v-model="form.font_size" class="form-select" data-testid="settings-font-size">
                      <option value="normal">Normal</option>
                      <option value="large">Large</option>
                      <option value="x-large">Extra large</option>
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
                        Enable high contrast mode
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
                        Reduce motion and animations
                      </label>
                    </div>
                  </div>
                </div>

                <hr class="my-4" />
                <h6 class="text-muted mb-3">Notifications</h6>
                <div class="row">
                  <div class="col-md-6">
                    <div
                      v-for="field in notificationFields.slice(0, 4)"
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
                      v-for="field in notificationFields.slice(4)"
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
                    <label class="form-label" for="notification_digest_frequency">Notification digest</label>
                    <select
                      id="notification_digest_frequency"
                      v-model="form.notification_digest_frequency"
                      class="form-select"
                      data-testid="settings-digest-frequency"
                    >
                      <option value="off">Off</option>
                      <option value="daily">Daily summary</option>
                      <option value="weekly">Weekly summary</option>
                    </select>
                    <div class="form-text">Unread in-app notifications summarized on a schedule.</div>
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
                        Email digest (requires system email above)
                      </label>
                    </div>
                  </div>
                </div>

                <hr class="my-4" />
                <h6 class="text-muted mb-3">Privacy</h6>
                <div class="form-check mb-3">
                  <input
                    id="profile_public"
                    v-model="form.profile_public"
                    class="form-check-input"
                    type="checkbox"
                  >
                  <label class="form-check-label" for="profile_public">
                    Make my profile visible to other users
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
                    Share anonymous usage analytics
                  </label>
                </div>

                <div v-if="saveError" class="alert alert-danger">{{ saveError }}</div>
                <div class="d-flex justify-content-between mt-4">
                  <router-link :to="{ name: 'Dashboard' }" class="btn btn-outline-secondary">Cancel</router-link>
                  <button
                    type="submit"
                    class="btn btn-primary"
                    :disabled="saving"
                    data-testid="save-settings-btn"
                  >
                    <span v-if="saving"><span class="spinner-border spinner-border-sm me-2"></span>Saving...</span>
                    <span v-else><i class="bi bi-check-circle me-2"></i>Save settings</span>
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>

        <div class="col-lg-4">
          <div class="card mb-4">
            <div class="card-header"><h6 class="mb-0"><i class="bi bi-person me-2"></i>Profile</h6></div>
            <div class="card-body small">
              <p class="mb-3">Need to update your account details or eligibility data instead?</p>
              <router-link :to="{ name: 'Profile' }" class="btn btn-outline-primary btn-sm">
                Go to Profile
              </router-link>
            </div>
          </div>
          <div class="card">
            <div class="card-header"><h6 class="mb-0"><i class="bi bi-shield-check me-2"></i>Note</h6></div>
            <div class="card-body small">
              These settings are saved to your account and apply across the SEIM portal.
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useToast } from '@/composables/useToast'
import api from '@/services/api'
import { applyUiPreferences } from '@/services/uiPreferences'
import { setAppLocale } from '@/i18n'

const { t, locale } = useI18n()

function onLocaleChange() {
  setAppLocale(locale.value)
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
  email_programs: false,
  email_system: true,
  inapp_applications: true,
  inapp_documents: true,
  inapp_comments: true,
  notification_digest_frequency: 'off',
  email_notification_digest: false,
  profile_public: false,
  share_analytics: true,
})

const form = ref(defaultForm())

const notificationFields = [
  { key: 'email_applications', label: 'Email me about application updates' },
  { key: 'email_documents', label: 'Email me about document updates' },
  { key: 'email_programs', label: 'Email me about new programs' },
  { key: 'email_system', label: 'Email me about system messages' },
  { key: 'inapp_applications', label: 'Show in-app application notifications' },
  { key: 'inapp_documents', label: 'Show in-app document notifications' },
  { key: 'inapp_comments', label: 'Show in-app comment notifications' },
]

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
    errorToast('Failed to load settings')
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
    success('Settings saved.')
  } catch (err) {
    const msg =
      err.response?.data?.detail ||
      err.response?.data?.theme?.[0] ||
      err.response?.data?.font_size?.[0] ||
      'Failed to save settings.'
    saveError.value = typeof msg === 'string' ? msg : JSON.stringify(msg)
    errorToast('Could not save settings')
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
