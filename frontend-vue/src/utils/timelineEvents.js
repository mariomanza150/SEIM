import { formatApplicationStatus } from '@/utils/formatters'

const STATUS_SLUGS = [
  'under_review',
  'nominated',
  'waitlist',
  'submitted',
  'approved',
  'rejected',
  'completed',
  'cancelled',
  'withdrawn',
  'draft',
]

const GENERIC_STATUS_CODES = new Set(['change', 'changed'])

export const TIMELINE_CREATED_EVENT_TYPES = new Set(['application_created', 'created'])

export function timelineHasCreatedEvent(events) {
  return (events || []).some((event) => TIMELINE_CREATED_EVENT_TYPES.has(event?.event_type))
}

function statusFromType(eventType) {
  const type = String(eventType || '')
  if (!type.startsWith('status_')) return ''
  const code = type.slice(7)
  if (!code || GENERIC_STATUS_CODES.has(code)) return ''
  return code
}

function statusFromDescription(description) {
  const text = String(description || '')
  return STATUS_SLUGS.find((slug) => new RegExp(`\\b${slug}\\b`).test(text)) || ''
}

export function timelineStatusSlug(event) {
  return statusFromType(event?.event_type) || statusFromDescription(event?.description)
}

function statusLabel(slug, t, te) {
  return formatApplicationStatus({ status: slug, t, te })
}

export function formatTimelineEventHeading(event, { t, te }) {
  const type = event?.event_type || ''
  if (type === 'application_created' || type === 'created') {
    return t('applicationDetailPage.timelineCreated')
  }
  if (type === 'submitted') return t('applicationDetailPage.timeline.applicationSubmitted')
  if (type === 'form_submitted') return t('applicationDetailPage.timeline.programFormActivity')
  if (type === 'withdrawn' || type === 'waitlisted') {
    return type === 'withdrawn'
      ? t('applicationDetailPage.timeline.applicationWithdrawn')
      : t('applicationDetailPage.timeline.waitlisted')
  }
  if (type === 'comment' || type === 'comment_added') {
    return t('applicationDetailPage.timeline.commentRecorded')
  }
  if (type === 'subject_grades_proposed') return t('applicationDetailPage.timeline.subjectGradesProposed')
  if (type === 'subject_grades_confirmed') return t('applicationDetailPage.timeline.subjectGradesConfirmed')
  if (type === 'subject_grades_rejected') return t('applicationDetailPage.timeline.subjectGradesRejected')
  if (type.startsWith('status_') || type === 'status_change') {
    const slug = timelineStatusSlug(event)
    if (slug) {
      return t('applicationDetailPage.timeline.statusChanged', {
        status: statusLabel(slug, t, te),
      })
    }
    return t('applicationDetailPage.timeline.statusUpdated')
  }
  return (
    String(type).replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
    || t('applicationDetailPage.status.unknown')
  )
}

export function formatTimelineEventDescription(event, { t, te }) {
  const desc = typeof event?.description === 'string' ? event.description.trim() : ''
  if (!desc) return ''
  const slug = timelineStatusSlug(event)
  const narrated = /status changed|set status to|changed to\s/i.test(desc)
  if (slug && narrated) {
    return t('applicationDetailPage.timeline.statusChangedTo', {
      status: statusLabel(slug, t, te),
    })
  }
  return desc
}
