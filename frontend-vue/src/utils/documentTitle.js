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
