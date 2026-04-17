<template>
  <div class="admin-workflow-editor-page">
    <PageHeader :title="headerTitle" :subtitle="headerSubtitle">
      <template #breadcrumb>
        <nav aria-label="Breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item">
              <router-link :to="{ name: 'Dashboard' }">{{ t('route.names.Dashboard') }}</router-link>
            </li>
            <li class="breadcrumb-item">
              <router-link :to="{ name: 'AdminWorkflows' }">{{ t('route.names.AdminWorkflows') }}</router-link>
            </li>
            <li class="breadcrumb-item active">{{ headerTitle }}</li>
          </ol>
        </nav>
      </template>

      <template #actions>
        <button type="button" class="btn btn-outline-secondary" :disabled="busy" @click="reload">
          <i class="bi bi-arrow-clockwise me-1" aria-hidden="true"></i>{{ t('adminCommon.refresh') }}
        </button>
        <button type="button" class="btn btn-outline-secondary" :disabled="busy || !currentVersionId" @click="validateBpmn">
          <i class="bi bi-check2-circle me-1" aria-hidden="true"></i>{{ t('adminWorkflowEditor.validate') }}
        </button>
        <button type="button" class="btn btn-primary" :disabled="busy" @click="saveDraft">
          <i class="bi bi-save2 me-1" aria-hidden="true"></i>{{ t('adminCommon.save') }}
        </button>
        <button type="button" class="btn btn-success" :disabled="busy || !currentVersionId" @click="publish">
          <i class="bi bi-cloud-upload me-1" aria-hidden="true"></i>{{ t('adminWorkflowEditor.publish') }}
        </button>
      </template>
    </PageHeader>

    <div v-if="error" class="alert alert-danger" role="alert">
      <i class="bi bi-exclamation-triangle me-2" aria-hidden="true"></i>
      {{ error }}
    </div>

    <div class="row g-3">
      <div class="col-lg-9">
        <div class="card">
          <div class="card-body p-0">
            <div ref="canvasEl" class="bpmn-canvas" data-testid="bpmn-canvas" />
          </div>
        </div>
      </div>
      <div class="col-lg-3">
        <div class="card">
          <div class="card-header">
            <div class="d-flex justify-content-between align-items-center gap-2">
              <div class="fw-medium">{{ t('adminWorkflowEditor.properties') }}</div>
              <span v-if="currentVersionLabel" class="badge bg-secondary">{{ currentVersionLabel }}</span>
            </div>
          </div>
          <div class="card-body p-0">
            <div ref="propertiesEl" class="bpmn-properties" data-testid="bpmn-properties" />
          </div>
        </div>

        <div class="card mt-3">
          <div class="card-header fw-medium">{{ t('adminWorkflowEditor.versions') }}</div>
          <div class="list-group list-group-flush">
            <button
              v-for="v in versions"
              :key="v.id"
              type="button"
              class="list-group-item list-group-item-action d-flex justify-content-between align-items-center"
              :class="{ active: String(v.id) === String(currentVersionId) }"
              :disabled="busy"
              @click="loadVersion(v.id)"
            >
              <span class="text-truncate">v{{ v.version }} — {{ v.status }}</span>
              <i class="bi bi-chevron-right" aria-hidden="true" />
            </button>
          </div>
          <div class="card-footer">
            <button type="button" class="btn btn-sm btn-outline-primary w-100" :disabled="busy" @click="createNewDraftVersion">
              <i class="bi bi-plus-circle me-1" aria-hidden="true"></i>{{ t('adminWorkflowEditor.newVersion') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import api from '@/services/api'
import { useToast } from '@/composables/useToast'
import { useConfirm } from '@/composables/useConfirm'
import PageHeader from '@/components/PageHeader.vue'

import BpmnModeler from 'bpmn-js/lib/Modeler'
import { BpmnPropertiesPanelModule, BpmnPropertiesProviderModule } from 'bpmn-js-properties-panel'

import 'bpmn-js/dist/assets/diagram-js.css'
import 'bpmn-js/dist/assets/bpmn-font/css/bpmn.css'
import '@bpmn-io/properties-panel/dist/assets/properties-panel.css'

const { t } = useI18n()
const route = useRoute()
const { success, error: errorToast } = useToast()
const { confirm } = useConfirm()

const canvasEl = ref(null)
const propertiesEl = ref(null)

const workflowId = computed(() => route.params.id)

const definition = ref(null)
const versions = ref([])
const currentVersionId = ref(null)
const currentVersionLabel = ref('')
const busy = ref(false)
const error = ref(null)

let modeler = null

const headerTitle = computed(() => definition.value?.name || t('adminWorkflowEditor.loadingTitle'))
const headerSubtitle = computed(() => definition.value?.description || t('adminWorkflowEditor.subtitle'))

function defaultBpmnXml(name = 'Workflow') {
  const safe = String(name || 'Workflow').replace(/[<>&"]/g, '')
  return `<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"
  xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
  xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
  id="Definitions_1"
  targetNamespace="http://seim.local/bpmn">
  <bpmn:process id="Process_1" isExecutable="true">
    <bpmn:startEvent id="StartEvent_1" name="Start" />
  </bpmn:process>
  <bpmndi:BPMNDiagram id="BPMNDiagram_1">
    <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Process_1">
      <bpmndi:BPMNShape id="StartEvent_1_di" bpmnElement="StartEvent_1">
        <dc:Bounds x="180" y="100" width="36" height="36" />
      </bpmndi:BPMNShape>
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn:definitions>`
}

async function fetchDefinition() {
  const res = await api.get(`/api/workflows/${workflowId.value}/`)
  definition.value = res.data
}

async function fetchVersions() {
  const res = await api.get(`/api/workflows/${workflowId.value}/versions/`)
  versions.value = Array.isArray(res.data) ? res.data : []
}

async function ensureModeler() {
  if (modeler) return
  if (!canvasEl.value || !propertiesEl.value) return
  modeler = new BpmnModeler({
    container: canvasEl.value,
    propertiesPanel: { parent: propertiesEl.value },
    additionalModules: [BpmnPropertiesPanelModule, BpmnPropertiesProviderModule],
  })
}

async function importXml(xml) {
  await ensureModeler()
  if (!modeler) return
  await modeler.importXML(xml)
  const canvas = modeler.get('canvas')
  canvas.zoom('fit-viewport')
}

async function loadLatest() {
  await fetchDefinition()
  await fetchVersions()
  const drafts = versions.value.filter((v) => v.status === 'draft').sort((a, b) => b.version - a.version)
  const published = versions.value.filter((v) => v.status === 'published').sort((a, b) => b.version - a.version)
  const best = drafts[0] || published[0]
  if (best) {
    await loadVersion(best.id)
    return
  }
  await createNewDraftVersion()
}

async function loadVersion(id) {
  busy.value = true
  error.value = null
  try {
    const res = await api.get(`/api/workflow-versions/${id}/`)
    const v = res.data
    currentVersionId.value = v.id
    currentVersionLabel.value = `v${v.version} — ${v.status}`
    await importXml(v.bpmn_xml || defaultBpmnXml(definition.value?.name))
  } catch (err) {
    console.error('Failed to load workflow version:', err)
    error.value = t('adminWorkflowEditor.loadError')
  } finally {
    busy.value = false
  }
}

async function createNewDraftVersion() {
  busy.value = true
  error.value = null
  try {
    const res = await api.post(`/api/workflows/${workflowId.value}/versions/`, {
      bpmn_xml: defaultBpmnXml(definition.value?.name),
    })
    await fetchVersions()
    await loadVersion(res.data.id)
    success(t('adminWorkflowEditor.toastVersionCreated'))
  } catch (err) {
    console.error('Failed to create workflow version:', err)
    error.value = t('adminWorkflowEditor.createVersionError')
    errorToast(t('adminWorkflowEditor.createVersionToastError'))
  } finally {
    busy.value = false
  }
}

async function saveDraft() {
  busy.value = true
  error.value = null
  try {
    await ensureModeler()
    const { xml } = await modeler.saveXML({ format: true })
    if (currentVersionId.value) {
      await api.patch(`/api/workflow-versions/${currentVersionId.value}/`, { bpmn_xml: xml })
      success(t('adminWorkflowEditor.toastSaved'))
      await fetchVersions()
      const row = versions.value.find((v) => String(v.id) === String(currentVersionId.value))
      if (row) currentVersionLabel.value = `v${row.version} — ${row.status}`
    } else {
      const res = await api.post(`/api/workflows/${workflowId.value}/versions/`, { bpmn_xml: xml })
      await fetchVersions()
      currentVersionId.value = res.data.id
      currentVersionLabel.value = `v${res.data.version} — ${res.data.status}`
      success(t('adminWorkflowEditor.toastVersionCreated'))
    }
  } catch (err) {
    console.error('Failed to save workflow draft:', err)
    error.value = t('adminWorkflowEditor.saveError')
    errorToast(t('adminWorkflowEditor.saveToastError'))
  } finally {
    busy.value = false
  }
}

async function validateBpmn() {
  if (!currentVersionId.value) return
  busy.value = true
  error.value = null
  try {
    await saveDraft()
    await api.post(`/api/workflow-versions/${currentVersionId.value}/validate/`)
    success(t('adminWorkflowEditor.toastValid'))
  } catch (err) {
    console.error('Validation failed:', err)
    const msg = err.response?.data?.error
    error.value = typeof msg === 'string' ? msg : t('adminWorkflowEditor.validateError')
    errorToast(t('adminWorkflowEditor.validateToastError'))
  } finally {
    busy.value = false
  }
}

async function publish() {
  if (!currentVersionId.value) return
  const ok = await confirm({
    title: t('adminWorkflowEditor.publish'),
    message: t('adminWorkflowEditor.publishConfirm'),
    confirmText: t('adminWorkflowEditor.publish'),
    cancelText: t('adminCommon.cancel'),
    variant: 'primary',
  })
  if (!ok) return
  busy.value = true
  error.value = null
  try {
    await saveDraft()
    await api.post(`/api/workflow-versions/${currentVersionId.value}/publish/`)
    await fetchVersions()
    const row = versions.value.find((v) => String(v.id) === String(currentVersionId.value))
    if (row) currentVersionLabel.value = `v${row.version} — ${row.status}`
    success(t('adminWorkflowEditor.toastPublished'))
  } catch (err) {
    console.error('Publish failed:', err)
    error.value = t('adminWorkflowEditor.publishError')
    errorToast(t('adminWorkflowEditor.publishToastError'))
  } finally {
    busy.value = false
  }
}

async function reload() {
  await loadLatest()
}

onMounted(async () => {
  await ensureModeler()
  await loadLatest()
})

onBeforeUnmount(() => {
  try {
    modeler?.destroy()
  } catch {
    /* ignore */
  }
  modeler = null
})
</script>

<style scoped>
.admin-workflow-editor-page {
  min-height: 70vh;
}

.bpmn-canvas {
  height: 70vh;
  width: 100%;
}

.bpmn-properties {
  min-height: 70vh;
  overflow: auto;
}
</style>

