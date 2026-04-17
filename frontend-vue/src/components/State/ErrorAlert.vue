<template>
  <div class="alert alert-danger" role="alert" :data-testid="testId || undefined">
    <i v-if="iconClass" :class="iconClass" class="me-2" aria-hidden="true"></i>
    <slot>{{ message }}</slot>
  </div>
</template>

<script setup>
defineProps({
  message: { type: String, default: '' },
  iconClass: { type: String, default: 'bi bi-exclamation-triangle' },
  testId: { type: String, default: '' },
})
</script>

