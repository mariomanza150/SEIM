/**
 * @vitest-environment jsdom
 */
import { describe, it, expect } from 'vitest'
import { eligibilityFailureMessages, formatEligibilityRuleMessage } from './eligibilityMessages'

describe('eligibilityMessages', () => {
  const t = (key, params = {}) => {
    if (key === 'eligibilityRules.language_unmet') {
      return `Need ${params.required}, have ${params.student}`
    }
    return key
  }

  it('prefers message_key over English message', () => {
    const text = formatEligibilityRuleMessage(
      {
        id: 'required_language',
        passed: false,
        skipped: false,
        message: 'Language requirement not met. Required: German, Your language: English',
        message_key: 'language_unmet',
        message_params: { required: 'German', student: 'English' },
      },
      t,
    )
    expect(text).toBe('Need German, have English')
  })

  it('falls back to English message when key is missing', () => {
    expect(
      formatEligibilityRuleMessage({ passed: false, message: 'Semester below program minimum.' }, t),
    ).toBe('Semester below program minimum.')
  })

  it('collects failed rules and skips passed/skipped', () => {
    const lines = eligibilityFailureMessages(
      {
        eligible: false,
        rules: [
          { id: 'gpa', passed: true, skipped: false },
          {
            id: 'required_language',
            passed: false,
            skipped: false,
            message_key: 'language_unmet',
            message_params: { required: 'German', student: 'English' },
          },
        ],
      },
      t,
    )
    expect(lines).toEqual(['Need German, have English'])
  })
})
