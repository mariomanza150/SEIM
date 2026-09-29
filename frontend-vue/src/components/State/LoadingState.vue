<template>
  <div class="text-center py-5" :aria-live="ariaLive">
    <div class="spinner-border text-primary" role="status">
      <span class="visually-hidden">{{ spinnerLabel }}</span>
    </div>
    <p v-if="hint" class="mt-3 text-muted">{{ hint }}</p>
  </div>
</template>

<script setup>
defineProps({
  spinnerLabel: { type: String, default: 'Loading' },
  hint: { type: String, default: '' },
  ariaLive: { type: String, default: 'polite' },
})
</script>
