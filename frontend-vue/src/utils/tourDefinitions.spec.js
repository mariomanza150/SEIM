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
  filterMountedSteps,
  isPageTourAllowed,
  isTourCompleted,
  isTourTargetMounted,
  markTourCompleted,
  pageToursForRole,
  resolvePageTourFromHelp,
  resolvePageTourFromRoute,
  resolveTourRole,
  tourIdForPage,
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
    document.body.innerHTML = ''
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

  it('builds role-specific dashboard steps', () => {
    const student = buildTourSteps(i18n.global.t, 'student')
    expect(student.some((s) => s.id === 'applications')).toBe(true)
    const admin = buildTourSteps(i18n.global.t, 'admin')
    expect(admin.some((s) => s.id === 'admin')).toBe(true)
    expect(admin.some((s) => s.id === 'review')).toBe(true)
  })

  it('includes version in tour id', () => {
    expect(tourIdForRole('staff')).toContain(String(TOUR_VERSION))
    expect(tourIdForPage('documents', 'student')).toContain('documents')
    expect(tourIdForPage('documents', 'student')).toContain(String(TOUR_VERSION))
  })

  it('filters page tours by role', () => {
    expect(pageToursForRole('student')).toContain('applications')
    expect(pageToursForRole('student')).not.toContain('review-queue')
    expect(pageToursForRole('partner')).toEqual(['partner-portal'])
    expect(isPageTourAllowed('admin-programs', 'admin')).toBe(true)
    expect(isPageTourAllowed('admin-programs', 'student')).toBe(false)
  })

  it('builds page-level steps with bilingual copy', () => {
    const apps = buildTourSteps(i18n.global.t, 'student', 'applications', {
      te: i18n.global.te,
    })
    expect(apps.map((s) => s.id)).toEqual(
      expect.arrayContaining(['header', 'actions', 'filters', 'list']),
    )
    expect(apps[0].title).toBeTruthy()
    expect(apps[0].title).not.toContain('tours.pages')

    setAppLocale('es')
    const appsEs = buildTourSteps(i18n.global.t, 'student', 'applications', {
      te: i18n.global.te,
    })
    expect(appsEs[0].title).toMatch(/Solicitudes/i)
  })

  it('returns empty page steps when role is not allowed', () => {
    expect(buildTourSteps(i18n.global.t, 'partner', 'review-queue')).toEqual([])
  })

  it('skips steps whose selectors are not mounted', () => {
    document.body.innerHTML = `
      <div data-tour="applications-header"></div>
      <div data-tour="applications-filters" style="width:10px;height:10px"></div>
    `
    const header = document.querySelector('[data-tour="applications-header"]')
    Object.defineProperty(header, 'getBoundingClientRect', {
      value: () => ({ width: 20, height: 20, top: 0, left: 0, bottom: 20, right: 20 }),
    })
    const filters = document.querySelector('[data-tour="applications-filters"]')
    Object.defineProperty(filters, 'getBoundingClientRect', {
      value: () => ({ width: 20, height: 20, top: 0, left: 0, bottom: 20, right: 20 }),
    })

    const raw = buildTourSteps(i18n.global.t, 'student', 'applications')
    const mounted = filterMountedSteps(raw)
    expect(mounted.map((s) => s.id)).toEqual(['header', 'filters'])
    expect(isTourTargetMounted('[data-tour="applications-new"]')).toBe(false)
  })

  it('maps help articles and routes to page tours', () => {
    expect(resolvePageTourFromRoute('CoordinatorReviewQueue')).toBe('review-queue')
    expect(resolvePageTourFromHelp({
      contextual_keys: ['PartnerPortal'],
      topic: 'partner',
    }, 'partner')).toBe('partner-portal')
    expect(resolvePageTourFromHelp({
      contextual_keys: ['Applications'],
      topic: 'applications',
    }, 'partner')).toBe('dashboard')
    expect(resolvePageTourFromHelp({
      topic: 'documents',
    }, 'student')).toBe('documents')
  })
})

describe('useProductTour', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    useProductTour().closeTour()
  })

  it('opens and advances steps', () => {
    const api = useProductTour()
    api.openTour({ role: 'student', tourId: 'welcome-student-v1', pageId: 'dashboard' })
    expect(api.open.value).toBe(true)
    expect(api.pageId.value).toBe('dashboard')
    expect(api.stepIndex.value).toBe(0)
    api.setStepIndex(2)
    expect(api.stepIndex.value).toBe(2)
    api.closeTour()
    expect(api.open.value).toBe(false)
  })

  it('stores a pending page tour for post-navigation start', () => {
    const api = useProductTour()
    api.requestPageTour('documents', { force: true })
    expect(api.pendingPageId.value).toBe('documents')
    api.clearPendingPageTour()
    expect(api.pendingPageId.value).toBe(null)
  })
})
