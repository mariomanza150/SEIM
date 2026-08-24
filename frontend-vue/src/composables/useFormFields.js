import { ref } from 'vue'

/**
 * Minimal per-field validation state for Bootstrap forms.
 *
 * Usage:
 *   const { fieldErrors, setFieldError, clearFieldErrors, fieldClass, ariaInvalid, describeId } = useFormFields()
 *   <input :class="fieldClass('email')" :aria-invalid="ariaInvalid('email')" :aria-describedby="describeId('email')" />
 *   <div v-if="fieldErrors.email" :id="describeId('email')" class="invalid-feedback d-block">{{ fieldErrors.email }}</div>
 */
export function useFormFields() {
  const fieldErrors = ref({})

  function setFieldError(fieldId, message) {
    if (!message) {
      clearFieldError(fieldId)
      return
    }
    fieldErrors.value = { ...fieldErrors.value, [fieldId]: message }
  }

  function clearFieldError(fieldId) {
    if (!fieldErrors.value[fieldId]) return
    const next = { ...fieldErrors.value }
    delete next[fieldId]
    fieldErrors.value = next
  }

  function clearFieldErrors() {
    fieldErrors.value = {}
  }

  function hasFieldError(fieldId) {
    return Boolean(fieldErrors.value[fieldId])
  }

  function fieldClass(fieldId, baseClass = 'form-control') {
    return [baseClass, { 'is-invalid': hasFieldError(fieldId) }]
  }

  function selectClass(fieldId) {
    return fieldClass(fieldId, 'form-select')
  }

  function ariaInvalid(fieldId) {
    return hasFieldError(fieldId) ? 'true' : 'false'
  }

  function describeId(fieldId) {
    return hasFieldError(fieldId) ? `${fieldId}-error` : undefined
  }

  /**
   * Map DRF-style field errors onto form fields.
   * @param {Record<string, string|string[]>} apiErrors
   */
  function applyApiFieldErrors(apiErrors) {
    if (!apiErrors || typeof apiErrors !== 'object') return
    for (const [key, value] of Object.entries(apiErrors)) {
      if (key === 'detail') continue
      const msg = Array.isArray(value) ? value.join(' ') : String(value)
      setFieldError(key, msg)
    }
  }

  return {
    fieldErrors,
    setFieldError,
    clearFieldError,
    clearFieldErrors,
    hasFieldError,
    fieldClass,
    selectClass,
    ariaInvalid,
    describeId,
    applyApiFieldErrors,
  }
}
