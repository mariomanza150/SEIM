/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import i18n, { setAppLocale } from '@/i18n'
import { formatNotificationCopy } from './notificationCopy'

describe('formatNotificationCopy (MQ-033)', () => {
  beforeEach(() => {
    setAppLocale('en')
  })

  afterEach(() => {
    setAppLocale('en')
  })

  function copy(n, locale = 'en') {
    setAppLocale(locale)
    return formatNotificationCopy(n, { t: i18n.global.t, te: i18n.global.te })
  }

  it('localizes status-update messages instead of raw slugs', () => {
    const en = copy({
      title: 'Application Status Update',
      message: 'Your application for Fulbright Program - Harvard University, USA status has changed to under_review.',
      action_text: 'View Application',
    })
    expect(en.title).toBe('Application Status Update')
    expect(en.message).toContain('Under review')
    expect(en.message).not.toContain('under_review')
    expect(en.actionText).toBe('View application')

    const es = copy(
      {
        title: 'Application Status Update',
        message: 'Your application for Fulbright Program - Harvard University, USA status has changed to under_review.',
        action_text: 'View Application',
      },
      'es',
    )
    expect(es.title).toBe('Actualización de estado de la solicitud')
    expect(es.message).toContain('En revisión')
    expect(es.message).not.toContain('under_review')
    expect(es.actionText).toBe('Ver solicitud')
  })

  it('localizes seed “application is {slug}” titles', () => {
    const es = copy(
      {
        title: 'Movilidad Internacional application is draft',
        message: 'Your application for Movilidad Internacional is currently marked as draft.',
        action_text: 'View application',
      },
      'es',
    )
    expect(es.title).toContain('Borrador')
    expect(es.title).not.toMatch(/\bdraft\b/)
    expect(es.message).toContain('Borrador')
  })

  it('localizes partner-portal seed copy', () => {
    const es = copy(
      {
        title: 'Partner portal ready',
        message: 'Your linked exchange agreement is available in the partner portal.',
        action_text: 'Open partner portal',
      },
      'es',
    )
    expect(es.title).toBe('Portal de socios listo')
    expect(es.message).toContain('convenio')
    expect(es.actionText).toBe('Abrir portal de socios')
  })

  it('localizes document-type prefixes on resubmit messages', () => {
    const es = copy(
      {
        title: 'Document resubmission requested',
        message: 'transcript: MQ-2026-08-18 please replace transcript with official stamp.',
        action_text: 'View document',
      },
      'es',
    )
    expect(es.title).toBe('Se solicitó reenvío del documento')
    expect(es.message.startsWith('Historial académico:')).toBe(true)
    expect(es.actionText).toBe('Ver documento')
  })

  it('maps humanized English status labels from new backend copy', () => {
    const es = copy(
      {
        title: 'Application Status Update',
        message: 'Your application for DAAD status has changed to Under Review.',
      },
      'es',
    )
    expect(es.message).toContain('En revisión')
    expect(es.message).not.toMatch(/Under Review/i)
  })
})
