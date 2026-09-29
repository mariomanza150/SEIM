<template>
  <div class="admin-features-page" data-testid="admin-features-page">
    <PageHeader :title="t('adminFeatures.title')" :subtitle="t('adminFeatures.subtitle')">
      <template #breadcrumb>
        <PageBreadcrumb
          :aria-label="t('adminCommon.breadcrumbAria')"
          :items="[
            { to: { name: 'Dashboard' }, label: t('route.names.Dashboard') },
            { label: t('route.names.AdminFeatures') },
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
      :loading="loading && !loadedOnce"
      :error="error || ''"
      :empty="false"
      skeleton="detail"
      :loading-label="t('adminCommon.loading')"
    >
      <div class="card mb-4" data-testid="admin-features-card">
        <div class="card-body">
          <div class="form-check form-switch">
            <input
              id="scholarships-enabled"
              v-model="draft.scholarships_enabled"
              class="form-check-input"
              type="checkbox"
              role="switch"
              data-testid="scholarships-enabled-switch"
              :disabled="saving"
              @change="saveDraft"
            />
            <label class="form-check-label" for="scholarships-enabled">
              {{ t('adminFeatures.scholarshipsEnabled') }}
            </label>
          </div>
          <p class="text-muted small mb-0 mt-2">{{ t('adminFeatures.scholarshipsHelp') }}</p>
        </div>
      </div>

      <div class="card" data-testid="admin-features-doc-history-card">
        <div class="card-header">{{ t('adminFeatures.documentHistoryTitle') }}</div>
        <div class="card-body">
          <p class="text-muted small">{{ t('adminFeatures.documentHistoryHelp') }}</p>
          <div class="form-check form-switch mb-3">
            <input
              id="doc-history-enabled"
              v-model="draft.document_version_history_enabled"
              class="form-check-input"
              type="checkbox"
              role="switch"
              data-testid="doc-history-enabled-switch"
              :disabled="saving"
              @change="saveDraft"
            />
            <label class="form-check-label" for="doc-history-enabled">
              {{ t('adminFeatures.documentHistoryEnabled') }}
            </label>
          </div>
          <div class="ms-1" :class="{ 'opacity-50': !draft.document_version_history_enabled }">
            <div class="form-check mb-2">
              <input
                id="doc-history-student"
                v-model="draft.document_version_history_student"
                class="form-check-input"
                type="checkbox"
                data-testid="doc-history-student-switch"
                :disabled="saving || !draft.document_version_history_enabled"
                @change="saveDraft"
              />
              <label class="form-check-label" for="doc-history-student">
                {{ t('adminFeatures.documentHistoryStudent') }}
              </label>
            </div>
            <div class="form-check mb-2">
              <input
                id="doc-history-coordinator"
                v-model="draft.document_version_history_coordinator"
                class="form-check-input"
                type="checkbox"
                data-testid="doc-history-coordinator-switch"
                :disabled="saving || !draft.document_version_history_enabled"
                @change="saveDraft"
              />
              <label class="form-check-label" for="doc-history-coordinator">
                {{ t('adminFeatures.documentHistoryCoordinator') }}
              </label>
            </div>
            <div class="form-check">
              <input
                id="doc-history-admin"
                v-model="draft.document_version_history_admin"
                class="form-check-input"
                type="checkbox"
                data-testid="doc-history-admin-switch"
                :disabled="saving || !draft.document_version_history_enabled"
                @change="saveDraft"
              />
              <label class="form-check-label" for="doc-history-admin">
                {{ t('adminFeatures.documentHistoryAdmin') }}
              </label>
            </div>
          </div>
          <p v-if="updatedAt" class="text-muted small mt-3 mb-0">
            {{ t('adminFeatures.updatedAt', { when: updatedAt }) }}
          </p>
        </div>
      </div>
    </PageStateShell>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import PageHeader from '@/components/PageHeader.vue'
import PageBreadcrumb from '@/components/PageBreadcrumb.vue'
import PageStateShell from '@/components/State/PageStateShell.vue'
import { useFeatures } from '@/composables/useFeatures'
import { useToast } from '@/composables/useToast'

const { t } = useI18n()
const { success, error: errorToast } = useToast()
const { features, loadFeatures, updateFeatures } = useFeatures()

const loading = ref(false)
const saving = ref(false)
const error = ref('')
const loadedOnce = ref(false)
const draft = reactive({
  scholarships_enabled: true,
  document_version_history_enabled: true,
  document_version_history_student: false,
  document_version_history_coordinator: true,
  document_version_history_admin: true,
})

const updatedAt = computed(() => features.value?.updated_at || '')

function syncDraftFromFeatures() {
  draft.scholarships_enabled = features.value?.scholarships_enabled !== false
  draft.document_version_history_enabled =
    features.value?.document_version_history_enabled !== false
  draft.document_version_history_student = Boolean(
    features.value?.document_version_history_student,
  )
  draft.document_version_history_coordinator =
    features.value?.document_version_history_coordinator !== false
  draft.document_version_history_admin =
    features.value?.document_version_history_admin !== false
}

async function reload() {
  loading.value = true
  error.value = ''
  try {
    await loadFeatures(true)
    syncDraftFromFeatures()
    loadedOnce.value = true
  } catch (err) {
    error.value = err?.message || t('adminFeatures.loadError')
  } finally {
    loading.value = false
  }
}

async function saveDraft() {
  saving.value = true
  try {
    await updateFeatures({
      scholarships_enabled: draft.scholarships_enabled,
      document_version_history_enabled: draft.document_version_history_enabled,
      document_version_history_student: draft.document_version_history_student,
      document_version_history_coordinator: draft.document_version_history_coordinator,
      document_version_history_admin: draft.document_version_history_admin,
    })
    success(t('adminFeatures.toastSaved'))
  } catch (err) {
    syncDraftFromFeatures()
    errorToast(t('adminFeatures.saveError'))
  } finally {
    saving.value = false
  }
}

onMounted(reload)
</script>
