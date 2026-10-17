/**
 * Input bounds for a Promedio typed in a given grade scale.
 * Scales up to 10 use two decimals; wider scales (e.g. 0–100) use one.
 */
export function gradeScaleBounds(scale) {
  const lo = Number(scale?.min_value)
  const hi = Number(scale?.max_value)
  if (!Number.isFinite(lo) || !Number.isFinite(hi) || hi === lo) {
    return { min: 0, max: null, step: 0.01 }
  }
  const min = Math.min(lo, hi)
  const max = Math.max(lo, hi)
  return { min, max, step: max > 10 ? 0.1 : 0.01 }
}

/** Find a scale row by id in a list of ``{ id, ... }`` rows (ids compared as strings). */
export function findScale(scales, id) {
  if (id == null || id === '') return null
  return (scales || []).find((row) => String(row.id) === String(id)) || null
}

/** Normalise the profile's ``grade_scale_policy`` payload. */
export function gradeScalePolicy(profile) {
  const policy = profile?.grade_scale_policy || {}
  const defaultId = policy.default_grade_scale == null ? '' : String(policy.default_grade_scale)
  return {
    locked: Boolean(policy.locked && defaultId),
    defaultId,
    defaultName: policy.default_grade_scale_name || '',
  }
}
