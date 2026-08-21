<template>
  <div
    class="seim-compact-filter-bar"
    :class="{
      'card mb-4': !embedded,
      'seim-compact-filter-bar--sticky': sticky && !embedded,
      'seim-compact-filter-bar--embedded': embedded,
    }"
    :data-testid="testId"
  >
    <div :class="embedded ? '' : 'card-body py-3'">
      <div class="row g-2 align-items-end">
        <slot name="primary" />
        <div class="col-auto d-flex flex-wrap gap-2 align-items-end">
          <button
            type="button"
            class="btn btn-outline-secondary"
            :class="{ 'btn-sm': embedded }"
            data-testid="compact-filter-clear"
            @click="$emit('clear')"
          >
            <i class="bi bi-x-circle me-1" aria-hidden="true" />{{ resolvedClear }}
          </button>
          <button
            v-if="hasDisclosure"
            type="button"
            class="btn btn-outline-secondary"
            :class="{ 'btn-sm': embedded }"
            :aria-expanded="open ? 'true' : 'false'"
            data-testid="compact-filter-advanced-toggle"
            @click="open = !open"
          >
            <i
              class="bi"
              :class="open ? 'bi-chevron-up' : 'bi-chevron-down'"
              aria-hidden="true"
            />
            <span class="ms-1">{{ resolvedToggle }}</span>
          </button>
        </div>
      </div>
      <div
        v-if="hasDisclosure && open"
        class="seim-compact-filter-bar__extra border-top pt-3 mt-3"
        data-testid="compact-filter-extra"
      >
        <div v-if="hasAdvanced" class="mb-3" data-testid="compact-filter-advanced">
          <slot name="advanced" />
        </div>
        <div v-if="hasPresets" data-testid="compact-filter-presets">
          <slot name="presets" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, useSlots } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  testId: { type: String, default: undefined },
  clearLabel: { type: String, default: '' },
  toggleLabel: { type: String, default: '' },
  sticky: { type: Boolean, default: true },
  embedded: { type: Boolean, default: false },
})

defineEmits(['clear'])

const { t } = useI18n()
const slots = useSlots()
const open = ref(false)

const hasAdvanced = computed(() => typeof slots.advanced === 'function')
const hasPresets = computed(() => typeof slots.presets === 'function')
const hasDisclosure = computed(() => hasAdvanced.value || hasPresets.value)
const resolvedClear = computed(() => props.clearLabel || t('common.clearFilters'))
const resolvedToggle = computed(() => props.toggleLabel || t('common.advancedFilters'))
</script>

<style scoped>
.seim-compact-filter-bar--sticky {
  position: sticky;
  top: 0;
  z-index: 20;
  background-color: var(--seim-surface-bg);
  color: var(--seim-surface-text);
  border-color: var(--seim-border-color);
}

.seim-compact-filter-bar--embedded {
  background-color: var(--seim-app-bg);
  color: var(--seim-surface-text);
  border: 1px solid var(--seim-border-color);
  border-radius: 0.375rem;
  padding: 0.75rem;
  margin-bottom: 0.75rem;
}
</style>
