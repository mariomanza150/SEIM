import { STAFF_SAVED_SEARCH_TYPE } from '@/utils/staffListSearchPresets'

/** Saved-search `search_type` for coordinator review queue filters. */
export const REVIEW_QUEUE_SEARCH_TYPE = STAFF_SAVED_SEARCH_TYPE.APPLICATION_REVIEW_QUEUE

const DEFAULT_ORDERING = '-submitted_at'

/**
 * Build JSON `filters` payload for POST /api/saved-searches/ (review queue).
 */
export function serializeReviewQueueFilters(state) {
  return {
    search: state.search || '',
    status: state.status || '',
    ordering: state.ordering || DEFAULT_ORDERING,
    pending_review: Boolean(state.pending_review),
    needs_document_resubmit: Boolean(state.needs_document_resubmit),
    assigned_to_me: Boolean(state.assigned_to_me),
  }
}

/**
 * Map stored filters onto the review queue `filters` ref shape (legacy keys tolerated).
 */
export function deserializeReviewQueueFilters(raw) {
  const f = raw && typeof raw === 'object' ? raw : {}
  return {
    search: f.search ?? '',
    status: f.status || f.status_name || '',
    ordering: f.ordering || DEFAULT_ORDERING,
    pending_review: Boolean(f.pending_review),
    needs_document_resubmit: Boolean(f.needs_document_resubmit),
    assigned_to_me: Boolean(f.assigned_to_me),
  }
}
