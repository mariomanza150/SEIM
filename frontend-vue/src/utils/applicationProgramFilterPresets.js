/** Saved-search `search_type` for new-application program list filters. */
export const APPLICATION_PROGRAM_FILTER_SEARCH_TYPE = 'program'

const DEFAULT_ORDERING = 'name'

export function defaultApplicationProgramFilterState() {
  return {
    search: '',
    required_language: '',
    min_language_level: '',
    start_date_after: '',
    start_date_before: '',
    min_gpa_max: '',
    accepting_applications: false,
    ordering: DEFAULT_ORDERING,
  }
}

/**
 * JSON `filters` for POST /api/saved-searches/ (`search_type=program`).
 */
export function serializeApplicationProgramFilters(state) {
  const s = state && typeof state === 'object' ? state : {}
  let gpa = s.min_gpa_max
  if (gpa !== '' && gpa != null && !Number.isNaN(Number(gpa))) {
    gpa = Number(gpa)
  } else {
    gpa = ''
  }
  return {
    search: (s.search || '').trim(),
    required_language: (s.required_language || '').trim(),
    min_language_level: s.min_language_level || '',
    start_date_after: s.start_date_after || '',
    start_date_before: s.start_date_before || '',
    min_gpa_max: gpa === '' ? '' : gpa,
    accepting_applications: Boolean(s.accepting_applications),
    ordering: s.ordering || DEFAULT_ORDERING,
  }
}

/**
 * Map stored filters onto the ApplicationForm `programFilters` ref shape.
 */
export function deserializeApplicationProgramFilters(raw) {
  const f = raw && typeof raw === 'object' ? raw : {}
  const base = defaultApplicationProgramFilterState()
  let gpa = f.min_gpa_max
  if (gpa !== '' && gpa != null && !Number.isNaN(Number(gpa))) {
    gpa = String(Number(gpa))
  } else {
    gpa = ''
  }
  return {
    ...base,
    search: f.search ?? '',
    required_language: f.required_language ?? '',
    min_language_level: f.min_language_level ?? '',
    start_date_after: f.start_date_after ?? '',
    start_date_before: f.start_date_before ?? '',
    min_gpa_max: gpa,
    accepting_applications: Boolean(f.accepting_applications),
    ordering: f.ordering || DEFAULT_ORDERING,
  }
}
