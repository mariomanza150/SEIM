/**
 * Normalize DRF / Django error payloads for display.
 */

export function flattenFieldMessages(raw) {
  if (raw == null) return []
  if (typeof raw === 'string') return [raw]
  if (Array.isArray(raw)) {
    return raw.flatMap((item) => flattenFieldMessages(item))
  }
  if (typeof raw === 'object') {
    return Object.values(raw).flatMap((v) => flattenFieldMessages(v))
  }
  return [String(raw)]
}

export function formatApiErrorResponse(data) {
  if (data == null || typeof data !== 'object') return null
  if (typeof data.detail === 'string') return data.detail
  if (Array.isArray(data.detail)) return data.detail.map(String).join(' ')
  if (Array.isArray(data.non_field_errors)) return data.non_field_errors.join(' ')
  const parts = []
  for (const [key, val] of Object.entries(data)) {
    if (key === 'detail' && val && typeof val === 'object' && !Array.isArray(val)) {
      for (const inner of Object.values(val)) {
        if (Array.isArray(inner)) parts.push(...inner.map(String))
        else if (inner != null) parts.push(String(inner))
      }
      continue
    }
    if (Array.isArray(val)) parts.push(...val.map(String))
    else if (typeof val === 'string') parts.push(val)
  }
  return parts.length ? parts.join(' ') : null
}

export function fieldErrorsFromResponse(data) {
  if (!data || typeof data !== 'object' || Array.isArray(data)) return {}
  const skip = new Set(['detail', 'non_field_errors', 'code', 'error_code'])
  const fields = {}
  for (const [key, val] of Object.entries(data)) {
    if (skip.has(key)) continue
    const messages = flattenFieldMessages(val)
    if (messages.length) fields[key] = messages
  }
  return fields
}

export function getApiErrorMessage(error, fallback = 'Request failed') {
  const data = error?.response?.data
  return formatApiErrorResponse(data) || error?.message || fallback
}
