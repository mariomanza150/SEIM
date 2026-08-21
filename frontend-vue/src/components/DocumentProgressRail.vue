<template>
  <aside
    v-if="hasItems"
    class="card mb-4 document-progress-rail"
    data-testid="document-progress-rail"
  >
    <div class="card-header d-flex justify-content-between align-items-center gap-2">
      <h6 class="mb-0">{{ t('eligibilityFix.railTitle') }}</h6>
      <span
        class="badge"
        :class="complete ? 'bg-success' : 'bg-warning text-dark'"
      >
        {{
          t('applicationDetailPage.approvedFraction', {
            approved: approvedCount,
            required: requiredCount,
          })
        }}
      </span>
    </div>
    <div class="card-body py-3">
      <div class="progress mb-3" style="height: 6px">
        <div
          class="progress-bar"
          :class="complete ? 'bg-success' : 'bg-primary'"
          role="progressbar"
          :style="{ width: `${progressPercent}%` }"
          :aria-valuenow="progressPercent"
          aria-valuemin="0"
          aria-valuemax="100"
        />
      </div>
      <p v-if="complete" class="small text-muted mb-0">{{ t('eligibilityFix.railComplete') }}</p>
      <template v-else>
        <p class="small fw-semibold mb-1">
          {{ t('eligibilityFix.railDueNow', { done: dueNowDone, total: dueNowItems.length }) }}
        </p>
        <ul v-if="dueNowItems.length" class="list-unstyled small mb-3">
          <li
            v-for="item in dueNowItems"
            :key="`due-${item.document_type_id}`"
            class="mb-1"
            data-testid="document-progress-rail-due-item"
          >
            <a :href="itemHref(item)" class="text-decoration-none">{{ itemLabel(item) }}</a>
            <span class="text-muted"> — {{ statusLabel(item) }}</span>
          </li>
        </ul>
        <p v-if="laterItems.length" class="small fw-semibold mb-1">
          {{ t('eligibilityFix.railLater', { n: laterItems.length }) }}
        </p>
        <ul v-if="laterItems.length" class="list-unstyled small mb-0">
          <li
            v-for="item in laterItems"
            :key="`later-${item.document_type_id}`"
            class="mb-1 text-muted"
            data-testid="document-progress-rail-later-item"
          >
            <a :href="itemHref(item)" class="text-decoration-none text-muted">{{ itemLabel(item) }}</a>
          </li>
        </ul>
      </template>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { documentTypeLabel } from '@/utils/documentApi'

const props = defineProps({
  checklist: {
    type: Object,
    default: null,
  },
})

const { t, te } = useI18n()

const items = computed(() => (Array.isArray(props.checklist?.items) ? props.checklist.items : []))
const hasItems = computed(() => items.value.length > 0)
const requiredCount = computed(() => Number(props.checklist?.required_count || 0))
const approvedCount = computed(() => Number(props.checklist?.approved_count || 0))
const complete = computed(() => Boolean(props.checklist?.complete))
const progressPercent = computed(() => {
  if (!requiredCount.value) return complete.value ? 100 : 0
  return Math.min(100, Math.round((approvedCount.value / requiredCount.value) * 100))
})

function isDone(item) {
  return item.status === 'approved' || item.status === 'n_a'
}

const dueNowItems = computed(() =>
  items.value.filter((item) => item.due_now !== false && !isDone(item)),
)

const laterItems = computed(() =>
  items.value.filter((item) => item.due_now === false && !isDone(item)),
)

const dueNowDone = computed(() =>
  items.value.filter((item) => item.due_now !== false && isDone(item)).length,
)

function itemHref(item) {
  return `#checklist-item-${item.document_type_id}`
}

function itemLabel(item) {
  return documentTypeLabel(item, item?.name || t('documentDetailPage.notAvailable'), { t, te })
}

function statusLabel(item) {
  const key = `applicationDetailPage.checklist.${item.status}`
  if (te(key)) return t(key)
  return item.status
}
</script>

<style scoped>
.document-progress-rail {
  position: sticky;
  top: 4.5rem;
  z-index: 10;
  background-color: var(--seim-surface-bg);
  color: var(--seim-surface-text);
}
</style>
