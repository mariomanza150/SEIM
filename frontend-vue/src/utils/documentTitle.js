import i18n from '@/i18n'

/**
 * Localized browser tab title for a matched route (Vue Router route object).
 */
export function resolveDocumentTitle(routeLike) {
  const t = i18n.global.t
  const name = routeLike?.name
  if (name === 'NotFound') {
    return `${t('route.notFoundBrowserTitle')} - ${t('route.fallbackTitle')}`
  }
  if (typeof name === 'string' && name) {
    const key = `route.names.${name}`
    if (i18n.global.te(key)) {
      return `${t(key)} - ${t('route.fallbackTitle')}`
    }
  }
  return t('route.fallbackTitle')
}

/**
 * Set document meta description from the active i18n locale (SEO / sharing fallbacks).
 * @param {(key: string) => string} t - vue-i18n translate function
 */
export function syncAppMetaDescription(t) {
  if (typeof document === 'undefined') return
  const el = document.querySelector('meta[name="description"]')
  if (!el) return
  el.setAttribute('content', t('appMeta.metaDescription'))
}

function upsertHeadMeta(byAttr, key, content) {
  if (typeof document === 'undefined') return
  let el = document.head.querySelector(`meta[${byAttr}="${key}"]`)
  if (!el) {
    el = document.createElement('meta')
    el.setAttribute(byAttr, key)
    document.head.appendChild(el)
  }
  el.setAttribute('content', content)
}

/**
 * Open Graph + Twitter Card tags for link previews (SPA updates on navigation / locale).
 * @param {(key: string) => string} t - vue-i18n translate function
 * @param {object} [routeLike] - matched route (uses tab title; generic product title when tab is only fallback)
 */
export function syncAppSocialMeta(t, routeLike = {}) {
  if (typeof document === 'undefined') return
  const tabTitle = resolveDocumentTitle(routeLike)
  const fallback = t('route.fallbackTitle')
  const shareTitle = tabTitle === fallback ? t('appMeta.socialTitle') : tabTitle
  const desc = t('appMeta.metaDescription')
  const site = t('route.fallbackTitle')

  upsertHeadMeta('property', 'og:title', shareTitle)
  upsertHeadMeta('property', 'og:description', desc)
  upsertHeadMeta('property', 'og:locale', t('appMeta.ogLocale'))
  upsertHeadMeta('property', 'og:locale:alternate', t('appMeta.ogLocaleAlternate'))
  upsertHeadMeta('property', 'og:site_name', site)
  upsertHeadMeta('property', 'og:type', 'website')
  upsertHeadMeta('name', 'twitter:card', 'summary')
  upsertHeadMeta('name', 'twitter:title', shareTitle)
  upsertHeadMeta('name', 'twitter:description', desc)
}

/**
 * Absolute page URL for `<link rel="canonical">`, `og:url`, and `twitter:url` (strip hash only).
 * @param {string} absoluteHref - full https? URL
 */
export function syncCanonicalLink(absoluteHref) {
  if (typeof document === 'undefined' || !absoluteHref) return
  const href = absoluteHref.split('#')[0]
  let link = document.head.querySelector('link[rel="canonical"]')
  if (!link) {
    link = document.createElement('link')
    link.setAttribute('rel', 'canonical')
    document.head.appendChild(link)
  }
  link.setAttribute('href', href)
  upsertHeadMeta('property', 'og:url', href)
  upsertHeadMeta('name', 'twitter:url', href)
}
