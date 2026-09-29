export const ACCESS_TOKEN_KEYS = ['access_token', 'seim_access_token']
export const REFRESH_TOKEN_KEYS = ['refresh_token', 'seim_refresh_token']

export function getStoredToken(keys) {
  return keys.map((key) => localStorage.getItem(key)).find(Boolean) || null
}

export function persistToken(keys, value) {
  keys.forEach((key) => {
    if (value) {
      localStorage.setItem(key, value)
    } else {
      localStorage.removeItem(key)
    }
  })
}

export function getStoredAccessToken() {
  return getStoredToken(ACCESS_TOKEN_KEYS)
}
