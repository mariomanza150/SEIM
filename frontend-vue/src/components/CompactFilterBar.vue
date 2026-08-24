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
      <div class="d-md-none d-flex flex-wrap align-items-center gap-2 mb-2">
        <button
          type="button"
          class="btn btn-outline-secondary btn-sm"
          data-testid="compact-filter-mobile-open"
          :aria-label="resolvedFiltersLabel"
          @click="mobileOpen = true"
        >
          <i class="bi bi-funnel me-1" aria-hidden="true" />
          {{ resolvedFiltersLabel }}
          <span v-if="activeFilterCount > 0" class="badge bg-primary ms-1">{{ activeFilterCount }}</span>
        </button>
        <button
          type="button"
          class="btn btn-outline-secondary btn-sm"
          data-testid="compact-filter-mobile-clear"
          :aria-label="resolvedClear"
          @click="$emit('clear')"
        >
          <i class="bi bi-x-circle me-1" aria-hidden="true" />{{ resolvedClear }}
        </button>
      </div>

      <div class="d-none d-md-block">
        <div class="row g-2 align-items-end">
          <slot name="primary" />
          <div class="col-auto d-flex flex-wrap gap-2 align-items-end">
            <button
              type="button"
              class="btn btn-outline-secondary"
              :class="{ 'btn-sm': embedded }"
              data-testid="compact-filter-clear"
              :aria-label="resolvedClear"
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

    <div
      v-if="mobileOpen"
      class="offcanvas offcanvas-bottom show d-md-none seim-compact-filter-bar__mobile-drawer"
      tabindex="-1"
      data-testid="compact-filter-mobile-drawer"
      @click.self="mobileOpen = false"
    >
      <div class="offcanvas-header">
        <h2 class="offcanvas-title h6 mb-0">{{ resolvedFiltersLabel }}</h2>
        <button
          type="button"
          class="btn-close"
          :aria-label="t('common.close')"
          @click="mobileOpen = false"
        />
      </div>
      <div class="offcanvas-body">
        <div class="row g-3 align-items-end">
          <slot name="primary" />
        </div>
        <div v-if="hasDisclosure" class="mt-3">
          <button
            v-if="hasAdvanced || hasPresets"
            type="button"
            class="btn btn-outline-secondary btn-sm mb-3"
            :aria-expanded="mobileExtraOpen ? 'true' : 'false'"
            @click="mobileExtraOpen = !mobileExtraOpen"
          >
            {{ resolvedToggle }}
          </button>
          <div v-if="mobileExtraOpen">
            <div v-if="hasAdvanced" class="mb-3">
              <slot name="advanced" />
            </div>
            <div v-if="hasPresets">
              <slot name="presets" />
            </div>
          </div>
        </div>
        <div class="d-flex gap-2 mt-4">
          <button type="button" class="btn btn-primary flex-grow-1" @click="mobileOpen = false">
            {{ t('common.applyFilters') }}
          </button>
          <button type="button" class="btn btn-outline-secondary" @click="$emit('clear')">
            {{ resolvedClear }}
          </button>
        </div>
      </div>
    </div>
    <div
      v-if="mobileOpen"
      class="offcanvas-backdrop fade show d-md-none"
      @click="mobileOpen = false"
    />
  </div>
</template>

<script setup>
import { computed, ref, useSlots } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  testId: { type: String, default: undefined },
  clearLabel: { type: String, default: '' },
  toggleLabel: { type: String, default: '' },
  filtersLabel: { type: String, default: '' },
  activeFilterCount: { type: Number, default: 0 },
  sticky: { type: Boolean, default: true },
  embedded: { type: Boolean, default: false },
})

defineEmits(['clear'])

const { t } = useI18n()
const slots = useSlots()
const open = ref(false)
const mobileOpen = ref(false)
const mobileExtraOpen = ref(false)

const hasAdvanced = computed(() => typeof slots.advanced === 'function')
const hasPresets = computed(() => typeof slots.presets === 'function')
const hasDisclosure = computed(() => hasAdvanced.value || hasPresets.value)
const resolvedClear = computed(() => props.clearLabel || t('common.clearFilters'))
const resolvedToggle = computed(() => props.toggleLabel || t('common.advancedFilters'))
const resolvedFiltersLabel = computed(() => props.filtersLabel || t('common.filters'))
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

.seim-compact-filter-bar__mobile-drawer {
  visibility: visible;
  height: auto;
  max-height: 85vh;
}
</style>
