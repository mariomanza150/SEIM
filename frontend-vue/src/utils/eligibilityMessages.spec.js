/**
 * @vitest-environment jsdom
 */
import { describe, it, expect } from 'vitest'
import {
  eligibilityFailureMessages,
  eligibilityFixItems,
  eligibilityFixLink,
  formatEligibilityRuleMessage,
} from './eligibilityMessages'

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

  it('orders fix items and maps GPA / language / docs to actions', () => {
    const items = eligibilityFixItems(
      {
        eligible: false,
        rules: [
          {
            id: 'required_documents',
            passed: false,
            skipped: false,
            message: 'Required documents are not all approved yet: transcript',
            message_key: 'documents_incomplete',
            message_params: { items: 'transcript' },
          },
          {
            id: 'gpa',
            passed: false,
            skipped: false,
            message: 'GPA below program minimum.',
            message_key: 'gpa_below',
            message_params: { student: '2.0', required: '3.0' },
          },
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
    expect(items.map((row) => row.key)).toEqual(['gpa', 'required_language', 'required_documents'])
    expect(items.map((row) => row.action)).toEqual(['profile', 'profile', 'documents'])
    expect(items[1].message).toBe('Need German, have English')
  })

  it('links profile and upload actions', () => {
    expect(eligibilityFixLink('profile', { nextPath: '/applications/1' })).toEqual({
      name: 'Profile',
      query: { next: '/applications/1' },
    })
    expect(eligibilityFixLink('documents', { applicationId: 'app-1' })).toEqual({
      name: 'ApplicationDetail',
      params: { id: 'app-1' },
      hash: '#document-upload',
    })
  })
})
