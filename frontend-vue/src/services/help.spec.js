/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { unwrapHelpArticles, fetchHelpArticles, fetchHelpArticle } from './help'
import api from '@/services/api'

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
  },
}))

describe('help service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('unwrapHelpArticles returns arrays as-is', () => {
    const rows = [{ slug: 'getting-started', title: 'Getting started' }]
    expect(unwrapHelpArticles(rows)).toEqual(rows)
  })

  it('unwrapHelpArticles unwraps paginated results', () => {
    const rows = [{ slug: 'uploads', title: 'Uploading files' }]
    expect(unwrapHelpArticles({ results: rows, count: 1 })).toEqual(rows)
  })

  it('unwrapHelpArticles returns empty list for unexpected payloads', () => {
    expect(unwrapHelpArticles(null)).toEqual([])
    expect(unwrapHelpArticles({})).toEqual([])
    expect(unwrapHelpArticles({ results: null })).toEqual([])
  })

  it('fetchHelpArticles applies default page size and optional filters', async () => {
    api.get.mockResolvedValue({ data: { results: [] } })
    await fetchHelpArticles({ q: 'upload', key: 'Documents', topic: 'documents' })
    expect(api.get).toHaveBeenCalledWith('/api/help/articles/', {
      params: {
        page_size: 100,
        q: 'upload',
        key: 'Documents',
        topic: 'documents',
      },
    })
  })

  it('fetchHelpArticles allows overriding page_size', async () => {
    api.get.mockResolvedValue({ data: { results: [] } })
    await fetchHelpArticles({ page_size: 25 })
    expect(api.get).toHaveBeenCalledWith('/api/help/articles/', {
      params: { page_size: 25 },
    })
  })

  it('fetchHelpArticle encodes the slug path segment', async () => {
    api.get.mockResolvedValue({ data: { slug: 'a/b' } })
    await fetchHelpArticle('start application')
    expect(api.get).toHaveBeenCalledWith('/api/help/articles/start%20application/')
  })
})
