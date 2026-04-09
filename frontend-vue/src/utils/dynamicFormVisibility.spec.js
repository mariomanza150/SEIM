import { describe, it, expect } from 'vitest'
import { fieldMeetsVisibleWhen, stepMeetsVisibleWhen, visibleWhenRuleMatches } from './dynamicFormVisibility'

describe('fieldMeetsVisibleWhen', () => {
  it('allows when no rule', () => {
    expect(fieldMeetsVisibleWhen({ type: 'string' }, {})).toBe(true)
  })

  it('equals', () => {
    const cfg = { 'x-seim-visibleWhen': { field: 'g', equals: 'yes' } }
    expect(fieldMeetsVisibleWhen(cfg, { g: 'yes' })).toBe(true)
    expect(fieldMeetsVisibleWhen(cfg, { g: 'no' })).toBe(false)
  })

  it('truthy', () => {
    const cfg = { 'x-seim-visibleWhen': { field: 'g', truthy: true } }
    expect(fieldMeetsVisibleWhen(cfg, { g: 'x' })).toBe(true)
    expect(fieldMeetsVisibleWhen(cfg, { g: '' })).toBe(false)
  })
})

describe('stepMeetsVisibleWhen', () => {
  it('uses visible_when on step', () => {
    const step = { key: 's2', visible_when: { field: 'g', equals: 1 } }
    expect(stepMeetsVisibleWhen(step, { g: 1 })).toBe(true)
    expect(stepMeetsVisibleWhen(step, { g: 2 })).toBe(false)
  })
})

describe('visibleWhenRuleMatches', () => {
  it('matches equals', () => {
    expect(visibleWhenRuleMatches({ field: 'a', equals: 'z' }, { a: 'z' })).toBe(true)
  })

  it('program_id context', () => {
    expect(visibleWhenRuleMatches({ program_id: 3 }, {}, { program_id: 3 })).toBe(true)
    expect(visibleWhenRuleMatches({ program_id: 3 }, {}, { program_id: 4 })).toBe(false)
  })

  it('staff_only', () => {
    expect(visibleWhenRuleMatches({ staff_only: true }, {}, { viewer_roles: ['student'] })).toBe(false)
    expect(visibleWhenRuleMatches({ staff_only: true }, {}, { viewer_roles: ['coordinator'] })).toBe(true)
  })
})
