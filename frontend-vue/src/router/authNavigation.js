/**
 * Auth + staff-only resolution for routes with meta.requiresAuth.
 * Used by the global beforeEach so cold restores via checkAuth() still honor meta.staffReviewQueue.
 *
 * @param {import('vue-router').RouteLocationNormalized} to
 * @param {{ isAuthenticated: boolean, accessToken: string | null, canUseStaffReviewQueue: boolean, checkAuth: () => Promise<void> }} authStore
 * @returns {Promise<'next' | 'login' | 'applications'>}
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
    return 'applications'
  }

  return 'next'
}
