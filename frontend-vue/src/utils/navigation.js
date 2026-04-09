const SPA_BASE_PREFIX = '/seim'

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

  if (spaPath === '/' || spaPath === '/dashboard') {
    return { name: 'Dashboard' }
  }
  if (spaPath === '/login') {
    return { name: 'Login' }
  }
  if (
    spaPath === '/applications' ||
    spaPath === '/applications/new' ||
    spaPath === '/applications/create'
  ) {
    return {
      name: spaPath === '/applications' ? 'Applications' : 'ApplicationNew',
    }
  }
  if (spaPath === '/documents') {
    return { name: 'Documents' }
  }
  if (spaPath === '/notifications') {
    return { name: 'Notifications' }
  }
  if (spaPath === '/profile' || spaPath === '/settings') {
    return {
      name: spaPath === '/profile' ? 'Profile' : 'Settings',
    }
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
    path.startsWith('/seim/admin') ||
    /^https?:\/\//.test(url)
  )
}
