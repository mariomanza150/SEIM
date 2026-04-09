import { describe, it, expect } from 'vitest'
import { parseCompareIdsFromQuery, compareIdsToQueryParam, MAX_COMPARE_PROGRAMS } from './programCompareQuery'

describe('programCompareQuery', () => {
  it('parses and caps ids', () => {
    const many = 'a,b,c,d,e,f'
    expect(parseCompareIdsFromQuery({ ids: many })).toEqual(['a', 'b', 'c', 'd'])
    expect(MAX_COMPARE_PROGRAMS).toBe(4)
  })

  it('serializes ids for query', () => {
    expect(compareIdsToQueryParam(['x', 'y'])).toBe('x,y')
    expect(compareIdsToQueryParam([])).toBe('')
  })
})
