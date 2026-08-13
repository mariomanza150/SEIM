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
              </tr>
              <tr v-if="!applications.length">
                <td colspan="4" class="text-muted text-center py-3">{{ t('partnerPortalPage.noApplicants') }}</td>
              </tr>
            </tbody>
          </table>
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

onMounted(load)
</script>
