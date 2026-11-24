import { defineStore } from 'pinia'
import { ref } from 'vue'
import { DASHBOARD_PAGE_ID } from '@/utils/tourDefinitions'

export const useProductTourStore = defineStore('productTour', () => {
  const open = ref(false)
  const stepIndex = ref(0)
  const role = ref('student')
  const tourId = ref('')
  const pageId = ref(DASHBOARD_PAGE_ID)
  const force = ref(false)
  /** When set, ProductTour starts this page tour after the matching route mounts. */
  const pendingPageId = ref(null)

  function openTour({
    role: nextRole,
    tourId: nextTourId,
    pageId: nextPageId = DASHBOARD_PAGE_ID,
    force: nextForce = false,
  } = {}) {
    role.value = nextRole || 'student'
    tourId.value = nextTourId || ''
    pageId.value = nextPageId || DASHBOARD_PAGE_ID
    force.value = Boolean(nextForce)
    stepIndex.value = 0
    open.value = true
    pendingPageId.value = null
  }

  function requestPageTour(nextPageId, { force: nextForce = true } = {}) {
    pendingPageId.value = nextPageId || DASHBOARD_PAGE_ID
    force.value = Boolean(nextForce)
  }

  function clearPendingPageTour() {
    pendingPageId.value = null
  }

  function closeTour() {
    open.value = false
    stepIndex.value = 0
    force.value = false
  }

  function setStepIndex(index) {
    stepIndex.value = Math.max(0, index)
  }

  return {
    open,
    stepIndex,
    role,
    tourId,
    pageId,
    force,
    pendingPageId,
    openTour,
    requestPageTour,
    clearPendingPageTour,
    closeTour,
    setStepIndex,
  }
})
