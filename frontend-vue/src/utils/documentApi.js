/**
 * Helpers for /api/documents/ payloads: `application` may be a UUID string (legacy)
 * or `{ id, program_name }`; `type` may be a PK or `{ id, name, description }`.
 */

export function documentApplicationId(application) {
  if (application == null || application === '') return ''
  if (typeof application === 'object' && application !== null && application.id != null) {
    return String(application.id)
  }
  return String(application)
}

export function documentApplicationProgramName(application, applicationsList = [], fallback = '') {
  if (application == null || application === '') return fallback
  if (typeof application === 'object' && application !== null && application.program_name) {
    return application.program_name
  }
  const id = documentApplicationId(application)
  const app = applicationsList.find((a) => String(a.id) === id)
  const name = app?.program_name || app?.program?.name
  if (name) return name
  return fallback || id
}

export function documentTypeLabel(type, fallback = '') {
  if (type == null || type === '') return fallback
  if (typeof type === 'object' && type !== null && type.name) return String(type.name)
  if (typeof type === 'number' || typeof type === 'string') return String(type)
  return fallback
}
