/**
 * @vitest-environment node
 */
import { describe, it, expect } from 'vitest'
import { ref } from 'vue'
import { usePagination } from './usePagination'

describe('usePagination', () => {
  it('returns a single page when page size is missing or zero', () => {
    const { totalPages, pageItems } = usePagination({
      count: 40,
      pageSize: 0,
      currentPage: 1,
    })
    expect(totalPages.value).toBe(1)
    expect(pageItems.value).toEqual([{ type: 'page', page: 1 }])
  })

  it('lists every page when total fits in the button window', () => {
    const { totalPages, pageItems } = usePagination({
      count: 30,
      pageSize: 10,
      currentPage: 2,
      maxPageButtons: 7,
    })
    expect(totalPages.value).toBe(3)
    expect(pageItems.value.map((item) => item.page)).toEqual([1, 2, 3])
  })

  it('inserts ellipses and keeps first/last when many pages', () => {
    const currentPage = ref(5)
    const { totalPages, pageItems } = usePagination({
      count: 200,
      pageSize: 10,
      currentPage,
      maxPageButtons: 7,
    })
    expect(totalPages.value).toBe(20)
    expect(pageItems.value[0]).toEqual({ type: 'page', page: 1 })
    expect(pageItems.value.some((item) => item.type === 'ellipsis')).toBe(true)
    expect(pageItems.value.at(-1)).toEqual({ type: 'page', page: 20 })
    expect(pageItems.value.map((item) => item.page).filter(Boolean)).toContain(5)
  })

  it('shifts the window near the start without going below page 2', () => {
    const { pageItems } = usePagination({
      count: 200,
      pageSize: 10,
      currentPage: 1,
      maxPageButtons: 7,
    })
    const pages = pageItems.value.filter((item) => item.type === 'page').map((item) => item.page)
    expect(pages[0]).toBe(1)
    expect(pages[1]).toBe(2)
    expect(pages.at(-1)).toBe(20)
  })

  it('shifts the window near the end without exceeding the last page', () => {
    const { pageItems } = usePagination({
      count: 200,
      pageSize: 10,
      currentPage: 20,
      maxPageButtons: 7,
    })
    const pages = pageItems.value.filter((item) => item.type === 'page').map((item) => item.page)
    expect(pages[0]).toBe(1)
    expect(pages.at(-1)).toBe(20)
    expect(pages.at(-2)).toBe(19)
  })

  it('reads reactive count and pageSize refs', () => {
    const count = ref(0)
    const pageSize = ref(10)
    const currentPage = ref(1)
    const { totalPages } = usePagination({ count, pageSize, currentPage })
    expect(totalPages.value).toBe(1)
    count.value = 55
    expect(totalPages.value).toBe(6)
  })
})
