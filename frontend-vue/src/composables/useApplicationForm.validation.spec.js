/**
 * @vitest-environment jsdom
 */
import { describe, it, expect } from 'vitest'
import { ref } from 'vue'
import {
  applyServerValidationErrors,
  isFieldValidationErrorBody,
} from './useApplicationForm'

describe('isFieldValidationErrorBody', () => {
  it('accepts field maps and non_field_errors', () => {
    expect(isFieldValidationErrorBody({ program: ['Required'] })).toBe(true)
    expect(isFieldValidationErrorBody({ non_field_errors: ['Nope'] })).toBe(true)
    expect(isFieldValidationErrorBody({ dynamic_form: ['Missing'] })).toBe(true)
    expect(isFieldValidationErrorBody('plain string')).toBe(true)
  })

  it('rejects generic API failure bodies', () => {
    expect(isFieldValidationErrorBody({ detail: 'Forbidden' })).toBe(false)
    expect(isFieldValidationErrorBody({ error: 'Server blew up' })).toBe(false)
    expect(isFieldValidationErrorBody({ code: 'profile_incomplete' })).toBe(false)
    expect(isFieldValidationErrorBody(null)).toBe(false)
    expect(isFieldValidationErrorBody(undefined)).toBe(false)
    expect(isFieldValidationErrorBody([])).toBe(false)
  })
})

describe('applyServerValidationErrors', () => {
  it('applies field errors and returns true', () => {
    const errors = ref({})
    const dynamicFormErrors = ref([])
    expect(
      applyServerValidationErrors(
        { program: ['Pick a program'], dynamic_form: ['Incomplete'] },
        errors,
        dynamicFormErrors,
      ),
    ).toBe(true)
    expect(errors.value.program).toEqual(['Pick a program'])
    expect(dynamicFormErrors.value).toEqual(['Incomplete'])
  })

  it('returns false for detail-only bodies without mutating field map meaningfully', () => {
    const errors = ref({ program: ['keep'] })
    const dynamicFormErrors = ref(['keep-df'])
    expect(applyServerValidationErrors({ detail: 'Not allowed' }, errors, dynamicFormErrors)).toBe(
      false,
    )
    expect(errors.value).toEqual({ program: ['keep'] })
    expect(dynamicFormErrors.value).toEqual(['keep-df'])
  })
})
