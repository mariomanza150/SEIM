/**
 * Match backend ``application_forms.visibility`` for ``x-seim-visibleWhen`` / ``visible_when``.
 */

function isTruthy(value) {
  if (value === null || value === undefined) return false
  if (typeof value === 'boolean') return value
  if (typeof value === 'number') return value !== 0
  if (typeof value === 'string') return value.trim() !== ''
  if (Array.isArray(value)) return value.length > 0
  return true
}

function contextConstraintsPass(rule, context) {
  const ctx = context || {}

  if (Object.prototype.hasOwnProperty.call(rule, 'program_id')) {
    const want = Number(rule.program_id)
    if (!Number.isFinite(want)) return false
    const cur = ctx.program_id
    if (cur == null || !Number.isFinite(Number(cur))) return false
    if (Number(cur) !== want) return false
  }

  if (Object.prototype.hasOwnProperty.call(rule, 'program_id_in')) {
    const raw = rule.program_id_in
    if (!Array.isArray(raw) || raw.length === 0) return false
    const allowed = raw.map((x) => Number(x)).filter((n) => Number.isFinite(n))
    const cur = ctx.program_id
    if (cur == null || !Number.isFinite(Number(cur))) return false
    if (!allowed.includes(Number(cur))) return false
  }

  if (rule.has_assigned_coordinator === true) {
    if (!ctx.has_assigned_coordinator) return false
  }
  if (rule.has_assigned_coordinator === false) {
    if (ctx.has_assigned_coordinator) return false
  }

  if (rule.staff_only === true) {
    const vr = new Set(ctx.viewer_roles || [])
    if (!vr.has('coordinator') && !vr.has('admin')) return false
  }

  if (Object.prototype.hasOwnProperty.call(rule, 'roles_any')) {
    const need = rule.roles_any
    if (!Array.isArray(need) || need.length === 0) return false
    const vr = new Set((ctx.viewer_roles || []).map(String))
    const allowed = new Set(need.map(String))
    const hit = [...vr].some((role) => allowed.has(role))
    if (!hit) return false
  }

  return true
}

/**
 * @param {Record<string, unknown>|undefined} rule
 * @param {Record<string, unknown>} values - dynamic form responses
 * @param {Record<string, unknown>} [context] - program_id, has_assigned_coordinator
 */
export function visibleWhenRuleMatches(rule, values, context = undefined) {
  if (!rule || typeof rule !== 'object') return true
  if (!contextConstraintsPass(rule, context)) return false

  const fieldName = rule.field
  if (!fieldName || typeof fieldName !== 'string') return true

  const key = fieldName.trim()
  const value = Object.prototype.hasOwnProperty.call(values, key) ? values[key] : undefined

  if (Object.prototype.hasOwnProperty.call(rule, 'equals')) {
    return value === rule.equals
  }
  if (Object.prototype.hasOwnProperty.call(rule, 'notEquals')) {
    return value !== rule.notEquals
  }
  if (Object.prototype.hasOwnProperty.call(rule, 'in')) {
    const choices = rule.in
    if (!Array.isArray(choices)) return false
    return choices.includes(value)
  }
  if (rule.truthy === true) return isTruthy(value)
  if (rule.truthy === false) return !isTruthy(value)
  return true
}

/**
 * @param {Record<string, unknown>|undefined} fieldConfig
 * @param {Record<string, unknown>} values
 * @param {Record<string, unknown>} [context]
 */
export function fieldMeetsVisibleWhen(fieldConfig, values, context = undefined) {
  if (!fieldConfig || typeof fieldConfig !== 'object') return true
  const rule = fieldConfig['x-seim-visibleWhen'] ?? fieldConfig.x_seim_visibleWhen
  return visibleWhenRuleMatches(rule, values, context)
}

/**
 * @param {Record<string, unknown>|undefined} step
 * @param {Record<string, unknown>} values
 * @param {Record<string, unknown>} [context]
 */
export function stepMeetsVisibleWhen(step, values, context = undefined) {
  if (!step || typeof step !== 'object') return true
  const rule = step.visible_when ?? step.visibleWhen
  return visibleWhenRuleMatches(rule, values, context)
}
