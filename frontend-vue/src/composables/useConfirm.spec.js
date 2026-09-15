import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import i18n, { setAppLocale } from '@/i18n'
import { useConfirm, resolveConfirm } from './useConfirm'
import ConfirmDialog from '@/components/ConfirmDialog.vue'

describe('useConfirm + ConfirmDialog', () => {
  beforeEach(() => {
    setAppLocale('en')
    if (useConfirm().confirmState.open) {
      resolveConfirm(false)
    }
  })

  it('defaults confirm/cancel labels from i18n', async () => {
    const { confirm, confirmState } = useConfirm()
    const promise = confirm({ title: 'T', message: 'M' })
    expect(confirmState.open).toBe(true)
    expect(confirmState.confirmText).toBe(i18n.global.t('common.ok'))
    expect(confirmState.cancelText).toBe(i18n.global.t('common.cancel'))
    resolveConfirm(false)
    await expect(promise).resolves.toBe(false)
  })

  it('uses Spanish defaults when locale is es', async () => {
    setAppLocale('es')
    const { confirm, confirmState } = useConfirm()
    const promise = confirm({ title: 'T', message: 'M' })
    expect(confirmState.confirmText).toBe('Aceptar')
    expect(confirmState.cancelText).toBe('Cancelar')
    resolveConfirm(false)
    await expect(promise).resolves.toBe(false)
  })

  it('traps Tab focus and restores opener on close', async () => {
    const opener = document.createElement('button')
    opener.textContent = 'Open'
    document.body.appendChild(opener)
    opener.focus()

    const wrapper = mount(ConfirmDialog, {
      global: { plugins: [i18n] },
      attachTo: document.body,
    })

    const { confirm } = useConfirm()
    const promise = confirm({ title: 'Delete?', message: 'Sure?' })
    await nextTick()
    await nextTick()

    const accept = document.querySelector('[data-testid="confirm-accept-btn"]')
    const cancel = document.querySelector('[data-testid="confirm-cancel-btn"]')
    expect(accept).toBeTruthy()
    accept.focus()
    expect(document.activeElement).toBe(accept)

    const dialog = document.querySelector('.seim-confirm-dialog')
    dialog.dispatchEvent(
      new KeyboardEvent('keydown', { key: 'Tab', bubbles: true, cancelable: true }),
    )
    expect(document.activeElement).toBe(cancel)

    resolveConfirm(false)
    await promise
    await nextTick()
    expect(document.activeElement).toBe(opener)

    wrapper.unmount()
    opener.remove()
  })
})
