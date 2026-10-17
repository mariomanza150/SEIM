import { describe, it, expect } from 'vitest'
import { findScale, gradeScaleBounds, gradeScalePolicy } from './gradeScale'

describe('gradeScale utils', () => {
  it('derives min/max/step from the scale', () => {
    expect(gradeScaleBounds({ min_value: 0, max_value: 10 })).toEqual({ min: 0, max: 10, step: 0.01 })
    expect(gradeScaleBounds({ min_value: 0, max_value: 100 })).toEqual({ min: 0, max: 100, step: 0.1 })
    expect(gradeScaleBounds({ min_value: 5, max_value: 1 })).toEqual({ min: 1, max: 5, step: 0.01 })
    expect(gradeScaleBounds(null)).toEqual({ min: 0, max: null, step: 0.01 })
  })

  it('finds scales by string id', () => {
    expect(findScale([{ id: 'a' }, { id: 2 }], '2')).toEqual({ id: 2 })
    expect(findScale([{ id: 'a' }], '')).toBeNull()
  })

  it('normalises the grade scale policy', () => {
    expect(gradeScalePolicy({ grade_scale_policy: { locked: true, default_grade_scale: 7, default_grade_scale_name: 'MX' } }))
      .toEqual({ locked: true, defaultId: '7', defaultName: 'MX' })
    expect(gradeScalePolicy({})).toEqual({ locked: false, defaultId: '', defaultName: '' })
  })
})
