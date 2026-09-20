/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import CollapsibleCard from './CollapsibleCard.vue'
import DocumentProgressRail from './DocumentProgressRail.vue'
import i18n, { setAppLocale } from '@/i18n'

describe('CollapsibleCard', () => {
  it('starts collapsed by default and expands on toggle', async () => {
    const wrapper = mount(CollapsibleCard, {
      props: { testId: 'demo', defaultOpen: false },
      slots: { title: 'Section title', default: '<p data-testid="body">Body</p>' },
    })
    const toggle = wrapper.find('[data-testid="collapsible-card-toggle"]')
    expect(toggle.attributes('aria-expanded')).toBe('false')
    expect(wrapper.find('[data-testid="collapsible-card-panel"]').exists()).toBe(false)

    await toggle.trigger('click')
    expect(toggle.attributes('aria-expanded')).toBe('true')
    expect(wrapper.find('[data-testid="collapsible-card-panel"]').exists()).toBe(true)
  })
})

describe('DocumentProgressRail', () => {
  beforeEach(() => {
    setAppLocale('en')
  })

  const checklist = {
    required_count: 1,
    approved_count: 0,
    complete: false,
    items: [
      {
        document_type_id: 42,
        slug: 'transcript',
        name: 'Transcript',
        status: 'missing',
        due_now: true,
      },
    ],
  }

  it('starts collapsed and expands to show due-now links', async () => {
    const wrapper = mount(DocumentProgressRail, {
      props: { checklist },
      global: { plugins: [i18n] },
    })
    expect(wrapper.find('[data-testid="document-progress-rail-badge"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="collapsible-card-toggle"]').attributes('aria-expanded')).toBe(
      'false',
    )
    expect(wrapper.find('[data-testid="document-progress-rail-link"]').exists()).toBe(false)

    await wrapper.find('[data-testid="collapsible-card-toggle"]').trigger('click')
    const link = wrapper.find('[data-testid="document-progress-rail-link"]')
    expect(link.exists()).toBe(true)
    expect(link.attributes('href')).toBe('#checklist-item-42')
    await link.trigger('click')
    expect(wrapper.emitted('navigate-item')).toHaveLength(1)
    expect(wrapper.emitted('navigate-item')[0][0]).toMatchObject({
      document_type_id: 42,
      status: 'missing',
    })
  })
})
