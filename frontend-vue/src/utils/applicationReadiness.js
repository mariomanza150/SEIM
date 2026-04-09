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
