/**
 * Map sidebar item keys to related route names so deep links expand the
 * correct accordion section (e.g. ApplicationDetail → Applications).
 */
export const NAV_ROUTE_FAMILIES = {
  applications: [
    'Applications',
    'ApplicationNew',
    'ApplicationEdit',
    'ApplicationDetail',
    'AdminApplicationEdit',
  ],
  documents: ['Documents', 'DocumentDetail'],
  help: ['HelpCenter', 'HelpArticle'],
  exchangeAgreements: ['StaffExchangeAgreements', 'StaffAgreementDocuments'],
  adminPrograms: ['AdminPrograms', 'AdminProgramDestinations'],
  adminDynforms: ['AdminDynforms', 'AdminDynformEditor'],
  adminWorkflows: ['AdminWorkflows', 'AdminWorkflowEditor'],
  adminDocuments: ['AdminDocuments', 'AdminDocumentTypeEdit'],
}

/**
 * Whether a sidebar nav item should be considered active for the given route name.
 * @param {{ key?: string, to?: { name?: string } }} item
 * @param {string | symbol | null | undefined} routeName
 */
export function navItemMatchesRoute(item, routeName) {
  if (!routeName || typeof routeName !== 'string') return false
  if (item?.to?.name === routeName) return true
  const family = item?.key ? NAV_ROUTE_FAMILIES[item.key] : null
  return Array.isArray(family) && family.includes(routeName)
}
