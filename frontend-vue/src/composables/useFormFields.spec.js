import { describe, it, expect } from 'vitest'
import { useFormFields } from '@/composables/useFormFields'

describe('useFormFields', () => {
  it('tracks and clears field errors', () => {
    const { fieldErrors, setFieldError, clearFieldErrors, hasFieldError, fieldClass, ariaInvalid } = useFormFields()
    setFieldError('email', 'Required')
    expect(fieldErrors.value.email).toBe('Required')
    expect(hasFieldError('email')).toBe(true)
    expect(fieldClass('email')).toEqual(['form-control', { 'is-invalid': true }])
    expect(ariaInvalid('email')).toBe('true')
    clearFieldErrors()
    expect(hasFieldError('email')).toBe(false)
  })

  it('maps API field errors', () => {
    const { fieldErrors, applyApiFieldErrors } = useFormFields()
    applyApiFieldErrors({ matricula: ['Invalid format'], detail: 'ignored' })
    expect(fieldErrors.value.matricula).toBe('Invalid format')
    expect(fieldErrors.value.detail).toBeUndefined()
  })
})
