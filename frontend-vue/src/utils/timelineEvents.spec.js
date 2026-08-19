import { describe, it, expect } from 'vitest'
import {
  formatTimelineEventDescription,
  formatTimelineEventHeading,
  timelineHasCreatedEvent,
  timelineStatusSlug,
} from './timelineEvents'
import i18n from '@/i18n'

const t = i18n.global.t
const te = i18n.global.te

describe('timelineEvents', () => {
  it('reads nominated from a generic status_change description', () => {
    expect(
      timelineStatusSlug({
        event_type: 'status_change',
        description: 'Application status changed to nominated',
      }),
    ).toBe('nominated')
  })

  it('does not treat status_change as a status named Change', () => {
    expect(
      formatTimelineEventHeading(
        { event_type: 'status_change', description: 'Application status changed to under_review' },
        { t, te },
      ),
    ).toBe(t('applicationDetailPage.timeline.statusChanged', { status: t('applicationDetailPage.status.under_review') }))
  })

  it('rewrites stored slug descriptions', () => {
    expect(
      formatTimelineEventDescription(
        { event_type: 'status_nominated', description: 'Nomination matching set status to nominated.' },
        { t, te },
      ),
    ).toBe(
      t('applicationDetailPage.timeline.statusChangedTo', {
        status: t('applicationDetailPage.status.nominated'),
      }),
    )
    expect(
      formatTimelineEventDescription(
        { event_type: 'status_change', description: 'Application status changed to under_review' },
        { t, te },
      ),
    ).not.toMatch(/under_review/)
  })

  it('detects seeded application_created events', () => {
    expect(timelineHasCreatedEvent([])).toBe(false)
    expect(
      timelineHasCreatedEvent([{ event_type: 'status_change' }, { event_type: 'application_created' }]),
    ).toBe(true)
    expect(timelineHasCreatedEvent([{ event_type: 'created' }])).toBe(true)
  })
})
