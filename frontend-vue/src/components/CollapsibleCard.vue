<template>
  <div
    class="card collapsible-card"
    :class="[cardClass, { 'mb-4': withMargin }]"
    :data-testid="testId || undefined"
  >
    <div
      class="card-header d-flex justify-content-between align-items-center gap-2"
      :class="{ 'py-2': compactHeader }"
    >
      <button
        type="button"
        class="btn btn-link text-decoration-none text-body flex-grow-1 text-start px-0 py-0 d-flex align-items-center gap-2 min-w-0"
        :id="toggleId"
        :aria-expanded="open ? 'true' : 'false'"
        :aria-controls="panelId"
        data-testid="collapsible-card-toggle"
        @click="open = !open"
      >
        <i
          class="bi flex-shrink-0"
          :class="open ? 'bi-chevron-down' : 'bi-chevron-right'"
          aria-hidden="true"
        ></i>
        <span class="min-w-0" :class="titleClass">
          <slot name="title" />
        </span>
      </button>
      <div v-if="$slots['header-extra']" class="flex-shrink-0 d-flex align-items-center gap-2">
        <slot name="header-extra" />
      </div>
    </div>
    <div
      v-if="open"
      :id="panelId"
      class="card-body"
      :class="bodyClass"
      role="region"
      :aria-labelledby="toggleId"
      data-testid="collapsible-card-panel"
    >
      <slot />
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  /** When true, section starts expanded. */
  defaultOpen: {
    type: Boolean,
    default: false,
  },
  testId: {
    type: String,
    default: '',
  },
  cardClass: {
    type: [String, Object, Array],
    default: '',
  },
  bodyClass: {
    type: [String, Object, Array],
    default: '',
  },
  titleClass: {
    type: String,
    default: 'mb-0',
  },
  withMargin: {
    type: Boolean,
    default: true,
  },
  compactHeader: {
    type: Boolean,
    default: false,
  },
})

const open = ref(props.defaultOpen)
const uid = Math.random().toString(36).slice(2, 9)
const toggleId = computed(() => `collapsible-toggle-${props.testId || uid}`)
const panelId = computed(() => `collapsible-panel-${props.testId || uid}`)

watch(
  () => props.defaultOpen,
  (value) => {
    open.value = value
  },
)

defineExpose({
  open,
  expand: () => {
    open.value = true
  },
  collapse: () => {
    open.value = false
  },
})
</script>

<style scoped>
.min-w-0 {
  min-width: 0;
}

.collapsible-card :deep(.card-header) {
  background-color: var(--seim-surface-bg, inherit);
}
</style>
