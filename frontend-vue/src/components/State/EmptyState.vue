<template>
  <div class="card" :data-testid="testId || undefined">
    <div class="card-body text-center py-5">
      <i v-if="iconClass" :class="iconClass" class="display-1 text-muted" aria-hidden="true"></i>
      <h4 v-if="title" class="mt-3">{{ title }}</h4>
      <p v-if="body" class="text-muted">{{ body }}</p>
      <div v-if="$slots.actions" class="mt-3">
        <slot name="actions" />
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  iconClass: { type: String, default: '' },
  title: { type: String, default: '' },
  body: { type: String, default: '' },
  testId: { type: String, default: '' },
})
</script>

