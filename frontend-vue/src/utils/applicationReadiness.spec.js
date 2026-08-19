import { describe, it, expect } from 'vitest'
import { readinessLevelBadgeClass, formatReadinessHeadline } from './applicationReadiness'

const messages = {
  'applicationDetailPage.readinessHeadline.nominated': 'Nominated for a seat.',
  'applicationDetailPage.readinessHeadline.draft.eligibilityUnmet': 'Eligibility requirements not met',
  'applicationDetailPage.readinessHeadline.draft.missingDocsOne': '{n} required document missing',
  'applicationDetailPage.readinessHeadline.draft.missingDocsMany': '{n} required documents missing',
  'applicationDetailPage.readinessHeadline.draft.hostIncomplete': 'Host destination incomplete',
  'applicationDetailPage.readinessHeadline.draft.closedOn': 'Applications closed on {date}.',
  'applicationDetailPage.readinessHeadline.draft.windowClosed': 'Application window is closed for this program.',
  'applicationDetailPage.readinessHeadline.draft.ready': 'Requirements look complete — submit when ready.',
}

const t = (key, params) => {
  let out = messages[key] || key
  if (params?.n != null) out = out.replace('{n}', String(params.n))
  if (params?.date) out = out.replace('{date}', params.date)
  return out
}
const te = (key) => key in messages

describe('readinessLevelBadgeClass', () => {
  it('maps known levels', () => {
    expect(readinessLevelBadgeClass('ready')).toContain('success')
    expect(readinessLevelBadgeClass('blocked')).toContain('danger')
  })
})

describe('formatReadinessHeadline', () => {
  it('localizes nominated instead of the API slug fallback', () => {
    expect(
      formatReadinessHeadline({
        status: 'nominated',
        headline: 'Status: nominated.',
        t,
        te,
      }),
    ).toBe('Nominated for a seat.')
  })

  it('composes draft headlines from structured readiness', () => {
    expect(
      formatReadinessHeadline({
        status: 'draft',
        headline: '1 required document(s) missing; Eligibility requirements not met.',
        readiness: {
          window_open: true,
          document_counts: { missing: 1, resubmit: 0, pending_review: 0, required: 2 },
          eligibility: { complete: false },
          host_destination: { required: true, complete: true },
          form_complete: true,
        },
        t,
        te,
        locale: 'en',
      }),
    ).toBe('1 required document missing; Eligibility requirements not met.')
  })

  it('falls back to the API headline when draft structure is absent', () => {
    expect(
      formatReadinessHeadline({
        status: 'draft',
        headline: '1 required document(s) missing.',
        t,
        te,
      }),
    ).toBe('1 required document(s) missing.')
  })
})
