<template>
  <div class="card" role="status" :data-testid="testId || undefined">
    <div class="card-body text-center py-5">
      <i v-if="iconClass" :class="iconClass" class="display-1 text-muted" aria-hidden="true"></i>
      <component :is="headingTag" v-if="title" class="mt-3">{{ title }}</component>
      <p v-if="body" class="text-muted">{{ body }}</p>
      <div v-if="$slots.actions" class="mt-3">
        <slot name="actions" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  iconClass: { type: String, default: '' },
  title: { type: String, default: '' },
  body: { type: String, default: '' },
  testId: { type: String, default: '' },
  headingLevel: { type: Number, default: 4 },
})

const headingTag = computed(() => {
  const level = Math.min(6, Math.max(2, props.headingLevel))
  return `h${level}`
})
</script>
