export function severityClass(severity) {
  return (
    {
      blocker: 'text-bg-danger',
      major: 'text-bg-warning',
      minor: 'text-bg-info',
      cosmetic: 'text-bg-secondary',
    }[severity] || 'text-bg-secondary'
  )
}

export function formatBytes(n) {
  if (!n && n !== 0) return ''
  if (n < 1024) return `${n} B`
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(0)} KB`
  return `${(n / (1024 * 1024)).toFixed(1)} MB`
}
