import { describe, it, expect, beforeEach } from 'vitest'
import {
  setReviewQueueNav,
  getReviewQueueNav,
  clearReviewQueueNav,
  syncReviewQueueNavIndex,
} from './reviewQueueNav'

describe('reviewQueueNav', () => {
  beforeEach(() => {
    sessionStorage.clear()
  })

  it('stores and resolves prev/next for the current id', () => {
    setReviewQueueNav([11, 22, 33], 22)
    expect(getReviewQueueNav(22)).toEqual({
      ids: ['11', '22', '33'],
      index: 1,
      prevId: '11',
      nextId: '33',
    })
  })

  it('returns null when current id is not in the stored queue', () => {
    setReviewQueueNav([11, 22], 11)
    expect(getReviewQueueNav(99)).toBeNull()
  })

  it('clears storage', () => {
    setReviewQueueNav([1, 2], 1)
    clearReviewQueueNav()
    expect(getReviewQueueNav(1)).toBeNull()
  })

  it('syncs index when moving within the queue', () => {
    setReviewQueueNav([11, 22, 33], 11)
    const next = syncReviewQueueNavIndex(33)
    expect(next).toMatchObject({ index: 2, prevId: '22', nextId: null })
  })
})
