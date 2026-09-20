import { describe, expect, it } from 'vitest'
import { resolveSectionDefaultOpen, resolveSectionDefaultsMap } from './sectionDefaults'

describe('sectionDefaults', () => {
  const action = { id: 'action', defaultOpen: true }
  const pending = {
    id: 'pending_review',
    defaultOpen: false,
    defaultOpenForStaff: true,
  }
  const done = { id: 'done', defaultOpen: false }

  it('opens defaultOpen sections for students', () => {
    expect(resolveSectionDefaultOpen(action, {})).toBe(true)
    expect(resolveSectionDefaultOpen(pending, {})).toBe(false)
    expect(resolveSectionDefaultOpen(done, {})).toBe(false)
  })

  it('opens staff-relevant sections for coordinators', () => {
    const viewer = { isCoordinator: true }
    expect(resolveSectionDefaultOpen(action, viewer)).toBe(true)
    expect(resolveSectionDefaultOpen(pending, viewer)).toBe(true)
    expect(resolveSectionDefaultOpen(done, viewer)).toBe(false)
  })

  it('keeps all role-based sections collapsed for admins', () => {
    const viewer = { isAdmin: true, isCoordinator: true }
    expect(resolveSectionDefaultOpen(action, viewer)).toBe(false)
    expect(resolveSectionDefaultOpen(pending, viewer)).toBe(false)
  })

  it('honors openWhen context even for admins', () => {
    const merge = {
      id: 'mergeFields',
      defaultOpen: false,
      openWhen: (ctx) => Boolean(ctx.hasTemplate),
    }
    expect(resolveSectionDefaultOpen(merge, { isAdmin: true }, { hasTemplate: false })).toBe(false)
    expect(resolveSectionDefaultOpen(merge, { isAdmin: true }, { hasTemplate: true })).toBe(true)
  })

  it('builds an id map via resolveSectionDefaultsMap', () => {
    const map = resolveSectionDefaultsMap([action, pending, done], { isCoordinator: true })
    expect(map).toEqual({
      action: true,
      pending_review: true,
      done: false,
    })
  })
})
