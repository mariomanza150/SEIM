/**
 * Helpers for /api/documents/ payloads: `application` may be a UUID string (legacy),
 * `{ id, program_name }`, or (defensive) a **JSON string** of that object when an upstream
 * layer double-encodes. `type` may be a PK or `{ id, name, description }` (or stringified).
 */

function coerceDocumentNested(value) {
  if (typeof value !== 'string') return value
  const s = value.trim()
  if (!(s.startsWith('{') || s.startsWith('['))) return value
  try {
    return JSON.parse(s)
  } catch {
    return value
  }
}

export function documentApplicationId(application) {
  const app = coerceDocumentNested(application)
  if (app == null || app === '') return ''
  if (typeof app === 'object' && app !== null && app.id != null) {
    return String(app.id)
  }
  return String(app)
}

export function documentApplicationProgramName(application, applicationsList = [], fallback = '') {
  const app = coerceDocumentNested(application)
  if (app == null || app === '') return fallback
  if (typeof app === 'object' && app !== null && app.program_name) {
    return app.program_name
  }
  const id = documentApplicationId(app)
  const row = applicationsList.find((a) => String(a.id) === id)
  const name = row?.program_name || row?.program?.name
  if (name) return name
  return fallback || id
}

export function documentTypeLabel(type, fallback = '') {
  const t = coerceDocumentNested(type)
  if (t == null || t === '') return fallback
  if (typeof t === 'object' && t !== null && t.name) return String(t.name)
  if (typeof t === 'number' || typeof t === 'string') return String(t)
  return fallback
}
