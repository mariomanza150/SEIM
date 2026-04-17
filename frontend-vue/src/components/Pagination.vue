<template>
  <nav v-if="count > pageSize" :aria-label="ariaLabel">
    <ul class="pagination justify-content-center" :class="ulClass">
      <li class="page-item" :class="{ disabled: !canGoPrevious }">
        <button
          type="button"
          class="page-link"
          :disabled="!canGoPrevious"
          :aria-label="t('pagination.previous')"
          @click="emitPageChange(currentPage - 1)"
        >
          {{ t('pagination.previous') }}
        </button>
      </li>

      <li
        v-for="(item, idx) in pageItems"
        :key="item.type === 'page' ? item.page : `e-${idx}`"
        class="page-item"
        :class="{
          active: item.type === 'page' && item.page === currentPage,
          disabled: item.type === 'ellipsis',
        }"
      >
        <span v-if="item.type === 'ellipsis'" class="page-link" aria-hidden="true">…</span>
        <button
          v-else
          type="button"
          class="page-link"
          :aria-label="t('pagination.pageNumberAria', { n: item.page })"
          :aria-current="item.page === currentPage ? 'page' : undefined"
          @click="emitPageChange(item.page)"
        >
          {{ item.page }}
        </button>
      </li>

      <li class="page-item" :class="{ disabled: !canGoNext }">
        <button
          type="button"
          class="page-link"
          :disabled="!canGoNext"
          :aria-label="t('pagination.next')"
          @click="emitPageChange(currentPage + 1)"
        >
          {{ t('pagination.next') }}
        </button>
      </li>
    </ul>
  </nav>
</template>

<script setup>
import { computed, toRef } from 'vue'
import { useI18n } from 'vue-i18n'
import { usePagination } from '@/composables/usePagination'

const props = defineProps({
  count: { type: Number, required: true },
  pageSize: { type: Number, required: true },
  currentPage: { type: Number, required: true },
  canGoNext: { type: Boolean, default: true },
  canGoPrevious: { type: Boolean, default: true },
  ariaLabel: { type: String, default: '' },
  ulClass: { type: String, default: '' },
  maxPageButtons: { type: Number, default: 7 },
})

const emit = defineEmits(['page-change'])

const { t } = useI18n()
const { pageItems, totalPages } = usePagination({
  count: toRef(props, 'count'),
  pageSize: toRef(props, 'pageSize'),
  currentPage: toRef(props, 'currentPage'),
  maxPageButtons: props.maxPageButtons,
})

const safePage = computed(() => Math.min(Math.max(1, props.currentPage), totalPages.value))

function emitPageChange(page) {
  const next = Math.min(Math.max(1, page), totalPages.value)
  if (next === safePage.value) return
  emit('page-change', next)
}
</script>

