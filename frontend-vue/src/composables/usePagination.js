import { computed } from 'vue'

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value))
}

export function usePagination({ count, pageSize, currentPage, maxPageButtons = 7 }) {
  const totalPages = computed(() => {
    const size = Number(pageSize?.value ?? pageSize ?? 0)
    const c = Number(count?.value ?? count ?? 0)
    if (!size || size <= 0) return 1
    return Math.max(1, Math.ceil(c / size))
  })

  const pageItems = computed(() => {
    const total = totalPages.value
    const cur = clamp(Number(currentPage?.value ?? currentPage ?? 1), 1, total)

    if (total <= maxPageButtons) {
      return Array.from({ length: total }, (_, i) => ({ type: 'page', page: i + 1 }))
    }

    const windowSize = Math.max(3, maxPageButtons - 2) // keep room for first/last
    const half = Math.floor(windowSize / 2)
    let start = cur - half
    let end = cur + half

    if (start < 2) {
      start = 2
      end = start + windowSize - 1
    }
    if (end > total - 1) {
      end = total - 1
      start = end - windowSize + 1
    }

    const items = [{ type: 'page', page: 1 }]
    if (start > 2) items.push({ type: 'ellipsis' })
    for (let p = start; p <= end; p += 1) items.push({ type: 'page', page: p })
    if (end < total - 1) items.push({ type: 'ellipsis' })
    items.push({ type: 'page', page: total })
    return items
  })

  return { totalPages, pageItems }
}

