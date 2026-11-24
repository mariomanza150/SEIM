/**
 * @vitest-environment jsdom
 */
import { describe, expect, it } from 'vitest'
import { navItemMatchesRoute } from './navRouteMatch'

describe('navItemMatchesRoute', () => {
  it('matches the item route name exactly', () => {
    expect(navItemMatchesRoute({ key: 'dashboard', to: { name: 'Dashboard' } }, 'Dashboard')).toBe(true)
    expect(navItemMatchesRoute({ key: 'dashboard', to: { name: 'Dashboard' } }, 'Applications')).toBe(false)
  })

  it('matches deep-link child routes for known families', () => {
    expect(navItemMatchesRoute({ key: 'applications', to: { name: 'Applications' } }, 'ApplicationDetail')).toBe(
      true,
    )
    expect(navItemMatchesRoute({ key: 'documents', to: { name: 'Documents' } }, 'DocumentDetail')).toBe(true)
    expect(navItemMatchesRoute({ key: 'help', to: { name: 'HelpCenter' } }, 'HelpArticle')).toBe(true)
    expect(
      navItemMatchesRoute({ key: 'exchangeAgreements', to: { name: 'StaffExchangeAgreements' } }, 'StaffAgreementDocuments'),
    ).toBe(true)
  })

  it('ignores unknown keys and empty names', () => {
    expect(navItemMatchesRoute({ key: 'other', to: { name: 'Other' } }, 'ApplicationDetail')).toBe(false)
    expect(navItemMatchesRoute({ key: 'applications', to: { name: 'Applications' } }, null)).toBe(false)
  })
})
