<template>
  <div class="seim-responsive-list">
    <div class="d-none d-md-block">
      <slot />
    </div>
    <div class="d-md-none seim-responsive-list__mobile">
      <div
        v-for="(item, index) in items"
        :key="itemKey ? item[itemKey] : index"
        class="card mb-3 seim-responsive-list__card card-hover"
        :data-testid="mobileTestId ? `${mobileTestId}-${index}` : undefined"
      >
        <div class="card-body">
          <slot name="mobile-card" :item="item" :index="index">
            <dl class="row mb-0 seim-responsive-list__dl">
              <template v-for="col in columns" :key="col.key">
                <dt class="col-5 text-muted small">{{ col.label }}</dt>
                <dd class="col-7 mb-2">
                  <slot :name="`col-${col.key}`" :item="item" :value="item[col.key]">
                    {{ formatValue(item, col) }}
                  </slot>
                </dd>
              </template>
            </dl>
            <div v-if="$slots.actions" class="mt-3 d-flex flex-wrap gap-2">
              <slot name="actions" :item="item" :index="index" />
            </div>
          </slot>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  items: { type: Array, default: () => [] },
  columns: { type: Array, default: () => [] },
  itemKey: { type: String, default: 'id' },
  mobileTestId: { type: String, default: '' },
})

function formatValue(item, col) {
  const raw = item?.[col.key]
  if (col.format && typeof col.format === 'function') return col.format(raw, item)
  if (raw == null || raw === '') return '—'
  return String(raw)
}
</script>

<style scoped>
.seim-responsive-list__dl dt {
  font-weight: 500;
}

.seim-responsive-list__card {
  border-color: var(--seim-border-color, #dee2e6);
}
</style>
