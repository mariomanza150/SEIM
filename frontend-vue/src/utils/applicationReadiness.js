import { formatDate } from '@/utils/formatters'

/** Bootstrap badge class for API `readiness.level`. */
export function readinessLevelBadgeClass(level) {
  const m = {
    done: 'bg-primary',
    ready: 'bg-success',
    ok: 'bg-info text-dark',
    attention: 'bg-warning text-dark',
    blocked: 'bg-danger',
  }
  return m[level] || 'bg-secondary'
}

/** Progress bar color from 0–100 score. */
export function readinessScoreBarClass(score) {
  if (score >= 90) return 'bg-success'
  if (score >= 60) return 'bg-info'
  if (score >= 35) return 'bg-warning'
  return 'bg-danger'
}

function countPhrase(t, oneKey, manyKey, n) {
  return t(n === 1 ? oneKey : manyKey, { n })
}

function formatWindowOn(windowOn, locale) {
  if (!windowOn) return ''
  const dateString = /^\d{4}-\d{2}-\d{2}$/.test(windowOn) ? `${windowOn}T12:00:00` : windowOn
  return formatDate({ dateString, locale, fallback: windowOn })
}

/** Localized draft headline from structured readiness fields. */
export function formatDraftReadinessHeadline({ readiness, t, locale } = {}) {
  if (!readiness) return ''

  if (readiness.window_open === false) {
    const date = formatWindowOn(readiness.window_on, locale)
    if (readiness.window_reason === 'not_open_yet' && date) {
      return t('applicationDetailPage.readinessHeadline.draft.opensOn', { date })
    }
    if (readiness.window_reason === 'closed' && date) {
      return t('applicationDetailPage.readinessHeadline.draft.closedOn', { date })
    }
    return t('applicationDetailPage.readinessHeadline.draft.windowClosed')
  }

  const counts = readiness.document_counts || {}
  const parts = []
  if (counts.missing) {
    parts.push(countPhrase(
      t,
      'applicationDetailPage.readinessHeadline.draft.missingDocsOne',
      'applicationDetailPage.readinessHeadline.draft.missingDocsMany',
      counts.missing,
    ))
  }
  if (counts.resubmit) {
    parts.push(countPhrase(
      t,
      'applicationDetailPage.readinessHeadline.draft.resubmitOne',
      'applicationDetailPage.readinessHeadline.draft.resubmitMany',
      counts.resubmit,
    ))
  }
  if (counts.invalid) {
    parts.push(countPhrase(
      t,
      'applicationDetailPage.readinessHeadline.draft.invalidOne',
      'applicationDetailPage.readinessHeadline.draft.invalidMany',
      counts.invalid,
    ))
  }
  if (counts.pending_review) {
    parts.push(countPhrase(
      t,
      'applicationDetailPage.readinessHeadline.draft.pendingReviewOne',
      'applicationDetailPage.readinessHeadline.draft.pendingReviewMany',
      counts.pending_review,
    ))
  }
  if (readiness.form_complete === false) {
    parts.push(t('applicationDetailPage.readinessHeadline.draft.formIncomplete'))
  }
  if (readiness.host_destination && readiness.host_destination.complete === false) {
    parts.push(t('applicationDetailPage.readinessHeadline.draft.hostIncomplete'))
  }
  if (readiness.eligibility && readiness.eligibility.complete === false) {
    parts.push(t('applicationDetailPage.readinessHeadline.draft.eligibilityUnmet'))
  }
  const daysLeft = readiness.deadline_days
  if (daysLeft != null && daysLeft >= 0 && daysLeft <= 14) {
    parts.push(countPhrase(
      t,
      'applicationDetailPage.readinessHeadline.draft.deadlineDaysOne',
      'applicationDetailPage.readinessHeadline.draft.deadlineDaysMany',
      daysLeft,
    ))
  }

  if (parts.length) return `${parts.join('; ')}.`

  const hasStructure = Boolean(
    readiness.document_counts
    || readiness.host_destination
    || readiness.eligibility
    || readiness.form_complete != null
    || readiness.window_open != null,
  )
  if (!hasStructure) return ''
  if (counts.required === 0) {
    return t('applicationDetailPage.readinessHeadline.draft.readyNoDocs')
  }
  return t('applicationDetailPage.readinessHeadline.draft.ready')
}

/** Localized headline; drafts compose from structured readiness when present. */
export function formatReadinessHeadline({ status, headline, readiness, t, te, locale } = {}) {
  if (status && status !== 'draft') {
    const key = `applicationDetailPage.readinessHeadline.${status}`
    if (typeof te === 'function' ? te(key) : true) {
      const translated = t(key)
      if (translated && translated !== key) return translated
    }
  }
  const composed = formatDraftReadinessHeadline({ readiness, t, locale })
  return composed || headline || ''
}
