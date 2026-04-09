import { isSpaUrl, normalizeSpaLocation } from '@/utils/navigation'

export function normalizePaginated(data) {
  if (!data) return []
  if (Array.isArray(data)) return data
  if (Array.isArray(data.results)) return data.results
  return []
}

function ts(value) {
  if (!value) return 0
  const n = new Date(value).getTime()
  return Number.isFinite(n) ? n : 0
}

/**
 * Build prioritized dashboard rows from parallel API payloads.
 * @param {object} params
 * @param {object[]} params.notifications
 * @param {object[]} params.drafts
 * @param {object[]} params.documents
 * @param {object[]} params.assignedPending
 * @param {object[]} params.pendingReview
 * @param {object[]} params.resubmitApps
 * @param {boolean} params.isStudent
 * @param {boolean} params.isStaff
 */
export function mergeDashboardNextSteps({
  notifications = [],
  drafts = [],
  documents = [],
  assignedPending = [],
  pendingReview = [],
  resubmitApps = [],
  isStudent,
  isStaff,
}) {
  const rows = []

  for (const n of notifications) {
    const actionUrl = n.action_url || null
    const spa = actionUrl && isSpaUrl(actionUrl) ? normalizeSpaLocation(actionUrl) : null
    rows.push({
      id: `n-${n.id}`,
      kind: 'notification',
      title: n.title || 'Notification',
      subtitle: (n.message || '').slice(0, 120),
      spaRoute: spa,
      href: actionUrl && !spa ? actionUrl : null,
      sort: 1000_000_000_000 - ts(n.sent_at),
    })
  }

  if (isStudent) {
    for (const d of drafts) {
      const program = d.program_name || 'Program'
      rows.push({
        id: `draft-${d.id}`,
        kind: 'draft',
        title: 'Finish draft application',
        subtitle: program,
        spaRoute: { name: 'ApplicationEdit', params: { id: d.id } },
        href: null,
        sort: 2000_000_000_000 - ts(d.created_at),
      })
    }

    for (const doc of documents) {
      const open = (doc.resubmission_requests || []).some((r) => r.resolved === false)
      if (!open) continue
      rows.push({
        id: `doc-${doc.id}`,
        kind: 'document_resubmit',
        title: 'Document resubmission requested',
        subtitle: 'Upload a new version from the document page',
        spaRoute: { name: 'DocumentDetail', params: { id: doc.id } },
        href: null,
        sort: 3000_000_000_000 - ts(doc.updated_at || doc.created_at),
      })
    }
  }

  if (isStaff) {
    const assignedIds = new Set(assignedPending.map((a) => a.id))

    for (const a of assignedPending) {
      const who = a.student_display_name || a.student_email || 'Student'
      const prog = a.program_name || 'Program'
      rows.push({
        id: `rv-a-${a.id}`,
        kind: 'review_assigned',
        title: 'Review assigned application',
        subtitle: `${who} · ${prog}`,
        spaRoute: { name: 'ApplicationDetail', params: { id: a.id } },
        href: null,
        sort: 3000_000_000_000 - ts(a.submitted_at || a.created_at),
      })
    }

    for (const a of pendingReview) {
      if (assignedIds.has(a.id)) continue
      const who = a.student_display_name || a.student_email || 'Student'
      const prog = a.program_name || 'Program'
      rows.push({
        id: `rv-${a.id}`,
        kind: 'review',
        title: 'Application awaiting review',
        subtitle: `${who} · ${prog}`,
        spaRoute: { name: 'ApplicationDetail', params: { id: a.id } },
        href: null,
        sort: 4000_000_000_000 - ts(a.submitted_at || a.created_at),
      })
    }

    for (const a of resubmitApps) {
      const who = a.student_display_name || a.student_email || 'Student'
      const prog = a.program_name || 'Program'
      rows.push({
        id: `rs-${a.id}`,
        kind: 'resubmit_queue',
        title: 'Open document resubmission',
        subtitle: `${who} · ${prog}`,
        spaRoute: { name: 'ApplicationDetail', params: { id: a.id } },
        href: null,
        sort: 5000_000_000_000 - ts(a.submitted_at || a.created_at),
      })
    }
  }

  rows.sort((x, y) => x.sort - y.sort)
  return rows.slice(0, 14)
}

export async function fetchDashboardNextSteps(api, { userRole, canUseStaffReviewQueue }) {
  const isStudent = userRole === 'student'
  const isStaff = Boolean(canUseStaffReviewQueue)

  const requests = [
    api
      .get('/api/notifications/', {
        params: { is_read: false, page_size: 8, ordering: '-sent_at' },
      })
      .then((r) => normalizePaginated(r.data))
      .catch(() => []),
  ]

  if (isStudent) {
    requests.push(
      api
        .get('/api/applications/', {
          params: { status: 'draft', page_size: 10, ordering: '-created_at' },
        })
        .then((r) => normalizePaginated(r.data))
        .catch(() => []),
      api
        .get('/api/documents/', { params: { page_size: 50, ordering: '-created_at' } })
        .then((r) => normalizePaginated(r.data))
        .catch(() => []),
    )
  }

  if (isStaff) {
    requests.push(
      api
        .get('/api/applications/', {
          params: {
            assigned_to_me: true,
            pending_review: true,
            page_size: 8,
            ordering: '-submitted_at',
          },
        })
        .then((r) => normalizePaginated(r.data))
        .catch(() => []),
      api
        .get('/api/applications/', {
          params: { pending_review: true, page_size: 8, ordering: '-submitted_at' },
        })
        .then((r) => normalizePaginated(r.data))
        .catch(() => []),
      api
        .get('/api/applications/', {
          params: {
            needs_document_resubmit: true,
            page_size: 8,
            ordering: '-submitted_at',
          },
        })
        .then((r) => normalizePaginated(r.data))
        .catch(() => []),
    )
  }

  const results = await Promise.all(requests)

  if (isStudent) {
    const [notif, draftList, docList] = results
    return mergeDashboardNextSteps({
      notifications: notif,
      drafts: draftList,
      documents: docList,
      isStudent: true,
      isStaff: false,
    })
  }

  if (isStaff) {
    const [notif, assignedPending, pendingReview, resubmitApps] = results
    return mergeDashboardNextSteps({
      notifications: notif,
      assignedPending,
      pendingReview,
      resubmitApps,
      isStudent: false,
      isStaff: true,
    })
  }

  const [notif] = results
  return mergeDashboardNextSteps({
    notifications: notif,
    isStudent: false,
    isStaff: false,
  })
}
