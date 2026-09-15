/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import i18n, { setAppLocale } from '@/i18n'
import {
  TOUR_VERSION,
  buildTourSteps,
  clearTourCompletion,
  isTourCompleted,
  markTourCompleted,
  resolveTourRole,
  tourIdForRole,
  tourStorageUserKey,
} from '@/utils/tourDefinitions'
import { useProductTour } from '@/composables/useProductTour'

describe('tourDefinitions', () => {
  beforeEach(() => {
    setAppLocale('en')
    localStorage.clear()
    setActivePinia(createPinia())
    useProductTour().closeTour()
  })

  it('resolves role from auth flags', () => {
    expect(resolveTourRole({ isAdmin: true })).toBe('admin')
    expect(resolveTourRole({ canUsePartnerPortal: true })).toBe('partner')
    expect(resolveTourRole({ canUseStaffReviewQueue: true })).toBe('staff')
    expect(resolveTourRole({})).toBe('student')
  })

  it('persists completion and clears on replay', () => {
    const tourId = tourIdForRole('student')
    expect(isTourCompleted(7, tourId)).toBe(false)
    markTourCompleted(7, tourId)
    expect(isTourCompleted(7, tourId)).toBe(true)
    clearTourCompletion(7, tourId)
    expect(isTourCompleted(7, tourId)).toBe(false)
  })

  it('falls back to email when user id is missing', () => {
    expect(tourStorageUserKey({ email: 'A@Test.com' })).toBe('a@test.com')
    expect(tourStorageUserKey({ id: 9, email: 'a@test.com' })).toBe('9')
  })

  it('builds role-specific steps', () => {
    const student = buildTourSteps(i18n.global.t, 'student')
    expect(student.some((s) => s.id === 'applications')).toBe(true)
    const admin = buildTourSteps(i18n.global.t, 'admin')
    expect(admin.some((s) => s.id === 'admin')).toBe(true)
    expect(admin.some((s) => s.id === 'review')).toBe(true)
  })

  it('includes version in tour id', () => {
    expect(tourIdForRole('staff')).toContain(String(TOUR_VERSION))
  })
})

describe('useProductTour', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    useProductTour().closeTour()
  })

  it('opens and advances steps', () => {
    const api = useProductTour()
    api.openTour({ role: 'student', tourId: 'welcome-student-v1' })
    expect(api.open.value).toBe(true)
    expect(api.stepIndex.value).toBe(0)
    api.setStepIndex(2)
    expect(api.stepIndex.value).toBe(2)
    api.closeTour()
    expect(api.open.value).toBe(false)
  })
})
