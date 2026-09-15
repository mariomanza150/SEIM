/**
 * Build command-palette items from the same visibility rules as AppShell nav.
 *
 * @param {object} opts
 * @param {(key: string) => string} opts.t
 * @param {boolean} opts.canUsePartnerPortal
 * @param {boolean} opts.canUseStaffReviewQueue
 * @param {boolean} opts.isAdmin
 * @returns {Array<{ id: string, section: string, sectionKey: string, label: string, keywords: string, iconClass: string, type: 'route'|'action', to?: object, action?: string }>}
 */
export function buildCommandPaletteItems({
  t,
  canUsePartnerPortal = false,
  canUseStaffReviewQueue = false,
  isAdmin = false,
}) {
  const items = []

  function addRoute(sectionKey, section, id, to, label, iconClass, keywords = '') {
    items.push({
      id,
      sectionKey,
      section,
      label,
      keywords: keywords.toLowerCase(),
      iconClass,
      type: 'route',
      to,
    })
  }

  function addAction(sectionKey, section, id, action, label, iconClass, keywords = '') {
    items.push({
      id,
      sectionKey,
      section,
      label,
      keywords: keywords.toLowerCase(),
      iconClass,
      type: 'action',
      action,
    })
  }

  const main = t('nav.sections.main')
  const staff = t('nav.sections.staff')
  const account = t('nav.sections.account')
  const admin = t('nav.sections.admin')
  const actions = t('commandPalette.sectionActions')

  addRoute('main', main, 'dashboard', { name: 'Dashboard' }, t('route.names.Dashboard'), 'bi bi-house-door', 'home')

  if (!canUsePartnerPortal) {
    addRoute('main', main, 'applications', { name: 'Applications' }, t('route.names.Applications'), 'bi bi-file-earmark-text', 'apply')
    addRoute('main', main, 'programCompare', { name: 'ProgramCompare' }, t('route.names.ProgramCompare'), 'bi bi-columns-gap', 'compare programs')
    addRoute('main', main, 'documents', { name: 'Documents' }, t('route.names.Documents'), 'bi bi-folder', 'files upload')
    addRoute('main', main, 'toeflPractice', { name: 'ToeflPractice' }, t('route.names.ToeflPractice'), 'bi bi-journal-text', 'toefl english')
    addRoute('main', main, 'deadlines', { name: 'DeadlinesCalendar' }, t('dashboard.nav.deadlines'), 'bi bi-calendar3', 'calendar')
  } else {
    addRoute('main', main, 'partnerPortal', { name: 'PartnerPortal' }, t('route.names.PartnerPortal'), 'bi bi-building', 'partner')
  }

  if (canUseStaffReviewQueue) {
    addRoute('staff', staff, 'reviewQueue', { name: 'CoordinatorReviewQueue' }, t('route.names.CoordinatorReviewQueue'), 'bi bi-clipboard-check', 'review queue')
    addRoute('staff', staff, 'workload', { name: 'CoordinatorWorkload' }, t('dashboard.nav.workload'), 'bi bi-graph-up-arrow', 'workload')
    addRoute('staff', staff, 'notificationRouting', { name: 'NotificationRouting' }, t('dashboard.nav.notificationRouting'), 'bi bi-diagram-3', 'routing')
    addRoute('staff', staff, 'exchangeAgreements', { name: 'StaffExchangeAgreements' }, t('route.names.StaffExchangeAgreements'), 'bi bi-file-earmark-richtext', 'agreements')
    addRoute('staff', staff, 'eligibilityRulesets', { name: 'EligibilityRulesets' }, t('route.names.EligibilityRulesets'), 'bi bi-funnel', 'eligibility')
    addRoute('staff', staff, 'scholarshipScoringRulesets', { name: 'ScholarshipScoringRulesets' }, t('route.names.ScholarshipScoringRulesets'), 'bi bi-pie-chart', 'scholarship')
    addRoute('staff', staff, 'nominations', { name: 'Nominations' }, t('route.names.Nominations'), 'bi bi-trophy', 'nominate')
    addRoute('staff', staff, 'analyticsForecasts', { name: 'AnalyticsForecasts' }, t('route.names.AnalyticsForecasts'), 'bi bi-graph-up', 'forecast analytics')
  }

  addRoute('account', account, 'notifications', { name: 'Notifications' }, t('route.names.Notifications'), 'bi bi-bell', 'alerts')
  addRoute('account', account, 'help', { name: 'HelpCenter' }, t('route.names.HelpCenter'), 'bi bi-question-circle', 'help support')
  addRoute('account', account, 'profile', { name: 'Profile' }, t('route.names.Profile'), 'bi bi-person', 'profile account')
  addRoute('account', account, 'settings', { name: 'Settings' }, t('route.names.Settings'), 'bi bi-gear', 'preferences theme')

  if (isAdmin) {
    addRoute('admin', admin, 'adminPrograms', { name: 'AdminPrograms' }, t('route.names.AdminPrograms'), 'bi bi-mortarboard')
    addRoute('admin', admin, 'adminCatalogs', { name: 'AdminCatalogs' }, t('route.names.AdminCatalogs'), 'bi bi-list-ul')
    addRoute('admin', admin, 'adminGrades', { name: 'AdminGrades' }, t('route.names.AdminGrades'), 'bi bi-bar-chart-steps')
    addRoute('admin', admin, 'adminUsers', { name: 'AdminUsers' }, t('route.names.AdminUsers'), 'bi bi-people')
    addRoute('admin', admin, 'adminSessions', { name: 'AdminSessions' }, t('route.names.AdminSessions'), 'bi bi-shield-lock')
    addRoute('admin', admin, 'adminWorkflowCatalogs', { name: 'AdminWorkflowCatalogs' }, t('route.names.AdminWorkflowCatalogs'), 'bi bi-list-ol')
    addRoute('admin', admin, 'adminForms', { name: 'AdminForms' }, t('route.names.AdminForms'), 'bi bi-ui-checks-grid')
    addRoute('admin', admin, 'adminDynforms', { name: 'AdminDynforms' }, t('route.names.AdminDynforms'), 'bi bi-window-sidebar')
    addRoute('admin', admin, 'adminDataManagement', { name: 'AdminDataManagement' }, t('route.names.AdminDataManagement'), 'bi bi-database-gear')
    addRoute('admin', admin, 'adminWorkflows', { name: 'AdminWorkflows' }, t('route.names.AdminWorkflows'), 'bi bi-diagram-3')
    addRoute('admin', admin, 'adminDocuments', { name: 'AdminDocuments' }, t('route.names.AdminDocuments'), 'bi bi-file-earmark-text')
  }

  addAction('actions', actions, 'toggleTheme', 'toggleTheme', t('commandPalette.actionToggleTheme'), 'bi bi-circle-half', 'dark light theme')
  addAction('actions', actions, 'openHelp', 'openHelp', t('commandPalette.actionOpenHelp'), 'bi bi-question-circle', 'help')
  addAction('actions', actions, 'logout', 'logout', t('commandPalette.actionLogout'), 'bi bi-box-arrow-right', 'sign out logout')

  return items
}

/**
 * Simple case-insensitive filter: all query tokens must appear in label or keywords.
 * @param {Array<{ label: string, keywords?: string }>} items
 * @param {string} query
 */
export function filterCommandPaletteItems(items, query) {
  const q = String(query || '')
    .trim()
    .toLowerCase()
  if (!q) return items
  const tokens = q.split(/\s+/).filter(Boolean)
  return items.filter((item) => {
    const hay = `${item.label || ''} ${item.keywords || ''}`.toLowerCase()
    return tokens.every((token) => hay.includes(token))
  })
}
