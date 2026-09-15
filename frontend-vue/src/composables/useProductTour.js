import { storeToRefs } from 'pinia'
import { useProductTourStore } from '@/stores/productTour'

/**
 * Shared API for product tour. Pinia keeps a single state instance across
 * lazy-loaded route chunks (e.g. Settings → open, ProductTour in App.vue → render).
 */
export function useProductTour() {
  const store = useProductTourStore()
  const { open, stepIndex, role, tourId, force } = storeToRefs(store)

  return {
    open,
    stepIndex,
    role,
    tourId,
    force,
    openTour: store.openTour,
    closeTour: store.closeTour,
    setStepIndex: store.setStepIndex,
  }
}
