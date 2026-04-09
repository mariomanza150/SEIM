/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import NotificationRouting from './NotificationRouting.vue'
import api from '@/services/api'
import i18n, { setAppLocale } from '@/i18n'

vi.mock('@/services/api', () => ({
  default: { get: vi.fn() },
}))

vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: vi.fn(), error: vi.fn() }),
}))

const mockPayload = {
  schema_version: 4,
  settings_categories: {
    applications: {
      email_user_settings_field: 'email_applications',
      inapp_user_settings_field: 'inapp_applications',
      typical_triggers: 'Application lifecycle (mock).',
    },
    system: {
      email_user_settings_field: 'email_system',
      inapp_user_settings_field: 'inapp_system',
      notes: 'Digests and alerts.',
    },
  },
  reminder_event_type_to_settings_category: {
    application_deadline: 'applications',
  },
  reminder_event_type_descriptions: {
    application_deadline: 'Deadline tied to application milestones.',
  },
  reminder_default_settings_category: 'programs',
  digest: {
    settings_category: 'system',
    email_gates: ['email_system', 'email_notification_digest'],
    inapp_user_settings_field: 'inapp_system',
    typical_triggers: 'Digest mock summary line for tests.',
  },
}

describe('NotificationRouting', () => {
  beforeEach(() => {
    localStorage.clear()
    setAppLocale('en')
    vi.clearAllMocks()
    api.get.mockResolvedValue({ data: mockPayload })
  })

  afterEach(() => {
    setAppLocale('en')
    localStorage.clear()
  })

  it('loads routing reference and shows category and reminder tables', async () => {
    const wrapper = mount(NotificationRouting, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(api.get).toHaveBeenCalledWith('/api/notifications/routing-reference/')
    expect(wrapper.text()).toContain('Notification routing')
    expect(wrapper.text()).toContain('applications')
    expect(wrapper.text()).toContain('email_applications')
    expect(wrapper.text()).toContain('application_deadline')
    expect(wrapper.text()).toContain('Digest routing')
    expect(wrapper.text()).toContain('Digest mock summary line for tests.')
    expect(wrapper.text()).toContain('Application lifecycle (mock).')
    expect(wrapper.text()).toContain('Deadline tied to application milestones.')
  })
})
