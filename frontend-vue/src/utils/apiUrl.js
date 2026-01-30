/**
 * Resolve API/media URLs for download links.
 * Django may return relative paths (e.g. /media/documents/file.pdf).
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

export function resolveFileUrl(url) {
  if (!url) return ''
  if (url.startsWith('http://') || url.startsWith('https://')) return url
  const base = API_BASE.replace(/\/$/, '')
  const path = url.startsWith('/') ? url : `/${url}`
  return `${base}${path}`
}
