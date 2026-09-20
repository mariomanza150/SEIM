<template>
  <CollapsibleCard
    v-if="hasItems"
    test-id="document-progress-rail"
    card-class="document-progress-rail"
    body-class="py-3"
    title-class="h6 mb-0"
    compact-header
    :default-open="false"
  >
    <template #title>{{ t('eligibilityFix.railTitle') }}</template>
    <template #header-extra>
      <span
        class="badge"
        :class="complete ? 'bg-success' : 'bg-warning text-dark'"
        data-testid="document-progress-rail-badge"
      >
        {{
          t('applicationDetailPage.approvedFraction', {
            approved: approvedCount,
            required: requiredCount,
          })
        }}
      </span>
    </template>

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
          <a
            :href="itemHref(item)"
            class="text-decoration-none"
            data-testid="document-progress-rail-link"
            @click.prevent="onItemClick(item)"
          >{{ itemLabel(item) }}</a>
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
          <a
            :href="itemHref(item)"
            class="text-decoration-none text-muted"
            data-testid="document-progress-rail-link"
            @click.prevent="onItemClick(item)"
          >{{ itemLabel(item) }}</a>
        </li>
      </ul>
    </template>
  </CollapsibleCard>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import CollapsibleCard from '@/components/CollapsibleCard.vue'
import { documentTypeLabel } from '@/utils/documentApi'

const props = defineProps({
  checklist: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['navigate-item'])

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

function onItemClick(item) {
  emit('navigate-item', item)
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
:deep(.document-progress-rail) {
  position: sticky;
  top: 4.5rem;
  z-index: 10;
  background-color: var(--seim-surface-bg);
  color: var(--seim-surface-text);
}
</style>
