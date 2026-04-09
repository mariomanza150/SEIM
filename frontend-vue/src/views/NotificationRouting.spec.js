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
  schema_version: 9,
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
    recipient_summary: 'Mock digest recipients line for tests.',
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
    expect(wrapper.text()).toContain('Recipients (digest)')
    expect(wrapper.text()).toContain('Mock digest recipients line for tests.')
    expect(wrapper.text()).toContain('Digest mock summary line for tests.')
    expect(wrapper.text()).toContain('Application lifecycle (mock).')
    expect(wrapper.text()).toContain('Deadline tied to application milestones.')
    expect(wrapper.text()).toContain('Who can call this API')
    expect(wrapper.text()).toContain('Mock: only staff roles')
    expect(wrapper.text()).toContain('Primarily the applicant (mock).')
    expect(wrapper.text()).toContain('Transactional sends (catalog)')
    expect(wrapper.text()).toContain('application_submitted')
    expect(wrapper.text()).toContain('Recipients (this send)')
    expect(wrapper.text()).toContain('Mock: the student who submitted.')
    expect(wrapper.text()).toContain('Mock: student submit confirmation.')
  })
})
