function titleCaseFromSnake(value) {
  return String(value || '')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase())
}

export function applicationProgramDisplayName(app) {
  if (!app) return ''
  return (app.program_name || app.program?.name || '').trim()
}

export function applicationStatusBadgeClass(status) {
  const classes = {
    draft: 'bg-secondary',
    submitted: 'bg-info',
    under_review: 'bg-warning',
    approved: 'bg-success',
    rejected: 'bg-danger',
    completed: 'bg-primary',
  }
  return classes[status] || 'bg-secondary'
}

export function formatApplicationStatus({ status, t, te, unknownKey = 'applicationDetailPage.status.unknown' }) {
  if (!status) return t(unknownKey)
  const key = `applicationDetailPage.status.${status}`
  if (typeof te === 'function' && te(key)) return t(key)
  return titleCaseFromSnake(status)
}

export function formatDate({ dateString, locale, fallback = 'N/A' }) {
  if (!dateString) return fallback
  const date = new Date(dateString)
  const localeTag = locale === 'es' ? 'es' : 'en-US'
  return date.toLocaleDateString(localeTag, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

export function formatDateTime({ dateString, locale, fallback = 'N/A' }) {
  if (!dateString) return fallback
  const date = new Date(dateString)
  const localeTag = locale === 'es' ? 'es' : 'en-US'
  return date.toLocaleString(localeTag, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

