/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import NotificationRouting from './NotificationRouting.vue'
import api from '@/services/api'
import i18n, { setAppLocale } from '@/i18n'

vi.mock('@/services/api', () => ({
  default: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: vi.fn(), error: vi.fn() }),
}))

const mockPayload = {
  schema_version: 12,
  reference_api_access: {
    roles_any: ['coordinator', 'admin'],
    superuser: true,
    description: 'Mock: only staff roles; others get HTTP 403.',
  },
  settings_categories: {
    applications: {
      email_user_settings_field: 'email_applications',
      inapp_user_settings_field: 'inapp_applications',
      typical_triggers: 'Application lifecycle (mock).',
      primary_recipients: 'Primarily the applicant (mock).',
    },
    system: {
      email_user_settings_field: 'email_system',
      inapp_user_settings_field: 'inapp_system',
      notes: 'Digests and alerts.',
    },
  },
  transactional_routes: [
    {
      route_key: 'application_submitted',
      settings_category: 'applications',
      recipient_summary: 'Mock: the student who submitted.',
      summary: 'Mock: student submit confirmation.',
      source: 'exchange.services.ApplicationService.submit_application',
    },
  ],
  transactional_route_keys_by_settings_category: {
    applications: ['application_submitted'],
    ungated: ['account_security_email'],
  },
  reminder_event_type_to_settings_category: {
    application_deadline: 'applications',
  },
  reminder_event_types_by_settings_category: {
    applications: ['application_deadline'],
  },
  reminder_event_type_descriptions: {
    application_deadline: 'Deadline tied to application milestones.',
  },
  reminder_event_type_recipient_summaries: {
    application_deadline: 'Mock: reminder owner receives the notification.',
  },
  reminder_default_settings_category: 'programs',
  digest: {
    settings_category: 'system',
    email_gates: ['email_system', 'email_notification_digest'],
    inapp_user_settings_field: 'inapp_system',
    recipient_summary: 'Mock digest recipients line for tests.',
    typical_triggers: 'Digest mock summary line for tests.',
  },
}

describe('NotificationRouting', () => {
  beforeEach(() => {
    localStorage.clear()
    setAppLocale('en')
    vi.clearAllMocks()
    api.get.mockImplementation((url) => {
      if (String(url).includes('notification-routing-overrides')) {
        return Promise.resolve({ data: { results: [], next: null } })
      }
      return Promise.resolve({ data: mockPayload })
    })
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
    expect(api.get).toHaveBeenCalledWith('/api/notification-routing-overrides/')
    expect(wrapper.text()).toContain('Notification routing')
    expect(wrapper.text()).toContain('Routing overrides')
    expect(wrapper.text()).toContain('No overrides yet')
    expect(wrapper.text()).toContain('applications')
    expect(wrapper.text()).toContain('email_applications')
    expect(wrapper.text()).toContain('application_deadline')
    expect(wrapper.text()).toContain('Digest routing')
    expect(wrapper.text()).toContain('Recipients (digest)')
    expect(wrapper.text()).toContain('Mock digest recipients line for tests.')
    expect(wrapper.text()).toContain('Digest mock summary line for tests.')
    expect(wrapper.text()).toContain('Application lifecycle (mock).')
    expect(wrapper.text()).toContain('Reminder event types by UserSettings group')
    expect(wrapper.text()).toContain('Recipients (reminder)')
    expect(wrapper.text()).toContain('Mock: reminder owner receives the notification.')
    expect(wrapper.text()).toContain('Deadline tied to application milestones.')
    expect(wrapper.text()).toContain('Who can call this API')
    expect(wrapper.text()).toContain('Mock: only staff roles')
    expect(wrapper.text()).toContain('Primarily the applicant (mock).')
    expect(wrapper.text()).toContain('Transactional routes by UserSettings group')
    expect(wrapper.text()).toContain('ungated')
    expect(wrapper.text()).toContain('account_security_email')
    expect(wrapper.text()).toContain('Transactional sends (catalog)')
    expect(wrapper.text()).toContain('application_submitted')
    expect(wrapper.text()).toContain('Recipients (this send)')
    expect(wrapper.text()).toContain('Mock: the student who submitted.')
    expect(wrapper.text()).toContain('Mock: student submit confirmation.')
  })

  it('lists routing overrides returned by the overrides API', async () => {
    const ov = {
      id: 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
      kind: 'reminder_event_type',
      key: 'application_deadline',
      settings_category: 'documents',
      is_active: true,
    }
    api.get.mockImplementation((url) => {
      if (String(url).includes('notification-routing-overrides')) {
        return Promise.resolve({ data: { results: [ov], next: null } })
      }
      return Promise.resolve({ data: mockPayload })
    })
    const wrapper = mount(NotificationRouting, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.text()).toContain('application_deadline')
    expect(wrapper.text()).toContain('documents')
    expect(wrapper.text()).toContain('reminder_event_type')
  })
})
