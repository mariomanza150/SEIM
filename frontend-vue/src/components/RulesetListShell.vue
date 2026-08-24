<template>
  <PageStateShell
    :loading="loading"
    :error="error"
    :empty="empty"
    :empty-body="emptyBody"
    :empty-title="emptyTitle"
    :loading-label="loadingLabel"
    skeleton="table"
    :skeleton-columns="skeletonColumns"
  >
    <ResponsiveList
      :items="items"
      :columns="columns"
      :mobile-test-id="mobileTestId"
    >
      <slot name="table" />
      <template v-for="col in columns" :key="col.key" #[`col-${col.key}`]="slotProps">
        <slot :name="`col-${col.key}`" v-bind="slotProps" />
      </template>
      <template #actions="slotProps">
        <slot name="actions" v-bind="slotProps" />
      </template>
      <template v-if="$slots['mobile-card']" #mobile-card="slotProps">
        <slot name="mobile-card" v-bind="slotProps" />
      </template>
    </ResponsiveList>
  </PageStateShell>
</template>

<script setup>
import PageStateShell from '@/components/State/PageStateShell.vue'
import ResponsiveList from '@/components/ResponsiveList.vue'

defineProps({
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
  empty: { type: Boolean, default: false },
  emptyBody: { type: String, default: '' },
  emptyTitle: { type: String, default: '' },
  loadingLabel: { type: String, default: '' },
  skeletonColumns: { type: Number, default: 5 },
  items: { type: Array, default: () => [] },
  columns: { type: Array, default: () => [] },
  mobileTestId: { type: String, default: 'ruleset-list' },
})
</script>
