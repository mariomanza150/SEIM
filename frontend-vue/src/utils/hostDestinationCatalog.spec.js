/**
 * @vitest-environment jsdom
 */
import { describe, it, expect } from 'vitest'
import {
  buildHostNameOptions,
  countriesMatch,
  decodeHostSuggestion,
  encodeHostSuggestion,
  filterCountryOptionsByHostName,
  filterGradeScalesByCountry,
  filterInstitutionsBySearch,
  gradeScaleMatchesCountry,
} from './hostDestinationCatalog'

const countryOptions = [
  { value: 'España', label: 'España', aliases: ['Spain'] },
  { value: 'EUA', label: 'EUA', aliases: ['USA', 'United States'] },
  { value: 'Alemania', label: 'Alemania', aliases: ['Germany'] },
  { value: 'Francia', label: 'Francia', aliases: ['France'] },
]

describe('hostDestinationCatalog', () => {
  it('matches countries via catalog aliases', () => {
    expect(countriesMatch('EUA', 'United States', countryOptions)).toBe(true)
    expect(countriesMatch('Alemania', 'Germany', countryOptions)).toBe(true)
    expect(countriesMatch('España', 'EUA', countryOptions)).toBe(false)
  })

  it('filters grade scales by country including EU regional scales', () => {
    const scales = [
      { id: '1', name: 'MX', country: 'Mexico' },
      { id: '2', name: 'US GPA', country: 'United States' },
      { id: '3', name: 'ECTS', country: 'European Union' },
      { id: '4', name: 'Generic', country: '' },
    ]

    const forEua = filterGradeScalesByCountry(scales, 'EUA', countryOptions)
    expect(forEua.map((s) => s.id).sort()).toEqual(['2', '4'])

    const forSpain = filterGradeScalesByCountry(scales, 'España', countryOptions)
    expect(forSpain.map((s) => s.id).sort()).toEqual(['3', '4'])
    expect(gradeScaleMatchesCountry(scales[2], 'Francia', countryOptions)).toBe(true)
  })

  it('builds host name options and encodes/decodes suggestions', () => {
    const institutions = [
      { name: 'Universidad de León', country: 'España', grade_scale: 'gs-1' },
      { name: 'MIT', country: 'EUA', grade_scale: 'gs-2' },
      { name: 'Universidad de León', country: 'España', grade_scale: 'gs-1' },
    ]
    const options = buildHostNameOptions(institutions, { country: 'España' })
    expect(options).toHaveLength(1)
    expect(options[0].label).toContain('España')

    const encoded = encodeHostSuggestion(institutions[0])
    expect(decodeHostSuggestion(encoded)).toEqual({
      name: 'Universidad de León',
      country: 'España',
      grade_scale: 'gs-1',
    })
    expect(decodeHostSuggestion('Brand New U')).toEqual({
      name: 'Brand New U',
      country: '',
      grade_scale: '',
    })
  })

  it('narrows country options from typed university name', () => {
    const institutions = [
      { name: 'Universidad de León', country: 'España' },
      { name: 'MIT', country: 'EUA' },
    ]
    const filtered = filterCountryOptionsByHostName(countryOptions, institutions, 'león')
    expect(filtered.map((c) => c.value)).toEqual(['España'])
  })

  it('filters the destinations list by search text', () => {
    const institutions = [
      { name: 'MIT', country: 'EUA', grade_scale_name: 'US GPA' },
      { name: 'Universidad de León', country: 'España', grade_scale_code: 'ECTS' },
    ]
    expect(filterInstitutionsBySearch(institutions, 'espa').map((i) => i.name)).toEqual([
      'Universidad de León',
    ])
    expect(filterInstitutionsBySearch(institutions, 'gpa').map((i) => i.name)).toEqual(['MIT'])
  })
})
