const SPA_BASE_PREFIX = '/seim'

const EXACT_SPA_ROUTES = {
  '/': { name: 'Dashboard' },
  '/dashboard': { name: 'Dashboard' },
  '/admin-dashboard': { name: 'Dashboard' },
  '/login': { name: 'Login' },
  '/register': { name: 'Register' },
  '/verify-email': { name: 'VerifyEmail' },
  '/password-reset': { name: 'PasswordReset' },
  '/applications': { name: 'Applications' },
  '/applications/new': { name: 'ApplicationNew' },
  '/applications/create': { name: 'ApplicationNew' },
  '/documents': { name: 'Documents' },
  '/notifications': { name: 'Notifications' },
  '/profile': { name: 'Profile' },
  '/settings': { name: 'Settings' },
  '/preferences': { name: 'Settings' },
  '/calendar': { name: 'DeadlinesCalendar' },
  '/review-queue': { name: 'CoordinatorReviewQueue' },
  '/coordinator-workload': { name: 'CoordinatorWorkload' },
  '/workload': { name: 'CoordinatorWorkload' },
  '/notification-routing': { name: 'NotificationRouting' },
  '/exchange-agreements': { name: 'StaffExchangeAgreements' },
  '/agreement-documents': { name: 'StaffExchangeAgreements' },
  '/exchange': { name: 'StaffExchangeAgreements' },
  '/programs/compare': { name: 'ProgramCompare' },
  '/programs': { name: 'ProgramCompare' },
  '/eligibility-rulesets': { name: 'EligibilityRulesets' },
  '/nominations': { name: 'Nominations' },
  '/analytics-forecasts': { name: 'AnalyticsForecasts' },
  '/analytics': { name: 'AnalyticsForecasts' },
  '/partner': { name: 'PartnerPortal' },
  '/admin': { name: 'AdminPrograms' },
  '/admin/programs': { name: 'AdminPrograms' },
  '/admin/forms': { name: 'AdminForms' },
  '/admin/dynforms': { name: 'AdminDynforms' },
  '/admin/data-management': { name: 'AdminDataManagement' },
  '/admin/workflows': { name: 'AdminWorkflows' },
  '/admin/documents': { name: 'AdminDocuments' },
  '/grades': { name: 'Profile' },
}

function stripTrailingSlash(path) {
  if (!path || path === '/') return '/'
  return path.endsWith('/') ? path.slice(0, -1) : path
}

function normalizePath(url) {
  if (!url) return null

  try {
    const parsed = new URL(url, window.location.origin)
    return stripTrailingSlash(parsed.pathname)
  } catch {
    return stripTrailingSlash(url)
  }
}

export function normalizeSpaLocation(url) {
  const path = normalizePath(url)
  if (!path) return null

  const spaPath = path.startsWith(SPA_BASE_PREFIX) ? path.slice(SPA_BASE_PREFIX.length) || '/' : path

  if (EXACT_SPA_ROUTES[spaPath]) {
    return { ...EXACT_SPA_ROUTES[spaPath] }
  }

  const applicationEditMatch = spaPath.match(/^\/applications\/([^/]+)\/edit$/)
  if (applicationEditMatch) {
    return { name: 'ApplicationEdit', params: { id: applicationEditMatch[1] } }
  }

  const applicationDetailMatch = spaPath.match(/^\/applications\/([^/]+)$/)
  if (applicationDetailMatch) {
    return { name: 'ApplicationDetail', params: { id: applicationDetailMatch[1] } }
  }

  const documentDetailMatch = spaPath.match(/^\/documents\/([^/]+)$/)
  if (documentDetailMatch) {
    return { name: 'DocumentDetail', params: { id: documentDetailMatch[1] } }
  }

  const agreementRepositoryMatch = spaPath.match(/^\/exchange-agreements\/([^/]+)\/documents$/)
  if (agreementRepositoryMatch) {
    return {
      name: 'StaffAgreementDocuments',
      params: { agreementId: agreementRepositoryMatch[1] },
    }
  }

  const dynformEditorMatch = spaPath.match(/^\/admin\/dynforms\/([^/]+)$/)
  if (dynformEditorMatch) {
    return { name: 'AdminDynformEditor', params: { id: dynformEditorMatch[1] } }
  }

  const destinationsMatch = spaPath.match(/^\/admin\/programs\/([^/]+)\/destinations$/)
  if (destinationsMatch) {
    return { name: 'AdminProgramDestinations', params: { id: destinationsMatch[1] } }
  }

  const workflowEditorMatch = spaPath.match(/^\/admin\/workflows\/([^/]+)$/)
  if (workflowEditorMatch) {
    return { name: 'AdminWorkflowEditor', params: { id: workflowEditorMatch[1] } }
  }

  const documentTypeEditorMatch = spaPath.match(/^\/admin\/documents\/([^/]+)$/)
  if (documentTypeEditorMatch) {
    return { name: 'AdminDocumentTypeEdit', params: { id: documentTypeEditorMatch[1] } }
  }

  const adminApplicationMatch = spaPath.match(/^\/admin\/applications\/([^/]+)$/)
  if (adminApplicationMatch) {
    return { name: 'AdminApplicationEdit', params: { id: adminApplicationMatch[1] } }
  }

  return null
}

export function isSpaUrl(url) {
  return normalizeSpaLocation(url) !== null
}

export function isNewTabUrl(url) {
  const path = normalizePath(url)
  if (!path) return false

  return (
    path.startsWith('/cms') ||
    path.startsWith('/seim/django-admin') ||
    /^https?:\/\//.test(url)
  )
}
