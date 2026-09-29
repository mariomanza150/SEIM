const THEME_LINK_ID = 'seim-institution-theme-css'
const THEME_VARS_ID = 'seim-institution-theme-vars'

/** Parse #RRGGBB or #RGB to "r, g, b" for Bootstrap --bs-primary-rgb. */
export function hexToRgbTriplet(hex) {
  if (!hex || typeof hex !== 'string') return null
  let normalized = hex.trim().replace('#', '')
  if (normalized.length === 3) {
    normalized = normalized
      .split('')
      .map((c) => c + c)
      .join('')
  }
  if (normalized.length !== 6 || !/^[0-9a-fA-F]{6}$/.test(normalized)) return null
  const r = parseInt(normalized.slice(0, 2), 16)
  const g = parseInt(normalized.slice(2, 4), 16)
  const b = parseInt(normalized.slice(4, 6), 16)
  return `${r}, ${g}, ${b}`
}

function upsertLink(id, href) {
  if (typeof document === 'undefined' || !href) return
  let el = document.getElementById(id)
  if (!el) {
    el = document.createElement('link')
    el.id = id
    el.rel = 'stylesheet'
    document.head.appendChild(el)
  }
  if (el.getAttribute('href') !== href) {
    el.setAttribute('href', href)
  }
}

function upsertStyle(id, cssText) {
  if (typeof document === 'undefined' || !cssText) return
  let el = document.getElementById(id)
  if (!el) {
    el = document.createElement('style')
    el.id = id
    document.head.appendChild(el)
  }
  el.textContent = cssText
}

/**
 * Apply institution theme stylesheet and CSS variables (mirrors CMS base.html).
 * @param {{ theme_css?: string, theme?: Record<string, string> }} branding
 */
export function applyBrandTheme(branding) {
  if (typeof document === 'undefined' || !branding) return

  const themeCss = branding.theme_css || 'uadec/theme.css'
  upsertLink(THEME_LINK_ID, `/static/${themeCss.replace(/^\//, '')}`)

  const theme = branding.theme || {}
  const primary = theme.primary || '#667eea'
  const accent = theme.accent || '#764ba2'
  const primaryRgb = hexToRgbTriplet(primary) || '102, 126, 234'

  const css = `:root {
  --uadec-blue: ${theme.primary || '#2E5790'};
  --uadec-blue-light: ${theme.primary_light || '#3251AC'};
  --uadec-blue-dark: ${theme.primary_dark || '#1E3A5F'};
  --uadec-gold: ${theme.accent || '#BF9B4C'};
  --uadec-gold-light: ${theme.accent_light || '#EDB621'};
  --uadec-gold-dark: ${theme.accent_dark || '#A6863D'};
  --uadec-navy: ${theme.navy || '#1E3A5F'};
  --uadec-orange: ${theme.orange || '#E67E22'};
  --uadec-text: ${theme.text || '#2C3E50'};
  --brand-primary: ${primary};
  --brand-primary-light: ${theme.primary_light || primary};
  --brand-primary-dark: ${theme.primary_dark || primary};
  --brand-accent: ${accent};
  --brand-accent-light: ${theme.accent_light || accent};
  --brand-accent-dark: ${theme.accent_dark || accent};
  --brand-navy: ${theme.navy || '#1E3A5F'};
  --brand-orange: ${theme.orange || '#E67E22'};
  --brand-text: ${theme.text || '#2C3E50'};
  --seim-brand-primary: ${primary};
  --seim-brand-secondary: ${accent};
  --bs-primary: ${primary};
  --bs-primary-rgb: ${primaryRgb};
  --bs-link-color: ${primary};
  --primary-color: ${primary};
}`

  upsertStyle(THEME_VARS_ID, css)

  const themeColorMeta = document.querySelector('meta[name="theme-color"]')
  if (themeColorMeta && document.documentElement.dataset.theme !== 'dark') {
    themeColorMeta.setAttribute('content', primary)
  }
}
