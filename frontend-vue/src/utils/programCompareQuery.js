const MAX_PROGRAMS = 4

/**
 * Parse `?ids=uuid,uuid` into at most four non-empty id strings.
 */
export function parseCompareIdsFromQuery(query) {
  const raw = query?.ids
  if (raw == null || raw === '') return []
  const s = typeof raw === 'string' ? raw : String(raw)
  return s
    .split(',')
    .map((part) => part.trim())
    .filter(Boolean)
    .slice(0, MAX_PROGRAMS)
}

export function compareIdsToQueryParam(ids) {
  const list = (ids || []).filter(Boolean).slice(0, MAX_PROGRAMS)
  return list.length ? list.join(',') : ''
}

export { MAX_PROGRAMS as MAX_COMPARE_PROGRAMS }
