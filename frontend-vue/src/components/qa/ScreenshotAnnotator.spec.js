/**
 * @vitest-environment jsdom
 */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import i18n, { setAppLocale } from '@/i18n'
import ScreenshotAnnotator from './ScreenshotAnnotator.vue'

describe('ScreenshotAnnotator', () => {
  let ctx
  beforeEach(() => {
    setAppLocale('en')
    ctx = { clearRect: vi.fn(), drawImage: vi.fn(), fillRect: vi.fn(), strokeRect: vi.fn() }
    vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue(ctx)
    vi.spyOn(HTMLCanvasElement.prototype, 'toBlob').mockImplementation((cb) => cb(new Blob(['x'], { type: 'image/png' })))
    URL.createObjectURL = vi.fn(() => 'blob:x')
    URL.revokeObjectURL = vi.fn()
  })
  afterEach(() => vi.restoreAllMocks())

  const file = new File(['abc'], 'shot.png', { type: 'image/png' })

  function fire(el, type, x = 0, y = 0) {
    el.dispatchEvent(new MouseEvent(type, { clientX: x, clientY: y, bubbles: true }))
  }

  function drag(canvas, x1, y1, x2, y2) {
    const el = canvas.element
    fire(el, 'pointerdown', x1, y1)
    fire(el, 'pointermove', x2, y2)
    fire(el, 'pointerup')
  }

  it('returns the original file when nothing is drawn', () => {
    const w = mount(ScreenshotAnnotator, { props: { file }, global: { plugins: [i18n] } })
    w.find('[data-testid="qa-annotate-apply"]').trigger('click')
    expect(w.emitted('apply')[0][0]).toBe(file)
  })

  it('draws highlight and redact boxes, undo, and exports a png', async () => {
    const w = mount(ScreenshotAnnotator, { props: { file }, global: { plugins: [i18n] } })
    const canvas = w.find('[data-testid="qa-annotate-canvas"]')
    drag(canvas, 0, 0, 50, 40)
    await w.find('[data-testid="qa-annotate-redact"]').trigger('click')
    drag(canvas, 10, 10, 60, 60)
    drag(canvas, 5, 5, 6, 6) // too small, ignored
    expect(w.vm.shapes.length).toBe(2)
    await w.find('[data-testid="qa-annotate-undo"]').trigger('click')
    expect(w.vm.shapes.length).toBe(1)
    w.find('[data-testid="qa-annotate-apply"]').trigger('click')
    const out = w.emitted('apply')[0][0]
    expect(out).toBeInstanceOf(File)
    expect(out.name).toBe('shot-annotated.png')
  })

  it('escape cancels', () => {
    const w = mount(ScreenshotAnnotator, { props: { file }, global: { plugins: [i18n] }, attachTo: document.body })
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))
    expect(w.emitted('cancel')).toBeTruthy()
    w.unmount()
  })
})
