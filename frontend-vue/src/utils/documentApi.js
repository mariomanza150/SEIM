/**
 * Helpers for /api/documents/ payloads: `application` may be a UUID string (legacy),
 * `{ id, program_name }`, or a **JSON string** (possibly double-encoded) of that object.
 * `type` may be a PK or `{ id, name, description }` (or stringified).
 */

/** Best-effort parse of id + program_name from a string that looks like JSON but failed JSON.parse. */
function applicationFieldsFromLooseString(s) {
  if (typeof s !== 'string') return null
  const idMatch = s.match(/"id"\s*:\s*"([^"]+)"/)
  const nameMatch = s.match(/"program_name"\s*:\s*"((?:[^"\\]|\\.)*)"/)
  if (!idMatch && !nameMatch) return null
  let programName = ''
  if (nameMatch) {
    programName = nameMatch[1].replace(/\\(["\\/bfnrt])/g, (_, c) => {
      const map = { '"': '"', '\\': '\\', '/': '/', b: '\b', f: '\f', n: '\n', r: '\r', t: '\t' }
      return map[c] ?? `\\${c}`
    })
  }
  return {
    id: idMatch ? idMatch[1] : '',
    program_name: programName,
  }
}

/** Best-effort type name from a loose JSON-ish string. */
function typeNameFromLooseString(s) {
  if (typeof s !== 'string') return ''
  const m = s.match(/"name"\s*:\s*"((?:[^"\\]|\\.)*)"/)
  if (!m) return ''
  return m[1].replace(/\\(["\\/bfnrt])/g, (_, c) => {
    const map = { '"': '"', '\\': '\\', '/': '/', b: '\b', f: '\f', n: '\n', r: '\r', t: '\t' }
    return map[c] ?? `\\${c}`
  })
}

function coerceDocumentNested(value) {
  if (value == null || typeof value !== 'string') return value
  let current = value
  for (let depth = 0; depth < 8; depth += 1) {
    if (typeof current !== 'string') break
    const t = current.trim()
    if (!t) break
    if (t.startsWith('{') || t.startsWith('[')) {
      try {
        current = JSON.parse(t)
        continue
      } catch {
        break
      }
    }
    if (t.startsWith('"') && t.endsWith('"') && t.length >= 2) {
      try {
        const inner = JSON.parse(t)
        if (typeof inner === 'string') {
          current = inner
          continue
        }
      } catch {
        /* ignore */
      }
    }
    break
  }
  return current
}

export function documentApplicationId(application) {
  let app = coerceDocumentNested(application)
  if (typeof app === 'string') {
    const loose = applicationFieldsFromLooseString(app)
    if (loose?.id) return loose.id
  }
  if (app == null || app === '') return ''
  if (typeof app === 'object' && app !== null && app.id != null) {
    return String(app.id)
  }
  return String(app)
}

export function documentApplicationProgramName(application, applicationsList = [], fallback = '') {
  let app = coerceDocumentNested(application)
  if (typeof app === 'string') {
    const loose = applicationFieldsFromLooseString(app)
    if (loose?.program_name) return loose.program_name
    if (loose?.id) {
      app = { id: loose.id, program_name: loose.program_name || '' }
    } else if (/^\s*\{/.test(app) || app.includes('"id"')) {
      return fallback
    }
  }
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
  let t = coerceDocumentNested(type)
  if (typeof t === 'string') {
    const looseName = typeNameFromLooseString(t)
    if (looseName) return looseName
  }
  if (t == null || t === '') return fallback
  if (typeof t === 'object' && t !== null && t.name) return String(t.name)
  if (typeof t === 'number' || typeof t === 'string') return String(t)
  return fallback
}

/** Label for application `<select>` options (list API uses `program_name`; FK may be id-only). */
export function applicationSelectLabel(app, fallback = '') {
  if (app == null || typeof app !== 'object') return fallback || String(app ?? '')
  const name = app.program_name || app.program?.name
  if (name) return String(name)
  if (app.id != null) return String(app.id)
  return fallback
}
