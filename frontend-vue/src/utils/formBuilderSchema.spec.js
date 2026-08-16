/**
 * @vitest-environment node
 */
import { describe, it, expect } from 'vitest'
import { createField, fieldsFromSchema, schemaFromFields } from './formBuilderSchema'

describe('formBuilderSchema', () => {
  it('round-trips visual fields through JSON schema', () => {
    const fields = [
      { ...createField('email'), label: 'Email', required: true, placeholder: 'you@example.com' },
      {
        ...createField('select'),
        label: 'Campus',
        options: [
          { value: 'north', label: 'North' },
          { value: 'south', label: 'South' },
        ],
      },
      { ...createField('textarea'), label: 'Notes', helpText: 'Optional' },
    ]
    const { schema, uiSchema } = schemaFromFields(fields)
    expect(schema.required).toContain(fields[0].id)
    expect(schema.properties[fields[0].id].format).toBe('email')
    expect(schema.properties[fields[1].id].enum).toEqual(['north', 'south'])
    expect(uiSchema[fields[2].id]['ui:widget']).toBe('textarea')

    const restored = fieldsFromSchema(schema, uiSchema)
    expect(restored.map((field) => field.type)).toEqual(['email', 'select', 'textarea'])
    expect(restored[1].options).toEqual([
      { value: 'north', label: 'North' },
      { value: 'south', label: 'South' },
    ])
  })
})
