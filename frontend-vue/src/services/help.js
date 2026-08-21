import api from '@/services/api'

export function unwrapHelpArticles(data) {
  if (Array.isArray(data)) return data
  if (Array.isArray(data?.results)) return data.results
  return []
}

export function fetchHelpArticles(params = {}) {
  const query = { page_size: params.page_size ?? 100 }
  if (params.q) query.q = params.q
  if (params.key) query.key = params.key
  if (params.topic) query.topic = params.topic
  return api.get('/api/help/articles/', { params: query })
}

export function fetchHelpArticle(slug) {
  return api.get(`/api/help/articles/${encodeURIComponent(slug)}/`)
}
