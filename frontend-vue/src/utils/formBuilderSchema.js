export const FIELD_TYPES = [
  { type: 'text', name: 'Text Input', icon: 'bi-input-cursor-text', desc: 'Single line text' },
  { type: 'textarea', name: 'Textarea', icon: 'bi-textarea-t', desc: 'Multi-line text' },
  { type: 'email', name: 'Email', icon: 'bi-envelope', desc: 'Email address' },
  { type: 'number', name: 'Number', icon: 'bi-123', desc: 'Numeric input' },
  { type: 'date', name: 'Date', icon: 'bi-calendar', desc: 'Date picker' },
  { type: 'select', name: 'Select', icon: 'bi-list-ul', desc: 'Dropdown menu' },
  { type: 'checkbox', name: 'Checkbox', icon: 'bi-check-square', desc: 'Checkbox' },
  { type: 'radio', name: 'Radio', icon: 'bi-circle', desc: 'Radio buttons' },
  { type: 'file', name: 'File Upload', icon: 'bi-upload', desc: 'File upload' },
]

const SCHEMA_TYPE = {
  text: 'string',
  textarea: 'string',
  email: 'string',
  number: 'number',
  date: 'string',
  select: 'string',
  checkbox: 'boolean',
  radio: 'string',
  file: 'string',
}

let fieldCounter = 0

export function createField(type) {
  fieldCounter += 1
  const needsOptions = type === 'select' || type === 'radio'
  return {
    id: `field_${Date.now()}_${fieldCounter}`,
    type,
    label: FIELD_TYPES.find((item) => item.type === type)?.name || type,
    required: false,
    placeholder: '',
    helpText: '',
    options: needsOptions ? [{ value: 'option_1', label: 'Option 1' }] : [],
  }
}

export function mapSchemaToFieldType(fieldSchema = {}, ui = {}) {
  const widget = ui['ui:widget']
  if (widget === 'textarea') return 'textarea'
  if (widget === 'radio') return 'radio'
  if (widget === 'file') return 'file'
  if (fieldSchema.format === 'email') return 'email'
  if (fieldSchema.format === 'date') return 'date'
  if (fieldSchema.type === 'number') return 'number'
  if (fieldSchema.type === 'boolean') return 'checkbox'
  if (fieldSchema.enum) return 'select'
  return 'text'
}

export function fieldsFromSchema(schema = {}, uiSchema = {}) {
  const properties = schema?.properties && typeof schema.properties === 'object' ? schema.properties : {}
  const required = Array.isArray(schema?.required) ? schema.required : []
  return Object.entries(properties).map(([id, fieldSchema]) => {
    const ui = uiSchema?.[id] || {}
    const type = mapSchemaToFieldType(fieldSchema || {}, ui)
    return {
      id,
      type,
      label: fieldSchema?.title || id,
      required: required.includes(id),
      placeholder: ui['ui:placeholder'] || '',
      helpText: ui['ui:help'] || '',
      options: Array.isArray(fieldSchema?.enum)
        ? fieldSchema.enum.map((value, idx) => ({
            value,
            label: fieldSchema.enumNames?.[idx] || value,
          }))
        : [],
      min: fieldSchema?.minimum,
      max: fieldSchema?.maximum,
    }
  })
}

export function schemaFromFields(fields = []) {
  const properties = {}
  const required = []
  const uiSchema = {}

  fields.forEach((field) => {
    const fieldName = field.id
    const fieldSchema = {
      type: SCHEMA_TYPE[field.type] || 'string',
      title: field.label || fieldName,
    }
    if (field.type === 'email') fieldSchema.format = 'email'
    if (field.type === 'date') fieldSchema.format = 'date'
    if ((field.type === 'select' || field.type === 'radio') && field.options?.length) {
      fieldSchema.enum = field.options.map((opt) => opt.value || opt)
      fieldSchema.enumNames = field.options.map((opt) => opt.label || opt.value || opt)
    }
    if (field.type === 'number') {
      if (field.min !== undefined && field.min !== '') fieldSchema.minimum = Number(field.min)
      if (field.max !== undefined && field.max !== '') fieldSchema.maximum = Number(field.max)
    }
    properties[fieldName] = fieldSchema
    if (field.required) required.push(fieldName)

    const ui = {}
    if (field.placeholder) ui['ui:placeholder'] = field.placeholder
    if (field.helpText) ui['ui:help'] = field.helpText
    if (field.type === 'textarea') ui['ui:widget'] = 'textarea'
    if (field.type === 'radio') ui['ui:widget'] = 'radio'
    if (field.type === 'file') ui['ui:widget'] = 'file'
    if (Object.keys(ui).length) uiSchema[fieldName] = ui
  })

  return {
    schema: { type: 'object', properties, required },
    uiSchema,
  }
}
