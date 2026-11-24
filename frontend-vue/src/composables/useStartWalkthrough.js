import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useProductTour } from '@/composables/useProductTour'
import {
  DASHBOARD_PAGE_ID,
  clearTourCompletion,
  isPageTourAllowed,
  resolvePageTourFromHelp,
  resolvePageTourFromRoute,
  resolveTourRole,
  routeForPageTour,
  tourIdForPage,
  tourStorageUserKey,
} from '@/utils/tourDefinitions'

/**
 * Navigate (if needed) and start a page/role walkthrough.
 */
export function useStartWalkthrough() {
  const router = useRouter()
  const route = useRoute()
  const authStore = useAuthStore()
  const { requestPageTour, openTour } = useProductTour()

  function currentRole() {
    return resolveTourRole(authStore)
  }

  function prepareTour(pageId, { force = true } = {}) {
    if (!authStore.isAuthenticated) return null
    const role = currentRole()
    if (!isPageTourAllowed(pageId, role)) return null
    const userKey = tourStorageUserKey(authStore.user)
    const tourId = tourIdForPage(pageId, role)
    if (userKey && force) clearTourCompletion(userKey, tourId)
    return { role, tourId, pageId, force }
  }

  /**
   * @param {string} pageId
   * @param {{ force?: boolean }} [options]
   */
  async function startWalkthrough(pageId, options = {}) {
    const prepared = prepareTour(pageId, options)
    if (!prepared) return false

    const dest = routeForPageTour(pageId)
    const alreadyOnPage = resolvePageTourFromRoute(route.name) === pageId
    // Dashboard/welcome tour targets live in the app shell — start in place.
    const shellTour = pageId === DASHBOARD_PAGE_ID

    if (!dest || alreadyOnPage || shellTour) {
      openTour(prepared)
      if (typeof window !== 'undefined') {
        window.dispatchEvent(
          new CustomEvent('seim-start-page-tour', {
            detail: { pageId, force: prepared.force },
          }),
        )
      }
      return true
    }

    requestPageTour(pageId, { force: prepared.force })
    await router.push(dest)
    return true
  }

  /**
   * @param {{ contextual_keys?: string[]|string, topic?: string }|null|undefined} article
   */
  async function startWalkthroughForArticle(article) {
    const pageId = resolvePageTourFromHelp(article, currentRole())
    if (!pageId) return false
    return startWalkthrough(pageId, { force: true })
  }

  function startPageTourForCurrentRoute({ force = true } = {}) {
    const pageId = resolvePageTourFromRoute(route.name)
    if (!pageId) return Promise.resolve(false)
    return startWalkthrough(pageId, { force })
  }

  return {
    startWalkthrough,
    startWalkthroughForArticle,
    startPageTourForCurrentRoute,
    resolvePageTourFromHelp: (article) => resolvePageTourFromHelp(article, currentRole()),
    currentRole,
  }
}
