<template>
  <div class="partner-portal-page">
    <PageHeader :title="t('partnerPortalPage.title')" :subtitle="t('partnerPortalPage.subtitle')">
      <template #breadcrumb>
        <nav :aria-label="t('partnerPortalPage.breadcrumbAria')">
          <ol class="breadcrumb">
            <li class="breadcrumb-item">
              <router-link :to="{ name: 'Dashboard' }">{{ t('route.names.Dashboard') }}</router-link>
            </li>
            <li class="breadcrumb-item active">{{ t('route.names.PartnerPortal') }}</li>
          </ol>
        </nav>
      </template>
    </PageHeader>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">{{ t('partnerPortalPage.loading') }}</span>
      </div>
    </div>
    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-else data-testid="partner-portal-page">
      <div class="card mb-4">
        <div class="card-header"><h5 class="mb-0">{{ t('partnerPortalPage.agreementsHeading') }}</h5></div>
        <div class="table-responsive">
          <table class="table mb-0">
            <thead>
              <tr>
                <th>{{ t('partnerPortalPage.colTitle') }}</th>
                <th>{{ t('partnerPortalPage.colInstitution') }}</th>
                <th>{{ t('partnerPortalPage.colStatus') }}</th>
                <th>{{ t('partnerPortalPage.colDocuments') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="ag in agreements" :key="ag.id">
                <td>{{ ag.title }}</td>
                <td>{{ ag.partner_institution_name }}</td>
                <td>{{ ag.status }}</td>
                <td>
                  <button type="button" class="btn btn-sm btn-outline-primary" @click="loadDocs(ag)">
                    {{ t('partnerPortalPage.viewDocuments') }}
                  </button>
                </td>
              </tr>
              <tr v-if="!agreements.length">
                <td colspan="4" class="text-muted text-center py-3">{{ t('partnerPortalPage.noAgreements') }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-if="docsAgreement" class="card mb-4" data-testid="partner-docs">
        <div class="card-header">
          <h5 class="mb-0">{{ t('partnerPortalPage.docsHeading', { title: docsAgreement.title }) }}</h5>
        </div>
        <ul class="list-group list-group-flush">
          <li v-for="d in docs" :key="d.id" class="list-group-item">
            {{ d.title || d.file }}
            <span class="badge bg-secondary ms-2">{{ d.category }}</span>
          </li>
          <li v-if="!docs.length" class="list-group-item text-muted">{{ t('partnerPortalPage.noDocuments') }}</li>
        </ul>
      </div>

      <div class="card">
        <div class="card-header"><h5 class="mb-0">{{ t('partnerPortalPage.applicantsHeading') }}</h5></div>
        <div class="table-responsive">
          <table class="table mb-0" data-testid="partner-applications">
            <thead>
              <tr>
                <th>{{ t('partnerPortalPage.colStudent') }}</th>
                <th>{{ t('partnerPortalPage.colProgram') }}</th>
                <th>{{ t('partnerPortalPage.colStatus') }}</th>
                <th>{{ t('partnerPortalPage.colDocs') }}</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="app in applications" :key="app.id">
                <td>{{ app.student_display_name }}</td>
                <td>{{ app.program_name }}</td>
                <td>{{ app.status_name || app.status }}</td>
                <td>
                  {{
                    app.document_checklist?.complete
                      ? t('partnerPortalPage.docsComplete')
                      : t('partnerPortalPage.docsIncomplete')
                  }}
                </td>
                <td>
                  <button
                    type="button"
                    class="btn btn-sm btn-outline-primary"
                    data-testid="partner-open-thread"
                    @click="openThread(app)"
                  >
                    {{ t('partnerPortalPage.openThread') }}
                  </button>
                </td>
              </tr>
              <tr v-if="!applications.length">
                <td colspan="5" class="text-muted text-center py-3">{{ t('partnerPortalPage.noApplicants') }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-if="threadApp" class="card mt-4" data-testid="partner-thread">
        <div class="card-header">
          <h5 class="mb-0">
            {{ t('partnerPortalPage.threadHeading', { name: threadApp.student_display_name }) }}
          </h5>
        </div>
        <div class="card-body">
          <div v-if="threadLoading" class="text-muted small">{{ t('partnerPortalPage.threadLoading') }}</div>
          <ul v-else class="list-unstyled mb-3">
            <li v-for="c in threadComments" :key="c.id" class="mb-2">
              <div class="small text-muted">{{ c.author_display_name }}</div>
              <div>{{ c.text }}</div>
            </li>
            <li v-if="!threadComments.length" class="text-muted">{{ t('partnerPortalPage.threadEmpty') }}</li>
          </ul>
          <form @submit.prevent="postThread">
            <label class="form-label" for="partner-thread-text">{{ t('partnerPortalPage.threadLabel') }}</label>
            <textarea
              id="partner-thread-text"
              v-model="threadText"
              class="form-control mb-2"
              rows="3"
              required
              data-testid="partner-thread-text"
            ></textarea>
            <button
              type="submit"
              class="btn btn-primary btn-sm"
              :disabled="threadBusy"
              data-testid="partner-thread-submit"
            >
              {{ t('partnerPortalPage.threadSubmit') }}
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import PageHeader from '@/components/PageHeader.vue'

const { t } = useI18n()
const loading = ref(true)
const error = ref('')
const agreements = ref([])
const applications = ref([])
const docs = ref([])
const docsAgreement = ref(null)
const threadApp = ref(null)
const threadComments = ref([])
const threadText = ref('')
const threadLoading = ref(false)
const threadBusy = ref(false)

function unwrap(data) {
  if (Array.isArray(data)) return data
  if (data && Array.isArray(data.results)) return data.results
  return []
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [ag, apps] = await Promise.all([
      api.get('/api/partner/agreements/'),
      api.get('/api/partner/applications/'),
    ])
    agreements.value = unwrap(ag.data)
    applications.value = unwrap(apps.data)
  } catch {
    error.value = t('partnerPortalPage.loadError')
  } finally {
    loading.value = false
  }
}

async function loadDocs(ag) {
  docsAgreement.value = ag
  try {
    const { data } = await api.get(`/api/partner/agreements/${ag.id}/documents/`)
    docs.value = Array.isArray(data) ? data : unwrap(data)
  } catch {
    docs.value = []
  }
}

async function openThread(app) {
  threadApp.value = app
  threadText.value = ''
  threadLoading.value = true
  try {
    const { data } = await api.get(`/api/partner/applications/${app.id}/comments/`)
    threadComments.value = Array.isArray(data) ? data : unwrap(data)
  } catch {
    threadComments.value = []
  } finally {
    threadLoading.value = false
  }
}

async function postThread() {
  const text = threadText.value.trim()
  if (!text || !threadApp.value) return
  threadBusy.value = true
  try {
    const { data } = await api.post(
      `/api/partner/applications/${threadApp.value.id}/comments/`,
      { text },
    )
    threadComments.value = [...threadComments.value, data]
    threadText.value = ''
  } finally {
    threadBusy.value = false
  }
}

onMounted(load)
</script>
