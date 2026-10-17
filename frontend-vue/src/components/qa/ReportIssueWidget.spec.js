/**
 * @vitest-environment jsdom
 */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import i18n, { setAppLocale } from '@/i18n'
import { useQaStore } from '@/stores/qa'
import { createIssue } from '@/qa/api'
import ReportIssueWidget from './ReportIssueWidget.vue'

vi.mock('@/services/api', () => ({ default: { get: vi.fn(), post: vi.fn() } }))
vi.mock('@/qa/api', () => ({ createIssue: vi.fn() }))
vi.mock('vue-router', () => ({
  useRoute: () => ({ name: 'Dashboard', fullPath: '/dashboard', params: {} }),
  useRouter: () => ({ replace: vi.fn() }),
}))
const toast = { success: vi.fn(), info: vi.fn(), error: vi.fn() }
vi.mock('@/composables/useToast', () => ({ useToast: () => toast }))

let mounted = []
function mountWidget() {
  const w = mount(ReportIssueWidget, { global: { plugins: [i18n] }, attachTo: document.body })
  mounted.push(w)
  return w
}

describe('ReportIssueWidget', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    setAppLocale('en')
    vi.clearAllMocks()
  })

  afterEach(() => {
    mounted.forEach((w) => w.unmount())
    mounted = []
  })

  it('renders nothing for non-testers', () => {
    const qa = useQaStore()
    qa.context = { enabled: true, is_tester: false }
    const w = mountWidget()
    expect(w.find('[data-testid="qa-report-fab"]').exists()).toBe(false)
  })

  it('opens, validates the title and submits multipart with context', async () => {
    const qa = useQaStore()
    qa.context = { enabled: true, is_tester: true, version: '1.0.0', limits: { max_attachments: 2, max_image_mb: 1, max_video_mb: 2 } }
    createIssue.mockResolvedValue({ data: { reference: 'QA-7' } })
    const w = mountWidget()
    await w.find('[data-testid="qa-report-fab"]').trigger('click')
    await flushPromises()
    expect(document.querySelector('[data-testid="qa-report-dialog"]')).not.toBeNull()

    await w.vm.submit()
    expect(createIssue).not.toHaveBeenCalled()
    expect(w.vm.errors.title).toBeTruthy()

    w.vm.form.title = 'Broken save'
    w.vm.addFiles([new File(['x'], 'a.png', { type: 'image/png' })])
    await w.vm.submit()
    await flushPromises()
    expect(createIssue).toHaveBeenCalledTimes(1)
    const fd = createIssue.mock.calls[0][0]
    expect(fd.get('title')).toBe('Broken save')
    expect(fd.get('route_name')).toBe('Dashboard')
    expect(fd.get('app_version')).toBe('1.0.0')
    expect(fd.getAll('files')).toHaveLength(1)
    expect(JSON.parse(fd.get('diagnostics'))).toHaveProperty('consoleErrors')
    expect(toast.success).toHaveBeenCalledWith(expect.stringContaining('QA-7'), 6000)
    expect(qa.widgetOpen).toBe(false)
  })

  it('enforces client-side file count and size limits', async () => {
    const qa = useQaStore()
    qa.context = { enabled: true, is_tester: true, limits: { max_attachments: 1, max_image_mb: 1, max_video_mb: 2 } }
    const w = mountWidget()
    const big = new File([new Uint8Array(2 * 1024 * 1024)], 'big.png', { type: 'image/png' })
    w.vm.addFiles([big])
    expect(w.vm.files).toHaveLength(0)
    expect(w.vm.errors.files).toContain('big.png')
    w.vm.addFiles([new File(['a'], 'a.txt', { type: 'text/plain' }), new File(['b'], 'b.txt', { type: 'text/plain' })])
    expect(w.vm.files).toHaveLength(1)
    expect(w.vm.errors.files).toContain('1')
  })

  it('shows server-side file errors', async () => {
    const qa = useQaStore()
    qa.context = { enabled: true, is_tester: true }
    createIssue.mockRejectedValue({ response: { status: 400, data: { files: ['x.svg: File type not allowed.'] } } })
    const w = mountWidget()
    w.vm.form.title = 'x'
    await w.vm.submit()
    await flushPromises()
    expect(w.vm.errors.files).toContain('not allowed')
  })

  it('toggles with Ctrl+Shift+B', async () => {
    const qa = useQaStore()
    qa.context = { enabled: true, is_tester: true }
    mountWidget()
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'B', ctrlKey: true, shiftKey: true }))
    await flushPromises()
    expect(qa.widgetOpen).toBe(true)
  })

  it('renders Spanish copy', async () => {
    setAppLocale('es')
    const qa = useQaStore()
    qa.context = { enabled: true, is_tester: true }
    const w = mountWidget()
    expect(w.text()).toContain('Reportar problema')
  })
})
