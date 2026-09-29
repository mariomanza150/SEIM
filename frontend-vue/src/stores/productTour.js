import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useProductTourStore = defineStore('productTour', () => {
  const open = ref(false)
  const stepIndex = ref(0)
  const role = ref('student')
  const tourId = ref('')
  const force = ref(false)

  function openTour({ role: nextRole, tourId: nextTourId, force: nextForce = false } = {}) {
    role.value = nextRole || 'student'
    tourId.value = nextTourId || ''
    force.value = Boolean(nextForce)
    stepIndex.value = 0
    open.value = true
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
    force,
    openTour,
    closeTour,
    setStepIndex,
  }
})
