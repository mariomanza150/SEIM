import api from '@/services/api'

export function createIssue(formData) {
  return api.post('/api/qa/issues/', formData)
}

export function listIssues(params = {}) {
  return api.get('/api/qa/issues/', { params })
}

export function getIssue(id) {
  return api.get(`/api/qa/issues/${id}/`)
}

export function updateIssue(id, payload) {
  return api.patch(`/api/qa/issues/${id}/`, payload)
}

export function addComment(id, body, isInternal = false) {
  return api.post(`/api/qa/issues/${id}/comments/`, { body, is_internal: isInternal })
}

export function addAttachments(id, files) {
  const fd = new FormData()
  for (const f of files) fd.append('files', f)
  return api.post(`/api/qa/issues/${id}/attachments/`, fd)
}

/** Fetch an attachment with the JWT and return an object URL (caller revokes). */
export async function attachmentObjectUrl(downloadUrl) {
  const { data } = await api.get(downloadUrl, { responseType: 'blob' })
  return URL.createObjectURL(data)
}
