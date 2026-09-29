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

/** True when `name` is a machine key (slug) rather than a display phrase. */
export function looksLikeTechnicalDocumentName(name) {
  return /^[a-z0-9]+(?:[_-][a-z0-9]+)*$/.test(String(name || '').trim())
}

export function documentTypeLabel(type, fallback = '', i18n) {
  let t = coerceDocumentNested(type)
  if (typeof t === 'string') {
    const looseName = typeNameFromLooseString(t)
    if (looseName) return looseName
  }
  if (t == null || t === '') return fallback
  if (typeof t === 'object' && t !== null) {
    const name = t.name != null ? String(t.name).trim() : ''
    const description = t.description != null ? String(t.description).trim() : ''
    const slug = t.slug != null ? String(t.slug).trim() : ''
    const i18nSlug = (slug || (looksLikeTechnicalDocumentName(name) ? name : '')).toLowerCase()
    if (i18nSlug && i18n?.te && i18n?.t) {
      const key = `documentTypes.${i18nSlug}`
      if (i18n.te(key)) return i18n.t(key)
    }
    if (description && (looksLikeTechnicalDocumentName(name) || (slug && name === slug))) {
      return description
    }
    if (name) return name
    if (description) return description
  }
  if (typeof t === 'number' || typeof t === 'string') return String(t)
  return fallback
}

/**
 * Review status for an uploaded document.
 *
 * `is_valid` defaults to false on upload, so false alone is not a rejection.
 * Staff validation sets `validated_at`; only then is false treated as invalid.
 *
 * @returns {'valid' | 'invalid' | 'pending'}
 */
export function documentReviewStatus(doc) {
  if (doc?.is_valid === true) return 'valid'
  if (doc?.is_valid === false && doc?.validated_at) return 'invalid'
  return 'pending'
}

/**
 * i18n key for checklist-aligned review labels (Approved / Rejected / Pending review).
 */
export function documentReviewStatusI18nKey(doc) {
  const status = documentReviewStatus(doc)
  if (status === 'valid') return 'applicationDetailPage.checklist.approved'
  if (status === 'invalid') return 'applicationDetailPage.checklist.invalid'
  return 'applicationDetailPage.checklist.pending_review'
}

/** Checklist-aligned badge label for an uploaded document. */
export function documentReviewStatusLabel(doc, i18n) {
  const key = documentReviewStatusI18nKey(doc)
  if (i18n?.te?.(key) && i18n?.t) return i18n.t(key)
  const status = documentReviewStatus(doc)
  if (status === 'valid') return 'Approved'
  if (status === 'invalid') return 'Rejected'
  return 'Pending review'
}

export function documentReviewStatusBadgeClass(doc) {
  const status = documentReviewStatus(doc)
  if (status === 'valid') return 'bg-success'
  if (status === 'invalid') return 'bg-danger'
  return 'bg-warning text-dark'
}

/** Checklist statuses that still need a student upload / replace. */
export const CHECKLIST_UPLOAD_GAP_STATUSES = new Set([
  'missing',
  'invalid',
  'resubmit_requested',
])

/**
 * Checklist items the student can still upload for (gaps only).
 * Excludes instructions-only / n_a and already-submitted / approved rows.
 */
export function checklistUploadGaps(checklist) {
  const items = Array.isArray(checklist?.items) ? checklist.items : []
  return items.filter((item) => {
    if (!item) return false
    if (item.submission_mode === 'instructions_only' || item.status === 'n_a') return false
    return CHECKLIST_UPLOAD_GAP_STATUSES.has(item.status)
  })
}

/**
 * Checklist items available in the upload picker, including allows_multiple types
 * that already have a current upload (pending/approved).
 */
export function checklistUploadTargets(checklist) {
  const items = Array.isArray(checklist?.items) ? checklist.items : []
  return items.filter((item) => {
    if (!item) return false
    if (item.submission_mode === 'instructions_only' || item.status === 'n_a') return false
    if (CHECKLIST_UPLOAD_GAP_STATUSES.has(item.status)) return true
    return Boolean(item.allows_multiple)
  })
}

/** Global upload defaults when a document type has no family/extension overrides. */
export const DEFAULT_ACCEPTED_EXTENSIONS = ['pdf', 'jpg', 'jpeg', 'png']
export const DEFAULT_MAX_FILE_SIZE_MB = 10

function normalizeExtension(ext) {
  return String(ext || '')
    .trim()
    .toLowerCase()
    .replace(/^\./, '')
}

/**
 * Resolved extensions for a document type (families + accepted_extensions extras).
 * Prefers API `resolved_accepted_extensions` when present.
 * Empty configuration falls back to global defaults.
 */
export function documentTypeAcceptedExtensions(type) {
  const seen = []
  const add = (ext) => {
    const cleaned = normalizeExtension(ext)
    if (cleaned && !seen.includes(cleaned)) seen.push(cleaned)
  }

  const resolved = type?.resolved_accepted_extensions
  if (resolved != null && String(resolved).trim() !== '') {
    for (const part of String(resolved).split(',')) add(part)
    if (seen.length) return seen
  }

  const families = type?.file_type_families
  if (Array.isArray(families)) {
    for (const family of families) {
      if (family && family.is_active === false) continue
      for (const part of String(family?.extensions || '').split(',')) add(part)
    }
  }
  for (const part of String(type?.accepted_extensions || '').split(',')) add(part)
  return seen.length ? seen : [...DEFAULT_ACCEPTED_EXTENSIONS]
}

export function documentTypeMaxFileSizeMb(type) {
  const raw = type?.max_file_size_mb
  const n = Number(raw)
  if (Number.isFinite(n) && n > 0) return n
  return DEFAULT_MAX_FILE_SIZE_MB
}

/** Value for `<input type="file" accept="…">` from extension list. */
export function acceptAttributeFromExtensions(extensions) {
  const list = Array.isArray(extensions) ? extensions : []
  return list
    .map((ext) => normalizeExtension(ext))
    .filter(Boolean)
    .map((ext) => `.${ext}`)
    .join(',')
}

/** Uppercase display list, e.g. "PDF, JPG, PNG". */
export function formatAcceptedExtensionsLabel(extensions) {
  return (Array.isArray(extensions) ? extensions : [])
    .map((ext) => String(ext || '').trim().toUpperCase().replace(/^\./, ''))
    .filter(Boolean)
    .join(', ')
}

/**
 * Localized "Accepted: PDF (max 10MB)" hint, or empty string when type is missing.
 * `t` is vue-i18n `t` (or any (key, params) => string).
 */
export function documentTypeAcceptedHintText(type, t) {
  if (!type) return ''
  const formats = formatAcceptedExtensionsLabel(documentTypeAcceptedExtensions(type))
  if (!formats) return ''
  const translate = typeof t === 'function' ? t : null
  if (!translate) {
    return `Accepted: ${formats} (max ${documentTypeMaxFileSizeMb(type)}MB)`
  }
  return translate('documentUpload.acceptedHint', {
    formats,
    maxMb: documentTypeMaxFileSizeMb(type),
  })
}

/**
 * Client-side file check aligned with server rules.
 * @returns {{ ok: true } | { ok: false, errorKey: string, params: object }}
 */
export function validateDocumentFile(file, type) {
  if (!file) {
    return { ok: false, errorKey: 'documentUpload.fileRequired', params: {} }
  }
  const extensions = documentTypeAcceptedExtensions(type)
  const name = String(file.name || '')
  const dot = name.lastIndexOf('.')
  const ext = dot >= 0 ? normalizeExtension(name.slice(dot + 1)) : ''
  const formats = formatAcceptedExtensionsLabel(extensions)
  const maxMb = documentTypeMaxFileSizeMb(type)

  if (!ext || !extensions.includes(ext)) {
    return {
      ok: false,
      errorKey: 'documentUpload.fileTypeNotAllowed',
      params: { formats, maxMb },
    }
  }

  const size = Number(file.size)
  if (Number.isFinite(size) && size > maxMb * 1024 * 1024) {
    return {
      ok: false,
      errorKey: 'documentUpload.fileTooLarge',
      params: { formats, maxMb },
    }
  }

  return { ok: true }
}

function defaultSelectStatusLabel(rawStatus) {
  return String(rawStatus).replace(/_/g, ' ')
}

/** Base label (program + status) without id suffix. */
export function applicationSelectBaseLabel(app, fallback = '', formatStatus = defaultSelectStatusLabel) {
  if (app == null || typeof app !== 'object') return fallback || String(app ?? '')
  const name = app.program_name || app.program?.name
  const rawStatus = typeof app.status === 'string' ? app.status : app.status?.name
  const status =
    rawStatus && typeof formatStatus === 'function'
      ? formatStatus(rawStatus)
      : rawStatus
        ? defaultSelectStatusLabel(rawStatus)
        : ''
  if (name && status) return `${name} (${status})`
  if (name) return String(name)
  if (app.id != null) return String(app.id)
  return fallback
}

/** Label for application `<select>` options. Pass `siblings` to suffix colliding labels with a short id. */
export function applicationSelectLabel(app, fallback = '', siblings = null, formatStatus = defaultSelectStatusLabel) {
  const base = applicationSelectBaseLabel(app, fallback, formatStatus)
  if (!Array.isArray(siblings) || siblings.length < 2 || app == null || typeof app !== 'object' || app.id == null) {
    return base
  }
  const hits = siblings.filter((s) => applicationSelectBaseLabel(s, fallback, formatStatus) === base)
  if (hits.length <= 1) return base
  return `${base} · ${String(app.id).slice(0, 8)}`
}

/** Prefer RFC 5987 / quoted filename from Content-Disposition; else ``fallback``. */
export function filenameFromContentDisposition(header, fallback = 'download') {
  if (!header || typeof header !== 'string') return fallback
  const utf8 = /filename\*=(?:UTF-8''|utf-8'')([^;\s]+)/i.exec(header)
  if (utf8?.[1]) {
    try {
      return decodeURIComponent(utf8[1].replace(/["']/g, '').trim()) || fallback
    } catch {
      /* keep falling through */
    }
  }
  const quoted = /filename\s*=\s*"([^"]+)"/i.exec(header)
  if (quoted?.[1]) return quoted[1].trim() || fallback
  const plain = /filename\s*=\s*([^;\s]+)/i.exec(header)
  if (plain?.[1]) return plain[1].replace(/["']/g, '').trim() || fallback
  return fallback
}
