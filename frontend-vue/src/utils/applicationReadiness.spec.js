import { describe, it, expect } from 'vitest'
import { readinessLevelBadgeClass, formatReadinessHeadline } from './applicationReadiness'

describe('readinessLevelBadgeClass', () => {
  it('maps known levels', () => {
    expect(readinessLevelBadgeClass('ready')).toContain('success')
    expect(readinessLevelBadgeClass('blocked')).toContain('danger')
  })
})

describe('formatReadinessHeadline', () => {
  const t = (key) => ({
    'applicationDetailPage.readinessHeadline.nominated': 'Nominated for a seat.',
  }[key] || key)
  const te = (key) => key in {
    'applicationDetailPage.readinessHeadline.nominated': true,
  }

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

  it('keeps draft API headlines', () => {
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
