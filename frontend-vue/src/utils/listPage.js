/**
 * Normalize a list-fetch page argument.
 * Native `@change="fetchX"` handlers pass a DOM Event, which must not become `?page=[object Event]`.
 */
export function resolveListPage(page, fallback = 1) {
  const n = Number.parseInt(page, 10)
  return Number.isInteger(n) && n >= 1 ? n : fallback
}
