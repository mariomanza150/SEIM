/** Map check_eligibility `rules` rows to locale strings. */

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

export function eligibilityFailureMessages(data, t) {
  const rules = Array.isArray(data?.rules) ? data.rules : []
  const fromRules = rules
    .filter((r) => r && !r.passed && !r.skipped)
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
