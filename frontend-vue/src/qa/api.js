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

export function listDemoAccounts() {
  return api.get('/api/qa/demo-accounts/')
}

export function demoLogin(userId) {
  return api.post('/api/qa/demo-login/', { user_id: userId })
}

export function demoReturn(refresh) {
  return api.post('/api/qa/demo-login/return/', refresh ? { refresh } : {})
}

export function searchUsersToImpersonate(q) {
  return api.get('/api/qa/impersonate/search/', { params: { q } })
}

export function impersonate(userId, reason = '') {
  return api.post('/api/qa/impersonate/', { user_id: userId, reason })
}

export function listOutbox(params = {}) {
  return api.get('/api/qa/outbox/', { params })
}

export function getOutboxMessage(id) {
  return api.get(`/api/qa/outbox/${id}/`)
}

export function getFlags() {
  return api.get('/api/qa/flags/')
}

export function resetDemoData() {
  return api.post('/api/qa/reset-demo/', { confirm: 'RESET' })
}

export function verifyIssue(id, result, comment = '') {
  return api.post(`/api/qa/issues/${id}/verify/`, { result, comment })
}

export function listTriagers() {
  return api.get('/api/qa/triagers/')
}

export function listScenarios(params = {}) {
  return api.get('/api/qa/scenarios/', { params })
}

export function saveScenarioResult(id, payload) {
  return api.post(`/api/qa/scenarios/${id}/result/`, payload)
}

export function clearScenarioResult(id) {
  return api.delete(`/api/qa/scenarios/${id}/result/`)
}

export function getScenarioMatrix(params = {}) {
  return api.get('/api/qa/scenarios/matrix/', { params })
}
