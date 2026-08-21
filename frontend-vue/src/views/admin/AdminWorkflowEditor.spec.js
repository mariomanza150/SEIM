/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import { createRouter, createMemoryHistory } from 'vue-router'
import en from '@/locales/en.json'
import AdminWorkflowEditor from './AdminWorkflowEditor.vue'

const { mockGet, mockPost, mockPatch, mockConfirm, mockSuccess, mockErrorToast, mockImportXML, mockSaveXML, mockDestroy, mockZoom } =
  vi.hoisted(() => ({
    mockGet: vi.fn(),
    mockPost: vi.fn(),
    mockPatch: vi.fn(),
    mockConfirm: vi.fn(),
    mockSuccess: vi.fn(),
    mockErrorToast: vi.fn(),
    mockImportXML: vi.fn().mockResolvedValue({}),
    mockSaveXML: vi.fn().mockResolvedValue({ xml: '<bpmn:definitions />' }),
    mockDestroy: vi.fn(),
    mockZoom: vi.fn(),
  }))

vi.mock('@/services/api', () => ({
  default: { get: mockGet, post: mockPost, patch: mockPatch },
}))
vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: mockSuccess, error: mockErrorToast }),
}))
vi.mock('@/composables/useConfirm', () => ({
  useConfirm: () => ({ confirm: mockConfirm }),
}))
vi.mock('bpmn-js/lib/Modeler', () => {
  class MockBpmnModeler {
    constructor() {
      this.importXML = mockImportXML
      this.saveXML = mockSaveXML
      this.destroy = mockDestroy
    }

    get() {
      return { zoom: mockZoom }
    }
  }
  return { default: MockBpmnModeler }
})
vi.mock('bpmn-js-properties-panel', () => ({
  BpmnPropertiesPanelModule: {},
  BpmnPropertiesProviderModule: {},
}))
vi.mock('bpmn-js/dist/assets/diagram-js.css', () => ({}))
vi.mock('bpmn-js/dist/assets/bpmn-font/css/bpmn.css', () => ({}))
vi.mock('@bpmn-io/properties-panel/dist/assets/properties-panel.css', () => ({}))

const draftXml = '<?xml version="1.0"?><bpmn:definitions><bpmn:process id="P1" /></bpmn:definitions>'

async function mountEditor() {
  const i18n = createI18n({ legacy: false, locale: 'en', messages: { en } })
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', name: 'Dashboard', component: { template: '<div />' } },
      { path: '/admin/workflows', name: 'AdminWorkflows', component: { template: '<div />' } },
      {
        path: '/admin/workflows/:id',
        name: 'AdminWorkflowEditor',
        component: AdminWorkflowEditor,
      },
    ],
  })
  await router.push({ name: 'AdminWorkflowEditor', params: { id: 'wf-1' } })
  const wrapper = mount(AdminWorkflowEditor, { global: { plugins: [i18n, router] } })
  await flushPromises()
  return wrapper
}

describe('AdminWorkflowEditor', () => {
  beforeEach(() => {
    mockGet.mockReset()
    mockPost.mockReset()
    mockPatch.mockReset()
    mockConfirm.mockReset()
    mockSuccess.mockReset()
    mockErrorToast.mockReset()
    mockImportXML.mockClear()
    mockSaveXML.mockClear()
    mockDestroy.mockClear()
    mockZoom.mockClear()
    mockConfirm.mockResolvedValue(true)

    mockGet.mockImplementation((url) => {
      if (url === '/api/workflows/wf-1/') {
        return Promise.resolve({
          data: { id: 'wf-1', name: 'Exchange flow', description: 'Main BPMN' },
        })
      }
      if (url === '/api/workflows/wf-1/versions/') {
        return Promise.resolve({
          data: [
            { id: 'ver-1', version: 1, status: 'draft' },
            { id: 'ver-0', version: 0, status: 'published' },
          ],
        })
      }
      if (url === '/api/workflow-versions/ver-1/') {
        return Promise.resolve({
          data: { id: 'ver-1', version: 1, status: 'draft', bpmn_xml: draftXml },
        })
      }
      return Promise.resolve({ data: {} })
    })
    mockPatch.mockResolvedValue({ data: {} })
    mockPost.mockResolvedValue({ data: { id: 'ver-2', version: 2, status: 'draft' } })
  })

  it('loads the latest draft version into the BPMN canvas', async () => {
    const wrapper = await mountEditor()
    expect(wrapper.text()).toContain('Exchange flow')
    expect(wrapper.get('[data-testid="workflow-version-status"]').text()).toContain('v1')
    expect(wrapper.get('[data-testid="workflow-version-status"]').text()).toContain('Draft')
    expect(mockImportXML).toHaveBeenCalledWith(draftXml)
    expect(wrapper.find('[data-testid="bpmn-canvas"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="bpmn-properties"]').exists()).toBe(true)
  })

  it('validates by saving the draft then posting validate', async () => {
    const wrapper = await mountEditor()
    mockPost.mockResolvedValue({ data: {} })
    await wrapper.get('[data-testid="workflow-validate"]').trigger('click')
    await flushPromises()
    expect(mockSaveXML).toHaveBeenCalled()
    expect(mockPatch).toHaveBeenCalledWith('/api/workflow-versions/ver-1/', {
      bpmn_xml: '<bpmn:definitions />',
    })
    expect(mockPost).toHaveBeenCalledWith('/api/workflow-versions/ver-1/validate/')
    expect(wrapper.get('[data-testid="workflow-validate-result"]').text()).toContain('BPMN validated')
    expect(mockSuccess).toHaveBeenCalledWith('BPMN validated')
  })

  it('publishes after confirmation', async () => {
    const wrapper = await mountEditor()
    mockPost.mockResolvedValue({ data: {} })
    const publishBtn = wrapper.findAll('button').find((b) => b.text().includes('Publish'))
    expect(publishBtn).toBeTruthy()
    await publishBtn.trigger('click')
    await flushPromises()
    expect(mockConfirm).toHaveBeenCalled()
    expect(mockPost).toHaveBeenCalledWith('/api/workflow-versions/ver-1/publish/')
    expect(mockSuccess).toHaveBeenCalledWith('Workflow published')
  })

  it('surfaces validation API errors in the result alert', async () => {
    const wrapper = await mountEditor()
    mockPost.mockRejectedValue({ response: { data: { error: 'Missing end event' } } })
    await wrapper.get('[data-testid="workflow-validate"]').trigger('click')
    await flushPromises()
    expect(wrapper.get('[data-testid="workflow-validate-result"]').text()).toContain('Missing end event')
    expect(wrapper.get('[data-testid="workflow-validate-result"]').classes()).toContain('alert-danger')
    expect(mockErrorToast).toHaveBeenCalled()
  })
})
