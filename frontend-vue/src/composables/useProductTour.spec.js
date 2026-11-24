/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useProductTour } from './useProductTour'

describe('useProductTour', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('opens a tour and clears any pending page tour', () => {
    const tour = useProductTour()
    tour.requestPageTour('applications')
    expect(tour.pendingPageId.value).toBe('applications')

    tour.openTour({ role: 'coordinator', tourId: 'review-queue', pageId: 'review-queue', force: true })
    expect(tour.open.value).toBe(true)
    expect(tour.role.value).toBe('coordinator')
    expect(tour.tourId.value).toBe('review-queue')
    expect(tour.pageId.value).toBe('review-queue')
    expect(tour.force.value).toBe(true)
    expect(tour.stepIndex.value).toBe(0)
    expect(tour.pendingPageId.value).toBe(null)
  })

  it('tracks pending page tours and clears them', () => {
    const tour = useProductTour()
    tour.requestPageTour('documents', { force: false })
    expect(tour.pendingPageId.value).toBe('documents')
    expect(tour.force.value).toBe(false)
    tour.clearPendingPageTour()
    expect(tour.pendingPageId.value).toBe(null)
  })

  it('updates step index and closes the tour', () => {
    const tour = useProductTour()
    tour.openTour({ role: 'student', tourId: 'dashboard' })
    tour.setStepIndex(2)
    expect(tour.stepIndex.value).toBe(2)
    tour.closeTour()
    expect(tour.open.value).toBe(false)
    expect(tour.stepIndex.value).toBe(0)
    expect(tour.force.value).toBe(false)
  })
})
