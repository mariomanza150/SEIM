/**
 * Cross-field helpers for admin host-university / destinations forms.
 * Uses existing host institutions across programs as a suggestion catalog.
 */

const EUROPEAN_COUNTRY_VALUES = new Set([
  'Alemania',
  'España',
  'Finlandia',
  'Francia',
  'Italia',
])

export function normalizeCountryToken(value) {
  return String(value || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .trim()
    .toLowerCase()
}

/** Build lookup tokens for a country catalog option (value, label, aliases). */
export function countryOptionTokens(option) {
  if (!option) return []
  const tokens = [option.value, option.label, ...(option.aliases || [])]
  return tokens.map(normalizeCountryToken).filter(Boolean)
}

/**
 * True when ``left`` and ``right`` refer to the same country, using catalog aliases.
 */
export function countriesMatch(left, right, countryOptions = []) {
  const a = normalizeCountryToken(left)
  const b = normalizeCountryToken(right)
  if (!a || !b) return false
  if (a === b) return true

  for (const option of countryOptions) {
    const tokens = countryOptionTokens(option)
    if (tokens.includes(a) && tokens.includes(b)) return true
  }
  return false
}

function isEuropeanUnionScaleCountry(scaleCountry) {
  const token = normalizeCountryToken(scaleCountry)
  return token.includes('europe') || token === 'eu' || token === 'ects'
}

/**
 * Whether a grade scale should appear for the selected host country.
 * Scales with no country stay available; EU-scoped scales match European CGRI countries.
 */
export function gradeScaleMatchesCountry(scale, countryValue, countryOptions = []) {
  if (!countryValue) return true
  const scaleCountry = scale?.country
  if (!scaleCountry) return true
  if (countriesMatch(scaleCountry, countryValue, countryOptions)) return true
  if (isEuropeanUnionScaleCountry(scaleCountry) && EUROPEAN_COUNTRY_VALUES.has(countryValue)) {
    return true
  }
  return false
}

export function filterGradeScalesByCountry(scales, countryValue, countryOptions = []) {
  const list = Array.isArray(scales) ? scales : []
  if (!countryValue) return list
  return list.filter((scale) => gradeScaleMatchesCountry(scale, countryValue, countryOptions))
}

/**
 * Deduplicated name suggestions from host institutions, optionally narrowed by country.
 */
export function buildHostNameOptions(institutions, { country = '', query = '' } = {}) {
  const list = Array.isArray(institutions) ? institutions : []
  const countryNeedle = String(country || '').trim()
  const queryNeedle = normalizeCountryToken(query)
  const seen = new Set()
  const options = []

  for (const inst of list) {
    const name = String(inst?.name || '').trim()
    if (!name) continue
    if (countryNeedle && String(inst.country || '').trim() !== countryNeedle) continue
    if (queryNeedle && !normalizeCountryToken(name).includes(queryNeedle)) continue
    const key = `${normalizeCountryToken(name)}|${normalizeCountryToken(inst.country)}`
    if (seen.has(key)) continue
    seen.add(key)
    const countryLabel = String(inst.country || '').trim()
    options.push({
      value: encodeHostSuggestion(inst),
      label: countryLabel ? `${name} · ${countryLabel}` : name,
      aliases: [name],
      meta: {
        name,
        country: countryLabel,
        grade_scale: inst.grade_scale || '',
      },
    })
  }

  return options.sort((a, b) => a.label.localeCompare(b.label, undefined, { sensitivity: 'base' }))
}

const SUGGESTION_SEP = '\u001f'

export function encodeHostSuggestion(inst) {
  return [
    String(inst?.name || '').trim(),
    String(inst?.country || '').trim(),
    inst?.grade_scale || '',
  ].join(SUGGESTION_SEP)
}

export function decodeHostSuggestion(value) {
  const raw = String(value || '')
  if (!raw.includes(SUGGESTION_SEP)) {
    const name = raw.trim()
    return name ? { name, country: '', grade_scale: '' } : null
  }
  const [name, country = '', grade_scale = ''] = raw.split(SUGGESTION_SEP)
  const trimmed = String(name || '').trim()
  if (!trimmed) return null
  return {
    name: trimmed,
    country: String(country || '').trim(),
    grade_scale: grade_scale || '',
  }
}

/**
 * Countries that appear on catalog institutions matching the typed university name.
 * Falls back to the full catalog when the query is empty or has no matches.
 */
export function filterCountryOptionsByHostName(countryOptions, institutions, nameQuery) {
  const options = Array.isArray(countryOptions) ? countryOptions : []
  const needle = normalizeCountryToken(nameQuery)
  if (!needle) return options

  const matchingCountries = new Set()
  for (const inst of institutions || []) {
    const name = normalizeCountryToken(inst?.name)
    if (!name.includes(needle)) continue
    const country = String(inst?.country || '').trim()
    if (country) matchingCountries.add(country)
  }

  if (!matchingCountries.size) return options
  return options.filter((opt) => matchingCountries.has(opt.value))
}

/**
 * Institutions in the current program list matching a free-text search.
 */
export function filterInstitutionsBySearch(institutions, search) {
  const list = Array.isArray(institutions) ? institutions : []
  const needle = normalizeCountryToken(search)
  if (!needle) return list
  return list.filter((inst) => {
    const hay = [
      inst?.name,
      inst?.country,
      inst?.grade_scale_name,
      inst?.grade_scale_code,
    ]
      .map(normalizeCountryToken)
      .join(' ')
    return hay.includes(needle)
  })
}
