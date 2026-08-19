function titleCaseFromSnake(value) {
  return String(value || '')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase())
}

export function applicationProgramDisplayName(app) {
  if (!app) return ''
  return (app.program_name || app.program?.name || '').trim()
}

export function applicationHostInstitution(app) {
  if (!app) return ''
  const nested = typeof app.program === 'object' && app.program ? app.program.institution : ''
  return (app.host_institution_name || nested || '').trim()
}

export function applicationHostCountry(app) {
  if (!app) return ''
  const nested = typeof app.program === 'object' && app.program ? app.program.country : ''
  return (app.host_institution_country || nested || '').trim()
}

function parseLocalDate(value) {
  const iso = String(value || '').match(/^(\d{4})-(\d{2})-(\d{2})(?:$|T)/)
  if (iso) return new Date(Number(iso[1]), Number(iso[2]) - 1, Number(iso[3]))
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? null : date
}

export function applicationProgramDuration({ app, locale, fallback = '' }) {
  if (!app) return fallback
  const nested = typeof app.program === 'object' && app.program
    ? String(app.program.duration || '').trim()
    : ''
  if (nested) return nested
  const start = parseLocalDate(app.program_start_date)
  const end = parseLocalDate(app.program_end_date)
  if (!start || !end) return fallback
  const localeTag = locale === 'es' ? 'es' : 'en-US'
  const opts = { year: 'numeric', month: 'short', day: 'numeric' }
  return `${start.toLocaleDateString(localeTag, opts)} – ${end.toLocaleDateString(localeTag, opts)}`
}

export function applicationStatusBadgeClass(status) {
  const classes = {
    draft: 'bg-secondary',
    submitted: 'bg-info',
    under_review: 'bg-warning',
    approved: 'bg-success',
    nominated: 'bg-success',
    rejected: 'bg-danger',
    completed: 'bg-primary',
    waitlist: 'bg-secondary',
    cancelled: 'bg-dark',
    withdrawn: 'bg-dark',
  }
  return classes[status] || 'bg-secondary'
}

export const APPLICATION_STATUS_FILTER_VALUES = [
  'draft',
  'submitted',
  'under_review',
  'nominated',
  'waitlist',
  'approved',
  'rejected',
  'completed',
  'cancelled',
  'withdrawn',
]

/** Read a validated application status filter from a route query object. */
export function applicationStatusFromRouteQuery(query) {
  const raw = query?.status
  if (typeof raw !== 'string') return ''
  return APPLICATION_STATUS_FILTER_VALUES.includes(raw) ? raw : ''
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

export function formatScorePoints(value) {
  const n = Number(value)
  if (!Number.isFinite(n)) return value == null ? '' : String(value)
  return n.toLocaleString('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
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

