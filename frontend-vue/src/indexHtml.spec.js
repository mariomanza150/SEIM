/**
 * @vitest-environment node
 */
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { describe, it, expect } from 'vitest'

const __dirname = dirname(fileURLToPath(import.meta.url))
const indexPath = join(__dirname, '..', 'index.html')

describe('frontend-vue/index.html', () => {
  it('includes bilingual noscript messaging and accessibility role', () => {
    const html = readFileSync(indexPath, 'utf8')
    expect(html).toContain('role="alert"')
    expect(html).toContain('lang="en"')
    expect(html).toContain('lang="es"')
    expect(html).toContain('JavaScript required')
    expect(html).toContain('Se requiere JavaScript')
    expect(html).toContain('Please enable JavaScript')
    expect(html).toContain('Activa JavaScript')
  })
})
