import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mergeDashboardNextSteps, normalizePaginated, fetchDashboardNextSteps } from './dashboardNextSteps'
import i18n, { setAppLocale } from '@/i18n'

describe('normalizePaginated', () => {
  it('handles DRF page shape', () => {
    expect(normalizePaginated({ results: [{ id: 1 }], count: 1 })).toEqual([{ id: 1 }])
  })
  it('handles bare array', () => {
    expect(normalizePaginated([{ id: 2 }])).toEqual([{ id: 2 }])
  })
})

describe('mergeDashboardNextSteps', () => {
  const t = (key, params) => i18n.global.t(key, params)

  beforeEach(() => {
    setAppLocale('en')
  })

  afterEach(() => {
    setAppLocale('en')
  })

  it('prioritizes notifications and dedupes assigned from pending review', () => {
    const rows = mergeDashboardNextSteps({
      notifications: [{ id: 'a', title: 'N1', message: 'm', sent_at: '2026-01-02T00:00:00Z', action_url: null }],
      assignedPending: [
        {
          id: 'app1',
          student_display_name: 'Sam',
          program_name: 'P1',
          created_at: '2026-01-01T00:00:00Z',
        },
      ],
      pendingReview: [
        {
          id: 'app1',
          student_display_name: 'Sam',
          program_name: 'P1',
          submitted_at: '2026-01-01T00:00:00Z',
        },
        {
          id: 'app2',
          student_display_name: 'Jo',
          program_name: 'P2',
          submitted_at: '2026-01-01T00:00:00Z',
        },
      ],
      resubmitApps: [],
      isStudent: false,
      isStaff: true,
      t,
    })
    const kinds = rows.map((r) => r.kind)
    expect(kinds[0]).toBe('notification')
    expect(kinds.filter((k) => k === 'review')).toHaveLength(1)
    expect(rows.some((r) => r.id === 'rv-app2')).toBe(true)
  })

  it('includes student drafts and open resubmissions', () => {
    const rows = mergeDashboardNextSteps({
      notifications: [],
      drafts: [{ id: 'd1', program_name: 'Spain', created_at: '2026-01-01T00:00:00Z' }],
      documents: [
        {
          id: 'doc1',
          created_at: '2026-01-01T00:00:00Z',
          resubmission_requests: [{ resolved: false }],
        },
      ],
      isStudent: true,
      isStaff: false,
      t,
    })
    expect(rows.some((r) => r.kind === 'draft')).toBe(true)
    expect(rows.some((r) => r.kind === 'document_resubmit')).toBe(true)
  })

  it('uses Spanish copy when locale is es', () => {
    setAppLocale('es')
    const rows = mergeDashboardNextSteps({
      notifications: [],
      drafts: [{ id: 'd1', program_name: 'España', created_at: '2026-01-01T00:00:00Z' }],
      documents: [],
      isStudent: true,
      isStaff: false,
      t,
    })
    const draft = rows.find((r) => r.kind === 'draft')
    expect(draft.title).toBe('Terminar borrador de solicitud')
    expect(draft.subtitle).toBe('España')
  })

  it('throws without translate function', () => {
    expect(() =>
      mergeDashboardNextSteps({
        notifications: [],
        isStudent: false,
        isStaff: false,
      }),
    ).toThrow(/t \(i18n translate\) is required/)
  })
})

describe('fetchDashboardNextSteps', () => {
  const t = (key, params) => i18n.global.t(key, params)

  it('loads notifications only for non-student non-staff', async () => {
    const api = {
      get: vi.fn().mockResolvedValue({ data: { results: [{ id: 1, sent_at: '2026-01-01T00:00:00Z' }] } }),
    }
    const rows = await fetchDashboardNextSteps(api, { userRole: null, canUseStaffReviewQueue: false, t })
    expect(api.get).toHaveBeenCalledTimes(1)
    expect(rows.length).toBeGreaterThan(0)
  })
})
