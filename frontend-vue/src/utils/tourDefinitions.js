export const TOUR_VERSION = 1

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

/**
 * Step definitions use i18n title/body keys and a data-tour selector.
 * @param {(key: string) => string} t
 * @param {'admin'|'staff'|'partner'|'student'} role
 */
export function buildTourSteps(t, role) {
  const common = [
    {
      id: 'sidebar',
      selector: '[data-tour="sidebar-nav"]',
      title: t(`tours.${role}.steps.sidebarTitle`),
      body: t(`tours.${role}.steps.sidebarBody`),
    },
    {
      id: 'commandPalette',
      selector: '[data-tour="command-palette"]',
      title: t(`tours.${role}.steps.paletteTitle`),
      body: t(`tours.${role}.steps.paletteBody`),
    },
  ]

  if (role === 'partner') {
    return [
      ...common,
      {
        id: 'stats',
        selector: '[data-tour="dashboard-stats"]',
        title: t('tours.partner.steps.statsTitle'),
        body: t('tours.partner.steps.statsBody'),
      },
      {
        id: 'partner',
        selector: '[data-tour="nav-partner"]',
        title: t('tours.partner.steps.portalTitle'),
        body: t('tours.partner.steps.portalBody'),
      },
    ]
  }

  if (role === 'staff' || role === 'admin') {
    const steps = [
      ...common,
      {
        id: 'stats',
        selector: '[data-tour="dashboard-stats"]',
        title: t(`tours.${role}.steps.statsTitle`),
        body: t(`tours.${role}.steps.statsBody`),
      },
      {
        id: 'review',
        selector: '[data-tour="nav-review-queue"]',
        title: t(`tours.${role}.steps.reviewTitle`),
        body: t(`tours.${role}.steps.reviewBody`),
      },
    ]
    if (role === 'admin') {
      steps.push({
        id: 'admin',
        selector: '[data-tour="admin-menu"]',
        title: t('tours.admin.steps.adminTitle'),
        body: t('tours.admin.steps.adminBody'),
      })
    }
    return steps
  }

  return [
    ...common,
    {
      id: 'stats',
      selector: '[data-tour="dashboard-stats"]',
      title: t('tours.student.steps.statsTitle'),
      body: t('tours.student.steps.statsBody'),
    },
    {
      id: 'applications',
      selector: '[data-tour="nav-applications"]',
      title: t('tours.student.steps.applicationsTitle'),
      body: t('tours.student.steps.applicationsBody'),
    },
  ]
}

export function tourIdForRole(role) {
  return `welcome-${role}-v${TOUR_VERSION}`
}
