/** Map check_eligibility `rules` rows to locale strings and actionable fix items. */

const RULE_ORDER = [
  'application_window',
  'min_semester',
  'min_credits',
  'gpa',
  'required_language',
  'language_proficiency',
  'toefl',
  'age',
  'profile',
  'required_documents',
  'dynamic_form',
]

const ACTION_BY_RULE_ID = {
  application_window: null,
  min_semester: 'profile',
  min_credits: 'profile',
  gpa: 'profile',
  required_language: 'profile',
  language_proficiency: 'profile',
  toefl: 'profile',
  age: 'profile',
  profile: 'profile',
  required_documents: 'documents',
  dynamic_form: 'form',
}

export function formatEligibilityRuleMessage(rule, t) {
  if (!rule || typeof rule !== 'object') return ''
  const key = rule.message_key
  if (key) {
    const i18nKey = `eligibilityRules.${key}`
    const params = rule.message_params || {}
    const translated = t(i18nKey, params)
    if (translated && translated !== i18nKey) return translated
  }
  return typeof rule.message === 'string' ? rule.message : ''
}

function failedRules(data) {
  const rules = Array.isArray(data?.rules) ? data.rules : []
  return rules.filter((r) => r && !r.passed && !r.skipped)
}

function inferActionFromKeyOrText(messageKey, text) {
  const key = String(messageKey || '').toLowerCase()
  const blob = `${key} ${text || ''}`.toLowerCase()
  if (key.startsWith('documents_') || blob.includes('document')) return 'documents'
  if (key.startsWith('dynamic_form') || blob.includes('application form')) return 'form'
  if (
    key.startsWith('gpa_')
    || key.startsWith('language_')
    || key.startsWith('semester_')
    || key.startsWith('credits_')
    || key.startsWith('age_')
    || key === 'profile_missing'
    || blob.includes('gpa')
    || blob.includes('language')
    || blob.includes('semester')
    || blob.includes('credit')
    || blob.includes('profile')
  ) {
    return 'profile'
  }
  return null
}

export function eligibilityFailureMessages(data, t) {
  const fromRules = failedRules(data)
    .map((r) => formatEligibilityRuleMessage(r, t))
    .filter(Boolean)
  if (fromRules.length) return fromRules
  const message = data?.message
  if (!message || typeof message !== 'string') return []
  const trimmed = message.trim()
  if (!trimmed) return []
  if (trimmed.includes('\n- ')) {
    const parts = trimmed.split('\n- ').map((s) => s.trim()).filter(Boolean)
    const prefix = 'Eligibility requirements not met:'
    if (parts[0]?.startsWith(prefix)) {
      const rest = parts[0].slice(prefix.length).trim()
      if (rest) parts[0] = rest
      else parts.shift()
    }
    return parts
  }
  return [trimmed]
}

/** Ordered, actionable gaps from preview / readiness.eligibility payloads. */
export function eligibilityFixItems(data, t) {
  const failed = failedRules(data).slice().sort((a, b) => {
    const ia = RULE_ORDER.indexOf(a.id)
    const ib = RULE_ORDER.indexOf(b.id)
    return (ia < 0 ? 99 : ia) - (ib < 0 ? 99 : ib)
  })
  if (failed.length) {
    return failed.map((rule, index) => {
      const message = formatEligibilityRuleMessage(rule, t)
      const action = Object.prototype.hasOwnProperty.call(ACTION_BY_RULE_ID, rule.id)
        ? ACTION_BY_RULE_ID[rule.id]
        : inferActionFromKeyOrText(rule.message_key, message)
      return {
        key: rule.id || String(index),
        message,
        action,
      }
    }).filter((item) => item.message)
  }
  const fromMessage = eligibilityFailureMessages(data, t)
  if (fromMessage.length) {
    return fromMessage.map((message, index) => ({
      key: String(index),
      message,
      action: inferActionFromKeyOrText(null, message),
    }))
  }
  const issues = Array.isArray(data?.issues) ? data.issues.filter(Boolean) : []
  return issues.map((message, index) => ({
    key: String(index),
    message: String(message),
    action: inferActionFromKeyOrText(null, String(message)),
  }))
}

export function eligibilityFixLink(action, { applicationId, nextPath } = {}) {
  if (action === 'profile') {
    return { name: 'Profile', query: nextPath ? { next: nextPath } : undefined }
  }
  if (action === 'documents') {
    if (applicationId) {
      return { name: 'ApplicationDetail', params: { id: applicationId }, hash: '#document-upload' }
    }
    return { name: 'Documents' }
  }
  if (action === 'form' && applicationId) {
    return { name: 'ApplicationEdit', params: { id: applicationId } }
  }
  return null
}

export function eligibilityFixActionKey(action) {
  if (action === 'profile') return 'eligibilityFix.openProfile'
  if (action === 'documents') return 'eligibilityFix.uploadDocuments'
  if (action === 'form') return 'eligibilityFix.completeForm'
  return ''
}
