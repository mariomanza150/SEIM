import { describe, it, expect } from 'vitest'
import {
  deserializeReviewQueueFilters,
  serializeReviewQueueFilters,
} from './reviewQueuePresets'

describe('reviewQueuePresets', () => {
  it('serializes booleans and strings', () => {
    expect(
      serializeReviewQueueFilters({
        search: 'a',
        status: 'submitted',
        ordering: '-created_at',
        pending_review: true,
        needs_document_resubmit: false,
        assigned_to_me: 1,
      }),
    ).toEqual({
      search: 'a',
      status: 'submitted',
      ordering: '-created_at',
      pending_review: true,
      needs_document_resubmit: false,
      assigned_to_me: true,
    })
  })

  it('maps legacy status_name', () => {
    expect(deserializeReviewQueueFilters({ status_name: 'under_review' }).status).toBe('under_review')
  })
})
