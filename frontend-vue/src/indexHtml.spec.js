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
import { THEME_COLOR_DARK, THEME_COLOR_LIGHT } from './services/uiPreferences'

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
    expect(html).toContain(en.appMeta.socialTitle)
    expect(html).toContain(es.appMeta.socialTitle)
    expect(html).toContain('id="seim-shell-bootstrap"')
    expect(html).toContain("var LOCALE_KEY = 'seim.ui_locale'")
    expect(html).toContain("var PREFS_KEY = 'seim_ui_preferences'")
    expect(html).toContain('name="color-scheme"')
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

  it('shell bootstrap sets theme-color from stored UI preferences', () => {
    const html = readFileSync(indexPath, 'utf8')
    const dom = new JSDOM(html, {
      runScripts: 'dangerously',
      url: 'http://localhost/',
      beforeParse(window) {
        window.localStorage.setItem(
          'seim_ui_preferences',
          JSON.stringify({
            theme: 'dark',
            font_size: 'normal',
            high_contrast: false,
            reduce_motion: false,
          }),
        )
      },
    })
    expect(dom.window.document.querySelector('meta[name="theme-color"]').getAttribute('content')).toBe(
      THEME_COLOR_DARK,
    )
    expect(dom.window.document.querySelector('meta[name="color-scheme"]').getAttribute('content')).toBe('dark')
  })

  it('shell bootstrap defaults theme-color to light when prefs absent', () => {
    const html = readFileSync(indexPath, 'utf8')
    const dom = new JSDOM(html, {
      runScripts: 'dangerously',
      url: 'http://localhost/',
    })
    expect(dom.window.document.querySelector('meta[name="theme-color"]').getAttribute('content')).toBe(
      THEME_COLOR_LIGHT,
    )
    expect(dom.window.document.querySelector('meta[name="color-scheme"]').getAttribute('content')).toBe(
      'light dark',
    )
  })

  it('shell bootstrap sets color-scheme light when theme preference is light', () => {
    const html = readFileSync(indexPath, 'utf8')
    const dom = new JSDOM(html, {
      runScripts: 'dangerously',
      url: 'http://localhost/',
      beforeParse(window) {
        window.localStorage.setItem(
          'seim_ui_preferences',
          JSON.stringify({
            theme: 'light',
            font_size: 'normal',
            high_contrast: false,
            reduce_motion: false,
          }),
        )
      },
    })
    expect(dom.window.document.querySelector('meta[name="color-scheme"]').getAttribute('content')).toBe('light')
  })

  it('shell bootstrap sets canonical and og:url from window.location', () => {
    const html = readFileSync(indexPath, 'utf8')
    const dom = new JSDOM(html, {
      runScripts: 'dangerously',
      url: 'http://localhost:8080/seim/login?ref=1#section',
    })
    const doc = dom.window.document
    expect(doc.querySelector('link[rel="canonical"]').getAttribute('href')).toBe(
      'http://localhost:8080/seim/login?ref=1',
    )
    expect(doc.querySelector('meta[property="og:url"]').getAttribute('content')).toBe(
      'http://localhost:8080/seim/login?ref=1',
    )
    expect(doc.querySelector('meta[name="twitter:url"]').getAttribute('content')).toBe(
      'http://localhost:8080/seim/login?ref=1',
    )
    expect(doc.querySelector('meta[property="og:type"]').getAttribute('content')).toBe('website')
  })

  it('shell bootstrap adds localized Open Graph and Twitter meta', () => {
    const html = readFileSync(indexPath, 'utf8')
    const dom = new JSDOM(html, {
      runScripts: 'dangerously',
      url: 'http://localhost/',
      beforeParse(window) {
        window.localStorage.setItem('seim.ui_locale', 'es')
      },
    })
    const doc = dom.window.document
    expect(doc.querySelector('meta[property="og:title"]').getAttribute('content')).toBe(es.appMeta.socialTitle)
    expect(doc.querySelector('meta[property="og:locale"]').getAttribute('content')).toBe('es_ES')
    expect(doc.querySelector('meta[name="twitter:card"]').getAttribute('content')).toBe('summary')
  })
})
