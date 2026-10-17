/* global __APP_COMMIT__, __APP_BUILD_TIME__ */
export const APP_COMMIT = typeof __APP_COMMIT__ !== 'undefined' ? __APP_COMMIT__ : ''
export const APP_BUILD_TIME = typeof __APP_BUILD_TIME__ !== 'undefined' ? __APP_BUILD_TIME__ : ''

export function shortCommit(sha) {
  return sha ? String(sha).slice(0, 7) : ''
}
