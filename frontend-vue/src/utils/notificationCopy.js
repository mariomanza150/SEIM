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

const TITLE_KEYS = {
  'Application Status Update': 'notifications.copy.statusUpdateTitle',
  'Application Submitted': 'notifications.copy.submittedTitle',
  'Application received (waitlist)': 'notifications.copy.waitlistTitle',
  'Document resubmission requested': 'notifications.copy.resubmitTitle',
  'Document not accepted': 'notifications.copy.documentRejectedTitle',
  'Document resubmitted': 'notifications.copy.documentResubmittedTitle',
  'Feedback on your document': 'notifications.copy.documentFeedbackTitle',
  'Partner portal ready': 'notifications.copy.partnerReadyTitle',
  'Coordinator inbox ready': 'notifications.copy.coordinatorInboxTitle',
  'Demo analytics dataset prepared': 'notifications.copy.demoAnalyticsTitle',
  'Scholarship nomination': 'notifications.copy.scholarshipNominationTitle',
  'Scholarship awarded': 'notifications.copy.scholarshipAwardedTitle',
  'Scholarship declined': 'notifications.copy.scholarshipDeclinedTitle',
  'Scholarship disbursement started': 'notifications.copy.scholarshipDisbursingTitle',
  'Scholarship disbursed': 'notifications.copy.scholarshipDisbursedTitle',
  'Scholarship nomination withdrawn': 'notifications.copy.scholarshipWithdrawnTitle',
  'Scholarship update': 'notifications.copy.scholarshipUpdateTitle',
}

const MESSAGE_KEYS = {
  'Your linked exchange agreement is available in the partner portal.':
    'notifications.copy.partnerReadyMessage',
  'Submitted and under-review applications are available for review.':
    'notifications.copy.coordinatorInboxMessage',
  'The system now has seeded applications, documents, and notifications.':
    'notifications.copy.demoAnalyticsMessage',
}

const ACTION_KEYS = {
  'view application': 'notifications.copy.viewApplication',
  'open partner portal': 'notifications.copy.openPartnerPortal',
  'view document': 'notifications.copy.viewDocument',
  'review document': 'notifications.copy.reviewDocument',
  'review applications': 'notifications.copy.reviewApplications',
  'open dashboard': 'notifications.copy.openDashboard',
}

function toStatusSlug(value) {
  return String(value || '')
    .trim()
    .toLowerCase()
    .replace(/[\s-]+/g, '_')
}

function statusLabel(value, t, te) {
  return formatApplicationStatus({ status: toStatusSlug(value), t, te })
}

function replaceStatusSlugs(text, t, te) {
  let out = String(text || '')
  for (const slug of STATUS_SLUGS) {
    if (!slug.includes('_')) continue
    out = out.replace(new RegExp(`\\b${slug}\\b`, 'gi'), statusLabel(slug, t, te))
  }
  return out
}

function formatDocumentTypePrefix(text, t, te) {
  return String(text || '').replace(
    /^(Regarding\s+)?([a-z0-9]+(?:[_-][a-z0-9]+)*)(\s*:)/i,
    (full, regarding, slug, colon) => {
      const key = `documentTypes.${slug.toLowerCase()}`
      if (typeof te === 'function' && te(key)) {
        const label = t(key)
        if (regarding) return `${t('notifications.copy.regarding')} ${label}${colon}`
        return `${label}${colon}`
      }
      return full
    },
  )
}

export function formatNotificationTitle(title, { t, te } = {}) {
  const raw = String(title || '').trim()
  if (!raw) return t?.('notifications.defaultTitle') || ''
  const mapped = TITLE_KEYS[raw]
  if (mapped && t) return t(mapped)
  const isStatus = raw.match(/^(.+) application is (.+)$/i)
  if (isStatus && t) {
    return t('notifications.copy.applicationIsStatusTitle', {
      program: isStatus[1],
      status: statusLabel(isStatus[2], t, te),
    })
  }
  return replaceStatusSlugs(raw, t, te)
}

export function formatNotificationMessage(message, { t, te } = {}) {
  const raw = String(message || '').trim()
  if (!raw) return ''
  const mapped = MESSAGE_KEYS[raw]
  if (mapped && t) return t(mapped)
  const changed = raw.match(/^Your application for (.+) status has changed to (.+?)\.?$/i)
  if (changed && t) {
    return t('notifications.copy.statusChangedMessage', {
      program: changed[1],
      status: statusLabel(changed[2], t, te),
    })
  }
  const submitted = raw.match(/^Your application for (.+) has been submitted successfully\.?$/i)
  if (submitted && t) {
    return t('notifications.copy.submittedMessage', { program: submitted[1] })
  }
  const marked = raw.match(/^Your application for (.+) is currently marked as (.+?)\.?$/i)
  if (marked && t) {
    return t('notifications.copy.markedAsMessage', {
      program: marked[1],
      status: statusLabel(marked[2], t, te),
    })
  }
  const waitlist = raw.match(
    /^Your application for (.+) was received\. The program is at capacity; you are on the waitlist and will be notified if a seat opens\.?$/i,
  )
  if (waitlist && t) {
    return t('notifications.copy.waitlistMessage', { program: waitlist[1] })
  }
  return replaceStatusSlugs(formatDocumentTypePrefix(raw, t, te), t, te)
}

export function formatNotificationAction(actionText, { t, te } = {}) {
  const raw = String(actionText || '').trim()
  if (!raw) return ''
  const key = ACTION_KEYS[raw.toLowerCase()]
  if (key && t) return t(key)
  return replaceStatusSlugs(raw, t, te)
}

export function formatNotificationCopy(notification, i18n) {
  return {
    title: formatNotificationTitle(notification?.title, i18n),
    message: formatNotificationMessage(notification?.message, i18n),
    actionText: formatNotificationAction(notification?.action_text, i18n),
  }
}
