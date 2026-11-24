export const TOUR_VERSION = 1

/** Dashboard welcome tour (role-specific shell). */
export const DASHBOARD_PAGE_ID = 'dashboard'

/**
 * Page-level walkthrough ids (role-aware step copy; selectors may be role-gated).
 * @type {readonly string[]}
 */
export const PAGE_TOUR_IDS = Object.freeze([
  'applications',
  'application-form',
  'documents',
  'review-queue',
  'partner-portal',
  'admin-programs',
])

/** Roles that may start each page tour. */
export const PAGE_TOUR_ROLES = Object.freeze({
  [DASHBOARD_PAGE_ID]: ['student', 'staff', 'admin', 'partner'],
  applications: ['student', 'staff', 'admin'],
  'application-form': ['student', 'staff', 'admin'],
  documents: ['student', 'staff', 'admin'],
  'review-queue': ['staff', 'admin'],
  'partner-portal': ['partner'],
  'admin-programs': ['admin'],
})

/** Vue route name → page tour id. */
export const ROUTE_TO_PAGE_TOUR = Object.freeze({
  Dashboard: DASHBOARD_PAGE_ID,
  Applications: 'applications',
  ApplicationNew: 'application-form',
  ApplicationEdit: 'application-form',
  Documents: 'documents',
  DocumentDetail: 'documents',
  CoordinatorReviewQueue: 'review-queue',
  PartnerPortal: 'partner-portal',
  AdminPrograms: 'admin-programs',
  AdminProgramDestinations: 'admin-programs',
  AdminApplicationEdit: 'application-form',
})

/** Help article contextual keys / topics → page tour id. */
export const HELP_KEY_TO_PAGE_TOUR = Object.freeze({
  Dashboard: DASHBOARD_PAGE_ID,
  Applications: 'applications',
  ApplicationNew: 'application-form',
  ApplicationEdit: 'application-form',
  Documents: 'documents',
  DocumentDetail: 'documents',
  CoordinatorReviewQueue: 'review-queue',
  PartnerPortal: 'partner-portal',
  AdminPrograms: 'admin-programs',
  AdminProgramDestinations: 'admin-programs',
  AdminApplicationEdit: 'application-form',
})

export const HELP_TOPIC_TO_PAGE_TOUR = Object.freeze({
  applications: 'applications',
  documents: 'documents',
  review: 'review-queue',
  partner: 'partner-portal',
  admin: 'admin-programs',
  getting_started: DASHBOARD_PAGE_ID,
})

/** Destination routes used when Help starts a walkthrough off-page. */
export const PAGE_TOUR_ROUTES = Object.freeze({
  [DASHBOARD_PAGE_ID]: { name: 'Dashboard' },
  applications: { name: 'Applications' },
  'application-form': { name: 'ApplicationNew' },
  documents: { name: 'Documents' },
  'review-queue': { name: 'CoordinatorReviewQueue' },
  'partner-portal': { name: 'PartnerPortal' },
  'admin-programs': { name: 'AdminPrograms' },
})

export function tourStorageUserKey(user) {
  if (!user) return null
  if (user.id != null && user.id !== '') return String(user.id)
  if (user.email) return String(user.email).toLowerCase()
  if (user.username) return String(user.username).toLowerCase()
  return null
}

/**
 * @param {object} auth
 * @param {boolean} auth.isAdmin
 * @param {boolean} auth.canUseStaffReviewQueue
 * @param {boolean} auth.canUsePartnerPortal
 * @returns {'admin'|'staff'|'partner'|'student'}
 */
export function resolveTourRole(auth) {
  if (auth?.isAdmin) return 'admin'
  if (auth?.canUsePartnerPortal) return 'partner'
  if (auth?.canUseStaffReviewQueue) return 'staff'
  return 'student'
}

/**
 * @param {string|number} userId
 * @param {string} tourId
 */
export function tourStorageKey(userId, tourId) {
  return `seim.tour.${userId}.${tourId}`
}

/**
 * @param {string|number} userId
 * @param {string} tourId
 * @param {number} [version]
 */
export function isTourCompleted(userId, tourId, version = TOUR_VERSION) {
  if (typeof localStorage === 'undefined' || userId == null) return false
  try {
    const raw = localStorage.getItem(tourStorageKey(userId, tourId))
    if (!raw) return false
    if (raw === 'done') return true
    const parsed = JSON.parse(raw)
    return parsed?.status === 'done' && Number(parsed?.version) === Number(version)
  } catch {
    return false
  }
}

/**
 * @param {string|number} userId
 * @param {string} tourId
 * @param {number} [version]
 */
export function markTourCompleted(userId, tourId, version = TOUR_VERSION) {
  if (typeof localStorage === 'undefined' || userId == null) return
  try {
    localStorage.setItem(
      tourStorageKey(userId, tourId),
      JSON.stringify({ status: 'done', version }),
    )
  } catch {
    /* ignore quota */
  }
}

/**
 * @param {string|number} userId
 * @param {string} tourId
 */
export function clearTourCompletion(userId, tourId) {
  if (typeof localStorage === 'undefined' || userId == null) return
  try {
    localStorage.removeItem(tourStorageKey(userId, tourId))
  } catch {
    /* ignore */
  }
}

export function tourIdForRole(role) {
  return `welcome-${role}-v${TOUR_VERSION}`
}

/**
 * @param {string} pageId
 * @param {'admin'|'staff'|'partner'|'student'} role
 */
export function tourIdForPage(pageId, role) {
  if (!pageId || pageId === DASHBOARD_PAGE_ID) return tourIdForRole(role)
  return `page-${pageId}-${role}-v${TOUR_VERSION}`
}

/**
 * @param {string} pageId
 * @param {'admin'|'staff'|'partner'|'student'} role
 */
export function isPageTourAllowed(pageId, role) {
  const allowed = PAGE_TOUR_ROLES[pageId]
  if (!allowed) return false
  return allowed.includes(role)
}

/**
 * @param {'admin'|'staff'|'partner'|'student'} role
 * @returns {string[]}
 */
export function pageToursForRole(role) {
  return PAGE_TOUR_IDS.filter((pageId) => isPageTourAllowed(pageId, role))
}

/**
 * @param {string|undefined|null} routeName
 * @returns {string|null}
 */
export function resolvePageTourFromRoute(routeName) {
  if (!routeName) return null
  return ROUTE_TO_PAGE_TOUR[routeName] || null
}

/**
 * Resolve a page walkthrough from a help article's contextual keys / topic.
 * @param {{ contextual_keys?: string[]|string, topic?: string, slug?: string }|null|undefined} article
 * @param {'admin'|'staff'|'partner'|'student'} role
 * @returns {string|null}
 */
export function resolvePageTourFromHelp(article, role) {
  if (!article) return null
  const keys = Array.isArray(article.contextual_keys)
    ? article.contextual_keys
    : String(article.contextual_keys || '')
        .split(',')
        .map((part) => part.trim())
        .filter(Boolean)

  for (const key of keys) {
    const pageId = HELP_KEY_TO_PAGE_TOUR[key]
    if (pageId && isPageTourAllowed(pageId, role)) return pageId
  }

  const topicPage = HELP_TOPIC_TO_PAGE_TOUR[article.topic]
  if (topicPage && isPageTourAllowed(topicPage, role)) return topicPage

  if (isPageTourAllowed(DASHBOARD_PAGE_ID, role)) return DASHBOARD_PAGE_ID
  return null
}

/**
 * @param {string} pageId
 * @returns {{ name: string }|null}
 */
export function routeForPageTour(pageId) {
  return PAGE_TOUR_ROUTES[pageId] || null
}

/**
 * True when the selector matches a mounted, visible-enough element.
 * @param {string} selector
 * @param {ParentNode|Document} [root]
 */
export function isTourTargetMounted(selector, root) {
  if (!selector) return false
  const doc = root || (typeof document !== 'undefined' ? document : null)
  if (!doc || typeof doc.querySelector !== 'function') return false
  try {
    const el = doc.querySelector(selector)
    if (!el) return false
    if (typeof el.getBoundingClientRect === 'function') {
      const rect = el.getBoundingClientRect()
      if (rect.width < 1 && rect.height < 1) return false
    }
    return true
  } catch {
    return false
  }
}

/**
 * Drop steps whose DOM targets are missing so tours never stall on role-gated UI.
 * @param {Array<{ selector?: string }>} steps
 * @param {ParentNode|Document} [root]
 */
export function filterMountedSteps(steps, root) {
  if (!Array.isArray(steps)) return []
  return steps.filter((step) => {
    if (!step?.selector) return true
    return isTourTargetMounted(step.selector, root)
  })
}

/**
 * @param {(key: string, values?: object) => string} t
 * @param {string} pageId
 * @param {string} stepKey prefix without Title/Body suffix
 * @param {'admin'|'staff'|'partner'|'student'} role
 * @param {(key: string) => boolean} [te]
 */
function pageStepCopy(t, pageId, stepKey, role, te) {
  const roleTitle = `tours.pages.${pageId}.${role}.steps.${stepKey}Title`
  const roleBody = `tours.pages.${pageId}.${role}.steps.${stepKey}Body`
  const sharedTitle = `tours.pages.${pageId}.steps.${stepKey}Title`
  const sharedBody = `tours.pages.${pageId}.steps.${stepKey}Body`
  const has = typeof te === 'function' ? te : (key) => {
    const value = t(key)
    return value !== key
  }
  return {
    title: has(roleTitle) ? t(roleTitle) : t(sharedTitle),
    body: has(roleBody) ? t(roleBody) : t(sharedBody),
  }
}

function step(id, selector, title, body) {
  return { id, selector, title, body }
}

/**
 * Dashboard shell walkthrough (existing welcome tour).
 * @param {(key: string) => string} t
 * @param {'admin'|'staff'|'partner'|'student'} role
 */
export function buildDashboardTourSteps(t, role) {
  const common = [
    step(
      'sidebar',
      '[data-tour="sidebar-nav"]',
      t(`tours.${role}.steps.sidebarTitle`),
      t(`tours.${role}.steps.sidebarBody`),
    ),
    step(
      'commandPalette',
      '[data-tour="command-palette"]',
      t(`tours.${role}.steps.paletteTitle`),
      t(`tours.${role}.steps.paletteBody`),
    ),
  ]

  if (role === 'partner') {
    return [
      ...common,
      step(
        'stats',
        '[data-tour="dashboard-stats"]',
        t('tours.partner.steps.statsTitle'),
        t('tours.partner.steps.statsBody'),
      ),
      step(
        'partner',
        '[data-tour="nav-partner"]',
        t('tours.partner.steps.portalTitle'),
        t('tours.partner.steps.portalBody'),
      ),
    ]
  }

  if (role === 'staff' || role === 'admin') {
    const steps = [
      ...common,
      step(
        'stats',
        '[data-tour="dashboard-stats"]',
        t(`tours.${role}.steps.statsTitle`),
        t(`tours.${role}.steps.statsBody`),
      ),
      step(
        'review',
        '[data-tour="nav-review-queue"]',
        t(`tours.${role}.steps.reviewTitle`),
        t(`tours.${role}.steps.reviewBody`),
      ),
    ]
    if (role === 'admin') {
      steps.push(
        step(
          'admin',
          '[data-tour="admin-menu"]',
          t('tours.admin.steps.adminTitle'),
          t('tours.admin.steps.adminBody'),
        ),
      )
    }
    return steps
  }

  return [
    ...common,
    step(
      'stats',
      '[data-tour="dashboard-stats"]',
      t('tours.student.steps.statsTitle'),
      t('tours.student.steps.statsBody'),
    ),
    step(
      'applications',
      '[data-tour="nav-applications"]',
      t('tours.student.steps.applicationsTitle'),
      t('tours.student.steps.applicationsBody'),
    ),
  ]
}

/**
 * @param {(key: string) => string} t
 * @param {string} pageId
 * @param {'admin'|'staff'|'partner'|'student'} role
 * @param {(key: string) => boolean} [te]
 */
export function buildPageTourSteps(t, pageId, role, te) {
  if (!pageId || pageId === DASHBOARD_PAGE_ID) {
    return buildDashboardTourSteps(t, role)
  }
  if (!isPageTourAllowed(pageId, role)) return []

  const copy = (stepKey) => pageStepCopy(t, pageId, stepKey, role, te)

  if (pageId === 'applications') {
    const header = copy('header')
    const filters = copy('filters')
    const list = copy('list')
    const actions = copy('actions')
    return [
      step('header', '[data-tour="applications-header"]', header.title, header.body),
      step('actions', '[data-tour="applications-new"]', actions.title, actions.body),
      step('tabs', '[data-tour="applications-tabs"]', copy('tabs').title, copy('tabs').body),
      step('filters', '[data-tour="applications-filters"]', filters.title, filters.body),
      step('list', '[data-tour="applications-list"]', list.title, list.body),
    ]
  }

  if (pageId === 'application-form') {
    const header = copy('header')
    const program = copy('program')
    const dynamic = copy('dynamic')
    const submit = copy('submit')
    return [
      step('header', '[data-tour="application-form-header"]', header.title, header.body),
      step('program', '[data-tour="application-form-program"]', program.title, program.body),
      step('dynamic', '[data-tour="application-form-dynamic"]', dynamic.title, dynamic.body),
      step('submit', '[data-tour="application-form-actions"]', submit.title, submit.body),
    ]
  }

  if (pageId === 'documents') {
    const header = copy('header')
    const filters = copy('filters')
    const list = copy('list')
    const prefill = copy('prefill')
    return [
      step('header', '[data-tour="documents-header"]', header.title, header.body),
      step('prefill', '[data-tour="documents-prefill"]', prefill.title, prefill.body),
      step('filters', '[data-tour="documents-filters"]', filters.title, filters.body),
      step('list', '[data-tour="documents-list"]', list.title, list.body),
    ]
  }

  if (pageId === 'review-queue') {
    const header = copy('header')
    const filters = copy('filters')
    const list = copy('list')
    return [
      step('header', '[data-tour="review-queue-header"]', header.title, header.body),
      step('filters', '[data-tour="review-queue-filters"]', filters.title, filters.body),
      step('list', '[data-tour="review-queue-list"]', list.title, list.body),
    ]
  }

  if (pageId === 'partner-portal') {
    const header = copy('header')
    const agreements = copy('agreements')
    const nominees = copy('nominees')
    const docs = copy('docs')
    return [
      step('header', '[data-tour="partner-portal-header"]', header.title, header.body),
      step('agreements', '[data-tour="partner-agreements"]', agreements.title, agreements.body),
      step('nominees', '[data-tour="partner-applications"]', nominees.title, nominees.body),
      step('docs', '[data-tour="partner-docs"]', docs.title, docs.body),
    ]
  }

  if (pageId === 'admin-programs') {
    const header = copy('header')
    const create = copy('create')
    const filters = copy('filters')
    const table = copy('table')
    return [
      step('header', '[data-tour="admin-programs-header"]', header.title, header.body),
      step('create', '[data-tour="admin-programs-create"]', create.title, create.body),
      step('filters', '[data-tour="admin-programs-filters"]', filters.title, filters.body),
      step('table', '[data-tour="admin-programs-table"]', table.title, table.body),
    ]
  }

  return []
}

/**
 * Step definitions use i18n title/body keys and a data-tour selector.
 * @param {(key: string) => string} t
 * @param {'admin'|'staff'|'partner'|'student'} role
 * @param {string} [pageId]
 * @param {{ filterMounted?: boolean, root?: ParentNode|Document, te?: (key: string) => boolean }} [options]
 */
export function buildTourSteps(t, role, pageId = DASHBOARD_PAGE_ID, options = {}) {
  const steps = buildPageTourSteps(t, pageId || DASHBOARD_PAGE_ID, role, options.te)
  if (options.filterMounted) {
    return filterMountedSteps(steps, options.root)
  }
  return steps
}

/**
 * Find the next (or previous) step index whose target is mounted.
 * @param {Array<{ selector?: string }>} steps
 * @param {number} fromIndex
 * @param {1|-1} direction
 * @param {ParentNode|Document} [root]
 * @returns {number} index or -1
 */
export function findNextMountedStepIndex(steps, fromIndex, direction = 1, root) {
  if (!Array.isArray(steps) || !steps.length) return -1
  let idx = fromIndex
  while (idx >= 0 && idx < steps.length) {
    const step = steps[idx]
    if (!step?.selector || isTourTargetMounted(step.selector, root)) return idx
    idx += direction
  }
  return -1
}
