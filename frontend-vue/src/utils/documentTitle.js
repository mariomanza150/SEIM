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
