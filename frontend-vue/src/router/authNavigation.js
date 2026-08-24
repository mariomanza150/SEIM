/**
 * Auth + staff-only resolution for routes with meta.requiresAuth.
 * Used by the global beforeEach so cold restores via checkAuth() still honor meta.staffReviewQueue.
 *
 * @param {import('vue-router').RouteLocationNormalized} to
 * @param {{ isAuthenticated: boolean, accessToken: string | null, canUseStaffReviewQueue: boolean, checkAuth: () => Promise<void> }} authStore
 * @returns {Promise<'next' | 'login' | 'applications' | 'partner' | 'dashboard' | 'reviewQueue'>}
 */
export async function resolveAuthenticatedNavigation(to, authStore) {
  if (!authStore.isAuthenticated) {
    if (authStore.accessToken) {
      try {
        await authStore.checkAuth()
      } catch {
        return 'login'
      }
    }
    if (!authStore.isAuthenticated) {
      return 'login'
    }
  }

  if (to.meta.staffReviewQueue && !authStore.canUseStaffReviewQueue) {
    if (authStore.canUsePartnerPortal) return 'partner'
    return 'applications'
  }

  if (to.meta.partnerPortal && !authStore.canUsePartnerPortal) {
    if (authStore.canUseStaffReviewQueue) return 'reviewQueue'
    return 'applications'
  }

  if (
    authStore.canUsePartnerPortal
    && (to.matched?.some(
      (r) => r.meta && (r.meta.studentApplications || r.meta.studentDocuments),
    ) ?? false)
  ) {
    return 'partner'
  }

  // Admin-only routes (SPA admin console)
  if (to.meta.adminOnly && !authStore.isAdmin) {
    if (authStore.canUsePartnerPortal) return 'partner'
    if (authStore.canUseStaffReviewQueue) return 'dashboard'
    return 'applications'
  }

  return 'next'
}
