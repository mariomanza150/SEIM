/**
 * Shared default-open rules for collapsible sections (admin / coordinator / student).
 *
 * Convention:
 * - Admins: density-first — prefer collapsed unless a section opts in via context.
 * - Coordinators: open staff-relevant sections (`defaultOpenForStaff`).
 * - Students: open action-needed sections (`defaultOpen`).
 * - Context predicates (`openWhen`) can force open for task relevance on admin-only pages
 *   (e.g. merge fields when a template is attached).
 *
 * Section def shape:
 *   {
 *     id: string,
 *     defaultOpen?: boolean,
 *     defaultOpenForStaff?: boolean,
 *     openWhen?: (context) => boolean,
 *   }
 */

/**
 * Resolve whether a collapsible section should start expanded.
 *
 * @param {object} def Section definition
 * @param {object} [viewer]
 * @param {boolean} [viewer.isAdmin]
 * @param {boolean} [viewer.isCoordinator]
 * @param {object} [context] Arbitrary view state passed to `def.openWhen`
 * @returns {boolean}
 */
export function resolveSectionDefaultOpen(def, viewer = {}, context = {}) {
  if (!def) return false

  if (typeof def.openWhen === 'function') {
    try {
      if (def.openWhen(context)) return true
    } catch {
      /* ignore predicate errors — fall through to role rules */
    }
  }

  if (viewer.isAdmin) return false
  if (def.defaultOpenForStaff && viewer.isCoordinator) return true
  return Boolean(def.defaultOpen)
}

/**
 * Build an id → open map from section defs for a given viewer/context.
 *
 * @param {object[]} defs
 * @param {object} [viewer]
 * @param {object} [context]
 * @returns {Record<string, boolean>}
 */
export function resolveSectionDefaultsMap(defs, viewer = {}, context = {}) {
  const list = Array.isArray(defs) ? defs : []
  return Object.fromEntries(
    list.map((def) => [def.id, resolveSectionDefaultOpen(def, viewer, context)]),
  )
}
