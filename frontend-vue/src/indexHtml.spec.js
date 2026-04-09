/**
 * @vitest-environment node
 */
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { describe, it, expect } from 'vitest'
import { JSDOM } from 'jsdom'
import en from './locales/en.json'
import es from './locales/es.json'

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

  it('embeds shell meta strings matching locale appMeta (keep in sync)', () => {
    const html = readFileSync(indexPath, 'utf8')
    expect(html).toContain(en.appMeta.metaDescription)
    expect(html).toContain(es.appMeta.metaDescription)
    expect(html).toContain('id="seim-shell-locale-bootstrap"')
    expect(html).toContain("var KEY = 'seim.ui_locale'")
  })

  it('shell bootstrap sets lang and meta from localStorage before module loads', () => {
    const html = readFileSync(indexPath, 'utf8')
    const dom = new JSDOM(html, {
      runScripts: 'dangerously',
      url: 'http://localhost/',
      beforeParse(window) {
        window.localStorage.setItem('seim.ui_locale', 'es')
      },
    })
    const doc = dom.window.document
    expect(doc.documentElement.lang).toBe('es')
    expect(doc.title).toBe('SEIM')
    expect(doc.querySelector('meta[name="description"]').getAttribute('content')).toBe(es.appMeta.metaDescription)
  })
})
